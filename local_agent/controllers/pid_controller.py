"""
PID Controller Implementation for Educational Control Systems
Classical PID with educational features and analysis tools
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import time

logger = logging.getLogger(__name__)

class PIDMode(Enum):
    """PID controller modes"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    TUNING = "tuning"

@dataclass
class PIDParameters:
    """PID controller parameters"""
    Kp: float = 1.0      # Proportional gain
    Ki: float = 0.0      # Integral gain  
    Kd: float = 0.0      # Derivative gain
    
    # Practical limits
    output_min: float = -100.0   # Minimum controller output
    output_max: float = 100.0    # Maximum controller output
    integral_min: float = -50.0  # Anti-windup: minimum integral term
    integral_max: float = 50.0   # Anti-windup: maximum integral term
    
    # Derivative filtering
    derivative_filter: float = 0.1  # Low-pass filter coefficient for derivative
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'PIDParameters':
        """Create from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate PID parameters"""
        warnings = []
        
        if self.Kp < 0:
            warnings.append("Proportional gain should typically be positive")
        if self.Ki < 0:
            warnings.append("Integral gain should typically be positive")
        if self.Kd < 0:
            warnings.append("Derivative gain should typically be positive")
            
        if self.output_min >= self.output_max:
            warnings.append("Output minimum must be less than output maximum")
        if self.integral_min >= self.integral_max:
            warnings.append("Integral minimum must be less than integral maximum")
            
        if self.derivative_filter <= 0 or self.derivative_filter > 1:
            warnings.append("Derivative filter should be between 0 and 1")
            
        return warnings

@dataclass
class PIDState:
    """Internal PID controller state"""
    previous_error: float = 0.0
    integral: float = 0.0
    derivative: float = 0.0
    filtered_derivative: float = 0.0
    previous_time: Optional[float] = None
    previous_input: float = 0.0  # For derivative-on-measurement
    
    def reset(self):
        """Reset controller state"""
        self.previous_error = 0.0
        self.integral = 0.0
        self.derivative = 0.0
        self.filtered_derivative = 0.0
        self.previous_time = None
        self.previous_input = 0.0

