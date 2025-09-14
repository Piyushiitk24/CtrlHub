import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './index.css';

// Minimal pages
const Home = lazy(() => import('./pages/Home'));
const RotaryInvertedPendulum = lazy(() => import('./pages/experiments/RotaryInvertedPendulum'));

const App: React.FC = () => {
  return (
    <Router>
      <Suspense fallback={
        <div className="app-container home-container">
          <div className="loading-container">
            <div className="spinner" />
            <span className="loading-text">Loading CtrlHub...</span>
          </div>
        </div>
      }>
        <Routes>
          <Route index element={<Home />} />
          <Route path="experiments/rotary-inverted-pendulum" element={<RotaryInvertedPendulum />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </Suspense>
    </Router>
  );
};

export default App;