import csv
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, send_file, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import os
import requests
import re
from dotenv import load_dotenv
from config import config
from local_covers import LocalCoverManager

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')

# Configure app based on environment
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Database path - use absolute path to avoid issues in production
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reading_challenge.db')
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'book_list.csv')

# React build path
REACT_BUILD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'build')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to mark books as read or add reviews.'

# Initialize Local Cover Manager
cover_manager = LocalCoverManager()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in ['s', 'n']:
        return User(user_id)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').lower()
        password = request.form.get('password', '')
        
        # Secure authentication with hashed passwords
        valid_user = False
        if username == 's':
            valid_user = check_password_hash(app.config['SILAS_PASSWORD_HASH'], password)
        elif username == 'n':
            valid_user = check_password_hash(app.config['NADINE_PASSWORD_HASH'], password)
        
        if valid_user:
            user = User(username)
            login_user(user)
            name = 'Silas' if username == 's' else 'Nadine'
            flash(f'Welcome back, {name}! Happy reading! 📚', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Database initialization
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER,
            s_read BOOLEAN DEFAULT FALSE,
            n_read BOOLEAN DEFAULT FALSE,
            cover_url TEXT,
            order_index INTEGER
        )
    ''')
    
    # Create reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            reader TEXT NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            review TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Function to get cover image using local cover management
def get_cover_image(title, author, book_id=None):
    """Get cover URL using local cover management system"""
    try:
        # If we have a book_id, use it; otherwise try to find it in the database
        if book_id is None:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM books WHERE title = ? AND author = ?', (title, author))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                book_id = result[0]
            else:
                print(f"⚠️  No book found in database for '{title}' by {author}")
                return None
        
        # Get cover URL from local cover manager
        cover_url = cover_manager.get_cover_url(book_id, title, author)
        
        # If it's the default cover URL, we don't have a specific cover
        if cover_url == '/static/covers/default_book_cover.jpg':
            print(f"  ℹ️  Using default cover for '{title}' by {author}")
        else:
            print(f"  ✓ Found local cover for '{title}' by {author}: {cover_url}")
        
        return cover_url
            
    except Exception as e:
        print(f"  ✗ Error getting cover for '{title}' by {author}: {e}")
        return None

# Load books from CSV into database
def load_books_from_csv():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if books are already loaded
    cursor.execute('SELECT COUNT(*) FROM books')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Check if CSV file exists
    if not os.path.exists(CSV_PATH):
        print(f"Warning: {CSV_PATH} not found. Adding sample books for testing.")
        # Add some sample books for testing
        sample_books = [
            (False, False, "Pride and Prejudice", "Jane Austen", 1813),
            (False, False, "To Kill a Mockingbird", "Harper Lee", 1960),
            (False, False, "1984", "George Orwell", 1949),
            (False, False, "The Great Gatsby", "F. Scott Fitzgerald", 1925),
            (False, False, "Jane Eyre", "Charlotte Brontë", 1847)
        ]
        
        for i, (s_read, n_read, title, author, year) in enumerate(sample_books):
            cursor.execute('''
                INSERT INTO books (title, author, year, s_read, n_read, cover_url, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, author, year, s_read, n_read, None, i))
        
        conn.commit()
        conn.close()
        print("Sample books added successfully")
        return
    
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            
            order_index = 0
            for row in csv_reader:
                if len(row) >= 4 and row[2]:  # Make sure we have title and author
                    s_read = row[0].strip().lower() == 'x'
                    n_read = row[1].strip().lower() == 'x'
                    title = row[2].strip()
                    author = row[3].strip()
                    
                    # Extract year from title if present and remove brackets
                    year = None
                    if '(' in title and ')' in title:
                        try:
                            year_str = title[title.rfind('(') + 1:title.rfind(')')]
                            year = int(year_str)
                            title = title[:title.rfind('(')].strip()
                        except ValueError:
                            pass
                    
                    # Insert book without cover initially - covers will be managed locally
                    cursor.execute('''
                        INSERT INTO books (title, author, year, s_read, n_read, cover_url, order_index)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (title, author, year, s_read, n_read, None, order_index))
                    
                    order_index += 1
        
        conn.commit()
        print(f"Successfully loaded {order_index} books from CSV")
    except Exception as e:
        print(f"Error loading books from CSV: {e}")
    finally:
        conn.close()

# Initialize database and load books when app starts (works with both direct run and gunicorn)
def initialize_app():
    """Initialize database and load books with proper error handling"""
    try:
        print(f"Initializing database at: {DATABASE_PATH}")
        print(f"CSV file location: {CSV_PATH}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"App file directory: {os.path.dirname(os.path.abspath(__file__))}")
        
        init_db()
        print("Database tables created successfully")
        
        print("Loading books from CSV...")
        load_books_from_csv()
        print("App initialization complete")
        
        # Verify the database was properly initialized
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM books')
        book_count = cursor.fetchone()[0]
        print(f"Database contains {book_count} books")
        conn.close()
        
    except Exception as e:
        print(f"ERROR during app initialization: {e}")
        import traceback
        traceback.print_exc()

# Call initialization
initialize_app()

@app.route('/')
def index():
    # Ensure database is initialized
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Test if books table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
        if not cursor.fetchone():
            # Table doesn't exist, try to initialize
            print("Books table not found, initializing database...")
            conn.close()
            initialize_app()
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
        
    except Exception as e:
        print(f"Database connection error: {e}")
        # Try to initialize database
        initialize_app()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
    
    # Get filter parameters
    filter_by = request.args.get('filter', 'all')
    century_filter = request.args.get('century', 'all')
    author_filter = request.args.get('author', 'all')
    
    # Build base query
    base_conditions = []
    
    # Apply reading status filter
    if filter_by == 'silas':
        base_conditions.append('s_read = 1')
    elif filter_by == 'nadine':
        base_conditions.append('n_read = 1')
    elif filter_by == 'both':
        base_conditions.append('s_read = 1 AND n_read = 1')
    elif filter_by == 'unread':
        base_conditions.append('s_read = 0 AND n_read = 0')
    
    # Apply century filter
    if century_filter == '19th':
        base_conditions.append('year >= 1800 AND year < 1900')
    elif century_filter == '20th':
        base_conditions.append('year >= 1900 AND year < 2000')
    elif century_filter == '21st':
        base_conditions.append('year >= 2000')
    
    # Apply author filter
    if author_filter != 'all':
        base_conditions.append('author = ?')
    
    # Build final query
    where_clause = ''
    query_params = []
    if base_conditions:
        where_clause = 'WHERE ' + ' AND '.join(base_conditions)
        if author_filter != 'all':
            query_params.append(author_filter)
    
    query = f'''
        SELECT id, title, author, year, s_read, n_read, cover_url FROM books
        {where_clause}
        ORDER BY order_index
    '''
    
    cursor.execute(query, query_params)
    books = cursor.fetchall()
    
    # Get all unique authors with book counts, ordered by surname
    cursor.execute('''
        SELECT author, COUNT(*) as book_count 
        FROM books 
        GROUP BY author 
        ORDER BY 
            CASE WHEN author LIKE '% %' 
                 THEN TRIM(SUBSTR(author, INSTR(author, ' ') + 1)) 
                 ELSE author 
            END,
            author
    ''')
    authors_data = cursor.fetchall()
    all_authors = [{'name': author, 'count': count, 'display': f"{author} ({count})"} 
                   for author, count in authors_data]
    
    # Get reading statistics
    cursor.execute('SELECT COUNT(*) FROM books WHERE s_read = 1')
    s_read_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM books WHERE n_read = 1')
    n_read_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM books')
    total_books = cursor.fetchone()[0]
    
    # Get century statistics
    cursor.execute('SELECT COUNT(*) FROM books WHERE year >= 1800 AND year < 1900')
    books_19th = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM books WHERE year >= 1900 AND year < 2000')
    books_20th = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM books WHERE year >= 2000')
    books_21st = cursor.fetchone()[0]
    
    conn.close()
    
    stats = {
        's_read': s_read_count,
        'n_read': n_read_count,
        'total': total_books,
        's_percentage': round((s_read_count / total_books * 100), 1) if total_books > 0 else 0,
        'n_percentage': round((n_read_count / total_books * 100), 1) if total_books > 0 else 0,
        'books_19th': books_19th,
        'books_20th': books_20th,
        'books_21st': books_21st
    }
    
    return render_template('index.html', 
                         books=books, 
                         stats=stats, 
                         current_filter=filter_by, 
                         current_century=century_filter,
                         current_author=author_filter,
                         all_authors=all_authors)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get book details including cover URL
    cursor.execute('''
        SELECT id, title, author, year, s_read, n_read, cover_url FROM books WHERE id = ?
    ''', (book_id,))
    book = cursor.fetchone()
    
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('index'))
    
    # Get reviews for this book
    cursor.execute('''
        SELECT reader, rating, review, date_added FROM reviews 
        WHERE book_id = ? ORDER BY date_added DESC
    ''', (book_id,))
    reviews = cursor.fetchall()
    
    conn.close()
    
    return render_template('book_detail.html', book=book, reviews=reviews)

@app.route('/mark_read/<int:book_id>/<reader>')
@login_required
def mark_read(book_id, reader):
    # Check if user can only mark their own books
    if current_user.id != reader:
        flash('You can only mark your own books as read', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    if reader not in ['s', 'n']:
        flash('Invalid reader', 'error')
        return redirect(url_for('index'))
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    column = f'{reader}_read'
    cursor.execute(f'UPDATE books SET {column} = 1 WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    
    flash(f'Book marked as read by {reader.upper()}!', 'success')
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/add_review/<int:book_id>', methods=['POST'])
@login_required
def add_review(book_id):
    reader = request.form.get('reader')
    rating = request.form.get('rating')
    review_text = request.form.get('review')
    
    # Check if user can only add reviews for themselves
    if current_user.id != reader:
        flash('You can only add reviews for yourself', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    if not reader or not rating:
        flash('Reader and rating are required', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError
    except ValueError:
        flash('Rating must be between 1 and 5', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO reviews (book_id, reader, rating, review)
        VALUES (?, ?, ?, ?)
    ''', (book_id, reader, rating, review_text))
    
    conn.commit()
    conn.close()
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/fetch_covers', methods=['POST'])
@login_required
def fetch_covers():
    """Update database with local cover URLs and show statistics"""
    try:
        # Update database with local cover URLs
        updated_count = cover_manager.update_database_covers()
        
        # Get statistics
        stats = cover_manager.get_statistics()
        
        if updated_count > 0:
            flash(f'Successfully updated {updated_count} book cover URLs! Database now has {stats["books_with_covers"]} books with covers.', 'success')
        else:
            flash(f'All books already have cover URLs assigned. {stats["books_with_covers"]} books have covers, {stats["books_without_covers"]} use default cover.', 'info')
            
    except Exception as e:
        print(f"Error updating covers: {e}")
        flash('Error updating covers. Please try again later.', 'error')
    
    return redirect(url_for('index'))

