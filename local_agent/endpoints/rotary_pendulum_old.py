"""
FastAPI endpoints for Rotary Inverted Pendulum Experiment
========================================================

This module provides REST API endpoints for controlling and monitoring
the rotary inverted pendulum PyBullet simulation.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import logging
from pathlib import Path

from models.rotary_pendulum_sim import RotaryInvertedPendulumSim

logger = logging.getLogger(__name__)

# Global experiment instance
current_experiment: Optional[RotaryInvertedPendulumSim] = None

router = APIRouter(prefix="/experiments/rotary-pendulum", tags=["Rotary Pendulum"])

class PIDGainsRequest(BaseModel):
    kp: float
    ki: float
    kd: float

class ControlRequest(BaseModel):
    enabled: bool

class StartExperimentRequest(BaseModel):
    duration: float = 30.0
    pidGains: PIDGainsRequest
    gui: bool = True

@router.post("/start")
async def start_experiment(request: StartExperimentRequest):
    """Start the rotary pendulum simulation"""
    global current_experiment
    
    try:
        # Get mesh directory path
        mesh_dir = Path(__file__).parent.parent.parent / "meshes"
        
        if not mesh_dir.exists():
            raise HTTPException(status_code=500, detail="Mesh directory not found")
        
        # Create new experiment
        current_experiment = RotaryInvertedPendulumSim(
            mesh_dir=str(mesh_dir),
            gui=request.gui
        )
        
        # Setup experiment
        await current_experiment.setup_experiment()
        
        # Configure PID gains
        if current_experiment.simulation:
            current_experiment.simulation.set_pid_gains(
                request.pidGains.kp,
                request.pidGains.ki, 
                request.pidGains.kd
            )
        
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
        if current_experiment and current_experiment.simulation:
            # Get final results before stopping
            results = current_experiment.simulation.get_simulation_data()
            metrics = current_experiment._calculate_performance_metrics(results)
            
            # Stop simulation
            current_experiment.simulation.disable_control()
            
            logger.info("Rotary pendulum experiment stopped")
            
            return {
                "success": True,
                "message": "Experiment stopped successfully",
                "final_metrics": metrics
            }
        else:
            return {
                "success": False,
                "message": "No active experiment to stop"
            }
            
    except Exception as e:
        logger.error(f"Failed to stop experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_experiment():
    """Reset the current experiment"""
    global current_experiment
    
    try:
        if current_experiment and current_experiment.simulation:
            current_experiment.simulation.reset_simulation()
            
            logger.info("Rotary pendulum experiment reset")
            
            return {
                "success": True,
                "message": "Experiment reset successfully"
            }
        else:
            return {
                "success": False,
                "message": "No active experiment to reset"
            }
            
    except Exception as e:
        logger.error(f"Failed to reset experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/state")
async def get_current_state():
    """Get current pendulum state"""
    global current_experiment
    
    try:
        if current_experiment and current_experiment.simulation:
            # Update state from simulation
            current_experiment.simulation.update_state()
            state = current_experiment.simulation.current_state
            
            # Get encoder readings
            encoder_data = current_experiment.simulation.get_encoder_readings()
            
            return {
                "success": True,
                "state": {
                    "armAngle": state.arm_angle,
                    "armVelocity": state.arm_velocity,
                    "pendulumAngle": state.pendulum_angle,
                    "pendulumVelocity": state.pendulum_velocity,
                    "time": state.time
                },
                "controlEnabled": current_experiment.simulation.control_enabled,
                "encoders": encoder_data,
                "isUpright": current_experiment.simulation.is_pendulum_upright()
            }
        else:
            return {
                "success": False,
                "message": "No active experiment"
            }
            
    except Exception as e:
        logger.error(f"Failed to get state: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/control")
async def set_control_state(request: ControlRequest):
    """Enable or disable control"""
    global current_experiment
    
    try:
        if current_experiment and current_experiment.simulation:
            if request.enabled:
                current_experiment.simulation.enable_control()
            else:
                current_experiment.simulation.disable_control()
                
            return {
                "success": True,
                "message": f"Control {'enabled' if request.enabled else 'disabled'}",
                "control_enabled": request.enabled
            }
        else:
            return {
                "success": False,
                "message": "No active experiment"
            }
            
    except Exception as e:
        logger.error(f"Failed to set control state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pid")
async def update_pid_gains(gains: PIDGainsRequest):
    """Update PID controller gains"""
    global current_experiment
    
    try:
        if current_experiment and current_experiment.simulation:
            current_experiment.simulation.set_pid_gains(
                gains.kp, gains.ki, gains.kd
            )
            
            return {
                "success": True,
                "message": "PID gains updated",
                "gains": {
                    "kp": gains.kp,
                    "ki": gains.ki,
                    "kd": gains.kd
                }
            }
        else:
            return {
                "success": False,
                "message": "No active experiment"
            }
            
    except Exception as e:
        logger.error(f"Failed to update PID gains: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results")
async def get_experiment_results():
    """Get complete experiment results and metrics"""
    global current_experiment
    
    try:
        if current_experiment and current_experiment.simulation:
            # Get simulation data
            data = current_experiment.simulation.get_simulation_data()
            
            # Calculate metrics
            metrics = current_experiment._calculate_performance_metrics(data)
            
            return {
                "success": True,
                "data": data,
                "metrics": metrics,
                "experiment_info": {
                    "pid_gains": {
                        "kp": current_experiment.simulation.pid_controller.kp,
                        "ki": current_experiment.simulation.pid_controller.ki,
                        "kd": current_experiment.simulation.pid_controller.kd
                    },
                    "motor_params": {
                        "steps_per_revolution": current_experiment.simulation.motor_params.steps_per_revolution,
                        "microsteps": current_experiment.simulation.motor_params.microsteps,
                        "holding_torque": current_experiment.simulation.motor_params.holding_torque
                    }
                }
            }
        else:
            return {
                "success": False,
                "message": "No active experiment"
            }
            
    except Exception as e:
        logger.error(f"Failed to get results: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/status")
async def get_experiment_status():
    """Get overall experiment status"""
    global current_experiment
    
    try:
        if current_experiment and current_experiment.simulation:
            return {
                "success": True,
                "active": True,
                "control_enabled": current_experiment.simulation.control_enabled,
                "simulation_time": current_experiment.simulation.current_state.time,
                "pendulum_upright": current_experiment.simulation.is_pendulum_upright()
            }
        else:
            return {
                "success": True,
                "active": False,
                "message": "No active experiment"
            }
            
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/step")
async def step_simulation():
    """Advance simulation by one step (for manual control)"""
    global current_experiment
    
    try:
        if current_experiment and current_experiment.simulation:
            current_experiment.simulation.step_simulation()
            
            return {
                "success": True,
                "message": "Simulation stepped"
            }
        else:
            return {
                "success": False,
                "message": "No active experiment"
            }
            
    except Exception as e:
        logger.error(f"Failed to step simulation: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/hardware-mapping")
async def get_hardware_mapping():
    """Get the hardware connection mapping for reference"""
    return {
        "success": True,
        "hardware_mapping": {
            "stepper_motor": {
                "model": "17HS4023",
                "connections": {
                    "step_pin": 3,
                    "dir_pin": 2,
                    "enable_pin": 5
                },
                "specifications": {
                    "steps_per_revolution": 200,
                    "microsteps": 8,
                    "holding_torque": "0.4 N·m"
                }
            },
            "encoder": {
                "model": "AS5600",
                "connections": {
                    "scl_pin": "SCL (I2C)",
                    "sda_pin": "SDA (I2C)",
                    "dir_pin": "Direction output",
                    "vcc": "3.3V or 5V",
                    "gnd": "Ground"
                },
                "specifications": {
                    "resolution": "12-bit (4096 positions)",
                    "accuracy": "±0.1°",
                    "interface": "I2C"
                }
            },
            "power_supply": {
                "voltage": "12V",
                "current_rating": "2A minimum",
                "connection": "DC barrel jack"
            }
        }
    }
