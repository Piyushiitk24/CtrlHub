import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { NavNode } from '../../nav';

interface CollapsibleSidebarProps {
  sections: NavNode[];
  title: string;
  className?: string;
}

const CollapsibleSidebar: React.FC<CollapsibleSidebarProps> = ({ 
  sections, 
  title, 
  className = '' 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const { pathname } = useLocation();

  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth <= 768);
      // Auto-close on mobile when navigating
      if (window.innerWidth <= 768) {
        setIsOpen(false);
      }
    };

    checkIsMobile();
    window.addEventListener('resize', checkIsMobile);
    return () => window.removeEventListener('resize', checkIsMobile);
  }, []);

  // Auto-close sidebar on mobile when route changes
  useEffect(() => {
    if (isMobile) {
      setIsOpen(false);
    }
  }, [pathname, isMobile]);

  if (sections.length === 0) return null;

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape' && isOpen) {
      setIsOpen(false);
    }
  };

  return (
    <div className={`collapsible-sidebar ${className}`}>
      {/* Toggle Button - visible on mobile or when sidebar can be collapsed */}
      <button
        className={`sidebar-toggle ${isOpen ? 'active' : ''}`}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        aria-expanded={isOpen}
        aria-label={`${isOpen ? 'Close' : 'Open'} ${title} navigation`}
      >
        <span className="toggle-icon">
          {isOpen ? '✕' : '☰'}
        </span>
        <span className="toggle-text">
          {isOpen ? 'Close Menu' : `${title} Sections`}
        </span>
      </button>

      {/* Sidebar Content */}
      <div className={`sidebar-content ${isOpen ? 'open' : ''} ${isMobile ? 'mobile' : 'desktop'}`}>
        <div className="sidebar-header">
          <h4 className="sidebar-title">{title}</h4>
          {isMobile && (
            <button
              className="sidebar-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close navigation"
            >
              ✕
            </button>
          )}
        </div>

        <nav className="sidebar-nav" role="navigation">
          <ul className="sidebar-sections">
            {sections.map((section, index) => {
              const isActive = pathname === section.path;
              return (
                <li key={section.path} className="sidebar-section-item">
                  <Link
                    to={section.path}
                    className={`sidebar-section-link ${isActive ? 'active' : ''}`}
                    onClick={() => isMobile && setIsOpen(false)}
                  >
                    <span className="section-index">{index + 1}</span>
                    <span className="section-title">{section.title}</span>
                    {isActive && <span className="active-indicator">●</span>}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="sidebar-footer">
          <div className="progress-summary">
            {sections.findIndex(s => s.path === pathname) + 1} of {sections.length} sections
          </div>
        </div>
      </div>

      {/* Mobile Overlay */}
      {isMobile && isOpen && (
        <div 
          className="sidebar-overlay"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}
    </div>
  );
};

export default CollapsibleSidebar;