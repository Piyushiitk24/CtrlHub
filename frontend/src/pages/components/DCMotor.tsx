import React from 'react';
import { Link } from 'react-router-dom';

const DCMotor: React.FC = () => {
  return (
    <>
      <div className="section">
        <h3>Learning Path</h3>
        <div>
          <Link to="/components/dc-motor/simulink-first-principles" className="btn btn-primary">1) Simulink from First Principles</Link>
          <Link to="/components/dc-motor/transfer-function-and-simulink" className="btn btn-primary">2) Transfer Function & Simulink TF</Link>
          <Link to="/components/dc-motor/hardware-build" className="btn btn-primary">3) Build Hardware (Arduino + L298N + Encoder)</Link>
          <Link to="/components/dc-motor/parameter-extraction" className="btn btn-primary">4) Extract Parameters (No Datasheet)</Link>
        </div>
        <div className="alert alert-info">
          “C’mon, you bought it from the black market — that datasheet’s fiction. Let’s measure the truth.”
        </div>
      </div>

      <div className="section">
        <h3>Parameter Extraction Topics</h3>
        <ul>
          <li>Finding R and L</li>
          <li>Estimating rotor inertia J</li>
          <li>Calculating Kt (torque constant) and Ke (back‑EMF constant)</li>
          <li>Back‑EMF measurement and validation</li>
          <li>Coast‑down test: slope analysis and steady‑state speed tests</li>
        </ul>
      </div>
    </>
  );
};

export default DCMotor;
