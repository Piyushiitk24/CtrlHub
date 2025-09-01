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
from simulations.simulation_engine import SimulationEngine
from models.dc_motor import DCMotorModel

class CtrlHubAgent:
    def __init__(self):
        self.app = FastAPI(title="CtrlHub Local Agent")
        self.setup_cors()
        self.setup_routes()
        self.arduino = ArduinoInterface()
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
            """Run DC motor parameter extraction tests"""
            try:
                test_type = request.get("testType", "coast-down")
                
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