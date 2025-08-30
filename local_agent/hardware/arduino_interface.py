"""
Hardware Interface Module
Professional Arduino communication for VirtualLab Control Systems
"""

import serial
import serial.tools.list_ports
import asyncio
import json
import time
import logging
from typing import List, Optional, Dict, Any, Callable

logger = logging.getLogger(__name__)

class ArduinoInterface:
    """
    Professional Arduino communication interface
    Handles USB serial communication with robust error handling
    """
    
    def __init__(self, baudrate: int = 9600, timeout: float = 2.0):
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection: Optional[serial.Serial] = None
        self.port: Optional[str] = None
        self.is_connected = False
        self.callbacks: Dict[str, Callable] = {}
        self.running = False
        self._read_task = None
        
    def scan_ports(self) -> List[str]:
        """
        Scan for available Arduino ports
        Returns list of potential Arduino port names
        """
        arduino_ports = []
        
        try:
            ports = serial.tools.list_ports.comports()
            
            for port in ports:
                # Check for common Arduino identifiers
                port_desc = port.description.lower()
                port_hwid = port.hwid.lower() if port.hwid else ""
                
                arduino_indicators = [
                    'arduino', 'ch340', 'ch341', 'cp210', 'ftdi', 
                    'usb serial', 'usb2.0-serial'
                ]
                
                if any(indicator in port_desc or indicator in port_hwid 
                       for indicator in arduino_indicators):
                    arduino_ports.append(port.device)
                    logger.info(f"Found potential Arduino: {port.device} - {port.description}")
            
            # Add common Arduino ports if not found
            if not arduino_ports:
                common_ports = [
                    '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1',  # Linux
                    '/dev/cu.usbmodem*', '/dev/cu.usbserial*',  # macOS
                    'COM3', 'COM4', 'COM5', 'COM6'  # Windows
                ]
                
                for port in common_ports:
                    if '*' not in port:  # Skip wildcard entries for now
                        arduino_ports.append(port)
        
        except Exception as e:
            logger.error(f"Port scanning failed: {e}")
        
        return arduino_ports
    
    async def connect(self, port: Optional[str] = None) -> bool:
        """
        Connect to Arduino on specified port or auto-detect
        """
        try:
            # If no port specified, scan for available ports
            if not port:
                available_ports = self.scan_ports()
                if not available_ports:
                    logger.error("No Arduino ports found")
                    return False
                port = available_ports[0]  # Use first available port
            
            # Attempt connection
            logger.info(f"Attempting to connect to Arduino on {port}")
            
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout
            )
            
            # Wait for Arduino to initialize
            await asyncio.sleep(2.0)
            
            # Send handshake command
            handshake_success = await self._send_handshake()
            
            if handshake_success:
                self.port = port
                self.is_connected = True
                logger.info(f"Successfully connected to Arduino on {port}")
                
                # Start reading task
                self._start_reading_task()
                return True
            else:
                self.serial_connection.close()
                self.serial_connection = None
                logger.error("Arduino handshake failed")
                return False
                
        except serial.SerialException as e:
            logger.error(f"Serial connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def _send_handshake(self) -> bool:
        """
        Send handshake command to verify Arduino communication
        """
        try:
            # Send handshake command
            command = "HANDSHAKE\\n"
            self.serial_connection.write(command.encode())
            self.serial_connection.flush()
            
            # Wait for response
            start_time = time.time()
            while (time.time() - start_time) < self.timeout:
                if self.serial_connection.in_waiting > 0:
                    response = self.serial_connection.readline().decode().strip()
                    if "OK" in response or "READY" in response:
                        return True
                
                await asyncio.sleep(0.1)
            
            return False
            
        except Exception as e:
            logger.error(f"Handshake failed: {e}")
            return False
    
    def _start_reading_task(self):
        """Start the continuous reading task"""
        if not self._read_task:
            self.running = True
            self._read_task = asyncio.create_task(self._continuous_read())
    
    async def _continuous_read(self):
        """Continuously read data from Arduino"""
        while self.running and self.is_connected:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode().strip()
                    if line:
                        await self._process_incoming_data(line)
                
                await asyncio.sleep(0.01)  # 100Hz reading rate
                
            except Exception as e:
                logger.error(f"Reading error: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_incoming_data(self, data: str):
        """Process incoming data from Arduino"""
        try:
            # Parse different data formats
            if data.startswith("ENCODER:"):
                encoder_data = self._parse_encoder_data(data)
                await self._trigger_callback("encoder", encoder_data)
                
            elif data.startswith("MOTOR:"):
                motor_data = self._parse_motor_data(data)
                await self._trigger_callback("motor", motor_data)
                
            elif data.startswith("STATUS:"):
                status_data = {"message": data.replace("STATUS:", ""), "timestamp": time.time()}
                await self._trigger_callback("status", status_data)
                
            elif data.startswith("ERROR:"):
                error_data = {"error": data.replace("ERROR:", ""), "timestamp": time.time()}
                await self._trigger_callback("error", error_data)
                
        except Exception as e:
            logger.error(f"Data processing error: {e}")
    
    def _parse_encoder_data(self, data: str) -> Dict[str, Any]:
        """Parse encoder data: ENCODER:position,velocity,timestamp"""
        try:
            values = data.replace("ENCODER:", "").split(",")
            return {
                "position": int(values[0]) if len(values) > 0 else 0,
                "velocity": float(values[1]) if len(values) > 1 else 0.0,
                "arduino_timestamp": int(values[2]) if len(values) > 2 else 0,
                "system_timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Encoder data parsing error: {e}")
            return {"position": 0, "velocity": 0.0, "system_timestamp": time.time()}
    
    def _parse_motor_data(self, data: str) -> Dict[str, Any]:
        """Parse motor data: MOTOR:speed,direction,current"""
        try:
            values = data.replace("MOTOR:", "").split(",")
            return {
                "speed": int(values[0]) if len(values) > 0 else 0,
                "direction": values[1] if len(values) > 1 else "STOP",
                "current": float(values[2]) if len(values) > 2 else 0.0,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Motor data parsing error: {e}")
            return {"speed": 0, "direction": "STOP", "current": 0.0, "timestamp": time.time()}
    
    async def _trigger_callback(self, data_type: str, data: Dict[str, Any]):
        """Trigger registered callbacks"""
        if data_type in self.callbacks:
            try:
                callback = self.callbacks[data_type]
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Callback error for {data_type}: {e}")
    
    def register_callback(self, data_type: str, callback: Callable):
        """Register callback for specific data type"""
        self.callbacks[data_type] = callback
        logger.info(f"Registered callback for {data_type}")
    
    async def send_command(self, command: str) -> Dict[str, Any]:
        """Send command to Arduino and return response"""
        if not self.is_connected or not self.serial_connection:
            raise Exception("Arduino not connected")
        
        try:
            # Send command
            full_command = f"{command}\\n"
            self.serial_connection.write(full_command.encode())
            self.serial_connection.flush()
            
            # Wait for acknowledgment
            start_time = time.time()
            while (time.time() - start_time) < self.timeout:
                if self.serial_connection.in_waiting > 0:
                    response = self.serial_connection.readline().decode().strip()
                    if response:
                        return {
                            "command": command,
                            "response": response,
                            "success": "OK" in response or "DONE" in response,
                            "timestamp": time.time()
                        }
                
                await asyncio.sleep(0.01)
            
            # Timeout occurred
            return {
                "command": command,
                "response": "TIMEOUT",
                "success": False,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Command sending failed: {e}")
            return {
                "command": command,
                "response": f"ERROR: {e}",
                "success": False,
                "timestamp": time.time()
            }
    
    async def send_motor_command(self, speed: int, direction: str) -> Dict[str, Any]:
        """Send motor control command"""
        # Validate inputs
        speed = max(0, min(255, speed))  # Clamp to valid PWM range
        direction = direction.upper()
        
        if direction not in ["FORWARD", "REVERSE", "STOP"]:
            direction = "STOP"
        
        # Send command
        command = f"MOTOR_{direction}_{speed:03d}"
        return await self.send_command(command)
    
    async def send_pid_command(self, kp: float, ki: float, kd: float) -> Dict[str, Any]:
        """Send PID parameters to Arduino"""
        command = f"PID_{kp:.3f}_{ki:.3f}_{kd:.3f}"
        return await self.send_command(command)
    
    async def request_encoder_data(self) -> Dict[str, Any]:
        """Request current encoder reading"""
        return await self.send_command("READ_ENCODER")
    
    async def calibrate_encoder(self) -> Dict[str, Any]:
        """Calibrate encoder (reset position to zero)"""
        return await self.send_command("CALIBRATE_ENCODER")
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get Arduino system information"""
        return await self.send_command("SYSTEM_INFO")
    
    async def disconnect(self):
        """Disconnect from Arduino"""
        try:
            self.running = False
            
            # Cancel reading task
            if self._read_task:
                self._read_task.cancel()
                try:
                    await self._read_task
                except asyncio.CancelledError:
                    pass
                self._read_task = None
            
            # Close serial connection
            if self.serial_connection:
                # Send disconnect command
                try:
                    await self.send_command("DISCONNECT")
                except:
                    pass  # Ignore errors during disconnect
                
                self.serial_connection.close()
                self.serial_connection = None
            
            self.is_connected = False
            self.port = None
            logger.info("Disconnected from Arduino")
            
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            "connected": self.is_connected,
            "port": self.port,
            "baudrate": self.baudrate,
            "available_ports": self.scan_ports()
        }