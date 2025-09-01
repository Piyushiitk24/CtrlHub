import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Breadcrumbs from '../components/Breadcrumbs';
import { findHub } from '../nav';

interface HubLayoutProps {
  title: string;
}

const HubLayout: React.FC<HubLayoutProps> = ({ title }) => {
  const location = useLocation();
  const hub = findHub(location.pathname);

  return (
    <div className="hub-container" style={{ '--hub-color': hub?.color || '#6c757d' } as React.CSSProperties}>
      <Breadcrumbs />
      <h2 className="hub-title">{title}</h2>
      <Outlet />
    </div>
  );
};

export default HubLayout;