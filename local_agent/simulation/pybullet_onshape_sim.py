"""
PyBullet Physics Simulation for OnShape Rotary Pendulum
======================================================

This module provides PyBullet-based physics simulation using URDF generated
from OnShape models, with real-time control and state monitoring.
"""

import pybullet as p
import pybullet_data
import numpy as np
import os
import time
from typing import Optional, Dict, List, Tuple, Any
import json
from pathlib import Path

class OnShapePyBulletSimulation:
    """PyBullet-based rotary inverted pendulum simulation using OnShape models"""
    
    def __init__(self, urdf_path: Optional[str] = None, gui: bool = False):
        self.urdf_path = urdf_path
        self.gui = gui
        self.physics_client = None
        self.pendulum_id = None
        
        # Joint indices (will be determined from URDF)
        self.motor_joint_id = None
        self.pendulum_joint_id = None
        self.joint_name_to_id = {}
        
        # Simulation parameters
        self.dt = 1/240.0  # 240 Hz physics
        self.gravity = -9.81
        self.simulation_time = 0.0
        
        # State variables
        self.motor_position = 0.0
        self.motor_velocity = 0.0
        self.pendulum_angle = 0.0
        self.pendulum_velocity = 0.0
        
        # Control system
        self.pid_controller = PIDController(kp=20.0, ki=0.1, kd=2.0)
        self.control_enabled = False
        self.target_angle = 0.0  # Target pendulum angle (upright)
        
        # Data logging
        self.state_history = []
        self.max_history = 1000
        
        # Performance metrics
        self.metrics = {
            'rms_error': 0.0,
            'max_deviation': 0.0,
            'control_effort': 0.0,
            'uptime_percentage': 0.0
        }
    
    def initialize(self) -> bool:
        """Initialize PyBullet simulation"""
        try:
            # Connect to PyBullet
            if self.gui:
                self.physics_client = p.connect(p.GUI)
                p.configureDebugVisualizer(p.COV_ENABLE_GUI, 1)
                p.resetDebugVisualizerCamera(
                    cameraDistance=0.8,
                    cameraYaw=45,
                    cameraPitch=-20,
                    cameraTargetPosition=[0, 0, 0.1]
                )
                
                # Add debug sliders for PID tuning
                self._setup_debug_gui()
            else:
                self.physics_client = p.connect(p.DIRECT)
            
            # Set up physics
            p.setAdditionalSearchPath(pybullet_data.getDataPath())
            p.setGravity(0, 0, self.gravity)
            p.setTimeStep(self.dt)
            p.setRealTimeSimulation(0)  # Use stepped simulation
            
            # Load environment
            self._load_environment()
            
            # Load pendulum model
            if not self._load_pendulum_model():
                return False
            
            # Set initial conditions
            self._set_initial_state()
            
            print("✅ PyBullet simulation initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize PyBullet simulation: {e}")
            return False
    
    def _setup_debug_gui(self):
        """Setup debug GUI for PID tuning"""
        self.debug_kp = p.addUserDebugParameter("Kp", 0, 50, self.pid_controller.kp)
        self.debug_ki = p.addUserDebugParameter("Ki", 0, 5, self.pid_controller.ki)
        self.debug_kd = p.addUserDebugParameter("Kd", 0, 10, self.pid_controller.kd)
        self.debug_target = p.addUserDebugParameter("Target Angle", -0.5, 0.5, 0.0)
    
    def _load_environment(self):
        """Load environment (ground plane, lighting, etc.)"""
        # Load ground plane
        p.loadURDF("plane.urdf", basePosition=[0, 0, -0.1])
        
        # Add lighting for better visualization
        if self.gui:
            p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)
    
    def _load_pendulum_model(self) -> bool:
        """Load the pendulum model from URDF"""
        try:
            if self.urdf_path and os.path.exists(self.urdf_path):
                print(f"📁 Loading URDF: {self.urdf_path}")
                
                self.pendulum_id = p.loadURDF(
                    self.urdf_path, 
                    basePosition=[0, 0, 0],
                    baseOrientation=[0, 0, 0, 1],
                    useFixedBase=True,
                    flags=p.URDF_USE_INERTIA_FROM_FILE
                )
                
                # Get joint information
                self._analyze_joints()
                
                print(f"✅ Loaded OnShape model with {p.getNumJoints(self.pendulum_id)} joints")
                
            else:
                print("⚠️  URDF not found, creating simple model")
                self._create_simple_pendulum()
            
            return self.pendulum_id is not None
            
        except Exception as e:
            print(f"❌ Failed to load pendulum model: {e}")
            return False
    
    def _analyze_joints(self):
        """Analyze joints in the loaded URDF"""
        if self.pendulum_id is None:
            return
        
        num_joints = p.getNumJoints(self.pendulum_id)
        
        for joint_id in range(num_joints):
            joint_info = p.getJointInfo(self.pendulum_id, joint_id)
            joint_name = joint_info[1].decode('utf-8')
            joint_type = joint_info[2]
            
            self.joint_name_to_id[joint_name] = joint_id
            
            print(f"🔗 Joint {joint_id}: {joint_name} (type: {joint_type})")
            
            # Identify motor and pendulum joints
            if 'motor' in joint_name.lower():
                self.motor_joint_id = joint_id
            elif 'pendulum' in joint_name.lower():
                self.pendulum_joint_id = joint_id
        
        # Fallback if names don't match
        if self.motor_joint_id is None:
            self.motor_joint_id = 0
        if self.pendulum_joint_id is None:
            self.pendulum_joint_id = 1 if num_joints > 1 else 0
    
    def _create_simple_pendulum(self):
        """Create a simple pendulum model using basic shapes (fallback)"""
        # This is a fallback if URDF loading fails
        base_collision = p.createCollisionShape(p.GEOM_CYLINDER, radius=0.05, height=0.1)
        base_visual = p.createVisualShape(p.GEOM_CYLINDER, radius=0.05, height=0.1, 
                                         rgbaColor=[0.2, 0.2, 0.2, 1])
        
        arm_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.075, 0.01, 0.01])
        arm_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.075, 0.01, 0.01],
                                        rgbaColor=[0.8, 0.8, 0.8, 1])
        
        pend_collision = p.createCollisionShape(p.GEOM_CYLINDER, radius=0.005, height=0.2)
        pend_visual = p.createVisualShape(p.GEOM_CYLINDER, radius=0.005, height=0.2,
                                         rgbaColor=[1.0, 0.2, 0.2, 1])
        
        self.pendulum_id = p.createMultiBody(
            baseMass=0.1,
            baseCollisionShapeIndex=arm_collision,
            baseVisualShapeIndex=arm_visual,
            basePosition=[0, 0, 0.1],
            linkMasses=[0.05],
            linkCollisionShapeIndices=[pend_collision],
            linkVisualShapeIndices=[pend_visual],
            linkPositions=[[0.15, 0, 0]],
            linkOrientations=[[0, 0, 0, 1]],
            linkInertialFramePositions=[[0, 0, -0.1]],
            linkInertialFrameOrientations=[[0, 0, 0, 1]],
            linkParentIndices=[0],
            linkJointTypes=[p.JOINT_REVOLUTE],
            linkJointAxis=[[1, 0, 0]]
        )
        
        self.motor_joint_id = 0
        self.pendulum_joint_id = 0
    
    def _set_initial_state(self):
        """Set initial joint positions and velocities"""
        if self.pendulum_id is None:
            return
        
        # Set motor joint to 0
        if self.motor_joint_id is not None:
            p.resetJointState(self.pendulum_id, self.motor_joint_id, 0.0)
        
        # Set pendulum slightly off vertical (small perturbation)
        if self.pendulum_joint_id is not None:
            p.resetJointState(self.pendulum_id, self.pendulum_joint_id, 0.1)
        
        # Reset controller
        self.pid_controller.reset()
        self.simulation_time = 0.0
        self.state_history.clear()
    
    def step_simulation(self, duration: float = None) -> Dict[str, Any]:
        """
        Step the simulation and return current state
        
        Args:
            duration: If provided, run for this many seconds
        """
        if self.pendulum_id is None:
            return {'error': 'Simulation not initialized'}
        
        # Update PID gains from debug GUI if available
        if self.gui and hasattr(self, 'debug_kp'):
            self._update_debug_parameters()
        
        # Get current state
        current_state = self._get_current_state()
        
        # Apply control if enabled
        control_torque = 0.0
        if self.control_enabled:
            control_torque = self._apply_control(current_state)
        
        # Step physics
        p.stepSimulation()
        self.simulation_time += self.dt
        
        # Log state
        self._log_state(current_state, control_torque)
        
        # Calculate metrics
        self._update_metrics()
        
        # Prepare return data
        return {
            'success': True,
            'time': self.simulation_time,
            'motor_angle': np.degrees(current_state['motor_position']),
            'motor_velocity': np.degrees(current_state['motor_velocity']),
            'pendulum_angle': np.degrees(current_state['pendulum_angle']),
            'pendulum_velocity': np.degrees(current_state['pendulum_velocity']),
            'control_torque': control_torque,
            'control_enabled': self.control_enabled,
            'target_angle': np.degrees(self.target_angle),
            'metrics': self.metrics.copy()
        }
    
    def _get_current_state(self) -> Dict[str, float]:
        """Get current joint states"""
        motor_state = p.getJointState(self.pendulum_id, self.motor_joint_id)
        pendulum_state = p.getJointState(self.pendulum_id, self.pendulum_joint_id)
        
        return {
            'motor_position': motor_state[0],
            'motor_velocity': motor_state[1],
            'pendulum_angle': pendulum_state[0],
            'pendulum_velocity': pendulum_state[1]
        }
    
    def _apply_control(self, state: Dict[str, float]) -> float:
        """Apply PID control to balance the pendulum"""
        # Error is difference between target and current pendulum angle
        error = self.target_angle - state['pendulum_angle']
        
        # Calculate control output
        control_output = self.pid_controller.update(error, self.dt)
        
        # Apply torque to motor joint
        if self.motor_joint_id is not None:
            p.setJointMotorControl2(
                self.pendulum_id,
                self.motor_joint_id,
                p.TORQUE_CONTROL,
                force=control_output
            )
        
        return control_output
    
    def _update_debug_parameters(self):
        """Update PID parameters from debug GUI"""
        kp = p.readUserDebugParameter(self.debug_kp)
        ki = p.readUserDebugParameter(self.debug_ki)
        kd = p.readUserDebugParameter(self.debug_kd)
        self.target_angle = p.readUserDebugParameter(self.debug_target)
        
        self.pid_controller.set_gains(kp, ki, kd)
    
    def _log_state(self, state: Dict[str, float], control_torque: float):
        """Log current state for analysis"""
        log_entry = {
            'time': self.simulation_time,
            'motor_angle': state['motor_position'],
            'motor_velocity': state['motor_velocity'],
            'pendulum_angle': state['pendulum_angle'],
            'pendulum_velocity': state['pendulum_velocity'],
            'control_torque': control_torque,
            'error': self.target_angle - state['pendulum_angle']
        }
        
        self.state_history.append(log_entry)
        
        # Limit history size
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)
    
    def _update_metrics(self):
        """Update performance metrics"""
        if len(self.state_history) < 10:
            return
        
        recent_history = self.state_history[-100:]  # Last 100 samples
        
        # RMS error
        errors = [abs(entry['error']) for entry in recent_history]
        self.metrics['rms_error'] = np.sqrt(np.mean(np.square(errors)))
        
        # Max deviation
        self.metrics['max_deviation'] = max(errors)
        
        # Control effort
        torques = [abs(entry['control_torque']) for entry in recent_history]
        self.metrics['control_effort'] = np.mean(torques)
        
        # Uptime percentage (percentage of time pendulum is within 10 degrees of upright)
        upright_count = sum(1 for error in errors if error < np.radians(10))
        self.metrics['uptime_percentage'] = (upright_count / len(errors)) * 100
    
    def set_pid_gains(self, kp: float, ki: float, kd: float):
        """Set PID controller gains"""
        self.pid_controller.set_gains(kp, ki, kd)
    
    def enable_control(self):
        """Enable PID control"""
        self.control_enabled = True
        self.pid_controller.reset()
    
    def disable_control(self):
        """Disable PID control"""
        self.control_enabled = False
        # Set motor torque to 0
        if self.pendulum_id and self.motor_joint_id is not None:
            p.setJointMotorControl2(
                self.pendulum_id,
                self.motor_joint_id,
                p.TORQUE_CONTROL,
                force=0
            )
    
    def reset_simulation(self):
        """Reset simulation to initial state"""
        self._set_initial_state()
        self.metrics = {
            'rms_error': 0.0,
            'max_deviation': 0.0,
            'control_effort': 0.0,
            'uptime_percentage': 0.0
        }
    
    def get_state_history(self) -> List[Dict]:
        """Get the complete state history"""
        return self.state_history.copy()
    
    def close(self):
        """Close PyBullet simulation"""
        if self.physics_client is not None:
            p.disconnect(self.physics_client)
            self.physics_client = None


