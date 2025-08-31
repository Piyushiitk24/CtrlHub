import React, { useState, useEffect } from 'react';
import { LocalAgentHandler } from './utils/LocalAgentHandler';

interface SystemStatus {
  localAgent: boolean;
  arduino: boolean;
  motorController: boolean;
}

interface MotorData {
  position: number;
  velocity: number;
  current: number;
  voltage: number;
  temperature: number;
}

const App: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    localAgent: false,
    arduino: false,
    motorController: false
  });

  const [motorData, setMotorData] = useState<MotorData>({
    position: 0,
    velocity: 0,
    current: 0,
    voltage: 0,
    temperature: 25
  });

  const [isConnecting, setIsConnecting] = useState(false);
  const [localAgent] = useState(new LocalAgentHandler());

  useEffect(() => {
    // Check local agent connection on mount
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const status = await localAgent.getSystemStatus();
      setSystemStatus({
        localAgent: status.agent_running,
        arduino: status.arduino_connected,
        motorController: status.motor_controller_ready
      });
    } catch (error) {
      console.error('Failed to get system status:', error);
      setSystemStatus({
        localAgent: false,
        arduino: false,
        motorController: false
      });
    }
  };

  const handleConnect = async () => {
    setIsConnecting(true);
    try {
      await localAgent.connect();
      await checkSystemStatus();
    } catch (error) {
      console.error('Connection failed:', error);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleStartEducationalDemo = async () => {
    try {
      console.log('Starting educational demo...');
      // Here you would integrate with the educational system
      alert('Educational demo will be integrated in the next update!');
    } catch (error) {
      console.error('Failed to start educational demo:', error);
    }
  };

  const StatusIndicator: React.FC<{ connected: boolean; label: string }> = ({ connected, label }) => (
    <div style={{ display: 'flex', alignItems: 'center', margin: '10px 0' }}>
      <span className={`status-indicator ${connected ? 'status-connected' : 'status-disconnected'}`}></span>
      <span style={{ color: connected ? '#4CAF50' : '#f44336', fontWeight: '600' }}>
        {label}: {connected ? 'Connected' : 'Disconnected'}
      </span>
    </div>
  );

  return (
    <div className="App">
      {/* Hero Section */}
      <div className="hero">
        <div className="container">
          <h1>CtrlHub</h1>
          <p>Advanced Control Systems Education Platform</p>
          <p style={{ fontSize: '1rem', opacity: 0.8 }}>
            Learn DC motor control through hands-on experiments, first-principles modeling, and advanced PID design
          </p>
        </div>
      </div>

      <div className="container">
        {/* System Status Card */}
        <div className="card">
          <h2 style={{ color: '#667eea', marginBottom: '20px' }}>System Status</h2>
          <StatusIndicator connected={systemStatus.localAgent} label="Local Agent" />
          <StatusIndicator connected={systemStatus.arduino} label="Arduino Hardware" />
          <StatusIndicator connected={systemStatus.motorController} label="Motor Controller" />
          
          <div style={{ marginTop: '20px' }}>
            <button 
              className="btn" 
              onClick={handleConnect}
              disabled={isConnecting}
            >
              {isConnecting ? 'Connecting...' : 'Connect Hardware'}
            </button>
            <button 
              className="btn" 
              onClick={checkSystemStatus}
              style={{ marginLeft: '10px' }}
            >
              Refresh Status
            </button>
          </div>
        </div>

        {/* Educational Features */}
        <div className="card">
          <h2 style={{ color: '#667eea', marginBottom: '30px' }}>Educational System</h2>
          <div className="features">
            <div className="feature">
              <h3>🔬 Parameter Extraction</h3>
              <p>Learn to measure motor parameters through hands-on experiments including resistance, back-EMF, torque constant, and inertia analysis.</p>
            </div>
            <div className="feature">
              <h3>📐 First-Principles Modeling</h3>
              <p>Derive motor equations from Kirchhoff's and Newton's laws. Build mathematical models from fundamental physics principles.</p>
            </div>
            <div className="feature">
              <h3>🎛️ PID Controller Design</h3>
              <p>Master multiple PID tuning methods including Ziegler-Nichols, pole placement, frequency domain, and genetic algorithms.</p>
            </div>
            <div className="feature">
              <h3>⚡ Hardware Integration</h3>
              <p>Validate theory with real Arduino-based motor control. Bridge the gap between simulation and real-world applications.</p>
            </div>
          </div>
          
          <div style={{ textAlign: 'center', marginTop: '30px' }}>
            <button 
              className="btn"
              onClick={handleStartEducationalDemo}
              style={{ fontSize: '18px', padding: '15px 30px' }}
            >
              Start Educational Journey
            </button>
          </div>
        </div>

        {/* Motor Data Monitoring */}
        {systemStatus.arduino && (
          <div className="card">
            <h2 style={{ color: '#667eea', marginBottom: '20px' }}>Real-Time Motor Data</h2>
            <div className="control-panel">
              <div className="control-group">
                <label>Position (degrees)</label>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
                  {motorData.position.toFixed(1)}°
                </div>
              </div>
              <div className="control-group">
                <label>Velocity (rpm)</label>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
                  {motorData.velocity.toFixed(0)} RPM
                </div>
              </div>
              <div className="control-group">
                <label>Current (A)</label>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
                  {motorData.current.toFixed(2)} A
                </div>
              </div>
              <div className="control-group">
                <label>Voltage (V)</label>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
                  {motorData.voltage.toFixed(1)} V
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Curriculum Overview */}
        <div className="card">
          <h2 style={{ color: '#667eea', marginBottom: '20px' }}>7-Module Progressive Curriculum</h2>
          <div style={{ display: 'grid', gap: '15px' }}>
            {[
              { title: 'Module 1: Introduction & Safety', duration: '30 min', description: 'Fundamentals and safety protocols' },
              { title: 'Module 2: Parameter Extraction', duration: '90 min', description: 'Hands-on measurement techniques' },
              { title: 'Module 3: First-Principles Modeling', duration: '60 min', description: 'Physics-based mathematical models' },
              { title: 'Module 4: Open-Loop Analysis', duration: '45 min', description: 'System limitations understanding' },
              { title: 'Module 5: Feedback Control Theory', duration: '75 min', description: 'PID fundamentals' },
              { title: 'Module 6: Advanced Control Design', duration: '120 min', description: 'Multiple tuning methods' },
              { title: 'Module 7: Real-World Applications', duration: '90 min', description: 'Hardware validation' }
            ].map((module, index) => (
              <div key={index} style={{ 
                padding: '20px', 
                border: '2px solid #e0e0e0', 
                borderRadius: '10px',
                background: 'rgba(102, 126, 234, 0.05)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 style={{ margin: 0, color: '#667eea' }}>{module.title}</h4>
                  <span style={{ 
                    background: '#667eea', 
                    color: 'white', 
                    padding: '4px 12px', 
                    borderRadius: '15px',
                    fontSize: '12px'
                  }}>
                    {module.duration}
                  </span>
                </div>
                <p style={{ margin: '10px 0 0 0', color: '#666' }}>{module.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div style={{ textAlign: 'center', padding: '40px 0', color: 'white' }}>
          <p style={{ opacity: 0.8 }}>
            CtrlHub - Bridging Theory and Practice in Control Systems Education
          </p>
          <p style={{ opacity: 0.6, fontSize: '14px' }}>
            Open Source Educational Platform | MIT License
          </p>
        </div>
      </div>
    </div>
  );
};

export default App;