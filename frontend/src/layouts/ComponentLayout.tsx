import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Breadcrumbs from '../components/Breadcrumbs';
import BookmarkButton from '../components/navigation/BookmarkButton';
import { findHub } from '../nav';

interface ComponentLayoutProps {
  title: string;
}

const ComponentLayout: React.FC<ComponentLayoutProps> = ({ title }) => {
  const location = useLocation();
  const hub = findHub(location.pathname);

  return (
    <div className="component-container" style={{ '--hub-color': hub?.color || '#6c757d' } as React.CSSProperties}>
      <Breadcrumbs />
      <div className="page-header" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <h2 className="component-title">{title}</h2>
        <BookmarkButton title={title} />
      </div>
      <Outlet />
    </div>
  );
};

export default ComponentLayout;