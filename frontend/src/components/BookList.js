import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './BookList.css';

const BookList = ({ user }) => {
  const [books, setBooks] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    filter: 'all',
    century: 'all'
  });

  useEffect(() => {
    fetchBooks();
    fetchStats();
  }, [filters]);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.filter !== 'all') params.append('filter', filters.filter);
      if (filters.century !== 'all') params.append('century', filters.century);
      
      const response = await axios.get(`/api/books?${params.toString()}`);
      setBooks(response.data.books);
      setError(null);
    } catch (error) {
      console.error('Error fetching books:', error);
      setError('Failed to load books');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading books...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        <p>{error}</p>
        <button onClick={fetchBooks}>Try Again</button>
      </div>
    );
  }

  return (
    <div className="book-list-container">
      {/* Statistics Header */}
      <div className="stats-header">
        <div className="hero-section">
          <h2>📖 Reading Progress Challenge</h2>
          <div className="readers-progress">
            <div className="reader-card silas">
              <h3>👨‍💻 Silas</h3>
              <div className="progress-info">
                <span className="books-read">{stats.s_read || 0}</span>
                <span className="total-books">/ {stats.total || 0} books</span>
                <div className="percentage">{stats.s_percentage || 0}%</div>
              </div>
            </div>
            <div className="reader-card nadine">
              <h3>👩‍🎨 Nadine</h3>
              <div className="progress-info">
                <span className="books-read">{stats.n_read || 0}</span>
                <span className="total-books">/ {stats.total || 0} books</span>
                <div className="percentage">{stats.n_percentage || 0}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label>Show books:</label>
          <select 
            value={filters.filter} 
            onChange={(e) => handleFilterChange('filter', e.target.value)}
          >
            <option value="all">All Books</option>
            <option value="silas">Read by Silas</option>
            <option value="nadine">Read by Nadine</option>
            <option value="both">Read by Both</option>
            <option value="unread">Unread by Both</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Century:</label>
          <select 
            value={filters.century} 
            onChange={(e) => handleFilterChange('century', e.target.value)}
          >
            <option value="all">All Centuries</option>
            <option value="19th">19th Century</option>
            <option value="20th">20th Century</option>
            <option value="21st">21st Century</option>
          </select>
        </div>
      </div>

      {/* Books Grid */}
      <div className="books-grid">
        {books.length === 0 ? (
          <div className="no-books">
            <p>No books found matching your filters.</p>
          </div>
        ) : (
          books.map(book => (
            <div key={book.id} className="book-card">
              <Link to={`/book/${book.id}`} className="book-link">
                <div className="book-cover">
                  {book.cover_url ? (
                    <img src={book.cover_url} alt={`Cover of ${book.title}`} />
                  ) : (
                    <div className="no-cover">
                      <span>📚</span>
                    </div>
                  )}
                </div>
                <div className="book-info">
                  <h3 className="book-title">{book.title}</h3>
                  <p className="book-author">by {book.author}</p>
                  {book.year && <p className="book-year">({book.year})</p>}
                  <div className="reading-status">
                    <span className={`status silas ${book.s_read ? 'read' : ''}`}>
                      S {book.s_read ? '✓' : '○'}
                    </span>
                    <span className={`status nadine ${book.n_read ? 'read' : ''}`}>
                      N {book.n_read ? '✓' : '○'}
                    </span>
                  </div>
                </div>
              </Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default BookList;
