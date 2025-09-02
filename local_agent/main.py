"""
CtrlHub Local Agent - Desktop Application
Runs on student's computer to handle hardware and complex simulations
"""

import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import tkinter as tk
from tkinter import ttk
import threading
import sys
import webbrowser
import json
import logging
import os

# Add current directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fix imports - use absolute imports instead of relative
from hardware.arduino_interface import ArduinoInterface
from hardware.arduino_programmer import ArduinoProgrammer, program_arduino_automatically
from simulations.simulation_engine import SimulationEngine
from models.dc_motor import DCMotorModel
from endpoints.rotary_pendulum import router as rotary_pendulum_router
from routes.onshape_routes import router as onshape_router

class CtrlHubAgent:
    def __init__(self):
        self.app = FastAPI(title="CtrlHub Local Agent")
        self.setup_cors()
        self.setup_routes()
        
        # Include experiment routers
        self.app.include_router(rotary_pendulum_router)
        self.app.include_router(onshape_router)
        
        self.arduino = ArduinoInterface()
        self.programmer = ArduinoProgrammer()
        try:
            self.simulation_engine = SimulationEngine()
        except Exception as e:
            print(f"Warning: Simulation engine init failed: {e}")
            self.simulation_engine = None
        self.logger = logging.getLogger(__name__)

    def setup_cors(self):
        """Setup CORS for frontend communication"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "CtrlHub Local Agent", 
                "status": "running", 
                "version": "1.0",
                "endpoints": [
                    "/status", "/hardware/connect", "/hardware/disconnect", 
                    "/hardware/scan", "/simulation/run"
                ]
            }
        
        @self.app.get("/status")
        async def status():
            return {
                "agent_status": "running",
                "arduino_connected": self.arduino.is_connected,
                "arduino_port": getattr(self.arduino, 'port', None),
                "available_ports": self.arduino.scan_ports()
            }
        
        @self.app.get("/hardware/scan")
        async def scan_ports():
            ports = self.arduino.scan_ports()
            return {
                "success": True,
                "ports": ports,
                "message": f"Found {len(ports)} potential Arduino ports"
            }
        
        @self.app.post("/hardware/connect")
        @self.app.get("/hardware/connect")
        async def connect_arduino():
            success = await self.arduino.connect()
            return {
                "success": success,
                "message": "Connected to Arduino" if success else "Failed to connect",
                "port": getattr(self.arduino, 'port', None)
            }
        
        @self.app.post("/hardware/disconnect")
        @self.app.get("/hardware/disconnect")
        async def disconnect_arduino():
            await self.arduino.disconnect()
            return {"success": True, "message": "Disconnected from Arduino"}
        
        @self.app.post("/simulation/run")
        async def run_simulation(request: dict):
            """Run complex Python simulations locally"""
            try:
                if self.simulation_engine:
                    result = self.simulation_engine.run_simulation(request)
                    return {"success": True, "data": result}
                else:
                    return {"success": False, "error": "Simulation engine not available"}
            except Exception as e:
                return {"success": False, "error": str(e)}

        @self.app.post("/simulation/dc_motor")
        async def run_dc_motor_test(request: dict):
            """Run DC motor parameter extraction tests or simulations"""
            try:
                test_type = request.get("testType", "coast-down")
                simulation_mode = request.get("simulationMode", False)
                
                if simulation_mode:
                    # Pure simulation using Python control libraries
                    return await self.run_dc_motor_simulation(request)
                else:
                    # Hardware-based testing
                    if test_type == "coast-down":
                        result = await self.arduino.run_coast_down_test()
                        return result
                        
                    elif test_type == "steady-state":
                        pwm_value = request.get("motorSpeed", 150)
                        duration = request.get("duration", 10000) // 1000  # Convert ms to seconds
                        result = await self.arduino.run_steady_state_test(pwm_value, duration)
                        return result
                        
                    elif test_type == "back-emf":
                        pwm_value = request.get("motorSpeed", 200)
                        duration = request.get("duration", 5000) // 1000  # Convert ms to seconds
                        result = await self.arduino.run_back_emf_test(pwm_value, duration)
                        return result
                        
                    else:
                        return {"success": False, "error": f"Unknown test type: {test_type}"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}

        @self.app.get("/arduino/detect")
        async def detect_arduino():
            """Detect available Arduino ports"""
            try:
                ports = self.programmer.get_arduino_ports()
                return {
                    "success": True,
                    "ports": ports,
                    "message": f"Found {len(ports)} Arduino(s)"
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        @self.app.post("/arduino/program")
        async def program_arduino(request: dict = None):
            """Program Arduino with CtrlHub sketch automatically"""
            try:
                sketch_name = "CtrlHub_Parameter_Extraction"
                port = None
                
                if request:
                    sketch_name = request.get("sketch", sketch_name)
                    port = request.get("port", None)
                
                success, message = self.programmer.program_arduino(sketch_name, port)
                
                return {
                    "success": success,
                    "message": message,
                    "sketch": sketch_name
                }
                
            except Exception as e:
                return {"success": False, "error": str(e)}

        @self.app.get("/arduino/setup")
        async def setup_arduino_environment():
            """Setup Arduino CLI environment"""
            try:
                success = self.programmer.setup_arduino_cli()
                return {
                    "success": success,
                    "message": "Arduino CLI setup complete" if success else "Arduino CLI setup failed"
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def run_dc_motor_simulation(self, request: dict):
        """Run DC motor simulation using Python control libraries"""
        import numpy as np
        import time
        
        try:
            test_type = request.get("testType", "coast-down")
            duration = request.get("duration", 5000) / 1000.0  # Convert ms to seconds
            motor_speed = request.get("motorSpeed", 150)
            sample_rate = request.get("sampleRate", 100)
            
            # Sample rate timing
            dt = 1.0 / sample_rate
            time_points = np.arange(0, duration, dt)
            
            # Simulated motor parameters
            R = 2.5  # Resistance (Ohms)
            L = 0.003  # Inductance (H)
            Kt = 0.01  # Torque constant
            Ke = 0.01  # Back-EMF constant
            J = 1e-6  # Moment of inertia
            b = 1e-6  # Viscous friction
            
            simulation_data = []
            
            if test_type == "coast-down":
                # Coast-down simulation - motor decelerating from initial speed
                initial_speed = 300  # RPM
                omega = initial_speed * 2 * np.pi / 60  # Convert to rad/s
                
                for t in time_points:
                    # Simple exponential decay
                    current_omega = omega * np.exp(-b * t / J)
                    current_speed = current_omega * 60 / (2 * np.pi)  # Convert back to RPM
                    current_voltage = 0  # No voltage applied during coast-down
                    current_current = 0  # No current during coast-down
                    
                    simulation_data.append({
                        "time": int(t * 1000),  # Convert to ms
                        "speed": round(current_speed, 2),
                        "voltage": round(current_voltage, 2),
                        "current": round(current_current, 2)
                    })
                    
            elif test_type == "steady-state":
                # Steady-state simulation - motor reaching steady speed
                applied_voltage = motor_speed / 255.0 * 12.0  # Convert PWM to voltage
                steady_speed = (applied_voltage - 0) / Ke  # Steady-state speed
                
                for t in time_points:
                    # First-order response to steady state
                    tau = L / R  # Time constant
                    current_speed = steady_speed * (1 - np.exp(-t / tau)) * 60 / (2 * np.pi)
                    current_voltage = applied_voltage
                    current_current = applied_voltage / R * np.exp(-t / tau)
                    
                    simulation_data.append({
                        "time": int(t * 1000),
                        "speed": round(current_speed, 2),
                        "voltage": round(current_voltage, 2),
                        "current": round(current_current, 2)
                    })
                    
            elif test_type == "open-loop":
                # Open-loop step response
                applied_voltage = motor_speed / 255.0 * 12.0
                steady_speed = applied_voltage / Ke
                
                for t in time_points:
                    tau = L / R
                    current_speed = steady_speed * (1 - np.exp(-t / tau)) * 60 / (2 * np.pi)
                    current_voltage = applied_voltage
                    current_current = applied_voltage / R * np.exp(-t / tau)
                    
                    simulation_data.append({
                        "time": int(t * 1000),
                        "speed": round(current_speed, 2),
                        "voltage": round(current_voltage, 2),
                        "current": round(current_current, 2)
                    })
                    
            elif test_type == "closed-loop":
                # Closed-loop PID control simulation
                target_speed = motor_speed * 60 / (2 * np.pi)  # Target in RPM
                current_speed = 0
                integral_error = 0
                previous_error = 0
                
                # PID gains (can be passed from frontend)
                kp = 0.1
                ki = 0.01
                kd = 0.001
                
                for i, t in enumerate(time_points):
                    error = target_speed - current_speed
                    integral_error += error * dt
                    derivative_error = (error - previous_error) / dt if i > 0 else 0
                    
                    # PID output
                    pid_output = kp * error + ki * integral_error + kd * derivative_error
                    applied_voltage = max(0, min(12, pid_output))  # Clamp to 0-12V
                    
                    # Motor dynamics
                    tau = L / R
                    steady_speed = applied_voltage / Ke
                    current_speed += (steady_speed - current_speed) * dt / tau
                    current_current = applied_voltage / R
                    
                    simulation_data.append({
                        "time": int(t * 1000),
                        "speed": round(current_speed, 2),
                        "voltage": round(applied_voltage, 2),
                        "current": round(current_current, 2)
                    })
                    
                    previous_error = error
            
            return {
                "success": True,
                "data": simulation_data,
                "message": f"Simulated {test_type} test completed"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Simulation failed: {str(e)}"}

    def start_server(self):
        """Start the FastAPI server in a separate thread"""
        def run_server():
            uvicorn.run(self.app, host="127.0.0.1", port=8003, log_level="info")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

    def start_gui(self):
        """Start the desktop GUI"""
        self.gui_root = tk.Tk()
        self.gui_root.title("CtrlHub Control Systems - Local Agent")
        self.gui_root.geometry("500x400")
        
        # Main frame
        main_frame = ttk.Frame(self.gui_root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="CtrlHub Local Agent", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status indicators
        ttk.Label(main_frame, text="Server Status:").grid(row=1, column=0, sticky=tk.W)
        self.server_status = ttk.Label(main_frame, text="Running on localhost:8002", 
                                      foreground="green")
        self.server_status.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(main_frame, text="Arduino Status:").grid(row=2, column=0, sticky=tk.W)
        self.arduino_status = ttk.Label(main_frame, text="Not Connected", 
                                       foreground="red")
        self.arduino_status.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Connect Arduino", 
                  command=self.gui_connect_arduino).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open CtrlHub Web App", 
                  command=lambda: webbrowser.open("http://localhost:3000")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", 
                  command=self.gui_root.quit).pack(side=tk.LEFT, padx=5)
        
        # Log area
        ttk.Label(main_frame, text="Log:").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        self.log_text = tk.Text(main_frame, height=10, width=60)
        self.log_text.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
        # Update status periodically
        self.update_gui_status()
        
        # Start GUI
        self.gui_root.mainloop()

    def gui_connect_arduino(self):
        """GUI Arduino connection handler"""
        success = self.arduino.connect_sync()
        if success:
            self.arduino_status.config(text=f"Connected on {self.arduino.port}", 
                                     foreground="green")
            self.log_message(f"✅ Arduino connected on {self.arduino.port}")
        else:
            self.arduino_status.config(text="Connection Failed", foreground="red")
            self.log_message("❌ Failed to connect to Arduino")

    def update_gui_status(self):
        """Update GUI status periodically"""
        if self.arduino.is_connected:
            self.arduino_status.config(text=f"Connected on {self.arduino.port}", 
                                     foreground="green")
        else:
            self.arduino_status.config(text="Not Connected", foreground="red")
        
        # Schedule next update
        if self.gui_root:
            self.gui_root.after(2000, self.update_gui_status)

    def log_message(self, message):
        """Add message to log area"""
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)

if __name__ == "__main__":
    try:
        print("🎓 Starting CtrlHub Control Systems - Local Agent")
        print("=" * 55)
        
        agent = CtrlHubAgent()
        print("✅ Agent initialized successfully")
        
        # Start the server in a separate thread
        print("🌐 Starting web server on http://localhost:8003")
        agent.start_server()
        
        # Show GUI (blocking)
        print("🖥️  Opening agent control panel...")
        agent.start_gui()
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()