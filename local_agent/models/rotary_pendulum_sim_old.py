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

import pybullet as p
import pybullet_data
import numpy as np
import time
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class PendulumState:
    """Current state of the pendulum system"""
    arm_angle: float  # radians
    arm_velocity: float  # rad/s
    pendulum_angle: float  # radians from vertical (0 = upright)
    pendulum_velocity: float  # rad/s
    time: float  # simulation time

@dataclass
class StepperMotorParams:
    """Stepper motor parameters matching 17HS4023"""
    steps_per_revolution: int = 200
    microsteps: int = 8
    holding_torque: float = 0.4  # N⋅m
    detent_torque: float = 0.012  # N⋅m
    rotor_inertia: float = 5.4e-5  # kg⋅m²
    max_velocity: float = 5.0  # rad/s
    max_acceleration: float = 10.0  # rad/s²

@dataclass
class PIDController:
    """PID controller for pendulum stabilization"""
    kp: float = 3.0
    ki: float = 0.0  
    kd: float = 0.1
    integral: float = 0.0
    prev_error: float = 0.0
    output_limit: float = 1.0  # N⋅m

    def update(self, error: float, dt: float) -> float:
        """Update PID controller and return control output"""
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        
        # Apply output limits
        output = max(-self.output_limit, min(self.output_limit, output))
        
        self.prev_error = error
        return output

    def reset(self):
        """Reset PID controller state"""
        self.integral = 0.0
        self.prev_error = 0.0

