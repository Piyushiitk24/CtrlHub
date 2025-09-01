import React from 'react';
import { Link } from 'react-router-dom';

const Driver: React.FC = () => (
  <div className="study-container single-pane">
    <div className="study-header">
      <Link to="/components" className="back-button">← Back</Link>
      <h2 className="study-title">Motor Driver</h2>
    </div>
    <div className="study-content">
      <div className="section">
        <h3>Overview</h3>
        <p>H‑bridges, PWM strategies, current limits, and protection circuits.</p>
      </div>
    </div>
  </div>
);

export default Driver;
