import React from 'react';
import { ComponentMetadata } from '../../data/componentMetadata';

interface SemanticTagsProps {
  component: ComponentMetadata;
  showAll?: boolean;
  onTagClick?: (tag: string) => void;
}

const SemanticTags: React.FC<SemanticTagsProps> = ({ 
  component, 
  showAll = false, 
  onTagClick 
}) => {
  const maxVisibleTags = showAll ? component.concepts.length : 8;

  const getTagCategory = (tag: string): 'concept' | 'technology' | 'application' | 'skill' => {
    const techTerms = ['arduino', 'simulink', 'matlab', 'pwm', 'h-bridge', 'mosfet'];
    const applicationTerms = ['control', 'motor', 'driver', 'sensor', 'actuator'];
    const skillTerms = ['modeling', 'implementation', 'analysis', 'design'];
    
    const lowerTag = tag.toLowerCase();
    
    if (techTerms.some(term => lowerTag.includes(term))) return 'technology';
    if (applicationTerms.some(term => lowerTag.includes(term))) return 'application';
    if (skillTerms.some(term => lowerTag.includes(term))) return 'skill';
    return 'concept';
  };

  const getTagColor = (category: string): string => {
    switch (category) {
      case 'concept': return '#007bff';
      case 'technology': return '#28a745';
      case 'application': return '#ffc107';
      case 'skill': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getTagIcon = (category: string): string => {
    switch (category) {
      case 'concept': return '💡';
      case 'technology': return '⚙️';
      case 'application': return '🎯';
      case 'skill': return '🎓';
      default: return '🏷️';
    }
  };

  return (
    <div className="semantic-tags">
      <div className="tags-header">
        <h4 className="tags-title">🏷️ Concepts & Technologies</h4>
        <p className="tags-subtitle">
          Key concepts, technologies, and skills covered in this component
        </p>
      </div>

      <div className="tags-grid">
        {/* Concepts */}
        <div className="tag-category">
          <h5 className="category-title">
            💡 Core Concepts
          </h5>
          <div className="tags-container">
            {component.concepts.slice(0, maxVisibleTags).map((concept, index) => {
              const category = getTagCategory(concept);
              return (
                <button
                  key={index}
                  className={`semantic-tag ${category}`}
                  style={{ 
                    borderColor: getTagColor(category),
                    color: getTagColor(category)
                  }}
                  onClick={() => onTagClick?.(concept)}
                  title={`${concept} (${category})`}
                >
                  <span className="tag-icon">{getTagIcon(category)}</span>
                  <span className="tag-text">{concept}</span>
                </button>
              );
            })}
            {component.concepts.length > maxVisibleTags && !showAll && (
              <span className="more-tags">
                +{component.concepts.length - maxVisibleTags} more
              </span>
            )}
          </div>
        </div>

        {/* Application Domains */}
        <div className="tag-category">
          <h5 className="category-title">
            🎯 Application Domains
          </h5>
          <div className="tags-container">
            {component.applicationDomains.map((domain, index) => (
              <button
                key={index}
                className="semantic-tag application"
                style={{ 
                  borderColor: getTagColor('application'),
                  color: getTagColor('application')
                }}
                onClick={() => onTagClick?.(domain)}
              >
                <span className="tag-icon">🎯</span>
                <span className="tag-text">{domain}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Learning Objectives */}
        <div className="tag-category">
          <h5 className="category-title">
            🎓 Learning Objectives
          </h5>
          <div className="tags-container">
            {component.learningObjectives.map((objective, index) => (
              <button
                key={index}
                className="semantic-tag skill"
                style={{ 
                  borderColor: getTagColor('skill'),
                  color: getTagColor('skill')
                }}
                onClick={() => onTagClick?.(objective)}
              >
                <span className="tag-icon">🎓</span>
                <span className="tag-text">{objective}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Generic Tags */}
        {component.tags.length > 0 && (
          <div className="tag-category">
            <h5 className="category-title">
              🏷️ Tags
            </h5>
            <div className="tags-container">
              {component.tags.map((tag, index) => {
                const category = getTagCategory(tag);
                return (
                  <button
                    key={index}
                    className={`semantic-tag ${category}`}
                    style={{ 
                      borderColor: getTagColor(category),
                      color: getTagColor(category)
                    }}
                    onClick={() => onTagClick?.(tag)}
                  >
                    <span className="tag-icon">{getTagIcon(category)}</span>
                    <span className="tag-text">{tag}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Tag Legend */}
      <div className="tags-legend">
        <h6 className="legend-title">Tag Categories:</h6>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-icon">💡</span>
            <span className="legend-text">Concepts</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">⚙️</span>
            <span className="legend-text">Technologies</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">🎯</span>
            <span className="legend-text">Applications</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">🎓</span>
            <span className="legend-text">Skills</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SemanticTags;