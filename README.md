# 🎛️ CtrlHub - Control Systems Education Platform

**Professional Control Systems Education Platform with Hybrid Architecture**

A comprehensive educational hub for learning control systems from first principles, featuring real hardware integration and sophisticated simulation capabilities.

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    STUDENT'S COMPUTER                       │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │  React Frontend │    │    Python Local Agent          │ │
│  │  (Browser)      │    │  (Desktop Application)         │ │
│  │                 │◄──►│                                 │ │
│  │ - Beautiful UI  │    │ - Hardware Communication       │ │
│  │ - Web Serial    │    │ - Complex Simulations          │ │
│  │ - Simple Sims   │    │ - MATLAB Model Translation     │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│           │                           │                    │
└───────────┼───────────────────────────┼────────────────────┘
            │                           │
            │                           │
┌───────────▼───────────────────────────▼────────────────────┐
│                  CLOUD BACKEND                             │
│              Educational Content Delivery                  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 **Repository Structure**

```
CtrlHub/
├── frontend/                    # React Web Application
│   ├── src/
│   │   ├── components/         # UI Components
│   │   ├── utils/              # Communication Handlers
│   │   └── assets/             # Styling & Resources
│   └── package.json
├── local_agent/                 # Python Desktop Application
│   ├── main.py                 # Entry point & GUI
│   ├── hardware/               # Arduino communication
│   ├── models/                 # Control system models
│   ├── simulations/            # Simulation engine
│   ├── gui/                    # Desktop interface
│   └── requirements.txt
├── cloud_backend/              # Optional Cloud Services
│   ├── content/                # Educational materials
│   └── api/                    # Content delivery API
├── arduino/                    # Arduino sketches
├── installer/                  # Desktop agent installers
│   ├── windows/               # Windows installer
│   ├── macos/                 # macOS installer
│   └── linux/                 # Linux installer
└── docs/                      # Documentation
```

## 🎯 **Key Features**

### **🔬 First Principles Learning**
- Derive motor models from basic electrical and mechanical equations
- Measure actual parameters through experimental methods
- Compare theoretical models with real hardware behavior

### **🛠️ Hands-On Hardware Integration**
- Students connect their own Arduino and motor setup
- Real-time control and data acquisition
- Hardware-in-the-loop validation

### **⚡ Hybrid Simulation Architecture**
- Simple simulations run in browser (JavaScript)
- Complex simulations run locally (Python)
- Best performance and capability for different use cases

### **📚 Progressive Learning Path**
- Coast-down tests for parameter identification
- Transfer function derivation and validation
- PID controller design (Ziegler-Nichols, Bode methods)
- Real-time control implementation

## 🚀 **Quick Start**

### **For Students:**

1. **Download CtrlHub Agent** (Desktop app)
   ```bash
   # Download from releases or install via pip
   pip install ctrlhub-agent
   ```

2. **Start the Agent**
   ```bash
   ctrlhub-agent
   ```

3. **Open Web Interface**
   - Visit: `http://localhost:3000`
   - Connect your Arduino
   - Start learning!

### **For Developers:**

1. **Clone Repository**
   ```bash
   git clone https://github.com/Piyushiitk24/CtrlHub.git
   cd CtrlHub
   ```

2. **Setup Local Agent**
   ```bash
   cd local_agent
   pip install -r requirements.txt
   python main.py
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 🎓 **Educational Philosophy**

This platform follows a **first-principles approach** to control systems education:

1. **🔍 Fundamental Understanding**: Start with basic physics and mathematics
2. **📊 Experimental Validation**: Measure parameters through hands-on experiments
3. **🧮 Mathematical Modeling**: Derive models from measured data
4. **🎛️ Controller Design**: Apply classical control theory
5. **⚡ Real-time Implementation**: Test designs on actual hardware
6. **🔄 Iterative Improvement**: Refine understanding through experimentation

## 🛠️ **Hardware Requirements**

- **Arduino UNO/Mega** (USB connection)
- **DC Motor** (12V, with encoder preferred)
- **Motor Driver** (L298N or similar)
- **Power Supply** (12V, 2A minimum)
- **Breadboard & Jumper Wires**
- **Computer** (Windows/macOS/Linux)

## 📖 **Learning Modules**

### **Module 1: System Identification**
- DC motor parameter measurement
- Coast-down test analysis
- Resistance and inductance calculation
- Moment of inertia determination

### **Module 2: Mathematical Modeling**
- First-principles equation derivation
- Transfer function development
- State-space representation
- Frequency domain analysis

### **Module 3: Controller Design**
- PID controller fundamentals
- Ziegler-Nichols tuning method
- Bode plot analysis
- Root locus techniques

### **Module 4: Implementation & Validation**
- Real-time control implementation
- Hardware-software integration
- Performance analysis
- System optimization

## 🤝 **Contributing**

We welcome contributions from educators and developers! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- Built with modern web technologies (React, FastAPI, Python Control)
- Inspired by MIT and Stanford control systems curricula
- Designed for accessible, hands-on engineering education

---

**🎯 Mission**: Make professional-grade control systems education accessible to students worldwide through hands-on experimentation and first-principles learning via CtrlHub.