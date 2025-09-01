"""
Arduino Programmer - Automatic sketch upload without Arduino IDE
Handles Arduino sketch compilation and uploading using Python
"""

import os
import subprocess
import platform
import shutil
import tempfile
import json
from pathlib import Path
from typing import Optional, Tuple, List
import requests
import zipfile

class ArduinoProgrammer:
    def __init__(self):
        self.arduino_cli_path = None
        self.board_fqbn = "arduino:avr:mega"  # Arduino Mega 2560
        self.programmer = "wiring"
        self.sketch_dir = Path(__file__).parent.parent / "arduino_sketches"
        
    def check_arduino_cli(self) -> bool:
        """Check if Arduino CLI is installed and accessible"""
        try:
            result = subprocess.run(['arduino-cli', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def install_arduino_cli(self) -> bool:
        """Install Arduino CLI if not present"""
        try:
            print("📦 Installing Arduino CLI...")
            
            # Determine platform and download appropriate binary
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            if system == "darwin":  # macOS
                if "arm" in machine or "aarch64" in machine:
                    url = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_macOS_ARM64.tar.gz"
                else:
                    url = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_macOS_64bit.tar.gz"
            elif system == "linux":
                url = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz"
            elif system == "windows":
                url = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip"
            else:
                print(f"❌ Unsupported platform: {system}")
                return False
            
            # Download and extract
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                download_path = temp_path / "arduino-cli.archive"
                
                print(f"⬇️ Downloading from {url}")
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with open(download_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract based on file type
                if url.endswith('.zip'):
                    with zipfile.ZipFile(download_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_path)
                else:
                    subprocess.run(['tar', '-xzf', str(download_path), '-C', str(temp_path)], 
                                 check=True)
                
                # Find and move the executable
                cli_executable = temp_path / "arduino-cli"
                if system == "windows":
                    cli_executable = temp_path / "arduino-cli.exe"
                
                # Create local bin directory
                local_bin = Path.home() / ".local" / "bin"
                local_bin.mkdir(parents=True, exist_ok=True)
                
                target_path = local_bin / cli_executable.name
                shutil.copy2(cli_executable, target_path)
                target_path.chmod(0o755)
                
                self.arduino_cli_path = str(target_path)
                print(f"✅ Arduino CLI installed to {target_path}")
                
                # Add to PATH if not already there
                self._add_to_path(str(local_bin))
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to install Arduino CLI: {e}")
            return False
    
    def _add_to_path(self, directory: str):
        """Add directory to PATH if not already present"""
        current_path = os.environ.get('PATH', '')
        if directory not in current_path.split(os.pathsep):
            # For current session
            os.environ['PATH'] = f"{directory}{os.pathsep}{current_path}"
            
            # Suggest permanent addition
            shell = os.environ.get('SHELL', '/bin/bash')
            if 'zsh' in shell:
                profile_file = Path.home() / ".zshrc"
            else:
                profile_file = Path.home() / ".bashrc"
            
            print(f"💡 To permanently add Arduino CLI to PATH, add this line to {profile_file}:")
            print(f"export PATH=\"{directory}:$PATH\"")
    
    def setup_arduino_cli(self) -> bool:
        """Setup Arduino CLI with required cores and libraries"""
        try:
            # Check if Arduino CLI is available
            if not self.check_arduino_cli():
                if not self.install_arduino_cli():
                    return False
            
            print("🔧 Setting up Arduino CLI...")
            
            # Update core index
            subprocess.run(['arduino-cli', 'core', 'update-index'], 
                          check=True, capture_output=True)
            
            # Install Arduino AVR core for Mega
            subprocess.run(['arduino-cli', 'core', 'install', 'arduino:avr'], 
                          check=True, capture_output=True)
            
            print("✅ Arduino CLI setup complete")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Arduino CLI setup failed: {e}")
            return False
    
    def get_arduino_ports(self) -> List[str]:
        """Get list of available Arduino ports"""
        try:
            result = subprocess.run(['arduino-cli', 'board', 'list', '--format', 'json'], 
                                  capture_output=True, text=True, check=True)
            
            boards = json.loads(result.stdout)
            ports = []
            
            for board in boards:
                if board.get('matching_boards'):
                    for matching_board in board['matching_boards']:
                        if 'mega' in matching_board.get('name', '').lower():
                            ports.append(board['address'])
            
            return ports
            
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            # Fallback to serial port detection
            import serial.tools.list_ports
            ports = []
            for port in serial.tools.list_ports.comports():
                if 'arduino' in port.description.lower() or 'mega' in port.description.lower():
                    ports.append(port.device)
            return ports
    
    def compile_sketch(self, sketch_name: str) -> bool:
        """Compile Arduino sketch"""
        try:
            sketch_path = self.sketch_dir / f"{sketch_name}.ino"
            if not sketch_path.exists():
                print(f"❌ Sketch not found: {sketch_path}")
                return False
            
            print(f"🔨 Compiling {sketch_name}...")
            
            result = subprocess.run([
                'arduino-cli', 'compile',
                '--fqbn', self.board_fqbn,
                str(sketch_path.parent)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Compilation successful")
                return True
            else:
                print(f"❌ Compilation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Compilation timed out")
            return False
        except Exception as e:
            print(f"❌ Compilation error: {e}")
            return False
    
    def upload_sketch(self, sketch_name: str, port: str) -> bool:
        """Upload compiled sketch to Arduino"""
        try:
            sketch_path = self.sketch_dir / f"{sketch_name}.ino"
            if not sketch_path.exists():
                print(f"❌ Sketch not found: {sketch_path}")
                return False
            
            print(f"📤 Uploading {sketch_name} to {port}...")
            
            result = subprocess.run([
                'arduino-cli', 'upload',
                '--fqbn', self.board_fqbn,
                '--port', port,
                '--input-dir', str(sketch_path.parent)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Upload successful")
                return True
            else:
                print(f"❌ Upload failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Upload timed out")
            return False
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def program_arduino(self, sketch_name: str = "CtrlHub_Parameter_Extraction", 
                       port: Optional[str] = None) -> Tuple[bool, str]:
        """Complete programming workflow: setup, compile, and upload"""
        try:
            # Setup Arduino CLI if needed
            if not self.setup_arduino_cli():
                return False, "Failed to setup Arduino CLI"
            
            # Auto-detect port if not provided
            if port is None:
                ports = self.get_arduino_ports()
                if not ports:
                    return False, "No Arduino found. Please connect your Arduino Mega."
                port = ports[0]  # Use first available port
                print(f"🔍 Auto-detected Arduino on port: {port}")
            
            # Compile sketch
            if not self.compile_sketch(sketch_name):
                return False, f"Failed to compile sketch: {sketch_name}"
            
            # Upload sketch
            if not self.upload_sketch(sketch_name, port):
                return False, f"Failed to upload sketch to {port}"
            
            return True, f"Successfully programmed Arduino on {port}"
            
        except Exception as e:
            return False, f"Programming failed: {str(e)}"

# Convenience function for easy access
def program_arduino_automatically(sketch_name: str = "CtrlHub_Parameter_Extraction", 
                                port: Optional[str] = None) -> Tuple[bool, str]:
    """Program Arduino with CtrlHub sketch automatically"""
    programmer = ArduinoProgrammer()
    return programmer.program_arduino(sketch_name, port)

if __name__ == "__main__":
    # Test the programmer
    print("🔧 Testing Arduino Programmer...")
    success, message = program_arduino_automatically()
    print(f"Result: {message}")
