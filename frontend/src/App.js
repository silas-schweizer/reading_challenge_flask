import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';
import BookList from './components/BookList';
import BookDetail from './components/BookDetail';
import Login from './components/Login';
import About from './components/About';

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:5001';
axios.defaults.withCredentials = true;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get('/api/auth/user');
      if (response.data.authenticated) {
        setUser(response.data.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout');
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <div className="header-content">
            <h1>📚 Classic Literature Reading Challenge</h1>
            <nav className="nav-links">
              <Link to="/">Home</Link>
              <Link to="/about">About</Link>
              {user ? (
                <div className="user-info">
                  <span>Welcome, {user.name}!</span>
                  <button onClick={handleLogout} className="logout-btn">
                    Logout
                  </button>
                </div>
              ) : (
                <Link to="/login">Login</Link>
              )}
            </nav>
          </div>
        </header>

        <main className="main-content">
          <Routes>
            <Route 
              path="/" 
              element={<BookList user={user} />} 
            />
            <Route 
              path="/book/:id" 
              element={<BookDetail user={user} />} 
            />
            <Route 
              path="/login" 
              element={
                user ? 
                <Navigate to="/" replace /> : 
                <Login onLogin={handleLogin} />
              } 
            />
            <Route 
              path="/about" 
              element={<About />} 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
