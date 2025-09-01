
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

  useEffect(() => { 
    document.title = 'DC Motor — Parameter Extraction — CtrlHub'; 
    checkAgentConnection();
  }, []);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `${timestamp}: ${message}`]);
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

  const runCoastDownTest = async () => {
    if (!arduinoConnected) {
      addLog('❌ Arduino not connected');
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
    if (!arduinoConnected) {
      addLog('❌ Arduino not connected');
      return;
    }

    addLog('🔋 Starting back-EMF measurement...');
    
    try {
      // Run motor at constant speed and measure voltage and current
      const result = await agent.runDCMotorSimulation({
        testType: 'back-emf',
        duration: 5000,
        motorSpeed: 200,
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
        <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          Local Agent: {isConnected ? 'Connected' : 'Disconnected'}
        </div>
        <div className={`status-indicator ${arduinoConnected ? 'connected' : 'disconnected'}`}>
          Arduino: {arduinoConnected ? 'Connected' : 'Disconnected'}
        </div>
        {!isConnected && (
          <button onClick={checkAgentConnection} className="btn btn-primary">
            Reconnect Agent
          </button>
        )}
        {isConnected && !arduinoConnected && (
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
                type="number" 
                step="0.1" 
                value={parameters.R || ''} 
                onChange={(e) => setParameters(prev => ({...prev, R: parseFloat(e.target.value) || null}))}
                placeholder="Measure with multimeter"
              />
            </div>
            <div className="input-group">
              <label>Inductance (H):</label>
              <input 
                type="number" 
                step="0.001" 
                value={parameters.L || ''} 
                onChange={(e) => setParameters(prev => ({...prev, L: parseFloat(e.target.value) || null}))}
                placeholder="Measure with LCR meter"
              />
            </div>
          </div>
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
              disabled={!arduinoConnected || testRunning}
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
            disabled={!arduinoConnected || !parameters.R}
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
      </div>

      {/* Real-time Chart */}
      {testData.length > 0 && (
        <div className="chart-section">
          <h3>📈 Real-time Data</h3>
          <Line data={chartData} options={chartOptions} />
        </div>
      )}

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
