"""
Simulation Engine for Control Systems Education
Orchestrates real-time and offline simulations with educational focus
"""

import asyncio
import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import time
import threading
from queue import Queue, Empty

from ..models.dc_motor import DCMotorModel, MotorParameters
from ..hardware.arduino_interface import ArduinoInterface

logger = logging.getLogger(__name__)

class SimulationMode(Enum):
    """Simulation execution modes"""
    OFFLINE = "offline"          # Pure simulation, no hardware
    HARDWARE = "hardware"        # Real hardware only
    HYBRID = "hybrid"           # Hardware-in-the-loop simulation
    VALIDATION = "validation"    # Compare simulation vs hardware

@dataclass
class SimulationConfig:
    """Configuration for simulation runs"""
    mode: SimulationMode
    duration: float = 10.0           # Simulation duration (seconds)
    dt: float = 0.01                # Time step (seconds)
    sample_rate: float = 100.0       # Data sampling rate (Hz)
    auto_save: bool = True           # Auto-save results
    real_time: bool = False          # Real-time execution
    hardware_timeout: float = 1.0    # Hardware communication timeout
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "duration": self.duration,
            "dt": self.dt,
            "sample_rate": self.sample_rate,
            "auto_save": self.auto_save,
            "real_time": self.real_time,
            "hardware_timeout": self.hardware_timeout
        }

