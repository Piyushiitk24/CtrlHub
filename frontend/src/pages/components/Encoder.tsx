import React from 'react';
import { Link } from 'react-router-dom';

const Encoder: React.FC = () => (
  <div className="study-container single-pane">
    <div className="study-header">
      <Link to="/components" className="back-button">← Back</Link>
      <h2 className="study-title">Encoder</h2>
    </div>
    <div className="study-content">
      <div className="section">
        <h3>Overview</h3>
        <p>Quadrature decoding, noise filtering, and resolution trade‑offs.</p>
      </div>
    </div>
  </div>
);

export default Encoder;
