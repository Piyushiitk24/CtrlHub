import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useHubNavigation } from '../../hooks/useNavigation';

const JumpToSection: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { currentComponent, hub } = useHubNavigation();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Get sections to show in dropdown
  const sections = currentComponent?.children || hub?.children || [];
  
  // Don't render if no sections to jump to
  if (sections.length === 0) return null;

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div className="jump-to-section" ref={dropdownRef}>
      <button
        className="jump-to-button"
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <span>Jump to Section</span>
        <span className={`dropdown-arrow ${isOpen ? 'open' : ''}`}>▼</span>
      </button>
      
      {isOpen && (
        <div className="jump-to-dropdown">
          <div className="dropdown-header">
            {currentComponent ? `${currentComponent.title} Sections` : `${hub?.title} Sections`}
          </div>
          <div className="dropdown-sections">
            {sections.map((section, index) => (
              <Link
                key={section.path}
                to={section.path}
                className="dropdown-section-item"
                onClick={() => setIsOpen(false)}
              >
                <span className="section-number">{index + 1}</span>
                <span className="section-name">{section.title}</span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default JumpToSection;