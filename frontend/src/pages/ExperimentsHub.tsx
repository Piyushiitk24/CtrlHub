import React from 'react';
import { Link } from 'react-router-dom';
import { NAV } from '../nav';

const ExperimentsHub: React.FC = () => {
  // Get experiments from centralized navigation structure
  const experimentsHub = NAV.hubs.find(hub => hub.path === '/experiments');
  const experiments = experimentsHub?.children || [];

  // Icon mapping for each experiment
  const experimentIcons: { [key: string]: string } = {
    '/experiments/rotary-inverted-pendulum': '🪁',
    '/experiments/ball-and-beam': '🟡', 
    '/experiments/cart-pole': '🚃',
    '/experiments/dc-servo-speed': '⚡',
    '/experiments/dc-motor-pid': '🎛️',
    '/experiments/maglev': '🧲',
    '/experiments/furuta-pendulum': '🌀',
  };

  return (
    <>
      <p className="home-subtitle">Pick a classic benchmark to explore and validate.</p>
      <div className="modules-grid" style={{ maxWidth: '1100px' }}>
        {experiments.map((experiment) => (
          <Link key={experiment.path} to={experiment.path} className="module-card" style={{ textDecoration: 'none' }}>
            <div className="module-icon">{experimentIcons[experiment.path] || '🧪'}</div>
            <div className="module-title">{experiment.title}</div>
            <p className="module-description">{experiment.description}</p>
          </Link>
        ))}
      </div>
    </>
  );
};

export default ExperimentsHub;
