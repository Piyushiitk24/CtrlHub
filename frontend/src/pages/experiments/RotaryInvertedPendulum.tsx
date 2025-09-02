/*
RotaryInvertedPendulum.tsx - Frontend component for rotary inverted pendulum experiment
==================================================================================

This component provides an interactive interface for the rotary inverted pendulum 
experiment, integrating PyBullet simulation with real-time control and visualization.
*/

import React, { useState, useEffect, useRef } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';
import PendulumVisualizer3D from '../../components/visualization/PendulumVisualizer3D';
import { OnShapeUpload } from '../../components/upload/OnShapeUpload';
import '../../styles/RotaryPendulum.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface PendulumState {
  armAngle: number;
  armVelocity: number;
  pendulumAngle: number;
  pendulumVelocity: number;
  time: number;
}

interface PIDGains {
  kp: number;
  ki: number;
  kd: number;
}

interface ExperimentData {
  time: number[];
  armAngle: number[];
  armVelocity: number[];
  pendulumAngle: number[];
  pendulumVelocity: number[];
  controlTorque: number[];
  targetPosition: number[];
}

interface PerformanceMetrics {
  rmsErrorRad: number;
  rmsErrorDeg: number;
  maxDeviationRad: number;
  maxDeviationDeg: number;
  controlEffortNm: number;
  settlingTimeS?: number;
  uptimePercentage: number;
}

