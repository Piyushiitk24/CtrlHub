import React from 'react';
import { useParams } from 'react-router-dom';
import RotaryInvertedPendulum from './RotaryInvertedPendulum';

const Placeholder: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();

  // Route to appropriate experiment component based on slug
  switch (slug) {
    case 'rotary-inverted-pendulum':
      return <RotaryInvertedPendulum />;
    default:
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>Experiment: {slug}</h2>
          <p>This experiment is not yet implemented.</p>
          <p>Available experiments:</p>
          <ul style={{ textAlign: 'left', maxWidth: '300px', margin: '0 auto' }}>
            <li>rotary-inverted-pendulum</li>
          </ul>
        </div>
      );
  }
};

export default Placeholder;
