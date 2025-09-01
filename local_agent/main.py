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

# Import our hardware and simulation modules
from .hardware.arduino_interface import ArduinoInterface
from .simulations.simulation_engine import SimulationEngine
from .models.dc_motor import DCMotorModel

class CtrlHubAgent:
    def __init__(self):
        self.app = FastAPI(title="CtrlHub Local Agent")
        self.setup_cors()
        self.setup_routes()
        self.arduino = ArduinoInterface()
        self.simulation_engine = SimulationEngine()
        self.dc_motor_model = DCMotorModel()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow from any origin for local use
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        @self.app.get("/")
        async def root():
            return {"status": "CtrlHub Agent Running", "version": "1.0.0"}
            
        @self.app.get("/health")
        async def health():
            return {
                "agent_status": "running",
                "arduino_connected": self.arduino.is_connected(),
                "simulation_engine": "ready"
            }
            
        @self.app.post("/hardware/connect")
        async def connect_arduino():
            """Direct USB connection to student's Arduino"""
            try:
                result = await self.connect_local_arduino()
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
            
        @self.app.post("/hardware/disconnect")
        async def disconnect_arduino():
            """Disconnect from Arduino"""
            try:
                self.arduino.disconnect()
                return {"success": True, "message": "Arduino disconnected"}
            except Exception as e:
                return {"success": False, "error": str(e)}
                
        @self.app.get("/hardware/ports")
        async def scan_ports():
            """Scan for available serial ports"""
            try:
                ports = self.arduino.scan_ports()
                return {"success": True, "ports": ports}
            except Exception as e:
                return {"success": False, "error": str(e)}
            
        @self.app.post("/simulation/run")
        async def run_simulation(request: dict):
            """Run complex Python simulations locally"""
            try:
                result = await self.run_local_simulation(request)
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
                
        @self.app.post("/simulation/dc_motor")
        async def simulate_dc_motor(request: dict):
            """Run DC motor simulation with parameters"""
            try:
                result = self.dc_motor_model.simulate(request)
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
                
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time communication"""
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_text()
                    # Handle real-time data from frontend
                    response = await self.handle_websocket_data(json.loads(data))
                    await websocket.send_text(json.dumps(response))
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
                
    async def connect_local_arduino(self):
        """Connect to local Arduino"""
        return self.arduino.connect()
        
    async def run_local_simulation(self, model_data):
        """Run simulation using local Python engine"""
        return self.simulation_engine.run(model_data)
        
    async def handle_websocket_data(self, data):
        """Handle WebSocket data for real-time operations"""
        if data.get("type") == "arduino_command":
            return self.arduino.send_command(data.get("command"))
        elif data.get("type") == "simulation_step":
            return self.simulation_engine.step(data.get("params"))
        else:
            return {"error": "Unknown command type"}
    
    def start_gui(self):
        """Simple GUI for the desktop agent"""
        root = tk.Tk()
        root.title("CtrlHub Control Systems - Local Agent")
        root.geometry("500x400")
        
        # Status display
        ttk.Label(root, text="CtrlHub Agent Status", font=("Arial", 16, "bold")).pack(pady=10)
        
        status_label = ttk.Label(root, text="🟢 Agent Running on http://localhost:8001", 
                                font=("Arial", 12))
        status_label.pack(pady=5)
        
        # Open web interface button
        def open_web():
            webbrowser.open("http://localhost:3000")
            
        ttk.Button(root, text="Open CtrlHub Interface", command=open_web, 
                  style="Accent.TButton").pack(pady=10)
        
        # Arduino connection status
        hardware_frame = ttk.LabelFrame(root, text="Hardware Status", padding=10)
        hardware_frame.pack(pady=10, padx=20, fill="x")
        
        self.arduino_status = ttk.Label(hardware_frame, text="⚫ Arduino: Not Connected")
        self.arduino_status.pack(pady=5)
        
        ttk.Button(hardware_frame, text="Scan for Arduino", 
                  command=self.scan_arduino).pack(pady=5)
        
        # Simulation status
        sim_frame = ttk.LabelFrame(root, text="Simulation Engine", padding=10)
        sim_frame.pack(pady=10, padx=20, fill="x")
        
        ttk.Label(sim_frame, text="✅ Python Simulation Engine Ready").pack(pady=5)
        ttk.Label(sim_frame, text="✅ DC Motor Models Loaded").pack(pady=2)
        ttk.Label(sim_frame, text="✅ Control Systems Library Ready").pack(pady=2)
        
        # Logs frame
        log_frame = ttk.LabelFrame(root, text="Activity Log", padding=10)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.log_text = tk.Text(log_frame, height=6, width=50)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.log("CtrlHub Agent started successfully")
        self.log("Waiting for connections from web frontend...")
        
        root.mainloop()
    
    def log(self, message):
        """Add message to GUI log"""
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
    
    def scan_arduino(self):
        """Scan for connected Arduino boards"""
        try:
            ports = self.arduino.scan_ports()
            if ports:
                self.arduino_status.config(text=f"🟡 Found Arduino on {ports[0]}")
                self.log(f"Found Arduino ports: {ports}")
                # Attempt auto-connection
                if self.arduino.connect():
                    self.arduino_status.config(text="🟢 Arduino: Connected")
                    self.log("Arduino connected successfully")
            else:
                self.arduino_status.config(text="🔴 No Arduino Found")
                self.log("No Arduino ports found")
        except Exception as e:
            self.arduino_status.config(text="🔴 Arduino: Error")
            self.log(f"Arduino scan error: {e}")
    
    def start_server(self):
        """Start the FastAPI server in a separate thread"""
        def run_server():
            uvicorn.run(self.app, host="127.0.0.1", port=8001, log_level="info")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

if __name__ == "__main__":
    agent = CtrlHubAgent()
    agent.start_server()
    agent.start_gui()  # Shows GUI for easy management