@dataclass
class SimulationResults:
    """Container for simulation data and analysis"""
    config: SimulationConfig
    time_data: List[float]
    input_data: List[float]          # Applied voltages
    output_data: List[float]         # Measured/simulated speeds
    current_data: List[float]        # Current measurements
    metadata: Dict[str, Any]
    analysis: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "config": self.config.to_dict(),
            "time_data": self.time_data,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "current_data": self.current_data,
            "metadata": self.metadata,
            "analysis": self.analysis
        }
    
    def save_to_file(self, filepath: str):
        """Save results to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"Simulation results saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

class SimulationEngine:
    """
    Main simulation engine coordinating models, hardware, and data collection
    """
    
    def __init__(self, motor_params: Optional[MotorParameters] = None):
        self.motor_model = DCMotorModel(motor_params) if motor_params else None
        self.arduino = None
        self.is_running = False
        self.current_results = None
        
        # Real-time simulation state
        self._sim_thread = None
        self._data_queue = Queue()
        self._stop_event = threading.Event()
        
        # Callbacks for real-time data streaming
        self.data_callbacks: List[Callable[[Dict[str, Any]], None]] = []
    
    def set_motor_parameters(self, params: MotorParameters):
        """Update motor parameters and reinitialize model"""
        self.motor_model = DCMotorModel(params)
        logger.info("Motor parameters updated")
    
    def connect_hardware(self, arduino_interface: ArduinoInterface) -> bool:
        """Connect to Arduino hardware"""
        try:
            self.arduino = arduino_interface
            logger.info("Hardware connected to simulation engine")
            return True
        except Exception as e:
            logger.error(f"Hardware connection failed: {e}")
            return False
    
    def add_data_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for real-time data streaming"""
        self.data_callbacks.append(callback)
    
    def remove_data_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove data callback"""
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
    
    def _notify_callbacks(self, data: Dict[str, Any]):
        """Notify all registered callbacks with new data"""
        for callback in self.data_callbacks:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    async def run_step_response(self, config: SimulationConfig, 
                               step_voltage: float = 12.0) -> SimulationResults:
        """
        Run step response test (offline simulation or hardware)
        """
        if config.mode == SimulationMode.OFFLINE:
            return await self._run_step_offline(config, step_voltage)
        elif config.mode == SimulationMode.HARDWARE:
            return await self._run_step_hardware(config, step_voltage)
        elif config.mode == SimulationMode.HYBRID:
            return await self._run_step_hybrid(config, step_voltage)
        else:
            raise ValueError(f"Unsupported simulation mode: {config.mode}")
    
    async def _run_step_offline(self, config: SimulationConfig, 
                               step_voltage: float) -> SimulationResults:
        """Pure simulation step response"""
        if not self.motor_model:
            raise ValueError("Motor model not configured")
        
        logger.info(f"Running offline step response: {step_voltage}V for {config.duration}s")
        
        # Generate time vector
        time_points = np.arange(0, config.duration, config.dt)
        
        # Simulate step response using transfer function
        time_out, response = self.motor_model.simulate_step_response(
            step_voltage, config.duration, config.dt
        )
        
        # Generate current data (simplified)
        # In real scenario, we'd integrate the full state-space model
        current_data = []
        self.motor_model.reset_state()
        
        for t in time_out:
            if t < config.dt:  # Initial transient
                state_data = self.motor_model.simulate_real_time(step_voltage, 0.0, config.dt)
                current_data.append(state_data["current"])
            else:
                current_data.append(current_data[-1] * 0.99)  # Simplified decay
        
        # Package results
        results = SimulationResults(
            config=config,
            time_data=time_out.tolist(),
            input_data=[step_voltage] * len(time_out),
            output_data=response.tolist(),
            current_data=current_data,
            metadata={
                "test_type": "step_response",
                "step_voltage": step_voltage,
                "motor_parameters": self.motor_model.params.to_dict(),
                "simulation_mode": "offline"
            }
        )
        
        # Add analysis
        results.analysis = self._analyze_step_response(results)
        
        self.current_results = results
        return results
    
    async def _run_step_hardware(self, config: SimulationConfig,
                                step_voltage: float) -> SimulationResults:
        """Hardware-only step response"""
        if not self.arduino:
            raise ValueError("Arduino not connected")
        
        logger.info(f"Running hardware step response: {step_voltage}V for {config.duration}s")
        
        # Initialize data collection
        time_data = []
        input_data = []
        output_data = []
        current_data = []
        
        start_time = time.time()
        sample_interval = 1.0 / config.sample_rate
        last_sample_time = start_time
        
        try:
            # Apply step input
            await self.arduino.send_command("MOTOR_VOLTAGE", {"voltage": step_voltage})
            
            # Collect data
            while (time.time() - start_time) < config.duration:
                current_time = time.time()
                
                if (current_time - last_sample_time) >= sample_interval:
                    # Read hardware data
                    try:
                        # Get motor data from Arduino
                        motor_data = await self.arduino.send_command("GET_MOTOR_DATA", {})
                        
                        if motor_data and "speed" in motor_data:
                            time_data.append(current_time - start_time)
                            input_data.append(step_voltage)
                            output_data.append(motor_data["speed"])
                            current_data.append(motor_data.get("current", 0.0))
                            
                            # Real-time callback
                            callback_data = {
                                "time": current_time - start_time,
                                "voltage": step_voltage,
                                "speed": motor_data["speed"],
                                "current": motor_data.get("current", 0.0),
                                "mode": "hardware"
                            }
                            self._notify_callbacks(callback_data)
                        
                        last_sample_time = current_time
                        
                    except Exception as e:
                        logger.warning(f"Data collection error: {e}")
                
                # Small delay to prevent overwhelming the system
                if config.real_time:
                    await asyncio.sleep(0.001)
            
            # Stop motor
            await self.arduino.send_command("MOTOR_VOLTAGE", {"voltage": 0.0})
            
        except Exception as e:
            logger.error(f"Hardware step response failed: {e}")
            # Ensure motor is stopped
            try:
                await self.arduino.send_command("MOTOR_VOLTAGE", {"voltage": 0.0})
            except:
                pass
            raise
        
        # Package results
        results = SimulationResults(
            config=config,
            time_data=time_data,
            input_data=input_data,
            output_data=output_data,
            current_data=current_data,
            metadata={
                "test_type": "step_response",
                "step_voltage": step_voltage,
                "simulation_mode": "hardware",
                "arduino_port": getattr(self.arduino, 'port', 'unknown')
            }
        )
        
        # Add analysis
        results.analysis = self._analyze_step_response(results)
        
        self.current_results = results
        return results
    
    async def _run_step_hybrid(self, config: SimulationConfig,
                              step_voltage: float) -> SimulationResults:
        """
        Hardware-in-the-loop simulation
        Uses real hardware for some measurements, simulation for others
        """
        if not self.motor_model or not self.arduino:
            raise ValueError("Both motor model and Arduino required for hybrid mode")
        
        logger.info(f"Running hybrid step response: {step_voltage}V for {config.duration}s")
        
        # This would implement a more sophisticated HIL approach
        # For now, we'll run both and compare
        hardware_results = await self._run_step_hardware(config, step_voltage)
        simulation_results = await self._run_step_offline(config, step_voltage)
        
        # Combine results with comparison
        results = SimulationResults(
            config=config,
            time_data=hardware_results.time_data,
            input_data=hardware_results.input_data,
            output_data=hardware_results.output_data,
            current_data=hardware_results.current_data,
            metadata={
                "test_type": "step_response",
                "step_voltage": step_voltage,
                "simulation_mode": "hybrid",
                "hardware_results": hardware_results.to_dict(),
                "simulation_results": simulation_results.to_dict()
            }
        )
        
        # Add hybrid analysis
        results.analysis = self._analyze_hybrid_results(hardware_results, simulation_results)
        
        self.current_results = results
        return results
    
    def _analyze_step_response(self, results: SimulationResults) -> Dict[str, Any]:
        """Analyze step response characteristics"""
        try:
            time_data = np.array(results.time_data)
            output_data = np.array(results.output_data)
            
            if len(output_data) < 10:
                return {"error": "Insufficient data for analysis"}
            
            # Find steady-state value (average of last 10% of data)
            steady_state_start = int(0.9 * len(output_data))
            steady_state_value = np.mean(output_data[steady_state_start:])
            
            # Rise time (10% to 90% of steady-state)
            target_10 = 0.1 * steady_state_value
            target_90 = 0.9 * steady_state_value
            
            idx_10 = np.where(output_data >= target_10)[0]
            idx_90 = np.where(output_data >= target_90)[0]
            
            rise_time = None
            if len(idx_10) > 0 and len(idx_90) > 0:
                t_10 = time_data[idx_10[0]]
                t_90 = time_data[idx_90[0]]
                rise_time = t_90 - t_10
            
            # Settling time (within 2% of steady-state)
            settling_tolerance = 0.02 * steady_state_value
            settling_mask = np.abs(output_data - steady_state_value) <= settling_tolerance
            
            settling_time = None
            if np.any(settling_mask):
                # Find the last time it was outside the tolerance
                outside_tolerance = np.where(~settling_mask)[0]
                if len(outside_tolerance) > 0:
                    settling_time = time_data[outside_tolerance[-1]]
            
            # Overshoot
            max_value = np.max(output_data)
            overshoot_percent = ((max_value - steady_state_value) / steady_state_value * 100) if steady_state_value > 0 else 0
            
            # Peak time
            peak_time = time_data[np.argmax(output_data)]
            
            analysis = {
                "steady_state_value": float(steady_state_value),
                "rise_time": float(rise_time) if rise_time is not None else None,
                "settling_time": float(settling_time) if settling_time is not None else None,
                "overshoot_percent": float(overshoot_percent),
                "peak_time": float(peak_time),
                "peak_value": float(max_value),
                "final_value": float(output_data[-1])
            }
            
            logger.info(f"Step response analysis: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_hybrid_results(self, hardware_results: SimulationResults,
                               simulation_results: SimulationResults) -> Dict[str, Any]:
        """Compare hardware and simulation results"""
        try:
            hw_analysis = hardware_results.analysis or {}
            sim_analysis = simulation_results.analysis or {}
            
            # Calculate differences
            differences = {}
            for key in ["steady_state_value", "rise_time", "settling_time", "overshoot_percent"]:
                hw_val = hw_analysis.get(key)
                sim_val = sim_analysis.get(key)
                
                if hw_val is not None and sim_val is not None:
                    abs_diff = abs(hw_val - sim_val)
                    rel_diff = (abs_diff / hw_val * 100) if hw_val != 0 else 0
                    differences[f"{key}_difference"] = {
                        "absolute": float(abs_diff),
                        "relative_percent": float(rel_diff),
                        "hardware": float(hw_val),
                        "simulation": float(sim_val)
                    }
            
            # Overall model accuracy
            hw_output = np.array(hardware_results.output_data)
            sim_output = np.array(simulation_results.output_data)
            
            # Interpolate simulation to match hardware time points if needed
            if len(hw_output) != len(sim_output):
                hw_time = np.array(hardware_results.time_data)
                sim_time = np.array(simulation_results.time_data)
                sim_output_interp = np.interp(hw_time, sim_time, sim_output)
            else:
                sim_output_interp = sim_output
            
            # Calculate correlation and RMS error
            correlation = np.corrcoef(hw_output, sim_output_interp[:len(hw_output)])[0, 1]
            rms_error = np.sqrt(np.mean((hw_output - sim_output_interp[:len(hw_output)])**2))
            
            return {
                "hardware_analysis": hw_analysis,
                "simulation_analysis": sim_analysis,
                "differences": differences,
                "correlation": float(correlation) if not np.isnan(correlation) else None,
                "rms_error": float(rms_error),
                "model_accuracy_percent": float((1 - rms_error / np.mean(hw_output)) * 100) if np.mean(hw_output) > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Hybrid analysis failed: {e}")
            return {"error": str(e)}
    
    async def run_parameter_identification(self, config: SimulationConfig) -> Dict[str, Any]:
        """
        Run parameter identification tests
        """
        if config.mode == SimulationMode.OFFLINE:
            if not self.motor_model:
                raise ValueError("Motor model required for offline parameter identification")
            
            # Simulate coast-down test
            coast_results = self.motor_model.coast_down_analysis(initial_speed=100.0)
            
            # Simulate step response for different voltages
            step_voltages = [6.0, 9.0, 12.0]
            step_results = []
            
            for voltage in step_voltages:
                step_config = SimulationConfig(
                    mode=SimulationMode.OFFLINE,
                    duration=3.0,
                    dt=0.01
                )
                step_result = await self._run_step_offline(step_config, voltage)
                step_results.append(step_result.to_dict())
            
            return {
                "coast_down": coast_results,
                "step_responses": step_results,
                "identified_parameters": self.motor_model.params.to_dict(),
                "system_characteristics": self.motor_model.calculate_system_characteristics()
            }
        
        elif config.mode == SimulationMode.HARDWARE:
            # Hardware parameter identification would require specific test sequences
            raise NotImplementedError("Hardware parameter identification not yet implemented")
        
        else:
            raise ValueError(f"Parameter identification not supported for mode: {config.mode}")
    
    def start_real_time_simulation(self, config: SimulationConfig, 
                                  input_function: Callable[[float], float]):
        """
        Start real-time simulation with custom input function
        """
        if self.is_running:
            raise RuntimeError("Simulation already running")
        
        self.is_running = True
        self._stop_event.clear()
        
        def simulation_worker():
            """Worker thread for real-time simulation"""
            try:
                start_time = time.time()
                last_time = start_time
                
                while not self._stop_event.is_set():
                    current_time = time.time()
                    elapsed = current_time - start_time
                    dt = current_time - last_time
                    
                    if elapsed >= config.duration:
                        break
                    
                    # Get input from function
                    input_voltage = input_function(elapsed)
                    
                    if config.mode == SimulationMode.OFFLINE and self.motor_model:
                        # Pure simulation
                        result = self.motor_model.simulate_real_time(input_voltage, 0.0, dt)
                        result["mode"] = "simulation"
                        result["input_voltage"] = input_voltage
                        
                    elif config.mode == SimulationMode.HARDWARE and self.arduino:
                        # Real hardware (simplified)
                        # In practice, this would be more complex
                        result = {
                            "time": elapsed,
                            "input_voltage": input_voltage,
                            "mode": "hardware"
                        }
                    
                    # Queue data for main thread
                    self._data_queue.put(result)
                    
                    # Notify callbacks
                    self._notify_callbacks(result)
                    
                    last_time = current_time
                    
                    # Real-time timing
                    if config.real_time:
                        time.sleep(max(0, config.dt - dt))
                        
            except Exception as e:
                logger.error(f"Real-time simulation error: {e}")
            finally:
                self.is_running = False
        
        self._sim_thread = threading.Thread(target=simulation_worker, daemon=True)
        self._sim_thread.start()
        
        logger.info("Real-time simulation started")
    
    def stop_real_time_simulation(self):
        """Stop real-time simulation"""
        if self.is_running:
            self._stop_event.set()
            if self._sim_thread:
                self._sim_thread.join(timeout=2.0)
            self.is_running = False
            logger.info("Real-time simulation stopped")
    
    def get_real_time_data(self) -> Optional[Dict[str, Any]]:
        """Get latest real-time data (non-blocking)"""
        try:
            return self._data_queue.get_nowait()
        except Empty:
            return None
    
    def export_results_csv(self, results: SimulationResults, filepath: str):
        """Export results to CSV format"""
        try:
            import csv
            
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow(['Time', 'Input_Voltage', 'Output_Speed', 'Current'])
                
                # Data
                for i in range(len(results.time_data)):
                    writer.writerow([
                        results.time_data[i],
                        results.input_data[i],
                        results.output_data[i],
                        results.current_data[i] if i < len(results.current_data) else 0
                    ])
            
            logger.info(f"Results exported to CSV: {filepath}")
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_real_time_simulation()
        if self.arduino:
            # Arduino cleanup handled by ArduinoInterface
            pass