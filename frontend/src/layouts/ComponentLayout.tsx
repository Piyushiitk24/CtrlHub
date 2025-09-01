import React, { useEffect, useMemo } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { NAV, findByPath } from '../nav';
import Breadcrumbs from '../components/Breadcrumbs';
import JumpToSection from '../components/navigation/JumpToSection';
import CollapsibleSidebar from '../components/navigation/CollapsibleSidebar';

type Props = { title: string };

const ComponentLayout: React.FC<Props> = ({ title }) => {
  const { pathname } = useLocation();
  useEffect(() => { document.title = `${title} — CtrlHub`; }, [title]);

  const node = useMemo(() => findByPath(NAV.hubs, pathname) || findByPath(NAV.hubs, pathname.split('/').slice(0,3).join('/')), [pathname]);
  const children = node?.children || [];

  return (
    <div className="study-container single-pane">
      <div className="study-header">
        <Link to="/components" className="back-button">← Back</Link>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <Breadcrumbs />
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
            <h2 className="study-title">{title}</h2>
            <JumpToSection />
          </div>
        </div>
      </div>
      {/* Collapsible Sidebar for Section Navigation */}
      {children.length > 0 && (
        <CollapsibleSidebar title="Sections" sections={children} />
      )}
      <div className="study-content">
        <Outlet />
      </div>
    </div>
  );
};

export default ComponentLayout;
