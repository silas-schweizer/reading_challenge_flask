import React from 'react';

const Login = () => {
  return (
    <div className="container">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header text-center">
              <h3>
                <i className="fas fa-sign-in-alt me-2"></i>
                Login Required
              </h3>
            </div>
            <div className="card-body text-center">
              <p className="mb-4">
                Authentication and book management features are available through 
                the traditional Flask interface.
              </p>
              
              <div className="alert alert-info">
                <i className="fas fa-info-circle me-2"></i>
                <strong>Available Actions:</strong>
                <ul className="list-unstyled mt-2 mb-0">
                  <li>• Mark books as read</li>
                  <li>• Add book reviews</li>
                  <li>• Rate books</li>
                  <li>• Secure authentication</li>
                </ul>
              </div>

              <a 
                href="/login" 
                className="btn btn-primary btn-lg"
              >
                <i className="fas fa-external-link-alt me-2"></i>
                Go to Flask Login
              </a>
              
              <div className="mt-3">
                <small className="text-muted">
                  This will redirect to the Flask authentication system
                </small>
              </div>
            </div>
          </div>

          <div className="card mt-4">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="fas fa-question-circle me-2"></i>
                Why Use Flask Login?
              </h5>
            </div>
            <div className="card-body">
              <p className="mb-2">
                The React frontend is designed for browsing and viewing books, 
                while the Flask interface provides:
              </p>
              <ul className="mb-0">
                <li>Secure user authentication</li>
                <li>Session management</li>
                <li>Form validation and CSRF protection</li>
                <li>Database write operations</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;