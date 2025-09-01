import React from 'react';
import { Link } from 'react-router-dom';
import { ComponentMetadata } from '../../data/componentMetadata';

interface ComponentCardProps {
  component: ComponentMetadata;
  showRelated?: boolean;
}

const ComponentCard: React.FC<ComponentCardProps> = ({ component, showRelated = false }) => {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner': return '#00ff41';
      case 'Intermediate': return '#ffcc02';
      case 'Advanced': return '#ff6b35';
      case 'Expert': return '#ff4757';
      default: return '#555';
    }
  };

  const getComponentTypeIcon = (type: string) => {
    switch (type) {
      case 'Actuator': return '⚙️';
      case 'Sensor': return '📡';
      case 'Controller': return '🎛️';
      case 'Driver': return '🔌';
      case 'Interface': return '🔗';
      default: return '📦';
    }
  };

  return (
    <div className="enhanced-component-card">
      <div className="card-header">
        <div className="component-icon">{component.icon}</div>
        <div className="header-info">
          <h3 className="component-title">{component.title}</h3>
          <div className="component-meta">
            <span className="component-type">
              {getComponentTypeIcon(component.componentType)} {component.componentType}
            </span>
            <span 
              className="difficulty-badge"
              style={{ backgroundColor: getDifficultyColor(component.difficulty) }}
            >
              {component.difficulty}
            </span>
          </div>
        </div>
      </div>

      <div className="card-body">
        <p className="component-description">{component.description}</p>
        
        {/* Key Features */}
        <div className="component-features">
          <div className="feature-indicators">
            {component.hasTheory && (
              <span className="feature-badge theory" title="Theory Content">📚 Theory</span>
            )}
            {component.hasSimulation && (
              <span className="feature-badge simulation" title="Simulation Content">🖥️ Simulation</span>
            )}
            {component.hasHardware && (
              <span className="feature-badge hardware" title="Hardware Content">🔧 Hardware</span>
            )}
          </div>
          
          <div className="time-estimate">
            <span className="time-icon">⏱️</span>
            {component.estimatedTime}
          </div>
        </div>

        {/* Application Domains */}
        <div className="application-domains">
          <span className="domains-label">Domains:</span>
          <div className="domains-list">
            {component.applicationDomains.map(domain => (
              <span key={domain} className="domain-tag">{domain}</span>
            ))}
          </div>
        </div>

        {/* Learning Objectives */}
        <div className="learning-objectives">
          <span className="objectives-label">Learn:</span>
          <div className="objectives-list">
            {component.learningObjectives.slice(0, 3).map(objective => (
              <span key={objective} className="objective-tag">{objective}</span>
            ))}
            {component.learningObjectives.length > 3 && (
              <span className="more-tag">+{component.learningObjectives.length - 3} more</span>
            )}
          </div>
        </div>

        {/* Key Concepts Tags */}
        <div className="key-concepts">
          <span className="concepts-label">Key Concepts:</span>
          <div className="concepts-list">
            {component.concepts.slice(0, 4).map(concept => (
              <span key={concept} className="concept-tag">{concept}</span>
            ))}
            {component.concepts.length > 4 && (
              <span className="more-tag">+{component.concepts.length - 4} more</span>
            )}
          </div>
        </div>

        {/* Prerequisites */}
        {component.prerequisites.length > 0 && (
          <div className="prerequisites">
            <span className="prereq-label">Prerequisites:</span>
            <div className="prereq-list">
              {component.prerequisites.map(prereq => (
                <span key={prereq} className="prereq-tag">{prereq}</span>
              ))}
            </div>
          </div>
        )}

        {/* Progress Info */}
        {component.sections > 0 && (
          <div className="progress-info">
            <span className="sections-count">
              📄 {component.sections} section{component.sections !== 1 ? 's' : ''}
            </span>
          </div>
        )}
      </div>

      <div className="card-footer">
        <Link to={component.path} className="explore-button">
          <span className="button-text">Explore Component</span>
          <span className="button-arrow">→</span>
        </Link>
      </div>
    </div>
  );
};

export default ComponentCard;