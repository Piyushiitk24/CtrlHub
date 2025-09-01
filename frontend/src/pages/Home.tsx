import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="App home-container">
      <h1 className="home-title">CtrlHub</h1>
      <p className="home-subtitle">
        Choose where to begin: explore raw components or dive into experiments.
      </p>

      <div className="modules-grid" style={{ maxWidth: '1100px' }}>
        <Link to="/components" className="module-card" style={{ textDecoration: 'none' }}>
          <div className="module-icon">🧩</div>
          <div className="module-title">Components Library</div>
          <p className="module-description">
            DC Motor, Driver, Stepper Motor, Encoder, Arduino. Study theory, models, and hands‑on wiring.
          </p>
          <div className="module-actions">
            <span className="btn btn-primary">Enter Components</span>
          </div>
        </Link>

        <Link to="/experiments" className="module-card" style={{ textDecoration: 'none' }}>
          <div className="module-icon">🧪</div>
          <div className="module-title">Experiments</div>
          <p className="module-description">
            Work through classic control problems with simulations and hardware validation.
          </p>
          <div className="module-actions">
            <span className="btn btn-secondary">Open Experiments</span>
          </div>
        </Link>

        <Link to="/optics" className="module-card" style={{ textDecoration: 'none' }}>
          <div className="module-icon">🔭</div>
          <div className="module-title">Optics</div>
          <p className="module-description">
            Imaging, wave optics, photonics hardware. Concept → simulation → lab.
          </p>
          <div className="module-actions">
            <span className="btn btn-primary">Explore</span>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default Home;
