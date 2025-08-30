"""
DC Motor Model from First Principles
Mathematical modeling based on fundamental electrical and mechanical equations
"""

import numpy as np
from scipy.integrate import odeint
from scipy import signal
import control as ctrl
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class MotorParameters:
    """
    DC Motor Parameters derived from first principles measurements
    
    All parameters should be measured through experimental methods:
    - R: Resistance measured using ohmmeter or V/I method
    - L: Inductance measured using impedance method or parameter identification
    - J: Inertia calculated from coast-down test
    - b: Friction coefficient from coast-down test
    - Kt: Torque constant from stall torque measurements
    - Ke: Back-EMF constant from free-running voltage measurements
    """
    R: float    # Resistance (Ohms)
    L: float    # Inductance (H)
    J: float    # Moment of inertia (kg⋅m²)
    b: float    # Viscous friction coefficient (N⋅m⋅s/rad)
    Kt: float   # Torque constant (N⋅m/A)
    Ke: float   # Back-EMF constant (V⋅s/rad)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'MotorParameters':
        """Create from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate parameter values and return warnings"""
        warnings = []
        
        if self.R <= 0:
            warnings.append("Resistance must be positive")
        if self.L <= 0:
            warnings.append("Inductance must be positive")
        if self.J <= 0:
            warnings.append("Inertia must be positive")
        if self.b < 0:
            warnings.append("Friction coefficient must be non-negative")
        if self.Kt <= 0:
            warnings.append("Torque constant must be positive")
        if self.Ke <= 0:
            warnings.append("Back-EMF constant must be positive")
            
        # Check physical consistency (Kt ≈ Ke in SI units)
        if abs(self.Kt - self.Ke) / max(self.Kt, self.Ke) > 0.1:
            warnings.append("Kt and Ke should be approximately equal in SI units")
            
        return warnings

