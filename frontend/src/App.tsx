import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import RootLayout from './layouts/RootLayout';
import HubLayout from './layouts/HubLayout';
import ComponentLayout from './layouts/ComponentLayout';
import './index.css';

// Lazy load components for better performance
const Home = lazy(() => import('./pages/Home'));
const ComponentsHub = lazy(() => import('./pages/ComponentsHub'));
const ExperimentsHub = lazy(() => import('./pages/ExperimentsHub'));
const OpticsMockup = lazy(() => import('./pages/OpticsMockup'));
const DCMotor = lazy(() => import('./pages/components/dc-motor/DCMotor'));
const DCMotorSimulink = lazy(() => import('./pages/components/dc-motor/SimulinkFirstPrinciples'));
const DCMotorTransfer = lazy(() => import('./pages/components/dc-motor/TransferFunctionAndSimulink'));
const DCMotorParameters = lazy(() => import('./pages/components/dc-motor/ParameterExtraction'));
const DCMotorPID = lazy(() => import('./pages/experiments/DCMotorPID'));
const Experiment = lazy(() => import('./pages/experiments/Placeholder'));

const App: React.FC = () => {
  return (
    <Router>
      <Suspense fallback={
        <div className="app-container home-container">
          <div className="loading-container">
            <div className="spinner" />
            <span className="loading-text">Loading CtrlHub...</span>
          </div>
        </div>
      }>
        <Routes>
          <Route element={<RootLayout />}>
            <Route index element={<Home />} />
            <Route path="components" element={<HubLayout title="Components" />}>
              <Route index element={<ComponentsHub />} />
              <Route path="dc-motor" element={<ComponentLayout title="DC Motor" />}>
                <Route index element={<DCMotor />} />
                <Route path="simulink-first-principles" element={<DCMotorSimulink />} />
                <Route path="transfer-function-and-simulink" element={<DCMotorTransfer />} />
                <Route path="parameter-extraction" element={<DCMotorParameters />} />
              </Route>
            </Route>
            <Route path="experiments" element={<HubLayout title="Experiments" />}>
              <Route index element={<ExperimentsHub />} />
              {/* All experiment routes now handled by Placeholder component */}
              <Route path=":slug" element={<Experiment />} />
            </Route>
            <Route path="optics" element={<HubLayout title="Optics" />}>
              <Route index element={<OpticsMockup />} />
            </Route>
          </Route>
        </Routes>
      </Suspense>
    </Router>
  );
};

export default App;