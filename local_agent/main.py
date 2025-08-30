"""
CtrlHub Desktop Agent
Main application with PyQt5 GUI and FastAPI server for hardware communication
"""

import sys
import asyncio
import threading
import webbrowser
import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QPushButton, QLabel, QTextEdit, QSystemTrayIcon, 
                           QMenu, QAction, QMessageBox, QGroupBox, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QIcon, QFont, QPixmap

from hardware.arduino_interface import ArduinoInterface
from models.dc_motor import DCMotorModel, MotorParameters
from simulations.simulation_engine import SimulationEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VirtualLabServer:
    """FastAPI server for local agent communication"""
    
    def __init__(self, gui_callback=None):
        self.app = FastAPI(
            title="VirtualLab Local Agent",
            description="Hardware interface and simulation engine",
            version="2.0.0"
        )
        self.gui_callback = gui_callback
        self.arduino = ArduinoInterface()
        self.simulation_engine = SimulationEngine()
        self.setup_middleware()
        self.setup_routes()
        
    def setup_middleware(self):
        """Configure CORS for browser communication"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Define API endpoints"""
        
        @self.app.get("/")
        async def root():
            return {
                "service": "VirtualLab Local Agent",
                "version": "2.0.0",
                "status": "running",
                "arduino_connected": self.arduino.is_connected
            }
        
        @self.app.post("/hardware/scan")
        async def scan_arduino():
            """Scan for available Arduino ports"""
            try:
                ports = self.arduino.scan_ports()
                return {"available_ports": ports}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/hardware/connect")
        async def connect_arduino(port: str = None):
            """Connect to Arduino"""
            try:
                success = await self.arduino.connect(port)
                if success and self.gui_callback:
                    self.gui_callback("arduino_connected", self.arduino.port)
                return {
                    "success": success,
                    "port": self.arduino.port,
                    "message": "Connected successfully" if success else "Connection failed"
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/hardware/disconnect")
        async def disconnect_arduino():
            """Disconnect from Arduino"""
            await self.arduino.disconnect()
            if self.gui_callback:
                self.gui_callback("arduino_disconnected", None)
            return {"success": True, "message": "Disconnected"}
        
        @self.app.post("/hardware/control")
        async def control_motor(command: dict):
            """Send motor control command"""
            try:
                if not self.arduino.is_connected:
                    raise HTTPException(status_code=400, detail="Arduino not connected")
                
                result = await self.arduino.send_motor_command(
                    command.get("speed", 0),
                    command.get("direction", "STOP")
                )
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/simulation/step_response")
        async def simulate_step_response(params: dict):
            """Run step response simulation"""
            try:
                result = await self.simulation_engine.step_response(
                    voltage=params.get("voltage", 12.0),
                    duration=params.get("duration", 2.0),
                    motor_params=params.get("motor_params")
                )
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/simulation/coast_down")
        async def simulate_coast_down(params: dict):
            """Run coast-down test simulation"""
            try:
                result = await self.simulation_engine.coast_down_test(
                    initial_speed=params.get("initial_speed", 100.0),
                    duration=params.get("duration", 5.0),
                    motor_params=params.get("motor_params")
                )
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/simulation/transfer_function")
        async def get_transfer_function(motor_params: dict = None):
            """Get motor transfer function"""
            try:
                result = await self.simulation_engine.get_transfer_function(motor_params)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

class ServerThread(QThread):
    """Thread to run FastAPI server"""
    
    def __init__(self, server, port=8001):
        super().__init__()
        self.server = server
        self.port = port
        
    def run(self):
        """Run the server in this thread"""
        try:
            uvicorn.run(self.server.app, host="127.0.0.1", port=self.port, log_level="info")
        except Exception as e:
            logger.error(f"Server error: {e}")

class VirtualLabGUI(QMainWindow):
    """Main GUI application for VirtualLab Local Agent"""
    
    def __init__(self):
        super().__init__()
        self.server = VirtualLabServer(gui_callback=self.handle_server_callback)
        self.server_thread = None
        self.system_tray = None
        self.init_ui()
        self.start_server()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("CtrlHub Desktop Agent")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("🎛️ VirtualLab Control Systems")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Status section
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        
        self.server_status_label = QLabel("🟢 Local Agent: Running on http://127.0.0.1:8001")
        self.arduino_status_label = QLabel("⚫ Arduino: Not Connected")
        self.browser_status_label = QLabel("🌐 Web Interface: Ready")
        
        status_layout.addWidget(self.server_status_label)
        status_layout.addWidget(self.arduino_status_label)
        status_layout.addWidget(self.browser_status_label)
        
        layout.addWidget(status_group)
        
        # Control section
        control_group = QGroupBox("Quick Actions")
        control_layout = QVBoxLayout(control_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.open_web_button = QPushButton("🌐 Open Web Interface")
        self.open_web_button.clicked.connect(self.open_web_interface)
        
        self.scan_arduino_button = QPushButton("🔍 Scan Arduino")
        self.scan_arduino_button.clicked.connect(self.scan_arduino)
        
        self.connect_arduino_button = QPushButton("🔌 Connect Arduino")
        self.connect_arduino_button.clicked.connect(self.connect_arduino)
        
        button_layout.addWidget(self.open_web_button)
        button_layout.addWidget(self.scan_arduino_button)
        button_layout.addWidget(self.connect_arduino_button)
        
        control_layout.addLayout(button_layout)
        layout.addWidget(control_group)
        
        # Log section
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Setup system tray
        self.setup_system_tray()
        
        # Add initial log message
        self.add_log("🚀 VirtualLab Local Agent started successfully")
        
    def setup_system_tray(self):
        """Setup system tray icon"""
        try:
            self.system_tray = QSystemTrayIcon(self)
            
            # Create tray menu
            tray_menu = QMenu()
            
            show_action = QAction("Show VirtualLab", self)
            show_action.triggered.connect(self.show)
            
            open_web_action = QAction("Open Web Interface", self)
            open_web_action.triggered.connect(self.open_web_interface)
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.quit_application)
            
            tray_menu.addAction(show_action)
            tray_menu.addAction(open_web_action)
            tray_menu.addSeparator()
            tray_menu.addAction(quit_action)
            
            self.system_tray.setContextMenu(tray_menu)
            self.system_tray.show()
            
        except Exception as e:
            logger.warning(f"System tray not available: {e}")
    
    def start_server(self):
        """Start the FastAPI server"""
        try:
            self.server_thread = ServerThread(self.server, port=8001)
            self.server_thread.start()
            self.add_log("🌐 Local server started on http://127.0.0.1:8001")
        except Exception as e:
            self.add_log(f"❌ Server start failed: {e}")
    
    def open_web_interface(self):
        """Open the web interface in default browser"""
        try:
            webbrowser.open("http://localhost:3000")
            self.add_log("🌐 Opened web interface in browser")
        except Exception as e:
            self.add_log(f"❌ Failed to open web interface: {e}")
    
    def scan_arduino(self):
        """Scan for available Arduino ports"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            ports = self.server.arduino.scan_ports()
            
            self.progress_bar.setVisible(False)
            
            if ports:
                self.add_log(f"🔍 Found Arduino ports: {', '.join(ports)}")
            else:
                self.add_log("⚠️ No Arduino ports found")
                
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.add_log(f"❌ Arduino scan failed: {e}")
    
    def connect_arduino(self):
        """Connect to Arduino"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            # Run connection in a separate thread (simplified for demo)
            # In production, use QThread properly
            import threading
            
            def connect_thread():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    success = loop.run_until_complete(self.server.arduino.connect())
                    
                    if success:
                        self.handle_server_callback("arduino_connected", self.server.arduino.port)
                    else:
                        self.add_log("❌ Arduino connection failed")
                        
                except Exception as e:
                    self.add_log(f"❌ Arduino connection error: {e}")
                finally:
                    self.progress_bar.setVisible(False)
            
            threading.Thread(target=connect_thread, daemon=True).start()
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.add_log(f"❌ Arduino connection failed: {e}")
    
    def handle_server_callback(self, event, data):
        """Handle callbacks from the server"""
        if event == "arduino_connected":
            self.arduino_status_label.setText(f"🟢 Arduino: Connected on {data}")
            self.add_log(f"🔌 Arduino connected on {data}")
        elif event == "arduino_disconnected":
            self.arduino_status_label.setText("⚫ Arduino: Not Connected")
            self.add_log("🔌 Arduino disconnected")
    
    def add_log(self, message):
        """Add message to the log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        logger.info(message)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.system_tray and self.system_tray.isVisible():
            QMessageBox.information(
                self, 
                "VirtualLab",
                "Application was minimized to tray. Click the tray icon to show the window again."
            )
            self.hide()
            event.ignore()
        else:
            self.quit_application()
    
    def quit_application(self):
        """Quit the application"""
        try:
            # Cleanup
            if self.server.arduino.is_connected:
                asyncio.run(self.server.arduino.disconnect())
            
            if self.server_thread and self.server_thread.isRunning():
                self.server_thread.terminate()
                self.server_thread.wait()
            
            QApplication.quit()
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            QApplication.quit()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when window is closed
    
    # Set application properties
    app.setApplicationName("VirtualLab Control Systems")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("VirtualLab Education")
    
    # Create and show main window
    window = VirtualLabGUI()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()