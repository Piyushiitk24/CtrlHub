# CtrlHub Control Systems - Local Agent

## 🎓 Educational Hardware Interface & Simulation Engine

The CtrlHub Local Agent is a powerful desktop application that enables students to:
- Connect their Arduino hardware directly to their computer
- Run complex control system simulations using Python
- Bridge the gap between web-based learning and hands-on experimentation

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      STUDENT'S COMPUTER                    │
│ ┌─────────────────┐   ┌─────────────────────────────────┐  │
│ │ React Frontend  │   │    Python Local Agent           │  │
│ │  (Browser)      │   │  (Desktop Application)          │  │
│ │                 │◄──►│                                │  │
│ │ - Beautiful UI  │   │ - Hardware Communication        │  │
│ │ - Web Serial    │   │ - Complex Simulations           │  │
│ │ - Simple Sims   │   │ - MATLAB Model Translation      │  │
│ └─────────────────┘   └─────────────────────────────────┘  │
│                                                           │
└─────────────┼───────────────────────────┼──────────────────┘
              │                           │
   ┌──────────▼──────────────────────────▼─────────────┐
   │                 CLOUD BACKEND                     │
   │ ┌───────────────────────────────────────────────┐ │
   │ │          Educational Content                 │ │
   │ │ - Course Materials      - Model Library      │ │
   │ │ - Progress Tracking     - Collaboration Tools│ │
   │ └───────────────────────────────────────────────┘ │
   └───────────────────────────────────────────────────┘
```

## 🚀 Features

### Hardware Interface
- **Direct Arduino Communication**: USB serial connection to student's hardware
- **Auto-Detection**: Automatically scans and identifies Arduino boards
- **Real-time Data**: WebSocket support for live sensor readings
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Simulation Engine
- **Complex Control Systems**: Full Python-based simulations with SciPy/Control
- **DC Motor Models**: First-principles mathematical modeling
- **PID Controllers**: Professional control system implementations
- **Real-time Plotting**: Live visualization of system responses

### Web Integration
- **RESTful API**: Clean interface for frontend communication
- **WebSocket Support**: Real-time bidirectional communication
- **Fallback Mode**: Basic JavaScript simulations when agent unavailable
- **Cross-Origin Ready**: Configured for web browser integration

## 📦 Installation

### Quick Start (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd CtrlHub

# Run the installer
chmod +x installer/install.sh
./installer/install.sh

# Start the agent
python local_agent/main.py
```

### Manual Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r local_agent/requirements.txt

# Run the agent
python local_agent/main.py
```

### Build Standalone Executable
```bash
# Install build tools
pip install cx-freeze pyinstaller

# Build executable
python setup.py build

# Or use PyInstaller
pyinstaller --onefile --windowed local_agent/main.py
```

## 🖥️ Usage

### 1. Start the Agent
```bash
python local_agent/main.py
```

This opens a GUI window showing:
- Agent status (running on `http://localhost:8001`)
- Arduino connection status
- Activity log

### 2. Connect Hardware
- Plug Arduino into USB port
- Click "Scan for Arduino" in the GUI
- Agent auto-connects when found

### 3. Use with Web Frontend
- Open CtrlHub website in browser
- The web interface automatically detects the local agent
- Enjoy full hardware integration!

## 🔌 API Reference

### Health Check
```http
GET /health
```
Returns agent and hardware status.

### Hardware Control
```http
POST /hardware/connect     # Connect to Arduino
POST /hardware/disconnect  # Disconnect Arduino  
GET  /hardware/ports       # Scan available ports
```

### Simulation Engine
```http
POST /simulation/run       # Run general simulation
POST /simulation/dc_motor  # DC motor specific simulation
```

### WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8001/ws');
ws.send(JSON.stringify({
  type: "arduino_command",
  command: "READ_ENCODER"
}));
```

## 🎯 DC Motor Simulation Example

### Frontend Integration
```typescript
import LocalAgentHandler from './utils/LocalAgentHandler';

