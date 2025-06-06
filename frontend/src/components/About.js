import React from 'react';

const About = () => {
  return (
    <div className="container">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card">
            <div className="card-header text-center">
              <h2>
                <i className="fas fa-book-open me-2"></i>
                About the Reading Challenge
              </h2>
            </div>
            <div className="card-body">
              <p className="lead text-center mb-4">
                A journey through classic literature, tracking progress and sharing discoveries.
              </p>

              <div className="row mb-4">
                <div className="col-md-6">
                  <div className="card bg-light">
                    <div className="card-body text-center">
                      <i className="fas fa-users fa-2x text-primary mb-3"></i>
                      <h5>Reading Together</h5>
                      <p className="mb-0">
                        Silas and Nadine are working through a curated list of 
                        classic literature, tracking their progress and sharing reviews.
                      </p>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card bg-light">
                    <div className="card-body text-center">
                      <i className="fas fa-chart-line fa-2x text-success mb-3"></i>
                      <h5>Progress Tracking</h5>
                      <p className="mb-0">
                        Monitor reading progress with statistics, century-based filtering,
                        and visual progress indicators.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <h4>
                <i className="fas fa-star me-2"></i>
                Features
              </h4>
              <ul className="list-group list-group-flush mb-4">
                <li className="list-group-item">
                  <i className="fas fa-book text-primary me-2"></i>
                  <strong>Curated Book List:</strong> Classic literature from multiple centuries
                </li>
                <li className="list-group-item">
                  <i className="fas fa-image text-info me-2"></i>
                  <strong>Book Covers:</strong> Automatic cover fetching from Open Library
                </li>
                <li className="list-group-item">
                  <i className="fas fa-filter text-warning me-2"></i>
                  <strong>Smart Filtering:</strong> Filter by reader status and publication century
                </li>
                <li className="list-group-item">
                  <i className="fas fa-comments text-success me-2"></i>
                  <strong>Reviews & Ratings:</strong> Personal reviews and 5-star ratings
                </li>
                <li className="list-group-item">
                  <i className="fas fa-chart-bar text-danger me-2"></i>
                  <strong>Progress Statistics:</strong> Visual progress tracking and percentages
                </li>
              </ul>

              <h4>
                <i className="fas fa-code me-2"></i>
                Technology Stack
              </h4>
              <div className="row">
                <div className="col-md-6">
                  <h6 className="text-primary">Backend</h6>
                  <ul className="list-unstyled">
                    <li><i className="fab fa-python me-2"></i>Flask (Python)</li>
                    <li><i className="fas fa-database me-2"></i>SQLite Database</li>
                    <li><i className="fas fa-shield-alt me-2"></i>Flask-Login Security</li>
                    <li><i className="fas fa-globe me-2"></i>RESTful API</li>
                  </ul>
                </div>
                <div className="col-md-6">
                  <h6 className="text-info">Frontend</h6>
                  <ul className="list-unstyled">
                    <li><i className="fab fa-react me-2"></i>React 18</li>
                    <li><i className="fas fa-route me-2"></i>React Router</li>
                    <li><i className="fab fa-bootstrap me-2"></i>Bootstrap 5</li>
                    <li><i className="fas fa-mobile-alt me-2"></i>Responsive Design</li>
                  </ul>
                </div>
              </div>

              <div className="alert alert-primary mt-4">
                <h6 className="alert-heading">
                  <i className="fas fa-lightbulb me-2"></i>
                  Dual Interface Design
                </h6>
                <p className="mb-0">
                  This application features both a modern React SPA for browsing and 
                  a traditional Flask interface for authentication and data management. 
                  Each interface is optimized for its specific use case.
                </p>
              </div>
            </div>
          </div>

          <div className="text-center mt-4">
            <a href="/" className="btn btn-outline-primary me-2">
              <i className="fas fa-home me-2"></i>
              Flask Interface
            </a>
            <a href="/app" className="btn btn-primary">
              <i className="fas fa-rocket me-2"></i>
              React Interface
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;