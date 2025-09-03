"""
DC Motor PID Control Experiment Endpoints
Educational workflow from parameters to hardware validation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import numpy as np
import asyncio
import logging

# Import control library with fallback
try:
    import control
    CONTROL_AVAILABLE = True
except ImportError:
    control = None
    CONTROL_AVAILABLE = False
    logging.warning("Python control library not available - some features will be limited")

try:
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    signal = None
    SCIPY_AVAILABLE = False

router = APIRouter(prefix="/dc-motor-pid", tags=["DC Motor PID Control"])

# Data models
class DCMotorParams(BaseModel):
    J: float  # Moment of inertia (kg⋅m²)
    b: float  # Viscous friction coefficient (N⋅m⋅s/rad)
    K: float  # Torque/Back-EMF constant (N⋅m/A or V⋅s/rad)
    R: float  # Resistance (Ohms)
    L: float  # Inductance (H)

class PIDParams(BaseModel):
    Kp: float
    Ki: float
    Kd: float

class TransferFunction(BaseModel):
    numerator: List[float]
    denominator: List[float]
    display: str

class TestPIDRequest(BaseModel):
    tf: TransferFunction
    pid: PIDParams
    setpoint: float

class FinalExperimentRequest(BaseModel):
    tf: TransferFunction
    pid: PIDParams
    desired_speed: float
    duration: float = 10.0

@router.post("/generate_transfer_function")
async def generate_transfer_function(params: DCMotorParams) -> Dict[str, Any]:
    """
    Generate DC motor transfer function from physical parameters
    G(s) = K / (J*L*s^2 + (J*R + b*L)*s + (b*R + K^2))
    """
    try:
        # Calculate transfer function coefficients
        numerator = [params.K]
        denominator = [
            params.J * params.L,
            params.J * params.R + params.b * params.L,
            params.b * params.R + params.K * params.K
        ]
        
        # Create LaTeX display string
        display = f"\\frac{{{params.K:.4f}}}{{{denominator[0]:.4f}s^2 + {denominator[1]:.4f}s + {denominator[2]:.4f}}}"
        
        # Validate transfer function (check for stability, etc.)
        poles = np.roots(denominator) if len(denominator) > 1 else []
        stable = all(np.real(pole) < 0 for pole in poles) if len(poles) > 0 else True
        
        result = {
            "tf": {
                "numerator": numerator,
                "denominator": denominator,
                "display": display
            },
            "analysis": {
                "stable": stable,
                "poles": [complex(pole).real + 1j*complex(pole).imag for pole in poles],
                "dc_gain": numerator[0] / denominator[-1] if denominator[-1] != 0 else float('inf')
            },
            "success": True
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer function generation failed: {str(e)}")

@router.post("/get_step_plot")
async def get_step_plot(request: Dict[str, Any]) -> Dict[str, Any]:
    """Generate step response plot data"""
    try:
        tf_data = request["tf"]
        
        if CONTROL_AVAILABLE and control is not None:
            # Use Python control library for accurate simulation
            num = tf_data["numerator"]
            den = tf_data["denominator"]
            
            # Create transfer function
            sys = control.TransferFunction(num, den)
            
            # Generate step response
            time_span = np.linspace(0, 10, 1000)
            time, response = control.step_response(sys, time_span)
            
            # Calculate performance metrics - simplified since step_info may not be available
            try:
                # Basic metrics calculation from response data
                steady_state = response[-1]
                peak_val = np.max(response)
                peak_idx = np.argmax(response)
                
                # Find rise time (10% to 90% of final value)
                rise_start_idx = np.where(response >= 0.1 * steady_state)[0]
                rise_end_idx = np.where(response >= 0.9 * steady_state)[0]
                rise_time = float(time[rise_end_idx[0]] - time[rise_start_idx[0]]) if len(rise_start_idx) > 0 and len(rise_end_idx) > 0 else 0.0
                
                metrics = {
                    "rise_time": rise_time,
                    "settling_time": 0.0,  # Would need more complex calculation
                    "overshoot": ((peak_val - steady_state) / steady_state * 100) if steady_state > 0 else 0.0,
                    "peak_time": float(time[peak_idx])
                }
            except Exception:
                metrics = {
                    "rise_time": 0.0,
                    "settling_time": 0.0,
                    "overshoot": 0.0,
                    "peak_time": 0.0
                }
            
            return {
                "time": time.tolist(),
                "response": response.tolist(),
                "metrics": metrics,
                "success": True
            }
        else:
            # Fallback numerical simulation
            return await fallback_step_response(tf_data)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step response generation failed: {str(e)}")

@router.post("/get_bode_plot")
async def get_bode_plot(request: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Bode plot data"""
    try:
        tf_data = request["tf"]
        
        if CONTROL_AVAILABLE and control is not None:
            num = tf_data["numerator"]
            den = tf_data["denominator"]
            
            # Create transfer function
            sys = control.TransferFunction(num, den)
            
            # Generate Bode plot
            omega = np.logspace(-2, 3, 1000)  # 0.01 to 1000 rad/s
            mag, phase, omega = control.bode_plot(sys, omega, plot=False)
            
            # Convert to dB
            mag_db = 20 * np.log10(np.abs(mag))
            phase_deg = np.angle(phase) * 180 / np.pi
            
            return {
                "frequency": omega.tolist(),
                "magnitude_db": mag_db.tolist(),
                "phase_deg": phase_deg.tolist(),
                "success": True
            }
        else:
            raise HTTPException(status_code=501, detail="Bode plot requires Python control library")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bode plot generation failed: {str(e)}")