const agentHandler = new LocalAgentHandler();

const runSimulation = async () => {
  const params = {
    type: 'dc_motor',
    parameters: {
      voltage: 12.0,
      resistance: 2.0,
      inductance: 0.001,
      ke: 0.01,
      kt: 0.01,
      j: 0.0001,
      b: 0.00001
    },
    duration: 5.0
  };

  const result = await agentHandler.runDCMotorSimulation(params);
  console.log('Simulation results:', result.data);
};
```

### Python Direct Usage
```python
from models.dc_motor import DCMotorModel, MotorParameters

# Define motor parameters
params = MotorParameters(
    R=2.0,    # Resistance (Ohms)
    L=0.001,  # Inductance (H)
    J=0.0001, # Inertia (kg⋅m²)
    b=0.00001,# Friction (N⋅m⋅s/rad)
    Kt=0.01,  # Torque constant (N⋅m/A)
    Ke=0.01   # Back-EMF constant (V⋅s/rad)
)

# Create model and simulate
motor = DCMotorModel(params)
result = motor.simulate_step_response(voltage=12.0, duration=5.0)
```

## 🔧 Configuration

### Environment Variables
```bash
export CTRLHUB_AGENT_PORT=8001
export CTRLHUB_LOG_LEVEL=INFO
export CTRLHUB_ARDUINO_TIMEOUT=2.0
```

### Configuration Files
The agent looks for `config.json` in the current directory:
```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8001
  },
  "hardware": {
    "baudrate": 9600,
    "timeout": 2.0,
    "auto_scan": true
  },
  "simulation": {
    "default_duration": 10.0,
    "time_step": 0.01,
    "real_time": false
  }
}
```

## 🐛 Troubleshooting

### Agent Won't Start
- Check Python version (3.8+ required)
- Verify all dependencies installed
- Check port 8001 is available

### Arduino Not Detected
- Verify USB connection
- Check device drivers installed
- Try different USB port
- Run with admin/sudo privileges

### Simulation Errors
- Check parameter values are realistic
- Verify numerical stability
- Reduce simulation time step

## 🔒 Security Considerations

- Agent only accepts connections from localhost
- No external network access required
- Student data stays on local machine
- Optional cloud sync for educational content

## 📝 Development

### Project Structure
```
local_agent/
├── main.py                 # Main application entry
├── requirements.txt        # Python dependencies
├── hardware/
│   └── arduino_interface.py # Arduino communication
├── models/
│   ├── dc_motor.py         # DC motor models
│   └── control_systems.py  # Control theory
├── simulations/
│   └── simulation_engine.py # Simulation orchestration
└── controllers/
    └── pid_controller.py   # PID implementation
```

### Adding New Models
1. Create model in `models/` directory
2. Inherit from base simulation class
3. Add API endpoint in `main.py`
4. Update frontend `LocalAgentHandler.ts`

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## 📚 Educational Resources

### Supported Experiments
- DC Motor Characterization
- PID Controller Tuning
- Step Response Analysis
- Frequency Response
- State Space Modeling
- Encoder Feedback Control

### Learning Objectives
- First-principles modeling
- Control system design
- Hardware-software integration
- Real-time system programming
- Professional software practices

## 🤝 Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for guidelines.

### Development Setup
```bash
# Fork and clone repository
git clone <your-fork>
cd CtrlHub

# Create feature branch
git checkout -b feature/new-model

# Install development dependencies
pip install -r requirements-dev.txt

# Make changes and test
pytest

# Submit pull request
```

## 📄 License

This project is licensed under the MIT License - see `LICENSE` file for details.

## 📧 Support

- 📖 Documentation: [docs.ctrlhub.edu](https://docs.ctrlhub.edu)
- 💬 Community: [discord.gg/ctrlhub](https://discord.gg/ctrlhub)
- 🐛 Issues: [GitHub Issues](https://github.com/ctrlhub/issues)
- 📧 Email: support@ctrlhub.edu

---

**Happy Learning! 🎓⚡🤖**
