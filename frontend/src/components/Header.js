import React from 'react';
import { Link } from 'react-router-dom';

function Header() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" to="/">
          <i className="fas fa-book-open"></i> Reading Challenge
        </Link>
        <div className="navbar-nav ms-auto">
          <Link className="nav-link" to="/about">
            <i className="fas fa-info-circle"></i> About
          </Link>
          <Link className="nav-link" to="/login">
            <i className="fas fa-sign-in-alt"></i> Login
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Header;
