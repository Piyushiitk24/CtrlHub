#!/usr/bin/env python3
"""
CtrlHub Development Server Launcher
Cross-platform Python launcher for development environment
"""

import os
import sys
import subprocess
import time
import signal
import platform
import threading
from pathlib import Path

class CtrlHubDevelopmentLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.local_agent_process = None
        self.frontend_process = None
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n🛑 Shutting down CtrlHub development servers...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Stop all running processes"""
        self.running = False
        
        if self.local_agent_process:
            print("   Stopping local agent...")
            self.local_agent_process.terminate()
            self.local_agent_process.wait()
        
        if self.frontend_process:
            print("   Stopping React dev server...")
            self.frontend_process.terminate()
            self.frontend_process.wait()
        
        # Kill any remaining processes on our ports
        self.kill_port_processes()
        print("✅ All servers stopped cleanly!")
    
    def kill_port_processes(self):
        """Kill processes on ports 8003 and 3000"""
        try:
            if platform.system() == "Windows":
                # Windows
                subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                             stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.run(["taskkill", "/F", "/IM", "node.exe"], 
                             stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            else:
                # Unix-like systems
                subprocess.run(["pkill", "-f", "python main.py"], 
                             stderr=subprocess.DEVNULL)
                subprocess.run(["pkill", "-f", "npm start"], 
                             stderr=subprocess.DEVNULL)
        except:
            pass
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        print("🔍 Checking dependencies...")
        
        # Check Python
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Node.js not found")
                return False
        except FileNotFoundError:
            print("❌ Node.js not found")
            return False
        
        print("✅ Dependencies check passed")
        return True
    
    def setup_python_env(self):
        """Setup Python virtual environment"""
        print("🐍 Setting up Python environment...")
        
        venv_path = self.project_root / "ctrlhub_env"
        
        # Create virtual environment if it doesn't exist
        if not venv_path.exists():
            print("   Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)])
        
        # Determine the Python executable in the virtual environment
        if platform.system() == "Windows":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        # Install requirements
        print("   Installing Python dependencies...")
        requirements_path = self.project_root / "local_agent" / "requirements.txt"
        subprocess.run([str(python_exe), "-m", "pip", "install", "-q", 
                       "-r", str(requirements_path)])
        
        print("✅ Python environment ready")
        return python_exe
    
    def setup_node_env(self):
        """Setup Node.js environment"""
        print("📦 Setting up Node.js environment...")
        
        frontend_path = self.project_root / "frontend"
        node_modules_path = frontend_path / "node_modules"
        
        # Install Node.js dependencies if needed
        if not node_modules_path.exists():
            print("   Installing Node.js dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_path)
        
        print("✅ Node.js environment ready")
    
    def start_local_agent(self, python_exe):
        """Start the local agent"""
        print("🖥️  Starting CtrlHub Local Agent...")
        
        local_agent_path = self.project_root / "local_agent"
        main_py = local_agent_path / "main.py"
        
        self.local_agent_process = subprocess.Popen(
            [str(python_exe), str(main_py)],
            cwd=local_agent_path
        )
        
        # Wait for local agent to start
        print("   Waiting for local agent to initialize...")
        time.sleep(5)
        
        # Check if it's running
        if self.local_agent_process.poll() is not None:
            print("❌ Local agent failed to start")
            return False
        
        print("✅ Local agent running on http://localhost:8003")
        return True
    
    def start_frontend(self):
        """Start the React development server"""
        print("🌐 Starting React Development Server...")
        
        frontend_path = self.project_root / "frontend"
        
        self.frontend_process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_path
        )
        
        # Wait for React dev server to start
        print("   Waiting for React server to initialize...")
        time.sleep(10)
        
        # Check if it's running
        if self.frontend_process.poll() is not None:
            print("❌ React dev server failed to start")
            return False
        
        print("✅ React dev server running on http://localhost:3000")
        return True
    
    def open_browser(self):
        """Open the browser"""
        print("🌍 Opening CtrlHub in browser...")
        
        url = "http://localhost:3000/components/dc-motor/parameter-extraction"
        
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", url])
            elif platform.system() == "Windows":  # Windows
                subprocess.run(["start", url], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", url])
        except:
            print(f"   Please open: {url}")
    
    def monitor_servers(self):
        """Monitor the running servers"""
        print("\n🎉 CtrlHub Development Environment Ready!")
        print("=" * 46)
        print("✅ Local Agent:     http://localhost:8003")
        print("✅ Web Interface:   http://localhost:3000")
        print("✅ Parameter Page:  http://localhost:3000/components/dc-motor/parameter-extraction")
        print("\n💡 Development Tips:")
        print("   • Both servers will auto-reload on file changes")
        print("   • Press Ctrl+C to stop all servers")
        print("   • Check terminal output for any errors")
        print("\n📊 Monitoring servers... (Press Ctrl+C to stop)")
        
        while self.running:
            time.sleep(5)
            
            # Check if processes are still running
            if self.local_agent_process and self.local_agent_process.poll() is not None:
                print("❌ Local agent stopped unexpectedly!")
                break
            
            if self.frontend_process and self.frontend_process.poll() is not None:
                print("❌ React dev server stopped unexpectedly!")
                break
    
    def run(self):
        """Main execution flow"""
        print("🎛️  Starting CtrlHub Development Environment...")
        print("=" * 46)
        
        try:
            # Clean up any existing processes
            print("🧹 Cleaning up existing processes...")
            self.kill_port_processes()
            time.sleep(2)
            
            # Check dependencies
            if not self.check_dependencies():
                return False
            
            # Setup environments
            python_exe = self.setup_python_env()
            self.setup_node_env()
            
            # Start services
            if not self.start_local_agent(python_exe):
                return False
            
            if not self.start_frontend():
                return False
            
            # Open browser
            time.sleep(2)
            self.open_browser()
            
            # Monitor servers
            self.monitor_servers()
            
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
        
        return True

if __name__ == "__main__":
    launcher = CtrlHubDevelopmentLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)
