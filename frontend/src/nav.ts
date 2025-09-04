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
      path: '/components',
      title: 'Components',
      description: 'Hardware components and their educational modules',
      color: '#00ff41', // Retro green primary
      icon: '⚙️',
      children: [
        { 
          path: '/components/dc-motor', 
          title: 'DC Motor',
          description: 'Parameter extraction and modeling',
          children: [
            { path: '/components/dc-motor/parameter-extraction', title: 'Parameter Extraction' },
            { path: '/components/dc-motor/simulink-first-principles', title: 'First Principles' },
            { path: '/components/dc-motor/transfer-function-and-simulink', title: 'Transfer Function' },
            { path: '/components/dc-motor/hardware-build', title: 'Hardware Build' },
          ]
        },
        { path: '/components/driver', title: 'Motor Driver', description: 'L298N and other motor drivers' },
        { path: '/components/stepper-motor', title: 'Stepper Motor', description: 'Precision positioning control' },
        { path: '/components/encoder', title: 'Encoder', description: 'Position and velocity feedback' },
        { path: '/components/arduino', title: 'Arduino', description: 'Microcontroller programming' },
      ],
    },
    {
      path: '/experiments',
      title: 'Experiments',
      description: 'Control systems experiments and analysis',
      color: '#ff6b35', // Retro orange accent
      icon: '🧪',
      children: [
        { path: '/experiments/rotary-inverted-pendulum', title: 'Rotary Inverted Pendulum', description: 'Swing‑up and stabilization control.' },
        { path: '/experiments/ball-and-beam', title: 'Ball & Beam', description: 'Positioning with nonlinear dynamics.' },
        { path: '/experiments/cart-pole', title: 'Cart‑Pole', description: 'Benchmark stabilization and control.' },
        { path: '/experiments/dc-servo-speed', title: 'DC Servo Speed', description: 'PID tuning and step response analysis.' },
        { path: '/experiments/dc-motor-pid', title: 'DC Motor PID Control', description: 'PID controller design and tuning' },
        { path: '/experiments/maglev', title: 'MagLev', description: 'Levitation dynamics and control.' },
        { path: '/experiments/furuta-pendulum', title: 'Furuta Pendulum', description: 'Underactuated control strategies.' },
      ],
    },
    {
      path: '/optics',
      title: 'Optics',
      description: 'Optical components and laser systems',
      color: '#ffcc02', // Retro yellow accent
      icon: '🔬',
      children: [
        { path: '/optics/laser-diode', title: 'Laser Diode', description: 'Coherent light sources' },
        { path: '/optics/photodiode', title: 'Photodiode', description: 'Light detection and measurement' },
        { path: '/optics/beam-profiling', title: 'Beam Profiling', description: 'Laser beam characterization' },
      ],
    },
  ],
  
  // Sample bookmarks for educational purposes
  defaultBookmarks: [
    { path: '/components/dc-motor/parameter-extraction', title: 'Parameter Extraction', addedAt: new Date() },
    { path: '/experiments/dc-motor-pid', title: 'DC Motor PID', addedAt: new Date() },
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