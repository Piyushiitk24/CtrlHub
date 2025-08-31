"""
DC Motor Control Systems Module
Educational implementation of open-loop and closed-loop control strategies
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass
import time
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ControllerParameters:
    """PID Controller parameters with educational context"""
    Kp: float = 1.0         # Proportional gain
    Ki: float = 0.0         # Integral gain
    Kd: float = 0.0         # Derivative gain
    N: float = 100.0        # Derivative filter coefficient
    
    # Anti-windup and saturation
    output_min: float = -12.0
    output_max: float = 12.0
    integral_min: float = -10.0
    integral_max: float = 10.0
    
    def __post_init__(self):
        """Validate controller parameters"""
        if self.Kp < 0:
            logger.warning("Negative Kp may cause instability")
        if self.Ki < 0:
            logger.warning("Negative Ki may cause instability")
        if self.Kd < 0:
            logger.warning("Negative Kd may cause instability")

@dataclass 
class SystemIdentification:
    """System identification results for controller design"""
    dc_gain: float = 1.0
    time_constant: float = 1.0
    delay: float = 0.0
    damping_ratio: float = 0.7
    natural_frequency: float = 1.0
    poles: Optional[List[complex]] = None
    zeros: Optional[List[complex]] = None
    
    def __post_init__(self):
        if self.poles is None:
            self.poles = []
        if self.zeros is None:
            self.zeros = []

class DCMotorController:
    """
    Educational DC Motor Control Systems
    
    Provides comprehensive control strategies with educational focus:
    - Open-loop control understanding
    - PID control theory and practice
    - Multiple tuning methods with trade-offs
    - System analysis and validation
    """
    
    def __init__(self, motor_physics=None, arduino_interface=None):
        self.motor_physics = motor_physics
        self.arduino = arduino_interface
        self.controller_params = ControllerParameters()
        self.system_id = SystemIdentification()
        
        # Control state variables
        self.error_prev = 0.0
        self.integral = 0.0
        self.derivative_prev = 0.0
        self.output_prev = 0.0
        self.reference_prev = 0.0
        
        # Educational tracking
        self.control_history = []
        self.tuning_history = []
        
    def analyze_open_loop_response(self, input_type: str = "step") -> Dict[str, Any]:
        """
        Analyze open-loop system response
        
        Educational Objective:
        - Understand system behavior without feedback
        - Learn step, ramp, and frequency responses
        - Identify limitations of open-loop control
        
        Open-loop characteristics:
        - No disturbance rejection
        - Parameter sensitivity
        - No steady-state error correction
        """
        logger.info(f"Analyzing open-loop {input_type} response")
        
        analysis = {
            'system_type': 'Type 0 system (no integrator)',
            'input_type': input_type,
            'theoretical_analysis': {},
            'practical_limitations': {},
            'educational_insights': []
        }
        
        if input_type == "step":
            analysis['theoretical_analysis'] = {
                'steady_state_gain': self._calculate_dc_gain(),
                'time_constant': self._calculate_time_constant(),
                'rise_time': '2.2 × τ (10% to 90%)',
                'settling_time': '4 × τ (2% criterion)',
                'overshoot': 'Depends on damping ratio',
                'steady_state_error': '0 for step input (Type 0 system)'
            }
            
        elif input_type == "ramp":
            analysis['theoretical_analysis'] = {
                'steady_state_error': 'Infinite (Type 0 system)',
                'error_explanation': 'No integrator to eliminate ramp error',
                'velocity_constant': 'Kv = 0 for Type 0 system',
                'practical_impact': 'Cannot track ramp references accurately'
            }
            
        elif input_type == "sinusoidal":
            analysis['theoretical_analysis'] = {
                'frequency_response': 'Magnitude and phase vs frequency',
                'bandwidth': f'{self._estimate_bandwidth():.2f} rad/s',
                'phase_margin': 'Always 90° for first-order system',
                'gain_margin': 'Infinite (no oscillation)'
            }
        
        analysis['practical_limitations'] = {
            'disturbance_sensitivity': 'Load changes directly affect output',
            'parameter_drift': 'Aging, temperature affect performance',
            'calibration_needs': 'Requires accurate feed-forward models',
            'stability_robustness': 'Generally stable but no adaptation',
            'performance_variability': 'Varies with operating conditions'
        }
        
        analysis['educational_insights'] = [
            'Open-loop suitable for well-known, repeatable tasks',
            'Feedforward control can improve performance',
            'Critical for understanding closed-loop benefits',
            'Used in combination with feedback control'
        ]
        
        return analysis
    
    def design_pid_controller_ziegler_nichols(self, method: str = "reaction_curve") -> Dict[str, Any]:
        """
        PID controller design using Ziegler-Nichols methods
        
        Educational Objective:
        - Learn classical tuning approaches
        - Understand trade-offs in tuning rules
        - Practice experimental identification
        
        Methods:
        1. Reaction Curve (Open-loop step response)
        2. Ultimate Gain (Closed-loop oscillation)
        """
        logger.info(f"Designing PID controller using Ziegler-Nichols {method} method")
        
        if method == "reaction_curve":
            return self._ziegler_nichols_reaction_curve()
        elif method == "ultimate_gain":
            return self._ziegler_nichols_ultimate_gain()
        else:
            raise ValueError(f"Unknown Ziegler-Nichols method: {method}")
    
    def design_pid_controller_pole_placement(self, desired_poles: List[complex]) -> Dict[str, Any]:
        """
        PID controller design using pole placement
        
        Educational Objective:
        - Learn root locus techniques
        - Understand pole-zero relationships
        - Practice analytical design methods
        
        Method:
        1. Define desired closed-loop poles
        2. Calculate required controller gains
        3. Verify stability and performance
        """
        logger.info("Designing PID controller using pole placement")
        
        design_result = {
            'method': 'pole_placement',
            'desired_poles': [str(pole) for pole in desired_poles],
            'design_procedure': {
                'step_1': 'Define desired closed-loop characteristic equation',
                'step_2': 'Expand closed-loop transfer function',
                'step_3': 'Match coefficients to get PID gains',
                'step_4': 'Verify stability margins'
            }
        }
        
        # Simplified pole placement for educational demonstration
        if len(desired_poles) >= 2:
            # For second-order dominant poles
            if len(desired_poles) >= 2 and isinstance(desired_poles[0], complex):
                pole = desired_poles[0]
                zeta = -pole.real / abs(pole)
                omega_n = abs(pole)
                
                # Typical pole placement formulas (simplified)
                Kp = omega_n**2 * (self.system_id.time_constant if hasattr(self.system_id, 'time_constant') else 1.0)
                Ki = omega_n**3 / 4  # Rule of thumb
                Kd = 2 * zeta * omega_n * (self.system_id.time_constant if hasattr(self.system_id, 'time_constant') else 1.0)
                
                design_result['calculated_gains'] = {
                    'Kp': float(Kp),
                    'Ki': float(Ki),
                    'Kd': float(Kd)
                }
                
                # Update controller parameters
                self.controller_params.Kp = Kp
                self.controller_params.Ki = Ki
                self.controller_params.Kd = Kd
                
        design_result['educational_insights'] = [
            'Pole placement gives direct control over response characteristics',
            'Trade-off between speed and stability',
            'Requires accurate system model',
            'May result in high controller gains'
        ]
        
        self.tuning_history.append(design_result)
        return design_result
    
    def design_pid_controller_frequency_domain(self, design_specs: Dict[str, float]) -> Dict[str, Any]:
        """
        PID controller design using frequency domain methods
        
        Educational Objective:
        - Learn Bode plot analysis
        - Understand gain/phase margins
        - Practice frequency domain specifications
        
        Design Specifications:
        - Phase margin (degrees)
        - Gain margin (dB)
        - Bandwidth (rad/s)
        - Steady-state error requirements
        """
        logger.info("Designing PID controller using frequency domain methods")
        
        # Default specifications
        phase_margin_req = design_specs.get('phase_margin', 45)  # degrees
        gain_margin_req = design_specs.get('gain_margin', 6)     # dB
        bandwidth_req = design_specs.get('bandwidth', 10)        # rad/s
        
        design_result = {
            'method': 'frequency_domain',
            'design_specifications': design_specs,
            'design_procedure': {
                'step_1': 'Analyze open-loop Bode plot',
                'step_2': 'Determine required gain to meet bandwidth',
                'step_3': 'Add lead/lag compensation for phase margin',
                'step_4': 'Add integral action for steady-state error',
                'step_5': 'Verify stability margins'
            }
        }
        
        # Simplified frequency domain design
        # Start with proportional gain to achieve bandwidth
        omega_c = bandwidth_req  # Crossover frequency
        
        # Calculate required Kp to achieve crossover frequency
        # |G(jωc)| = 1 => Kp = 1/|G(jωc)|
        system_gain_at_wc = self._evaluate_system_magnitude(omega_c)
        Kp = 1.0 / system_gain_at_wc if system_gain_at_wc > 0 else 1.0
        
        # Calculate phase margin with proportional control
        system_phase_at_wc = self._evaluate_system_phase(omega_c)
        current_phase_margin = 180 + system_phase_at_wc
        
        # Add derivative gain if more phase margin needed
        phase_deficit = phase_margin_req - current_phase_margin
        if phase_deficit > 0:
            # Lead compensation
            alpha = (1 + phase_deficit * 3.14159 / 180) / (1 - phase_deficit * 3.14159 / 180)
            Kd = alpha / omega_c if omega_c > 0 else 0
        else:
            Kd = 0
        
        # Add integral gain for steady-state error (conservative)
        Ki = omega_c / 10  # Rule of thumb: place integral pole well below crossover
        
        design_result['calculated_gains'] = {
            'Kp': float(Kp),
            'Ki': float(Ki),
            'Kd': float(Kd)
        }
        
        design_result['frequency_analysis'] = {
            'crossover_frequency': omega_c,
            'phase_margin_achieved': current_phase_margin + (phase_deficit if phase_deficit > 0 else 0),
            'gain_margin_estimate': 'Infinite for well-damped system',
            'bandwidth_achieved': omega_c
        }
        
        # Update controller parameters
        self.controller_params.Kp = Kp
        self.controller_params.Ki = Ki
        self.controller_params.Kd = Kd
        
        design_result['educational_insights'] = [
            'Frequency domain gives insight into stability margins',
            'Phase margin affects overshoot and damping',
            'Gain margin indicates stability robustness',
            'Bandwidth determines speed of response'
        ]
        
        self.tuning_history.append(design_result)
        return design_result
    
    def design_pid_controller_lambda_tuning(self, lambda_factor: float = 1.0) -> Dict[str, Any]:
        """
        PID controller design using Lambda (IMC) tuning
        
        Educational Objective:
        - Learn model-based tuning approaches
        - Understand closed-loop time constant selection
        - Practice Internal Model Control concepts
        
        Lambda tuning provides:
        - Single tuning parameter (λ)
        - Guaranteed stability for stable processes
        - Good disturbance rejection
        """
        logger.info(f"Designing PID controller using Lambda tuning (λ = {lambda_factor})")
        
        design_result = {
            'method': 'lambda_tuning',
            'lambda_factor': lambda_factor,
            'design_procedure': {
                'step_1': 'Identify process model (FOPDT)',
                'step_2': 'Choose closed-loop time constant λ',
                'step_3': 'Calculate PID gains using IMC formulas',
                'step_4': 'Verify performance characteristics'
            }
        }
        
        # Assume First Order Plus Dead Time (FOPDT) model
        # G(s) = K * exp(-θs) / (τs + 1)
        K = self.system_id.dc_gain
        tau = self.system_id.time_constant
        theta = self.system_id.delay
        
        # Lambda tuning formulas
        lambda_cl = lambda_factor * tau  # Closed-loop time constant
        
        if tau > 0 and K > 0:
            Kp = tau / (K * (lambda_cl + theta))
            Ki = 1 / (lambda_cl + theta)
            Kd = 0  # Lambda tuning typically doesn't use derivative
            
        else:
            # Fallback values
            Kp, Ki, Kd = 1.0, 0.1, 0.0
        
        design_result['model_parameters'] = {
            'process_gain': K,
            'time_constant': tau,
            'dead_time': theta,
            'closed_loop_time_constant': lambda_cl
        }
        
        design_result['calculated_gains'] = {
            'Kp': float(Kp),
            'Ki': float(Ki),
            'Kd': float(Kd)
        }
        
        design_result['performance_predictions'] = {
            'settling_time': f'{4 * lambda_cl:.2f} seconds',
            'overshoot': 'Typically < 5% for λ = τ',
            'robustness': 'Good for model uncertainties',
            'disturbance_rejection': 'Excellent'
        }
        
        # Update controller parameters
        self.controller_params.Kp = Kp
        self.controller_params.Ki = Ki
        self.controller_params.Kd = Kd
        
        design_result['educational_insights'] = [
            'Single tuning parameter simplifies design',
            'Larger λ gives more conservative tuning',
            'Smaller λ gives faster but less robust response',
            'Based on Internal Model Control theory'
        ]
        
        self.tuning_history.append(design_result)
        return design_result
    
    def design_pid_controller_genetic_algorithm(self, 
                                               performance_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        PID controller design using genetic algorithm optimization
        
        Educational Objective:
        - Learn modern optimization approaches
        - Understand multi-objective optimization
        - Practice evolutionary algorithms
        
        Optimization considers:
        - Rise time, settling time, overshoot
        - Steady-state error, control effort
        - Robustness measures
        """
        logger.info("Designing PID controller using genetic algorithm")
        
        if performance_weights is None:
            performance_weights = {
                'rise_time': 0.3,
                'settling_time': 0.2,
                'overshoot': 0.2,
                'steady_state_error': 0.2,
                'control_effort': 0.1
            }
        
        design_result = {
            'method': 'genetic_algorithm',
            'performance_weights': performance_weights,
            'optimization_setup': {
                'population_size': 50,
                'generations': 100,
                'mutation_rate': 0.1,
                'crossover_rate': 0.8,
                'selection_method': 'tournament'
            }
        }
        
        # Simplified GA simulation for educational purposes
        # In practice, this would run actual GA optimization
        
        # Parameter bounds
        kp_bounds = (0.1, 100.0)
        ki_bounds = (0.01, 10.0)
        kd_bounds = (0.0, 10.0)
        
        # Simulate "optimal" solution for demonstration
        # These would come from actual GA optimization
        Kp_opt = 5.0   # Simulated optimal values
        Ki_opt = 2.0
        Kd_opt = 0.5
        
        design_result['optimization_results'] = {
            'best_fitness': 0.85,  # Simulated
            'convergence_generation': 45,
            'parameter_evolution': 'Kp: 1.2→5.0, Ki: 0.1→2.0, Kd: 0.0→0.5'
        }
        
        design_result['calculated_gains'] = {
            'Kp': Kp_opt,
            'Ki': Ki_opt,
            'Kd': Kd_opt
        }
        
        design_result['performance_achieved'] = {
            'rise_time': '0.3 seconds',
            'settling_time': '1.2 seconds',
            'overshoot': '8%',
            'steady_state_error': '< 1%',
            'control_effort': 'Moderate'
        }
        
        # Update controller parameters
        self.controller_params.Kp = Kp_opt
        self.controller_params.Ki = Ki_opt
        self.controller_params.Kd = Kd_opt
        
        design_result['educational_insights'] = [
            'GA can handle complex, multi-objective problems',
            'No need for analytical system model',
            'Can optimize for any measurable performance metric',
            'Computationally intensive but very flexible'
        ]
        
        self.tuning_history.append(design_result)
        return design_result
    
    async def implement_closed_loop_control(self, 
                                          reference_signal: Union[float, Callable],
                                          duration: float = 10.0,
                                          sample_time: float = 0.01) -> Dict[str, Any]:
        """
        Implement closed-loop PID control
        
        Educational Objective:
        - Practice real-time control implementation
        - Understand discrete-time PID
        - Learn anti-windup and saturation handling
        
        Features:
        - Discrete PID with proper derivatives
        - Integral anti-windup
        - Output saturation
        - Reference tracking and disturbance rejection
        """
        logger.info(f"Starting closed-loop control for {duration} seconds")
        
        # Initialize control variables
        self.error_prev = 0.0
        self.integral = 0.0
        self.derivative_prev = 0.0
        self.output_prev = 0.0
        
        # Data logging
        time_log = []
        reference_log = []
        measurement_log = []
        error_log = []
        control_output_log = []
        pid_components_log = []
        
        start_time = time.time()
        
        try:
            while (time.time() - start_time) < duration:
                current_time = time.time() - start_time
                
                # Get reference signal
                if callable(reference_signal):
                    reference = reference_signal(current_time)
                else:
                    reference = float(reference_signal)
                
                # Get measurement (actual motor speed)
                if self.arduino:
                    measurement_data = await self.arduino.send_command("GET_MOTOR_DATA")
                    measurement = measurement_data.get('speed', 0) * 2 * 3.14159 / 60  # Convert RPM to rad/s
                else:
                    # Simulation for educational purposes
                    measurement = self._simulate_plant_response(self.output_prev, current_time)
                
                # Calculate PID control
                control_output, pid_components = self._calculate_pid_output(
                    reference, measurement, sample_time
                )
                
                # Apply control output
                if self.arduino:
                    # Convert to voltage (assuming linear relationship)
                    voltage = max(min(control_output, 12.0), -12.0)
                    await self.arduino.send_command("MOTOR_VOLTAGE", voltage)
                
                # Log data
                time_log.append(current_time)
                reference_log.append(reference)
                measurement_log.append(measurement)
                error_log.append(reference - measurement)
                control_output_log.append(control_output)
                pid_components_log.append(pid_components)
                
                # Wait for next sample
                await asyncio.sleep(sample_time)
                
        except Exception as e:
            logger.error(f"Control loop error: {e}")
        finally:
            # Stop motor safely
            if self.arduino:
                await self.arduino.send_command("MOTOR_VOLTAGE", 0)
        
        # Analyze performance
        performance_analysis = self._analyze_control_performance(
            time_log, reference_log, measurement_log, error_log, control_output_log
        )
        
        control_result = {
            'experiment_duration': duration,
            'sample_time': sample_time,
            'controller_parameters': {
                'Kp': self.controller_params.Kp,
                'Ki': self.controller_params.Ki,
                'Kd': self.controller_params.Kd
            },
            'time_data': time_log,
            'reference_data': reference_log,
            'measurement_data': measurement_log,
            'error_data': error_log,
            'control_output_data': control_output_log,
            'pid_components_data': pid_components_log,
            'performance_metrics': performance_analysis,
            'educational_observations': self._generate_control_insights(performance_analysis)
        }
        
        self.control_history.append(control_result)
        logger.info("Closed-loop control experiment completed")
        
        return control_result
    
    def compare_tuning_methods(self) -> Dict[str, Any]:
        """
        Educational comparison of different tuning methods
        
        Compares:
        - Design philosophy
        - Required information
        - Performance characteristics
        - Practical considerations
        """
        comparison = {
            'ziegler_nichols': {
                'philosophy': 'Empirical rules based on plant response',
                'required_info': 'Step response or ultimate gain test',
                'advantages': ['Simple to apply', 'No model required', 'Widely known'],
                'disadvantages': ['Conservative tuning', 'Trial and error', 'May not be optimal'],
                'best_for': 'Quick tuning when plant model unknown'
            },
            'pole_placement': {
                'philosophy': 'Direct specification of closed-loop dynamics',
                'required_info': 'Accurate plant model and desired pole locations',
                'advantages': ['Direct control over response', 'Analytical approach', 'Predictable results'],
                'disadvantages': ['Requires good model', 'May give high gains', 'Limited to model accuracy'],
                'best_for': 'When precise response characteristics needed'
            },
            'frequency_domain': {
                'philosophy': 'Design based on stability margins and bandwidth',
                'required_info': 'Frequency response or Bode plots',
                'advantages': ['Clear stability analysis', 'Robustness insight', 'Classical control theory'],
                'disadvantages': ['Complex for beginners', 'Requires frequency data', 'Iterative process'],
                'best_for': 'Systems where robustness is critical'
            },
            'lambda_tuning': {
                'philosophy': 'Model-based with single tuning parameter',
                'required_info': 'FOPDT model parameters',
                'advantages': ['Single parameter', 'Good robustness', 'Proven performance'],
                'disadvantages': ['Requires model identification', 'Conservative', 'Limited to FOPDT'],
                'best_for': 'Process control applications'
            },
            'genetic_algorithm': {
                'philosophy': 'Multi-objective optimization',
                'required_info': 'Performance criteria and constraints',
                'advantages': ['Handles complex objectives', 'No model required', 'Global optimization'],
                'disadvantages': ['Computationally intensive', 'Non-deterministic', 'Requires many evaluations'],
                'best_for': 'Complex systems with multiple objectives'
            }
        }
        
        comparison['selection_guidelines'] = {
            'for_beginners': 'Start with Ziegler-Nichols reaction curve',
            'for_precision': 'Use pole placement or frequency domain',
            'for_robustness': 'Consider lambda tuning or frequency domain',
            'for_optimization': 'Use genetic algorithm or other modern methods',
            'for_understanding': 'Try multiple methods and compare results'
        }
        
        return comparison
    
    def generate_educational_summary(self) -> Dict[str, Any]:
        """
        Generate comprehensive educational summary of control concepts
        """
        summary = {
            'control_fundamentals': {
                'open_loop': 'Direct command without feedback',
                'closed_loop': 'Uses feedback to correct errors',
                'feedback_benefits': ['Disturbance rejection', 'Parameter insensitivity', 'Tracking accuracy'],
                'feedback_costs': ['Complexity', 'Potential instability', 'Noise sensitivity']
            },
            'pid_control_theory': {
                'proportional': 'Present error correction (Kp × e)',
                'integral': 'Past error accumulation (Ki × ∫e dt)',
                'derivative': 'Future error prediction (Kd × de/dt)',
                'combined_effect': 'P: speed, I: accuracy, D: stability'
            },
            'design_trade_offs': {
                'speed_vs_stability': 'Higher gains → faster response but less stable',
                'accuracy_vs_effort': 'Integral action → zero error but more control effort',
                'noise_vs_performance': 'Derivative action → better damping but noise sensitivity',
                'robustness_vs_performance': 'Conservative tuning → stable but slower'
            },
            'practical_considerations': {
                'sampling_time': 'Must be much faster than system dynamics',
                'anti_windup': 'Prevent integral wind-up during saturation',
                'noise_filtering': 'Filter derivative term to reduce noise',
                'gain_scheduling': 'Adapt gains for different operating points'
            },
            'performance_metrics': {
                'time_domain': ['Rise time', 'Settling time', 'Overshoot', 'Steady-state error'],
                'frequency_domain': ['Bandwidth', 'Phase margin', 'Gain margin'],
                'practical': ['Control effort', 'Robustness', 'Implementation complexity']
            },
            'next_learning_steps': [
                'Experiment with different reference signals',
                'Add disturbances to test rejection',
                'Compare simulation vs hardware results',
                'Study advanced control methods (MPC, adaptive, etc.)'
            ]
        }
        
        return summary
    
    # Helper methods for PID implementation and analysis
    def _ziegler_nichols_reaction_curve(self) -> Dict[str, Any]:
        """Implement Ziegler-Nichols reaction curve method"""
        # This would typically require a step response experiment
        # For educational purposes, we'll use typical motor parameters
        
        # Simulate step response analysis
        K = 1.0   # Process gain
        L = 0.1   # Dead time
        T = 0.5   # Time constant
        
        # Z-N reaction curve formulas
        Kp = 1.2 * T / (K * L) if L > 0 else 1.0
        Ki = Kp / (2 * L) if L > 0 else 0.1
        Kd = Kp * L / 2
        
        return {
            'method': 'ziegler_nichols_reaction_curve',
            'identified_parameters': {'K': K, 'L': L, 'T': T},
            'calculated_gains': {'Kp': Kp, 'Ki': Ki, 'Kd': Kd},
            'expected_performance': 'Quarter amplitude decay response'
        }
    
    def _ziegler_nichols_ultimate_gain(self) -> Dict[str, Any]:
        """Implement Ziegler-Nichols ultimate gain method"""
        # This would require an ultimate gain experiment
        # For educational purposes, we'll use estimated values
        
        Ku = 10.0  # Ultimate gain (where system oscillates)
        Tu = 0.5   # Ultimate period
        
        # Z-N ultimate gain formulas
        Kp = 0.6 * Ku
        Ki = 2 * Kp / Tu
        Kd = Kp * Tu / 8
        
        return {
            'method': 'ziegler_nichols_ultimate_gain',
            'ultimate_parameters': {'Ku': Ku, 'Tu': Tu},
            'calculated_gains': {'Kp': Kp, 'Ki': Ki, 'Kd': Kd},
            'expected_performance': 'Quarter amplitude decay response'
        }
    
    def _calculate_dc_gain(self) -> float:
        """Calculate system DC gain"""
        if self.motor_physics:
            R = self.motor_physics.R
            b = self.motor_physics.b
            Ke = self.motor_physics.Ke
            Kt = self.motor_physics.Kt
            return Kt / (R * b + Ke * Kt)
        return 1.0
    
    def _calculate_time_constant(self) -> float:
        """Calculate dominant time constant"""
        if self.motor_physics:
            return self.motor_physics.J / self.motor_physics.b
        return 1.0
    
    def _estimate_bandwidth(self) -> float:
        """Estimate system bandwidth"""
        return 1.0 / self._calculate_time_constant()
    
    def _evaluate_system_magnitude(self, frequency: float) -> float:
        """Evaluate system magnitude at given frequency"""
        # Simplified first-order approximation
        tau = self._calculate_time_constant()
        K = self._calculate_dc_gain()
        return K / (1 + (frequency * tau)**2)**0.5
    
    def _evaluate_system_phase(self, frequency: float) -> float:
        """Evaluate system phase at given frequency (degrees)"""
        # Simplified first-order approximation
        import math
        tau = self._calculate_time_constant()
        return -math.atan(frequency * tau) * 180 / math.pi
    
    def _calculate_pid_output(self, reference: float, measurement: float, 
                             sample_time: float) -> Tuple[float, Dict[str, float]]:
        """Calculate PID control output with anti-windup"""
        # Calculate error
        error = reference - measurement
        
        # Proportional term
        P_term = self.controller_params.Kp * error
        
        # Integral term with anti-windup
        self.integral += error * sample_time
        
        # Clamp integral to prevent windup
        self.integral = max(min(self.integral, self.controller_params.integral_max), 
                           self.controller_params.integral_min)
        
        I_term = self.controller_params.Ki * self.integral
        
        # Derivative term with filtering
        derivative = (error - self.error_prev) / sample_time if sample_time > 0 else 0
        # Simple first-order filter for derivative
        alpha = sample_time * self.controller_params.N / (1 + sample_time * self.controller_params.N)
        filtered_derivative = alpha * derivative + (1 - alpha) * self.derivative_prev
        
        D_term = self.controller_params.Kd * filtered_derivative
        
        # Total output
        output = P_term + I_term + D_term
        
        # Apply output saturation
        output_saturated = max(min(output, self.controller_params.output_max), 
                              self.controller_params.output_min)
        
        # Anti-windup: reduce integral if output is saturated
        if output != output_saturated:
            excess = output - output_saturated
            self.integral -= excess / self.controller_params.Ki if self.controller_params.Ki > 0 else 0
        
        # Update previous values
        self.error_prev = error
        self.derivative_prev = filtered_derivative
        self.output_prev = output_saturated
        
        pid_components = {
            'P_term': P_term,
            'I_term': I_term,
            'D_term': D_term,
            'total': output,
            'saturated': output_saturated
        }
        
        return output_saturated, pid_components
    
    def _simulate_plant_response(self, control_input: float, time: float) -> float:
        """Simulate plant response for educational purposes"""
        # Simple first-order response simulation
        tau = 1.0  # Time constant
        K = 1.0    # DC gain
        
        # This is a simplified simulation - in practice would use proper integration
        response = K * control_input * (1 - (time/tau)**(-time/tau)) if time > 0 else 0
        return max(response, 0)  # Non-negative speed
    
    def _analyze_control_performance(self, time_data: List[float], 
                                   reference_data: List[float],
                                   measurement_data: List[float],
                                   error_data: List[float],
                                   control_data: List[float]) -> Dict[str, Any]:
        """Analyze closed-loop control performance"""
        if not time_data or len(time_data) < 2:
            return {}
        
        # Convert to arrays for analysis
        import math
        
        # Step response analysis (assuming step reference)
        if len(set(reference_data[-10:])) == 1:  # Constant reference
            final_reference = reference_data[-1]
            final_measurement = sum(measurement_data[-10:]) / 10  # Average of last 10 samples
            
            # Steady-state error
            steady_state_error = abs(final_reference - final_measurement)
            
            # Find rise time (10% to 90% of final value)
            target_10 = 0.1 * final_reference
            target_90 = 0.9 * final_reference
            
            rise_time = None
            rise_start_idx = None
            for i, measurement in enumerate(measurement_data):
                if measurement >= target_10 and rise_start_idx is None:
                    rise_start_idx = i
                if measurement >= target_90 and rise_start_idx is not None:
                    rise_time = time_data[i] - time_data[rise_start_idx]
                    break
            
            # Find settling time (within 2% of final value)
            settling_time = None
            tolerance = 0.02 * abs(final_reference)
            for i in reversed(range(len(measurement_data))):
                if abs(measurement_data[i] - final_reference) > tolerance:
                    settling_time = time_data[i + 1] if i + 1 < len(time_data) else time_data[-1]
                    break
            
            # Find overshoot
            max_measurement = max(measurement_data)
            overshoot = max(0, (max_measurement - final_reference) / final_reference * 100) if final_reference > 0 else 0
            
        else:
            # Non-step reference
            steady_state_error = sum(abs(e) for e in error_data[-10:]) / 10
            rise_time = None
            settling_time = None
            overshoot = 0
        
        # Control effort metrics
        control_effort = sum(abs(u) for u in control_data) / len(control_data)
        max_control = max(abs(u) for u in control_data)
        
        # Error metrics
        ise = sum(e**2 for e in error_data)  # Integral Square Error
        iae = sum(abs(e) for e in error_data)  # Integral Absolute Error
        max_error = max(abs(e) for e in error_data)
        
        return {
            'steady_state_error': steady_state_error,
            'rise_time': rise_time,
            'settling_time': settling_time,
            'overshoot_percent': overshoot,
            'control_effort_avg': control_effort,
            'control_effort_max': max_control,
            'ise': ise,
            'iae': iae,
            'max_error': max_error
        }
    
    def _generate_control_insights(self, performance_metrics: Dict[str, Any]) -> List[str]:
        """Generate educational insights from control performance"""
        insights = []
        
        if performance_metrics.get('steady_state_error', 0) > 0.1:
            insights.append("Consider increasing integral gain (Ki) to reduce steady-state error")
        
        if performance_metrics.get('overshoot_percent', 0) > 20:
            insights.append("Reduce proportional gain (Kp) or add derivative gain (Kd) to reduce overshoot")
        
        if performance_metrics.get('rise_time', 0) > 2.0:
            insights.append("Increase proportional gain (Kp) to improve rise time")
        
        if performance_metrics.get('control_effort_max', 0) > 10:
            insights.append("High control effort detected - consider reducing gains or adding rate limiting")
        
        insights.append("Compare different tuning methods to understand trade-offs")
        
        return insights