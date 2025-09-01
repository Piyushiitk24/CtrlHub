"""
FastAPI endpoints for rotary inverted pendulum experiments.

This module provides REST API endpoints for controlling and monitoring
the rotary inverted pendulum simulation system.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.rotary_pendulum_sim import RotaryInvertedPendulumSim

# Setup logging
logger = logging.getLogger(__name__)

# Router instance
router = APIRouter(prefix="/rotary-pendulum", tags=["rotary-pendulum"])

# Global experiment instance
current_experiment: Optional[RotaryInvertedPendulumSim] = None


# Request/Response Models
class PIDGains(BaseModel):
    kp: float = 10.0
    ki: float = 0.1
    kd: float = 5.0


class StartExperimentRequest(BaseModel):
    duration: float = 30.0
    pidGains: PIDGains = PIDGains()
    gui: bool = False


class PIDUpdateRequest(BaseModel):
    kp: float
    ki: float
    kd: float


class TargetAngleRequest(BaseModel):
    angle: float  # in degrees


# API Endpoints
@router.post("/start")
async def start_experiment(request: StartExperimentRequest):
    """Start the rotary pendulum simulation"""
    global current_experiment
    
    try:
        if current_experiment and current_experiment.running:
            return {"success": False, "message": "Experiment already running"}
        
        # Create new experiment
        current_experiment = RotaryInvertedPendulumSim()
        
        # Set PID parameters
        success = current_experiment.set_pid_parameters(
            request.pidGains.kp,
            request.pidGains.ki, 
            request.pidGains.kd
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set PID parameters")
        
        # Start experiment
        success = current_experiment.start_experiment()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to start experiment")
        
        logger.info(f"Rotary pendulum experiment started with duration {request.duration}s")
        
        return {
            "success": True,
            "message": "Experiment started successfully",
            "duration": request.duration,
            "pid_gains": {
                "kp": request.pidGains.kp,
                "ki": request.pidGains.ki,
                "kd": request.pidGains.kd
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to start experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_experiment():
    """Stop the current experiment"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {"success": False, "message": "No experiment running"}
        
        # Get performance metrics before stopping
        metrics = current_experiment.get_performance_metrics()
        
        # Stop experiment
        success = current_experiment.stop_experiment()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to stop experiment")
        
        logger.info("Rotary pendulum experiment stopped")
        
        return {
            "success": True,
            "message": "Experiment stopped successfully",
            "performance_metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Failed to stop experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_experiment():
    """Reset the experiment to initial conditions"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {"success": False, "message": "No experiment to reset"}
        
        success = current_experiment.reset_simulation()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset experiment")
        
        logger.info("Experiment reset to initial conditions")
        
        return {
            "success": True,
            "message": "Experiment reset successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to reset experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state")
async def get_state():
    """Get current system state"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {"success": False, "message": "No experiment running"}
        
        state = current_experiment.get_current_state()
        
        if not state:
            return {"success": False, "message": "No state data available"}
        
        return {
            "success": True,
            "state": state
        }
        
    except Exception as e:
        logger.error(f"Failed to get state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pid")
async def update_pid_gains(request: PIDUpdateRequest):
    """Update PID controller gains"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {"success": False, "message": "No experiment running"}
        
        success = current_experiment.set_pid_parameters(
            request.kp,
            request.ki,
            request.kd
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update PID gains")
        
        logger.info(f"PID gains updated: Kp={request.kp}, Ki={request.ki}, Kd={request.kd}")
        
        return {
            "success": True,
            "message": "PID gains updated successfully",
            "gains": {
                "kp": request.kp,
                "ki": request.ki,
                "kd": request.kd
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to update PID gains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/target")
async def set_target_angle(request: TargetAngleRequest):
    """Set target pendulum angle"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {"success": False, "message": "No experiment running"}
        
        # Convert degrees to radians
        angle_rad = request.angle * 3.14159 / 180.0
        
        success = current_experiment.set_target_angle(angle_rad)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set target angle")
        
        logger.info(f"Target angle set to {request.angle}°")
        
        return {
            "success": True,
            "message": f"Target angle set to {request.angle}°",
            "target_angle_degrees": request.angle,
            "target_angle_radians": angle_rad
        }
        
    except Exception as e:
        logger.error(f"Failed to set target angle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/control/enable")
async def enable_control():
    """Enable PID control"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {"success": False, "message": "No experiment running"}
        
        success = current_experiment.enable_control()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to enable control")
        
        logger.info("Control enabled")
        
        return {
            "success": True,
            "message": "Control enabled successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to enable control: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/control/disable")
async def disable_control():
    """Disable PID control"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {"success": False, "message": "No experiment running"}
        
        success = current_experiment.disable_control()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to disable control")
        
        logger.info("Control disabled")
        
        return {
            "success": True,
            "message": "Control disabled successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to disable control: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_performance_metrics():
    """Get performance metrics"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {"success": False, "message": "No experiment running"}
        
        metrics = current_experiment.get_performance_metrics()
        
        return {
            "success": True,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data")
async def get_experiment_data():
    """Get all logged experiment data"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {"success": False, "message": "No experiment running"}
        
        # Get recent data (last 1000 points to avoid overwhelming the API)
        data_log = current_experiment.data_log[-1000:] if len(current_experiment.data_log) > 1000 else current_experiment.data_log
        
        return {
            "success": True,
            "data": data_log,
            "total_points": len(current_experiment.data_log),
            "returned_points": len(data_log)
        }
        
    except Exception as e:
        logger.error(f"Failed to get experiment data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_data():
    """Export experiment data to file"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {"success": False, "message": "No experiment running"}
        
        filename = current_experiment.export_data()
        
        if not filename:
            raise HTTPException(status_code=500, detail="Failed to export data")
        
        return {
            "success": True,
            "message": "Data exported successfully",
            "filename": filename
        }
        
    except Exception as e:
        logger.error(f"Failed to export data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Get experiment status"""
    global current_experiment
    
    try:
        if not current_experiment:
            return {
                "success": True,
                "running": False,
                "message": "No experiment initialized"
            }
        
        return {
            "success": True,
            "running": current_experiment.running,
            "control_enabled": current_experiment.control_enabled,
            "data_points": len(current_experiment.data_log),
            "pid_parameters": {
                "kp": current_experiment.pid_controller.kp,
                "ki": current_experiment.pid_controller.ki,
                "kd": current_experiment.pid_controller.kd
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
