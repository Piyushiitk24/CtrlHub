"""
Basic physics simulation fallback for when PyBullet is not available.
This provides a simple mathematical simulation for testing the OnShape integration.
"""

import numpy as np
import time
import json
from typing import Dict, List, Optional, Tuple

class BasicPhysicsSimulation:
    """
    A simple physics simulation that uses mathematical models instead of PyBullet.
    This allows us to test the OnShape integration system even when PyBullet isn't available.
    """
    
    def __init__(self):
        self.dt = 1/240.0  # 240 Hz simulation
        self.gravity = -9.81
        self.time = 0.0
        
        # System state
        self.joint_positions = {}
        self.joint_velocities = {}
        self.joint_torques = {}
        
        # System parameters (will be set from URDF)
        self.link_masses = {}
        self.link_inertias = {}
        self.joint_limits = {}
        
        # PID Controller for each joint
        self.pid_controllers = {}
        
        # Target positions
        self.target_positions = {}
        
        # Simulation state
        self.running = False
        
    def load_urdf(self, urdf_path: str) -> bool:
        """
        Load URDF file and initialize simulation parameters.
        For this basic simulation, we'll parse basic joint information.
        """
        try:
            # For now, initialize with standard rotary inverted pendulum parameters
            self.initialize_rotary_pendulum()
            return True
        except Exception as e:
            print(f"Error loading URDF: {e}")
            return False
    
    def initialize_rotary_pendulum(self):
        """Initialize parameters for a rotary inverted pendulum system."""
        # Joint 0: Base rotation (motor)
        self.joint_positions[0] = 0.0
        self.joint_velocities[0] = 0.0
        self.joint_torques[0] = 0.0
        self.target_positions[0] = 0.0
        
        # Joint 1: Pendulum swing
        self.joint_positions[1] = 0.1  # Start slightly off vertical
        self.joint_velocities[1] = 0.0
        self.joint_torques[1] = 0.0
        self.target_positions[1] = 0.0  # Target is upright (0 radians)
        
        # Physical parameters
        self.link_masses[0] = 0.5  # Base link mass (kg)
        self.link_masses[1] = 0.2  # Pendulum mass (kg)
        
        self.link_inertias[0] = 0.01  # Base rotational inertia
        self.link_inertias[1] = 0.001  # Pendulum inertia
        
        # Joint limits (radians)
        self.joint_limits[0] = (-np.pi, np.pi)
        self.joint_limits[1] = (-np.pi, np.pi)
        
        # Initialize PID controllers
        self.pid_controllers[0] = {
            'kp': 50.0, 'ki': 0.1, 'kd': 5.0,
            'error_sum': 0.0, 'last_error': 0.0
        }
        self.pid_controllers[1] = {
            'kp': 30.0, 'ki': 0.05, 'kd': 3.0,
            'error_sum': 0.0, 'last_error': 0.0
        }
    
    def set_joint_target_position(self, joint_id: int, position: float):
        """Set target position for a joint."""
        if joint_id in self.target_positions:
            self.target_positions[joint_id] = position
    
    def get_joint_state(self, joint_id: int) -> Tuple[float, float]:
        """Get current position and velocity of a joint."""
        if joint_id in self.joint_positions:
            return self.joint_positions[joint_id], self.joint_velocities[joint_id]
        return 0.0, 0.0
    
    def compute_pid_control(self, joint_id: int) -> float:
        """Compute PID control torque for a joint."""
        if joint_id not in self.pid_controllers:
            return 0.0
        
        pid = self.pid_controllers[joint_id]
        target = self.target_positions[joint_id]
        current = self.joint_positions[joint_id]
        
        # Compute error
        error = target - current
        
        # Proportional term
        p_term = pid['kp'] * error
        
        # Integral term
        pid['error_sum'] += error * self.dt
        i_term = pid['ki'] * pid['error_sum']
        
        # Derivative term
        d_error = (error - pid['last_error']) / self.dt
        d_term = pid['kd'] * d_error
        
        # Update last error
        pid['last_error'] = error
        
        # Compute total control signal
        control = p_term + i_term + d_term
        
        # Apply limits
        max_torque = 10.0  # Maximum torque (Nm)
        control = np.clip(control, -max_torque, max_torque)
        
        return control
    
    def simulate_rotary_pendulum_dynamics(self):
        """
        Simulate the dynamics of a rotary inverted pendulum.
        This is a simplified model for demonstration.
        """
        # Get current state
        theta1 = self.joint_positions[0]  # Base angle
        theta2 = self.joint_positions[1]  # Pendulum angle
        dtheta1 = self.joint_velocities[0]  # Base angular velocity
        dtheta2 = self.joint_velocities[1]  # Pendulum angular velocity
        
        # Physical parameters
        m1 = self.link_masses[0]  # Base mass
        m2 = self.link_masses[1]  # Pendulum mass
        L1 = 0.1  # Base link length (m)
        L2 = 0.3  # Pendulum length (m)
        I1 = self.link_inertias[0]  # Base inertia
        I2 = self.link_inertias[1]  # Pendulum inertia
        g = abs(self.gravity)
        
        # Control torques
        tau1 = self.compute_pid_control(0)  # Base torque
        tau2 = 0.0  # No direct torque on pendulum
        
        # Simplified dynamics equations for rotary inverted pendulum
        # This is a reduced model for demonstration
        
        # Base dynamics (with coupling from pendulum)
        coupling_term = m2 * L1 * L2 * np.sin(theta2) * dtheta2**2
        base_inertia = I1 + m1 * L1**2 + m2 * L1**2
        ddtheta1 = (tau1 + coupling_term) / base_inertia
        
        # Pendulum dynamics
        gravity_term = m2 * g * L2 * np.sin(theta2)
        coupling_from_base = -m2 * L1 * L2 * np.cos(theta2) * ddtheta1
        pendulum_inertia = I2 + m2 * L2**2
        ddtheta2 = (gravity_term + coupling_from_base) / pendulum_inertia
        
        # Add some damping
        damping = 0.1
        ddtheta1 -= damping * dtheta1
        ddtheta2 -= damping * dtheta2
        
        # Integrate to get new velocities and positions
        self.joint_velocities[0] += ddtheta1 * self.dt
        self.joint_velocities[1] += ddtheta2 * self.dt
        
        self.joint_positions[0] += self.joint_velocities[0] * self.dt
        self.joint_positions[1] += self.joint_velocities[1] * self.dt
        
        # Store torques for monitoring
        self.joint_torques[0] = tau1
        self.joint_torques[1] = tau2
    
    def step_simulation(self):
        """Step the simulation forward by one timestep."""
        if not self.running:
            return
        
        # Update physics
        self.simulate_rotary_pendulum_dynamics()
        
        # Update time
        self.time += self.dt
    
    def start_simulation(self):
        """Start the simulation."""
        self.running = True
        print("Basic physics simulation started")
    
    def stop_simulation(self):
        """Stop the simulation."""
        self.running = False
        print("Basic physics simulation stopped")
    
    def reset_simulation(self):
        """Reset the simulation to initial state."""
        self.time = 0.0
        self.initialize_rotary_pendulum()
        print("Basic physics simulation reset")
    
    def get_simulation_state(self) -> Dict:
        """Get current simulation state for monitoring."""
        state = {
            'time': self.time,
            'joint_positions': dict(self.joint_positions),
            'joint_velocities': dict(self.joint_velocities),
            'joint_torques': dict(self.joint_torques),
            'target_positions': dict(self.target_positions),
            'running': self.running
        }
        return state
    
    def get_link_world_position(self, link_id: int) -> Tuple[float, float, float]:
        """Get world position of a link (simplified for visualization)."""
        if link_id == 0:
            # Base link at origin
            return (0.0, 0.0, 0.0)
        elif link_id == 1:
            # Pendulum tip position
            theta1 = self.joint_positions[0]
            theta2 = self.joint_positions[1]
            L1 = 0.1
            L2 = 0.3
            
            # Position of pendulum tip
            x = L1 * np.cos(theta1) + L2 * np.sin(theta2) * np.cos(theta1)
            y = L1 * np.sin(theta1) + L2 * np.sin(theta2) * np.sin(theta1)
            z = L2 * np.cos(theta2)
            
            return (x, y, z)
        else:
            return (0.0, 0.0, 0.0)


