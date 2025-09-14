export interface NavNode {
  path: string;
  title: string;
  description?: string;
  color?: string;
  icon?: string;
  children?: NavNode[];
}

export interface Bookmark {
  path: string;
  title: string;
  addedAt: Date;
}

export const NAV = {
  hubs: [
    {
      path: '/experiments',
      title: 'Experiments',
      description: 'Control systems experiments and analysis',
      color: '#ff6b35', // Retro orange accent
      icon: '🧪',
      children: [
        { path: '/experiments/rotary-inverted-pendulum', title: 'Rotary Inverted Pendulum', description: 'Swing‑up and stabilization control.' }
      ],
    },
  ],
  
  // Sample bookmarks for educational purposes
  defaultBookmarks: [
    { path: '/experiments/rotary-inverted-pendulum', title: 'Rotary Inverted Pendulum', addedAt: new Date() }
  ],
};

export const findByPath = (nodes: NavNode[], path: string): NavNode | undefined => {
  for (const node of nodes) {
    if (node.path === path) return node;
    if (node.children) {
      const found = findByPath(node.children, path);
      if (found) return found;
    }
  }
  return undefined;
};

export const findHub = (path: string): NavNode | undefined => {
  const hubPath = '/' + path.split('/')[1];
  return NAV.hubs.find(h => h.path === hubPath);
};

// For routing consistency - export mainNav for backward compatibility
export const mainNav = NAV.hubs.map(hub => ({
  path: hub.path,
  name: hub.title,
  subItems: hub.children?.map(child => ({
    path: child.path,
    name: child.title,
    description: child.description
  })) || []
}));