import React from 'react';
import { Link } from 'react-router-dom';

const Arduino: React.FC = () => (
  <div className="study-container single-pane">
    <div className="study-header">
      <Link to="/components" className="back-button">← Back</Link>
      <h2 className="study-title">Arduino</h2>
    </div>
    <div className="study-content">
      <div className="section">
        <h3>Overview</h3>
        <p>Pinouts, serial protocol design, and timing considerations for control loops.</p>
      </div>
    </div>
  </div>
);

export default Arduino;
