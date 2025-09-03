import React, { Suspense, lazy, useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import ComponentsHub from './pages/ComponentsHub';
import ExperimentsHub from './pages/ExperimentsHub';
import DCMotor from './pages/components/DCMotor';
import Driver from './pages/components/Driver';
import StepperMotor from './pages/components/StepperMotor';
import Encoder from './pages/components/Encoder';
import Arduino from './pages/components/Arduino';
import OpticsHub from './pages/OpticsHub';
import RootLayout from './layouts/RootLayout';
import HubLayout from './layouts/HubLayout';
import ComponentLayout from './layouts/ComponentLayout';
import LocalAgentHandler from './utils/LocalAgentHandler';
import './index.css';

const DCMotorSimulink = lazy(() => import('./pages/components/dc-motor/SimulinkFirstPrinciples'));
const DCMotorTF = lazy(() => import('./pages/components/dc-motor/TransferFunctionTF'));
const DCMotorHardware = lazy(() => import('./pages/components/dc-motor/HardwareBuild'));
const DCMotorParameters = lazy(() => import('./pages/components/dc-motor/ParameterExtraction'));
const DCMotorPID = lazy(() => import('./pages/experiments/DCMotorPID'));
const Experiment = lazy(() => import('./pages/experiments/Placeholder'));

const App: React.FC = () => {
  const [agent, setAgent] = useState<LocalAgentHandler | null>(null);
  const [agentConnected, setAgentConnected] = useState(false);

  useEffect(() => {
    const agentHandler = new LocalAgentHandler();
    setAgent(agentHandler);

    const checkConnection = async () => {
      const connected = await agentHandler.checkLocalAgent();
      setAgentConnected(connected);
    };

    checkConnection();
    const interval = setInterval(checkConnection, 5000); // Check every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <Router>
      <Suspense fallback={<div className="app-container home-container"><div className="spinner" /> Loading...</div>}>
        <div className="agent-status-indicator" style={{ backgroundColor: agentConnected ? '#28a745' : '#dc3545' }}>
          <span className="status-dot"></span>
          {agentConnected ? 'Agent Connected' : 'Agent Disconnected'}
        </div>
        <Routes>
          <Route element={<RootLayout />}>
            <Route index element={<Home />} />
            <Route path="components" element={<HubLayout title="Components" />}>
              <Route index element={<ComponentsHub />} />
              <Route path="dc-motor" element={<ComponentLayout title="DC Motor" />}>
                <Route index element={<DCMotor />} />
                <Route path="simulink-first-principles" element={<DCMotorSimulink />} />
                <Route path="transfer-function-and-simulink" element={<DCMotorTF />} />
                <Route path="hardware-build" element={<DCMotorHardware />} />
                <Route path="parameter-extraction" element={<DCMotorParameters />} />
              </Route>
              <Route path="driver" element={<Driver />} />
              <Route path="stepper-motor" element={<StepperMotor />} />
              <Route path="encoder" element={<Encoder />} />
              <Route path="arduino" element={<Arduino />} />
            </Route>
            <Route path="experiments" element={<HubLayout title="Experiments" />}>
              <Route index element={<ExperimentsHub />} />
              <Route path="dc-motor-pid" element={<DCMotorPID />} />
              <Route path=":slug" element={<Experiment />} />
            </Route>
            <Route path="optics" element={<HubLayout title="Optics" />}>
              <Route index element={<OpticsHub />} />
            </Route>
          </Route>
        </Routes>
      </Suspense>
    </Router>
  );
};

export default App;