import React, { useState, useEffect } from 'react';
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
import LocalAgentHandler from '../../utils/LocalAgentHandler';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface DCMotorParams {
  J: number;    // Moment of inertia (kg⋅m²)
  b: number;    // Viscous friction coefficient (N⋅m⋅s/rad)
  K: number;    // Torque/Back-EMF constant (N⋅m/A or V⋅s/rad)
  R: number;    // Resistance (Ohms)
  L: number;    // Inductance (H)
}

interface PIDParams {
  Kp: number;
  Ki: number;
  Kd: number;
}

interface PlotData {
  time: number[];
  response: number[];
}

interface TransferFunction {
  numerator: number[];
  denominator: number[];
  display: string;
}

const DCMotorPID: React.FC = () => {
  const [agent] = useState(new LocalAgentHandler());
  const [isConnected, setIsConnected] = useState(false);
  const [arduinoConnected, setArduinoConnected] = useState(false);
  
  // Motor parameters with realistic defaults
  const [params, setParams] = useState<DCMotorParams>({
    J: 0.01,    // kg⋅m²
    b: 0.1,     // N⋅m⋅s/rad
    K: 0.01,    // N⋅m/A
    R: 1.0,     // Ohms
    L: 0.5      // H
  });
  
  const [transferFunction, setTransferFunction] = useState<TransferFunction | null>(null);
  const [pid, setPid] = useState<PIDParams>({ Kp: 1.0, Ki: 0.1, Kd: 0.01 });
  const [desiredSpeed, setDesiredSpeed] = useState<number>(100); // RPM
  
  // Plot data
  const [stepPlot, setStepPlot] = useState<PlotData | null>(null);
  const [bodePlot, setBodePlot] = useState<any>(null);
  const [pidTestPlot, setPidTestPlot] = useState<PlotData | null>(null);
  const [finalPlot, setFinalPlot] = useState<any>(null);
  
  // UI state
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});
  
  useEffect(() => {
    checkAgentConnection();
    const interval = setInterval(checkAgentConnection, 3000);
    return () => clearInterval(interval);
  }, []);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const checkAgentConnection = async () => {
    try {
      const connected = await agent.checkLocalAgent();
      setIsConnected(connected);
      if (connected) {
        addLog('✅ Local agent connected');
        checkArduinoConnection();
      } else {
        addLog('❌ Local agent disconnected - using fallback simulations');
      }
    } catch (error) {
      setIsConnected(false);
      addLog('❌ Failed to connect to local agent');
    }
  };

  const checkArduinoConnection = async () => {
    try {
      const result = await fetch('http://localhost:8003/status');
      const status = await result.json();
      setArduinoConnected(status.arduino_connected || false);
    } catch (error) {
      setArduinoConnected(false);
    }
  };

  // JavaScript fallback for transfer function generation
  const generateJSTransferFunction = (params: DCMotorParams): TransferFunction => {
    // For DC motor: G(s) = K / (J*L*s^2 + (J*R + b*L)*s + (b*R + K^2))
    const num = [params.K];
    const den = [
      params.J * params.L,
      params.J * params.R + params.b * params.L,
      params.b * params.R + params.K * params.K
    ];
    
    return {
      numerator: num,
      denominator: den,
      display: `\\frac{${params.K}}{${den[0].toFixed(4)}s^2 + ${den[1].toFixed(4)}s + ${den[2].toFixed(4)}}`
    };
  };

  // JavaScript fallback for step response
  const generateJSStepResponse = (tf: TransferFunction, duration: number = 10): PlotData => {
    const dt = 0.01;
    const time = [];
    const response = [];
    
    // Simple numerical integration using Euler method
    let y = 0, dy = 0;
    const num = tf.numerator;
    const den = tf.denominator;
    
    for (let t = 0; t <= duration; t += dt) {
      time.push(t);
      
      // Second order system approximation
      const omega_n = Math.sqrt(den[2] / den[0]);
      const zeta = den[1] / (2 * Math.sqrt(den[0] * den[2]));
      const k = num[0] / den[2];
      
      if (zeta < 1) {
        const omega_d = omega_n * Math.sqrt(1 - zeta * zeta);
        y = k * (1 - Math.exp(-zeta * omega_n * t) * 
          (Math.cos(omega_d * t) + (zeta * omega_n / omega_d) * Math.sin(omega_d * t)));
      } else {
        y = k * (1 - Math.exp(-omega_n * t) * (1 + omega_n * t));
      }
      
      response.push(y);
    }
    
    return { time, response };
  };

  const generateModel = async () => {
    setLoading(prev => ({ ...prev, model: true }));
    addLog('🔧 Generating transfer function model...');
    
    try {
      if (isConnected) {
        const response = await fetch('http://localhost:8003/dc-motor-pid/generate_transfer_function', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(params)
        });
        
        if (response.ok) {
          const result = await response.json();
          setTransferFunction(result.tf);
          addLog('✅ Transfer function generated using Python control library');
        } else {
          throw new Error('Agent request failed');
        }
      } else {
        // Fallback to JavaScript simulation
        const jsTf = generateJSTransferFunction(params);
        setTransferFunction(jsTf);
        addLog('✅ Transfer function generated using JavaScript fallback');
      }
    } catch (error) {
      // Fallback simulation
      const jsTf = generateJSTransferFunction(params);
      setTransferFunction(jsTf);
      addLog('⚠️ Using JavaScript fallback simulation');
    } finally {
      setLoading(prev => ({ ...prev, model: false }));
    }
  };

  const getStepPlot = async () => {
    if (!transferFunction) {
      addLog('❌ Generate model first');
      return;
    }
    
    setLoading(prev => ({ ...prev, step: true }));
    addLog('📊 Generating step response plot...');
    
    try {
      if (isConnected) {
        const response = await fetch('http://localhost:8003/dc-motor-pid/get_step_plot', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tf: transferFunction })
        });
        
        if (response.ok) {
          const result = await response.json();
          setStepPlot({ time: result.time, response: result.response });
          addLog('✅ Step response generated');
        } else {
          throw new Error('Agent request failed');
        }
      } else {
        const jsStep = generateJSStepResponse(transferFunction);
        setStepPlot(jsStep);
        addLog('✅ Step response generated (JavaScript)');
      }
    } catch (error) {
      const jsStep = generateJSStepResponse(transferFunction);
      setStepPlot(jsStep);
      addLog('⚠️ Using JavaScript fallback for step response');
    } finally {
      setLoading(prev => ({ ...prev, step: false }));
    }
  };

  const getBodePlot = async () => {
    if (!transferFunction) {
      addLog('❌ Generate model first');
      return;
    }
    
    setLoading(prev => ({ ...prev, bode: true }));
    addLog('📊 Generating Bode plot...');
    
    try {
      if (isConnected) {
        const response = await fetch('http://localhost:8003/dc-motor-pid/get_bode_plot', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tf: transferFunction })
        });
        
        if (response.ok) {
          const result = await response.json();
          setBodePlot(result);
          addLog('✅ Bode plot generated');
        } else {
          throw new Error('Agent request failed');
        }
      } else {
        addLog('⚠️ Bode plot requires local agent - not available in fallback mode');
      }
    } catch (error) {
      addLog('❌ Bode plot generation failed');
    } finally {
      setLoading(prev => ({ ...prev, bode: false }));
    }
  };

  const testPID = async () => {
    if (!transferFunction) {
      addLog('❌ Generate model first');
      return;
    }
    
    setLoading(prev => ({ ...prev, pid: true }));
    addLog('🎛️ Testing PID controller...');
    
    try {
      if (isConnected) {
        const response = await fetch('http://localhost:8003/dc-motor-pid/test_pid', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tf: transferFunction, pid, setpoint: desiredSpeed })
        });
        
        if (response.ok) {
          const result = await response.json();
          setPidTestPlot({ time: result.time, response: result.response });
          addLog(`✅ PID test complete - Rise time: ${result.metrics.rise_time.toFixed(2)}s, Overshoot: ${result.metrics.overshoot.toFixed(1)}%`);
        } else {
          throw new Error('Agent request failed');
        }
      } else {
        addLog('⚠️ PID simulation requires local agent - not available in fallback mode');
      }
    } catch (error) {
      addLog('❌ PID test failed');
    } finally {
      setLoading(prev => ({ ...prev, pid: false }));
    }
  };

  const connectHardware = async () => {
    setLoading(prev => ({ ...prev, hardware: true }));
    addLog('🔌 Connecting to Arduino...');
    
    try {
      const response = await fetch('http://localhost:8003/dc-motor-pid/connect_hardware', {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setArduinoConnected(true);
          addLog(`✅ Arduino connected on ${result.port}`);
        } else {
          addLog(`❌ Arduino connection failed: ${result.error}`);
        }
      }
    } catch (error) {
      addLog('❌ Hardware connection failed');
    } finally {
      setLoading(prev => ({ ...prev, hardware: false }));
    }
  };

  const runFinalExperiment = async () => {
    if (!transferFunction) {
      addLog('❌ Generate model first');
      return;
    }
    
    setLoading(prev => ({ ...prev, final: true }));
    addLog('🚀 Running final experiment (simulation + hardware)...');
    
    try {
      const response = await fetch('http://localhost:8003/dc-motor-pid/run_final_experiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tf: transferFunction,
          pid,
          desired_speed: desiredSpeed,
          duration: 10
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setFinalPlot(result);
        addLog('✅ Final experiment complete - check comparative plots');
      } else {
        throw new Error('Experiment failed');
      }
    } catch (error) {
      addLog('❌ Final experiment failed');
    } finally {
      setLoading(prev => ({ ...prev, final: false }));
    }
  };

  const renderStepChart = () => {
    if (!stepPlot) return null;
    
    const chartData = {
      labels: stepPlot.time.map(t => t.toFixed(2)),
      datasets: [
        {
          label: 'Step Response',
          data: stepPlot.response,
          borderColor: 'rgb(0, 255, 65)',
          backgroundColor: 'rgba(0, 255, 65, 0.1)',
          borderWidth: 2,
          fill: false,
        }
      ]
    };
    
    const options = {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'DC Motor Step Response',
          color: 'rgb(0, 255, 65)'
        },
        legend: {
          labels: { color: 'rgb(0, 255, 65)' }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Time (s)', color: 'rgb(0, 255, 65)' },
          ticks: { color: 'rgb(0, 255, 65)' },
          grid: { color: 'rgba(0, 255, 65, 0.2)' }
        },
        y: {
          title: { display: true, text: 'Speed (rad/s)', color: 'rgb(0, 255, 65)' },
          ticks: { color: 'rgb(0, 255, 65)' },
          grid: { color: 'rgba(0, 255, 65, 0.2)' }
        }
      }
    };
    
    return <Line data={chartData} options={options} />;
  };

  const renderFinalChart = () => {
    if (!finalPlot) return null;
    
    const chartData = {
      labels: finalPlot.time.map((t: number) => t.toFixed(2)),
      datasets: [
        {
          label: 'Desired Speed',
          data: finalPlot.desired,
          borderColor: 'rgb(255, 204, 2)',
          backgroundColor: 'rgba(255, 204, 2, 0.1)',
          borderWidth: 2,
          borderDash: [5, 5],
          fill: false,
        },
        {
          label: 'Simulated Speed',
          data: finalPlot.simulated,
          borderColor: 'rgb(0, 255, 65)',
          backgroundColor: 'rgba(0, 255, 65, 0.1)',
          borderWidth: 2,
          fill: false,
        },
        {
          label: 'Hardware Speed',
          data: finalPlot.hardware,
          borderColor: 'rgb(255, 107, 53)',
          backgroundColor: 'rgba(255, 107, 53, 0.1)',
          borderWidth: 2,
          fill: false,
        }
      ]
    };
    
    const options = {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Simulation vs Hardware Comparison',
          color: 'rgb(0, 255, 65)'
        },
        legend: {
          labels: { color: 'rgb(0, 255, 65)' }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Time (s)', color: 'rgb(0, 255, 65)' },
          ticks: { color: 'rgb(0, 255, 65)' },
          grid: { color: 'rgba(0, 255, 65, 0.2)' }
        },
        y: {
          title: { display: true, text: 'Speed (RPM)', color: 'rgb(0, 255, 65)' },
          ticks: { color: 'rgb(0, 255, 65)' },
          grid: { color: 'rgba(0, 255, 65, 0.2)' }
        }
      }
    };
    
    return <Line data={chartData} options={options} />;
  };

  return (
    <div className="study-container single-pane">
      <div className="study-header">
        <h2 className="study-title">DC Motor PID Control Experiment</h2>
        <p>Complete workflow from parameter input to hardware validation</p>
      </div>
      
      <div className="study-content">
        {/* Connection Status */}
        <div className="section">
          <h3>System Status</h3>
          <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
            <div className="status-card">
              <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
                {isConnected ? '🟢' : '🔴'} Local Agent: {isConnected ? 'Connected' : 'Disconnected'}
              </div>
            </div>
            <div className="status-card">
              <div className={`status-indicator ${arduinoConnected ? 'connected' : 'disconnected'}`}>
                {arduinoConnected ? '🟢' : '🔴'} Arduino: {arduinoConnected ? 'Connected' : 'Not Connected'}
              </div>
            </div>
          </div>
        </div>

        {/* Step 1: Motor Parameters */}
        <div className="section">
          <h3>Step 1: Motor Parameters</h3>
          <p>Enter your DC motor physical parameters:</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '20px' }}>
            <div>
              <label>Moment of Inertia (J) [kg⋅m²]:</label>
              <input
                type="number"
                step="0.001"
                value={params.J}
                onChange={(e) => setParams({...params, J: parseFloat(e.target.value) || 0})}
              />
            </div>
            <div>
              <label>Friction Coefficient (b) [N⋅m⋅s/rad]:</label>
              <input
                type="number"
                step="0.001"
                value={params.b}
                onChange={(e) => setParams({...params, b: parseFloat(e.target.value) || 0})}
              />
            </div>
            <div>
              <label>Motor Constant (K) [N⋅m/A]:</label>
              <input
                type="number"
                step="0.001"
                value={params.K}
                onChange={(e) => setParams({...params, K: parseFloat(e.target.value) || 0})}
              />
            </div>
            <div>
              <label>Resistance (R) [Ω]:</label>
              <input
                type="number"
                step="0.1"
                value={params.R}
                onChange={(e) => setParams({...params, R: parseFloat(e.target.value) || 0})}
              />
            </div>
            <div>
              <label>Inductance (L) [H]:</label>
              <input
                type="number"
                step="0.01"
                value={params.L}
                onChange={(e) => setParams({...params, L: parseFloat(e.target.value) || 0})}
              />
            </div>
          </div>
          
          <button
            onClick={generateModel}
            disabled={loading.model}
            className="btn btn-primary"
          >
            {loading.model ? 'Generating...' : 'Generate Transfer Function Model'}
          </button>
          
          {transferFunction && (
            <div style={{ marginTop: '20px', padding: '15px', background: 'rgba(0, 255, 65, 0.1)', border: '2px solid var(--secondary-green)', borderRadius: '8px' }}>
              <h4>Transfer Function:</h4>
              <BlockMath math={transferFunction.display} />
            </div>
          )}
        </div>

        {/* Step 2: System Analysis */}
        <div className="section">
          <h3>Step 2: System Analysis</h3>
          <p>Analyze the open-loop system characteristics:</p>
          
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <button
              onClick={getStepPlot}
              disabled={!transferFunction || loading.step}
              className="btn btn-secondary"
            >
              {loading.step ? 'Generating...' : 'Generate Step Response'}
            </button>
            <button
              onClick={getBodePlot}
              disabled={!transferFunction || loading.bode}
              className="btn btn-secondary"
            >
              {loading.bode ? 'Generating...' : 'Generate Bode Plot'}
            </button>
          </div>
          
          {stepPlot && (
            <div style={{ marginTop: '20px' }}>
              <h4>Step Response:</h4>
              {renderStepChart()}
            </div>
          )}
        </div>

        {/* Step 3: PID Controller Design */}
        <div className="section">
          <h3>Step 3: PID Controller Design</h3>
          <p>Design and tune your PID controller:</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', marginBottom: '20px' }}>
            <div>
              <label>Proportional (Kp):</label>
              <input
                type="number"
                step="0.1"
                value={pid.Kp}
                onChange={(e) => setPid({...pid, Kp: parseFloat(e.target.value) || 0})}
              />
            </div>
            <div>
              <label>Integral (Ki):</label>
              <input
                type="number"
                step="0.01"
                value={pid.Ki}
                onChange={(e) => setPid({...pid, Ki: parseFloat(e.target.value) || 0})}
              />
            </div>
            <div>
              <label>Derivative (Kd):</label>
              <input
                type="number"
                step="0.001"
                value={pid.Kd}
                onChange={(e) => setPid({...pid, Kd: parseFloat(e.target.value) || 0})}
              />
            </div>
            <div>
              <label>Desired Speed (RPM):</label>
              <input
                type="number"
                value={desiredSpeed}
                onChange={(e) => setDesiredSpeed(parseFloat(e.target.value) || 0)}
              />
            </div>
          </div>
          
          <button
            onClick={testPID}
            disabled={!transferFunction || loading.pid}
            className="btn btn-primary"
          >
            {loading.pid ? 'Testing...' : 'Test PID Controller'}
          </button>
        </div>

        {/* Step 4: Hardware Integration */}
        <div className="section">
          <h3>Step 4: Hardware Integration</h3>
          <p>Connect and test with real hardware:</p>
          
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <button
              onClick={connectHardware}
              disabled={!isConnected || loading.hardware}
              className="btn btn-secondary"
            >
              {loading.hardware ? 'Connecting...' : 'Connect Arduino'}
            </button>
            <button
              onClick={runFinalExperiment}
              disabled={!transferFunction || loading.final}
              className="btn btn-primary"
            >
              {loading.final ? 'Running...' : 'Run Final Experiment'}
            </button>
          </div>
          
          {finalPlot && (
            <div style={{ marginTop: '20px' }}>
              <h4>Simulation vs Hardware Comparison:</h4>
              {renderFinalChart()}
            </div>
          )}
        </div>

        {/* Activity Log */}
        <div className="section">
          <h3>Activity Log</h3>
          <div style={{ 
            height: '200px', 
            overflow: 'auto', 
            background: 'rgba(42, 42, 42, 0.8)', 
            padding: '10px', 
            border: '2px solid var(--secondary-green)',
            borderRadius: '8px',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '12px',
            color: 'var(--primary-green)'
          }}>
            {logs.map((log, index) => (
              <div key={index}>{log}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DCMotorPID;