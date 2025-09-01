import React, { useState, useEffect } from 'react';
import LocalAgentHandler from '../../utils/LocalAgentHandler';

interface AgentStatus {
  connected: boolean;
  arduinoConnected: boolean;
  port?: string;
  message?: string;
}

const CtrlHubAgentStatus: React.FC = () => {
  const [agentHandler] = useState(new LocalAgentHandler());
  const [status, setStatus] = useState<AgentStatus>({
    connected: false,
    arduinoConnected: false
  });
  const [isConnecting, setIsConnecting] = useState(false);
  const [availablePorts, setAvailablePorts] = useState<string[]>([]);

  useEffect(() => {
    checkAgentStatus();
    const interval = setInterval(checkAgentStatus, 3000); // Check every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const checkAgentStatus = async () => {
    try {
      const isConnected = await agentHandler.checkLocalAgent();
      if (isConnected) {
        // Get hardware status
        const healthResponse = await fetch('http://localhost:8001/health');
        const healthData = await healthResponse.json();
        
        setStatus({
          connected: true,
          arduinoConnected: healthData.arduino_connected || false,
          message: "CtrlHub Agent is running"
        });
      } else {
        setStatus({
          connected: false,
          arduinoConnected: false,
          message: "CtrlHub Agent not detected"
        });
      }
    } catch (error) {
      setStatus({
        connected: false,
        arduinoConnected: false,
        message: "Connection error"
      });
    }
  };

  const connectArduino = async () => {
    setIsConnecting(true);
    try {
      const result = await agentHandler.connectArduino();
      if (result.success) {
        setStatus(prev => ({ ...prev, arduinoConnected: true, port: result.port }));
      } else {
        alert(`Connection failed: ${result.error}`);
      }
    } catch (error: any) {
      alert(`Error: ${error?.message || 'Unknown error'}`);
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnectArduino = async () => {
    try {
      const result = await agentHandler.disconnectArduino();
      if (result.success) {
        setStatus(prev => ({ ...prev, arduinoConnected: false, port: undefined }));
      }
    } catch (error: any) {
      alert(`Disconnect error: ${error?.message || 'Unknown error'}`);
    }
  };

  const scanPorts = async () => {
    try {
      const result = await agentHandler.scanPorts();
      if (result.success) {
        setAvailablePorts(result.ports);
      }
    } catch (error) {
      console.error('Port scan error:', error);
    }
  };

  const runDemoSimulation = async () => {
    try {
      const demoParams = {
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

      const result = await agentHandler.runDCMotorSimulation(demoParams);
      console.log('Simulation result:', result);
      
      if (result.success) {
        alert('Simulation completed successfully! Check browser console for results.');
      } else {
        alert(`Simulation failed: ${result.error}`);
      }
    } catch (error: any) {
      alert(`Error: ${error?.message || 'Unknown error'}`);
    }
  };

  return (
    <div className="ctrlhub-agent-status p-4 border rounded-lg">
      <h3 className="text-lg font-bold mb-4">🎓 CtrlHub Local Agent</h3>
      
      {/* Agent Status */}
      <div className="mb-4">
        <div className="flex items-center mb-2">
          <span className={`w-3 h-3 rounded-full mr-2 ${status.connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
          <span className="font-medium">
            Agent Status: {status.connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        {status.message && (
          <p className="text-sm text-gray-600 ml-5">{status.message}</p>
        )}
      </div>

      {/* Arduino Status */}
      {status.connected && (
        <div className="mb-4">
          <div className="flex items-center mb-2">
            <span className={`w-3 h-3 rounded-full mr-2 ${status.arduinoConnected ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
            <span className="font-medium">
              Arduino: {status.arduinoConnected ? 'Connected' : 'Not Connected'}
            </span>
          </div>
          {status.port && (
            <p className="text-sm text-gray-600 ml-5">Port: {status.port}</p>
          )}
        </div>
      )}

      {/* Controls */}
      {status.connected && (
        <div className="space-y-2">
          {!status.arduinoConnected ? (
            <div className="space-x-2">
              <button
                onClick={connectArduino}
                disabled={isConnecting}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
              >
                {isConnecting ? 'Connecting...' : 'Connect Arduino'}
              </button>
              <button
                onClick={scanPorts}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Scan Ports
              </button>
            </div>
          ) : (
            <button
              onClick={disconnectArduino}
              className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              Disconnect Arduino
            </button>
          )}
          
          <button
            onClick={runDemoSimulation}
            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
          >
            Run Demo Simulation
          </button>
        </div>
      )}

      {/* Available Ports */}
      {availablePorts.length > 0 && (
        <div className="mt-4">
          <h4 className="font-medium mb-2">Available Ports:</h4>
          <ul className="text-sm">
            {availablePorts.map((port, index) => (
              <li key={index} className="text-gray-600">• {port}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Installation Instructions */}
      {!status.connected && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <h4 className="font-medium text-yellow-800 mb-2">🚀 Get Started:</h4>
          <ol className="text-sm text-yellow-700 space-y-1">
            <li>1. Download CtrlHub Agent from our website</li>
            <li>2. Run the installer</li>
            <li>3. Start CtrlHub Agent on your computer</li>
            <li>4. Connect your Arduino via USB</li>
            <li>5. Reload this page</li>
          </ol>
        </div>
      )}
    </div>
  );
};

export default CtrlHubAgentStatus;