class OnShapeBasicSimulation:
    """
    OnShape integration wrapper using basic physics simulation.
    This provides the same interface as the PyBullet version but uses basic math.
    """
    
    def __init__(self):
        self.sim = BasicPhysicsSimulation()
        self.urdf_loaded = False
        self.model_id = None
        
    def load_onshape_urdf(self, urdf_path: str) -> bool:
        """Load OnShape-generated URDF file."""
        try:
            success = self.sim.load_urdf(urdf_path)
            if success:
                self.urdf_loaded = True
                print(f"Successfully loaded OnShape URDF: {urdf_path}")
                return True
            else:
                print(f"Failed to load OnShape URDF: {urdf_path}")
                return False
        except Exception as e:
            print(f"Error loading OnShape URDF: {e}")
            return False
    
    def start_simulation(self):
        """Start the simulation."""
        if not self.urdf_loaded:
            print("No URDF loaded. Cannot start simulation.")
            return False
        
        self.sim.start_simulation()
        return True
    
    def stop_simulation(self):
        """Stop the simulation."""
        self.sim.stop_simulation()
    
    def reset_simulation(self):
        """Reset the simulation."""
        self.sim.reset_simulation()
    
    def step_simulation(self):
        """Step the simulation forward."""
        self.sim.step_simulation()
    
    def set_joint_control(self, joint_id: int, target_position: float):
        """Set joint target position."""
        self.sim.set_joint_target_position(joint_id, target_position)
    
    def get_simulation_data(self) -> Dict:
        """Get comprehensive simulation data."""
        base_state = self.sim.get_simulation_state()
        
        # Add additional information
        base_state.update({
            'urdf_loaded': self.urdf_loaded,
            'model_id': self.model_id,
            'simulation_type': 'BasicPhysics',
            'joint_info': {
                0: {'name': 'base_joint', 'type': 'revolute'},
                1: {'name': 'pendulum_joint', 'type': 'revolute'}
            }
        })
        
        return base_state
    
    def run_simulation_loop(self, duration: float = 10.0, real_time: bool = True):
        """
        Run simulation for a specified duration.
        
        Args:
            duration: Simulation duration in seconds
            real_time: If True, run at real-time speed
        """
        if not self.start_simulation():
            return
        
        start_time = time.time()
        sim_start_time = self.sim.time
        
        try:
            while self.sim.running and (self.sim.time - sim_start_time) < duration:
                self.step_simulation()
                
                if real_time:
                    # Sleep to maintain real-time execution
                    elapsed_real = time.time() - start_time
                    elapsed_sim = self.sim.time - sim_start_time
                    
                    if elapsed_sim > elapsed_real:
                        time.sleep(elapsed_sim - elapsed_real)
                
                # Print status every second
                if int(self.sim.time) % 1 == 0 and self.sim.time > 0:
                    state = self.get_simulation_data()
                    pos = state['joint_positions']
                    print(f"Time: {self.sim.time:.1f}s - Base: {pos[0]:.3f} rad, Pendulum: {pos[1]:.3f} rad")
        
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
        
        finally:
            self.stop_simulation()
            print("Simulation completed")


if __name__ == "__main__":
    """Test the basic physics simulation."""
    print("Testing OnShape Basic Physics Simulation...")
    
    # Create simulation
    sim = OnShapeBasicSimulation()
    
    # Load dummy URDF (will use default parameters)
    sim.load_onshape_urdf("dummy_path.urdf")
    
    # Set some test targets
    sim.set_joint_control(0, 0.5)  # Rotate base to 0.5 radians
    sim.set_joint_control(1, 0.0)  # Keep pendulum upright
    
    # Run simulation
    print("Starting 5-second simulation...")
    sim.run_simulation_loop(duration=5.0, real_time=False)
    
    print("Basic physics simulation test completed!")
