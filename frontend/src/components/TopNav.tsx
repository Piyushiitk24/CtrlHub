import React, { useState, useEffect, useRef } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { findHub } from '../nav';
import BookmarkList from './navigation/BookmarkList';

const TopNav: React.FC = () => {
  const location = useLocation();
  const hub = findHub(location.pathname);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const hamburgerRef = useRef<HTMLButtonElement>(null);
  const drawerRef = useRef<HTMLDivElement>(null);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  useEffect(() => {
    setIsMenuOpen(false);
  }, [location.pathname]);

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
        <NavLink to="/" className="topnav-logo">CtrlHub</NavLink>
        <div className="topnav-links">
          <NavLink to="/components" className={({ isActive }) => (isActive ? 'topnav-link active' : 'topnav-link')}>Components</NavLink>
          <NavLink to="/experiments" className={({ isActive }) => (isActive ? 'topnav-link active' : 'topnav-link')}>Experiments</NavLink>
          <NavLink to="/optics" className={({ isActive }) => (isActive ? 'topnav-link active' : 'topnav-link')}>Optics</NavLink>
          <BookmarkList />
        </div>
        <button ref={hamburgerRef} className="topnav-hamburger" onClick={toggleMenu} aria-label="Toggle menu" aria-expanded={isMenuOpen}>
          <span className="line" />
          <span className="line" />
          <span className="line" />
        </button>
      </nav>
      <div className={`nav-overlay ${isMenuOpen ? 'open' : ''}`} onClick={toggleMenu} role="button" tabIndex={-1} />
      <div ref={drawerRef} className={`mobile-nav-drawer ${isMenuOpen ? 'open' : ''}`}>
        <NavLink to="/components" className={({ isActive }) => (isActive ? 'topnav-link active' : 'topnav-link')} onClick={toggleMenu}>
            Components
          </NavLink>
        <NavLink to="/experiments" className={({ isActive }) => (isActive ? 'topnav-link active' : 'topnav-link')} onClick={toggleMenu}>
            Experiments
          </NavLink>
        <NavLink to="/optics" className={({ isActive }) => (isActive ? 'topnav-link active' : 'topnav-link')} onClick={toggleMenu}>
            Optics
          </NavLink>
      </div>
    </header>
  );
};

export default TopNav;
