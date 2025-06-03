import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import './BookDetail.css';

const BookDetail = ({ user }) => {
  const { id } = useParams();
  const [book, setBook] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    review: ''
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchBookDetail();
  }, [id]);

  const fetchBookDetail = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/book/${id}`);
      setBook(response.data.book);
      setReviews(response.data.reviews);
      setError(null);
    } catch (error) {
      console.error('Error fetching book:', error);
      setError('Failed to load book details');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (reader) => {
    if (!user || user.id !== reader) {
      alert('You can only mark your own books as read');
      return;
    }

    try {
      const response = await axios.post(`/api/mark_read/${id}/${reader}`);
      if (response.data.success) {
        // Update book state
        setBook(prev => ({
          ...prev,
          [`${reader}_read`]: true
        }));
        alert(response.data.message);
      }
    } catch (error) {
      console.error('Error marking book as read:', error);
      alert('Failed to mark book as read');
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!user) {
      alert('Please log in to add a review');
      return;
    }

    try {
      setSubmitting(true);
      const response = await axios.post(`/api/add_review/${id}`, {
        reader: user.id,
        rating: reviewForm.rating,
        review: reviewForm.review
      });

      if (response.data.success) {
        // Reset form
        setReviewForm({ rating: 5, review: '' });
        // Refresh book details to get new review
        await fetchBookDetail();
        alert(response.data.message);
      }
    } catch (error) {
      console.error('Error adding review:', error);
      alert('Failed to add review');
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getReaderName = (readerId) => {
    return readerId === 's' ? 'Silas' : 'Nadine';
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading book details...</p>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="error">
        <p>{error || 'Book not found'}</p>
        <Link to="/" className="back-link">← Back to Books</Link>
      </div>
    );
  }

  return (
    <div className="book-detail-container">
      <Link to="/" className="back-link">← Back to Books</Link>
      
      <div className="book-detail-card">
        <div className="book-header">
          <div className="book-cover-large">
            {book.cover_url ? (
              <img src={book.cover_url} alt={`Cover of ${book.title}`} />
            ) : (
              <div className="no-cover-large">
                <span>📚</span>
              </div>
            )}
          </div>
          
          <div className="book-info-detailed">
            <h1 className="book-title-large">{book.title}</h1>
            <h2 className="book-author-large">by {book.author}</h2>
            {book.year && <p className="book-year-large">Published: {book.year}</p>}
            
            <div className="reading-status-large">
              <div className={`reader-status silas ${book.s_read ? 'read' : ''}`}>
                <span className="reader-name">👨‍💻 Silas</span>
                <span className="status-indicator">
                  {book.s_read ? '✓ Read' : '○ Not Read'}
                </span>
                {user && user.id === 's' && !book.s_read && (
                  <button 
                    onClick={() => handleMarkRead('s')}
                    className="mark-read-btn"
                  >
                    Mark as Read
                  </button>
                )}
              </div>
              
              <div className={`reader-status nadine ${book.n_read ? 'read' : ''}`}>
                <span className="reader-name">👩‍🎨 Nadine</span>
                <span className="status-indicator">
                  {book.n_read ? '✓ Read' : '○ Not Read'}
                </span>
                {user && user.id === 'n' && !book.n_read && (
                  <button 
                    onClick={() => handleMarkRead('n')}
                    className="mark-read-btn"
                  >
                    Mark as Read
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Reviews Section */}
        <div className="reviews-section">
          <h3>Reviews</h3>
          
          {user && (
            <form onSubmit={handleReviewSubmit} className="review-form">
              <h4>Add Your Review</h4>
              <div className="rating-input">
                <label>Rating:</label>
                <select 
                  value={reviewForm.rating}
                  onChange={(e) => setReviewForm(prev => ({
                    ...prev,
                    rating: parseInt(e.target.value)
                  }))}
                >
                  <option value={5}>5 Stars - Excellent</option>
                  <option value={4}>4 Stars - Very Good</option>
                  <option value={3}>3 Stars - Good</option>
                  <option value={2}>2 Stars - Fair</option>
                  <option value={1}>1 Star - Poor</option>
                </select>
              </div>
              
              <div className="review-text-input">
                <label>Review (optional):</label>
                <textarea
                  value={reviewForm.review}
                  onChange={(e) => setReviewForm(prev => ({
                    ...prev,
                    review: e.target.value
                  }))}
                  placeholder="Share your thoughts about this book..."
                  rows={4}
                />
              </div>
              
              <button 
                type="submit" 
                disabled={submitting}
                className="submit-review-btn"
              >
                {submitting ? 'Adding Review...' : 'Add Review'}
              </button>
            </form>
          )}

          <div className="reviews-list">
            {reviews.length === 0 ? (
              <p className="no-reviews">No reviews yet. Be the first to review this book!</p>
            ) : (
              reviews.map((review, index) => (
                <div key={index} className="review-card">
                  <div className="review-header">
                    <span className="reviewer">{getReaderName(review.reader)}</span>
                    <div className="rating">
                      {'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}
                    </div>
                    <span className="review-date">{formatDate(review.date_added)}</span>
                  </div>
                  {review.review && (
                    <p className="review-text">{review.review}</p>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookDetail;
