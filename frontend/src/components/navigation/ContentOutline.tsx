import React, { useState, useEffect } from 'react';

interface Heading {
  id: string;
  text: string;
  level: number;
}

const ContentOutline: React.FC = () => {
  const [headings, setHeadings] = useState<Heading[]>([]);
  const [activeId, setActiveId] = useState<string>('');

  useEffect(() => {
    const headingElements = Array.from(
      document.querySelectorAll<HTMLHeadingElement>('.content-main h2, .content-main h3, .content-main h4')
    );

    const mappedHeadings = headingElements.map((h, i) => {
      if (!h.id) h.id = `heading-${i}`;
      return {
        id: h.id,
        text: h.innerText,
        level: parseInt(h.tagName.substring(1), 10),
      };
    });
    setHeadings(mappedHeadings);

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActiveId(entry.target.id);
        });
      },
      { rootMargin: '0px 0px -80% 0px' }
    );

    headingElements.forEach((h) => observer.observe(h));
    return () => observer.disconnect();
  }, []);

  if (headings.length === 0) return null;

  return (
    <aside className="content-outline">
      <h4>On this page</h4>
      <ul>
        {headings.map((h) => (
          <li key={h.id} className={`level-${h.level} ${activeId === h.id ? 'active' : ''}`}>
            <a href={`#${h.id}`}>{h.text}</a>
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default ContentOutline;