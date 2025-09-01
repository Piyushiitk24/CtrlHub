# CtrlHub DC Motor Parameter Extraction

## 🎯 Overview
The CtrlHub Parameter Extraction system allows you to measure real DC motor parameters using your Arduino hardware setup. No more relying on uncertain datasheets - extract actual values from your motor!

## 🔧 Hardware Requirements

### Required Components
- **Arduino Mega 2560** (or compatible)
- **12V DC Geared Motor** (300 RPM recommended)
- **L298N Motor Driver**
- **Quadrature Encoder** (600 PPR / 2400 CPR)
- **12V Power Supply**
- **Multimeter** (for resistance measurement)
- **LCR Meter** (for inductance measurement)

### Pin Configuration
```
Arduino Mega Pin Connections:
├── Motor Control
│   ├── Pin 9  → L298N ENA (PWM Speed Control)
│   ├── Pin 8  → L298N IN1 (Direction)
│   └── Pin 7  → L298N IN2 (Direction)
├── Encoder Inputs
│   ├── Pin 2  → Encoder A Signal (Interrupt)
│   └── Pin 3  → Encoder B Signal (Interrupt)
└── Power
    ├── 5V     → Encoder VCC
    └── GND    → Common Ground

L298N Connections:
├── VCC → 12V Power Supply (+)
├── GND → Common Ground
├── OUT1 → Motor Terminal 1
└── OUT2 → Motor Terminal 2

Encoder Connections:
├── VCC (Red)    → Arduino 5V
├── GND (Black)  → Common Ground
├── A (Green)    → Arduino Pin 2
└── B (White)    → Arduino Pin 3
```

## 💻 Software Setup

### 1. Install CtrlHub Local Agent

```bash
# Clone the repository
git clone <repository-url>
cd CtrlHub

# Set up Python virtual environment
python -m venv ctrlhub_env
source ctrlhub_env/bin/activate  # On macOS/Linux
# or
ctrlhub_env\Scripts\activate     # On Windows

# Install dependencies
cd local_agent
pip install -r requirements.txt
```

### 2. Upload Arduino Sketch

**✨ AUTOMATIC - No Arduino IDE Required!**

The CtrlHub system will automatically program your Arduino:

1. Navigate to: `http://localhost:3000/components/dc-motor/parameter-extraction`
2. Click **"Program Arduino"** button
3. System automatically:
   - Downloads and sets up Arduino CLI
   - Detects your Arduino Mega
   - Compiles the CtrlHub sketch
   - Uploads it to your Arduino

**Expected Result:** "Arduino programmed successfully!" in the log console

### 3. Start the System

```bash
# Terminal 1: Start Local Agent
cd local_agent
python main.py

# Terminal 2: Start Web Interface (in another terminal)
cd frontend
npm install
npm start
```

## 🧪 Parameter Extraction Process

### Phase 1: Resistance (R) and Inductance (L)
**Equipment:** Multimeter, LCR Meter

1. **Disconnect** the motor from the driver circuit
2. **Measure Resistance:**
   - Set multimeter to resistance mode (Ω)
   - Connect probes to motor terminals
   - Record value (typically 1-10 Ω)
3. **Measure Inductance:**
   - Connect LCR meter to motor terminals
   - Set frequency to 1 kHz
   - Record value in mH, convert to H

### Phase 2: Rotor Inertia (J) - Coast-Down Test
**Equipment:** Complete Arduino setup

**Procedure:**
1. Navigate to: `http://localhost:3000/components/dc-motor/parameter-extraction`
2. Ensure Arduino is connected (green status indicator)
3. Click **"Run Coast-Down Test"**
4. System automatically:
   - Accelerates motor for 4 seconds at full speed
   - Cuts power and logs deceleration for 8 seconds
   - Calculates inertia from speed decay slope

**Formula:** `J = -b × ω / (dω/dt)`

### Phase 3: Back-EMF (Ke) and Torque (Kt) Constants
**Equipment:** Arduino setup, Multimeter

**Procedure:**
1. Enter measured resistance value from Phase 1
2. Click **"Measure Back-EMF Constants"**
3. System runs motor at constant speed
4. Measures steady-state voltage and current
5. Calculates: `V_emf = V_supply - (I × R)`
6. Computes: `Ke = V_emf / ω` and `Kt = Ke`

### Phase 4: Viscous Damping (b) - Steady-State Test
**Equipment:** Arduino setup

**Procedure:**
1. System runs motor at constant, low speed
2. Measures steady-state current and speed
3. Calculates: `b = Kt × I_ss / ω_ss`

## 📊 Real-Time Data Visualization

The web interface provides:
- **Live connection status** indicators
- **Real-time speed plots** during tests
- **Parameter summary table** with all extracted values
- **Live log console** for monitoring test progress

## 🔍 Expected Parameter Ranges

| Parameter | Symbol | Typical Range | Units |
|-----------|---------|---------------|-------|
| Resistance | R | 1 - 10 | Ω |
| Inductance | L | 1 - 10 | mH |
| Inertia | J | 10⁻⁵ - 10⁻³ | kg⋅m² |
| Back-EMF Constant | Ke | 0.01 - 0.1 | V⋅s/rad |
| Torque Constant | Kt | 0.01 - 0.1 | N⋅m/A |
| Viscous Damping | b | 10⁻⁵ - 10⁻³ | N⋅m⋅s/rad |

## 🛠️ Troubleshooting

### Arduino Connection Issues
```bash
# Check available ports
ls /dev/cu.* | grep usb  # macOS
ls /dev/tty* | grep USB  # Linux
# Check Device Manager     # Windows
```

### Common Problems
1. **Arduino not detected:**
   - Check USB cable connection
   - Verify correct COM port selection
   - Ensure Arduino sketch is uploaded

2. **Motor not responding:**
   - Verify L298N power connections
   - Check motor driver jumper settings
   - Confirm pin connections match code

3. **Encoder issues:**
   - Verify interrupt pin connections (2, 3)
   - Check encoder power supply (5V)
   - Ensure proper grounding

4. **Web interface not loading:**
   - Confirm local agent is running on port 8003
   - Check React app is running on port 3000
   - Verify no firewall blocking connections

## 📈 Using Extracted Parameters

Once you have all parameters, you can:

1. **Create Simulink models** with accurate transfer functions
2. **Design control systems** (PID, state-space, etc.)
3. **Predict motor behavior** under different loads
4. **Optimize performance** for specific applications

### Example: Creating Transfer Function
```matlab
% In MATLAB/Simulink
s = tf('s');
R = 2.5;      % Your measured resistance
L = 0.003;    % Your measured inductance  
Kt = 0.015;   % Your measured torque constant
Ke = 0.015;   % Your measured back-EMF constant
J = 0.0001;   % Your measured inertia
b = 0.0005;   % Your measured damping

% Motor transfer function: ω(s)/V(s)
H = Kt / ((J*s + b)*(L*s + R) + Kt*Ke);
```

## 🎓 Educational Value

This system teaches:
- **First-principles motor modeling**
- **Parameter identification techniques** 
- **Real-time data acquisition**
- **Hardware-software integration**
- **Control systems fundamentals**

## 📝 Data Export

Extracted parameters can be:
- **Copied** from the summary table
- **Exported** to JSON format
- **Used directly** in simulation software
- **Saved** for future reference

## 🔄 Iterative Improvement

For better accuracy:
1. **Repeat measurements** multiple times
2. **Average results** for consistency
3. **Validate** with different test conditions
4. **Cross-check** with theoretical calculations

## 🏆 Success Criteria

You'll know the extraction is successful when:
- ✅ All parameters are within expected ranges
- ✅ Measurements are repeatable (±5% variation)
- ✅ Simulated behavior matches real motor response
- ✅ Control systems designed with these parameters work effectively

## 📞 Support

If you encounter issues:
1. Check the **live logs** in the web interface
2. Verify **hardware connections** against the pin diagram
3. Ensure **Arduino sketch** is properly uploaded
4. Confirm **all dependencies** are installed

---

**Happy Parameter Hunting! 🔍⚙️**

*Remember: These are YOUR motor's real parameters - not some generic datasheet values. Use them with confidence!*
