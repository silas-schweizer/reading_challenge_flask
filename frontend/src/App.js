import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import BookList from './components/BookList';
import Login from './components/Login';
import BookDetail from './components/BookDetail';
import About from './components/About';
import Header from './components/Header';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <div className="container mt-4">
          <Routes>
            <Route path="/" element={<BookList />} />
            <Route path="/login" element={<Login />} />
            <Route path="/book/:id" element={<BookDetail />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
