import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => (
  <div className="study-container single-pane">
    <div className="study-header">
      <h2 className="study-title">404 — Navigation Error</h2>
    </div>
    <div className="study-content">
      <div className="section">
        <h3>⚠️ Path Not Found</h3>
        <p>The requested route doesn't exist in our navigation system. Let's get you back on track:</p>
        
        <div className="navigation-shortcuts">
          <div className="shortcut-group">
            <h4>🧩 Components</h4>
            <div className="shortcut-links">
              <Link to="/components" className="btn btn-primary">Browse All Components</Link>
              <Link to="/components/dc-motor" className="btn btn-small">DC Motor Studies</Link>
              <Link to="/components/driver" className="btn btn-small">Motor Driver</Link>
            </div>
          </div>
          
          <div className="shortcut-group">
            <h4>🧪 Experiments</h4>
            <div className="shortcut-links">
              <Link to="/experiments" className="btn btn-secondary">Browse Experiments</Link>
              <Link to="/experiments/rotary-inverted-pendulum" className="btn btn-small">Rotary Pendulum</Link>
              <Link to="/experiments/cart-pole" className="btn btn-small">Cart-Pole</Link>
            </div>
          </div>
          
          <div className="shortcut-group">
            <h4>🔭 Optics</h4>
            <div className="shortcut-links">
              <Link to="/optics" className="btn btn-primary">Explore Optics</Link>
            </div>
          </div>
        </div>
        
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <Link to="/" className="btn btn-success">🏠 Return to Home</Link>
        </div>
      </div>
    </div>
  </div>
);

export default NotFound;