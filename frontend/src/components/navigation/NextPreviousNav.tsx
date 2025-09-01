import React from 'react';
import { Link } from 'react-router-dom';
import { useNavigationSequence } from '../../hooks/useNavigation';

const NextPreviousNav: React.FC = () => {
  const { previous, next, progress, current } = useNavigationSequence();

  // Don't render if no siblings (not in a sequence)
  if (progress.total <= 1) return null;

  return (
    <div className="next-prev-nav">
      <div className="nav-progress">
        <div className="progress-info">
          <span className="progress-text">
            {progress.currentIndex + 1} of {progress.total}
          </span>
          <div className="progress-bar-container">
            <div 
              className="progress-bar-fill" 
              style={{ width: `${progress.percentage}%` }}
            />
          </div>
          <span className="progress-percentage">{progress.percentage}%</span>
        </div>
        {current && (
          <div className="current-section">
            <span className="section-label">Current Section:</span>
            <span className="section-title">{current.title}</span>
          </div>
        )}
      </div>
      
      <div className="nav-buttons">
        <div className="nav-button-container">
          {previous ? (
            <Link to={previous.path} className="nav-button nav-button-prev">
              <div className="nav-button-content">
                <span className="nav-direction">← Previous</span>
                <span className="nav-title">{previous.title}</span>
              </div>
            </Link>
          ) : (
            <div className="nav-button nav-button-disabled">
              <div className="nav-button-content">
                <span className="nav-direction">← Previous</span>
                <span className="nav-title">Start of sequence</span>
              </div>
            </div>
          )}
        </div>
        
        <div className="nav-button-container">
          {next ? (
            <Link to={next.path} className="nav-button nav-button-next">
              <div className="nav-button-content">
                <span className="nav-direction">Next →</span>
                <span className="nav-title">{next.title}</span>
              </div>
            </Link>
          ) : (
            <div className="nav-button nav-button-disabled">
              <div className="nav-button-content">
                <span className="nav-direction">Next →</span>
                <span className="nav-title">End of sequence</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NextPreviousNav;