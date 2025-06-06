import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const BookDetail = () => {
  const { id } = useParams();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBook();
  }, [id]);

  const fetchBook = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`/api/books/${id}`);
      setBook(response.data);
    } catch (error) {
      console.error('Error fetching book:', error);
      setError('Book not found');
    } finally {
      setLoading(false);
    }
  };

  const getReaderBadge = (book) => {
    if (book.silas_read && book.nadine_read) {
      return <span className="badge bg-success ms-2">Both Read</span>;
    } else if (book.silas_read) {
      return <span className="badge bg-primary ms-2">Silas Read</span>;
    } else if (book.nadine_read) {
      return <span className="badge bg-info ms-2">Nadine Read</span>;
    }
    return <span className="badge bg-secondary ms-2">Unread</span>;
  };

  const renderStars = (rating) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <i 
          key={i}
          className={`fas fa-star ${i <= rating ? 'text-warning' : 'text-muted'}`}
        ></i>
      );
    }
    return stars;
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

  if (error || !book) {
    return (
      <div className="text-center mt-5">
        <i className="fas fa-exclamation-circle fa-3x text-danger mb-3"></i>
        <h4>Book Not Found</h4>
        <p className="text-muted">{error || 'The requested book could not be found.'}</p>
        <Link to="/" className="btn btn-primary">Back to Books</Link>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="row mb-3">
        <div className="col">
          <Link to="/" className="btn btn-outline-secondary">
            <i className="fas fa-arrow-left me-2"></i>Back to Books
          </Link>
        </div>
      </div>

      <div className="row">
        <div className="col-md-4">
          <div className="card">
            <div className="book-cover-container-detail">
              {book.cover_url ? (
                <img 
                  src={book.cover_url} 
                  className="card-img-top book-cover-detail"
                  alt={`Cover of ${book.title}`}
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div 
                className="no-cover-detail d-flex align-items-center justify-content-center"
                style={{display: book.cover_url ? 'none' : 'flex'}}
              >
                <i className="fas fa-book fa-4x text-muted"></i>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-8">
          <div className="card">
            <div className="card-body">
              <h2 className="card-title">{book.title}</h2>
              <h5 className="text-muted mb-3">by {book.author}</h5>
              
              {book.publication_year && (
                <p className="text-secondary">
                  <i className="fas fa-calendar me-2"></i>
                  Published: {book.publication_year}
                </p>
              )}

              <div className="mb-3">
                <strong>Reading Status:</strong>
                {getReaderBadge(book)}
              </div>

              {/* Reading Status Details */}
              <div className="row mb-4">
                <div className="col-sm-6">
                  <div className={`p-3 rounded ${book.silas_read ? 'bg-primary text-white' : 'bg-light'}`}>
                    <i className={`fas fa-user-graduate me-2 ${book.silas_read ? 'text-white' : 'text-muted'}`}></i>
                    <strong>Silas:</strong> {book.silas_read ? 'Read' : 'Not Read'}
                  </div>
                </div>
                <div className="col-sm-6">
                  <div className={`p-3 rounded ${book.nadine_read ? 'bg-info text-white' : 'bg-light'}`}>
                    <i className={`fas fa-user-graduate me-2 ${book.nadine_read ? 'text-white' : 'text-muted'}`}></i>
                    <strong>Nadine:</strong> {book.nadine_read ? 'Read' : 'Not Read'}
                  </div>
                </div>
              </div>

              {/* Authentication Note */}
              <div className="alert alert-info">
                <i className="fas fa-info-circle me-2"></i>
                <strong>Note:</strong> To mark books as read or add reviews, please use the 
                <Link to="/login" className="alert-link ms-1">traditional Flask interface</Link>.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      {book.reviews && book.reviews.length > 0 && (
        <div className="row mt-4">
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h4 className="mb-0">
                  <i className="fas fa-comments me-2"></i>
                  Reviews ({book.reviews.length})
                </h4>
              </div>
              <div className="card-body">
                {book.reviews.map((review, index) => (
                  <div key={index} className={`review-item ${index < book.reviews.length - 1 ? 'border-bottom pb-3 mb-3' : ''}`}>
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <div>
                        <strong className="text-capitalize">{review.reader}</strong>
                        <div className="ms-2 d-inline">
                          {renderStars(review.rating)}
                        </div>
                      </div>
                      <small className="text-muted">
                        {new Date(review.date_added).toLocaleDateString()}
                      </small>
                    </div>
                    {review.review && (
                      <p className="mb-0">{review.review}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BookDetail;