class DCMotorModel:
    """
    DC Motor Model from First Principles
    
    Based on fundamental equations:
    Electrical: V = R*i + L*di/dt + Ke*ω
    Mechanical: J*dω/dt = Kt*i - b*ω - T_load
    
    Where:
    - V: Applied voltage (V)
    - i: Armature current (A)
    - ω: Angular velocity (rad/s)
    - T_load: Load torque (N⋅m)
    """
    
    def __init__(self, params: MotorParameters):
        self.params = params
        self.state = np.array([0.0, 0.0])  # [current, angular_velocity]
        self.time = 0.0
        
        # Validate parameters
        warnings = params.validate()
        if warnings:
            for warning in warnings:
                logger.warning(f"Motor parameter warning: {warning}")
    
    def transfer_function(self) -> ctrl.TransferFunction:
        """
        Derive transfer function from first principles
        
        From the coupled differential equations:
        V = R*i + L*di/dt + Ke*ω
        J*dω/dt = Kt*i - b*ω
        
        Taking Laplace transform and solving:
        G(s) = ω(s)/V(s) = Kt / (L*J*s² + (R*J + L*b)*s + R*b + Kt*Ke)
        """
        R, L, J, b, Kt, Ke = (self.params.R, self.params.L, self.params.J,
                             self.params.b, self.params.Kt, self.params.Ke)
        
        # Numerator: Kt (torque constant)
        num = [Kt]
        
        # Denominator coefficients (characteristic equation)
        a2 = L * J                              # s² coefficient
        a1 = R * J + L * b                      # s¹ coefficient  
        a0 = R * b + Kt * Ke                    # s⁰ coefficient
        den = [a2, a1, a0]
        
        tf = ctrl.TransferFunction(num, den)
        
        logger.info(f"Transfer function: {Kt} / ({a2:.6f}s² + {a1:.6f}s + {a0:.6f})")
        
        return tf
    
    def state_space_model(self) -> ctrl.StateSpace:
        """
        State-space representation
        
        State vector: x = [i, ω]ᵀ
        Input: u = V (applied voltage)
        Output: y = ω (angular velocity)
        
        ẋ = Ax + Bu
        y = Cx + Du
        """
        R, L, J, b, Kt, Ke = (self.params.R, self.params.L, self.params.J,
                             self.params.b, self.params.Kt, self.params.Ke)
        
        # State matrix A
        A = np.array([[-R/L, -Ke/L],    # di/dt equation
                     [Kt/J, -b/J]])     # dω/dt equation
        
        # Input matrix B
        B = np.array([[1/L],            # Voltage affects current equation
                     [0]])              # Voltage doesn't directly affect mechanical equation
        
        # Output matrix C (output is angular velocity)
        C = np.array([[0, 1]])          # Select angular velocity from state
        
        # Feedthrough matrix D
        D = np.array([[0]])             # No direct feedthrough
        
        return ctrl.StateSpace(A, B, C, D)
    
    def simulate_step_response(self, step_voltage: float = 12.0, 
                             duration: float = 2.0, dt: float = 0.001) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate step response using transfer function
        """
        tf = self.transfer_function()
        
        # Generate time vector
        time_vector = np.arange(0, duration, dt)
        
        # Simulate step response
        time_out, response = ctrl.step_response(tf * step_voltage, time_vector)
        
        return time_out, response
    
    def simulate_real_time(self, voltage_input: float, load_torque: float = 0.0, 
                          dt: float = 0.001) -> Dict[str, float]:
        """
        Real-time simulation step for hardware-in-the-loop
        
        Integrates the differential equations one time step forward
        """
        def motor_dynamics(state, t, V, T_load):
            """
            Coupled differential equations
            state = [current, angular_velocity]
            """
            i, omega = state
            R, L, J, b, Kt, Ke = (self.params.R, self.params.L, self.params.J,
                                 self.params.b, self.params.Kt, self.params.Ke)
            
            # Electrical equation: L*di/dt = V - R*i - Ke*ω
            di_dt = (V - R*i - Ke*omega) / L
            
            # Mechanical equation: J*dω/dt = Kt*i - b*ω - T_load
            domega_dt = (Kt*i - b*omega - T_load) / J
            
            return [di_dt, domega_dt]
        
        # Integrate one time step
        t_span = [self.time, self.time + dt]
        solution = odeint(motor_dynamics, self.state, t_span, 
                         args=(voltage_input, load_torque))
        
        # Update state and time
        self.state = solution[-1]
        self.time += dt
        
        current, angular_velocity = self.state
        
        # Calculate derived quantities
        rpm = angular_velocity * 60 / (2 * np.pi)
        torque = self.params.Kt * current
        back_emf = self.params.Ke * angular_velocity
        power_input = voltage_input * current
        power_mechanical = torque * angular_velocity
        efficiency = (power_mechanical / power_input * 100) if power_input > 0 else 0
        
        return {
            "current": float(current),
            "angular_velocity": float(angular_velocity),
            "rpm": float(rpm),
            "torque": float(torque),
            "back_emf": float(back_emf),
            "power_input": float(power_input),
            "power_mechanical": float(power_mechanical),
            "efficiency": float(efficiency),
            "timestamp": float(self.time)
        }
    
    def coast_down_analysis(self, initial_speed: float, 
                          duration: float = 5.0, dt: float = 0.01) -> Dict[str, Any]:
        """
        Simulate coast-down test for parameter identification
        
        During coast-down (V = 0), the equation becomes:
        J*dω/dt = -b*ω  (no current flows when V = 0 and steady state)
        
        Solution: ω(t) = ω₀ * exp(-b*t/J)
        Time constant: τ = J/b
        """
        def coast_down_dynamics(omega, t):
            """Coast-down differential equation"""
            return -self.params.b * omega / self.params.J
        
        # Generate time vector
        time_vector = np.arange(0, duration, dt)
        
        # Solve the differential equation
        speed_response = odeint(coast_down_dynamics, initial_speed, time_vector)
        speed_response = speed_response.flatten()
        
        # Fit exponential decay to extract time constant
        # ω(t) = ω₀ * exp(-t/τ) → ln(ω) = ln(ω₀) - t/τ
        valid_indices = speed_response > 0.01  # Avoid log(0)
        if np.sum(valid_indices) < 2:
            logger.error("Insufficient data for coast-down analysis")
            return {"error": "Insufficient data"}
        
        log_speed = np.log(speed_response[valid_indices])
        time_valid = time_vector[valid_indices]
        
        # Linear regression: log(ω) = a + b*t, where b = -1/τ
        coeffs = np.polyfit(time_valid, log_speed, 1)
        time_constant = -1.0 / coeffs[0] if coeffs[0] != 0 else float('inf')
        
        # Calculate identified parameters
        identified_friction = self.params.J / time_constant if time_constant > 0 else 0
        identified_inertia = time_constant * self.params.b
        
        return {
            "time_constant": float(time_constant),
            "initial_speed": float(initial_speed),
            "final_speed": float(speed_response[-1]),
            "identified_friction": float(identified_friction),
            "identified_inertia": float(identified_inertia),
            "actual_friction": float(self.params.b),
            "actual_inertia": float(self.params.J),
            "time_data": time_vector.tolist(),
            "speed_data": speed_response.tolist(),
            "fit_quality": float(np.corrcoef(time_valid, log_speed)[0, 1]**2)  # R²
        }
    
    def frequency_response(self, frequency_range: Tuple[float, float] = (0.1, 1000),
                          num_points: int = 1000) -> Dict[str, Any]:
        """
        Calculate frequency response (Bode plot data)
        """
        tf = self.transfer_function()
        
        # Generate frequency vector (logarithmic)
        omega = np.logspace(np.log10(frequency_range[0]), 
                           np.log10(frequency_range[1]), num_points)
        
        # Calculate frequency response
        mag, phase, freq = ctrl.bode_plot(tf, omega, plot=False)
        
        # Convert to dB and degrees
        mag_db = 20 * np.log10(mag)
        phase_deg = np.degrees(phase)
        
        return {
            "frequency": freq.tolist(),
            "magnitude_db": mag_db.tolist(),
            "phase_deg": phase_deg.tolist(),
            "gain_margin": float(ctrl.margin(tf)[0]) if ctrl.margin(tf)[0] is not None else None,
            "phase_margin": float(ctrl.margin(tf)[1]) if ctrl.margin(tf)[1] is not None else None
        }
    
    def calculate_system_characteristics(self) -> Dict[str, float]:
        """
        Calculate important system characteristics
        """
        tf = self.transfer_function()
        
        try:
            # Poles and zeros
            poles = ctrl.pole(tf)
            zeros = ctrl.zero(tf)
            
            # Settling time (2% criterion)
            step_info = ctrl.step_info(tf)
            settling_time = step_info.get('SettlingTime', None)
            
            # Natural frequency and damping ratio
            if len(poles) >= 2:
                # For second-order system: s² + 2ζωₙs + ωₙ²
                wn = np.sqrt(poles[0] * poles[1]) if poles[0] * poles[1] > 0 else None
                zeta = -np.real(poles[0] + poles[1]) / (2 * wn) if wn else None
            else:
                wn = None
                zeta = None
            
            # DC gain
            dc_gain = float(ctrl.dcgain(tf))
            
            # Bandwidth (frequency where magnitude drops by 3dB)
            if hasattr(ctrl, 'bandwidth'):
                bandwidth = float(ctrl.bandwidth(tf))
            else:
                bandwidth = None
            
            return {
                "dc_gain": dc_gain,
                "poles": [complex(p).real for p in poles] + [complex(p).imag for p in poles],
                "zeros": [complex(z).real for z in zeros] + [complex(z).imag for z in zeros],
                "natural_frequency": float(wn) if wn else None,
                "damping_ratio": float(zeta) if zeta else None,
                "settling_time": float(settling_time) if settling_time else None,
                "bandwidth": bandwidth
            }
            
        except Exception as e:
            logger.error(f"Error calculating system characteristics: {e}")
            return {"error": str(e)}
    
    def reset_state(self):
        """Reset the simulation state"""
        self.state = np.array([0.0, 0.0])
        self.time = 0.0
    
    def get_current_state(self) -> Dict[str, float]:
        """Get current simulation state"""
        current, angular_velocity = self.state
        return {
            "current": float(current),
            "angular_velocity": float(angular_velocity),
            "rpm": float(angular_velocity * 60 / (2 * np.pi)),
            "time": float(self.time)
        }