class PIDController:
    """
    Educational PID Controller with comprehensive analysis features
    
    Features:
    - Classical PID algorithm
    - Anti-windup protection
    - Derivative filtering
    - Derivative-on-measurement option
    - Comprehensive logging for education
    - Tuning assistance
    """
    
    def __init__(self, parameters: PIDParameters):
        self.params = parameters
        self.state = PIDState()
        self.mode = PIDMode.AUTOMATIC
        
        # Performance tracking
        self.performance_history: List[Dict[str, float]] = []
        self.setpoint_history: List[float] = []
        self.output_history: List[float] = []
        self.error_history: List[float] = []
        self.time_history: List[float] = []
        
        # Tuning assistance
        self.derivative_on_measurement = False  # More stable for setpoint changes
        
        # Validate parameters
        warnings = parameters.validate()
        for warning in warnings:
            logger.warning(f"PID parameter warning: {warning}")
    
    def set_parameters(self, parameters: PIDParameters):
        """Update PID parameters"""
        self.params = parameters
        warnings = parameters.validate()
        for warning in warnings:
            logger.warning(f"PID parameter warning: {warning}")
        logger.info("PID parameters updated")
    
    def set_mode(self, mode: PIDMode):
        """Set controller mode"""
        if mode != self.mode:
            if mode == PIDMode.MANUAL:
                # Reset integral when switching to manual
                self.state.integral = 0.0
            elif mode == PIDMode.AUTOMATIC and self.mode == PIDMode.MANUAL:
                # Bump-less transfer from manual to automatic
                self.state.reset()
            
            self.mode = mode
            logger.info(f"PID mode changed to {mode.value}")
    
    def reset(self):
        """Reset controller state"""
        self.state.reset()
        self.performance_history.clear()
        self.setpoint_history.clear()
        self.output_history.clear()
        self.error_history.clear()
        self.time_history.clear()
        logger.info("PID controller reset")
    
    def compute(self, setpoint: float, measured_value: float, 
                current_time: Optional[float] = None) -> Dict[str, float]:
        """
        Compute PID controller output
        
        Returns dictionary with:
        - output: Controller output
        - error: Control error (setpoint - measured)
        - proportional: Proportional term
        - integral: Integral term  
        - derivative: Derivative term
        - dt: Time step used
        """
        if self.mode != PIDMode.AUTOMATIC:
            return {
                "output": 0.0,
                "error": setpoint - measured_value,
                "proportional": 0.0,
                "integral": 0.0,
                "derivative": 0.0,
                "dt": 0.0
            }
        
        # Time management
        if current_time is None:
            current_time = time.time()
        
        dt = 0.0
        if self.state.previous_time is not None:
            dt = current_time - self.state.previous_time
        else:
            # First iteration
            self.state.previous_time = current_time
            self.state.previous_input = measured_value
            return {
                "output": 0.0,
                "error": setpoint - measured_value,
                "proportional": 0.0,
                "integral": 0.0,
                "derivative": 0.0,
                "dt": 0.0
            }
        
        if dt <= 0:
            # Invalid time step
            return {
                "output": 0.0,
                "error": setpoint - measured_value,
                "proportional": 0.0,
                "integral": 0.0,
                "derivative": 0.0,
                "dt": 0.0
            }
        
        # Calculate error
        error = setpoint - measured_value
        
        # Proportional term
        proportional = self.params.Kp * error
        
        # Integral term with anti-windup
        self.state.integral += error * dt
        self.state.integral = np.clip(self.state.integral, 
                                    self.params.integral_min / max(self.params.Ki, 1e-6),
                                    self.params.integral_max / max(self.params.Ki, 1e-6))
        integral = self.params.Ki * self.state.integral
        
        # Derivative term
        if self.derivative_on_measurement:
            # Derivative on measurement (more stable for setpoint changes)
            derivative_input = -(measured_value - self.state.previous_input) / dt
        else:
            # Derivative on error (classical)
            derivative_input = (error - self.state.previous_error) / dt
        
        # Apply low-pass filter to derivative
        alpha = self.params.derivative_filter
        self.state.filtered_derivative = (alpha * derivative_input + 
                                        (1 - alpha) * self.state.filtered_derivative)
        derivative = self.params.Kd * self.state.filtered_derivative
        
        # Compute total output
        output_raw = proportional + integral + derivative
        output = np.clip(output_raw, self.params.output_min, self.params.output_max)
        
        # Update state
        self.state.previous_error = error
        self.state.previous_time = current_time
        self.state.previous_input = measured_value
        
        # Log performance data
        performance_data = {
            "time": current_time,
            "setpoint": setpoint,
            "measured": measured_value,
            "output": output,
            "error": error,
            "proportional": proportional,
            "integral": integral,
            "derivative": derivative,
            "dt": dt
        }
        
        self.performance_history.append(performance_data)
        self.setpoint_history.append(setpoint)
        self.output_history.append(output)
        self.error_history.append(error)
        self.time_history.append(current_time)
        
        # Limit history length for memory management
        max_history = 10000
        if len(self.performance_history) > max_history:
            self.performance_history = self.performance_history[-max_history:]
            self.setpoint_history = self.setpoint_history[-max_history:]
            self.output_history = self.output_history[-max_history:]
            self.error_history = self.error_history[-max_history:]
            self.time_history = self.time_history[-max_history:]
        
        return {
            "output": float(output),
            "error": float(error),
            "proportional": float(proportional),
            "integral": float(integral),
            "derivative": float(derivative),
            "dt": float(dt)
        }
    
    def analyze_performance(self, window_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze controller performance
        """
        if len(self.performance_history) < 2:
            return {"error": "Insufficient data for analysis"}
        
        # Use last window_size points, or all data if not specified
        if window_size is None or window_size > len(self.performance_history):
            data_slice = slice(None)
        else:
            data_slice = slice(-window_size, None)
        
        errors = np.array(self.error_history[data_slice])
        outputs = np.array(self.output_history[data_slice])
        times = np.array(self.time_history[data_slice])
        
        if len(errors) == 0:
            return {"error": "No data in specified window"}
        
        # Performance metrics
        analysis = {
            # Error statistics
            "mean_absolute_error": float(np.mean(np.abs(errors))),
            "root_mean_square_error": float(np.sqrt(np.mean(errors**2))),
            "max_absolute_error": float(np.max(np.abs(errors))),
            "error_std": float(np.std(errors)),
            
            # Settling behavior
            "final_error": float(errors[-1]),
            "steady_state_error": float(np.mean(errors[-min(100, len(errors)):])),
            
            # Output statistics
            "mean_output": float(np.mean(outputs)),
            "output_std": float(np.std(outputs)),
            "output_range": float(np.max(outputs) - np.min(outputs)),
            
            # Control effort
            "total_variation": float(np.sum(np.abs(np.diff(outputs)))),
            "output_saturation_percent": float(np.sum((outputs >= self.params.output_max) | 
                                                    (outputs <= self.params.output_min)) / len(outputs) * 100),
            
            # Timing
            "average_sample_time": float(np.mean(np.diff(times))) if len(times) > 1 else 0.0,
            "sample_time_jitter": float(np.std(np.diff(times))) if len(times) > 1 else 0.0,
            
            # Data window info
            "analysis_window_size": len(errors),
            "total_data_points": len(self.performance_history),
            "time_span": float(times[-1] - times[0]) if len(times) > 1 else 0.0
        }
        
        return analysis
    
    def suggest_tuning(self) -> Dict[str, Any]:
        """
        Provide tuning suggestions based on performance analysis
        """
        analysis = self.analyze_performance()
        
        if "error" in analysis:
            return analysis
        
        suggestions = {
            "current_parameters": self.params.to_dict(),
            "analysis": analysis,
            "suggestions": []
        }
        
        # Rule-based tuning suggestions
        mae = analysis["mean_absolute_error"]
        rmse = analysis["root_mean_square_error"]
        output_std = analysis["output_std"]
        saturation_percent = analysis["output_saturation_percent"]
        
        # High steady-state error -> increase Kp or add Ki
        if abs(analysis["steady_state_error"]) > mae * 0.5:
            if self.params.Ki == 0:
                suggestions["suggestions"].append({
                    "type": "add_integral",
                    "message": "High steady-state error detected. Consider adding integral action (Ki > 0).",
                    "suggested_Ki": self.params.Kp * 0.1
                })
            else:
                suggestions["suggestions"].append({
                    "type": "increase_proportional",
                    "message": "High steady-state error detected. Consider increasing Kp.",
                    "suggested_Kp": self.params.Kp * 1.2
                })
        
        # High oscillation -> reduce Kp or Kd
        if output_std > np.mean(np.abs(self.output_history)) * 0.3:
            suggestions["suggestions"].append({
                "type": "reduce_oscillation",
                "message": "High output variation detected. Consider reducing Kp or adding/increasing Kd.",
                "suggested_Kp": self.params.Kp * 0.8,
                "suggested_Kd": max(self.params.Kd * 1.5, self.params.Kp * 0.05)
            })
        
        # Output saturation -> reduce gains or increase limits
        if saturation_percent > 10:
            suggestions["suggestions"].append({
                "type": "output_saturation",
                "message": f"Output saturated {saturation_percent:.1f}% of the time. Consider reducing gains or increasing output limits.",
                "suggested_scaling": 0.8
            })
        
        # Fast response but stable -> might increase Kp
        if mae < rmse * 0.5 and output_std < np.mean(np.abs(self.output_history)) * 0.1:
            suggestions["suggestions"].append({
                "type": "increase_response",
                "message": "System appears stable with low error. Consider increasing Kp for faster response.",
                "suggested_Kp": self.params.Kp * 1.3
            })
        
        return suggestions
    
    def get_step_response_analysis(self, setpoint_change_threshold: float = 0.1) -> Dict[str, Any]:
        """
        Analyze step response characteristics from historical data
        """
        if len(self.performance_history) < 10:
            return {"error": "Insufficient data for step response analysis"}
        
        # Find step changes in setpoint
        setpoints = np.array(self.setpoint_history)
        setpoint_changes = np.abs(np.diff(setpoints))
        step_indices = np.where(setpoint_changes > setpoint_change_threshold)[0]
        
        if len(step_indices) == 0:
            return {"error": "No significant setpoint changes found"}
        
        # Analyze the most recent step response
        step_start = step_indices[-1] + 1
        step_end = min(step_start + 500, len(self.performance_history))  # Analyze next 500 points
        
        if step_end - step_start < 20:
            return {"error": "Insufficient data after step change"}
        
        # Extract step response data
        step_times = np.array(self.time_history[step_start:step_end])
        step_errors = np.array(self.error_history[step_start:step_end])
        step_outputs = np.array(self.output_history[step_start:step_end])
        step_setpoints = np.array(self.setpoint_history[step_start:step_end])
        
        # Normalize time to start from 0
        step_times = step_times - step_times[0]
        
        # Calculate characteristics
        final_setpoint = step_setpoints[-1]
        initial_error = step_errors[0]
        final_errors = step_errors[-min(20, len(step_errors)):]  # Last 20 points
        steady_state_error = np.mean(final_errors)
        
        # Settling time (2% criterion)
        settling_threshold = 0.02 * abs(initial_error)
        settled_mask = np.abs(step_errors - steady_state_error) <= settling_threshold
        
        settling_time = None
        if np.any(settled_mask):
            # Find when it first settles and stays settled
            for i in range(len(settled_mask) - 10):
                if np.all(settled_mask[i:i+10]):  # Settled for 10 consecutive points
                    settling_time = step_times[i]
                    break
        
        # Rise time (time to reach 90% of final value)
        target_90_percent = 0.9 * initial_error
        rise_indices = np.where(np.abs(step_errors) <= abs(target_90_percent))[0]
        rise_time = step_times[rise_indices[0]] if len(rise_indices) > 0 else None
        
        # Overshoot
        if initial_error > 0:  # Step up
            min_error = np.min(step_errors)
            overshoot = max(0, (steady_state_error - min_error) / initial_error * 100)
        else:  # Step down
            max_error = np.max(step_errors)
            overshoot = max(0, (max_error - steady_state_error) / abs(initial_error) * 100)
        
        return {
            "initial_error": float(initial_error),
            "steady_state_error": float(steady_state_error),
            "settling_time": float(settling_time) if settling_time is not None else None,
            "rise_time": float(rise_time) if rise_time is not None else None,
            "overshoot_percent": float(overshoot),
            "step_magnitude": float(abs(initial_error)),
            "response_time_span": float(step_times[-1]),
            "data_points_analyzed": len(step_errors)
        }
    
    def export_performance_data(self) -> Dict[str, List[float]]:
        """
        Export performance data for external analysis
        """
        return {
            "time": self.time_history.copy(),
            "setpoint": self.setpoint_history.copy(),
            "error": self.error_history.copy(),
            "output": self.output_history.copy(),
            "parameters": self.params.to_dict()
        }
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current controller state"""
        return {
            "mode": self.mode.value,
            "parameters": self.params.to_dict(),
            "internal_state": {
                "previous_error": self.state.previous_error,
                "integral": self.state.integral,
                "derivative": self.state.derivative,
                "filtered_derivative": self.state.filtered_derivative
            },
            "data_points": len(self.performance_history),
            "derivative_on_measurement": self.derivative_on_measurement
        }