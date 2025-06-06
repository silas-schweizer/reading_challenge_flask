import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './BookList.css';

const BookList = () => {
  const [books, setBooks] = useState([]);
  const [stats, setStats] = useState({});
  const [authors, setAuthors] = useState([]);
  const [filteredAuthors, setFilteredAuthors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [century, setCentury] = useState('all');
  const [selectedAuthors, setSelectedAuthors] = useState([]);
  const [authorSearch, setAuthorSearch] = useState('');
  const [showAuthorDropdown, setShowAuthorDropdown] = useState(false);
  const [fetching, setFetching] = useState(false);

  useEffect(() => {
    fetchBooks();
    fetchStats();
    fetchAuthors();
  }, [filter, century, selectedAuthors]);

  // Filter authors based on search
  useEffect(() => {
    if (authorSearch.trim() === '') {
      setFilteredAuthors(authors);
    } else {
      const filtered = authors.filter(author => 
        author.name.toLowerCase().includes(authorSearch.toLowerCase())
      );
      setFilteredAuthors(filtered);
    }
  }, [authors, authorSearch]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.dropdown')) {
        setShowAuthorDropdown(false);
      }
    };

    if (showAuthorDropdown) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showAuthorDropdown]);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filter !== 'all') params.append('filter', filter);
      if (century !== 'all') params.append('century', century);
      if (selectedAuthors.length > 0) {
        selectedAuthors.forEach(author => {
          params.append('authors', author);
        });
      }
      
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

  const fetchAuthors = async () => {
    try {
      const response = await axios.get('/api/authors');
      setAuthors(response.data);
    } catch (error) {
      console.error('Error fetching authors:', error);
    }
  };

  const handleAuthorToggle = (authorName) => {
    setSelectedAuthors(prev => {
      if (prev.includes(authorName)) {
        return prev.filter(a => a !== authorName);
      } else {
        return [...prev, authorName];
      }
    });
  };

  const clearAllAuthors = () => {
    setSelectedAuthors([]);
  };

  const clearAllFilters = () => {
    setFilter('all');
    setCentury('all');
    setSelectedAuthors([]);
    setAuthorSearch('');
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
      return <span className="badge reader-badge-modern reader-badge-both ms-2">Both</span>;
    } else if (book.silas_read) {
      return <span className="badge reader-badge-modern reader-badge-silas ms-2">Silas</span>;
    } else if (book.nadine_read) {
      return <span className="badge reader-badge-modern reader-badge-nadine ms-2">Nadine</span>;
    }
    return <span className="badge reader-badge-modern reader-badge-unread ms-2">Unread</span>;
  };

  const getProgressBarClass = (percentage) => {
    if (percentage >= 75) return 'bg-success';
    if (percentage >= 50) return 'bg-warning';
    return 'bg-danger';
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{minHeight: '60vh'}}>
        <div className="text-center">
          <div className="spinner-modern mx-auto mb-3"></div>
          <h4 className="text-muted">Loading your literary journey...</h4>
          <p className="text-muted">Preparing the greatest works of literature</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid">
      {/* Enhanced Statistics Dashboard */}
      <div className="stats-dashboard p-4 mb-5">
        <div className="text-center mb-4">
          <h1 className="text-white mb-2 fw-bold">
            <i className="fas fa-trophy text-warning me-3"></i>
            Classic Literature Reading Challenge
          </h1>
          <p className="text-white-50 mb-0 fs-5">Track your progress through the greatest works of literature</p>
        </div>
        
        <div className="row">
          <div className="col-md-6 mb-3">
            <div className="stats-card p-4 h-100">
              <div className="d-flex align-items-center mb-3">
                <div className="reader-badge-modern reader-badge-silas me-3">
                  <i className="fas fa-user"></i>
                </div>
                <div>
                  <h5 className="text-white mb-0">Silas's Progress</h5>
                  <small className="text-white-50">Literary Explorer</small>
                </div>
              </div>
              <div className="progress-modern mb-3">
                <div 
                  className={`progress-bar-modern gradient-success`}
                  style={{width: `${stats.s_percentage}%`, height: '100%'}}
                ></div>
              </div>
              <div className="d-flex justify-content-between text-white">
                <span className="fw-bold fs-4">{stats.s_read}</span>
                <span className="text-white-50">/ {stats.total} books</span>
                <span className="fw-bold text-warning">{stats.s_percentage}%</span>
              </div>
            </div>
          </div>
          <div className="col-md-6 mb-3">
            <div className="stats-card p-4 h-100">
              <div className="d-flex align-items-center mb-3">
                <div className="reader-badge-modern reader-badge-nadine me-3">
                  <i className="fas fa-user"></i>
                </div>
                <div>
                  <h5 className="text-white mb-0">Nadine's Progress</h5>
                  <small className="text-white-50">Literary Adventurer</small>
                </div>
              </div>
              <div className="progress-modern mb-3">
                <div 
                  className={`progress-bar-modern gradient-info`}
                  style={{width: `${stats.n_percentage}%`, height: '100%'}}
                ></div>
              </div>
              <div className="d-flex justify-content-between text-white">
                <span className="fw-bold fs-4">{stats.n_read}</span>
                <span className="text-white-50">/ {stats.total} books</span>
                <span className="fw-bold text-warning">{stats.n_percentage}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Filters and Controls */}
      <div className="filter-badges p-4 mb-4">
        <div className="d-flex align-items-center mb-3">
          <h5 className="mb-0 fw-bold text-dark">
            <i className="fas fa-sliders-h me-2 text-primary"></i>
            Filter Your Library
          </h5>
          <div className="ms-auto">
            <small className="text-muted">
              <i className="fas fa-books me-1"></i>
              Showing {books.length} of {stats.total} books
            </small>
          </div>
        </div>
        
        <div className="row">
          <div className="col-md-4 mb-3">
            <label className="form-label fw-semibold text-muted mb-2">
              <i className="fas fa-filter me-2 text-primary"></i>Reading Status
            </label>
            <div className="position-relative">
              <select 
                className="form-select form-control-modern" 
                value={filter} 
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="all">📚 All Books</option>
                <option value="read">✅ Read by Anyone</option>
                <option value="unread">⏳ Unread by Both</option>
                <option value="silas">👨‍💼 Read by Silas</option>
                <option value="nadine">👩‍🎨 Read by Nadine</option>
                <option value="both">👥 Read by Both</option>
              </select>
              <div className="position-absolute top-50 end-0 translate-middle-y me-3 pointer-events-none">
                <i className="fas fa-chevron-down text-muted"></i>
              </div>
            </div>
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label fw-semibold text-muted mb-2">
              <i className="fas fa-calendar-alt me-2 text-warning"></i>Century
            </label>
            <div className="position-relative">
              <select 
                className="form-select form-control-modern" 
                value={century} 
                onChange={(e) => setCentury(e.target.value)}
              >
                <option value="all">🌍 All Centuries</option>
                <option value="19th">🏛️ 19th Century</option>
                <option value="20th">📻 20th Century</option>
              </select>
              <div className="position-absolute top-50 end-0 translate-middle-y me-3 pointer-events-none">
                <i className="fas fa-chevron-down text-muted"></i>
              </div>
            </div>
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label fw-semibold text-muted mb-2">
              <i className="fas fa-users me-2 text-info"></i>Authors
            </label>
            <div className="dropdown-modern">
              <div className="input-group">
                <div className="position-relative flex-grow-1">
                  <input
                    type="text"
                    className="form-control form-control-modern pe-5"
                    placeholder="🔍 Search authors..."
                    value={authorSearch}
                    onChange={(e) => setAuthorSearch(e.target.value)}
                    onFocus={() => setShowAuthorDropdown(true)}
                  />
                  <div className="position-absolute top-50 end-0 translate-middle-y me-3 pointer-events-none">
                    <i className="fas fa-search text-muted"></i>
                  </div>
                </div>
                <button
                  className="btn btn-outline-modern btn-modern"
                  type="button"
                  onClick={() => setShowAuthorDropdown(!showAuthorDropdown)}
                >
                  <i className={`fas fa-chevron-${showAuthorDropdown ? 'up' : 'down'} me-2`}></i>
                  {selectedAuthors.length > 0 ? (
                    <span className="badge bg-primary rounded-pill ms-1">{selectedAuthors.length}</span>
                  ) : (
                    'Select'
                  )}
                </button>
              </div>
              {showAuthorDropdown && (
                <div className="dropdown-menu-modern w-100" style={{maxHeight: '300px', overflowY: 'auto'}}>
                  <div className="dropdown-item-modern border-bottom bg-light">
                    <div className="d-flex justify-content-between align-items-center">
                      <small className="text-muted fw-semibold">
                        <i className="fas fa-info-circle me-1 text-info"></i>
                        {selectedAuthors.length > 0 ? `${selectedAuthors.length} author${selectedAuthors.length > 1 ? 's' : ''} selected` : 'Select authors to filter'}
                      </small>
                      {selectedAuthors.length > 0 && (
                        <button
                          className="btn btn-sm btn-outline-danger rounded-pill"
                          onClick={clearAllAuthors}
                        >
                          <i className="fas fa-times me-1"></i>Clear all
                        </button>
                      )}
                    </div>
                  </div>
                  {filteredAuthors.length === 0 ? (
                    <div className="dropdown-item-modern text-center text-muted">
                      <i className="fas fa-search me-2"></i>
                      No authors found matching "{authorSearch}"
                    </div>
                  ) : (
                    filteredAuthors.map(author => (
                      <div key={author.name} className="dropdown-item-modern">
                        <div className="form-check">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id={`author-${author.name}`}
                            checked={selectedAuthors.includes(author.name)}
                            onChange={() => handleAuthorToggle(author.name)}
                          />
                          <label 
                            className="form-check-label w-100 cursor-pointer" 
                            htmlFor={`author-${author.name}`}
                          >
                            <div className="d-flex justify-content-between align-items-center">
                              <span className="fw-medium">{author.name}</span>
                              <span className="badge bg-secondary rounded-pill ms-2">
                                {author.count} book{author.count > 1 ? 's' : ''}
                              </span>
                            </div>
                          </label>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Active Filters Display */}
      {(filter !== 'all' || century !== 'all' || selectedAuthors.length > 0) && (
        <div className="row mb-4">
          <div className="col-12">
            <div className="filter-badges">
              <div className="d-flex flex-wrap align-items-center">
                <span className="me-3 fw-semibold text-dark">
                  <i className="fas fa-tag me-2 text-primary"></i>
                  Active Filters:
                </span>
                {filter !== 'all' && (
                  <span className="filter-badge me-2 mb-2">
                    <i className="fas fa-filter me-1"></i>
                    {filter === 'read' ? 'Read by Anyone' : 
                     filter === 'unread' ? 'Unread by Both' :
                     filter === 'silas' ? 'Silas Read' : 
                     filter === 'nadine' ? 'Nadine Read' : 
                     filter === 'both' ? 'Both Read' : filter}
                    <button
                      className="btn-close btn-close-white ms-2"
                      style={{fontSize: '0.7rem'}}
                      onClick={() => setFilter('all')}
                    ></button>
                  </span>
                )}
                {century !== 'all' && (
                  <span className="filter-badge me-2 mb-2">
                    <i className="fas fa-calendar me-1"></i>
                    {century} Century
                    <button
                      className="btn-close btn-close-white ms-2"
                      style={{fontSize: '0.7rem'}}
                      onClick={() => setCentury('all')}
                    ></button>
                  </span>
                )}
                {selectedAuthors.map(author => (
                  <span key={author} className="filter-badge me-2 mb-2">
                    <i className="fas fa-user me-1"></i>
                    {author}
                    <button
                      className="btn-close btn-close-white ms-2"
                      style={{fontSize: '0.7rem'}}
                      onClick={() => handleAuthorToggle(author)}
                    ></button>
                  </span>
                ))}
                <button
                  className="btn btn-sm btn-outline-secondary rounded-pill ms-auto"
                  onClick={clearAllFilters}
                >
                  <i className="fas fa-times-circle me-1"></i>
                  Clear All Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Enhanced Action Button */}
      <div className="row mb-5">
        <div className="col-12 text-center">
          <div className="d-inline-block">
            <button 
              className="btn btn-success btn-modern px-4 py-3" 
              onClick={fetchCovers}
              disabled={fetching}
            >
              {fetching ? (
                <>
                  <div className="spinner-border spinner-border-sm me-3" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                  <span className="fw-semibold">Fetching Book Covers...</span>
                </>
              ) : (
                <>
                  <i className="fas fa-download me-3"></i>
                  <span className="fw-semibold">Fetch Missing Book Covers</span>
                </>
              )}
            </button>
            <div className="mt-2">
              <small className="text-muted">
                <i className="fas fa-info-circle me-1"></i>
                Automatically download cover images for books without covers
              </small>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Books Grid with Beautiful Cards */}
      <div className="row g-4">
        {books.map((book, index) => (
          <div key={book.id} className="col-lg-3 col-md-4 col-sm-6">
            <div className="card h-100 book-card" style={{animationDelay: `${index * 0.1}s`}}>
              <div className="book-cover-container position-relative">
                {book.cover_url ? (
                  <>
                    <img 
                      src={book.cover_url} 
                      className="card-img-top book-cover"
                      alt={`Cover of ${book.title}`}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextElementSibling.style.display = 'flex';
                      }}
                    />
                    <div className="book-overlay position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center">
                      <div className="overlay-content text-center text-white p-3">
                        <i className="fas fa-eye fa-2x mb-2"></i>
                        <p className="mb-0 fw-semibold">View Details</p>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="no-cover d-flex flex-column align-items-center justify-content-center text-center p-4">
                    <i className="fas fa-book fa-3x text-muted mb-3"></i>
                    <h6 className="text-muted mb-2 fw-bold">{book.title}</h6>
                    <small className="text-muted">No cover available</small>
                  </div>
                )}
                {/* Reading Status Indicator */}
                <div className="position-absolute top-2 end-2">
                  {book.silas_read && book.nadine_read ? (
                    <div className="status-indicator status-both" title="Read by both">
                      <i className="fas fa-check-double"></i>
                    </div>
                  ) : book.silas_read ? (
                    <div className="status-indicator status-silas" title="Read by Silas">
                      <i className="fas fa-user"></i>
                    </div>
                  ) : book.nadine_read ? (
                    <div className="status-indicator status-nadine" title="Read by Nadine">
                      <i className="fas fa-user"></i>
                    </div>
                  ) : (
                    <div className="status-indicator status-unread" title="Unread">
                      <i className="fas fa-clock"></i>
                    </div>
                  )}
                </div>
              </div>
              <div className="card-body d-flex flex-column p-4">
                <div className="book-info mb-3">
                  <h6 className="card-title fw-bold mb-2 text-dark">{book.title}</h6>
                  <div className="author-info d-flex align-items-center mb-2">
                    <i className="fas fa-pen-fancy me-2 text-primary"></i>
                    <span className="text-muted fw-medium">{book.author}</span>
                  </div>
                  {book.publication_year && (
                    <div className="publication-year d-flex align-items-center">
                      <i className="fas fa-calendar me-2 text-warning"></i>
                      <span className="text-secondary small fw-medium">{book.publication_year}</span>
                    </div>
                  )}
                </div>
                
                <div className="mt-auto">
                  <div className="reader-status-modern mb-3">
                    {getReaderBadge(book)}
                  </div>
                  <Link 
                    to={`/book/${book.id}`} 
                    className="btn btn-primary btn-modern w-100 py-2"
                  >
                    <i className="fas fa-book-open me-2"></i>
                    <span className="fw-semibold">Explore Book</span>
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