class AS5600Encoder:
    """Simulated AS5600 magnetic encoder"""
    
    def __init__(self, resolution: int = 4096):
        self.resolution = resolution
        self.noise_std = 0.1  # degrees
        self.prev_raw = 0
        self.total_revolutions = 0
        
    def read_angle(self, true_angle: float) -> Tuple[int, float]:
        """
        Simulate AS5600 encoder reading
        
        Args:
            true_angle: True angle in radians
            
        Returns:
            (raw_value, degrees_continuous)
        """
        # Convert to degrees and add noise
        angle_deg = math.degrees(true_angle) + np.random.normal(0, self.noise_std)
        
        # Simulate 12-bit encoder (0-4095)
        raw_value = int((angle_deg % 360) / 360 * self.resolution) % self.resolution
        
        # Track revolutions for continuous angle
        delta_raw = raw_value - self.prev_raw
        if delta_raw > self.resolution // 2:
            delta_raw -= self.resolution
        elif delta_raw < -self.resolution // 2:
            delta_raw += self.resolution
            
        self.total_revolutions += delta_raw / self.resolution
        continuous_deg = self.total_revolutions * 360 + (raw_value / self.resolution * 360)
        
        self.prev_raw = raw_value
        
        return raw_value, continuous_deg
    
    def reset(self):
        """Reset encoder state"""
        self.prev_raw = 0
        self.total_revolutions = 0

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
        
    def initialize_simulation(self):
        """Initialize PyBullet physics simulation"""
        # Connect to physics server
        if self.gui:
            self.client_id = p.connect(p.GUI)
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 1)
            p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)
        else:
            self.client_id = p.connect(p.DIRECT)
            
        # Set up physics
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.setTimeStep(self.dt)
        p.setRealTimeSimulation(0)
        
        # Load ground plane
        p.loadURDF("plane.urdf")
        
        # Load robot
        try:
            # Change to mesh directory for relative paths
            original_cwd = Path.cwd()
            mesh_dir_abs = self.mesh_dir.resolve()
            
            # Create a temporary URDF with absolute mesh paths
            temp_urdf = self._create_absolute_urdf()
            
            self.robot_id = p.loadURDF(str(temp_urdf), [0, 0, 0])
            
            # Clean up temp file
            temp_urdf.unlink()
            
        except Exception as e:
            logger.error(f"Failed to load URDF: {e}")
            raise
            
        # Get joint information
        num_joints = p.getNumJoints(self.robot_id)
        logger.info(f"Robot loaded with {num_joints} joints")
        
        for i in range(num_joints):
            joint_info = p.getJointInfo(self.robot_id, i)
            logger.info(f"Joint {i}: {joint_info[1].decode('utf-8')} (type: {joint_info[2]})")
            
        # Set joint dynamics
        p.changeDynamics(self.robot_id, self.arm_joint_id, 
                        linearDamping=0.001, angularDamping=0.001)
        p.changeDynamics(self.robot_id, self.pendulum_joint_id,
                        linearDamping=0.0001, angularDamping=0.0001)
        
        # Initialize joint positions
        p.resetJointState(self.robot_id, self.arm_joint_id, 0)
        p.resetJointState(self.robot_id, self.pendulum_joint_id, math.pi)  # Start inverted
        
        logger.info("PyBullet simulation initialized successfully")
        
    def _create_absolute_urdf(self) -> Path:
        """Create a temporary URDF file with absolute mesh paths"""
        urdf_content = self.urdf_path.read_text()
        
        # Replace relative mesh paths with absolute paths
        mesh_files = ['base.stl', 'lid.stl', 'arm.stl', 'pendulum.stl']
        for mesh_file in mesh_files:
            rel_path = f'filename="{mesh_file}"'
            abs_path = f'filename="{self.mesh_dir / mesh_file}"'
            urdf_content = urdf_content.replace(rel_path, abs_path)
            
        # Create temporary file
        temp_urdf = self.mesh_dir / "temp_inverted_pendulum.urdf"
        temp_urdf.write_text(urdf_content)
        
        return temp_urdf
        
    def update_state(self):
        """Update current system state from PyBullet"""
        # Get arm state
        arm_pos, arm_vel, _, _ = p.getJointState(self.robot_id, self.arm_joint_id)
        
        # Get pendulum state  
        pend_pos, pend_vel, _, _ = p.getJointState(self.robot_id, self.pendulum_joint_id)
        
        # Convert pendulum angle to deviation from upright (0 = upright)
        pendulum_angle = self._normalize_angle(pend_pos - math.pi)
        
        self.current_state = PendulumState(
            arm_angle=arm_pos,
            arm_velocity=arm_vel,
            pendulum_angle=pendulum_angle,
            pendulum_velocity=pend_vel,
            time=time.time()
        )
        
    def _normalize_angle(self, angle: float) -> float:
        """Normalize angle to [-pi, pi]"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
        
    def is_pendulum_upright(self, tolerance: float = 0.4) -> bool:
        """Check if pendulum is close to upright position"""
        return abs(self.current_state.pendulum_angle) < tolerance
        
    def apply_control(self):
        """Apply PID control to stabilize pendulum"""
        current_time = self.current_state.time
        
        if current_time - self.last_control_time < self.control_dt:
            return
            
        if not self.control_enabled:
            return
            
        # PID control for pendulum stabilization
        pendulum_error = -self.current_state.pendulum_angle  # Want 0 (upright)
        dt = current_time - self.last_control_time
        
        # Calculate control torque
        control_torque = self.pid_controller.update(pendulum_error, dt)
        
        # Apply stepper motor constraints
        control_torque = max(-self.motor_params.holding_torque, 
                           min(self.motor_params.holding_torque, control_torque))
        
        # Apply torque to arm joint
        p.setJointMotorControl2(self.robot_id, self.arm_joint_id,
                               p.TORQUE_CONTROL, force=control_torque)
        
        self.last_control_time = current_time
        
        # Log data
        self.data_log['time'].append(current_time)
        self.data_log['arm_angle'].append(self.current_state.arm_angle)
        self.data_log['arm_velocity'].append(self.current_state.arm_velocity)
        self.data_log['pendulum_angle'].append(self.current_state.pendulum_angle)
        self.data_log['pendulum_velocity'].append(self.current_state.pendulum_velocity)
        self.data_log['control_torque'].append(control_torque)
        self.data_log['target_position'].append(self.target_position)
        
    def enable_control(self):
        """Enable automatic control - starts balancing"""
        if self.is_pendulum_upright():
            self.control_enabled = True
            self.pid_controller.reset()
            logger.info("Control enabled - pendulum balancing started")
        else:
            logger.warning("Cannot enable control - pendulum not upright")
            
    def disable_control(self):
        """Disable automatic control"""
        self.control_enabled = False
        # Set motor to hold position
        p.setJointMotorControl2(self.robot_id, self.arm_joint_id,
                               p.POSITION_CONTROL, 
                               targetPosition=self.current_state.arm_angle,
                               force=0)
        logger.info("Control disabled")
        
    def step_simulation(self):
        """Advance simulation by one time step"""
        self.update_state()
        self.apply_control()
        p.stepSimulation()
        
        if self.gui:
            time.sleep(self.dt)  # Real-time visualization
            
    def run_simulation(self, duration: float = 30.0):
        """
        Run simulation for specified duration
        
        Args:
            duration: Simulation time in seconds
        """
        start_time = time.time()
        
        logger.info(f"Starting simulation for {duration} seconds")
        logger.info("Manual control:")
        logger.info("  - Move pendulum close to upright to enable control")
        logger.info("  - Press 'c' to manually enable control")
        logger.info("  - Press 'd' to disable control")
        logger.info("  - Press 'r' to reset simulation")
        
        try:
            while time.time() - start_time < duration:
                self.step_simulation()
                
                # Check for automatic control activation
                if not self.control_enabled and self.is_pendulum_upright():
                    print("🎯 Pendulum upright detected - enabling control")
                    self.enable_control()
                    
                # Check if pendulum fell
                if self.control_enabled and not self.is_pendulum_upright(tolerance=1.0):
                    print("💥 Pendulum fell - disabling control")
                    self.disable_control()
                    
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
            
        logger.info("Simulation completed")
        
    def get_encoder_readings(self) -> Dict[str, Any]:
        """Get simulated encoder readings"""
        arm_raw, arm_deg = self.arm_encoder.read_angle(self.current_state.arm_angle)
        pend_raw, pend_deg = self.pendulum_encoder.read_angle(self.current_state.pendulum_angle + math.pi)
        
        return {
            'arm_encoder': {
                'raw': arm_raw,
                'degrees': arm_deg,
                'radians': math.radians(arm_deg)
            },
            'pendulum_encoder': {
                'raw': pend_raw, 
                'degrees': pend_deg,
                'radians': math.radians(pend_deg)
            }
        }
        
    def set_pid_gains(self, kp: float, ki: float, kd: float):
        """Update PID controller gains"""
        self.pid_controller.kp = kp
        self.pid_controller.ki = ki
        self.pid_controller.kd = kd
        self.pid_controller.reset()
        logger.info(f"PID gains updated: Kp={kp}, Ki={ki}, Kd={kd}")
        
    def reset_simulation(self):
        """Reset simulation to initial state"""
        p.resetJointState(self.robot_id, self.arm_joint_id, 0)
        p.resetJointState(self.robot_id, self.pendulum_joint_id, math.pi)
        
        self.control_enabled = False
        self.pid_controller.reset()
        self.arm_encoder.reset()
        self.pendulum_encoder.reset()
        
        # Clear data log
        for key in self.data_log:
            self.data_log[key].clear()
            
        logger.info("Simulation reset")
        
    def get_simulation_data(self) -> Dict[str, List[float]]:
        """Get logged simulation data"""
        return self.data_log.copy()
        
    def close(self):
        """Clean up simulation"""
        if self.client_id is not None:
            p.disconnect(self.client_id)
            logger.info("PyBullet simulation closed")


class RotaryPendulumExperiment:
    """
    High-level experiment interface for rotary inverted pendulum
    
    This class provides a simplified interface for running pendulum experiments
    and integrates with the CtrlHub educational system.
    """
    
    def __init__(self, mesh_dir: str, gui: bool = True):
        self.mesh_dir = Path(mesh_dir)
        self.urdf_path = self.mesh_dir / "inverted_pendulum.urdf"
        self.gui = gui
        self.simulation = None
        
    async def setup_experiment(self):
        """Setup the pendulum experiment"""
        logger.info("Setting up rotary inverted pendulum experiment")
        
        # Verify files exist
        if not self.urdf_path.exists():
            raise FileNotFoundError(f"URDF file not found: {self.urdf_path}")
            
        required_meshes = ['base.stl', 'lid.stl', 'arm.stl', 'pendulum.stl']
        missing_meshes = [m for m in required_meshes if not (self.mesh_dir / m).exists()]
        if missing_meshes:
            raise FileNotFoundError(f"Missing mesh files: {missing_meshes}")
            
        # Initialize simulation
        self.simulation = RotaryInvertedPendulumSim(
            str(self.urdf_path), 
            str(self.mesh_dir), 
            gui=self.gui
        )
        self.simulation.initialize_simulation()
        
        logger.info("Rotary pendulum experiment ready")
        
    async def run_balancing_experiment(self, duration: float = 30.0, 
                                     kp: float = 3.0, ki: float = 0.0, 
                                     kd: float = 0.1) -> Dict[str, Any]:
        """
        Run pendulum balancing experiment
        
        Args:
            duration: Experiment duration in seconds
            kp, ki, kd: PID controller gains
            
        Returns:
            Experiment results with data and metrics
        """
        if not self.simulation:
            await self.setup_experiment()
            
        # Configure PID controller
        self.simulation.set_pid_gains(kp, ki, kd)
        
        logger.info(f"Running balancing experiment for {duration}s with PID gains: Kp={kp}, Ki={ki}, Kd={kd}")
        
        # Run simulation
        self.simulation.run_simulation(duration)
        
        # Collect results
        data = self.simulation.get_simulation_data()
        
        # Calculate performance metrics
        metrics = self._calculate_performance_metrics(data)
        
        return {
            'success': True,
            'duration': duration,
            'pid_gains': {'kp': kp, 'ki': ki, 'kd': kd},
            'data': data,
            'metrics': metrics,
            'experiment_type': 'pendulum_balancing'
        }
        
    def _calculate_performance_metrics(self, data: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate experiment performance metrics"""
        if not data['time']:
            return {}
            
        pendulum_angles = np.array(data['pendulum_angle'])
        control_torques = np.array(data['control_torque'])
        
        # RMS error (deviation from upright)
        rms_error = np.sqrt(np.mean(pendulum_angles**2))
        
        # Maximum deviation
        max_deviation = np.max(np.abs(pendulum_angles))
        
        # Control effort (RMS torque)
        control_effort = np.sqrt(np.mean(control_torques**2))
        
        # Settling time (time to get within 0.1 rad and stay there)
        settling_time = None
        tolerance = 0.1
        for i in range(len(pendulum_angles)):
            if all(abs(angle) < tolerance for angle in pendulum_angles[i:]):
                settling_time = data['time'][i] if i < len(data['time']) else None
                break
                
        # Uptime percentage (time within 0.5 rad of upright)
        upright_tolerance = 0.5
        uptime_count = sum(1 for angle in pendulum_angles if abs(angle) < upright_tolerance)
        uptime_percentage = (uptime_count / len(pendulum_angles)) * 100 if pendulum_angles.size > 0 else 0
        
        return {
            'rms_error_rad': float(rms_error),
            'rms_error_deg': float(np.degrees(rms_error)),
            'max_deviation_rad': float(max_deviation), 
            'max_deviation_deg': float(np.degrees(max_deviation)),
            'control_effort_nm': float(control_effort),
            'settling_time_s': settling_time,
            'uptime_percentage': float(uptime_percentage)
        }
        
    def close(self):
        """Clean up experiment"""
        if self.simulation:
            self.simulation.close()


# Example usage and testing
async def main():
    """Example usage of the rotary pendulum simulation"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Path to meshes directory
    mesh_dir = Path(__file__).parent.parent / "meshes"
    
    try:
        # Create experiment
        experiment = RotaryPendulumExperiment(str(mesh_dir), gui=True)
        
        # Run balancing experiment
        result = await experiment.run_balancing_experiment(
            duration=30.0,
            kp=2.0,
            ki=0.1, 
            kd=0.2
        )
        
        if result['success']:
            print("\n🎯 Experiment Results:")
            print(f"   RMS Error: {result['metrics']['rms_error_deg']:.2f}°")
            print(f"   Max Deviation: {result['metrics']['max_deviation_deg']:.2f}°")
            print(f"   Control Effort: {result['metrics']['control_effort_nm']:.3f} N⋅m")
            print(f"   Uptime: {result['metrics']['uptime_percentage']:.1f}%")
            if result['metrics']['settling_time_s']:
                print(f"   Settling Time: {result['metrics']['settling_time_s']:.2f}s")
        
    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        
    finally:
        if 'experiment' in locals():
            experiment.close()


if __name__ == "__main__":
    asyncio.run(main())
