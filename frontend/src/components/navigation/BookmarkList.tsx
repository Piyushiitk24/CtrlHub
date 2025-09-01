import React from 'react';
import { Link } from 'react-router-dom';
import { useBookmarks, Bookmark } from '../../contexts/BookmarkContext';
import { FaBookmark } from 'react-icons/fa';

const BookmarkList: React.FC = () => {
  const { bookmarks } = useBookmarks();

  return (
    <div className="bookmark-dropdown">
      <button className="btn" title="Bookmarks"><FaBookmark /></button>
      <div className="bookmark-content">
        {bookmarks.length > 0 ? (
          bookmarks.map((bookmark: Bookmark) => (
            <Link key={bookmark.path} to={bookmark.path}>
              {bookmark.title}
            </Link>
          ))
        ) : (
          <span>No bookmarks yet.</span>
        )}
      </div>
    </div>
  );
};

export default BookmarkList;