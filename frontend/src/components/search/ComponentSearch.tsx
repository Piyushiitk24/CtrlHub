import React, { useState } from 'react';
import { 
  ComponentMetadata, 
  DifficultyLevel, 
  ComponentType, 
  ApplicationDomain, 
  LearningObjective,
  getDifficultyLevels,
  getComponentTypes,
  getApplicationDomains,
  getLearningObjectives
} from '../../data/componentMetadata';

interface ComponentSearchProps {
  onSearchChange: (query: string) => void;
  onFiltersChange: (filters: ComponentFilters) => void;
  searchQuery: string;
  filters: ComponentFilters;
  resultsCount: number;
}

export interface ComponentFilters {
  difficulty: DifficultyLevel[];
  componentType: ComponentType[];
  applicationDomain: ApplicationDomain[];
  learningObjective: LearningObjective[];
  hasHardware: boolean | undefined;
  hasSimulation: boolean | undefined;
  hasTheory: boolean | undefined;
}

const ComponentSearch: React.FC<ComponentSearchProps> = ({
  onSearchChange,
  onFiltersChange,
  searchQuery,
  filters,
  resultsCount
}) => {
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);

  const handleFilterChange = <T extends keyof ComponentFilters>(
    filterType: T,
    value: ComponentFilters[T]
  ) => {
    onFiltersChange({
      ...filters,
      [filterType]: value
    });
  };

  const toggleArrayFilter = <T extends string>(
    filterType: 'difficulty' | 'componentType' | 'applicationDomain' | 'learningObjective',
    value: T
  ) => {
    const currentArray = filters[filterType] as T[];
    const newArray = currentArray.includes(value)
      ? currentArray.filter(item => item !== value)
      : [...currentArray, value];
    
    handleFilterChange(filterType, newArray as any);
  };

  const clearAllFilters = () => {
    onFiltersChange({
      difficulty: [],
      componentType: [],
      applicationDomain: [],
      learningObjective: [],
      hasHardware: undefined,
      hasSimulation: undefined,
      hasTheory: undefined
    });
  };

  const hasActiveFilters = 
    filters.difficulty.length > 0 ||
    filters.componentType.length > 0 ||
    filters.applicationDomain.length > 0 ||
    filters.learningObjective.length > 0 ||
    filters.hasHardware !== undefined ||
    filters.hasSimulation !== undefined ||
    filters.hasTheory !== undefined;

  return (
    <div className="component-search">
      {/* Search Bar */}
      <div className="search-bar-container">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search components, concepts, or technologies..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button 
              className="clear-search" 
              onClick={() => onSearchChange('')}
              title="Clear search"
            >
              ×
            </button>
          )}
        </div>
        
        <button
          className={`filters-toggle ${isFiltersOpen ? 'active' : ''}`}
          onClick={() => setIsFiltersOpen(!isFiltersOpen)}
        >
          <span className="filter-icon">⚙️</span>
          Filters
          {hasActiveFilters && <span className="filter-indicator">●</span>}
        </button>
      </div>

      {/* Results Count */}
      <div className="search-results-info">
        <span className="results-count">
          {resultsCount} component{resultsCount !== 1 ? 's' : ''} found
        </span>
        {hasActiveFilters && (
          <button className="clear-filters" onClick={clearAllFilters}>
            Clear all filters
          </button>
        )}
      </div>

      {/* Filters Panel */}
      {isFiltersOpen && (
        <div className="filters-panel">
          <div className="filters-grid">
            {/* Difficulty Filter */}
            <div className="filter-group">
              <h4 className="filter-title">Difficulty Level</h4>
              <div className="filter-options">
                {getDifficultyLevels().map(level => (
                  <label key={level} className="filter-checkbox">
                    <input
                      type="checkbox"
                      checked={filters.difficulty.includes(level)}
                      onChange={() => toggleArrayFilter('difficulty', level)}
                    />
                    <span className="checkbox-custom"></span>
                    <span className="filter-label">{level}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Component Type Filter */}
            <div className="filter-group">
              <h4 className="filter-title">Component Type</h4>
              <div className="filter-options">
                {getComponentTypes().map(type => (
                  <label key={type} className="filter-checkbox">
                    <input
                      type="checkbox"
                      checked={filters.componentType.includes(type)}
                      onChange={() => toggleArrayFilter('componentType', type)}
                    />
                    <span className="checkbox-custom"></span>
                    <span className="filter-label">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Application Domain Filter */}
            <div className="filter-group">
              <h4 className="filter-title">Application Domain</h4>
              <div className="filter-options">
                {getApplicationDomains().map(domain => (
                  <label key={domain} className="filter-checkbox">
                    <input
                      type="checkbox"
                      checked={filters.applicationDomain.includes(domain)}
                      onChange={() => toggleArrayFilter('applicationDomain', domain)}
                    />
                    <span className="checkbox-custom"></span>
                    <span className="filter-label">{domain}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Learning Objective Filter */}
            <div className="filter-group">
              <h4 className="filter-title">Learning Objective</h4>
              <div className="filter-options">
                {getLearningObjectives().map(objective => (
                  <label key={objective} className="filter-checkbox">
                    <input
                      type="checkbox"
                      checked={filters.learningObjective.includes(objective)}
                      onChange={() => toggleArrayFilter('learningObjective', objective)}
                    />
                    <span className="checkbox-custom"></span>
                    <span className="filter-label">{objective}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Content Type Filter */}
            <div className="filter-group">
              <h4 className="filter-title">Content Type</h4>
              <div className="filter-options">
                <label className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={filters.hasHardware === true}
                    onChange={(e) => handleFilterChange('hasHardware', e.target.checked ? true : undefined)}
                  />
                  <span className="checkbox-custom"></span>
                  <span className="filter-label">Hardware</span>
                </label>
                <label className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={filters.hasSimulation === true}
                    onChange={(e) => handleFilterChange('hasSimulation', e.target.checked ? true : undefined)}
                  />
                  <span className="checkbox-custom"></span>
                  <span className="filter-label">Simulation</span>
                </label>
                <label className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={filters.hasTheory === true}
                    onChange={(e) => handleFilterChange('hasTheory', e.target.checked ? true : undefined)}
                  />
                  <span className="checkbox-custom"></span>
                  <span className="filter-label">Theory</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComponentSearch;