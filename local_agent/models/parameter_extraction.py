"""
DC Motor Parameter Extraction Module
Educational tools for measuring and identifying motor parameters through experiments
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.optimize import curve_fit
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import time
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ExperimentConfig:
    """Configuration for parameter extraction experiments"""
    duration: float = 10.0
    sample_rate: float = 100.0
    voltage_levels: Optional[List[float]] = None
    settling_time: float = 2.0
    
    def __post_init__(self):
        if self.voltage_levels is None:
            self.voltage_levels = [3.0, 6.0, 9.0, 12.0]

@dataclass
class MeasurementData:
    """Container for experimental measurement data"""
    time: np.ndarray
    voltage: np.ndarray
    current: np.ndarray
    speed: np.ndarray
    position: np.ndarray
    temperature: Optional[np.ndarray] = None

class DCMotorParameterExtractor:
    """
    Educational DC Motor Parameter Extraction
    
    This class provides systematic methods to extract motor parameters
    through carefully designed experiments, following best practices
    in system identification.
    """
    
    def __init__(self, arduino_interface=None):
        self.arduino = arduino_interface
        self.extracted_params = {}
        self.experiment_history = []
        
    async def extract_resistance(self, voltage_range: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Extract motor resistance using locked-rotor test
        
        Educational Objective:
        - Understand Ohm's law application in motors
        - Learn about locked-rotor conditions
        - Practice steady-state analysis
        
        Method:
        1. Apply low DC voltage to prevent overheating
        2. Measure steady-state current
        3. Calculate R = V/I
        4. Repeat for multiple voltages to verify linearity
        """
        if voltage_range is None:
            voltage_range = [1.0, 2.0, 3.0]  # Low voltages for locked rotor
            
        logger.info("Starting resistance measurement (locked-rotor test)")
        
        measurements = {
            'voltages': [],
            'currents': [],
            'temperatures': []
        }
        
        if self.arduino:
            # Hardware-based measurement
            for voltage in voltage_range:
                logger.info(f"Applying {voltage}V for resistance measurement")
                
                # Apply voltage with rotor locked
                await self.arduino.send_command("MOTOR_VOLTAGE", voltage)
                await self.arduino.send_command("LOCK_ROTOR", True)
                
                # Wait for steady state
                await asyncio.sleep(2.0)
                
                # Measure steady-state current
                data = await self.arduino.send_command("GET_MOTOR_DATA")
                current = data.get('current', 0)
                temp = data.get('temperature', 25)
                
                measurements['voltages'].append(voltage)
                measurements['currents'].append(current)
                measurements['temperatures'].append(temp)
                
                # Safety: Turn off between measurements
                await self.arduino.send_command("MOTOR_VOLTAGE", 0)
                await asyncio.sleep(1.0)
            
            # Unlock rotor
            await self.arduino.send_command("LOCK_ROTOR", False)
        else:
            # Simulation for educational purposes
            for voltage in voltage_range:
                # Simulate realistic resistance with some noise
                R_true = 2.5  # Typical small motor resistance
                current = voltage / R_true + np.random.normal(0, 0.01)
                
                measurements['voltages'].append(voltage)
                measurements['currents'].append(current)
                measurements['temperatures'].append(25.0)
        
        # Analysis
        voltages = np.array(measurements['voltages'])
        currents = np.array(measurements['currents'])
        
        # Linear regression: V = R*I
        resistance, _ = np.polyfit(currents, voltages, 1)
        
        # Calculate R-squared for fit quality
        v_predicted = resistance * currents
        r_squared = 1 - np.sum((voltages - v_predicted)**2) / np.sum((voltages - np.mean(voltages))**2)
        
        # Temperature correction (copper has ~0.4%/°C coefficient)
        temp_avg = np.mean(measurements['temperatures'])
        resistance_20C = resistance / (1 + 0.004 * (temp_avg - 20))
        
        result = {
            'resistance_measured': float(resistance),
            'resistance_20C': float(resistance_20C),
            'r_squared': float(r_squared),
            'measurement_data': measurements,
            'method': 'locked_rotor_test',
            'temperature_avg': float(temp_avg),
            'educational_notes': {
                'principle': 'Ohms law: V = I*R under locked rotor conditions',
                'why_locked': 'Eliminates back-EMF, measures pure resistance',
                'temperature_effect': 'Resistance increases ~0.4% per °C for copper',
                'safety': 'Use low voltages to prevent overheating'
            }
        }
        
        self.extracted_params['resistance'] = result
        logger.info(f"Resistance extracted: {resistance:.3f} Ω (R² = {r_squared:.3f})")
        
        return result
    
    async def extract_back_emf_constant(self, speed_range: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Extract back-EMF constant using free-running test
        
        Educational Objective:
        - Understand electromagnetic induction in motors
        - Learn Faraday's law application
        - Practice dynamic measurement techniques
        
        Method:
        1. Spin motor to various speeds (external drive or initial voltage)
        2. Disconnect voltage and measure generated EMF
        3. Calculate Ke = EMF / ω
        4. Verify linearity across speed range
        """
        if speed_range is None:
            speed_range = [50, 100, 150, 200]  # RPM
            
        logger.info("Starting back-EMF constant measurement")
        
        measurements = {
            'speeds_rpm': [],
            'speeds_rad_s': [],
            'back_emf_voltages': [],
            'decay_time_constants': []
        }
        
        if self.arduino:
            # Hardware-based measurement
            for target_speed in speed_range:
                logger.info(f"Measuring back-EMF at {target_speed} RPM")
                
                # Accelerate to target speed
                await self._accelerate_to_speed(target_speed)
                
                # Wait for steady state
                await asyncio.sleep(2.0)
                
                # Measure actual speed
                data = await self.arduino.send_command("GET_MOTOR_DATA")
                actual_speed = data.get('speed', 0)  # RPM
                
                # Disconnect motor (set voltage to 0)
                await self.arduino.send_command("MOTOR_VOLTAGE", 0)
                
                # Measure back-EMF during coast-down
                back_emf_data = await self._measure_coast_down_emf(duration=3.0)
                
                # Calculate average back-EMF at measured speed
                initial_back_emf = back_emf_data['initial_voltage']
                
                measurements['speeds_rpm'].append(actual_speed)
                measurements['speeds_rad_s'].append(actual_speed * 2 * np.pi / 60)
                measurements['back_emf_voltages'].append(initial_back_emf)
                measurements['decay_time_constants'].append(back_emf_data['time_constant'])
                
                # Cool down between measurements
                await asyncio.sleep(3.0)
        else:
            # Simulation for educational purposes
            Ke_true = 0.05  # V·s/rad
            for speed_rpm in speed_range:
                speed_rad_s = speed_rpm * 2 * np.pi / 60
                back_emf = Ke_true * speed_rad_s + np.random.normal(0, 0.1)
                
                measurements['speeds_rpm'].append(speed_rpm)
                measurements['speeds_rad_s'].append(speed_rad_s)
                measurements['back_emf_voltages'].append(back_emf)
                measurements['decay_time_constants'].append(0.5)
        
        # Analysis
        speeds_rad_s = np.array(measurements['speeds_rad_s'])
        back_emf_voltages = np.array(measurements['back_emf_voltages'])
        
        # Linear regression: EMF = Ke * ω
        ke_constant, intercept = np.polyfit(speeds_rad_s, back_emf_voltages, 1)
        
        # Calculate fit quality
        emf_predicted = ke_constant * speeds_rad_s + intercept
        r_squared = 1 - np.sum((back_emf_voltages - emf_predicted)**2) / np.sum((back_emf_voltages - np.mean(back_emf_voltages))**2)
        
        result = {
            'ke_constant': float(ke_constant),
            'intercept': float(intercept),
            'r_squared': float(r_squared),
            'measurement_data': measurements,
            'method': 'free_running_back_emf',
            'educational_notes': {
                'principle': 'Faradays law: EMF = Ke * ω (angular velocity)',
                'units': 'Ke in V·s/rad or V·min/rev',
                'linearity': 'Back-EMF should be linear with speed',
                'motor_generator': 'Same constant for motor and generator operation'
            }
        }
        
        self.extracted_params['ke_constant'] = result
        logger.info(f"Back-EMF constant extracted: {ke_constant:.4f} V·s/rad (R² = {r_squared:.3f})")
        
        return result
    
    async def extract_torque_constant(self, current_range: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Extract torque constant using stall torque test
        
        Educational Objective:
        - Understand force generation in motors
        - Learn relationship between current and torque
        - Practice static torque measurement
        
        Method:
        1. Apply known currents while preventing rotation
        2. Measure resulting stall torque
        3. Calculate Kt = τ / I
        4. Verify linearity and compare with Ke
        """
        if current_range is None:
            current_range = [0.5, 1.0, 1.5, 2.0]  # Amperes
            
        logger.info("Starting torque constant measurement (stall torque test)")
        
        measurements = {
            'currents': [],
            'stall_torques': [],
            'voltages_applied': []
        }
        
        if self.arduino:
            # Hardware-based measurement (requires torque sensor)
            for target_current in current_range:
                logger.info(f"Measuring stall torque at {target_current}A")
                
                # Apply voltage to achieve target current with rotor locked
                await self.arduino.send_command("LOCK_ROTOR", True)
                voltage = await self._achieve_target_current(target_current)
                
                # Wait for steady state
                await asyncio.sleep(1.0)
                
                # Measure actual current and torque
                data = await self.arduino.send_command("GET_MOTOR_DATA")
                actual_current = data.get('current', 0)
                stall_torque = data.get('torque', 0)  # From torque sensor
                
                measurements['currents'].append(actual_current)
                measurements['stall_torques'].append(stall_torque)
                measurements['voltages_applied'].append(voltage)
                
                # Safety: Turn off between measurements
                await self.arduino.send_command("MOTOR_VOLTAGE", 0)
                await asyncio.sleep(1.0)
            
            # Unlock rotor
            await self.arduino.send_command("LOCK_ROTOR", False)
        else:
            # Simulation for educational purposes
            Kt_true = 0.05  # N·m/A (should equal Ke in SI units)
            for current in current_range:
                torque = Kt_true * current + np.random.normal(0, 0.002)
                voltage = current * 2.5  # Assuming 2.5Ω resistance
                
                measurements['currents'].append(current)
                measurements['stall_torques'].append(torque)
                measurements['voltages_applied'].append(voltage)
        
        # Analysis
        currents = np.array(measurements['currents'])
        torques = np.array(measurements['stall_torques'])
        
        # Linear regression: τ = Kt * I
        kt_constant, intercept = np.polyfit(currents, torques, 1)
        
        # Calculate fit quality
        torque_predicted = kt_constant * currents + intercept
        r_squared = 1 - np.sum((torques - torque_predicted)**2) / np.sum((torques - np.mean(torques))**2)
        
        # Compare with Ke (should be equal in SI units)
        ke_result = self.extracted_params.get('ke_constant', {})
        ke_value = ke_result.get('ke_constant', None)
        kt_ke_ratio = kt_constant / ke_value if ke_value else None
        
        result = {
            'kt_constant': float(kt_constant),
            'intercept': float(intercept),
            'r_squared': float(r_squared),
            'kt_ke_ratio': float(kt_ke_ratio) if kt_ke_ratio else None,
            'measurement_data': measurements,
            'method': 'stall_torque_test',
            'educational_notes': {
                'principle': 'Motor force law: τ = Kt * I (current)',
                'units': 'Kt in N·m/A',
                'kt_ke_equality': 'In SI units, Kt = Ke (fundamental motor relationship)',
                'measurement_challenge': 'Requires torque sensor or load cell'
            }
        }
        
        self.extracted_params['kt_constant'] = result
        logger.info(f"Torque constant extracted: {kt_constant:.4f} N·m/A (R² = {r_squared:.3f})")
        
        if kt_ke_ratio:
            logger.info(f"Kt/Ke ratio: {kt_ke_ratio:.3f} (should be ~1.0 in SI units)")
        
        return result
    
    async def extract_inertia_and_friction(self, initial_speeds: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Extract moment of inertia and friction using coast-down test
        
        Educational Objective:
        - Understand rotational dynamics
        - Learn exponential decay analysis
        - Practice parameter fitting techniques
        
        Method:
        1. Accelerate motor to known speed
        2. Disconnect power and record speed decay
        3. Fit exponential decay: ω(t) = ω₀ * exp(-t/τ)
        4. Extract J and b from time constant τ = J/b
        """
        if initial_speeds is None:
            initial_speeds = [100, 150, 200]  # RPM
            
        logger.info("Starting inertia and friction extraction (coast-down test)")
        
        coast_down_data = []
        
        for initial_speed in initial_speeds:
            logger.info(f"Coast-down test from {initial_speed} RPM")
            
            if self.arduino:
                # Hardware-based measurement
                # Accelerate to target speed
                await self._accelerate_to_speed(initial_speed)
                await asyncio.sleep(2.0)
                
                # Record actual initial speed
                data = await self.arduino.send_command("GET_MOTOR_DATA")
                actual_initial_speed = data.get('speed', 0)
                
                # Disconnect and record coast-down
                await self.arduino.send_command("MOTOR_VOLTAGE", 0)
                coast_data = await self._record_coast_down(duration=10.0)
                
            else:
                # Simulation for educational purposes
                J_true = 0.0001  # kg·m²
                b_true = 0.00005  # N·m·s/rad
                tau = J_true / b_true  # Time constant
                
                coast_data = self._simulate_coast_down(initial_speed, tau, duration=10.0)
                actual_initial_speed = initial_speed
            
            # Analyze coast-down data
            analysis = self._analyze_coast_down(coast_data)
            analysis['initial_speed_rpm'] = actual_initial_speed
            
            coast_down_data.append(analysis)
            
            # Wait between tests
            await asyncio.sleep(3.0)
        
        # Extract parameters from multiple coast-down tests
        time_constants = [data['time_constant'] for data in coast_down_data]
        avg_time_constant = np.mean(time_constants)
        std_time_constant = np.std(time_constants)
        
        # Use resistance and torque constant to calculate inertia and friction
        R = self.extracted_params.get('resistance', {}).get('resistance_measured', 2.5)
        Kt = self.extracted_params.get('kt_constant', {}).get('kt_constant', 0.05)
        Ke = self.extracted_params.get('ke_constant', {}).get('ke_constant', 0.05)
        
        # From motor equations, mechanical time constant τ_mech = J/b
        # Electrical time constant τ_elec = L/R (much faster)
        # For coast-down with no voltage: τ ≈ J/b
        
        # Estimate friction assuming reasonable inertia
        # Typical small motor: J ≈ 0.0001 kg·m²
        J_estimated = 0.0001  # This could be calculated from motor geometry
        b_from_coast_down = J_estimated / avg_time_constant
        
        # Alternative: use known motor parameters if available
        # b = Kt*Ke/(R*τ) + other losses
        
        result = {
            'inertia_estimated': float(J_estimated),
            'friction_coefficient': float(b_from_coast_down),
            'time_constant_avg': float(avg_time_constant),
            'time_constant_std': float(std_time_constant),
            'coast_down_tests': coast_down_data,
            'method': 'coast_down_analysis',
            'educational_notes': {
                'principle': 'Rotational dynamics: J*dω/dt = -b*ω (no applied torque)',
                'exponential_decay': 'ω(t) = ω₀ * exp(-t/τ) where τ = J/b',
                'parameter_coupling': 'Coast-down gives τ = J/b, need independent measurement for J or b',
                'measurement_accuracy': 'Longer coast-down gives better parameter estimation'
            }
        }
        
        self.extracted_params['inertia_friction'] = result
        logger.info(f"Time constant: {avg_time_constant:.3f} ± {std_time_constant:.3f} s")
        logger.info(f"Estimated friction: {b_from_coast_down:.6f} N·m·s/rad")
        
        return result
    
    async def extract_inductance(self, frequency_range: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Extract motor inductance using AC impedance test
        
        Educational Objective:
        - Understand AC impedance in motors
        - Learn frequency domain analysis
        - Practice complex impedance calculations
        
        Method:
        1. Apply AC voltage at various frequencies
        2. Measure voltage and current amplitude and phase
        3. Calculate impedance Z = |V|/|I| ∠(φ_v - φ_i)
        4. Fit to model: Z = R + jωL
        """
        if frequency_range is None:
            frequency_range = [10, 50, 100, 200, 500]  # Hz
            
        logger.info("Starting inductance measurement (AC impedance test)")
        
        measurements = {
            'frequencies': [],
            'impedance_magnitudes': [],
            'phase_angles': [],
            'voltage_amplitudes': [],
            'current_amplitudes': []
        }
        
        test_voltage = 2.0  # Low voltage for safety
        
        if self.arduino:
            # Hardware-based measurement (requires AC capability)
            for frequency in frequency_range:
                logger.info(f"AC impedance test at {frequency} Hz")
                
                # Apply AC voltage at frequency
                await self.arduino.send_command("AC_VOLTAGE", {
                    'amplitude': test_voltage,
                    'frequency': frequency
                })
                
                # Wait for steady state
                await asyncio.sleep(max(5.0/frequency, 0.5))
                
                # Measure AC response
                ac_data = await self.arduino.send_command("GET_AC_DATA")
                
                v_amplitude = ac_data.get('voltage_amplitude', 0)
                i_amplitude = ac_data.get('current_amplitude', 0)
                phase_diff = ac_data.get('phase_difference', 0)
                
                if i_amplitude > 0:
                    impedance_mag = v_amplitude / i_amplitude
                    measurements['frequencies'].append(frequency)
                    measurements['impedance_magnitudes'].append(impedance_mag)
                    measurements['phase_angles'].append(phase_diff)
                    measurements['voltage_amplitudes'].append(v_amplitude)
                    measurements['current_amplitudes'].append(i_amplitude)
                
                # Turn off AC
                await self.arduino.send_command("AC_VOLTAGE", {
                    'amplitude': 0,
                    'frequency': 0
                })
                await asyncio.sleep(0.5)
        else:
            # Simulation for educational purposes
            R_true = 2.5  # Ω
            L_true = 0.001  # H
            
            for frequency in frequency_range:
                omega = 2 * np.pi * frequency
                impedance_mag = np.sqrt(R_true**2 + (omega * L_true)**2)
                phase_angle = np.arctan2(omega * L_true, R_true) * 180 / np.pi
                
                # Add some noise
                impedance_mag += np.random.normal(0, 0.05)
                phase_angle += np.random.normal(0, 1.0)
                
                measurements['frequencies'].append(frequency)
                measurements['impedance_magnitudes'].append(impedance_mag)
                measurements['phase_angles'].append(phase_angle)
                measurements['voltage_amplitudes'].append(test_voltage)
                measurements['current_amplitudes'].append(test_voltage / impedance_mag)
        
        # Analysis
        frequencies = np.array(measurements['frequencies'])
        impedances = np.array(measurements['impedance_magnitudes'])
        
        # Fit to impedance model: |Z| = sqrt(R² + (ωL)²)
        def impedance_model(omega, R, L):
            return np.sqrt(R**2 + (omega * L)**2)
        
        omega_values = 2 * np.pi * frequencies
        
        try:
            # Initial guess
            R_initial = impedances[0] if len(impedances) > 0 else 2.5
            L_initial = 0.001
            
            popt, pcov = curve_fit(impedance_model, omega_values, impedances, 
                                 p0=[R_initial, L_initial])
            
            R_fitted, L_fitted = popt
            param_errors = np.sqrt(np.diag(pcov))
            
            # Calculate R-squared
            impedance_predicted = impedance_model(omega_values, R_fitted, L_fitted)
            r_squared = 1 - np.sum((impedances - impedance_predicted)**2) / np.sum((impedances - np.mean(impedances))**2)
            
        except Exception as e:
            logger.error(f"Curve fitting failed: {e}")
            R_fitted = measurements['impedance_magnitudes'][0] if measurements['impedance_magnitudes'] else 2.5
            L_fitted = 0.001
            param_errors = [0, 0]
            r_squared = 0
        
        result = {
            'inductance': float(L_fitted),
            'resistance_from_ac': float(R_fitted),
            'inductance_error': float(param_errors[1]) if len(param_errors) > 1 else 0,
            'resistance_error': float(param_errors[0]) if len(param_errors) > 0 else 0,
            'r_squared': float(r_squared),
            'measurement_data': measurements,
            'method': 'ac_impedance_test',
            'educational_notes': {
                'principle': 'AC impedance: Z = R + jωL',
                'frequency_dependence': '|Z| increases with frequency due to inductance',
                'phase_shift': 'Current lags voltage by φ = arctan(ωL/R)',
                'comparison': 'Compare AC resistance with DC resistance measurement'
            }
        }
        
        self.extracted_params['inductance'] = result
        logger.info(f"Inductance extracted: {L_fitted:.6f} H (R² = {r_squared:.3f})")
        
        return result
    
    def generate_parameter_summary(self) -> Dict[str, Any]:
        """
        Generate comprehensive summary of all extracted parameters
        """
        summary = {
            'extraction_timestamp': time.time(),
            'parameters': {},
            'validation': {},
            'educational_summary': {}
        }
        
        # Compile all extracted parameters
        for param_name, param_data in self.extracted_params.items():
            if param_name == 'resistance':
                summary['parameters']['R'] = param_data.get('resistance_20C', 0)
                summary['parameters']['R_units'] = 'Ω'
            elif param_name == 'inductance':
                summary['parameters']['L'] = param_data.get('inductance', 0)
                summary['parameters']['L_units'] = 'H'
            elif param_name == 'ke_constant':
                summary['parameters']['Ke'] = param_data.get('ke_constant', 0)
                summary['parameters']['Ke_units'] = 'V·s/rad'
            elif param_name == 'kt_constant':
                summary['parameters']['Kt'] = param_data.get('kt_constant', 0)
                summary['parameters']['Kt_units'] = 'N·m/A'
            elif param_name == 'inertia_friction':
                summary['parameters']['J'] = param_data.get('inertia_estimated', 0)
                summary['parameters']['J_units'] = 'kg·m²'
                summary['parameters']['b'] = param_data.get('friction_coefficient', 0)
                summary['parameters']['b_units'] = 'N·m·s/rad'
        
        # Validation checks
        R = summary['parameters'].get('R', 0)
        L = summary['parameters'].get('L', 0)
        Ke = summary['parameters'].get('Ke', 0)
        Kt = summary['parameters'].get('Kt', 0)
        J = summary['parameters'].get('J', 0)
        b = summary['parameters'].get('b', 0)
        
        # Physical validation
        validation = {}
        
        if Kt > 0 and Ke > 0:
            kt_ke_ratio = Kt / Ke
            validation['kt_ke_consistency'] = {
                'ratio': kt_ke_ratio,
                'expected': 1.0,
                'valid': 0.8 < kt_ke_ratio < 1.2,
                'note': 'Kt should equal Ke in SI units'
            }
        
        if R > 0 and L > 0:
            electrical_time_constant = L / R
            validation['electrical_time_constant'] = {
                'value': electrical_time_constant,
                'typical_range': [0.0001, 0.01],
                'valid': 0.0001 < electrical_time_constant < 0.01,
                'note': 'L/R should be much smaller than mechanical time constant'
            }
        
        if J > 0 and b > 0:
            mechanical_time_constant = J / b
            validation['mechanical_time_constant'] = {
                'value': mechanical_time_constant,
                'typical_range': [0.1, 10.0],
                'valid': 0.1 < mechanical_time_constant < 10.0,
                'note': 'J/b determines speed response time'
            }
        
        summary['validation'] = validation
        
        # Educational summary
        summary['educational_summary'] = {
            'parameter_extraction_methods': {
                'resistance': 'Locked-rotor test using Ohms law',
                'inductance': 'AC impedance test with frequency sweep',
                'back_emf_constant': 'Free-running test measuring generated voltage',
                'torque_constant': 'Stall torque test with current measurement',
                'inertia_friction': 'Coast-down test with exponential decay analysis'
            },
            'physical_insights': {
                'electromagnetic': 'Kt = Ke shows motor-generator duality',
                'electrical': 'R and L determine current response speed',
                'mechanical': 'J and b determine velocity response speed',
                'coupling': 'All parameters interact in motor dynamics'
            },
            'next_steps': [
                'Use parameters in transfer function derivation',
                'Validate with step response experiments',
                'Design controllers based on identified parameters',
                'Compare theoretical vs experimental responses'
            ]
        }
        
        return summary
    
    # Helper methods for hardware interaction
    async def _accelerate_to_speed(self, target_speed_rpm: float):
        """Helper to accelerate motor to target speed"""
        if not self.arduino:
            return
            
        # Simple open-loop acceleration
        voltage = min(12.0, target_speed_rpm / 20.0)  # Rough approximation
        await self.arduino.send_command("MOTOR_VOLTAGE", voltage)
        
        # Wait and adjust
        for _ in range(20):
            await asyncio.sleep(0.1)
            data = await self.arduino.send_command("GET_MOTOR_DATA")
            current_speed = data.get('speed', 0)
            
            if abs(current_speed - target_speed_rpm) < 5:
                break
                
            # Adjust voltage
            if current_speed < target_speed_rpm:
                voltage = min(voltage + 0.5, 12.0)
            else:
                voltage = max(voltage - 0.5, 0)
            
            await self.arduino.send_command("MOTOR_VOLTAGE", voltage)
    
    async def _achieve_target_current(self, target_current: float) -> float:
        """Helper to achieve target current with voltage adjustment"""
        if not self.arduino:
            return target_current * 2.5  # Assume 2.5Ω resistance
            
        voltage = target_current * 2.5  # Initial guess
        
        for _ in range(10):
            await self.arduino.send_command("MOTOR_VOLTAGE", voltage)
            await asyncio.sleep(0.2)
            
            data = await self.arduino.send_command("GET_MOTOR_DATA")
            current = data.get('current', 0)
            
            if abs(current - target_current) < 0.05:
                break
                
            # Adjust voltage
            error = target_current - current
            voltage += error * 2.5 * 0.5  # Proportional adjustment
            voltage = np.clip(voltage, 0, 12.0)
        
        return voltage
    
    async def _measure_coast_down_emf(self, duration: float = 3.0) -> Dict[str, float]:
        """Measure back-EMF during coast-down"""
        if not self.arduino:
            # Simulate exponential decay
            return {'initial_voltage': 5.0, 'time_constant': 0.5}
            
        # Record voltage during coast-down
        emf_data = []
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            data = await self.arduino.send_command("GET_MOTOR_DATA")
            voltage = data.get('back_emf', 0)
            current_time = time.time() - start_time
            
            emf_data.append((current_time, voltage))
            await asyncio.sleep(0.01)
        
        # Analyze decay
        if len(emf_data) < 10:
            return {'initial_voltage': 0, 'time_constant': 1.0}
            
        times, voltages = zip(*emf_data)
        times = np.array(times)
        voltages = np.array(voltages)
        
        # Fit exponential decay
        try:
            def exp_decay(t, V0, tau):
                return V0 * np.exp(-t / tau)
                
            popt, _ = curve_fit(exp_decay, times, voltages, p0=[voltages[0], 0.5])
            initial_voltage, time_constant = popt
        except:
            initial_voltage = voltages[0] if len(voltages) > 0 else 0
            time_constant = 0.5
        
        return {
            'initial_voltage': float(initial_voltage),
            'time_constant': float(time_constant)
        }
    
    async def _record_coast_down(self, duration: float = 10.0) -> Dict[str, np.ndarray]:
        """Record speed during coast-down"""
        if not self.arduino:
            return self._simulate_coast_down(100, 2.0, duration)
            
        speed_data = []
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            data = await self.arduino.send_command("GET_MOTOR_DATA")
            speed = data.get('speed', 0)  # RPM
            current_time = time.time() - start_time
            
            speed_data.append((current_time, speed))
            await asyncio.sleep(0.01)
        
        times, speeds = zip(*speed_data)
        return {
            'time': np.array(times),
            'speed_rpm': np.array(speeds),
            'speed_rad_s': np.array(speeds) * 2 * np.pi / 60
        }
    
    def _simulate_coast_down(self, initial_speed_rpm: float, time_constant: float, 
                           duration: float = 10.0) -> Dict[str, np.ndarray]:
        """Simulate coast-down for educational purposes"""
        times = np.linspace(0, duration, int(duration * 100))
        initial_speed_rad_s = initial_speed_rpm * 2 * np.pi / 60
        
        # Exponential decay with noise
        speeds_rad_s = initial_speed_rad_s * np.exp(-times / time_constant)
        speeds_rad_s += np.random.normal(0, 0.1, len(speeds_rad_s))
        speeds_rad_s = np.maximum(speeds_rad_s, 0)  # No negative speeds
        
        speeds_rpm = speeds_rad_s * 60 / (2 * np.pi)
        
        return {
            'time': times,
            'speed_rpm': speeds_rpm,
            'speed_rad_s': speeds_rad_s
        }
    
    def _analyze_coast_down(self, coast_data: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Analyze coast-down data to extract time constant"""
        times = coast_data['time']
        speeds = coast_data['speed_rad_s']
        
        # Remove zero and negative speeds
        valid_mask = speeds > 0.1
        if np.sum(valid_mask) < 10:
            return {'time_constant': 1.0, 'initial_speed': 0, 'fit_quality': 0}
            
        times_valid = times[valid_mask]
        speeds_valid = speeds[valid_mask]
        
        # Fit exponential decay: ω(t) = ω₀ * exp(-t/τ)
        try:
            log_speeds = np.log(speeds_valid)
            # Linear fit: ln(ω) = ln(ω₀) - t/τ
            coeffs = np.polyfit(times_valid, log_speeds, 1)
            time_constant = -1.0 / coeffs[0] if coeffs[0] != 0 else 1.0
            initial_speed = np.exp(coeffs[1])
            
            # Calculate fit quality
            log_speeds_fit = coeffs[1] + coeffs[0] * times_valid
            r_squared = 1 - np.sum((log_speeds - log_speeds_fit)**2) / np.sum((log_speeds - np.mean(log_speeds))**2)
            
        except Exception as e:
            logger.warning(f"Coast-down analysis failed: {e}")
            time_constant = 1.0
            initial_speed = speeds_valid[0] if len(speeds_valid) > 0 else 0
            r_squared = 0
        
        return {
            'time_constant': float(time_constant),
            'initial_speed': float(initial_speed),
            'fit_quality': float(r_squared)
        }