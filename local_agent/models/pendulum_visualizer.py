"""
Enhanced rotary pendulum simulation with 3D visualization support.
This module extends the existing mathematical simulation with optional 3D rendering.
"""

import numpy as np
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    import trimesh
    import pyrender
    HAS_3D_SUPPORT = True
except ImportError:
    HAS_3D_SUPPORT = False

class PendulumVisualizer:
    """3D visualization for the rotary pendulum using trimesh and pyrender."""
    
    def __init__(self, urdf_path: Optional[str] = None):
        """Initialize the 3D visualizer."""
        self.urdf_path = urdf_path
        self.scene = None
        self.viewer = None
        self.meshes = {}
        self.nodes = {}
        
        if not HAS_3D_SUPPORT:
            print("⚠️  3D visualization not available. Install trimesh and pyrender for 3D support.")
            return
            
        self._setup_scene()
    
    def _setup_scene(self):
        """Setup the 3D scene."""
        if not HAS_3D_SUPPORT:
            return
            
        # Create scene
        self.scene = pyrender.Scene(bg_color=[0.1, 0.1, 0.2, 1.0])
        
        # Add lighting
        light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=3.0)
        light_node = pyrender.Node(light=light, matrix=np.eye(4))
        self.scene.add_node(light_node)
        
        # Add camera
        camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
        camera_pose = np.array([
            [1.0, 0.0, 0.0, 0.5],
            [0.0, 0.7, 0.7, 0.5],
            [0.0, -0.7, 0.7, 1.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
        camera_node = pyrender.Node(camera=camera, matrix=camera_pose)
        self.scene.add_node(camera_node)
        
        # Load URDF if provided
        if self.urdf_path and Path(self.urdf_path).exists():
            self._load_urdf()
        else:
            self._create_simple_pendulum()
    
    def _load_urdf(self):
        """Load URDF model."""
        try:
            import urdfpy
            robot = urdfpy.URDF.load(self.urdf_path)
            
            # Add robot to scene
            for link in robot.links:
                if link.visuals:
                    for visual in link.visuals:
                        if visual.geometry.mesh:
                            mesh = visual.geometry.mesh.load()
                            mesh_node = pyrender.Node(mesh=pyrender.Mesh.from_trimesh(mesh))
                            self.scene.add_node(mesh_node)
                            self.nodes[link.name] = mesh_node
                            
        except Exception as e:
            print(f"⚠️  Failed to load URDF: {e}")
            self._create_simple_pendulum()
    
    def _create_simple_pendulum(self):
        """Create a simple pendulum visualization."""
        # Base platform
        base_mesh = trimesh.creation.cylinder(radius=0.05, height=0.02)
        base_mesh.visual.face_colors = [100, 100, 100, 255]
        base_node = pyrender.Node(mesh=pyrender.Mesh.from_trimesh(base_mesh))
        self.scene.add_node(base_node)
        self.nodes['base'] = base_node
        
        # Arm
        arm_mesh = trimesh.creation.cylinder(radius=0.005, height=0.15)
        arm_mesh.visual.face_colors = [255, 100, 100, 255]
        arm_transform = np.eye(4)
        arm_transform[0, 3] = 0.075  # Position arm
        arm_node = pyrender.Node(mesh=pyrender.Mesh.from_trimesh(arm_mesh), matrix=arm_transform)
        self.scene.add_node(arm_node)
        self.nodes['arm'] = arm_node
        
        # Pendulum rod
        pendulum_mesh = trimesh.creation.cylinder(radius=0.003, height=0.30)
        pendulum_mesh.visual.face_colors = [100, 255, 100, 255]
        pendulum_transform = np.eye(4)
        pendulum_transform[0, 3] = 0.15  # At end of arm
        pendulum_transform[2, 3] = 0.15  # Vertical offset
        pendulum_node = pyrender.Node(mesh=pyrender.Mesh.from_trimesh(pendulum_mesh), matrix=pendulum_transform)
        self.scene.add_node(pendulum_node)
        self.nodes['pendulum'] = pendulum_node
    
    def update_pose(self, arm_angle: float, pendulum_angle: float):
        """Update the pose of the pendulum based on simulation state."""
        if not HAS_3D_SUPPORT or not self.scene:
            return
            
        # Update arm rotation
        if 'arm' in self.nodes:
            arm_transform = np.eye(4)
            arm_transform[0, 3] = 0.075
            # Rotate around Z-axis
            cos_a, sin_a = np.cos(arm_angle), np.sin(arm_angle)
            arm_transform[0, 0] = cos_a
            arm_transform[0, 1] = -sin_a
            arm_transform[1, 0] = sin_a
            arm_transform[1, 1] = cos_a
            self.nodes['arm'].matrix = arm_transform
        
        # Update pendulum rotation
        if 'pendulum' in self.nodes:
            pendulum_transform = np.eye(4)
            # Position at end of arm
            arm_end_x = 0.15 * np.cos(arm_angle)
            arm_end_y = 0.15 * np.sin(arm_angle)
            pendulum_transform[0, 3] = arm_end_x
            pendulum_transform[1, 3] = arm_end_y
            pendulum_transform[2, 3] = 0.15  # Half pendulum length up
            
            # Rotate pendulum around Y-axis (in arm's local frame)
            cos_p, sin_p = np.cos(pendulum_angle), np.sin(pendulum_angle)
            # Apply pendulum rotation in the arm's coordinate system
            pendulum_transform[0, 0] = cos_p * np.cos(arm_angle)
            pendulum_transform[0, 2] = sin_p * np.cos(arm_angle)
            pendulum_transform[1, 0] = cos_p * np.sin(arm_angle)
            pendulum_transform[1, 2] = sin_p * np.sin(arm_angle)
            pendulum_transform[2, 0] = -sin_p
            pendulum_transform[2, 2] = cos_p
            
            self.nodes['pendulum'].matrix = pendulum_transform
    
    def render_frame(self) -> Optional[np.ndarray]:
        """Render a single frame and return as image array."""
        if not HAS_3D_SUPPORT or not self.scene:
            return None
            
        try:
            # Render off-screen
            r = pyrender.OffscreenRenderer(640, 480)
            color, depth = r.render(self.scene)
            r.delete()
            return color
        except Exception as e:
            print(f"⚠️  Rendering failed: {e}")
            return None
    
    def start_viewer(self):
        """Start interactive 3D viewer (blocking)."""
        if not HAS_3D_SUPPORT or not self.scene:
            print("⚠️  3D visualization not available")
            return
            
        try:
            pyrender.Viewer(self.scene, use_raymond_lighting=True)
        except Exception as e:
            print(f"⚠️  Failed to start viewer: {e}")


def add_visualization_to_simulation():
    """Example of how to add 3D visualization to existing simulation."""
    print("🎯 Adding 3D Visualization Support")
    
    # Check if user has URDF file
    urdf_path = Path(__file__).parent.parent.parent / "meshes" / "inverted_pendulum.urdf"
    
    if urdf_path.exists():
        print(f"✅ Found URDF file: {urdf_path}")
        visualizer = PendulumVisualizer(str(urdf_path))
    else:
        print("ℹ️  No URDF found, using simple visualization")
        visualizer = PendulumVisualizer()
    
    # Test with some sample poses
    if HAS_3D_SUPPORT:
        print("🎬 Testing visualization...")
        for i in range(10):
            arm_angle = i * 0.1
            pendulum_angle = np.sin(i * 0.5) * 0.2
            visualizer.update_pose(arm_angle, pendulum_angle)
            
            # Render frame
            frame = visualizer.render_frame()
            if frame is not None:
                print(f"  Frame {i}: {frame.shape}")
    
    return visualizer


if __name__ == "__main__":
    add_visualization_to_simulation()
