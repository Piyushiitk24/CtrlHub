import React, { useEffect } from 'react';
import { Outlet } from 'react-router-dom';

type Props = { title: string };

const HubLayout: React.FC<Props> = ({ title }) => {
  useEffect(() => { document.title = `${title} — CtrlHub`; }, [title]);
  return (
    <div className="App home-container">
      <h1 className="home-title">{title}</h1>
      <Outlet />
    </div>
  );
};

export default HubLayout;
