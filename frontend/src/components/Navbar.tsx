import React, { useState, useEffect, useRef } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { NAV, findHub } from '../nav';
import LocalAgentHandler from '../utils/LocalAgentHandler';
import { FaBars, FaTimes, FaBookmark, FaChevronDown, FaPlug, FaWifi } from 'react-icons/fa';

interface NavbarProps {
  className?: string;
}

const Navbar: React.FC<NavbarProps> = ({ className = '' }) => {
  const location = useLocation();
  const hub = findHub(location.pathname);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [isBookmarksOpen, setIsBookmarksOpen] = useState(false);
  const [agentConnected, setAgentConnected] = useState(false);
  const [bookmarks, setBookmarks] = useState(NAV.defaultBookmarks);
  
  const hamburgerRef = useRef<HTMLButtonElement>(null);
  const drawerRef = useRef<HTMLDivElement>(null);
  const agentHandler = useRef(new LocalAgentHandler());

  // Agent connection monitoring
  useEffect(() => {
    const checkConnection = async () => {
      const connected = await agentHandler.current.checkLocalAgent();
      setAgentConnected(connected);
    };

    checkConnection();
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMenuOpen(false);
    setActiveDropdown(null);
    setIsBookmarksOpen(false);
  }, [location.pathname]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setIsMenuOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (!drawerRef.current?.contains(event.target as Node)) {
        setActiveDropdown(null);
        setIsBookmarksOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    setActiveDropdown(null);
    setIsBookmarksOpen(false);
  };

  const toggleDropdown = (hubPath: string) => {
    setActiveDropdown(activeDropdown === hubPath ? null : hubPath);
    setIsBookmarksOpen(false);
  };

  const toggleBookmarks = () => {
    setIsBookmarksOpen(!isBookmarksOpen);
    setActiveDropdown(null);
  };

  const addBookmark = (path: string, title: string) => {
    const newBookmark = { path, title, addedAt: new Date() };
    setBookmarks(prev => [...prev.filter(b => b.path !== path), newBookmark]);
  };

  const removeBookmark = (path: string) => {
    setBookmarks(prev => prev.filter(b => b.path !== path));
  };

  return (
    <header className={`navbar ${className}`} style={{ '--hub-color': hub?.color } as React.CSSProperties}>
      <div className="navbar-container">
        {/* Logo */}
        <NavLink to="/" className="navbar-logo" title="CtrlHub - Control Systems Education">
          <span className="logo-text">CtrlHub</span>
          <span className="logo-tagline">Control Systems Education</span>
        </NavLink>

        {/* Desktop Navigation */}
        <nav className="navbar-nav desktop-nav" role="navigation" aria-label="Main navigation">
          {NAV.hubs.map((hubItem) => (
            <div 
              key={hubItem.path} 
              className="nav-item"
              onMouseEnter={() => setActiveDropdown(hubItem.path)}
              onMouseLeave={() => setActiveDropdown(null)}
            >
              <NavLink
                to={hubItem.path}
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                title={hubItem.description}
              >
                <span className="nav-icon">{hubItem.icon}</span>
                <span className="nav-text">{hubItem.title}</span>
                {hubItem.children && <FaChevronDown className="nav-arrow" />}
              </NavLink>
              
              {/* Desktop Dropdown */}
              {hubItem.children && activeDropdown === hubItem.path && (
                <div className="nav-dropdown">
                  <div className="dropdown-content">
                    {hubItem.children.map((child) => (
                      <div key={child.path} className="dropdown-section">
                        <NavLink
                          to={child.path}
                          className={({ isActive }) => `dropdown-link ${isActive ? 'active' : ''}`}
                          title={child.description}
                        >
                          <span className="dropdown-title">{child.title}</span>
                          {child.description && (
                            <span className="dropdown-desc">{child.description}</span>
                          )}
                        </NavLink>
                        
                        {/* Sub-items for nested navigation */}
                        {child.children && (
                          <div className="dropdown-subitems">
                            {child.children.map((subChild) => (
                              <NavLink
                                key={subChild.path}
                                to={subChild.path}
                                className={({ isActive }) => `dropdown-sublink ${isActive ? 'active' : ''}`}
                              >
                                {subChild.title}
                              </NavLink>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </nav>

        {/* Right Side Actions */}
        <div className="navbar-actions">
          {/* Bookmarks Dropdown */}
          <div className="nav-item">
            <button
              className={`action-btn bookmarks-btn ${isBookmarksOpen ? 'active' : ''}`}
              onClick={toggleBookmarks}
              title="Bookmarks"
              aria-expanded={isBookmarksOpen}
            >
              <FaBookmark />
              <span className="action-text">Bookmarks</span>
              {bookmarks.length > 0 && (
                <span className="bookmark-count">{bookmarks.length}</span>
              )}
            </button>
            
            {/* Bookmarks Dropdown */}
            {isBookmarksOpen && (
              <div className="nav-dropdown bookmarks-dropdown">
                <div className="dropdown-content">
                  <div className="dropdown-header">
                    <h3>Bookmarks</h3>
                  </div>
                  {bookmarks.length > 0 ? (
                    bookmarks.map((bookmark) => (
                      <div key={bookmark.path} className="bookmark-item">
                        <NavLink
                          to={bookmark.path}
                          className="bookmark-link"
                          onClick={() => setIsBookmarksOpen(false)}
                        >
                          {bookmark.title}
                        </NavLink>
                        <button
                          className="bookmark-remove"
                          onClick={() => removeBookmark(bookmark.path)}
                          title={`Remove ${bookmark.title} from bookmarks`}
                        >
                          <FaTimes />
                        </button>
                      </div>
                    ))
                  ) : (
                    <div className="no-bookmarks">
                      <span>No bookmarks yet.</span>
                      <small>Navigate to any page and bookmark it!</small>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Agent Status */}
          <div className="nav-item">
            <div className={`agent-status ${agentConnected ? 'connected' : 'disconnected'}`} title={agentConnected ? 'Agent Connected - Hardware Available' : 'Agent Disconnected - Simulation Mode Only'}>
              <span className="agent-icon">
                {agentConnected ? <FaPlug /> : <FaWifi />}
              </span>
              <span className="agent-text">
                {agentConnected ? 'Agent Connected' : 'Agent Disconnected'}
              </span>
              <span className="agent-indicator"></span>
            </div>
          </div>

          {/* Mobile Hamburger */}
          <button
            ref={hamburgerRef}
            className={`hamburger-btn ${isMenuOpen ? 'active' : ''}`}
            onClick={toggleMenu}
            aria-label="Toggle mobile menu"
            aria-expanded={isMenuOpen}
          >
            {isMenuOpen ? <FaTimes /> : <FaBars />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isMenuOpen && (
        <div
          className="mobile-overlay"
          onClick={toggleMenu}
          role="button"
          tabIndex={-1}
          aria-label="Close mobile menu"
        />
      )}

      {/* Mobile Navigation Drawer */}
      <div ref={drawerRef} className={`mobile-drawer ${isMenuOpen ? 'open' : ''}`}>
        <div className="mobile-nav-header">
          <span className="mobile-nav-title">Navigation</span>
          <button
            className="mobile-close-btn"
            onClick={toggleMenu}
            aria-label="Close mobile menu"
          >
            <FaTimes />
          </button>
        </div>
        
        <nav className="mobile-nav" role="navigation" aria-label="Mobile navigation">
          {NAV.hubs.map((hubItem) => (
            <div key={hubItem.path} className="mobile-nav-section">
              <div className="mobile-nav-header-item">
                <NavLink
                  to={hubItem.path}
                  className={({ isActive }) => `mobile-nav-link hub-link ${isActive ? 'active' : ''}`}
                  onClick={toggleMenu}
                >
                  <span className="nav-icon">{hubItem.icon}</span>
                  <span className="nav-text">{hubItem.title}</span>
                </NavLink>
                
                {hubItem.children && (
                  <button
                    className={`mobile-dropdown-toggle ${activeDropdown === hubItem.path ? 'active' : ''}`}
                    onClick={() => toggleDropdown(hubItem.path)}
                    aria-expanded={activeDropdown === hubItem.path}
                  >
                    <FaChevronDown />
                  </button>
                )}
              </div>
              
              {/* Mobile Dropdown Content */}
              {hubItem.children && activeDropdown === hubItem.path && (
                <div className="mobile-dropdown">
                  {hubItem.children.map((child) => (
                    <div key={child.path} className="mobile-dropdown-item">
                      <NavLink
                        to={child.path}
                        className={({ isActive }) => `mobile-nav-link ${isActive ? 'active' : ''}`}
                        onClick={toggleMenu}
                      >
                        {child.title}
                      </NavLink>
                      
                      {/* Sub-items for mobile */}
                      {child.children && (
                        <div className="mobile-subitems">
                          {child.children.map((subChild) => (
                            <NavLink
                              key={subChild.path}
                              to={subChild.path}
                              className={({ isActive }) => `mobile-nav-sublink ${isActive ? 'active' : ''}`}
                              onClick={toggleMenu}
                            >
                              {subChild.title}
                            </NavLink>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {/* Mobile Bookmarks Section */}
          <div className="mobile-nav-section bookmarks-section">
            <div className="mobile-nav-header-item">
              <button
                className="mobile-nav-link bookmarks-mobile-btn"
                onClick={() => setIsBookmarksOpen(!isBookmarksOpen)}
              >
                <FaBookmark />
                <span>Bookmarks ({bookmarks.length})</span>
                <FaChevronDown className={isBookmarksOpen ? 'active' : ''} />
              </button>
            </div>
            
            {isBookmarksOpen && (
              <div className="mobile-dropdown">
                {bookmarks.length > 0 ? (
                  bookmarks.map((bookmark) => (
                    <div key={bookmark.path} className="mobile-bookmark-item">
                      <NavLink
                        to={bookmark.path}
                        className="mobile-nav-link"
                        onClick={toggleMenu}
                      >
                        {bookmark.title}
                      </NavLink>
                      <button
                        className="bookmark-remove"
                        onClick={() => removeBookmark(bookmark.path)}
                        title={`Remove ${bookmark.title}`}
                      >
                        <FaTimes />
                      </button>
                    </div>
                  ))
                ) : (
                  <div className="no-bookmarks">
                    No bookmarks yet.
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Mobile Agent Status */}
          <div className="mobile-agent-status">
            <div className={`agent-status ${agentConnected ? 'connected' : 'disconnected'}`}>
              <span className="agent-icon">
                {agentConnected ? <FaPlug /> : <FaWifi />}
              </span>
              <span className="agent-text">
                {agentConnected ? 'Agent Connected' : 'Agent Disconnected'}
              </span>
              <span className="agent-indicator"></span>
            </div>
          </div>
        </nav>
      </div>
    </header>
  );
};

export default Navbar;