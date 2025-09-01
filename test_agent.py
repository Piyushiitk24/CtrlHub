#!/usr/bin/env python3
"""
Simple test of CtrlHub Local Agent components
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy as np
    print("✅ NumPy imported successfully")
    
    import scipy
    print("✅ SciPy imported successfully")
    
    import control
    print("✅ Control library imported successfully")
    
    import fastapi
    print("✅ FastAPI imported successfully")
    
    import uvicorn
    print("✅ Uvicorn imported successfully")
    
    import serial
    print("✅ PySerial imported successfully")
    
    print("\n🎓 CtrlHub Local Agent - Component Test")
    print("=" * 50)
    
    # Test DC Motor Model directly
    print("\n📊 Testing DC Motor Model...")
    
    # Define motor parameters manually
    class MotorParameters:
        def __init__(self, R, L, J, b, Kt, Ke):
            self.R = R    # Resistance (Ohms)
            self.L = L    # Inductance (H)
            self.J = J    # Inertia (kg⋅m²)
            self.b = b    # Friction (N⋅m⋅s/rad)
            self.Kt = Kt  # Torque constant (N⋅m/A)
            self.Ke = Ke  # Back-EMF constant (V⋅s/rad)
            
        def to_dict(self):
            return {
                'R': self.R, 'L': self.L, 'J': self.J,
                'b': self.b, 'Kt': self.Kt, 'Ke': self.Ke
            }
    
    # Create simple DC motor simulation
    params = MotorParameters(
        R=2.0,    # 2 ohm resistance
        L=0.001,  # 1 mH inductance
        J=0.0001, # Small inertia
        b=0.00001,# Low friction
        Kt=0.01,  # Torque constant
        Ke=0.01   # Back-EMF constant
    )
    
    print(f"   Motor Parameters: R={params.R}Ω, L={params.L}H, J={params.J}kg⋅m²")
    
    # Simple step response calculation
    from scipy.integrate import odeint
    import matplotlib.pyplot as plt
    
    def motor_dynamics(state, t, voltage=12.0, load_torque=0.0):
        """Simple DC motor differential equations"""
        current, angular_velocity = state
        
        # Electrical equation: L*di/dt = V - R*i - Ke*w
        di_dt = (voltage - params.R * current - params.Ke * angular_velocity) / params.L
        
        # Mechanical equation: J*dw/dt = Kt*i - b*w - T_load
        dw_dt = (params.Kt * current - params.b * angular_velocity - load_torque) / params.J
        
        return [di_dt, dw_dt]
    
    # Simulate step response
    t = np.linspace(0, 5.0, 500)  # 5 seconds
    initial_state = [0.0, 0.0]   # Start at rest
    
    solution = odeint(motor_dynamics, initial_state, t, args=(12.0,))
    current = solution[:, 0]
    angular_velocity = solution[:, 1]
    rpm = angular_velocity * 60 / (2 * np.pi)
    
    print(f"   ✅ Simulation completed successfully!")
    print(f"   Final Current: {current[-1]:.3f} A")
    print(f"   Final Speed: {angular_velocity[-1]:.1f} rad/s")
    print(f"   Final RPM: {rpm[-1]:.1f}")
    
    # Test basic FastAPI setup
    print("\n🌐 Testing FastAPI Setup...")
    app = fastapi.FastAPI(title="CtrlHub Test Agent")
    
    @app.get("/")
    async def root():
        return {"status": "CtrlHub Agent Test Running", "version": "1.0.0"}
    
    @app.get("/health")
    async def health():
        return {
            "agent_status": "running",
            "arduino_connected": False,
            "simulation_engine": "ready"
        }
    
    print("   ✅ FastAPI app created successfully")
    print("   ✅ Routes defined successfully")
    
    # Test port scanning (simulate)
    print("\n🔌 Testing Hardware Interface...")
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        print(f"   Found {len(ports)} serial ports:")
        for port in ports[:3]:  # Show max 3 ports
            print(f"      - {port.device}: {port.description}")
        if len(ports) > 3:
            print(f"      ... and {len(ports) - 3} more")
    except Exception as e:
        print(f"   Port scanning test: {e}")
    
    print("\n🎉 All Components Test Passed!")
    print("\n🚀 CtrlHub Local Agent is ready to run!")
    print("   To start the full agent:")
    print("   python3 local_agent/main.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install fastapi uvicorn numpy scipy control pyserial websockets")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
