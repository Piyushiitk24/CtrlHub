import React from 'react';
import { Outlet } from 'react-router-dom';
import TopNav from '../components/TopNav';

const RootLayout: React.FC = () => {
  return (
    <div className="app-root">
      <TopNav />
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
};

export default RootLayout;
