import React from 'react';
import { Link } from 'react-router-dom';

const StepperMotor: React.FC = () => (
  <div className="study-container single-pane">
    <div className="study-header">
      <Link to="/components" className="back-button">← Back</Link>
      <h2 className="study-title">Stepper Motor</h2>
    </div>
    <div className="study-content">
      <div className="section">
        <h3>Overview</h3>
        <p>Full‑step, half‑step, and microstepping control with current regulation.</p>
      </div>
    </div>
  </div>
);

export default StepperMotor;
