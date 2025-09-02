#!/usr/bin/env python3
"""
Simple CtrlHub Web Server
Launches the educational system with a simple web interface
"""

import os
import sys
import asyncio
import webbrowser
from pathlib import Path

# Add the local_agent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Import educational modules
try:
    from models.comprehensive_dc_motor_education import ComprehensiveDCMotorEducationalSystem
    from models.dc_motor import MotorParameters
    educational_system_available = True
except ImportError as e:
    print(f"Warning: Educational system not available: {e}")
    educational_system_available = False

app = FastAPI(
    title="CtrlHub Educational Platform",
    description="DC Motor Control Systems Education",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global educational system instance
educational_system = None

@app.get("/", response_class=HTMLResponse)
async def get_main_page():
    """Serve the main educational platform page"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CtrlHub - Control Systems Education</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700;900&display=swap');
            
            :root {{
                --primary-green: #00ff41;
                --secondary-green: #008f11;
                --dark-green: #003d00;
                --accent-orange: #ff6b35;
                --accent-yellow: #ffcc02;
                --warm-white: #f5f3f0;
                --paper-white: #fefdf8;
                --charcoal: #2a2a2a;
                --light-gray: #d4d4aa;
                --border-green: #00aa30;
                --shadow-green: rgba(0, 255, 65, 0.2);
                --grid-pattern: #e8e8d4;
            }}
            
            body {{
                margin: 0;
                padding: 0;
                font-family: 'JetBrains Mono', 'Monaco', 'Menlo', monospace;
                line-height: 1.6;
                background: var(--paper-white);
                color: var(--charcoal);
                background-image: radial-gradient(circle at 20px 20px, var(--grid-pattern) 1px, transparent 1px);
                background-size: 40px 40px;
                min-height: 100vh;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            .hero {{
                text-align: center;
                padding: 60px 20px;
                border: 2px solid var(--primary-green);
                background: var(--paper-white);
                margin: 20px 0;
                box-shadow: 0 0 20px var(--shadow-green);
            }}
            .hero h1 {{
                font-family: 'Orbitron', monospace;
                font-size: 3.5rem;
                margin-bottom: 20px;
                color: var(--primary-green);
                text-shadow: 2px 2px 4px var(--shadow-green);
                font-weight: 700;
            }}
            .hero p {{
                font-size: 1.2rem;
                color: var(--charcoal);
            }}
            .card {{
                background: var(--paper-white);
                border: 2px solid var(--border-green);
                padding: 30px;
                margin: 20px 0;
                box-shadow: 4px 4px 0px var(--primary-green);
                position: relative;
            }}
            .card::before {{
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: var(--primary-green);
                z-index: -1;
                opacity: 0.1;
            }}
            .features {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin: 40px 0;
            }}
            .feature {{
                text-align: center;
                padding: 20px;
                border: 2px solid var(--border-green);
                background: var(--paper-white);
                box-shadow: 4px 4px 0px var(--primary-green);
            }}
            .feature h3 {{
                color: var(--primary-green);
                margin-bottom: 15px;
                font-size: 1.5rem;
                font-family: 'Orbitron', monospace;
                font-weight: 600;
            }}
            .btn {{
                background: var(--primary-green);
                color: var(--charcoal);
                border: 2px solid var(--border-green);
                padding: 12px 24px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.2s;
                text-decoration: none;
                display: inline-block;
                font-family: 'JetBrains Mono', monospace;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .btn:hover {{
                background: var(--secondary-green);
                box-shadow: 4px 4px 0px var(--dark-green);
                transform: translate(-2px, -2px);
            }}
            .status {{
                display: inline-block;
                padding: 8px 16px;
                font-weight: bold;
                margin: 10px 0;
                border: 2px solid;
                font-family: 'JetBrains Mono', monospace;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .status-success {{
                background: var(--primary-green);
                color: var(--charcoal);
                border-color: var(--border-green);
            }}
            .status-warning {{
                background: var(--accent-orange);
                color: var(--paper-white);
                border-color: var(--accent-orange);
            }}
            .api-demo {{
                background: var(--warm-white);
                padding: 20px;
                margin: 20px 0;
                border: 2px solid var(--border-green);
                box-shadow: 4px 4px 0px var(--primary-green);
            }}
            .api-demo h4 {{
                color: var(--primary-green);
                margin-bottom: 10px;
                font-family: 'Orbitron', monospace;
                font-weight: 600;
            }}
            .api-url {{
                background: var(--charcoal);
                color: #0f0;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                margin: 5px 0;
            }}
            @media (max-width: 768px) {{
                .hero h1 {{ font-size: 2.5rem; }}
                .features {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="hero">
            <div class="container">
                <h1>🎯 CtrlHub</h1>
                <p>Advanced Control Systems Education Platform</p>
                <p style="font-size: 1rem; opacity: 0.8;">
                    Learn DC motor control through hands-on experiments, first-principles modeling, and advanced PID design
                </p>
            </div>
        </div>

        <div class="container">
            <div class="card">
                <h2 style="color: #667eea;">🚀 System Status</h2>
                <div class="status status-success">✓ Web Server Running</div>
                <div class="status {'status-success' if educational_system_available else 'status-warning'}">
                    {'✓ Educational System Ready' if educational_system_available else '⚠ Educational System Loading...'}
                </div>
                <p style="color: #666; margin-top: 20px;">
                    Server running on <strong>http://localhost:8000</strong>
                </p>
            </div>

            <div class="card">
                <h2 style="color: #667eea;">📚 Educational Features</h2>
                <div class="features">
                    <div class="feature">
                        <h3>🔬 Parameter Extraction</h3>
                        <p>Learn to measure motor parameters through hands-on experiments including resistance, back-EMF, torque constant, and inertia analysis.</p>
                    </div>
                    <div class="feature">
                        <h3>📐 First-Principles Modeling</h3>
                        <p>Derive motor equations from Kirchhoff's and Newton's laws. Build mathematical models from fundamental physics principles.</p>
                    </div>
                    <div class="feature">
                        <h3>🎛️ PID Controller Design</h3>
                        <p>Master multiple PID tuning methods including Ziegler-Nichols, pole placement, frequency domain, and genetic algorithms.</p>
                    </div>
                    <div class="feature">
                        <h3>⚡ Hardware Integration</h3>
                        <p>Validate theory with real Arduino-based motor control. Bridge the gap between simulation and real-world applications.</p>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2 style="color: #667eea;">🎓 7-Module Progressive Curriculum</h2>
                <div style="display: grid; gap: 15px;">
                    <div style="padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; background: rgba(102, 126, 234, 0.05);">
                        <strong>Module 1: Introduction & Safety</strong> (30 min) - Fundamentals and safety protocols
                    </div>
                    <div style="padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; background: rgba(102, 126, 234, 0.05);">
                        <strong>Module 2: Parameter Extraction</strong> (90 min) - Hands-on measurement techniques
                    </div>
                    <div style="padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; background: rgba(102, 126, 234, 0.05);">
                        <strong>Module 3: First-Principles Modeling</strong> (60 min) - Physics-based mathematical models
                    </div>
                    <div style="padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; background: rgba(102, 126, 234, 0.05);">
                        <strong>Module 4: Open-Loop Analysis</strong> (45 min) - System limitations understanding
                    </div>
                    <div style="padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; background: rgba(102, 126, 234, 0.05);">
                        <strong>Module 5: Feedback Control Theory</strong> (75 min) - PID fundamentals
                    </div>
                    <div style="padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; background: rgba(102, 126, 234, 0.05);">
                        <strong>Module 6: Advanced Control Design</strong> (120 min) - Multiple tuning methods
                    </div>
                    <div style="padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; background: rgba(102, 126, 234, 0.05);">
                        <strong>Module 7: Real-World Applications</strong> (90 min) - Hardware validation
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/demo" class="btn" style="font-size: 18px; padding: 15px 30px;">
                        🚀 Start Educational Demo
                    </a>
                    <a href="/api/docs" class="btn" style="font-size: 16px; padding: 12px 24px; margin-left: 10px;">
                        📖 API Documentation
                    </a>
                </div>
            </div>

            <div class="card">
                <h2 style="color: #667eea;">🔧 API Endpoints</h2>
                <div class="api-demo">
                    <h4>Available Educational Endpoints:</h4>
                    <div class="api-url">GET /api/status - System status</div>
                    <div class="api-url">GET /api/curriculum - Curriculum overview</div>
                    <div class="api-url">POST /api/start-module - Start educational module</div>
                    <div class="api-url">GET /api/demo - Run educational demo</div>
                    <div class="api-url">GET /docs - Interactive API documentation</div>
                </div>
            </div>

            <div style="text-align: center; padding: 40px 0; color: white;">
                <p style="opacity: 0.8;">
                    CtrlHub - Bridging Theory and Practice in Control Systems Education
                </p>
                <p style="opacity: 0.6; font-size: 14px;">
                    Open Source Educational Platform | MIT License
                </p>
            </div>
        </div>

        <script>
            // Auto-refresh system status
            setInterval(async () => {{
                try {{
                    const response = await fetch('/api/status');
                    const status = await response.json();
                    console.log('System status:', status);
                }} catch (error) {{
                    console.log('Status check error:', error);
                }}
            }}, 10000);
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/api/status")
async def get_system_status():
    """Get current system status"""
    return {
        "status": "running",
        "educational_system": educational_system_available,
        "version": "1.0.0",
        "platform": "CtrlHub",
        "modules_available": [
            "Parameter Extraction",
            "First-Principles Modeling", 
            "Control Systems Design",
            "Comprehensive Education"
        ] if educational_system_available else [],
        "server_time": asyncio.get_event_loop().time()
    }

@app.get("/api/curriculum")
async def get_curriculum():
    """Get educational curriculum overview"""
    if not educational_system_available:
        raise HTTPException(status_code=503, detail="Educational system not available")
    
    return {
        "curriculum": [
            {
                "module": "Module 1: Introduction & Safety",
                "duration": "30 minutes",
                "description": "Control systems fundamentals and safety protocols",
                "objectives": ["Understand DC motor basics", "Learn safety procedures", "Setup hardware"]
            },
            {
                "module": "Module 2: Parameter Extraction", 
                "duration": "90 minutes",
                "description": "Hands-on measurement techniques",
                "objectives": ["Measure resistance", "Extract back-EMF", "Analyze inertia/friction"]
            },
            {
                "module": "Module 3: First-Principles Modeling",
                "duration": "60 minutes", 
                "description": "Physics-based mathematical models",
                "objectives": ["Apply Kirchhoff's laws", "Use Newton's dynamics", "Derive transfer functions"]
            },
            {
                "module": "Module 4: Open-Loop Analysis",
                "duration": "45 minutes",
                "description": "System limitations understanding", 
                "objectives": ["Analyze step response", "Understand limitations", "Need for feedback"]
            },
            {
                "module": "Module 5: Feedback Control Theory",
                "duration": "75 minutes",
                "description": "PID controller fundamentals",
                "objectives": ["Learn PID structure", "Understand stability", "Implement controllers"]
            },
            {
                "module": "Module 6: Advanced Control Design",
                "duration": "120 minutes",
                "description": "Multiple PID tuning methods",
                "objectives": ["Ziegler-Nichols tuning", "Pole placement", "Frequency domain design"]
            },
            {
                "module": "Module 7: Real-World Applications", 
                "duration": "90 minutes",
                "description": "Hardware validation and optimization",
                "objectives": ["Hardware integration", "Performance testing", "Real-world validation"]
            }
        ],
        "total_duration": "8.5 hours",
        "prerequisite": "Basic understanding of physics and mathematics"
    }

@app.get("/demo")
async def run_educational_demo():
    """Run a comprehensive educational demo"""
    if not educational_system_available:
        return HTMLResponse("""
        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>Educational Demo</h1>
        <p>Educational system is currently loading...</p>
        <p>Please check the console for more details.</p>
        <a href="/" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Back to Home</a>
        </body></html>
        """)
    
    try:
        # Initialize educational system with demo parameters
        demo_motor_params = MotorParameters(
            R=2.5,      # 2.5 Ohms resistance
            L=0.001,    # 1 mH inductance  
            J=0.0001,   # 0.1 g⋅cm² inertia
            b=0.00005,  # Friction coefficient
            Kt=0.05,    # 0.05 N⋅m/A torque constant
            Ke=0.05     # 0.05 V⋅s/rad back-EMF constant
        )
        
        # Create educational system instance
        global educational_system
        if educational_system is None:
            educational_system = ComprehensiveDCMotorEducationalSystem(
                arduino_interface=None,  # Simulation mode
                motor_params=demo_motor_params
            )
        
        # Generate a comprehensive report
        demo_results = educational_system.generate_comprehensive_educational_report()
        
        return {
            "status": "success",
            "message": "Educational demo completed successfully",
            "motor_parameters": {
                "resistance": demo_motor_params.R,
                "inductance": demo_motor_params.L,
                "inertia": demo_motor_params.J,
                "friction": demo_motor_params.b,
                "torque_constant": demo_motor_params.Kt,
                "back_emf_constant": demo_motor_params.Ke
            },
            "demo_results": demo_results,
            "next_steps": [
                "Connect Arduino hardware for hands-on experiments",
                "Run parameter extraction experiments",
                "Design and test PID controllers",
                "Validate models with real hardware"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Demo failed: {str(e)}",
            "suggestion": "Check system logs for detailed error information"
        }

@app.post("/api/start-module")
async def start_educational_module(module_name: str):
    """Start a specific educational module"""
    if not educational_system_available:
        raise HTTPException(status_code=503, detail="Educational system not available")
    
    try:
        global educational_system
        if educational_system is None:
            # Initialize with default parameters
            demo_motor_params = MotorParameters(R=2.5, L=0.001, J=0.0001, b=0.00005, Kt=0.05, Ke=0.05)
            educational_system = ComprehensiveDCMotorEducationalSystem(
                arduino_interface=None,
                motor_params=demo_motor_params
            )
        
        # Start the educational journey
        result = await educational_system.start_educational_journey(module_name)
        return {
            "status": "success",
            "module": module_name,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start module: {str(e)}")

def main():
    """Main entry point"""
    print("🎯 Starting CtrlHub Educational Platform...")
    print(f"📚 Educational system available: {educational_system_available}")
    
    # Configuration
    host = "0.0.0.0"
    port = 8000
    
    print(f"🚀 Server starting on http://{host}:{port}")
    print("🌐 Opening browser...")
    
    # Open browser after a short delay
    def open_browser():
        import time
        time.sleep(2)
        webbrowser.open(f"http://localhost:{port}")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()