@router.post("/test_pid")
async def test_pid(request: TestPIDRequest) -> Dict[str, Any]:
    """Test PID controller with closed-loop simulation"""
    try:
        tf_data = request.tf
        pid_params = request.pid
        setpoint = request.setpoint
        
        if CONTROL_AVAILABLE and control is not None:
            # Create plant transfer function
            plant_num = tf_data.numerator
            plant_den = tf_data.denominator
            plant = control.TransferFunction(plant_num, plant_den)
            
            # Create PID controller transfer function
            # PID(s) = Kp + Ki/s + Kd*s = (Kd*s^2 + Kp*s + Ki)/s
            pid_num = [pid_params.Kd, pid_params.Kp, pid_params.Ki]
            pid_den = [1, 0]  # s in denominator
            pid_controller = control.TransferFunction(pid_num, pid_den)
            
            # Create closed-loop system
            # T(s) = C(s)*G(s) / (1 + C(s)*G(s))
            open_loop = control.series(pid_controller, plant)
            closed_loop = control.feedback(open_loop, 1)
            
            # Generate step response
            time_span = np.linspace(0, 10, 1000)
            time, response = control.step_response(closed_loop * setpoint, time_span)
            
            # Calculate basic performance metrics
            steady_state = response[-1]
            peak_val = np.max(response)
            peak_idx = np.argmax(response)
            
            return {
                "time": time.tolist(),
                "response": response.tolist(),
                "metrics": {
                    "rise_time": 0.0,  # Would need more complex calculation
                    "settling_time": 0.0,  # Would need more complex calculation
                    "overshoot": ((peak_val - steady_state) / steady_state * 100) if steady_state > 0 else 0.0,
                    "steady_state_error": float(abs(setpoint - response[-1])),
                },
                "success": True
            }
        else:
            return await fallback_pid_simulation(tf_data.dict(), pid_params, setpoint)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PID test failed: {str(e)}")

@router.post("/connect_hardware")
async def connect_hardware() -> Dict[str, Any]:
    """Connect to Arduino hardware"""
    try:
        # Import arduino interface
        from ..hardware.arduino_interface import ArduinoInterface
        
        interface = ArduinoInterface()
        success = await interface.connect()
        
        if success:
            return {
                "success": True,
                "port": getattr(interface, 'port', 'Unknown'),
                "message": "Arduino connected successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to connect to Arduino",
                "message": "Check USB connection and port availability"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Hardware connection error"
        }

