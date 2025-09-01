import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { NAV, findByPath } from '../nav';

const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const parts = location.pathname.split('/').filter(Boolean);
  const crumbs: { label: string; to: string }[] = [];
  let acc = '';
  for (const p of parts) {
    acc += `/${p}`;
    const node = findByPath(NAV.hubs, acc);
    if (node) crumbs.push({ label: node.title, to: acc });
  }
  const items = [{ label: 'Home', to: '/' }, ...crumbs];

  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      {items.map((c, i) => {
        const isLast = i === items.length - 1;
        return (
          <span key={c.to} className="breadcrumb-item">
            {isLast ? (
              <span aria-current="page">{c.label}</span>
            ) : (
              <Link to={c.to}>{c.label}</Link>
            )}
            {!isLast && <span className="breadcrumb-sep">›</span>}
          </span>
        );
      })}
    </nav>
  );
};

export default Breadcrumbs;
