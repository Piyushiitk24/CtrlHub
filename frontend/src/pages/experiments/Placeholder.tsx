import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import Breadcrumbs from '../../components/Breadcrumbs';

const Placeholder: React.FC = () => {
  const { pathname } = useLocation();
  const name = pathname.replace('/experiments/', '').replace(/-/g, ' ').toUpperCase();
  return (
    <div className="study-container single-pane">
      <div className="study-header">
        <Link to="/experiments" className="back-button">← Back</Link>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <Breadcrumbs />
          <h2 className="study-title">{name}</h2>
        </div>
      </div>
      <div className="study-content">
        <div className="section">
          <h3>Overview</h3>
          <p>Placeholder content for {name}. We’ll add models, control design steps, and hardware notes here.</p>
        </div>
      </div>
    </div>
  );
};

export default Placeholder;