const RotaryInvertedPendulum: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [controlEnabled, setControlEnabled] = useState(false);
  const [currentState, setCurrentState] = useState<PendulumState>({
    armAngle: 0,
    armVelocity: 0,
    pendulumAngle: 0,
    pendulumVelocity: 0,
    time: 0
  });
  
  const [pidGains, setPidGains] = useState<PIDGains>({
    kp: 3.0,
    ki: 0.0,
    kd: 0.1
  });
  
  const [experimentData, setExperimentData] = useState<ExperimentData>({
    time: [],
    armAngle: [],
    armVelocity: [],
    pendulumAngle: [],
    pendulumVelocity: [],
    controlTorque: [],
    targetPosition: []
  });
  
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [duration, setDuration] = useState(30);
  
  // OnShape integration state
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  const [urdfPath, setUrdfPath] = useState<string | null>(null);
  const [modelUploaded, setModelUploaded] = useState(false);
  const [activeTab, setActiveTab] = useState<'control' | 'model'>('control');
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Check agent connection
  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 2000);
    return () => clearInterval(interval);
  }, []);

  const checkConnection = async () => {
    try {
      const response = await fetch('http://localhost:8003/status');
      const data = await response.json();
      setIsConnected(data.status === 'running');
    } catch (error) {
      setIsConnected(false);
    }
  };

  const startSimulation = async () => {
    try {
      const response = await fetch('http://localhost:8003/experiments/rotary-pendulum/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          duration,
          pidGains,
          gui: true
        }),
      });

      if (response.ok) {
        setSimulationRunning(true);
        startDataCollection();
      }
    } catch (error) {
      console.error('Failed to start simulation:', error);
    }
  };

  const stopSimulation = async () => {
    try {
      await fetch('http://localhost:8003/experiments/rotary-pendulum/stop', {
        method: 'POST',
      });
      
      setSimulationRunning(false);
      setControlEnabled(false);
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      
      // Get final results
      await getExperimentResults();
    } catch (error) {
      console.error('Failed to stop simulation:', error);
    }
  };

  const resetSimulation = async () => {
    try {
      await fetch('http://localhost:8003/experiments/rotary-pendulum/reset', {
        method: 'POST',
      });
      
      setCurrentState({
        armAngle: 0,
        armVelocity: 0,
        pendulumAngle: 0,
        pendulumVelocity: 0,
        time: 0
      });
      
      setExperimentData({
        time: [],
        armAngle: [],
        armVelocity: [],
        pendulumAngle: [],
        pendulumVelocity: [],
        controlTorque: [],
        targetPosition: []
      });
      
      setMetrics(null);
    } catch (error) {
      console.error('Failed to reset simulation:', error);
    }
  };

  const startDataCollection = () => {
    intervalRef.current = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:8003/experiments/rotary-pendulum/state');
        const data = await response.json();
        
        if (data.success) {
          setCurrentState(data.state);
          
          // Update experiment data
          setExperimentData(prev => ({
            time: [...prev.time, data.state.time],
            armAngle: [...prev.armAngle, data.state.armAngle],
            armVelocity: [...prev.armVelocity, data.state.armVelocity],
            pendulumAngle: [...prev.pendulumAngle, data.state.pendulumAngle],
            pendulumVelocity: [...prev.pendulumVelocity, data.state.pendulumVelocity],
            controlTorque: [...prev.controlTorque, data.controlTorque || 0],
            targetPosition: [...prev.targetPosition, data.targetPosition || 0]
          }));
        }
      } catch (error) {
        console.error('Failed to get state:', error);
      }
    }, 50); // 20 Hz update rate
  };

  const getExperimentResults = async () => {
    try {
      const response = await fetch('http://localhost:8003/experiments/rotary-pendulum/results');
      const data = await response.json();
      
      if (data.success) {
        setExperimentData(data.data);
        setMetrics(data.metrics);
      }
    } catch (error) {
      console.error('Failed to get results:', error);
    }
  };

  const updatePIDGains = async () => {
    try {
      await fetch('http://localhost:8003/experiments/rotary-pendulum/pid', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(pidGains),
      });
    } catch (error) {
      console.error('Failed to update PID gains:', error);
    }
  };

  const enableControl = async () => {
    try {
      await fetch('http://localhost:8003/experiments/rotary-pendulum/control', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: true }),
      });
    } catch (error) {
      console.error('Failed to enable control:', error);
    }
  };

  const disableControl = async () => {
    try {
      await fetch('http://localhost:8003/experiments/rotary-pendulum/control', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: false }),
      });
    } catch (error) {
      console.error('Failed to disable control:', error);
    }
  };

  // OnShape model handlers
  const handleUploadComplete = (files: any[]) => {
    setUploadedFiles(files);
    setModelUploaded(true);
    console.log('Files uploaded:', files);
  };

  const handleUrdfGenerated = (urdfPath: string) => {
    setUrdfPath(urdfPath);
    console.log('URDF generated:', urdfPath);
  };

  const startOnShapeSimulation = async () => {
    if (!urdfPath) {
      alert('Please upload OnShape model and generate URDF first');
      return;
    }

    try {
      const response = await fetch('http://localhost:8003/onshape/start-simulation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          urdf_path: urdfPath,
          duration,
          pidGains,
          gui: true
        }),
      });

      if (response.ok) {
        setSimulationRunning(true);
        startDataCollection();
      }
    } catch (error) {
      console.error('Failed to start OnShape simulation:', error);
    }
  };

  // Chart data for pendulum angle
  const angleChartData = {
    labels: experimentData.time.map(t => t.toFixed(2)),
    datasets: [
      {
        label: 'Pendulum Angle (rad)',
        data: experimentData.pendulumAngle,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.1,
      },
      {
        label: 'Target (0 rad)',
        data: experimentData.time.map(() => 0),
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderDash: [5, 5],
        tension: 0.1,
      },
    ],
  };

  // Chart data for arm angle
  const armChartData = {
    labels: experimentData.time.map(t => t.toFixed(2)),
    datasets: [
      {
        label: 'Arm Angle (rad)',
        data: experimentData.armAngle,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
      },
    ],
  };

  // Chart data for control torque
  const torqueChartData = {
    labels: experimentData.time.map(t => t.toFixed(2)),
    datasets: [
      {
        label: 'Control Torque (Nm)',
        data: experimentData.controlTorque,
        borderColor: 'rgb(153, 102, 255)',
        backgroundColor: 'rgba(153, 102, 255, 0.2)',
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Real-time Data',
      },
    },
    scales: {
      x: {
        display: false, // Hide x-axis labels for real-time
      },
    },
  };

  return (
    <div className="pendulum-experiment">
      <div className="experiment-header">
        <h1>🎛️ Rotary Inverted Pendulum</h1>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '🟢 Agent Connected' : '🔴 Agent Disconnected'}
        </div>
      </div>

      <div className="experiment-grid">
        {/* Control Panel with Tabs */}
        <div className="control-panel">
          <div className="panel-tabs">
            <button 
              className={`tab-button ${activeTab === 'control' ? 'active' : ''}`}
              onClick={() => setActiveTab('control')}
            >
              🎛️ Control
            </button>
            <button 
              className={`tab-button ${activeTab === 'model' ? 'active' : ''}`}
              onClick={() => setActiveTab('model')}
            >
              🏗️ OnShape Model
            </button>
          </div>

          {activeTab === 'control' && (
            <div className="control-content">
              <h3>Control Panel</h3>
              
              <div className="simulation-controls">
                <h4>Simulation</h4>
                <div className="control-group">
                  <label>Duration (seconds):</label>
                  <input
                    type="number"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    disabled={simulationRunning}
                    min="5"
                    max="300"
                  />
                </div>
                
                <div className="button-group">
                  <button
                    onClick={modelUploaded && urdfPath ? startOnShapeSimulation : startSimulation}
                    disabled={!isConnected || simulationRunning}
                    className="start-btn"
                  >
                    {modelUploaded && urdfPath ? 'Start OnShape Simulation' : 'Start Simulation'}
                  </button>
                  <button
                    onClick={stopSimulation}
                    disabled={!simulationRunning}
                    className="stop-btn"
                  >
                    Stop
                  </button>
                  <button
                    onClick={resetSimulation}
                    disabled={simulationRunning}
                    className="reset-btn"
                  >
                    Reset
                  </button>
                </div>
              </div>

              <div className="pid-controls">
                <h4>PID Controller</h4>
                <div className="control-group">
                  <label>Kp:</label>
                  <input
                    type="number"
                    step="0.1"
                    value={pidGains.kp}
                    onChange={(e) => setPidGains(prev => ({ ...prev, kp: Number(e.target.value) }))}
                    onBlur={updatePIDGains}
                  />
                </div>
                <div className="control-group">
                  <label>Ki:</label>
                  <input
                    type="number"
                    step="0.01"
                    value={pidGains.ki}
                    onChange={(e) => setPidGains(prev => ({ ...prev, ki: Number(e.target.value) }))}
                    onBlur={updatePIDGains}
                  />
                </div>
                <div className="control-group">
                  <label>Kd:</label>
                  <input
                    type="number"
                    step="0.01"
                    value={pidGains.kd}
                    onChange={(e) => setPidGains(prev => ({ ...prev, kd: Number(e.target.value) }))}
                    onBlur={updatePIDGains}
                  />
                </div>
                
                <div className="button-group">
                  <button
                    onClick={enableControl}
                    disabled={!simulationRunning || controlEnabled}
                    className="enable-btn"
                  >
                    Enable Control
                  </button>
                  <button
                    onClick={disableControl}
                    disabled={!controlEnabled}
                    className="disable-btn"
                  >
                    Disable Control
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'model' && (
            <div className="model-content">
              <OnShapeUpload 
                onUploadComplete={handleUploadComplete}
                onUrdfGenerated={handleUrdfGenerated}
              />
              
              {modelUploaded && (
                <div className="model-status">
                  <h4>📊 Model Status</h4>
                  <div className="status-info">
                    <div className="status-item">
                      <span className="status-label">Files Uploaded:</span>
                      <span className="status-value">{uploadedFiles.length}</span>
                    </div>
                    <div className="status-item">
                      <span className="status-label">URDF Generated:</span>
                      <span className="status-value">{urdfPath ? '✅ Yes' : '❌ No'}</span>
                    </div>
                    {urdfPath && (
                      <div className="status-item">
                        <span className="status-label">Ready for Simulation:</span>
                        <span className="status-value">✅ Yes</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* State Display */}
        <div className="state-panel">
          <h3>Current State</h3>
          <div className="state-grid">
            <div className="state-item">
              <span className="state-label">Arm Angle:</span>
              <span className="state-value">{(currentState.armAngle * 180 / Math.PI).toFixed(2)}°</span>
            </div>
            <div className="state-item">
              <span className="state-label">Arm Velocity:</span>
              <span className="state-value">{currentState.armVelocity.toFixed(3)} rad/s</span>
            </div>
            <div className="state-item">
              <span className="state-label">Pendulum Angle:</span>
              <span className="state-value">{(currentState.pendulumAngle * 180 / Math.PI).toFixed(2)}°</span>
            </div>
            <div className="state-item">
              <span className="state-label">Pendulum Velocity:</span>
              <span className="state-value">{currentState.pendulumVelocity.toFixed(3)} rad/s</span>
            </div>
            <div className="state-item">
              <span className="state-label">Time:</span>
              <span className="state-value">{currentState.time.toFixed(2)}s</span>
            </div>
            <div className="state-item">
              <span className="state-label">Control:</span>
              <span className={`state-value ${controlEnabled ? 'enabled' : 'disabled'}`}>
                {controlEnabled ? 'ENABLED' : 'DISABLED'}
              </span>
            </div>
          </div>
        </div>

        {/* 3D Visualization */}
        <div className="visualization-panel">
          <h3>3D Visualization</h3>
          <PendulumVisualizer3D
            armAngle={currentState.armAngle}
            pendulumAngle={currentState.pendulumAngle}
          />
        </div>

        {/* Performance Metrics */}
        {metrics && (
          <div className="metrics-panel">
            <h3>Performance Metrics</h3>
            <div className="metrics-grid">
              <div className="metric-item">
                <span className="metric-label">RMS Error:</span>
                <span className="metric-value">{metrics.rmsErrorDeg.toFixed(2)}°</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Max Deviation:</span>
                <span className="metric-value">{metrics.maxDeviationDeg.toFixed(2)}°</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Control Effort:</span>
                <span className="metric-value">{metrics.controlEffortNm.toFixed(3)} Nm</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Uptime:</span>
                <span className="metric-value">{metrics.uptimePercentage.toFixed(1)}%</span>
              </div>
              {metrics.settlingTimeS && (
                <div className="metric-item">
                  <span className="metric-label">Settling Time:</span>
                  <span className="metric-value">{metrics.settlingTimeS.toFixed(2)}s</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Charts */}
        <div className="charts-panel">
          <div className="chart-panel">
            <h4>Pendulum Angle</h4>
            <Line data={angleChartData} options={chartOptions} />
          </div>
          
          <div className="chart-panel">
            <h4>Arm Position</h4>
            <Line data={armChartData} options={chartOptions} />
          </div>
          
          <div className="chart-panel">
            <h4>Control Torque</h4>
            <Line data={torqueChartData} options={chartOptions} />
          </div>
        </div>
      </div>

      <div className="experiment-info">
        <h3>Experiment Information</h3>
        <div className="info-content">
          <h4>Objective:</h4>
          <p>Balance an inverted pendulum using rotary arm control with PID feedback.</p>
          
          <h4>Hardware:</h4>
          <ul>
            <li>Stepper Motor: 17HS4023 (200 steps/rev, 8 microsteps)</li>
            <li>Encoder: AS5600 magnetic encoder (12-bit resolution)</li>
            <li>Control: PID controller running at 1000 Hz</li>
          </ul>
          
          <h4>Instructions:</h4>
          <ol>
            <li>Start the simulation with PyBullet visualization</li>
            <li>Manually move the pendulum close to upright in the simulation</li>
            <li>Enable control to start automatic balancing</li>
            <li>Tune PID gains for optimal performance</li>
            <li>Analyze performance metrics and charts</li>
          </ol>
          
          <h4>OnShape Integration:</h4>
          <ol>
            <li>Switch to "OnShape Model" tab</li>
            <li>Upload your GLTF/STL files from OnShape</li>
            <li>Generate URDF for physics simulation</li>
            <li>Return to "Control" tab to start OnShape simulation</li>
            <li>Your actual CAD model will be used in the physics simulation!</li>
          </ol>
          
          <h4>Educational Goals:</h4>
          <ul>
            <li>Understand inverted pendulum dynamics</li>
            <li>Learn PID control design and tuning</li>
            <li>Experience real-time control challenges</li>
            <li>Analyze system performance metrics</li>
            <li>Bridge CAD design to physics simulation</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default RotaryInvertedPendulum;
