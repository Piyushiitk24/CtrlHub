export type NavNode = {
  id: string;
  title: string;
  path: string;
  quote?: string;
  children?: NavNode[];
};

export const NAV: { hubs: NavNode[] } = {
  hubs: [
    {
      id: 'components',
      title: 'Components',
      path: '/components',
      children: [
        {
          id: 'dc-motor',
          title: 'DC Motor',
          path: '/components/dc-motor',
          quote: '“C’mon, you bought it from the black market...”',
          children: [
            { id: 'simulink-first-principles', title: 'Simulink from First Principles', path: '/components/dc-motor/simulink-first-principles' },
            { id: 'transfer-function-and-simulink', title: 'Transfer Function & Simulink TF', path: '/components/dc-motor/transfer-function-and-simulink' },
            { id: 'hardware-build', title: 'Hardware Build (Arduino + L298N + Encoder)', path: '/components/dc-motor/hardware-build' },
            { id: 'parameter-extraction', title: 'Extract Parameters (No Datasheet)', path: '/components/dc-motor/parameter-extraction' }
          ]
        },
        { id: 'driver', title: 'Motor Driver', path: '/components/driver' },
        { id: 'stepper-motor', title: 'Stepper Motor', path: '/components/stepper-motor' },
        { id: 'encoder', title: 'Encoder', path: '/components/encoder' },
        { id: 'arduino', title: 'Arduino', path: '/components/arduino' }
      ]
    },
    {
      id: 'experiments',
      title: 'Experiments',
      path: '/experiments',
      children: [
        { id: 'rotary-inverted-pendulum', title: 'Rotary Inverted Pendulum', path: '/experiments/rotary-inverted-pendulum' },
        { id: 'ball-and-beam', title: 'Ball & Beam', path: '/experiments/ball-and-beam' },
        { id: 'cart-pole', title: 'Cart-Pole', path: '/experiments/cart-pole' },
        { id: 'dc-servo-speed', title: 'DC Servo Speed', path: '/experiments/dc-servo-speed' },
        { id: 'maglev', title: 'MagLev', path: '/experiments/maglev' },
        { id: 'furuta-pendulum', title: 'Furuta Pendulum', path: '/experiments/furuta-pendulum' }
      ]
    },
    { id: 'optics', title: 'Optics', path: '/optics' }
  ]
};

export function findByPath(nodes: NavNode[], path: string): NavNode | undefined {
  for (const n of nodes) {
    if (n.path === path) return n;
    if (n.children) {
      const found = findByPath(n.children, path);
      if (found) return found;
    }
  }
  return undefined;
}
