#!/usr/bin/env python3
"""
CtrlHub Local Agent - Demo Script
Demonstrates the capabilities of the local agent
"""

import asyncio
import json
import time
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from local_agent.models.dc_motor import DCMotorModel, MotorParameters

async def demo_simulation():
    """Demo the simulation capabilities"""
    print("🎓 CtrlHub Agent Demo - Simulation Engine")
    print("=" * 50)
    
    # Create DC motor model
    params = MotorParameters(
        R=2.0,    # Resistance (Ohms)
        L=0.001,  # Inductance (H) 
        J=0.0001, # Inertia (kg⋅m²)
        b=0.00001,# Friction (N⋅m⋅s/rad)
        Kt=0.01,  # Torque constant (N⋅m/A)
        Ke=0.01   # Back-EMF constant (V⋅s/rad)
    )
    
    motor = DCMotorModel(params)
    
    print(f"📊 Motor Parameters:")
    print(f"   Resistance: {params.R} Ω")
    print(f"   Inductance: {params.L} H")
    print(f"   Inertia: {params.J} kg⋅m²")
    print(f"   Friction: {params.b} N⋅m⋅s/rad")
    print(f"   Torque Constant: {params.Kt} N⋅m/A")
    print(f"   Back-EMF Constant: {params.Ke} V⋅s/rad")
    print()
    
    # Run step response simulation
    print("🚀 Running 12V Step Response Simulation...")
    result = motor.simulate_step_response(voltage=12.0, duration=5.0)
    
    if result['success']:
        data = result['data']
        print(f"✅ Simulation completed successfully!")
        print(f"   Duration: {len(data['time'])} data points")
        print(f"   Final Current: {data['current'][-1]:.3f} A")
        print(f"   Final Speed: {data['angular_velocity'][-1]:.1f} rad/s")
        print(f"   Final RPM: {data['rpm'][-1]:.1f}")
        
        # Save results
        with open('demo_results.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"📁 Results saved to demo_results.json")
    else:
        print(f"❌ Simulation failed: {result['error']}")
    
    print()

def demo_api_simulation():
    """Demo API-style simulation"""
    print("🌐 API Simulation Demo")
    print("=" * 30)
    
    motor = DCMotorModel(MotorParameters(
        R=2.0, L=0.001, J=0.0001, b=0.00001, Kt=0.01, Ke=0.01
    ))
    
    # Test different simulation types
    test_cases = [
        {
            "name": "Step Response",
            "request": {
                "type": "step_response",
                "voltage": 12.0,
                "duration": 3.0
            }
        },
        {
            "name": "Frequency Response", 
            "request": {
                "type": "frequency_response",
                "freq_min": 0.1,
                "freq_max": 1000.0,
                "freq_points": 50
            }
        }
    ]
    
    for test in test_cases:
        print(f"🧪 Testing {test['name']}...")
        result = motor.simulate(test['request'])
        
        if result.get('success'):
            print(f"   ✅ {test['name']} completed")
        else:
            print(f"   ❌ {test['name']} failed: {result.get('error')}")
    
    print()

async def demo_hardware_interface():
    """Demo hardware interface (without actual hardware)"""
    print("🔌 Hardware Interface Demo")
    print("=" * 35)
    
    try:
        from local_agent.hardware.arduino_interface import ArduinoInterface
        
        # Create interface
        arduino = ArduinoInterface()
        
        # Scan for ports
        print("🔍 Scanning for Arduino ports...")
        ports = arduino.scan_ports()
        
        if ports:
            print(f"   Found potential Arduino ports: {ports}")
            print("   (Note: This is a demo - no actual connection attempted)")
        else:
            print("   No Arduino ports detected")
            print("   (This is normal if no Arduino is connected)")
    except ImportError as e:
        print(f"   Hardware interface not available: {e}")
        print("   This is normal in demo mode")
    
    print()

def demo_web_integration():
    """Show how the web frontend would integrate"""
    print("🌐 Web Integration Example")
    print("=" * 35)
    
    # Show example API requests
    examples = [
        {
            "endpoint": "GET /health",
            "description": "Check agent status",
            "response": {
                "agent_status": "running",
                "arduino_connected": False,
                "simulation_engine": "ready"
            }
        },
        {
            "endpoint": "POST /simulation/dc_motor",
            "description": "Run DC motor simulation",
            "request": {
                "type": "step_response",
                "voltage": 12.0,
                "duration": 5.0
            }
        }
    ]
    
    for example in examples:
        print(f"📡 {example['endpoint']}")
        print(f"   {example['description']}")
        if 'request' in example:
            print(f"   Request: {json.dumps(example['request'], indent=6)}")
        if 'response' in example:
            print(f"   Response: {json.dumps(example['response'], indent=6)}")
        print()

async def main():
    """Run all demos"""
    print("🎓 CtrlHub Control Systems - Local Agent Demo")
    print("=" * 55)
    print("This demo showcases the capabilities of the CtrlHub Local Agent")
    print("without requiring actual hardware or web frontend.")
    print()
    
    # Run demos
    await demo_simulation()
    demo_api_simulation()
    await demo_hardware_interface()
    demo_web_integration()
    
    print("🎉 Demo completed!")
    print()
    print("🚀 To start the full agent:")
    print("   python local_agent/main.py")
    print()
    print("🌐 Then open CtrlHub in your browser to see the integration!")

if __name__ == "__main__":
    asyncio.run(main())
