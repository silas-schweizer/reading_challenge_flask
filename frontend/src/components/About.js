import React from 'react';
import './About.css';

const About = () => {
  return (
    <div className="about-container">
      <div className="about-card">
        <div className="about-header">
          <h1>📚 About This Reading Challenge</h1>
          <p>A journey through classic literature, one book at a time</p>
        </div>

        <div className="about-content">
          <section className="about-section">
            <h2>🎯 The Challenge</h2>
            <p>
              This reading challenge features a carefully curated collection of classic literature 
              spanning multiple centuries. Two dedicated readers, Silas and Nadine, are working 
              their way through this comprehensive list of literary masterpieces.
            </p>
          </section>

          <section className="about-section">
            <h2>👥 The Readers</h2>
            <div className="readers-info">
              <div className="reader-info silas">
                <h3>👨‍💻 Silas</h3>
                <p>
                  A passionate reader with a love for both classic and contemporary literature. 
                  Enjoys exploring different genres and time periods through the written word.
                </p>
              </div>
              <div className="reader-info nadine">
                <h3>👩‍🎨 Nadine</h3>
                <p>
                  An avid reader who appreciates the artistry and craftsmanship of classic 
                  literature. Loves discovering new perspectives through timeless stories.
                </p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>📖 The Collection</h2>
            <p>
              Our collection includes works from the 19th, 20th, and 21st centuries, 
              featuring renowned authors and their most celebrated works. Each book 
              represents a significant contribution to world literature and offers 
              unique insights into different cultures, time periods, and human experiences.
            </p>
          </section>

          <section className="about-section">
            <h2>⚡ Features</h2>
            <div className="features-grid">
              <div className="feature">
                <h4>📊 Progress Tracking</h4>
                <p>Monitor reading progress with detailed statistics and percentages</p>
              </div>
              <div className="feature">
                <h4>🔍 Smart Filtering</h4>
                <p>Filter books by reader status, century, and other criteria</p>
              </div>
              <div className="feature">
                <h4>⭐ Reviews & Ratings</h4>
                <p>Add personal reviews and ratings for completed books</p>
              </div>
              <div className="feature">
                <h4>🎨 Book Covers</h4>
                <p>Beautiful cover images sourced from Open Library API</p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>🛠️ Technical Details</h2>
            <div className="tech-stack">
              <div className="tech-category">
                <h4>Backend</h4>
                <ul>
                  <li>Flask (Python)</li>
                  <li>SQLite Database</li>
                  <li>Flask-Login for Authentication</li>
                  <li>RESTful API Design</li>
                </ul>
              </div>
              <div className="tech-category">
                <h4>Frontend</h4>
                <ul>
                  <li>React.js</li>
                  <li>React Router</li>
                  <li>Axios for API calls</li>
                  <li>Responsive CSS Design</li>
                </ul>
              </div>
              <div className="tech-category">
                <h4>Deployment</h4>
                <ul>
                  <li>Production-ready configuration</li>
                  <li>Docker support</li>
                  <li>Environment-based settings</li>
                  <li>Security best practices</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>🚀 Getting Started</h2>
            <p>
              This application supports both traditional Flask templates and a modern 
              React frontend. Users can log in to track their reading progress, mark 
              books as completed, and leave reviews for books they've read.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default About;
