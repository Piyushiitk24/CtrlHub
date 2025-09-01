import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { BookmarkProvider } from './contexts/BookmarkContext';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <BookmarkProvider>
      <App />
    </BookmarkProvider>
  </React.StrictMode>
);