@app.route('/test_fetch_covers', methods=['POST', 'GET'])
def test_fetch_covers():
    """Test endpoint to show local cover management statistics and update database"""
    try:
        # Update database with local cover URLs
        updated_count = cover_manager.update_database_covers()
        
        # Get comprehensive statistics
        stats = cover_manager.get_statistics()
        
        # Get list of books without covers for debugging
        books_without_covers = cover_manager.list_books_without_covers()
        
        print(f"📊 COVER STATISTICS:")
        print(f"   Total books: {stats['total_books']}")
        print(f"   Books with covers: {stats['books_with_covers']}")
        print(f"   Books without covers: {stats['books_without_covers']}")
        print(f"   Cover files on disk: {stats['cover_files']}")
        print(f"   Cover mappings: {stats['mappings']}")
        print(f"   Database updates: {updated_count}")
        
        if books_without_covers:
            print(f"\n📚 First 10 books without covers:")
            for i, (book_id, title, author) in enumerate(books_without_covers[:10]):
                print(f"   {i+1}. {title} by {author} (ID: {book_id})")
        
        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'statistics': stats,
            'books_without_covers_sample': [
                {'id': book_id, 'title': title, 'author': author} 
                for book_id, title, author in books_without_covers[:10]
            ],
            'message': f'Local cover management working! Updated {updated_count} database entries. {stats["books_with_covers"]} books have covers.'
        })
            
    except Exception as e:
        print(f"💥 ERROR in test_fetch_covers: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/about')
def about():
    """About page with information about the reading challenge"""
    return render_template('about.html')

@app.route('/features')
def features_complete():
    """Feature summary page"""
    return render_template('features_complete.html')

# API Endpoints for React Frontend
@app.route('/api/books')
def api_books():
    """API endpoint to get books with filtering for React frontend"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get filter parameters
        filter_by = request.args.get('filter', 'all')
        century_filter = request.args.get('century', 'all')
        author_filter = request.args.get('author', 'all')  # Legacy single author support
        selected_authors = request.args.getlist('authors')  # New multiple authors support
        
        # Build base query
        base_conditions = []
        query_params = []
        
        # Apply reading status filter
        if filter_by == 'silas':
            base_conditions.append('s_read = 1')
        elif filter_by == 'nadine':
            base_conditions.append('n_read = 1')
        elif filter_by == 'both':
            base_conditions.append('s_read = 1 AND n_read = 1')
        elif filter_by == 'unread':
            base_conditions.append('s_read = 0 AND n_read = 0')
        
        # Apply century filter
        if century_filter == '19th':
            base_conditions.append('year >= 1800 AND year < 1900')
        elif century_filter == '20th':
            base_conditions.append('year >= 1900 AND year < 2000')
        elif century_filter == '21st':
            base_conditions.append('year >= 2000')
        
        # Apply author filter (support both single and multiple authors)
        if selected_authors:  # New multiple authors format
            placeholders = ','.join(['?'] * len(selected_authors))
            base_conditions.append(f'author IN ({placeholders})')
            query_params.extend(selected_authors)
        elif author_filter != 'all':  # Legacy single author format
            base_conditions.append('author = ?')
            query_params.append(author_filter)
        
        # Build final query
        where_clause = ''
        if base_conditions:
            where_clause = 'WHERE ' + ' AND '.join(base_conditions)
        
        query = f'''
            SELECT id, title, author, year, s_read, n_read, cover_url FROM books
            {where_clause}
            ORDER BY order_index
        '''
        
        cursor.execute(query, query_params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to JSON format expected by React
        books = []
        for row in rows:
            books.append({
                'id': row[0],
                'title': row[1],
                'author': row[2],
                'publication_year': row[3],
                'silas_read': bool(row[4]),
                'nadine_read': bool(row[5]),
                'cover_url': row[6]
            })
        
        return jsonify(books)
        
    except Exception as e:
        print(f"Error in /api/books: {e}")
        return jsonify({'error': 'Failed to fetch books'}), 500

@app.route('/api/books/<int:book_id>')
def api_book_detail(book_id):
    """API endpoint to get single book details for React frontend"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get book details
        cursor.execute('''
            SELECT id, title, author, year, s_read, n_read, cover_url FROM books WHERE id = ?
        ''', (book_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'Book not found'}), 404
        
        # Get reviews for this book
        cursor.execute('''
            SELECT reader, rating, review, date_added FROM reviews 
            WHERE book_id = ? ORDER BY date_added DESC
        ''', (book_id,))
        reviews = cursor.fetchall()
        
        conn.close()
        
        # Convert to JSON format
        book = {
            'id': row[0],
            'title': row[1],
            'author': row[2],
            'publication_year': row[3],
            'silas_read': bool(row[4]),
            'nadine_read': bool(row[5]),
            'cover_url': row[6],
            'reviews': [
                {
                    'reader': review[0],
                    'rating': review[1],
                    'review': review[2],
                    'date_added': review[3]
                } for review in reviews
            ]
        }
        
        return jsonify(book)
        
    except Exception as e:
        print(f"Error in /api/books/{book_id}: {e}")
        return jsonify({'error': 'Failed to fetch book details'}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint to get reading statistics for React frontend"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get reading statistics
        cursor.execute('SELECT COUNT(*) FROM books WHERE s_read = 1')
        s_read_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM books WHERE n_read = 1')
        n_read_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM books')
        total_books = cursor.fetchone()[0]
        
        # Get century statistics
        cursor.execute('SELECT COUNT(*) FROM books WHERE year >= 1800 AND year < 1900')
        books_19th = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM books WHERE year >= 1900 AND year < 2000')
        books_20th = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM books WHERE year >= 2000')
        books_21st = cursor.fetchone()[0]
        
        conn.close()
        
        stats = {
            's_read': s_read_count,
            'n_read': n_read_count,
            'total': total_books,
            's_percentage': round((s_read_count / total_books * 100), 1) if total_books > 0 else 0,
            'n_percentage': round((n_read_count / total_books * 100), 1) if total_books > 0 else 0,
            'books_19th': books_19th,
            'books_20th': books_20th,
            'books_21st': books_21st
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error in /api/stats: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@app.route('/api/authors')
def api_authors():
    """API endpoint to get all unique authors with book counts, ordered by surname"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT author, COUNT(*) as book_count 
            FROM books 
            GROUP BY author 
            ORDER BY 
                CASE WHEN author LIKE '% %' 
                     THEN TRIM(SUBSTR(author, INSTR(author, ' ') + 1)) 
                     ELSE author 
                END,
                author
        ''')
        authors_data = cursor.fetchall()
        
        # Format as {name: "Author Name", count: 5, display: "Author Name (5)"}
        authors = []
        for author, count in authors_data:
            authors.append({
                'name': author,
                'count': count,
                'display': f"{author} ({count})"
            })
        
        conn.close()
        return jsonify(authors)
        
    except Exception as e:
        print(f"Error in /api/authors: {e}")
        return jsonify({'error': 'Failed to fetch authors'}), 500

# Routes to serve React frontend for production
@app.route('/static/css/<path:filename>')
def serve_react_css(filename):
    """Serve React CSS files"""
    react_static_path = os.path.join(REACT_BUILD_PATH, 'static', 'css')
    return send_from_directory(react_static_path, filename)

@app.route('/static/js/<path:filename>')
def serve_react_js(filename):
    """Serve React JS files"""
    react_static_path = os.path.join(REACT_BUILD_PATH, 'static', 'js')
    return send_from_directory(react_static_path, filename)

@app.route('/manifest.json')
def serve_manifest():
    """Serve React manifest.json"""
    return send_from_directory(REACT_BUILD_PATH, 'manifest.json')

@app.route('/asset-manifest.json')
def serve_asset_manifest():
    """Serve React asset-manifest.json"""
    return send_from_directory(REACT_BUILD_PATH, 'asset-manifest.json')

# React frontend routes - serve React app for all non-API routes
@app.route('/app')
@app.route('/app/')
@app.route('/app/<path:path>')
def serve_react_app(path=''):
    """Serve React app for /app routes"""
    try:
        return send_file(os.path.join(REACT_BUILD_PATH, 'index.html'))
    except Exception as e:
        print(f"Error serving React app: {e}")
        # Fallback to traditional Flask routes if React build not available
        return redirect(url_for('index'))

# Catch-all route for React Router (only for unmatched routes)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    Catch-all route that serves React app for frontend routes
    while preserving existing Flask routes
    """
    # Check if this is an API route
    if path.startswith('api/'):
        # Let Flask handle API routes normally
        abort(404)
    
    # Check if this is an existing Flask route
    flask_routes = [
        'login', 'book', 'mark_read', 'add_review', 
        'fetch_covers', 'test_fetch_covers', 'about'
    ]
    
    if path in flask_routes or path.startswith(tuple(f'{route}/' for route in flask_routes)):
        # Let Flask handle these routes normally
        abort(404)
    
    # Serve React app for all other routes
    try:
        # Check if React build exists
        react_index = os.path.join(REACT_BUILD_PATH, 'index.html')
        if os.path.exists(react_index):
            return send_file(react_index)
        else:
            # Fallback to Flask index if React build not available
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Error in catch_all route: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Database initialization is now handled at app startup above
    # Use environment variables for production deployment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port)