"""
Hardware Interface Module
Professional Arduino communication for CtrlHub Control Systems
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
    
    def get_connection_status(self) -> bool:
        """Check if Arduino is currently connected"""
        return self.is_connected and self.serial_connection is not None
    
    def connect_sync(self, port: Optional[str] = None) -> bool:
        """Synchronous connect wrapper for GUI"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.connect(port))
                return result
            finally:
                loop.close()
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def disconnect_sync(self):
        """Synchronous disconnect wrapper for GUI"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.disconnect())
            finally:
                loop.close()
        except Exception as e:
            print(f"Disconnect error: {e}")
        
    def scan_ports(self) -> List[str]:
        """
        Scan for available Arduino ports
        Returns list of potential Arduino port names
        """
        arduino_ports = []
        
        try:
            ports = serial.tools.list_ports.comports()
            print(f"Scanning {len(ports)} serial ports...")
            
            for port in ports:
                print(f"Found port: {port.device} - {port.description}")
                # Check for common Arduino identifiers
                port_desc = port.description.lower()
                port_hwid = port.hwid.lower() if port.hwid else ""
                
                arduino_indicators = [
                    'arduino', 'ch340', 'ch341', 'cp210', 'ftdi', 
                    'usb serial', 'usb2.0-serial', 'usbmodem'
                ]
                
                if any(indicator in port_desc or indicator in port_hwid 
                       for indicator in arduino_indicators):
                    arduino_ports.append(port.device)
                    print(f"✅ Identified Arduino: {port.device} - {port.description}")
                elif 'cu.usb' in port.device or 'ttyUSB' in port.device or 'ttyACM' in port.device:
                    # Include any USB serial device
                    arduino_ports.append(port.device)
                    print(f"✅ USB Serial device: {port.device} - {port.description}")
            
            # Always include your specific Arduino port
            your_arduino = "/dev/cu.usbmodem12301"
            if your_arduino not in arduino_ports:
                arduino_ports.insert(0, your_arduino)  # Put it first
                print(f"✅ Added your Arduino: {your_arduino}")
        
        except Exception as e:
            print(f"Port scanning failed: {e}")
            # Fallback to your known Arduino port
            arduino_ports = ["/dev/cu.usbmodem12301"]
        
        print(f"Final Arduino ports list: {arduino_ports}")
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
            
            # For development: Skip handshake and assume connection is good
            print(f"✅ Successfully connected to Arduino on {port} (dev mode)")
            self.port = port
            self.is_connected = True
            
            # Start reading task
            self._start_reading_task()
            return True
            
            # TODO: Re-enable handshake when Arduino firmware is ready
            # handshake_success = await self._send_handshake()
            # if handshake_success:
            #     self.port = port
            #     self.is_connected = True
            #     logger.info(f"Successfully connected to Arduino on {port}")
            #     self._start_reading_task()
            #     return True
            # else:
            #     self.serial_connection.close()
            #     self.serial_connection = None
            #     logger.error("Arduino handshake failed")
            #     return False
                
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

    async def run_coast_down_test(self, data_callback: Callable = None) -> Dict[str, Any]:
        """
        Run the coast-down test for inertia measurement
        Based on your Arduino sketch for coast-down testing
        """
        if not self.is_connected:
            return {"success": False, "error": "Arduino not connected"}
        
        try:
            logger.info("Starting coast-down test...")
            
            # Send command to start coast-down test
            await self.send_command("START_COAST_DOWN")
            
            # Collect data for the test duration
            test_data = []
            start_time = time.time()
            
            # Read data for about 12 seconds (4s accel + 8s logging)
            timeout_time = start_time + 15  # Extra buffer
            
            while time.time() < timeout_time:
                try:
                    if self.serial_connection.in_waiting > 0:
                        line = self.serial_connection.readline().decode('utf-8').strip()
                        
                        if line and ',' in line:
                            try:
                                # Parse CSV format: "ElapsedTime(ms),Speed(RPM)"
                                parts = line.split(',')
                                if len(parts) == 2:
                                    elapsed_ms = float(parts[0])
                                    speed_rpm = float(parts[1])
                                    
                                    data_point = {
                                        'time': elapsed_ms,
                                        'speed': speed_rpm
                                    }
                                    
                                    test_data.append(data_point)
                                    
                                    # Call callback if provided
                                    if data_callback:
                                        data_callback(data_point)
                                        
                                    logger.debug(f"Coast-down data: {elapsed_ms}ms, {speed_rpm}RPM")
                                    
                            except ValueError as e:
                                # Skip invalid data points
                                logger.debug(f"Skipping invalid data: {line}")
                                
                        elif "Test complete" in line:
                            logger.info("Coast-down test completed by Arduino")
                            break
                            
                except Exception as e:
                    logger.error(f"Error reading test data: {e}")
                    
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
            
            logger.info(f"Coast-down test finished. Collected {len(test_data)} data points")
            
            return {
                "success": True,
                "data": test_data,
                "test_type": "coast-down",
                "duration": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Coast-down test error: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_steady_state_test(self, pwm_value: int = 150, duration: int = 10, 
                                  data_callback: Callable = None) -> Dict[str, Any]:
        """
        Run steady-state test for viscous damping measurement
        Based on your Arduino sketch for steady-state testing
        """
        if not self.is_connected:
            return {"success": False, "error": "Arduino not connected"}
        
        try:
            logger.info(f"Starting steady-state test at PWM {pwm_value} for {duration}s...")
            
            # Send command to start steady-state test
            command = f"START_STEADY_STATE,{pwm_value},{duration}"
            await self.send_command(command)
            
            # Collect data for the test duration
            test_data = []
            start_time = time.time()
            timeout_time = start_time + duration + 5  # Extra buffer
            
            while time.time() < timeout_time:
                try:
                    if self.serial_connection.in_waiting > 0:
                        line = self.serial_connection.readline().decode('utf-8').strip()
                        
                        if "Current Speed:" in line:
                            try:
                                # Parse format: "Current Speed: 123.45 RPM"
                                speed_str = line.split(":")[1].strip().split()[0]
                                speed_rpm = float(speed_str)
                                
                                elapsed_time = time.time() - start_time
                                
                                data_point = {
                                    'time': elapsed_time * 1000,  # Convert to ms
                                    'speed': speed_rpm,
                                    'pwm': pwm_value
                                }
                                
                                test_data.append(data_point)
                                
                                # Call callback if provided
                                if data_callback:
                                    data_callback(data_point)
                                    
                                logger.debug(f"Steady-state data: {elapsed_time:.1f}s, {speed_rpm}RPM")
                                
                            except (ValueError, IndexError) as e:
                                logger.debug(f"Skipping invalid speed data: {line}")
                                
                except Exception as e:
                    logger.error(f"Error reading steady-state data: {e}")
                    
                await asyncio.sleep(0.1)  # Read every 100ms
            
            logger.info(f"Steady-state test finished. Collected {len(test_data)} data points")
            
            return {
                "success": True,
                "data": test_data,
                "test_type": "steady-state",
                "duration": time.time() - start_time,
                "pwm_value": pwm_value
            }
            
        except Exception as e:
            logger.error(f"Steady-state test error: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_back_emf_test(self, pwm_value: int = 200, duration: int = 5,
                               data_callback: Callable = None) -> Dict[str, Any]:
        """
        Run back-EMF measurement test
        Motor runs at constant speed for voltage/current measurements
        """
        if not self.is_connected:
            return {"success": False, "error": "Arduino not connected"}
        
        try:
            logger.info(f"Starting back-EMF test at PWM {pwm_value} for {duration}s...")
            
            # Send command to start back-EMF test
            command = f"START_BACK_EMF,{pwm_value},{duration}"
            await self.send_command(command)
            
            # Collect data for the test duration
            test_data = []
            start_time = time.time()
            timeout_time = start_time + duration + 3  # Extra buffer
            
            while time.time() < timeout_time:
                try:
                    if self.serial_connection.in_waiting > 0:
                        line = self.serial_connection.readline().decode('utf-8').strip()
                        
                        if "Current Speed:" in line:
                            try:
                                # Parse format: "Current Speed: 123.45 RPM"
                                speed_str = line.split(":")[1].strip().split()[0]
                                speed_rpm = float(speed_str)
                                
                                elapsed_time = time.time() - start_time
                                
                                # For back-EMF test, we need current measurement
                                # This would be enhanced with actual current sensor
                                estimated_current = 0.6  # Typical current for this PWM
                                
                                data_point = {
                                    'time': elapsed_time * 1000,  # Convert to ms
                                    'speed': speed_rpm,
                                    'current': estimated_current,
                                    'pwm': pwm_value
                                }
                                
                                test_data.append(data_point)
                                
                                # Call callback if provided
                                if data_callback:
                                    data_callback(data_point)
                                    
                                logger.debug(f"Back-EMF data: {elapsed_time:.1f}s, {speed_rpm}RPM, {estimated_current}A")
                                
                            except (ValueError, IndexError) as e:
                                logger.debug(f"Skipping invalid back-EMF data: {line}")
                                
                except Exception as e:
                    logger.error(f"Error reading back-EMF data: {e}")
                    
                await asyncio.sleep(0.1)  # Read every 100ms
            
            logger.info(f"Back-EMF test finished. Collected {len(test_data)} data points")
            
            return {
                "success": True,
                "data": test_data,
                "test_type": "back-emf",
                "duration": time.time() - start_time,
                "pwm_value": pwm_value
            }
            
        except Exception as e:
            logger.error(f"Back-EMF test error: {e}")
            return {"success": False, "error": str(e)}

    # PID Control Methods
    async def set_pid_parameters(self, kp: float, ki: float, kd: float) -> Dict[str, Any]:
        """Set PID controller parameters"""
        command = f"SET_PID {kp} {ki} {kd}"
        return await self.send_command(command)
    
    async def set_target_speed(self, speed: float) -> Dict[str, Any]:
        """Set target speed for PID control"""
        command = f"SET_SPEED {speed}"
        return await self.send_command(command)
    
    async def start_pid_control(self) -> Dict[str, Any]:
        """Start PID control loop"""
        return await self.send_command("START_PID_CONTROL")
    
    async def stop_pid_control(self) -> Dict[str, Any]:
        """Stop PID control loop"""
        return await self.send_command("STOP_PID_CONTROL")
    
    async def get_current_speed(self) -> Dict[str, Any]:
        """Get current motor speed"""
        return await self.send_command("GET_SPEED")
    
    async def collect_pid_data(self, duration: float = 10.0) -> Dict[str, Any]:
        """Collect PID control data over specified duration"""
        if not self.is_connected:
            return {"success": False, "error": "Arduino not connected"}
        
        try:
            time_data = []
            speed_data = []
            control_output_data = []
            error_data = []
            start_time = time.time()
            
            while (time.time() - start_time) < duration:
                try:
                    # Get current data
                    response = await self.send_command("GET_PID_DATA")
                    if response and response.get("success"):
                        data_str = response.get("response", "")
                        # Parse response format: "SPEED:100.0,ERROR:5.2,OUTPUT:150"
                        if "SPEED:" in data_str:
                            parts = data_str.split(",")
                            speed = float(parts[0].split(":")[1]) if len(parts) > 0 else 0.0
                            error = float(parts[1].split(":")[1]) if len(parts) > 1 else 0.0
                            output = float(parts[2].split(":")[1]) if len(parts) > 2 else 0.0
                            
                            current_time = time.time() - start_time
                            time_data.append(current_time)
                            speed_data.append(speed)
                            error_data.append(error)
                            control_output_data.append(output)
                    
                    await asyncio.sleep(0.05)  # 20Hz sampling rate
                    
                except Exception as e:
                    logger.warning(f"Data collection error: {e}")
                    continue
            
            return {
                "success": True,
                "time": time_data,
                "speed": speed_data,
                "error": error_data,
                "control_output": control_output_data,
                "duration": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"PID data collection error: {e}")
            return {"success": False, "error": str(e)}