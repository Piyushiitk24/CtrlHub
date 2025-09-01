import React from 'react';
import { useLocation } from 'react-router-dom';
import { useBookmarks } from '../../contexts/BookmarkContext';
import { FaBookmark, FaRegBookmark } from 'react-icons/fa';

interface BookmarkButtonProps {
  title: string;
}

const BookmarkButton: React.FC<BookmarkButtonProps> = ({ title }) => {
  const { pathname } = useLocation();
  const { addBookmark, removeBookmark, isBookmarked } = useBookmarks();
  const bookmarked = isBookmarked(pathname);

  const handleToggle = () => {
    if (bookmarked) {
      removeBookmark(pathname);
    } else {
      addBookmark({ path: pathname, title });
    }
  };

  return <button onClick={handleToggle} className="btn" title={bookmarked ? 'Remove Bookmark' : 'Add Bookmark'}>{bookmarked ? <FaBookmark /> : <FaRegBookmark />}</button>;
};

export default BookmarkButton;