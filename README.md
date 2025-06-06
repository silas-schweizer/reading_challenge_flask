# Reading Challenge Flask App

A secure web application to track progress through classic literature reading challenges, featuring both Flask backend and React frontend.

## 🌟 Features

- **Dual Frontend Options**: Traditional Flask templates + Modern React SPA
- **RESTful API**: Full API endpoints for React frontend integration
- **Book Cover Integration**: Automatic cover fetching from Open Library API
- **Reading Statistics**: Progress tracking and century-based filtering
- **Secure Authentication**: Uses bcrypt password hashing
- **Responsive Design**: Bootstrap-based UI that works on all devices

## 🔐 Security Features

- **Secure Authentication**: Uses bcrypt password hashing
- **Session Management**: Secure Flask-Login implementation
- **Environment Configuration**: Separate development/production configs
- **Input Validation**: Form validation and SQL injection prevention

## Quick Start (Development)

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd reading_challenge_flask
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Generate secure passwords**:
   ```bash
   python generate_passwords.py
   # Follow prompts and add output to .env file
   ```

4. **Start both servers** (recommended for development):
   ```bash
   ./start_dev.sh
   ```
   This starts:
   - Flask backend at http://localhost:5000
   - React frontend at http://localhost:3000

5. **Or start Flask only** (for production-like testing):
   ```bash
   python app.py
   ```
   Access at http://localhost:5000 (includes React app at `/app`)

## 🎯 Access Points

- **Traditional Flask UI**: http://localhost:5000
- **React SPA**: http://localhost:5000/app (or http://localhost:3000 in dev)
- **API Endpoints**: http://localhost:5000/api/*
- **Book Cover Fetching**: http://localhost:5000/test_fetch_covers

## 🚀 Production Deployment

**⚠️ CRITICAL: Never deploy with default passwords or debug=True**

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive production setup instructions.

### Quick Production Checklist:
- [ ] Set strong SECRET_KEY (32+ characters)
- [ ] Generate secure password hashes
- [ ] Set FLASK_ENV=production
- [ ] Use HTTPS/SSL certificates
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure monitoring and backups
- [ ] Use production database (PostgreSQL)

## Login Credentials

**Development (change for production):**
- **Silas**: Username `s`, Password `silas`
- **Nadine**: Username `n`, Password `nadine`

## Features

- ✅ Secure user authentication with bcrypt
- ✅ Role-based access control
- ✅ Automatic book cover fetching (Open Library API)
- ✅ Progress tracking and statistics
- ✅ Rating and review system
- ✅ Filtering by reader status and century
- ✅ Responsive design
- ✅ Production-ready configuration
- ✅ Clean, modern UI with Bootstrap
- ✅ Responsive design
- ✅ SQLite database for data persistence

## Technical Stack

- **Backend**: Flask, Flask-Login, SQLite
- **Frontend**: Bootstrap 5, Font Awesome
- **Cover Images**: Open Library API
- **Database**: SQLite with automatic schema creation

## Data Import

The app automatically imports your book list from `book_list.csv` and fetches cover images for each book on first run.

## Security Note

This is a development setup with simple authentication. For production use, implement proper password hashing and more secure authentication methods.

## Features

- **Book List Display**: View all books in the challenge with completion status for both readers
- **Progress Tracking**: Visual progress indicators showing how many books each reader has completed
- **Mark as Read**: Easily mark books as completed for either reader
- **Reviews & Ratings**: Add ratings (1-5 stars) and written reviews for completed books
- **Responsive Design**: Modern, mobile-friendly interface using Bootstrap

## Setup and Installation

1. **Install Python dependencies**:
   ```bash
   pip install Flask
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Open your browser** and go to: http://localhost:5000

## Data Format

The application reads from `book_list.csv` with the following format:
- Column 1 (S): 'x' if reader S has read the book, empty otherwise
- Column 2 (N): 'x' if reader N has read the book, empty otherwise  
- Column 3 (Titel): Book title (may include publication year in parentheses)
- Column 4 (Autor:in): Author name

## Usage

### Home Page
- View all books in the challenge
- See reading progress statistics for both readers
- Quick overview of completion status with colored badges

### Book Details
- Click "View Details" on any book to see more information
- Mark books as read for either reader
- Add ratings and reviews

### Adding Reviews
1. Go to a book's detail page
2. Select the reader (S or N)
3. Choose a rating (1-5 stars)
4. Optionally add a written review
5. Submit the form

## Database

The application uses SQLite to store:
- Book information (loaded from CSV)
- Reading completion status
- Reviews and ratings

The database is automatically created when you first run the application.

## File Structure

```
reading_challenge_flask/
├── app.py                 # Main Flask application
├── book_list.csv         # Book data (your existing file)
├── requirements.txt      # Python dependencies
├── reading_challenge.db  # SQLite database (created automatically)
└── templates/
    ├── base.html         # Base template with navigation
    ├── index.html        # Home page template
    └── book_detail.html  # Book detail page template
```

## Customization

- **Readers**: Currently set up for readers "S" and "N". You can modify the code to change reader names or add more readers.
- **Styling**: The application uses Bootstrap 5 with custom CSS. You can modify the styles in the `<style>` section of `base.html`.
- **Data**: To add more books, simply update the `book_list.csv` file and restart the application.
