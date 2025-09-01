import React from 'react';
import { Outlet } from 'react-router-dom';
import TopNav from '../components/TopNav';
import ScrollProgressBar from '../components/ui/ScrollProgressBar';

const RootLayout: React.FC = () => {
  return (
    <div className="app-container">
      <TopNav />
      <ScrollProgressBar />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default RootLayout;