#!/usr/bin/env python3
"""
CtrlHub Local Agent - Simplified Startup Script
Starts the agent with proper imports and error handling
"""

import sys
import os
import asyncio
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start the CtrlHub Local Agent"""
    try:
        print("🎓 Starting CtrlHub Control Systems - Local Agent")
        print("=" * 55)
        
        # Import and start the agent
        from local_agent.main import CtrlHubAgent
        
        agent = CtrlHubAgent()
        print("✅ Agent initialized successfully")
        
        # Start the server in a separate thread (non-blocking)
        print("🌐 Starting web server on http://localhost:8001")
        agent.start_server()
        
        # Show GUI
        print("🖥️  Opening agent control panel...")
        agent.start_gui()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Please ensure dependencies are installed:")
        print("   pip install -r local_agent/requirements.txt")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
