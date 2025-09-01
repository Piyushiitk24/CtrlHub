import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { 
  COMPONENT_METADATA, 
  searchComponents, 
  filterComponents,
  ComponentMetadata 
} from '../data/componentMetadata';
import ComponentSearch, { ComponentFilters } from '../components/search/ComponentSearch';
import ComponentCard from '../components/search/ComponentCard';
import SmartSuggestions from '../components/learning/SmartSuggestions';

const ComponentsHub: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<ComponentFilters>({
    difficulty: [],
    componentType: [],
    applicationDomain: [],
    learningObjective: [],
    hasHardware: undefined,
    hasSimulation: undefined,
    hasTheory: undefined
  });

  const filteredComponents = useMemo(() => {
    let results = searchComponents(searchQuery, COMPONENT_METADATA);
    results = filterComponents(results, filters);
    return results;
  }, [searchQuery, filters]);

  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
  };

  const handleFiltersChange = (newFilters: ComponentFilters) => {
    setFilters(newFilters);
  };

  return (
    <div className="components-hub">
      <div className="hub-header">
        <p className="home-subtitle">
          Study raw components before composing full systems. Search, filter, and explore components based on your learning goals.
        </p>
      </div>

      <SmartSuggestions />

      <ComponentSearch
        searchQuery={searchQuery}
        filters={filters}
        onSearchChange={handleSearchChange}
        onFiltersChange={handleFiltersChange}
        resultsCount={filteredComponents.length}
      />

      {filteredComponents.length === 0 ? (
        <div className="no-results">
          <div className="no-results-icon">🔍</div>
          <h3 className="no-results-title">No components found</h3>
          <p className="no-results-message">
            Try adjusting your search terms or filters to find what you're looking for.
          </p>
          <button 
            className="clear-all-button"
            onClick={() => {
              setSearchQuery('');
              setFilters({
                difficulty: [],
                componentType: [],
                applicationDomain: [],
                learningObjective: [],
                hasHardware: undefined,
                hasSimulation: undefined,
                hasTheory: undefined
              });
            }}
          >
            Clear all filters and search
          </button>
        </div>
      ) : (
        <div className="components-grid">
          {filteredComponents.map(component => (
            <ComponentCard 
              key={component.id} 
              component={component}
            />
          ))}
        </div>
      )}

      {/* Quick Access Section */}
      <div className="quick-access-section">
        <h3 className="quick-access-title">Popular Learning Paths</h3>
        <div className="learning-paths">
          <div className="learning-path">
            <h4 className="path-title">🚀 Control Systems Fundamentals</h4>
            <p className="path-description">Start with DC motors, add feedback with encoders, then control with Arduino</p>
            <div className="path-components">
              <Link to="/components/dc-motor" className="path-component">DC Motor</Link>
              <span className="path-arrow">→</span>
              <Link to="/components/encoder" className="path-component">Encoder</Link>
              <span className="path-arrow">→</span>
              <Link to="/components/arduino" className="path-component">Arduino</Link>
            </div>
          </div>
          
          <div className="learning-path">
            <h4 className="path-title">⚡ Power Electronics</h4>
            <p className="path-description">Understand motors, then dive into driver circuits and power management</p>
            <div className="path-components">
              <Link to="/components/dc-motor" className="path-component">DC Motor</Link>
              <span className="path-arrow">→</span>
              <Link to="/components/driver" className="path-component">Motor Driver</Link>
              <span className="path-arrow">→</span>
              <Link to="/components/stepper-motor" className="path-component">Stepper Motor</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComponentsHub;
