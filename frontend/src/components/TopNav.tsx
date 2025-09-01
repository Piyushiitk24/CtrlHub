import React, { useState, useEffect, useRef } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { findHub } from '../nav';
import BookmarkList from './navigation/BookmarkList';

const TopNav: React.FC = () => {
  const location = useLocation();
  const hub = findHub(location.pathname);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [agentConnected, setAgentConnected] = useState(false);
  const hamburgerRef = useRef<HTMLButtonElement>(null);
  const drawerRef = useRef<HTMLDivElement>(null);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  useEffect(() => {
    setIsMenuOpen(false);
  }, [location.pathname]);

  // Check agent connection status
  useEffect(() => {
    const checkAgentStatus = async () => {
      try {
        const response = await fetch('http://localhost:8003/health');
        setAgentConnected(response.ok);
      } catch {
        setAgentConnected(false);
      }
    };

    checkAgentStatus();
    const interval = setInterval(checkAgentStatus, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, []);

  // Focus management for mobile menu
  useEffect(() => {
    if (isMenuOpen) {
      const firstElement = drawerRef.current?.querySelector('a, button');
      if (firstElement instanceof HTMLElement) {
        firstElement.focus();
      }
    } else {
      hamburgerRef.current?.focus();
    }
  }, [isMenuOpen]);

  return (
    <header className="app-topnav" style={{ '--hub-color': hub?.color } as React.CSSProperties}>
      <nav className="topnav-inner">
        <NavLink to="/" className="topnav-logo">
          <span className="logo-icon">⚙️</span>
          CtrlHub
        </NavLink>
        
        {/* Desktop Navigation */}
        <div className="topnav-center">
          <div className="topnav-links">
            <NavLink to="/components" className={({ isActive }) => (isActive ? 'topnav-link active' : 'topnav-link')}>
              Components
            </NavLink>
            <NavLink to="/experiments" className={({ isActive }) => (isActive ? 'topnav-link active' : 'topnav-link')}>
              Experiments
            </NavLink>
            <NavLink to="/optics" className={({ isActive }) => (isActive ? 'topnav-link active' : 'topnav-link')}>
              Optics
            </NavLink>
          </div>
        </div>

        {/* Right side utilities */}
        <div className="topnav-utilities">
          <div className="agent-status">
            <div className={`status-indicator ${agentConnected ? 'connected' : 'disconnected'}`}></div>
            <span className="status-text">Agent {agentConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <BookmarkList />
          <button 
            ref={hamburgerRef} 
            className={`topnav-hamburger ${isMenuOpen ? 'open' : ''}`} 
            onClick={toggleMenu} 
            aria-label="Toggle menu" 
            aria-expanded={isMenuOpen}
          >
            <span className="hamburger-line"></span>
            <span className="hamburger-line"></span>
            <span className="hamburger-line"></span>
          </button>
        </div>
      </nav>

      {/* Mobile overlay */}
      <div 
        className={`nav-overlay ${isMenuOpen ? 'open' : ''}`} 
        onClick={toggleMenu} 
        aria-hidden="true"
      />
      
      {/* Mobile drawer */}
      <div ref={drawerRef} className={`mobile-nav-drawer ${isMenuOpen ? 'open' : ''}`}>
        <div className="mobile-nav-header">
          <span className="mobile-logo">⚙️ CtrlHub</span>
          <button className="close-drawer" onClick={toggleMenu} aria-label="Close menu">
            ✕
          </button>
        </div>
        <div className="mobile-nav-links">
          <NavLink to="/components" className={({ isActive }) => (isActive ? 'mobile-nav-link active' : 'mobile-nav-link')} onClick={toggleMenu}>
            <span className="nav-icon">🔧</span>
            Components
          </NavLink>
          <NavLink to="/experiments" className={({ isActive }) => (isActive ? 'mobile-nav-link active' : 'mobile-nav-link')} onClick={toggleMenu}>
            <span className="nav-icon">🧪</span>
            Experiments
          </NavLink>
          <NavLink to="/optics" className={({ isActive }) => (isActive ? 'mobile-nav-link active' : 'mobile-nav-link')} onClick={toggleMenu}>
            <span className="nav-icon">🔍</span>
            Optics
          </NavLink>
        </div>
        <div className="mobile-nav-footer">
          <div className={`mobile-agent-status ${agentConnected ? 'connected' : 'disconnected'}`}>
            <div className="status-indicator"></div>
            Agent {agentConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopNav;
