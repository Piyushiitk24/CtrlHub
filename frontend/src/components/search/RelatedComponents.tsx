import React from 'react';
import { Link } from 'react-router-dom';
import { ComponentMetadata, getRelatedComponents } from '../../data/componentMetadata';

interface RelatedComponentsProps {
  currentComponentId: string;
  components?: ComponentMetadata[];
}

const RelatedComponents: React.FC<RelatedComponentsProps> = ({ 
  currentComponentId, 
  components 
}) => {
  const relatedComponents = getRelatedComponents(currentComponentId, components);

  if (relatedComponents.length === 0) {
    return null;
  }

  return (
    <div className="related-components">
      <div className="related-header">
        <h3 className="related-title">Related Components</h3>
        <span className="related-subtitle">
          Components that work well together or build on similar concepts
        </span>
      </div>

      <div className="related-grid">
        {relatedComponents.map(component => (
          <Link 
            key={component.id} 
            to={component.path} 
            className="related-component-card"
          >
            <div className="related-card-header">
              <span className="related-icon">{component.icon}</span>
              <div className="related-info">
                <h4 className="related-component-title">{component.title}</h4>
                <span className="related-component-type">{component.componentType}</span>
              </div>
            </div>
            
            <p className="related-description">{component.description}</p>
            
            <div className="related-meta">
              <span className="related-difficulty" 
                    style={{ 
                      color: getDifficultyColor(component.difficulty),
                      fontWeight: 600 
                    }}>
                {component.difficulty}
              </span>
              <span className="related-time">{component.estimatedTime}</span>
            </div>

            <div className="related-connection">
              <span className="connection-reason">
                {getConnectionReason(currentComponentId, component)}
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

// Helper function to determine why components are related
const getConnectionReason = (currentId: string, related: ComponentMetadata): string => {
  if (related.prerequisites.includes(currentId)) {
    return 'Builds on this component';
  }
  if (related.suggestedNext.includes(currentId)) {
    return 'Recommended prerequisite';
  }
  return 'Similar application domain';
};

// Helper function for difficulty colors
const getDifficultyColor = (difficulty: string): string => {
  switch (difficulty) {
    case 'Beginner': return '#00ff41';
    case 'Intermediate': return '#ffcc02';
    case 'Advanced': return '#ff6b35';
    case 'Expert': return '#ff4757';
    default: return '#555';
  }
};

export default RelatedComponents;