import React from 'react';
import { NavLink } from 'react-router-dom';

const TopNav: React.FC = () => {
  return (
    <header className="app-topnav">
      <nav className="topnav-inner">
        <NavLink to="/" className="topnav-logo">CtrlHub</NavLink>
        <div className="topnav-links">
          <NavLink to="/components" className={({ isActive }) => isActive ? 'topnav-link active' : 'topnav-link'}>Components</NavLink>
          <NavLink to="/experiments" className={({ isActive }) => isActive ? 'topnav-link active' : 'topnav-link'}>Experiments</NavLink>
          <NavLink to="/optics" className={({ isActive }) => isActive ? 'topnav-link active' : 'topnav-link'}>Optics</NavLink>
        </div>
      </nav>
    </header>
  );
};

export default TopNav;
