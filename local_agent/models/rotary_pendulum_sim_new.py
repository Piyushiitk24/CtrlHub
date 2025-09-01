"""
Rotary Inverted Pendulum Simulation with Mathematical Physics Model

This module provides a comprehensive simulation of a rotary inverted pendulum system
using mathematical physics models. It includes stepper motor dynamics,
AS5600 magnetic encoder simulation, and PID control capabilities.

Key Features:
- Mathematical physics simulation (no PyBullet dependency)
- Realistic stepper motor control (17HS4023)
- AS5600 magnetic encoder simulation
- Advanced PID control system
- Real-time data logging and analysis
- Educational learning modules
"""

import numpy as np
import time
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import threading
import logging
from pathlib import Path


@dataclass
class StepperMotorParams:
    """Parameters for 17HS4023 stepper motor."""
    steps_per_revolution: int = 200
    max_torque: float = 0.4  # Nm
    max_speed: float = 300  # RPM
    holding_torque: float = 0.3  # Nm
    step_angle: float = 1.8  # degrees
    
    def __post_init__(self):
        self.step_angle_rad = math.radians(self.step_angle)
        self.max_angular_velocity = self.max_speed * 2 * math.pi / 60  # rad/s


class PIDController:
    """PID Controller for pendulum balancing."""
    
    def __init__(self, kp: float = 10.0, ki: float = 0.1, kd: float = 5.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.prev_error = 0.0
        self.integral = 0.0
        self.max_integral = 100.0
        self.max_output = 1.0
        
    def update(self, error: float, dt: float) -> float:
        """Update PID controller and return control output."""
        # Proportional term
        proportional = self.kp * error
        
        # Integral term
        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.max_integral, self.max_integral)
        integral = self.ki * self.integral
        
        # Derivative term
        derivative = self.kd * (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error
        
        # Combined output
        output = proportional + integral + derivative
        return np.clip(output, -self.max_output, self.max_output)
    
    def reset(self):
        """Reset PID controller state."""
        self.prev_error = 0.0
        self.integral = 0.0


class AS5600Encoder:
    """AS5600 magnetic encoder simulation."""
    
    def __init__(self):
        self.resolution = 4096  # 12-bit resolution
        self.noise_level = 0.001  # Small amount of noise
        
    def read_position(self, angle: float) -> Dict[str, Any]:
        """
        Read encoder position from angle.
        
        Args:
            angle: Angle in radians
            
        Returns:
            Dict with raw value and converted angle
        """
        # Normalize angle to 0-2π range
        normalized_angle = angle % (2 * math.pi)
        
        # Convert to raw encoder value
        raw_value = int((normalized_angle / (2 * math.pi)) * self.resolution)
        
        # Add small amount of noise
        noise = np.random.normal(0, self.noise_level)
        noisy_raw = max(0, min(self.resolution - 1, raw_value + int(noise * self.resolution)))
        
        # Convert back to angle
        measured_angle = (noisy_raw / self.resolution) * 2 * math.pi
        
        return {
            'raw': noisy_raw,
            'angle': measured_angle,
            'degrees': math.degrees(measured_angle)
        }


class RotaryInvertedPendulumSim:
    """
    Comprehensive rotary inverted pendulum simulation with mathematical physics.
    
    This class provides a complete simulation environment for a rotary inverted pendulum
    system, including realistic physics, hardware simulation, and educational features.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the rotary inverted pendulum simulation."""
        self.config = config or {}
        self.running = False
        self.time_step = 1.0 / 240.0  # 240 Hz simulation
        self.real_time_factor = 1.0
        
        # Physical parameters
        self.arm_length = 0.15  # 15cm arm
        self.pendulum_length = 0.30  # 30cm pendulum
        self.arm_mass = 0.05  # 50g
        self.pendulum_mass = 0.02  # 20g
        self.gravity = 9.81
        
        # Derived parameters
        self.arm_inertia = (1/3) * self.arm_mass * self.arm_length**2
        self.pendulum_inertia = (1/3) * self.pendulum_mass * self.pendulum_length**2
        
        # Motor parameters
        self.stepper_motor = StepperMotorParams()
        self.encoder = AS5600Encoder()
        self.pid_controller = PIDController()
        
        # State variables [theta, theta_dot, phi, phi_dot]
        # theta: arm angle, phi: pendulum angle from vertical
        self.state = np.array([0.0, 0.0, 0.1, 0.0])  # Start with small pendulum perturbation
        
        # Control variables
        self.target_pendulum_angle = 0.0  # Target upright position
        self.motor_torque = 0.0
        self.control_enabled = True
        
        # Data logging
        self.data_log = []
        self.start_time = None
        
        # Threading
        self.simulation_thread = None
        self.should_stop = threading.Event()
        
        # Educational features
        self.learning_mode = False
        self.performance_metrics = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def initialize_physics(self) -> bool:
        """Initialize mathematical physics simulation."""
        try:
            # Reset state
            self.state = np.array([0.0, 0.0, np.random.uniform(-0.1, 0.1), 0.0])
            
            # Initialize time
            self.start_time = time.time()
            
            self.logger.info("Mathematical physics simulation initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize physics: {e}")
            return False
    
    def step_simulation(self) -> Dict[str, Any]:
        """
        Step the mathematical physics simulation forward by one time step.
        
        Uses Runge-Kutta 4th order integration for the coupled pendulum equations.
        
        Returns:
            Dict containing current state information
        """
        if not self.running:
            return {}
        
        # Current state: [theta, theta_dot, phi, phi_dot]
        # theta: arm angle, phi: pendulum angle from vertical
        
        # Get current state
        theta, theta_dot, phi, phi_dot = self.state
        
        # PID Control (only if enabled)
        if self.control_enabled:
            pendulum_error = self.target_pendulum_angle - phi
            control_output = self.pid_controller.update(pendulum_error, self.time_step)
            
            # Apply stepper motor dynamics
            max_torque = self.stepper_motor.max_torque
            self.motor_torque = np.clip(control_output * max_torque, -max_torque, max_torque)
        else:
            self.motor_torque = 0.0
            control_output = 0.0
            pendulum_error = 0.0
        
        # Coupled pendulum equations of motion
        def equations_of_motion(state, torque):
            theta, theta_dot, phi, phi_dot = state
            
            # System parameters
            m1 = self.arm_mass
            m2 = self.pendulum_mass
            l1 = self.arm_length
            l2 = self.pendulum_length / 2  # Center of mass at half length
            I1 = self.arm_inertia
            I2 = self.pendulum_inertia
            g = self.gravity
            
            # Coupled equations for rotary inverted pendulum
            # Mass matrix coefficients
            M11 = I1 + m2 * l1**2 + I2 * np.sin(phi)**2
            M12 = (I2 + m2 * l2**2) * np.cos(phi)
            M21 = M12
            M22 = I2 + m2 * l2**2
            
            # Coriolis and centrifugal terms
            C1 = I2 * np.sin(phi) * np.cos(phi) * theta_dot**2 - (I2 + m2 * l2**2) * np.sin(phi) * phi_dot**2
            C2 = -I2 * np.sin(phi) * np.cos(phi) * theta_dot**2
            
            # Gravity terms
            G1 = 0  # No gravity effect on arm rotation
            G2 = m2 * g * l2 * np.sin(phi)
            
            # Input torques
            tau1 = torque  # Motor torque on arm
            tau2 = 0  # No direct torque on pendulum
            
            # Add damping
            damping_arm = 0.01
            damping_pendulum = 0.001
            
            tau1 -= damping_arm * theta_dot
            tau2 -= damping_pendulum * phi_dot
            
            # Solve for accelerations: [M]{ddot_q} = {tau} - {C} - {G}
            det_M = M11 * M22 - M12 * M21
            
            if abs(det_M) < 1e-10:  # Avoid singularity
                det_M = 1e-10
            
            theta_ddot = (M22 * (tau1 - C1 - G1) - M12 * (tau2 - C2 - G2)) / det_M
            phi_ddot = (M11 * (tau2 - C2 - G2) - M21 * (tau1 - C1 - G1)) / det_M
            
            return np.array([theta_dot, theta_ddot, phi_dot, phi_ddot])
        
        # Runge-Kutta 4th order integration
        dt = self.time_step
        k1 = equations_of_motion(self.state, self.motor_torque)
        k2 = equations_of_motion(self.state + 0.5 * dt * k1, self.motor_torque)
        k3 = equations_of_motion(self.state + 0.5 * dt * k2, self.motor_torque)
        k4 = equations_of_motion(self.state + dt * k3, self.motor_torque)
        
        # Update state
        self.state += dt * (k1 + 2*k2 + 2*k3 + k4) / 6
        
        # Extract updated values
        theta, theta_dot, phi, phi_dot = self.state
        
        # Simulate encoder readings
        encoder_readings = self.encoder.read_position(theta)
        
        # Current simulation time
        current_time = time.time() - self.start_time if self.start_time else 0
        
        # Create state dictionary
        state_data = {
            'timestamp': current_time,
            'arm_angle': theta,
            'arm_velocity': theta_dot,
            'pendulum_angle': phi,
            'pendulum_velocity': phi_dot,
            'motor_torque': self.motor_torque,
            'encoder_raw': encoder_readings['raw'],
            'encoder_angle': encoder_readings['angle'],
            'pid_output': control_output if self.control_enabled else 0,
            'pid_error': pendulum_error if self.control_enabled else 0,
            'target_angle': self.target_pendulum_angle,
            'control_enabled': self.control_enabled
        }
        
        # Log data
        self.data_log.append(state_data.copy())
        
        # Limit log size to prevent memory issues
        if len(self.data_log) > 10000:
            self.data_log = self.data_log[-5000:]  # Keep last 5000 entries
        
        return state_data
    
    def start_experiment(self) -> bool:
        """Start the pendulum balancing experiment."""
        try:
            if not self.initialize_physics():
                return False
            
            self.running = True
            self.should_stop.clear()
            
            # Start simulation thread
            self.simulation_thread = threading.Thread(target=self._simulation_loop)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
            
            self.logger.info("Pendulum experiment started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start experiment: {e}")
            return False
    
    def stop_experiment(self) -> bool:
        """Stop the pendulum experiment."""
        try:
            self.running = False
            self.should_stop.set()
            
            if self.simulation_thread and self.simulation_thread.is_alive():
                self.simulation_thread.join(timeout=2.0)
            
            self.logger.info("Pendulum experiment stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop experiment: {e}")
            return False
    
    def _simulation_loop(self):
        """Main simulation loop running in separate thread."""
        last_time = time.time()
        
        while self.running and not self.should_stop.is_set():
            current_time = time.time()
            
            # Maintain consistent time step
            if current_time - last_time >= self.time_step:
                self.step_simulation()
                last_time = current_time
            
            # Small sleep to prevent busy waiting
            time.sleep(0.001)
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current system state."""
        if not self.data_log:
            return {}
        return self.data_log[-1]
    
    def reset_simulation(self) -> bool:
        """Reset the simulation to initial conditions."""
        try:
            # Reset state with small random perturbation
            self.state = np.array([0.0, 0.0, np.random.uniform(-0.1, 0.1), 0.0])
            
            # Reset PID controller
            self.pid_controller.reset()
            
            # Clear data log
            self.data_log.clear()
            
            # Reset time
            self.start_time = time.time()
            
            self.logger.info("Simulation reset")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset simulation: {e}")
            return False
    
    def set_pid_parameters(self, kp: float, ki: float, kd: float) -> bool:
        """Set PID controller parameters."""
        try:
            self.pid_controller.kp = kp
            self.pid_controller.ki = ki
            self.pid_controller.kd = kd
            self.pid_controller.reset()  # Reset integral term
            
            self.logger.info(f"PID parameters set: Kp={kp}, Ki={ki}, Kd={kd}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set PID parameters: {e}")
            return False
    
    def set_target_angle(self, angle: float) -> bool:
        """Set target pendulum angle."""
        try:
            self.target_pendulum_angle = angle
            self.logger.info(f"Target angle set to {math.degrees(angle):.2f} degrees")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set target angle: {e}")
            return False
    
    def enable_control(self) -> bool:
        """Enable PID control."""
        self.control_enabled = True
        self.pid_controller.reset()
        self.logger.info("Control enabled")
        return True
    
    def disable_control(self) -> bool:
        """Disable PID control."""
        self.control_enabled = False
        self.motor_torque = 0.0
        self.logger.info("Control disabled")
        return True
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate and return performance metrics."""
        if len(self.data_log) < 100:  # Need sufficient data
            return {}
        
        # Get recent data (last 10 seconds or 2400 samples at 240Hz)
        recent_data = self.data_log[-2400:] if len(self.data_log) > 2400 else self.data_log
        
        pendulum_angles = [d['pendulum_angle'] for d in recent_data]
        pendulum_velocities = [d['pendulum_velocity'] for d in recent_data]
        motor_torques = [d['motor_torque'] for d in recent_data]
        
        # Calculate metrics
        rms_angle_error = np.sqrt(np.mean(np.array(pendulum_angles)**2))
        max_angle_deviation = np.max(np.abs(pendulum_angles))
        settling_time = self._calculate_settling_time(pendulum_angles)
        energy_consumption = np.mean(np.abs(motor_torques))
        
        return {
            'rms_angle_error': rms_angle_error,
            'max_angle_deviation': max_angle_deviation,
            'settling_time': settling_time,
            'energy_consumption': energy_consumption,
            'stability_rating': self._calculate_stability_rating(rms_angle_error),
            'data_points': len(recent_data)
        }
    
    def _calculate_settling_time(self, angles: List[float], threshold: float = 0.05) -> float:
        """Calculate settling time for pendulum to reach within threshold of upright."""
        if not angles:
            return 0.0
        
        for i, angle in enumerate(angles):
            if abs(angle) <= threshold:
                # Check if it stays within threshold for at least 1 second
                remaining = angles[i:i+240]  # 240 samples = 1 second at 240Hz
                if len(remaining) >= 240 and all(abs(a) <= threshold for a in remaining):
                    return i * self.time_step
        
        return len(angles) * self.time_step  # Never settled
    
    def _calculate_stability_rating(self, rms_error: float) -> str:
        """Calculate stability rating based on RMS error."""
        if rms_error < 0.02:  # < ~1 degree
            return "Excellent"
        elif rms_error < 0.05:  # < ~3 degrees
            return "Good"
        elif rms_error < 0.1:  # < ~6 degrees
            return "Fair"
        else:
            return "Poor"
    
    def export_data(self, filename: Optional[str] = None) -> str:
        """Export logged data to JSON file."""
        if not filename:
            timestamp = int(time.time())
            filename = f"pendulum_data_{timestamp}.json"
        
        try:
            # Prepare data for export
            export_data = {
                'metadata': {
                    'experiment_duration': len(self.data_log) * self.time_step,
                    'sample_rate': 1.0 / self.time_step,
                    'total_samples': len(self.data_log),
                    'physical_parameters': {
                        'arm_length': self.arm_length,
                        'pendulum_length': self.pendulum_length,
                        'arm_mass': self.arm_mass,
                        'pendulum_mass': self.pendulum_mass
                    },
                    'pid_parameters': {
                        'kp': self.pid_controller.kp,
                        'ki': self.pid_controller.ki,
                        'kd': self.pid_controller.kd
                    }
                },
                'data': self.data_log,
                'performance_metrics': self.get_performance_metrics()
            }
            
            # Write to file
            filepath = Path(filename)
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Data exported to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to export data: {e}")
            return ""


# Educational demonstration functions
def demo_basic_simulation():
    """Demonstrate basic pendulum simulation."""
    print("🎯 Starting Basic Pendulum Simulation Demo")
    
    sim = RotaryInvertedPendulumSim()
    
    if sim.start_experiment():
        print("✅ Simulation started successfully")
        
        # Run for 10 seconds
        for i in range(100):
            time.sleep(0.1)
            state = sim.get_current_state()
            if state:
                angle_deg = math.degrees(state['pendulum_angle'])
                print(f"  Time: {state['timestamp']:.1f}s, Pendulum: {angle_deg:.2f}°, "
                      f"Motor: {state['motor_torque']:.3f}Nm")
        
        sim.stop_experiment()
        
        # Show performance metrics
        metrics = sim.get_performance_metrics()
        if metrics:
            print(f"\n📊 Performance Metrics:")
            print(f"  Stability: {metrics['stability_rating']}")
            print(f"  RMS Error: {math.degrees(metrics['rms_angle_error']):.2f}°")
            print(f"  Max Deviation: {math.degrees(metrics['max_angle_deviation']):.2f}°")
    
    print("🏁 Demo completed")


if __name__ == "__main__":
    demo_basic_simulation()
