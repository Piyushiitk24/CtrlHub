"""
File Upload Handler for OnShape Models
=====================================

FastAPI endpoints for uploading OnShape GLTF/STL files and generating URDF
for PyBullet simulation integration.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional, Dict, Any
import os
import shutil
import json
from pathlib import Path
import tempfile
import asyncio
import sys

# Add the simulation directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'simulation'))
from urdf_generator import URDFGenerator

router = APIRouter(prefix="/onshape", tags=["OnShape Integration"])

# Configuration
ALLOWED_EXTENSIONS = {'.stl', '.obj', '.dae', '.gltf', '.glb', '.urdf'}
UPLOAD_DIR = "meshes"
SIMULATION_DIR = "simulation"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SIMULATION_DIR, exist_ok=True)

@router.post("/upload-model")
async def upload_onshape_model(
    file: UploadFile = File(...),
    model_type: str = Form("complete")  # "complete", "base", "arm", "pendulum"
):
    """
    Upload OnShape model file (GLTF, STL, etc.)
    
    Args:
        file: The model file to upload
        model_type: Type of model - "complete" for full assembly, or specific part name
    """
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size (50MB limit)
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 50MB."
        )
    
    try:
        # Create unique filename
        safe_filename = f"{model_type}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        file_size = len(content)
        
        # Analyze file if it's GLTF
        analysis = None
        if file_ext == '.gltf':
            try:
                generator = URDFGenerator(".")
                analysis = generator.analyze_gltf(file_path)
            except Exception as e:
                print(f"GLTF analysis failed: {e}")
        
        return JSONResponse({
            "success": True,
            "message": "File uploaded successfully",
            "filename": safe_filename,
            "original_filename": file.filename,
            "path": file_path,
            "size": file_size,
            "type": model_type,
            "format": file_ext,
            "analysis": analysis
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    descriptions: List[str] = Form(...)
):
    """
    Upload multiple OnShape files (e.g., separate STL files for each part)
    
    Args:
        files: List of model files
        descriptions: List of descriptions for each file (base, arm, pendulum, etc.)
    """
    
    if len(files) != len(descriptions):
        raise HTTPException(
            status_code=400,
            detail="Number of files must match number of descriptions"
        )
    
    uploaded_files = []
    
    for file, description in zip(files, descriptions):
        try:
            # Validate file
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                continue
            
            # Save file
            safe_filename = f"{description}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append({
                "filename": safe_filename,
                "original_filename": file.filename,
                "path": file_path,
                "size": len(content),
                "type": description,
                "format": file_ext
            })
            
        except Exception as e:
            print(f"Failed to upload {file.filename}: {e}")
    
    return JSONResponse({
        "success": True,
        "message": f"Uploaded {len(uploaded_files)} files successfully",
        "files": uploaded_files
    })

@router.post("/generate-urdf")
async def generate_urdf_from_uploads():
    """
    Generate URDF file from uploaded OnShape models
    """
    
    try:
        generator = URDFGenerator(".")
        
        # Look for uploaded files
        uploaded_files = {}
        gltf_file = None
        
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                file_ext = Path(filename).suffix.lower()
                
                if file_ext == '.gltf':
                    gltf_file = file_path
                elif file_ext in ['.stl', '.obj']:
                    # Determine part type from filename
                    filename_lower = filename.lower()
                    if 'base' in filename_lower:
                        uploaded_files['base'] = file_path
                    elif 'arm' in filename_lower:
                        uploaded_files['arm'] = file_path
                    elif 'pendulum' in filename_lower:
                        uploaded_files['pendulum'] = file_path
        
        # Generate URDF
        if gltf_file:
            result = generator.generate_from_onshape_files(gltf_file, uploaded_files)
        elif uploaded_files:
            # Generate from STL files only
            mesh_files = uploaded_files
            urdf_content = generator.create_rotary_pendulum_urdf(mesh_files, use_gltf=False)
            urdf_path = generator.save_urdf(urdf_content)
            
            result = {
                'success': True,
                'urdf_path': urdf_path,
                'urdf_content': urdf_content,
                'mesh_files': mesh_files
            }
        else:
            raise Exception("No suitable model files found")
        
        if not result['success']:
            raise Exception(result.get('error', 'Unknown error'))
        
        return JSONResponse({
            "success": True,
            "message": "URDF generated successfully",
            "urdf_path": result['urdf_path'],
            "mesh_files": result.get('mesh_files', {}),
            "gltf_analysis": result.get('gltf_analysis', None)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URDF generation failed: {str(e)}")

@router.get("/list-uploads")
async def list_uploaded_files():
    """List all uploaded model files"""
    
    files = []
    
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            file_ext = Path(filename).suffix.lower()
            
            if file_ext in ALLOWED_EXTENSIONS:
                file_stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "path": file_path,
                    "size": file_stat.st_size,
                    "format": file_ext,
                    "modified": file_stat.st_mtime
                })
    
    return JSONResponse({
        "success": True,
        "files": files,
        "count": len(files)
    })

@router.get("/download-urdf")
async def download_generated_urdf():
    """Download the generated URDF file"""
    
    urdf_path = os.path.join(SIMULATION_DIR, "rotary_pendulum.urdf")
    
    if not os.path.exists(urdf_path):
        raise HTTPException(status_code=404, detail="URDF file not found. Generate URDF first.")
    
    return FileResponse(
        urdf_path,
        media_type='application/xml',
        filename="rotary_pendulum.urdf"
    )

@router.delete("/clear-uploads")
async def clear_uploaded_files():
    """Clear all uploaded files"""
    
    try:
        cleared_count = 0
        
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    cleared_count += 1
        
        return JSONResponse({
            "success": True,
            "message": f"Cleared {cleared_count} files",
            "count": cleared_count
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear files: {str(e)}")

@router.post("/validate-model")
async def validate_uploaded_model(filename: str):
    """
    Validate an uploaded model file and provide feedback
    
    Args:
        filename: Name of the uploaded file to validate
    """
    
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    file_ext = Path(filename).suffix.lower()
    validation_result = {
        "filename": filename,
        "format": file_ext,
        "valid": False,
        "issues": [],
        "recommendations": []
    }
    
    try:
        if file_ext == '.gltf':
            # Validate GLTF structure
            generator = URDFGenerator(".")
            analysis = generator.analyze_gltf(file_path)
            
            if analysis['success']:
                validation_result["valid"] = True
                validation_result["components"] = analysis['components']
                validation_result["materials"] = len(analysis.get('materials', []))
                validation_result["meshes"] = len(analysis.get('meshes', []))
                
                # Check for required components
                required_components = ['base', 'arm', 'pendulum']
                found_components = list(analysis['components'].keys())
                missing = [comp for comp in required_components if comp not in found_components]
                
                if missing:
                    validation_result["issues"].append(f"Missing components: {', '.join(missing)}")
                    validation_result["recommendations"].append("Ensure all pendulum parts are included in the model")
                
            else:
                validation_result["issues"].append(f"GLTF analysis failed: {analysis.get('error', 'Unknown error')}")
        
        elif file_ext == '.stl':
            # Basic STL validation
            file_size = os.path.getsize(file_path)
            
            if file_size > 0:
                validation_result["valid"] = True
                validation_result["size"] = file_size
                
                if file_size > 10 * 1024 * 1024:  # 10MB
                    validation_result["issues"].append("Large file size may slow down simulation")
                    validation_result["recommendations"].append("Consider reducing mesh complexity")
            else:
                validation_result["issues"].append("File appears to be empty")
        
        else:
            validation_result["issues"].append(f"File format {file_ext} not fully supported")
            validation_result["recommendations"].append("Use GLTF or STL format for best results")
        
        return JSONResponse({
            "success": True,
            "validation": validation_result
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.get("/model-info/{filename}")
async def get_model_info(filename: str):
    """Get detailed information about an uploaded model"""
    
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    file_stat = os.stat(file_path)
    file_ext = Path(filename).suffix.lower()
    
    info = {
        "filename": filename,
        "format": file_ext,
        "size": file_stat.st_size,
        "modified": file_stat.st_mtime,
        "path": file_path
    }
    
    # Add format-specific information
    if file_ext == '.gltf':
        try:
            generator = URDFGenerator(".")
            analysis = generator.analyze_gltf(file_path)
            if analysis['success']:
                info["gltf_info"] = {
                    "components": analysis['components'],
                    "materials_count": len(analysis.get('materials', [])),
                    "meshes_count": len(analysis.get('meshes', []))
                }
        except Exception as e:
            info["gltf_info"] = {"error": str(e)}
    
    return JSONResponse({
        "success": True,
        "info": info
    })

@router.post("/start-simulation")
async def start_onshape_simulation(
    request: dict
):
    """
    Start PyBullet simulation using OnShape-generated URDF
    
    Args:
        request: Dictionary containing:
            - urdf_path: Path to the generated URDF file
            - duration: Simulation duration in seconds
            - pidGains: PID controller gains
            - gui: Whether to show GUI
    """
    try:
        # Try to import PyBullet simulation first
        try:
            # Add integrations directory to path
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'integrations'))
            from pybullet_onshape_sim import OnShapePyBulletSimulation
            PYBULLET_AVAILABLE = True
        except ImportError as e:
            print(f"PyBullet not available: {e}. Using basic physics simulation fallback.")
            PYBULLET_AVAILABLE = False
            # Import basic physics simulation
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
            from basic_physics_sim import OnShapeBasicSimulation
        
        urdf_path = request.get('urdf_path')
        duration = request.get('duration', 30)
        pid_gains = request.get('pidGains', {'kp': 3.0, 'ki': 0.0, 'kd': 0.1})
        gui = request.get('gui', True)
        
        if not urdf_path or not os.path.exists(urdf_path):
            raise HTTPException(status_code=400, detail="Valid URDF path required")
        
        # Initialize simulation (PyBullet or basic physics)
        if PYBULLET_AVAILABLE:
            sim = OnShapePyBulletSimulation(urdf_path, gui=gui)
            
            # Set PID gains for PyBullet simulation
            sim.set_pid_gains(
                pid_gains.get('kp', 3.0),
                pid_gains.get('ki', 0.0), 
                pid_gains.get('kd', 0.1)
            )
            simulation_type = "PyBullet"
        else:
            sim = OnShapeBasicSimulation()
            sim.load_onshape_urdf(urdf_path)
            
            # Set PID gains for basic simulation (if method exists)
            if hasattr(sim, 'set_pid_gains'):
                sim.set_pid_gains(
                    pid_gains.get('kp', 3.0),
                    pid_gains.get('ki', 0.0),
                    pid_gains.get('kd', 0.1)
                )
            simulation_type = "BasicPhysics"
        
        # Store simulation instance globally for state access
        global onshape_simulation
        onshape_simulation = sim
        
        return JSONResponse({
            "success": True,
            "message": f"OnShape simulation started using {simulation_type}",
            "simulation_type": simulation_type,
            "urdf_path": urdf_path,
            "duration": duration,
            "pid_gains": pid_gains
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start OnShape simulation: {str(e)}")

@router.get("/simulation-state")
async def get_onshape_simulation_state():
    """Get current state of the OnShape simulation"""
    
    try:
        global onshape_simulation
        
        if 'onshape_simulation' not in globals() or onshape_simulation is None:
            raise HTTPException(status_code=400, detail="No OnShape simulation running")
        
        # Get state using the appropriate method for each simulation type
        if hasattr(onshape_simulation, 'get_state'):
            # PyBullet simulation
            state = onshape_simulation.get_state()
            
            return JSONResponse({
                "success": True,
                "simulation_type": "PyBullet",
                "state": {
                    "time": state['time'],
                    "armAngle": state['arm_angle'],
                    "armVelocity": state['arm_velocity'],
                    "pendulumAngle": state['pendulum_angle'],
                    "pendulumVelocity": state['pendulum_velocity']
                },
                "controlTorque": state.get('control_torque', 0),
                "targetPosition": state.get('target_position', 0)
            })
        
        elif hasattr(onshape_simulation, 'get_simulation_data'):
            # Basic physics simulation
            state = onshape_simulation.get_simulation_data()
            
            return JSONResponse({
                "success": True,
                "simulation_type": "BasicPhysics", 
                "state": {
                    "time": state['time'],
                    "armAngle": state['joint_positions'].get(0, 0),
                    "armVelocity": state['joint_velocities'].get(0, 0),
                    "pendulumAngle": state['joint_positions'].get(1, 0),
                    "pendulumVelocity": state['joint_velocities'].get(1, 0)
                },
                "controlTorque": state['joint_torques'].get(0, 0),
                "targetPosition": state['target_positions'].get(0, 0),
                "running": state['running']
            })
        
        else:
            raise HTTPException(status_code=500, detail="Unknown simulation type")
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@router.post("/simulation-control")
async def control_onshape_simulation(request: dict):
    """Enable/disable control for OnShape simulation"""
    
    try:
        global onshape_simulation
        
        if 'onshape_simulation' not in globals() or onshape_simulation is None:
            raise HTTPException(status_code=400, detail="No OnShape simulation running")
        
        enabled = request.get('enabled', False)
        
        if enabled:
            onshape_simulation.enable_control()
        else:
            onshape_simulation.disable_control()
        
        return JSONResponse({
            "success": True,
            "message": f"Control {'enabled' if enabled else 'disabled'}"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Control operation failed: {str(e)}")

@router.post("/stop-simulation")
async def stop_onshape_simulation():
    """Stop the OnShape simulation"""
    
    try:
        global onshape_simulation
        
        if 'onshape_simulation' not in globals() or onshape_simulation is None:
            return JSONResponse({
                "success": True,
                "message": "No simulation was running"
            })
        
        onshape_simulation.stop()
        onshape_simulation = None
        
        return JSONResponse({
            "success": True,
            "message": "OnShape simulation stopped"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop simulation: {str(e)}")

# Global variable to store simulation instance
onshape_simulation = None
