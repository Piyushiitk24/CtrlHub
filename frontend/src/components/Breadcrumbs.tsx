import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { NAV, findByPath, findHub } from '../nav';
import { FaHome, FaChevronRight } from 'react-icons/fa';

const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const parts = location.pathname.split('/').filter(Boolean);
  const crumbs: { label: string; to: string; icon?: React.ReactNode }[] = [];
  
  let acc = '';
  for (const p of parts) {
    acc += `/${p}`;
    const node = findByPath(NAV.hubs, acc);
    if (node) {
      crumbs.push({ 
        label: node.title, 
        to: acc,
        icon: node.icon 
      });
    }
  }
  
  const items = [
    { label: 'Home', to: '/', icon: <FaHome /> }, 
    ...crumbs
  ];
  
  const hub = findHub(location.pathname);

  // Don't show breadcrumbs on home page
  if (location.pathname === '/') {
    return null;
  }

  return (
    <div className="breadcrumbs-container">
      <nav 
        className="breadcrumbs" 
        aria-label="Breadcrumb navigation" 
        style={{ '--hub-color': hub?.color } as React.CSSProperties}
      >
        <div className="breadcrumbs-inner">
          {items.map((crumb, index) => {
            const isLast = index === items.length - 1;
            return (
              <span key={crumb.to} className="breadcrumb-item">
                {isLast ? (
                  <span className="breadcrumb-current" aria-current="page">
                    {crumb.icon && <span className="breadcrumb-icon">{crumb.icon}</span>}
                    <span className="breadcrumb-text">{crumb.label}</span>
                  </span>
                ) : (
                  <Link 
                    to={crumb.to} 
                    className="breadcrumb-link"
                    title={`Navigate to ${crumb.label}`}
                  >
                    {crumb.icon && <span className="breadcrumb-icon">{crumb.icon}</span>}
                    <span className="breadcrumb-text">{crumb.label}</span>
                  </Link>
                )}
                {!isLast && (
                  <FaChevronRight className="breadcrumb-separator" aria-hidden="true" />
                )}
              </span>
            );
          })}
        </div>
        
        {/* Grid pattern overlay for retro aesthetics */}
        <div className="breadcrumbs-grid" aria-hidden="true"></div>
      </nav>
    </div>
  );
};

export default Breadcrumbs;
