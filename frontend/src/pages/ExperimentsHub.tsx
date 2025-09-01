import React from 'react';
import { Link } from 'react-router-dom';

const experiments = [
  { path: '/experiments/rotary-inverted-pendulum', icon: '🪁', title: 'Rotary Inverted Pendulum', desc: 'Swing‑up and stabilization control.' },
  { path: '/experiments/ball-and-beam', icon: '🟡', title: 'Ball & Beam', desc: 'Positioning with nonlinear dynamics.' },
  { path: '/experiments/cart-pole', icon: '🚃', title: 'Cart‑Pole', desc: 'Benchmark stabilization and control.' },
  { path: '/experiments/dc-servo-speed', icon: '⚡', title: 'DC Servo Speed', desc: 'PID tuning and step response analysis.' },
  { path: '/experiments/maglev', icon: '🧲', title: 'MagLev', desc: 'Levitation dynamics and control.' },
  { path: '/experiments/furuta-pendulum', icon: '🌀', title: 'Furuta Pendulum', desc: 'Underactuated control strategies.' },
];

const ExperimentsHub: React.FC = () => {
  return (
    <>
      <p className="home-subtitle">Pick a classic benchmark to explore and validate.</p>
      <div className="modules-grid" style={{ maxWidth: '1100px' }}>
        {experiments.map(({ path, icon, title, desc }) => (
          <Link key={path} to={path} className="module-card" style={{ textDecoration: 'none' }}>
            <div className="module-icon">{icon}</div>
            <div className="module-title">{title}</div>
            <p className="module-description">{desc}</p>
          </Link>
        ))}
      </div>
    </>
  );
};

export default ExperimentsHub;
