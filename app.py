import csv
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import os
import requests
import re
from dotenv import load_dotenv
from config import config

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure app based on environment
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to mark books as read or add reviews.'

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
    conn = sqlite3.connect('reading_challenge.db')
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

# Function to fetch cover image from Open Library API
def get_cover_image(title, author):
    try:
        # Clean title for API search
        clean_title = re.sub(r'[^\w\s]', '', title).strip()
        clean_author = re.sub(r'[^\w\s]', '', author).strip()
        
        # Search Open Library API
        search_url = f"http://openlibrary.org/search.json?title={clean_title}&author={clean_author}&limit=1"
        response = requests.get(search_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('docs') and len(data['docs']) > 0:
                book = data['docs'][0]
                if 'cover_i' in book:
                    cover_id = book['cover_i']
                    cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-L.jpg"  # Use -L for large size
                    return cover_url
    except Exception as e:
        print(f"Error fetching cover for {title}: {e}")
    
    return None

# Load books from CSV into database
def load_books_from_csv():
    conn = sqlite3.connect('reading_challenge.db')
    cursor = conn.cursor()
    
    # Check if books are already loaded
    cursor.execute('SELECT COUNT(*) FROM books')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Check if CSV file exists
    if not os.path.exists('book_list.csv'):
        print("Warning: book_list.csv not found. Skipping book import.")
        conn.close()
        return
    
    try:
        with open('book_list.csv', 'r', encoding='utf-8') as file:
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
                    
                    # Skip cover image fetching in production for faster startup
                    cover_url = None
                    if os.environ.get('FLASK_ENV', 'development') == 'development':
                        cover_url = get_cover_image(title, author)
                    
                    cursor.execute('''
                        INSERT INTO books (title, author, year, s_read, n_read, cover_url, order_index)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (title, author, year, s_read, n_read, cover_url, order_index))
                    
                    order_index += 1
        
        conn.commit()
        print(f"Successfully loaded {order_index} books from CSV")
    except Exception as e:
        print(f"Error loading books from CSV: {e}")
    finally:
        conn.close()

# Initialize database and load books when app starts (works with both direct run and gunicorn)
with app.app_context():
    init_db()
    load_books_from_csv()

@app.route('/')
def index():
    conn = sqlite3.connect('reading_challenge.db')
    cursor = conn.cursor()
    
    # Get filter parameters
    filter_by = request.args.get('filter', 'all')
    century_filter = request.args.get('century', 'all')
    
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
    
    # Build final query
    where_clause = ''
    if base_conditions:
        where_clause = 'WHERE ' + ' AND '.join(base_conditions)
    
    query = f'''
        SELECT id, title, author, year, s_read, n_read, cover_url FROM books
        {where_clause}
        ORDER BY order_index
    '''
    
    cursor.execute(query)
    books = cursor.fetchall()
    
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
    
    return render_template('index.html', books=books, stats=stats, current_filter=filter_by, current_century=century_filter)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    conn = sqlite3.connect('reading_challenge.db')
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
    
    conn = sqlite3.connect('reading_challenge.db')
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
    
    conn = sqlite3.connect('reading_challenge.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO reviews (book_id, reader, rating, review)
        VALUES (?, ?, ?, ?)
    ''', (book_id, reader, rating, review_text))
    
    conn.commit()
    conn.close()
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('book_detail', book_id=book_id))

if __name__ == '__main__':
    # Database initialization is now handled at app startup above
    # Use environment variables for production deployment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port)