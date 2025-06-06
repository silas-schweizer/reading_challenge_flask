import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const BookList = () => {
  const [books, setBooks] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [century, setCentury] = useState('all');
  const [fetching, setFetching] = useState(false);

  useEffect(() => {
    fetchBooks();
    fetchStats();
  }, [filter, century]);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filter !== 'all') params.append('filter', filter);
      if (century !== 'all') params.append('century', century);
      
      const response = await axios.get(`/api/books?${params}`);
      setBooks(response.data);
    } catch (error) {
      console.error('Error fetching books:', error);
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

  const fetchCovers = async () => {
    try {
      setFetching(true);
      const response = await axios.get('/test_fetch_covers');
      alert(`Successfully fetched ${response.data.updated_count} book covers!`);
      fetchBooks(); // Refresh the book list
    } catch (error) {
      console.error('Error fetching covers:', error);
      alert('Error fetching covers. Please try again later.');
    } finally {
      setFetching(false);
    }
  };

  const getReaderBadge = (book) => {
    if (book.silas_read && book.nadine_read) {
      return <span className="badge bg-success ms-2">Both</span>;
    } else if (book.silas_read) {
      return <span className="badge bg-primary ms-2">Silas</span>;
    } else if (book.nadine_read) {
      return <span className="badge bg-info ms-2">Nadine</span>;
    }
    return <span className="badge bg-secondary ms-2">Unread</span>;
  };

  const getProgressBarClass = (percentage) => {
    if (percentage >= 75) return 'bg-success';
    if (percentage >= 50) return 'bg-warning';
    return 'bg-danger';
  };

  if (loading) {
    return (
      <div className="text-center mt-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid">
      {/* Statistics Dashboard */}
      <div className="row mb-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">
                <i className="fas fa-user-graduate me-2"></i>Silas's Progress
              </h5>
              <div className="progress mb-2">
                <div 
                  className={`progress-bar ${getProgressBarClass(stats.s_percentage)}`}
                  style={{width: `${stats.s_percentage}%`}}
                ></div>
              </div>
              <p className="card-text">
                {stats.s_read} / {stats.total} books ({stats.s_percentage}%)
              </p>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">
                <i className="fas fa-user-graduate me-2"></i>Nadine's Progress
              </h5>
              <div className="progress mb-2">
                <div 
                  className={`progress-bar ${getProgressBarClass(stats.n_percentage)}`}
                  style={{width: `${stats.n_percentage}%`}}
                ></div>
              </div>
              <p className="card-text">
                {stats.n_read} / {stats.total} books ({stats.n_percentage}%)
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="row mb-4">
        <div className="col-md-4">
          <select 
            className="form-select" 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All Books</option>
            <option value="silas">Silas Read</option>
            <option value="nadine">Nadine Read</option>
            <option value="both">Both Read</option>
            <option value="unread">Unread</option>
          </select>
        </div>
        <div className="col-md-4">
          <select 
            className="form-select" 
            value={century} 
            onChange={(e) => setCentury(e.target.value)}
          >
            <option value="all">All Centuries</option>
            <option value="19th">19th Century ({stats.books_19th})</option>
            <option value="20th">20th Century ({stats.books_20th})</option>
            <option value="21st">21st Century ({stats.books_21st})</option>
          </select>
        </div>
        <div className="col-md-4">
          <button 
            className="btn btn-success" 
            onClick={fetchCovers}
            disabled={fetching}
          >
            {fetching ? (
              <>
                <span className="spinner-border spinner-border-sm me-2"></span>
                Fetching...
              </>
            ) : (
              <>
                <i className="fas fa-image me-2"></i>
                Fetch Covers
              </>
            )}
          </button>
        </div>
      </div>

      {/* Books Grid */}
      <div className="row">
        {books.map(book => (
          <div key={book.id} className="col-lg-3 col-md-4 col-sm-6 mb-4">
            <div className="card h-100 book-card">
              <div className="book-cover-container">
                {book.cover_url ? (
                  <img 
                    src={book.cover_url} 
                    className="card-img-top book-cover"
                    alt={`Cover of ${book.title}`}
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                ) : (
                  <div className="no-cover d-flex align-items-center justify-content-center">
                    <i className="fas fa-book fa-3x text-muted"></i>
                  </div>
                )}
              </div>
              <div className="card-body d-flex flex-column">
                <h6 className="card-title">{book.title}</h6>
                <p className="card-text text-muted small">
                  by {book.author}
                  {book.publication_year && (
                    <span className="text-secondary"> ({book.publication_year})</span>
                  )}
                </p>
                <div className="mt-auto">
                  {getReaderBadge(book)}
                  <Link 
                    to={`/book/${book.id}`} 
                    className="btn btn-outline-primary btn-sm mt-2 w-100"
                  >
                    View Details
                  </Link>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {books.length === 0 && (
        <div className="text-center mt-5">
          <i className="fas fa-search fa-3x text-muted mb-3"></i>
          <h4>No books found</h4>
          <p className="text-muted">Try adjusting your filters</p>
        </div>
      )}
    </div>
  );
};

export default BookList;