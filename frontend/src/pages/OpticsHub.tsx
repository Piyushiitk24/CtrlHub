import React from 'react';
import { Link } from 'react-router-dom';

const opticsModules = [
  { icon: '🔭', title: 'Lenses & Imaging', desc: 'Thin lens, focal length, magnification, ray diagrams.' },
  { icon: '🌈', title: 'Wave Optics', desc: 'Interference, diffraction, polarization, and coherence.' },
  { icon: '🪞', title: 'Mirrors & Beams', desc: 'Gaussian beams, reflections, cavity basics.' },
  { icon: '🔦', title: 'Photonics Hardware', desc: 'Lasers, detectors, optical mounts, and alignment.' },
];

const OpticsHub: React.FC = () => {
  return (
    <>
      <p className="home-subtitle">Explore foundational optics and photonics — theory to practice.</p>
      <div className="modules-grid" style={{ maxWidth: '1100px' }}>
        {opticsModules.map(({ icon, title, desc }) => (
          <div key={title} className="module-card">
            <div className="module-icon">{icon}</div>
            <div className="module-title">{title}</div>
            <p className="module-description">{desc}</p>
            <div className="module-actions">
              <span className="btn btn-primary">Explore</span>
            </div>
          </div>
        ))}
      </div>
    </>
  );
};

export default OpticsHub;
