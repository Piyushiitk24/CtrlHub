"""
VirtualLab Local Agent - Desktop Application
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

class VirtualLabAgent:
    def __init__(self):
        self.app = FastAPI(title="VirtualLab Local Agent")
        self.setup_cors()
        self.setup_routes()
        self.arduino = None
        self.simulation_engine = None
        
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
            return {"status": "VirtualLab Agent Running", "version": "1.0.0"}
            
        @self.app.post("/hardware/connect")
        async def connect_arduino():
            # Direct USB connection to student's Arduino
            return await self.connect_local_arduino()
            
        @self.app.post("/simulation/run")
        async def run_simulation(model_data: dict):
            # Run complex Python simulations locally
            return await self.run_local_simulation(model_data)
    
    def start_gui(self):
        """Simple GUI for the desktop agent"""
        root = tk.Tk()
        root.title("VirtualLab Control Systems - Local Agent")
        root.geometry("400x300")
        
        # Status display
        ttk.Label(root, text="VirtualLab Agent Status", font=("Arial", 14)).pack(pady=10)
        
        status_label = ttk.Label(root, text="🟢 Agent Running on http://localhost:8001")
        status_label.pack(pady=5)
        
        # Open web interface button
        def open_web():
            webbrowser.open("http://localhost:3000")
            
        ttk.Button(root, text="Open VirtualLab Interface", command=open_web).pack(pady=10)
        
        # Arduino connection status
        arduino_frame = ttk.LabelFrame(root, text="Hardware Status")
        arduino_frame.pack(pady=10, padx=20, fill="x")
        
        self.arduino_status = ttk.Label(arduino_frame, text="⚫ Arduino: Not Connected")
        self.arduino_status.pack(pady=5)
        
        ttk.Button(arduino_frame, text="Scan for Arduino", 
                  command=self.scan_arduino).pack(pady=5)
        
        root.mainloop()
    
    def scan_arduino(self):
        """Scan for connected Arduino boards"""
        # Implementation for Arduino detection
        pass
    
    def start_server(self):
        """Start the FastAPI server in a separate thread"""
        def run_server():
            uvicorn.run(self.app, host="127.0.0.1", port=8001, log_level="info")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

if __name__ == "__main__":
    agent = VirtualLabAgent()
    agent.start_server()
    agent.start_gui()  # Shows GUI for easy management