@router.post("/run_hardware")
async def run_hardware(request: Dict[str, Any]) -> Dict[str, Any]:
    """Run PID control on hardware"""
    try:
        from ..hardware.arduino_interface import ArduinoInterface
        
        pid_params = request["pid"]
        desired_speed = request["desired_speed"]
        duration = request.get("duration", 10.0)
        
        interface = ArduinoInterface()
        
        # Send PID parameters
        await interface.send_command(f"SET_PID {pid_params['Kp']} {pid_params['Ki']} {pid_params['Kd']}")
        await asyncio.sleep(0.1)
        
        # Set desired speed
        await interface.send_command(f"SET_SPEED {desired_speed}")
        await asyncio.sleep(0.1)
        
        # Start control
        await interface.send_command("START_PID_CONTROL")
        
        # Collect data
        time_data = []
        speed_data = []
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            try:
                response = await interface.send_command("GET_SPEED")
                if response and "speed" in response:
                    current_time = asyncio.get_event_loop().time() - start_time
                    time_data.append(current_time)
                    speed_data.append(response["speed"])
                
                await asyncio.sleep(0.05)  # 20Hz sampling
            except Exception as e:
                logging.warning(f"Data collection error: {e}")
                continue
        
        # Stop control
        await interface.send_command("STOP_PID_CONTROL")
        
        return {
            "time": time_data,
            "speed": speed_data,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware run failed: {str(e)}")

@router.post("/run_final_experiment")
async def run_final_experiment(request: FinalExperimentRequest) -> Dict[str, Any]:
    """Run complete experiment with simulation and hardware comparison"""
    try:
        # Run simulation
        sim_request = TestPIDRequest(
            tf=request.tf,
            pid=request.pid,
            setpoint=request.desired_speed
        )
        sim_result = await test_pid(sim_request)
        
        # Run hardware (if available)
        hw_result = None
        try:
            hw_request = {
                "pid": request.pid.dict(),
                "desired_speed": request.desired_speed,
                "duration": request.duration
            }
            hw_result = await run_hardware(hw_request)
        except Exception as e:
            logging.warning(f"Hardware unavailable: {e}")
        
        # Create comparative data
        time_sim = sim_result["time"]
        response_sim = sim_result["response"]
        
        # Create desired speed reference
        desired = [request.desired_speed] * len(time_sim)
        
        result = {
            "time": time_sim,
            "desired": desired,
            "simulated": response_sim,
            "hardware": hw_result["speed"] if hw_result and hw_result["success"] else [0] * len(time_sim),
            "metrics": {
                "simulation": sim_result["metrics"],
                "hardware_available": hw_result is not None and hw_result["success"]
            },
            "success": True
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Final experiment failed: {str(e)}")

# Fallback functions for when control library is not available
async def fallback_step_response(tf_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback step response using numerical integration"""
    try:
        num = tf_data["numerator"]
        den = tf_data["denominator"]
        
        # Simple second-order system approximation
        if len(den) >= 3:
            a = den[0]
            b = den[1] 
            c = den[2]
            k = num[0]
            
            omega_n = np.sqrt(c / a)
            zeta = b / (2 * np.sqrt(a * c))
            
            time = np.linspace(0, 10, 1000)
            response = np.zeros_like(time)
            
            if zeta < 1:
                # Underdamped
                omega_d = omega_n * np.sqrt(1 - zeta**2)
                for i, t in enumerate(time):
                    response[i] = (k / c) * (1 - np.exp(-zeta * omega_n * t) * 
                        (np.cos(omega_d * t) + (zeta * omega_n / omega_d) * np.sin(omega_d * t)))
            else:
                # Overdamped or critically damped
                for i, t in enumerate(time):
                    response[i] = (k / c) * (1 - np.exp(-omega_n * t) * (1 + omega_n * t))
            
            return {
                "time": time.tolist(),
                "response": response.tolist(),
                "metrics": {
                    "rise_time": 0.0,
                    "settling_time": 0.0,
                    "overshoot": 0.0,
                    "peak_time": 0.0
                },
                "success": True
            }
        else:
            raise ValueError("Invalid transfer function")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallback simulation failed: {str(e)}")

async def fallback_pid_simulation(tf_data: Dict[str, Any], pid_params: PIDParams, setpoint: float) -> Dict[str, Any]:
    """Fallback PID simulation using numerical methods"""
    try:
        # Simple numerical PID simulation
        dt = 0.01
        time_span = 10.0
        time = np.arange(0, time_span, dt)
        
        # Plant parameters (simplified)
        num = tf_data["numerator"]
        den = tf_data["denominator"]
        
        # Initialize
        response = np.zeros_like(time)
        error_prev = 0
        integral = 0
        plant_output = 0
        
        for i, t in enumerate(time):
            # Error calculation
            error = setpoint - plant_output
            
            # PID calculation
            proportional = pid_params.Kp * error
            integral += pid_params.Ki * error * dt
            derivative = pid_params.Kd * (error - error_prev) / dt if i > 0 else 0
            
            control_output = proportional + integral + derivative
            
            # Simple plant simulation (first-order approximation)
            if len(den) >= 2:
                tau = den[0] / den[1] if den[1] != 0 else 1.0
                k = num[0] / den[-1] if den[-1] != 0 else 1.0
                plant_output += (k * control_output - plant_output) * dt / tau
            
            response[i] = plant_output
            error_prev = error
        
        return {
            "time": time.tolist(),
            "response": response.tolist(),
            "metrics": {
                "rise_time": 0.0,
                "settling_time": 0.0,
                "overshoot": 0.0,
                "steady_state_error": abs(setpoint - response[-1])
            },
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallback PID simulation failed: {str(e)}")