class PIDController:
    """PID Controller for pendulum balancing"""
    
    def __init__(self, kp: float = 20.0, ki: float = 0.1, kd: float = 2.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.integral = 0.0
        self.previous_error = 0.0
        self.max_integral = 10.0  # Anti-windup
    
    def update(self, error: float, dt: float) -> float:
        """Update PID controller and return control output"""
        # Proportional term
        proportional = self.kp * error
        
        # Integral term with anti-windup
        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.max_integral, self.max_integral)
        integral = self.ki * self.integral
        
        # Derivative term
        derivative = self.kd * (error - self.previous_error) / dt
        
        # Store error for next iteration
        self.previous_error = error
        
        return proportional + integral + derivative
    
    def set_gains(self, kp: float, ki: float, kd: float):
        """Set PID gains"""
        self.kp = kp
        self.ki = ki
        self.kd = kd
    
    def reset(self):
        """Reset PID controller state"""
        self.integral = 0.0
        self.previous_error = 0.0


if __name__ == "__main__":
    # Test the PyBullet simulation
    print("🧪 Testing PyBullet OnShape Simulation")
    
    # Check for URDF
    urdf_path = "/Users/piyushtiwari/For_Projects/CtrlHub/simulation/rotary_pendulum.urdf"
    
    sim = OnShapePyBulletSimulation(urdf_path=urdf_path, gui=True)
    
    if sim.initialize():
        print("✅ Simulation initialized")
        sim.enable_control()
        
        # Run simulation for 10 seconds
        for i in range(2400):  # 10 seconds at 240 Hz
            state = sim.step_simulation()
            
            if i % 240 == 0:  # Print every second
                print(f"Time: {state['time']:.1f}s, "
                      f"Pendulum: {state['pendulum_angle']:.1f}°, "
                      f"RMS Error: {state['metrics']['rms_error']:.3f}")
        
        sim.close()
    else:
        print("❌ Failed to initialize simulation")
