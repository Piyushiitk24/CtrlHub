import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  smartContentOrganizer, 
  progressTracker, 
  SmartSuggestion, 
  LearningPath 
} from '../../utils/smartContent';
import { COMPONENT_METADATA } from '../../data/componentMetadata';

const SmartSuggestions: React.FC = () => {
  const [suggestions, setSuggestions] = useState<SmartSuggestion[]>([]);
  const [adaptivePath, setAdaptivePath] = useState<LearningPath | null>(null);
  const [stats, setStats] = useState({
    totalComponents: 0,
    completedComponents: 0,
    totalTimeSpent: 0,
    averageRating: 0,
    streakDays: 0
  });

  useEffect(() => {
    // Load smart suggestions and adaptive path
    const newSuggestions = smartContentOrganizer.getSmartSuggestions(3);
    const newAdaptivePath = smartContentOrganizer.getAdaptiveLearningPath();
    const newStats = progressTracker.getLearningStats();
    
    setSuggestions(newSuggestions);
    setAdaptivePath(newAdaptivePath);
    setStats(newStats);
  }, []);

  const getSuggestionIcon = (reason: SmartSuggestion['reason']): string => {
    switch (reason) {
      case 'prerequisite': return '📚';
      case 'next-step': return '⭐';
      case 'related': return '🔗';
      case 'popular': return '🔥';
      case 'difficulty-match': return '🎯';
      default: return '💡';
    }
  };

  const getSuggestionColor = (reason: SmartSuggestion['reason']): string => {
    switch (reason) {
      case 'prerequisite': return '#007bff';
      case 'next-step': return '#28a745';
      case 'related': return '#ffc107';
      case 'popular': return '#dc3545';
      case 'difficulty-match': return '#6f42c1';
      default: return '#6c757d';
    }
  };

  if (suggestions.length === 0 && !adaptivePath && stats.totalComponents === 0) {
    return (
      <div className="smart-suggestions">
        <div className="suggestions-header">
          <h3 className="suggestions-title">🚀 Get Started</h3>
          <p className="suggestions-subtitle">
            Begin your control systems journey with our recommended starting point
          </p>
        </div>
        
        <div className="getting-started-card">
          <div className="starter-icon">⚙️</div>
          <h4 className="starter-title">Start with DC Motor</h4>
          <p className="starter-description">
            Perfect introduction to electromechanical systems, mathematical modeling, and control theory
          </p>
          <Link to="/components/dc-motor" className="starter-button">
            Begin Learning →
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="smart-suggestions">
      <div className="suggestions-header">
        <h3 className="suggestions-title">🎯 Personalized for You</h3>
        <p className="suggestions-subtitle">
          Based on your learning progress and goals
        </p>
      </div>

      {/* Learning Statistics */}
      <div className="learning-stats">
        <div className="stat-item">
          <span className="stat-number">{stats.completedComponents}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{Math.round(stats.totalTimeSpent)}m</span>
          <span className="stat-label">Time Spent</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{stats.streakDays}</span>
          <span className="stat-label">Day Streak</span>
        </div>
        {stats.averageRating > 0 && (
          <div className="stat-item">
            <span className="stat-number">
              {stats.averageRating.toFixed(1)}⭐
            </span>
            <span className="stat-label">Avg Rating</span>
          </div>
        )}
      </div>

      {/* Adaptive Learning Path */}
      {adaptivePath && (
        <div className="adaptive-path">
          <div className="path-header">
            <h4 className="path-title">📈 Recommended Learning Path</h4>
            <span className="path-difficulty">{adaptivePath.difficulty}</span>
          </div>
          <h5 className="path-name">{adaptivePath.title}</h5>
          <p className="path-description">{adaptivePath.description}</p>
          <div className="path-components">
            {adaptivePath.components.map((compId, index) => {
              const component = COMPONENT_METADATA.find(c => c.id === compId);
              const progress = progressTracker.getComponentProgress(compId);
              const isCompleted = progress?.completed || false;
              
              return (
                <div key={compId} className="path-component">
                  {index > 0 && <span className="path-arrow">→</span>}
                  <Link 
                    to={component?.path || `#${compId}`}
                    className={`path-component-link ${isCompleted ? 'completed' : ''}`}
                  >
                    <span className="component-icon">{component?.icon || '📦'}</span>
                    <span className="component-name">{component?.title || compId}</span>
                    {isCompleted && <span className="completion-check">✓</span>}
                  </Link>
                </div>
              );
            })}
          </div>
          <div className="path-meta">
            <span className="path-time">⏱️ {adaptivePath.estimatedTime}</span>
          </div>
        </div>
      )}

      {/* Smart Suggestions */}
      {suggestions.length > 0 && (
        <div className="suggestions-list">
          <h4 className="suggestions-list-title">💡 Suggested Next Steps</h4>
          <div className="suggestions-grid">
            {suggestions.map((suggestion, index) => {
              const component = COMPONENT_METADATA.find(c => c.id === suggestion.componentId);
              if (!component) return null;

              return (
                <Link 
                  key={index}
                  to={component.path} 
                  className="suggestion-card"
                >
                  <div className="suggestion-header">
                    <span className="suggestion-icon">
                      {getSuggestionIcon(suggestion.reason)}
                    </span>
                    <span 
                      className="suggestion-badge"
                      style={{ backgroundColor: getSuggestionColor(suggestion.reason) }}
                    >
                      {suggestion.reason.replace('-', ' ')}
                    </span>
                  </div>
                  
                  <div className="suggestion-content">
                    <h5 className="suggestion-title">
                      {component.icon} {component.title}
                    </h5>
                    <p className="suggestion-description">
                      {component.description}
                    </p>
                    <p className="suggestion-explanation">
                      {suggestion.explanation}
                    </p>
                  </div>
                  
                  <div className="suggestion-meta">
                    <span className="confidence-bar">
                      <div 
                        className="confidence-fill"
                        style={{ width: `${suggestion.confidence * 100}%` }}
                      ></div>
                    </span>
                    <span className="confidence-text">
                      {Math.round(suggestion.confidence * 100)}% match
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartSuggestions;