
import React, { useState, useEffect, useRef } from 'react';
import LocalAgentHandler from '../../../utils/LocalAgentHandler';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import 'katex/dist/katex.min.css';
import { InlineMath } from 'react-katex';
import './ParameterExtraction.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TestData {
  time: number;
  speed: number;
  current?: number;
  voltage?: number;
}

interface MotorParameters {
  R: number | null;  // Resistance (Ohms)
  L: number | null;  // Inductance (Henry)
  J: number | null;  // Inertia (kg⋅m²)
  Kt: number | null; // Torque constant (Nm/A)
  Ke: number | null; // Back-EMF constant (V⋅s/rad)
  b: number | null;  // Viscous friction (N⋅m⋅s/rad)
}

const ParameterExtraction: React.FC = () => {
  const [agent] = useState(new LocalAgentHandler());
  const [isConnected, setIsConnected] = useState(false);
  const [arduinoConnected, setArduinoConnected] = useState(false);
  const [testRunning, setTestRunning] = useState(false);
  const [currentTest, setCurrentTest] = useState<string | null>(null);
  const [testData, setTestData] = useState<TestData[]>([]);
  const [parameters, setParameters] = useState<MotorParameters>({
    R: null, L: null, J: null, Kt: null, Ke: null, b: null
  });
  const [logs, setLogs] = useState<string[]>([]);
  const [simulationMode, setSimulationMode] = useState(false);
  const [pidGains, setPidGains] = useState({ kp: 1.0, ki: 0.1, kd: 0.05 });
  const [testInputType, setTestInputType] = useState<'step' | 'ramp' | 'sine'>('step');
  const [testInputValue, setTestInputValue] = useState(1.0);
  const [bodeData, setBodeData] = useState<any>(null);
  const [controlMode, setControlMode] = useState<'open' | 'closed'>('open');

  useEffect(() => { 
    document.title = 'DC Motor — Parameter Extraction — CtrlHub'; 
    checkAgentConnection();
  }, []);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `${timestamp}: ${message}`]);
  };

  // Enhanced input handler that supports all numeric formats including decimals, exponentials, negatives
  const handleNumericInput = (value: string, setter: (val: number | null) => void) => {
    // Always allow the display of what user is typing
    if (value === '' || value === '-' || value === '.' || value === '0.') {
      // Don't update the parameter for incomplete inputs
      return;
    }
    
    // Allow partial exponential notation like "1e", "1e-", "1e-3"
    if (value.match(/^-?\d*\.?\d*e?-?\d*$/i)) {
      const parsed = parseFloat(value);
      if (!isNaN(parsed) && isFinite(parsed)) {
        setter(parsed);
      }
      return;
    }
    
    // For other cases, try to parse as number
    const parsed = parseFloat(value);
    if (!isNaN(parsed) && isFinite(parsed)) {
      setter(parsed);
    }
  };

  const checkAgentConnection = async () => {
    try {
      const connected = await agent.checkLocalAgent();
      setIsConnected(connected);
      if (connected) {
        addLog('✅ Local agent connected');
        checkArduinoConnection();
      } else {
        addLog('❌ Local agent disconnected');
      }
    } catch (error) {
      setIsConnected(false);
      addLog('❌ Failed to connect to local agent');
    }
  };

  const checkArduinoConnection = async () => {
    try {
      const result = await agent.scanArduino();
      if (result.success && result.availablePorts.length > 0) {
        setArduinoConnected(result.connected);
        if (result.connected) {
          addLog(`✅ Arduino connected on ${result.connectedPort}`);
        } else {
          addLog(`🔍 Arduino detected on ${result.availablePorts[0]}`);
        }
      } else {
        setArduinoConnected(false);
        addLog('❌ No Arduino detected');
      }
    } catch (error) {
      setArduinoConnected(false);
      addLog('❌ Failed to scan for Arduino');
    }
  };

  const programArduino = async () => {
    try {
      setTestRunning(true);
      addLog('🔧 Setting up Arduino environment...');
      
      // First setup Arduino CLI
      const setupResult = await agent.setupArduinoEnvironment();
      if (!setupResult.success) {
        addLog(`❌ Arduino setup failed: ${setupResult.error}`);
        return;
      }
      addLog('✅ Arduino environment ready');

      // Detect Arduino
      addLog('🔍 Detecting Arduino...');
      const detectResult = await agent.detectArduino();
      if (!detectResult.success || detectResult.ports.length === 0) {
        addLog('❌ No Arduino found. Please connect your Arduino Mega.');
        return;
      }
      addLog(`✅ Arduino found on ${detectResult.ports[0]}`);

      // Program Arduino
      addLog('📤 Programming Arduino with CtrlHub sketch...');
      const programResult = await agent.programArduino();
      if (programResult.success) {
        addLog('✅ Arduino programmed successfully!');
        addLog('🎉 Ready for parameter extraction tests');
        
        // Check connection after programming
        setTimeout(checkArduinoConnection, 2000);
      } else {
        addLog(`❌ Programming failed: ${programResult.message}`);
      }
    } catch (error) {
      addLog(`❌ Programming error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setTestRunning(false);
    }
  };

  const connectArduino = async () => {
    try {
      addLog('🔌 Connecting to Arduino...');
      const result = await agent.connectArduino();
      if (result.success) {
        setArduinoConnected(true);
        addLog(`✅ Arduino connected on ${result.port}`);
      } else {
        addLog(`❌ Failed to connect: ${result.error}`);
      }
    } catch (error) {
      addLog('❌ Connection error');
    }
  };

  const runSteadyStateTest = async () => {
    if (!simulationMode && !arduinoConnected) {
      addLog('❌ Hardware mode: Arduino not connected');
      return;
    }

    setTestRunning(true);
    setCurrentTest('steady-state');
    setTestData([]);
    addLog('📊 Starting steady-state test...');

    try {
      const result = await agent.runDCMotorSimulation({
        testType: 'steady-state',
        duration: 10000,
        motorSpeed: testInputValue * 100,
        simulationMode,
        sampleRate: 100
      });

      if (result.success && result.data) {
        const processedData = result.data.map((point: any) => ({
          time: point.time / 1000,
          speed: point.speed,
          current: point.current,
          voltage: point.voltage
        }));
        setTestData(processedData);
        addLog('✅ Steady-state test completed');
        
        // Calculate steady-state parameters
        const steadyStateSpeed = processedData[processedData.length - 1].speed;
        const steadyStateCurrent = processedData[processedData.length - 1].current;
        addLog(`📊 Steady-state speed: ${steadyStateSpeed.toFixed(1)} RPM`);
        addLog(`📊 Steady-state current: ${steadyStateCurrent.toFixed(2)} A`);
      }
    } catch (error) {
      addLog('❌ Steady-state test error');
    } finally {
      setTestRunning(false);
      setCurrentTest(null);
    }
  };

  const runOpenLoopTest = async () => {
    if (!simulationMode && !arduinoConnected) {
      addLog('❌ Hardware mode: Arduino not connected');
      return;
    }

    setTestRunning(true);
    setCurrentTest('open-loop');
    setTestData([]);
    addLog(`🔓 Starting open-loop ${testInputType} test...`);

    try {
      const result = await agent.runDCMotorSimulation({
        testType: 'open-loop',
        inputType: testInputType,
        inputValue: testInputValue,
        duration: 8000,
        simulationMode,
        sampleRate: 50
      });

      if (result.success && result.data) {
        const processedData = result.data.map((point: any) => ({
          time: point.time / 1000,
          speed: point.speed,
          voltage: point.voltage
        }));
        setTestData(processedData);
        addLog('✅ Open-loop test completed');
      }
    } catch (error) {
      addLog('❌ Open-loop test error');
    } finally {
      setTestRunning(false);
      setCurrentTest(null);
    }
  };

  const runClosedLoopTest = async () => {
    if (!simulationMode && !arduinoConnected) {
      addLog('❌ Hardware mode: Arduino not connected');
      return;
    }

    setTestRunning(true);
    setCurrentTest('closed-loop');
    setTestData([]);
    addLog(`🔒 Starting closed-loop PID test (Kp=${pidGains.kp}, Ki=${pidGains.ki}, Kd=${pidGains.kd})...`);

    try {
      const result = await agent.runDCMotorSimulation({
        testType: 'closed-loop',
        pidGains,
        targetSpeed: testInputValue * 100,
        duration: 10000,
        simulationMode,
        sampleRate: 50
      });

      if (result.success && result.data) {
        const processedData = result.data.map((point: any) => ({
          time: point.time / 1000,
          speed: point.speed,
          voltage: point.voltage
        }));
        setTestData(processedData);
        addLog('✅ Closed-loop PID test completed');
        
        // Calculate performance metrics
        const settlingTime = calculateSettlingTime(processedData);
        const overshoot = calculateOvershoot(processedData);
        addLog(`📊 Settling time: ${settlingTime.toFixed(2)} s`);
        addLog(`📊 Overshoot: ${overshoot.toFixed(1)}%`);
      }
    } catch (error) {
      addLog('❌ Closed-loop test error');
    } finally {
      setTestRunning(false);
      setCurrentTest(null);
    }
  };

  const generateBodePlot = async () => {
    if (!parameters.R || !parameters.L || !parameters.J) {
      addLog('❌ Need R, L, and J parameters for Bode plot');
      return;
    }

    addLog('📈 Generating Bode plot...');
    
    try {
      // Placeholder for Bode plot generation
      // TODO: Implement Bode plot generation in LocalAgentHandler
      const simulatedBodeData = {
        frequencies: [0.1, 1, 10, 100, 1000],
        magnitude: [40, 20, 0, -20, -40],
        phase: [-90, -135, -180, -225, -270]
      };
      
      setBodeData(simulatedBodeData);
      addLog('✅ Bode plot generated (simulation)');
      addLog('📊 Note: This is a placeholder. Full implementation pending.');
    } catch (error) {
      addLog('❌ Bode plot generation error');
    }
  };

  const calculateSettlingTime = (data: TestData[]): number => {
    if (data.length < 10) return 0;
    const targetSpeed = testInputValue * 100;
    const tolerance = targetSpeed * 0.02; // 2% tolerance
    
    for (let i = data.length - 1; i >= 0; i--) {
      if (Math.abs(data[i].speed - targetSpeed) > tolerance) {
        return data[i + 1]?.time || data[data.length - 1].time;
      }
    }
    return data[data.length - 1].time;
  };

  const calculateOvershoot = (data: TestData[]): number => {
    if (data.length < 10) return 0;
    const targetSpeed = testInputValue * 100;
    const maxSpeed = Math.max(...data.map(d => d.speed));
    return ((maxSpeed - targetSpeed) / targetSpeed) * 100;
  };

  const runCoastDownTest = async () => {
    if (!simulationMode && !arduinoConnected) {
      addLog('❌ Hardware mode: Arduino not connected');
      return;
    }

    setTestRunning(true);
    setCurrentTest('coast-down');
    setTestData([]);
    addLog('🚀 Starting coast-down test...');

    try {
      // Start the test through the local agent
      const result = await agent.runDCMotorSimulation({
        testType: 'coast-down',
        duration: 12000, // 12 seconds total (4s accel + 8s logging)
        motorSpeed: 255,
        simulationMode,
        sampleRate: 50 // 50ms intervals
      });

      if (result.success) {
        addLog('✅ Coast-down test completed');
        // Process the results
        if (result.data) {
          const processedData = result.data.map((point: any) => ({
            time: point.time / 1000, // Convert to seconds
            speed: point.speed
          }));
          setTestData(processedData);
          
          // Calculate inertia from the coast-down data
          calculateInertia(processedData);
        }
      } else {
        addLog(`❌ Test failed: ${result.error}`);
      }
    } catch (error) {
      addLog('❌ Test execution error');
    } finally {
      setTestRunning(false);
      setCurrentTest(null);
    }
  };

  const calculateInertia = (data: TestData[]) => {
    if (data.length < 10) return;

    // Find the coast-down portion (after motor is turned off)
    const coastStartIndex = data.findIndex(point => point.time > 4); // After 4s acceleration
    const coastData = data.slice(coastStartIndex);

    if (coastData.length < 5) return;

    // Calculate deceleration slope (dω/dt)
    const timePoints = coastData.map(p => p.time);
    const speedPoints = coastData.map(p => p.speed * 2 * Math.PI / 60); // Convert RPM to rad/s

    // Linear regression to find slope
    const n = timePoints.length;
    const sumX = timePoints.reduce((sum, t) => sum + t, 0);
    const sumY = speedPoints.reduce((sum, s) => sum + s, 0);
    const sumXY = timePoints.reduce((sum, t, i) => sum + t * speedPoints[i], 0);
    const sumX2 = timePoints.reduce((sum, t) => sum + t * t, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    
    // For a coast-down test: J * dω/dt = -b * ω
    // We need to estimate viscous friction coefficient b first
    // For now, use a typical value or previous measurement
    const estimatedB = 0.001; // This should be measured from steady-state test
    
    // J = -b * ω / (dω/dt)
    const avgSpeed = speedPoints.reduce((sum, s) => sum + s, 0) / speedPoints.length;
    const calculatedJ = -estimatedB * avgSpeed / slope;

    setParameters(prev => ({ ...prev, J: Math.abs(calculatedJ) }));
    addLog(`📊 Calculated inertia: ${Math.abs(calculatedJ).toExponential(3)} kg⋅m²`);
  };

  const measureBackEMF = async () => {
    if (!simulationMode && !arduinoConnected) {
      addLog('❌ Hardware mode: Arduino not connected');
      return;
    }

    addLog('🔋 Starting back-EMF measurement...');
    
    try {
      // Run motor at constant speed and measure voltage and current
      const result = await agent.runDCMotorSimulation({
        testType: 'back-emf',
        duration: 5000,
        motorSpeed: 200,
        simulationMode,
        sampleRate: 100
      });

      if (result.success && result.data) {
        const V_supply = 12; // Assuming 12V supply
        const I_measured = result.data[result.data.length - 1].current || 0.6;
        const omega = result.data[result.data.length - 1].speed * 2 * Math.PI / 60;
        
        const R = parameters.R || 2.5;
        const V_emf = V_supply - (I_measured * R);
        const Ke = V_emf / omega;
        const Kt = Ke; // For SI units, Kt = Ke
        
        setParameters(prev => ({ ...prev, Ke, Kt }));
        addLog(`📊 Back-EMF: ${V_emf.toFixed(2)} V`);
        addLog(`📊 Ke (Back-EMF constant): ${Ke.toFixed(4)} V⋅s/rad`);
        addLog(`📊 Kt (Torque constant): ${Kt.toFixed(4)} N⋅m/A`);
      }
    } catch (error) {
      addLog('❌ Back-EMF measurement error');
    }
  };

  // Chart data for real-time plotting
  const chartData = {
    labels: testData.map(point => point.time.toFixed(1)),
    datasets: [
      {
        label: 'Speed (RPM)',
        data: testData.map(point => point.speed),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: currentTest === 'coast-down' ? 'Coast-Down Test: Speed vs Time' : 'Motor Speed Response'
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Time (s)'
        }
      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Speed (RPM)'
        }
      }
    }
  };

  return (
    <div className="parameter-extraction-page">
      <h1>DC Motor Parameter Extraction</h1>
      <p className="intro-text">
        Extract real motor parameters from your hardware setup. Connect your Arduino with the L298N driver, 
        encoder, and DC motor to measure actual values without relying on uncertain datasheets.
      </p>

      {/* Connection Status */}
      <div className="connection-status">
        <h2 className="connection-status-title">System Status</h2>
        
        {/* Simulation Mode Toggle */}
        <div className="simulation-mode-section">
          <div className="mode-toggle">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={simulationMode}
                onChange={(e) => setSimulationMode(e.target.checked)}
              />
              <span className="toggle-switch"></span>
              <span className="toggle-text">
                {simulationMode ? '🔬 Simulation Mode' : '🔧 Hardware Mode'}
              </span>
            </label>
          </div>
          <div className="mode-description">
            {simulationMode ? (
              <p>✅ Running in simulation mode - no hardware required. All tests use mathematical models.</p>
            ) : (
              <p>🔌 Hardware mode - requires Arduino connection for real motor testing.</p>
            )}
          </div>
        </div>

        <div className="status-grid">
          <div className={`status-card ${isConnected ? 'status-connected' : 'status-disconnected'}`}>
            <div className="status-icon">
              {isConnected ? '✅' : '❌'}
            </div>
            <div className="status-info">
              <div className="status-label">Local Agent</div>
              <div className="status-value">{isConnected ? 'Connected' : 'Disconnected'}</div>
            </div>
          </div>
          
          <div className={`status-card ${arduinoConnected || simulationMode ? 'status-connected' : 'status-disconnected'}`}>
            <div className="status-icon">
              {simulationMode ? '🔬' : (arduinoConnected ? '🔌' : '⚡')}
            </div>
            <div className="status-info">
              <div className="status-label">{simulationMode ? 'Simulation' : 'Arduino'}</div>
              <div className="status-value">
                {simulationMode ? 'Active' : (arduinoConnected ? 'Connected' : 'Disconnected')}
              </div>
            </div>
          </div>
        </div>
        
        <div className="action-buttons">
          {!isConnected && (
            <button onClick={checkAgentConnection} className="btn btn-primary">
              Reconnect Agent
            </button>
          )}
          
          {isConnected && !arduinoConnected && !simulationMode && (
            <div className="arduino-setup-buttons">
              <button 
                onClick={programArduino} 
                className="btn btn-secondary"
                disabled={testRunning}
              >
                {testRunning ? 'Programming...' : 'Program Arduino'}
              </button>
              <button onClick={connectArduino} className="btn btn-primary">
                Connect Arduino
              </button>
            </div>
          )}

          {!simulationMode && !arduinoConnected && (
            <div className="hardware-warning">
              <p>⚠️ Hardware mode requires Arduino connection. Switch to simulation mode or connect hardware.</p>
            </div>
          )}
        </div>
      </div>

      {/* Test Sections */}
      <div className="test-sections">
        
        {/* 1. Resistance and Inductance */}
        <div className="test-section">
          <h2>1. Resistance (R) and Inductance (L) Measurement</h2>
          <div className="theory-box">
            <h3>📚 Theory</h3>
            <p>
              <strong>Resistance (R):</strong> The opposition to current flow in the motor windings. 
              Measured using a multimeter in ohms (Ω). Typical range: 1-10Ω for small DC motors.
            </p>
            <p>
              <strong>Inductance (L):</strong> The ability of the motor windings to store magnetic energy. 
              Measured using an LCR meter in henries (H). Typical range: 1-10mH for small DC motors.
            </p>
            <p><strong>Method:</strong> Use a multimeter for resistance and an LCR meter for inductance measurements.</p>
          </div>
          
          <div className="measurement-inputs">
            <div className="input-group">
              <label>Resistance (Ω):</label>
              <input 
                type="text" 
                defaultValue={parameters.R !== null ? parameters.R.toString() : ''} 
                onBlur={(e) => handleNumericInput(e.target.value, (val) => setParameters(prev => ({...prev, R: val})))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleNumericInput(e.currentTarget.value, (val) => setParameters(prev => ({...prev, R: val})));
                  }
                }}
                placeholder="e.g., 1.415, 2.5, 0.003, 1e-3"
              />
            </div>
            <div className="input-group">
              <label>Inductance (H):</label>
              <input 
                type="text" 
                defaultValue={parameters.L !== null ? parameters.L.toString() : ''} 
                onBlur={(e) => handleNumericInput(e.target.value, (val) => setParameters(prev => ({...prev, L: val})))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleNumericInput(e.currentTarget.value, (val) => setParameters(prev => ({...prev, L: val})));
                  }
                }}
                placeholder="e.g., 0.003, 1e-3, -0.001, 5.2e-4"
              />
            </div>
          </div>
        </div>

        {/* Manual Parameter Input Section */}
        <div className="test-section">
          <h2>🎛️ Manual Parameter Input (For Simulation)</h2>
          <div className="theory-box">
            <h3>⚡ Direct Parameter Entry</h3>
            <p>
              <strong>For simulation mode:</strong> Enter known motor parameters directly to run control 
              system tests without hardware measurements. Use typical values or datasheet specifications.
            </p>
          </div>
          
          <div className="measurement-inputs">
            <div className="input-group">
              <label>Inertia J (kg⋅m²):</label>
              <input 
                type="text" 
                defaultValue={parameters.J !== null ? parameters.J.toString() : ''} 
                onBlur={(e) => handleNumericInput(e.target.value, (val) => setParameters(prev => ({...prev, J: val})))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleNumericInput(e.currentTarget.value, (val) => setParameters(prev => ({...prev, J: val})));
                  }
                }}
                placeholder="e.g., 1e-6, 0.0001, 5.2e-5"
              />
            </div>
            <div className="input-group">
              <label>Torque Constant Kt (Nm/A):</label>
              <input 
                type="text" 
                defaultValue={parameters.Kt !== null ? parameters.Kt.toString() : ''} 
                onBlur={(e) => handleNumericInput(e.target.value, (val) => setParameters(prev => ({...prev, Kt: val})))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleNumericInput(e.currentTarget.value, (val) => setParameters(prev => ({...prev, Kt: val})));
                  }
                }}
                placeholder="e.g., 0.01, 0.05, 1e-2"
              />
            </div>
            <div className="input-group">
              <label>Back-EMF Constant Ke (V⋅s/rad):</label>
              <input 
                type="text" 
                defaultValue={parameters.Ke !== null ? parameters.Ke.toString() : ''} 
                onBlur={(e) => handleNumericInput(e.target.value, (val) => setParameters(prev => ({...prev, Ke: val})))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleNumericInput(e.currentTarget.value, (val) => setParameters(prev => ({...prev, Ke: val})));
                  }
                }}
                placeholder="e.g., 0.01, 0.05, 1e-2"
              />
            </div>
            <div className="input-group">
              <label>Friction Coefficient b (N⋅m⋅s/rad):</label>
              <input 
                type="text" 
                defaultValue={parameters.b !== null ? parameters.b.toString() : ''} 
                onBlur={(e) => handleNumericInput(e.target.value, (val) => setParameters(prev => ({...prev, b: val})))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleNumericInput(e.currentTarget.value, (val) => setParameters(prev => ({...prev, b: val})));
                  }
                }}
                placeholder="e.g., 1e-6, 0.0001, 5e-5"
              />
            </div>
          </div>
          
          <button 
            onClick={() => {
              // Set typical small DC motor values for quick testing
              setParameters({
                R: 2.0,      // 2 ohms
                L: 0.003,    // 3 mH
                J: 1e-5,     // 10 μkg⋅m²
                Kt: 0.01,    // 10 mNm/A
                Ke: 0.01,    // 10 mV⋅s/rad
                b: 1e-5      // 10 μN⋅m⋅s/rad
              });
            }}
            className="btn btn-secondary"
            style={{marginTop: '10px'}}
          >
            🎯 Load Typical Small DC Motor Parameters
          </button>
        </div>

        {/* 2. Rotor Inertia */}
        <div className="test-section">
          <h2>2. Rotor Inertia (J) - Coast-Down Test</h2>
          <div className="theory-box">
            <h3>📚 Theory</h3>
            <p>
              <strong>Rotor Inertia (J):</strong> The resistance of the motor rotor to angular acceleration. 
              For a geared DC motor, this includes both the motor inertia and the reflected load inertia.
            </p>
            <p>
              <strong>Coast-Down Test:</strong> Accelerate the motor to a steady speed, then cut power and 
              measure the deceleration. The slope of speed vs time gives us the angular deceleration.
            </p>
            <p><strong>Equation:</strong> <InlineMath math="J = -b \times \omega / (d\omega/dt)" /></p>
          </div>

          <div className="test-controls">
            <button 
              onClick={runCoastDownTest} 
              className="btn btn-success btn-large"
              disabled={(!arduinoConnected && !simulationMode) || testRunning}
            >
              {testRunning && currentTest === 'coast-down' ? '🔄 Running...' : '🚀 Run Coast-Down Test'}
            </button>
            <div className="test-info">
              <p><strong>Test Sequence:</strong></p>
              <ol>
                <li>Motor accelerates for 4 seconds at full speed</li>
                <li>Power is cut, motor coasts down</li>
                <li>Speed is logged for 8 seconds</li>
                <li>Inertia is calculated from deceleration slope</li>
              </ol>
            </div>
          </div>

          {parameters.J && (
            <div className="result-box">
              <h4>📊 Calculated Inertia:</h4>
              <p><strong>J = {parameters.J.toExponential(3)} kg⋅m²</strong></p>
            </div>
          )}
        </div>

        {/* 3. Back-EMF and Torque Constants */}
        <div className="test-section">
          <h2>3. Back-EMF (<InlineMath math="K_e" />) and Torque (<InlineMath math="K_t" />) Constants</h2>
          <div className="theory-box">
            <h3>📚 Theory</h3>
            <p>
              <strong>Back-EMF Constant (Ke):</strong> Voltage generated per unit angular velocity. 
              <strong>Torque Constant (Kt):</strong> Torque produced per unit current.
            </p>
            <p><strong>Relationship:</strong> In SI units, <InlineMath math="K_t = K_e" /> (fundamental principle)</p>
            <p><strong>Method:</strong> Measure voltage in parallel and current in series while motor runs at constant speed.</p>
            <p><strong>Equation:</strong> <InlineMath math="V_{emf} = V_{supply} - (I \times R)" />, then <InlineMath math="K_e = V_{emf} / \omega" /></p>
          </div>

          <div className="measurement-steps">
            <h4>📋 Measurement Steps:</h4>
            <ol>
              <li>Connect multimeter in series to measure current</li>
              <li>Connect voltmeter in parallel to measure terminal voltage</li>
              <li>Run motor at constant speed</li>
              <li>Record steady-state values</li>
              <li>Calculate: V_emf = V_supply - (I × R)</li>
            </ol>
          </div>

          <button 
            onClick={measureBackEMF} 
            className="btn btn-primary"
            disabled={(!arduinoConnected && !simulationMode) || !parameters.R}
          >
            ⚡ Measure Back-EMF Constants
          </button>

          {(parameters.Ke || parameters.Kt) && (
            <div className="result-box">
              <h4>📊 Calculated Constants:</h4>
              {parameters.Ke && <p><strong>Ke = {parameters.Ke.toFixed(4)} V⋅s/rad</strong></p>}
              {parameters.Kt && <p><strong>Kt = {parameters.Kt.toFixed(4)} N⋅m/A</strong></p>}
            </div>
          )}
        </div>

        {/* 4. Steady-State Testing */}
        <div className="test-section">
          <h2>4. Steady-State Response Testing</h2>
          <div className="theory-box">
            <h3>📚 Theory</h3>
            <p>
              <strong>Steady-State Analysis:</strong> Analyze motor behavior at constant operating conditions.
              Helps determine viscous friction coefficient and validate motor equations.
            </p>
            <p><strong>Method:</strong> Apply constant voltage, measure steady-state speed and current.</p>
            <p><strong>Analysis:</strong> <InlineMath math="V_{steady} = I_{steady} \times R + K_e \times \omega_{steady}" /></p>
          </div>

          <div className="test-input-controls">
            <div className="input-group">
              <label>Test Voltage (V):</label>
              <input 
                type="text" 
                defaultValue={testInputValue.toString()}
                onBlur={(e) => handleNumericInput(e.target.value, (val) => setTestInputValue(val || 1.0))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleNumericInput(e.currentTarget.value, (val) => setTestInputValue(val || 1.0));
                  }
                }}
                placeholder="e.g., 1.0, -12, 0.003, 1e-2"
              />
            </div>
          </div>

          <button 
            onClick={runSteadyStateTest} 
            className="btn btn-info"
            disabled={(!arduinoConnected && !simulationMode) || testRunning}
          >
            {testRunning && currentTest === 'steady-state' ? '🔄 Running...' : '📊 Run Steady-State Test'}
          </button>
        </div>

        {/* 5. Open-Loop Control Testing */}
        <div className="test-section">
          <h2>5. Open-Loop Control Testing</h2>
          <div className="theory-box">
            <h3>📚 Theory</h3>
            <p>
              <strong>Open-Loop Control:</strong> System without feedback. Input directly controls motor voltage.
              Essential for understanding system limitations and the need for feedback control.
            </p>
            <p><strong>Test Inputs:</strong> Step, ramp, or sinusoidal voltage commands</p>
          </div>

          <div className="test-input-controls">
            <div className="input-group">
              <label>Input Type:</label>
              <select 
                value={testInputType} 
                onChange={(e) => setTestInputType(e.target.value as 'step' | 'ramp' | 'sine')}
              >
                <option value="step">Step Input</option>
                <option value="ramp">Ramp Input</option>
                <option value="sine">Sine Wave Input</option>
              </select>
            </div>
            <div className="input-group">
              <label>Input Amplitude:</label>
              <input 
                type="text" 
                value={testInputValue.toString()} 
                onChange={(e) => handleNumericInput(e.target.value, (val) => setTestInputValue(val || 1.0))}
                placeholder="e.g., 1.0, -10, 0.5, 2e-1"
              />
            </div>
          </div>

          <button 
            onClick={runOpenLoopTest} 
            className="btn btn-warning"
            disabled={(!arduinoConnected && !simulationMode) || testRunning}
          >
            {testRunning && currentTest === 'open-loop' ? '🔄 Running...' : '🔓 Run Open-Loop Test'}
          </button>
        </div>

        {/* 6. Closed-Loop PID Control Testing */}
        <div className="test-section">
          <h2>6. Closed-Loop PID Control Testing</h2>
          <div className="theory-box">
            <h3>📚 Theory</h3>
            <p>
              <strong>PID Control:</strong> Proportional-Integral-Derivative feedback control for precise speed regulation.
              Essential for rejecting disturbances and maintaining accurate speed control.
            </p>
            <p><strong>Control Law:</strong> <InlineMath math="u(t) = K_p e(t) + K_i \int e(t)dt + K_d \frac{de(t)}{dt}" /></p>
          </div>

          <div className="pid-controls">
            <div className="pid-gains-grid">
              <div className="input-group">
                <label>Kp (Proportional):</label>
                <input 
                  type="text" 
                  value={pidGains.kp} 
                  placeholder="0.01, 1.5, -2.3, 1e-2"
                  onChange={(e) => handleNumericInput(e.target.value, (val) => setPidGains(prev => ({...prev, kp: val || 0})))}
                />
              </div>
              <div className="input-group">
                <label>Ki (Integral):</label>
                <input 
                  type="text" 
                  value={pidGains.ki} 
                  placeholder="0.001, 0.01, 1e-3"
                  onChange={(e) => handleNumericInput(e.target.value, (val) => setPidGains(prev => ({...prev, ki: val || 0})))}
                />
              </div>
              <div className="input-group">
                <label>Kd (Derivative):</label>
                <input 
                  type="text" 
                  value={pidGains.kd} 
                  placeholder="0.001, 0.01, 1e-4"
                  onChange={(e) => handleNumericInput(e.target.value, (val) => setPidGains(prev => ({...prev, kd: val || 0})))}
                />
              </div>
            </div>
            <div className="input-group">
              <label>Target Speed (RPM):</label>
              <input 
                type="text" 
                value={testInputValue * 100} 
                placeholder="100, -500, 1.5e2"
                onChange={(e) => handleNumericInput(e.target.value, (val) => setTestInputValue((val || 100) / 100))}
              />
            </div>
          </div>

          <button 
            onClick={runClosedLoopTest} 
            className="btn btn-success"
            disabled={(!arduinoConnected && !simulationMode) || testRunning}
          >
            {testRunning && currentTest === 'closed-loop' ? '🔄 Running...' : '🔒 Run Closed-Loop PID Test'}
          </button>
        </div>

        {/* 7. Frequency Domain Analysis */}
        <div className="test-section">
          <h2>7. Bode Plot & Frequency Analysis</h2>
          <div className="theory-box">
            <h3>📚 Theory</h3>
            <p>
              <strong>Bode Plot:</strong> Frequency domain representation showing magnitude and phase response.
              Essential for understanding system stability, bandwidth, and control design.
            </p>
            <p><strong>Transfer Function:</strong> <InlineMath math="G(s) = \frac{K_t}{s(Js + b)(Ls + R) + K_tK_e}" /></p>
          </div>

          <button 
            onClick={generateBodePlot} 
            className="btn btn-primary"
            disabled={!parameters.R || !parameters.L || !parameters.J}
          >
            📈 Generate Bode Plot
          </button>

          <div className="bode-requirements">
            <p><strong>Requirements:</strong> Need R, L, and J parameters extracted first</p>
          </div>
        </div>
      </div>

      {/* Real-time Chart */}
      {testData.length > 0 && (
        <div className="chart-section">
          <h3>📈 Real-time Data</h3>
          <Line data={chartData} options={chartOptions} />
        </div>
      )}

      {/* Control System Block Diagrams */}
      <div className="block-diagram-section">
        <h3>🔗 Control System Block Diagrams</h3>
        
        {/* Open-Loop Block Diagram */}
        <div className="block-diagram">
          <h4>Open-Loop System</h4>
          <div className="diagram-container">
            <div className="block-diagram-flow">
              <div className="signal-line">
                <div className="signal-box input">
                  <span>Reference</span>
                  <span>r(t)</span>
                </div>
                <div className="arrow">→</div>
                <div className="signal-box plant">
                  <span>DC Motor Plant</span>
                  <span>G(s) = Kt/(s(Js+b)(Ls+R)+KtKe)</span>
                </div>
                <div className="arrow">→</div>
                <div className="signal-box output">
                  <span>Output</span>
                  <span>ω(t)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Closed-Loop Block Diagram */}
        <div className="block-diagram">
          <h4>Closed-Loop PID Control System</h4>
          <div className="diagram-container">
            <div className="block-diagram-flow">
              <div className="signal-line">
                <div className="signal-box input">
                  <span>Reference</span>
                  <span>r(t)</span>
                </div>
                <div className="arrow">→</div>
                <div className="summing-junction">
                  <span>+</span>
                  <span>-</span>
                </div>
                <div className="arrow">→</div>
                <div className="signal-box controller">
                  <span>PID Controller</span>
                  <span>Kp + Ki/s + Kd*s</span>
                </div>
                <div className="arrow">→</div>
                <div className="signal-box plant">
                  <span>DC Motor Plant</span>
                  <span>G(s)</span>
                </div>
                <div className="arrow">→</div>
                <div className="signal-box output">
                  <span>Output</span>
                  <span>ω(t)</span>
                </div>
              </div>
              <div className="feedback-line">
                <div className="arrow feedback-arrow">↙</div>
                <div className="signal-box sensor">
                  <span>Sensor/Encoder</span>
                  <span>H(s) = 1</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Transfer Function Details */}
        <div className="transfer-function-details">
          <h4>📐 Transfer Function Components</h4>
          <div className="tf-grid">
            <div className="tf-item">
              <strong>Electrical:</strong> 
              <span>(Ls + R)</span>
            </div>
            <div className="tf-item">
              <strong>Mechanical:</strong> 
              <span>(Js + b)</span>
            </div>
            <div className="tf-item">
              <strong>Coupling:</strong> 
              <span>Kt (torque), Ke (back-EMF)</span>
            </div>
            <div className="tf-item">
              <strong>Complete Plant:</strong> 
              <span>G(s) = Kt / [s(Js+b)(Ls+R) + KtKe]</span>
            </div>
          </div>
        </div>
      </div>

      {/* Parameter Summary */}
      <div className="parameter-summary">
        <h3>📋 Extracted Parameters Summary</h3>
        <div className="parameter-grid">
          <div className="parameter-item">
            <span className="param-name">Resistance (R):</span>
            <span className="param-value">{parameters.R ? `${parameters.R} Ω` : 'Not measured'}</span>
          </div>
          <div className="parameter-item">
            <span className="param-name">Inductance (L):</span>
            <span className="param-value">{parameters.L ? `${parameters.L} H` : 'Not measured'}</span>
          </div>
          <div className="parameter-item">
            <span className="param-name">Inertia (J):</span>
            <span className="param-value">{parameters.J ? `${parameters.J.toExponential(3)} kg⋅m²` : 'Not measured'}</span>
          </div>
          <div className="parameter-item">
            <span className="param-name">Viscous Damping (b):</span>
            <span className="param-value">{parameters.b ? `${parameters.b.toExponential(3)} N⋅m⋅s/rad` : 'Not measured'}</span>
          </div>
          <div className="parameter-item">
            <span className="param-name">Back-EMF Constant (Ke):</span>
            <span className="param-value">{parameters.Ke ? `${parameters.Ke.toFixed(4)} V⋅s/rad` : 'Not measured'}</span>
          </div>
          <div className="parameter-item">
            <span className="param-name">Torque Constant (Kt):</span>
            <span className="param-value">{parameters.Kt ? `${parameters.Kt.toFixed(4)} N⋅m/A` : 'Not measured'}</span>
          </div>
        </div>
      </div>

      {/* Live Logs */}
      <div className="logs-section">
        <h3>📝 Live Logs</h3>
        <div className="log-container">
          {logs.map((log, index) => (
            <div key={index} className="log-entry">{log}</div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ParameterExtraction;
