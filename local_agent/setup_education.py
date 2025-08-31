#!/usr/bin/env python3
"""
CtrlHub Educational System Quick Setup
Helps users get started with the DC motor educational platform
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("=" * 80)
    print("CTRLHUB DC MOTOR EDUCATIONAL SYSTEM - QUICK SETUP")
    print("=" * 80)
    print("Welcome to CtrlHub! This setup will prepare your educational environment.")
    print()

def check_python_version():
    """Check if Python version is adequate"""
    print("1. Checking Python version...")
    
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 8:
        print(f"   ✓ Python {version_info.major}.{version_info.minor}.{version_info.micro} is compatible")
        return True
    else:
        print(f"   ✗ Python {version_info.major}.{version_info.minor}.{version_info.micro} is too old")
        print("   Required: Python 3.8 or newer")
        return False

def check_required_packages():
    """Check if required packages are installed"""
    print("\n2. Checking required packages...")
    
    required_packages = [
        'numpy',
        'scipy',
        'matplotlib',
        'control',
        'pyserial',
        'fastapi',
        'uvicorn',
        'PyQt5'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').lower())
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} (missing)")
            missing_packages.append(package)
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing packages"""
    if not packages:
        print("\n   All required packages are already installed!")
        return True
    
    print(f"\n3. Installing missing packages: {', '.join(packages)}")
    
    try:
        # Update pip first
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # Install packages
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
        print("   ✓ Package installation completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Package installation failed: {e}")
        return False

def setup_hardware_check():
    """Check hardware setup capabilities"""
    print("\n4. Hardware setup check...")
    
    # Check for Arduino ports (basic check)
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        arduino_ports = [p for p in ports if 'arduino' in p.description.lower() or 'ch340' in p.description.lower() or 'cp210' in p.description.lower()]
        
        if arduino_ports:
            print(f"   ✓ Found {len(arduino_ports)} potential Arduino port(s):")
            for port in arduino_ports:
                print(f"     - {port.device}: {port.description}")
        else:
            print("   ⚠ No Arduino detected (hardware optional for learning)")
            if ports:
                print("   Available serial ports:")
                for port in ports:
                    print(f"     - {port.device}: {port.description}")
    except ImportError:
        print("   ⚠ Serial port detection unavailable")
    
    return True

def create_demo_script():
    """Create a simple demo launcher script"""
    print("\n5. Creating demo launcher...")
    
    current_dir = Path(__file__).parent
    demo_script = current_dir / "run_demo.py"
    
    demo_content = '''#!/usr/bin/env python3
"""
Quick Demo Launcher for CtrlHub Educational System
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dc_motor_education_demo import main

if __name__ == "__main__":
    print("Launching CtrlHub DC Motor Educational Demo...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nDemo interrupted by user.")
    except Exception as e:
        print(f"\\nDemo error: {e}")
        print("Please check the setup and try again.")
'''
    
    try:
        with open(demo_script, 'w') as f:
            f.write(demo_content)
        
        # Make executable on Unix-like systems
        if platform.system() != 'Windows':
            os.chmod(demo_script, 0o755)
        
        print(f"   ✓ Demo launcher created: {demo_script}")
        return demo_script
    except Exception as e:
        print(f"   ✗ Failed to create demo launcher: {e}")
        return None

def display_usage_instructions(demo_script):
    """Display usage instructions"""
    print("\n" + "=" * 80)
    print("SETUP COMPLETE - USAGE INSTRUCTIONS")
    print("=" * 80)
    
    print("\n📚 EDUCATIONAL SYSTEM OVERVIEW:")
    print("CtrlHub provides a comprehensive DC motor learning experience with:")
    print("• Parameter extraction through hands-on experiments")
    print("• First-principles mathematical modeling")
    print("• Multiple PID controller design methods")
    print("• Real hardware integration (Arduino + motor)")
    print("• Simulation mode for offline learning")
    
    print("\n🚀 GETTING STARTED:")
    print("1. Run the educational demo:")
    
    if demo_script:
        if platform.system() == 'Windows':
            print(f"   python {demo_script}")
        else:
            print(f"   ./{demo_script.name}")
            print(f"   # or: python {demo_script}")
    
    print("\n2. Start the main educational system:")
    print("   python main.py")
    
    print("\n3. Access the web interface (when main.py is running):")
    print("   http://localhost:8000")
    
    print("\n🔧 HARDWARE SETUP (OPTIONAL):")
    print("• Connect Arduino Uno/Nano to your computer")
    print("• Upload the motor control sketch (see arduino_code/)")
    print("• Connect DC motor with encoder to Arduino")
    print("• Wire motor driver (L298N or similar)")
    print("• System will auto-detect Arduino on startup")
    
    print("\n📖 LEARNING MODULES:")
    print("1. Introduction & Safety - Basic concepts and safe practices")
    print("2. Parameter Extraction - Hands-on measurement techniques") 
    print("3. First-Principles Modeling - Physics-based mathematical models")
    print("4. Open-Loop Analysis - Understanding system limitations")
    print("5. Feedback Control Theory - PID controller fundamentals")
    print("6. Advanced Control - Multiple PID tuning methods")
    print("7. Real-World Applications - Practical implementation")
    
    print("\n💡 EDUCATIONAL FEATURES:")
    print("• Progressive curriculum building from basics to advanced")
    print("• Multiple PID tuning approaches (Ziegler-Nichols, pole placement, etc.)")
    print("• Theory-practice integration with real hardware")
    print("• Comprehensive progress tracking and assessment")
    print("• Works with or without hardware (simulation mode)")
    
    print("\n📁 KEY FILES:")
    print("• main.py - Main application launcher")
    print("• models/dc_motor.py - Motor physics and simulation")
    print("• models/parameter_extraction.py - Experimental methods")
    print("• models/first_principles_modeling.py - Mathematical modeling")
    print("• models/control_systems.py - PID controller design")
    print("• models/comprehensive_dc_motor_education.py - Complete curriculum")
    
    print("\n🆘 TROUBLESHOOTING:")
    print("• Hardware not detected: Check USB connections and drivers")
    print("• Import errors: Ensure all packages are installed correctly")
    print("• Permission errors: Run with appropriate permissions")
    print("• Port access issues: Close other serial monitor applications")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Run the demo to see system capabilities")
    print("2. Explore the educational modules")
    print("3. Connect hardware for hands-on experiments")
    print("4. Customize parameters for your specific motor")
    print("5. Share your learning experience!")
    
    print("\n" + "=" * 80)

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        print("\nSetup cannot continue with incompatible Python version.")
        print("Please install Python 3.8 or newer and try again.")
        return False
    
    # Check and install packages
    missing_packages = check_required_packages()
    if missing_packages:
        install_success = install_missing_packages(missing_packages)
        if not install_success:
            print("\nSetup cannot continue due to package installation failure.")
            print("Please install the required packages manually and try again.")
            return False
    
    # Hardware check
    setup_hardware_check()
    
    # Create demo script
    demo_script = create_demo_script()
    
    # Display instructions
    display_usage_instructions(demo_script)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("Setup completed successfully! 🎉")
        print("Run the demo to get started with CtrlHub educational system.")
    else:
        print("Setup encountered issues. Please resolve them and try again.")
        sys.exit(1)