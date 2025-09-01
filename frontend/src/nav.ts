export interface NavNode {
  path: string;
  title: string;
  color?: string;
  children?: NavNode[];
}

export const NAV = {
  hubs: [
    {
      path: '/components',
      title: 'Components',
      color: '#007bff', // Blue
      children: [
        { path: '/components/dc-motor', title: 'DC Motor' },
        { path: '/components/driver', title: 'Driver' },
        { path: '/components/stepper-motor', title: 'Stepper Motor' },
        { path: '/components/encoder', title: 'Encoder' },
        { path: '/components/arduino', title: 'Arduino' },
      ],
    },
    {
      path: '/experiments',
      title: 'Experiments',
      color: '#28a745', // Green
      children: [
        { path: '/experiments/pid-tuning', title: 'PID Tuning' },
        { path: '/experiments/bode-plot-analysis', title: 'Bode Plot Analysis' },
      ],
    },
    {
      path: '/optics',
      title: 'Optics',
      color: '#ffc107', // Yellow
      children: [
        { path: '/optics/laser-diode', title: 'Laser Diode' },
        { path: '/optics/photodiode', title: 'Photodiode' },
      ],
    },
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