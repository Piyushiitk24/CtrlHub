import React from 'react';
import { useParams, Link } from 'react-router-dom';
import RotaryInvertedPendulum from './RotaryInvertedPendulum';
import DCMotorPID from './DCMotorPID';

const Placeholder: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();

  // Route to appropriate experiment component based on slug
  switch (slug) {
    case 'rotary-inverted-pendulum':
      return <RotaryInvertedPendulum />;
    case 'dc-motor-pid':
      return <DCMotorPID />;
    case 'ball-and-beam':
      return <BallAndBeamPlaceholder />;
    case 'cart-pole':
      return <CartPolePlaceholder />;
    case 'dc-servo-speed':
      return <DCServoSpeedPlaceholder />;
    case 'maglev':
      return <MaglevPlaceholder />;
    case 'furuta-pendulum':
      return <FurutaPendulumPlaceholder />;
    default:
      return <DefaultPlaceholder slug={slug} />;
  }
};

// Individual placeholders for each experiment
const BallAndBeamPlaceholder: React.FC = () => (
  <div className="experiment-container">
    <div className="experiment-header">
      <h1>🟡 Ball & Beam Experiment</h1>
      <p className="experiment-description">
        Positioning with nonlinear dynamics - balance a ball on a beam using angular control.
      </p>
    </div>
    <div className="coming-soon-card">
      <h3>🚧 Under Development</h3>
      <p>This experiment is being implemented with:</p>
      <ul>
        <li>Nonlinear dynamics modeling</li>
        <li>Linearization techniques</li>
        <li>PID and advanced control strategies</li>
        <li>Real-time hardware simulation</li>
      </ul>
      <Link to="/experiments" className="btn btn-secondary">← Back to Experiments</Link>
    </div>
  </div>
);

const CartPolePlaceholder: React.FC = () => (
  <div className="experiment-container">
    <div className="experiment-header">
      <h1>🚃 Cart-Pole Experiment</h1>
      <p className="experiment-description">
        Benchmark stabilization and control - classic inverted pendulum on a cart.
      </p>
    </div>
    <div className="coming-soon-card">
      <h3>🚧 Under Development</h3>
      <p>This experiment will feature:</p>
      <ul>
        <li>State-space modeling and LQR control</li>
        <li>Swing-up and stabilization modes</li>
        <li>Real-time control implementation</li>
        <li>Performance comparison metrics</li>
      </ul>
      <Link to="/experiments" className="btn btn-secondary">← Back to Experiments</Link>
    </div>
  </div>
);

const DCServoSpeedPlaceholder: React.FC = () => (
  <div className="experiment-container">
    <div className="experiment-header">
      <h1>⚡ DC Servo Speed Control</h1>
      <p className="experiment-description">
        PID tuning and step response analysis for precise speed control.
      </p>
    </div>
    <div className="coming-soon-card">
      <h3>🚧 Under Development</h3>
      <p>This experiment will include:</p>
      <ul>
        <li>Speed control loop design</li>
        <li>PID auto-tuning algorithms</li>
        <li>Disturbance rejection testing</li>
        <li>Performance metrics analysis</li>
      </ul>
      <Link to="/experiments" className="btn btn-secondary">← Back to Experiments</Link>
    </div>
  </div>
);

const MaglevPlaceholder: React.FC = () => (
  <div className="experiment-container">
    <div className="experiment-header">
      <h1>🧲 Magnetic Levitation</h1>
      <p className="experiment-description">
        Levitation dynamics and control - suspend objects using electromagnetic force.
      </p>
    </div>
    <div className="coming-soon-card">
      <h3>🚧 Under Development</h3>
      <p>This experiment will demonstrate:</p>
      <ul>
        <li>Electromagnetic modeling</li>
        <li>Unstable system stabilization</li>
        <li>Sensor fusion and feedback</li>
        <li>Advanced control techniques</li>
      </ul>
      <Link to="/experiments" className="btn btn-secondary">← Back to Experiments</Link>
    </div>
  </div>
);

const FurutaPendulumPlaceholder: React.FC = () => (
  <div className="experiment-container">
    <div className="experiment-header">
      <h1>🌀 Furuta Pendulum</h1>
      <p className="experiment-description">
        Underactuated control strategies - rotary inverted pendulum with energy-based control.
      </p>
    </div>
    <div className="coming-soon-card">
      <h3>🚧 Under Development</h3>
      <p>This experiment will cover:</p>
      <ul>
        <li>Energy-based control methods</li>
        <li>Partial feedback linearization</li>
        <li>Swing-up and stabilization</li>
        <li>Underactuated system analysis</li>
      </ul>
      <Link to="/experiments" className="btn btn-secondary">← Back to Experiments</Link>
    </div>
  </div>
);

const DefaultPlaceholder: React.FC<{ slug?: string }> = ({ slug }) => (
  <div className="experiment-container">
    <div className="experiment-header">
      <h1>🧪 Experiment: {slug}</h1>
      <p className="experiment-description">This experiment is not yet implemented.</p>
    </div>
    <div className="coming-soon-card">
      <h3>Available Experiments:</h3>
      <ul>
        <li>Rotary Inverted Pendulum ✅</li>
        <li>DC Motor PID Control ✅</li>
        <li>Ball & Beam 🚧</li>
        <li>Cart-Pole 🚧</li>
        <li>DC Servo Speed 🚧</li>
        <li>MagLev 🚧</li>
        <li>Furuta Pendulum 🚧</li>
      </ul>
      <Link to="/experiments" className="btn btn-secondary">← Back to Experiments</Link>
    </div>
  </div>
);

export default Placeholder;

/* Coming Soon Placeholders */
.coming-soon-card {
  background: var(--charcoal);
  border: 2px solid var(--accent-orange);
  border-radius: 12px;
  padding: 2rem;
  margin: 2rem 0;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.coming-soon-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    45deg,
    rgba(255, 107, 53, 0.1) 0%,
    rgba(255, 204, 2, 0.1) 50%,
    rgba(0, 255, 65, 0.1) 100%
  );
  pointer-events: none;
}

.coming-soon-card h3 {
  color: var(--accent-orange);
  font-family: 'Orbitron', monospace;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  text-shadow: 0 0 10px var(--shadow-orange);
}

.coming-soon-card p {
  color: var(--paper-white);
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.coming-soon-card ul {
  text-align: left;
  max-width: 400px;
  margin: 0 auto 2rem auto;
  color: var(--paper-white);
}

.coming-soon-card li {
  margin: 0.5rem 0;
  padding-left: 1rem;
  position: relative;
}

.coming-soon-card li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: var(--primary-green);
  font-weight: bold;
}

.experiment-header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.experiment-header::after {
  content: '';
  position: absolute;
  bottom: -1rem;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, var(--primary-green), var(--accent-orange));
  box-shadow: 0 0 10px var(--shadow-green);
}

.experiment-header h1 {
  font-family: 'Orbitron', monospace;
  color: var(--primary-green);
  font-size: 2.5rem;
  margin-bottom: 1rem;
  text-shadow: 0 0 20px var(--shadow-green);
}

.experiment-description {
  font-size: 1.2rem;
  color: var(--paper-white);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}
