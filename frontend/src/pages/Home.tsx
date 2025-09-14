import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="App home-container">
      <h1 className="home-title">CTRLHUB</h1>
      <p className="home-subtitle">Single-entry demo with local agent integration.</p>

      <div className="modules-grid" style={{ maxWidth: '780px' }}>
        <Link to="/experiments/rotary-inverted-pendulum" className="module-card" style={{ textDecoration: 'none' }}>
          <div className="module-icon">🧪</div>
          <div className="module-title">Experiments</div>
          <p className="module-description">
            Open the Rotary Inverted Pendulum experiment. Connect to the local Python agent and run.
          </p>
          <div className="module-actions">
            <span className="btn btn-secondary">Open Experiment</span>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default Home;
