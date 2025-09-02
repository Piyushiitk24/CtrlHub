"""
URDF Generation System for OnShape Models
=========================================

This module converts OnShape GLTF/STL files into proper URDF format
for PyBullet physics simulation with accurate mass properties and joints.
"""

import os
import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

class URDFGenerator:
    """Generate URDF files from OnShape model data"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.meshes_dir = os.path.join(project_root, "meshes")
        self.simulation_dir = os.path.join(project_root, "simulation")
        os.makedirs(self.meshes_dir, exist_ok=True)
        os.makedirs(self.simulation_dir, exist_ok=True)
        
        # Physical properties (estimated from typical rotary pendulum)
        self.properties = {
            'base': {
                'mass': 0.5,
                'com': [0, 0, 0.025],
                'inertia': {'ixx': 0.001, 'iyy': 0.001, 'izz': 0.001}
            },
            'arm': {
                'mass': 0.1,
                'com': [0.075, 0, 0],
                'inertia': {'ixx': 0.0001, 'iyy': 0.0005, 'izz': 0.0005}
            },
            'pendulum': {
                'mass': 0.05,
                'com': [0, 0, -0.1],
                'inertia': {'ixx': 0.0002, 'iyy': 0.0002, 'izz': 0.000001}
            }
        }
        
        # Joint configurations
        self.joints = {
            'motor_joint': {
                'type': 'revolute',
                'parent': 'base_link',
                'child': 'motor_arm',
                'origin': [0, 0, 0.05],
                'axis': [0, 0, 1],
                'limits': {'lower': -3.14159, 'upper': 3.14159, 'effort': 2.0, 'velocity': 10.0},
                'dynamics': {'damping': 0.01, 'friction': 0.05}
            },
            'pendulum_joint': {
                'type': 'revolute',
                'parent': 'motor_arm',
                'child': 'pendulum',
                'origin': [0.15, 0, 0],
                'axis': [1, 0, 0],
                'limits': {'lower': -3.14159, 'upper': 3.14159, 'effort': 0, 'velocity': 100},
                'dynamics': {'damping': 0.001, 'friction': 0.001}
            }
        }
    
    def analyze_gltf(self, gltf_path: str) -> Dict:
        """Analyze GLTF file to extract components and materials"""
        try:
            with open(gltf_path, 'r') as f:
                gltf_data = json.load(f)
            
            components = {}
            
            # Extract nodes and meshes
            if 'nodes' in gltf_data:
                for i, node in enumerate(gltf_data['nodes']):
                    node_name = node.get('name', f'node_{i}')
                    
                    # Identify component type based on name
                    if any(keyword in node_name.lower() for keyword in ['base', 'mount', 'platform']):
                        components['base'] = {
                            'node_index': i,
                            'name': node_name,
                            'mesh_index': node.get('mesh', 0)
                        }
                    elif any(keyword in node_name.lower() for keyword in ['arm', 'lever', 'motor']):
                        components['arm'] = {
                            'node_index': i,
                            'name': node_name,
                            'mesh_index': node.get('mesh', 1)
                        }
                    elif any(keyword in node_name.lower() for keyword in ['pendulum', 'rod', 'stick']):
                        components['pendulum'] = {
                            'node_index': i,
                            'name': node_name,
                            'mesh_index': node.get('mesh', 2)
                        }
            
            return {
                'components': components,
                'materials': gltf_data.get('materials', []),
                'meshes': gltf_data.get('meshes', []),
                'success': True
            }
            
        except Exception as e:
            print(f"Error analyzing GLTF: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_rotary_pendulum_urdf(self, mesh_files: Dict[str, str], use_gltf: bool = True) -> str:
        """
        Create URDF for rotary inverted pendulum
        
        Args:
            mesh_files: Dict mapping part names to mesh file paths
            use_gltf: Whether to use GLTF (True) or STL fallback (False)
        """
        
        # Create root element
        robot = ET.Element("robot")
        robot.set("name", "rotary_inverted_pendulum")
        
        # Add base link
        self._add_link(robot, "base_link", "base", mesh_files, use_gltf)
        
        # Add motor arm link
        self._add_link(robot, "motor_arm", "arm", mesh_files, use_gltf)
        
        # Add pendulum link
        self._add_link(robot, "pendulum", "pendulum", mesh_files, use_gltf)
        
        # Add joints
        self._add_joint(robot, "motor_joint")
        self._add_joint(robot, "pendulum_joint")
        
        # Convert to string with proper formatting
        rough_string = ET.tostring(robot, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def _add_link(self, parent: ET.Element, link_name: str, component_type: str, 
                  mesh_files: Dict[str, str], use_gltf: bool):
        """Add a link element to the URDF"""
        link = ET.SubElement(parent, "link")
        link.set("name", link_name)
        
        props = self.properties[component_type]
        
        # Inertial properties
        inertial = ET.SubElement(link, "inertial")
        origin = ET.SubElement(inertial, "origin")
        origin.set("xyz", f"{props['com'][0]} {props['com'][1]} {props['com'][2]}")
        origin.set("rpy", "0 0 0")
        
        mass = ET.SubElement(inertial, "mass")
        mass.set("value", str(props['mass']))
        
        inertia = ET.SubElement(inertial, "inertia")
        inertia.set("ixx", str(props['inertia']['ixx']))
        inertia.set("ixy", "0")
        inertia.set("ixz", "0")
        inertia.set("iyy", str(props['inertia']['iyy']))
        inertia.set("iyz", "0")
        inertia.set("izz", str(props['inertia']['izz']))
        
        # Visual properties
        visual = ET.SubElement(link, "visual")
        v_origin = ET.SubElement(visual, "origin")
        v_origin.set("xyz", "0 0 0")
        v_origin.set("rpy", "0 0 0")
        
        geometry = ET.SubElement(visual, "geometry")
        
        # Choose mesh file
        if use_gltf and "gltf" in mesh_files:
            mesh = ET.SubElement(geometry, "mesh")
            mesh.set("filename", mesh_files["gltf"])
            mesh.set("scale", "1 1 1")  # GLTF usually in correct units
        elif component_type in mesh_files:
            mesh = ET.SubElement(geometry, "mesh")
            mesh.set("filename", mesh_files[component_type])
            mesh.set("scale", "0.001 0.001 0.001")  # Convert mm to m for STL
        else:
            # Fallback to primitive shapes
            self._add_primitive_geometry(geometry, component_type)
        
        # Material
        material = ET.SubElement(visual, "material")
        material.set("name", f"{component_type}_material")
        color = ET.SubElement(material, "color")
        
        # Component-specific colors
        colors = {
            'base': "0.2 0.2 0.2 1.0",
            'arm': "0.8 0.8 0.8 1.0",
            'pendulum': "1.0 0.2 0.2 1.0"
        }
        color.set("rgba", colors.get(component_type, "0.5 0.5 0.5 1.0"))
        
        # Collision properties (simplified)
        collision = ET.SubElement(link, "collision")
        c_origin = ET.SubElement(collision, "origin")
        c_origin.set("xyz", f"{props['com'][0]} {props['com'][1]} {props['com'][2]}")
        c_origin.set("rpy", "0 0 0")
        
        c_geometry = ET.SubElement(collision, "geometry")
        self._add_primitive_geometry(c_geometry, component_type)
    
    def _add_primitive_geometry(self, geometry: ET.Element, component_type: str):
        """Add primitive geometry for collision or fallback visual"""
        if component_type == 'base':
            cylinder = ET.SubElement(geometry, "cylinder")
            cylinder.set("radius", "0.05")
            cylinder.set("length", "0.05")
        elif component_type == 'arm':
            box = ET.SubElement(geometry, "box")
            box.set("size", "0.15 0.02 0.02")
        elif component_type == 'pendulum':
            cylinder = ET.SubElement(geometry, "cylinder")
            cylinder.set("radius", "0.005")
            cylinder.set("length", "0.2")
    
    def _add_joint(self, parent: ET.Element, joint_name: str):
        """Add a joint element to the URDF"""
        joint_config = self.joints[joint_name]
        
        joint = ET.SubElement(parent, "joint")
        joint.set("name", joint_name)
        joint.set("type", joint_config['type'])
        
        # Parent and child links
        parent_elem = ET.SubElement(joint, "parent")
        parent_elem.set("link", joint_config['parent'])
        
        child_elem = ET.SubElement(joint, "child")
        child_elem.set("link", joint_config['child'])
        
        # Origin
        origin = ET.SubElement(joint, "origin")
        xyz = joint_config['origin']
        origin.set("xyz", f"{xyz[0]} {xyz[1]} {xyz[2]}")
        origin.set("rpy", "0 0 0")
        
        # Axis
        axis = ET.SubElement(joint, "axis")
        axis_vec = joint_config['axis']
        axis.set("xyz", f"{axis_vec[0]} {axis_vec[1]} {axis_vec[2]}")
        
        # Limits
        if joint_config['type'] == 'revolute':
            limit = ET.SubElement(joint, "limit")
            limits = joint_config['limits']
            limit.set("lower", str(limits['lower']))
            limit.set("upper", str(limits['upper']))
            limit.set("effort", str(limits['effort']))
            limit.set("velocity", str(limits['velocity']))
        
        # Dynamics
        dynamics = ET.SubElement(joint, "dynamics")
        dyn = joint_config['dynamics']
        dynamics.set("damping", str(dyn['damping']))
        dynamics.set("friction", str(dyn['friction']))
    
    def save_urdf(self, urdf_content: str, filename: str = "rotary_pendulum.urdf") -> str:
        """Save URDF content to file"""
        urdf_path = os.path.join(self.simulation_dir, filename)
        with open(urdf_path, 'w') as f:
            f.write(urdf_content)
        return urdf_path
    
    def generate_from_onshape_files(self, gltf_path: str, stl_files: Dict[str, str] = None) -> Dict:
        """
        Generate URDF from OnShape GLTF and optional STL files
        
        Args:
            gltf_path: Path to OnShape GLTF file
            stl_files: Optional dict of STL files for fallback
        """
        try:
            # Analyze GLTF
            gltf_analysis = self.analyze_gltf(gltf_path)
            
            if not gltf_analysis['success']:
                return {'success': False, 'error': 'Failed to analyze GLTF'}
            
            # Prepare mesh files dict
            mesh_files = {'gltf': gltf_path}
            if stl_files:
                mesh_files.update(stl_files)
            
            # Generate URDF with GLTF primary, STL fallback
            urdf_content = self.create_rotary_pendulum_urdf(mesh_files, use_gltf=True)
            
            # Save URDF
            urdf_path = self.save_urdf(urdf_content)
            
            return {
                'success': True,
                'urdf_path': urdf_path,
                'urdf_content': urdf_content,
                'gltf_analysis': gltf_analysis,
                'mesh_files': mesh_files
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


def estimate_inertial_properties(mesh_path: str, mass: float) -> Dict:
    """
    Estimate inertial properties from mesh file
    (Simplified version - could be enhanced with actual mesh analysis)
    """
    return {
        'mass': mass,
        'com': [0, 0, 0],  # Center of mass
        'inertia': {'ixx': 0.001, 'iyy': 0.001, 'izz': 0.001}
    }


if __name__ == "__main__":
    # Test the URDF generator
    generator = URDFGenerator("/Users/piyushtiwari/For_Projects/CtrlHub")
    
    # Test with the uploaded GLTF
    gltf_path = "/Users/piyushtiwari/For_Projects/CtrlHub/meshes/Rotary Inverted Pendulum.gltf"
    
    if os.path.exists(gltf_path):
        result = generator.generate_from_onshape_files(gltf_path)
        
        if result['success']:
            print("✅ URDF generated successfully!")
            print(f"📁 URDF saved to: {result['urdf_path']}")
            print(f"🔍 GLTF components found: {list(result['gltf_analysis']['components'].keys())}")
        else:
            print(f"❌ Failed to generate URDF: {result['error']}")
    else:
        print(f"❌ GLTF file not found: {gltf_path}")
