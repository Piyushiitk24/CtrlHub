import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Breadcrumbs from '../components/Breadcrumbs';
import ScrollProgressBar from '../components/ui/ScrollProgressBar';

const RootLayout: React.FC = () => {
  return (
    <div className="app-container">
      <Navbar />
      <ScrollProgressBar />
      <Breadcrumbs />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default RootLayout;