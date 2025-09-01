import React, { useState, useEffect } from 'react';

const ScrollProgressBar: React.FC = () => {
  const [scroll, setScroll] = useState(0);

  const onScroll = () => {
    const scrolled = document.documentElement.scrollTop;
    const maxHeight =
      document.documentElement.scrollHeight -
      document.documentElement.clientHeight;
    const scrollPercent = (scrolled / maxHeight) * 100;
    setScroll(scrollPercent);
  };

  useEffect(() => {
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <div className="scroll-progress-container">
      <div className="scroll-progress-bar" style={{ width: `${scroll}%` }} />
    </div>
  );
};

export default ScrollProgressBar;