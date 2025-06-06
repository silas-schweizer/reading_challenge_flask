#!/usr/bin/env python3
"""
Book Cover Downloader Script
Downloads book covers from Open Library API and stores them locally.
Creates a static file serving system for the Flask app.
"""

import os
import sqlite3
import requests
import urllib.parse
import re
import time
import json
from PIL import Image
import hashlib
from pathlib import Path

# Configuration
DATABASE_PATH = 'reading_challenge.db'
COVERS_DIR = 'static/covers'
COVERS_DATABASE = 'covers_mapping.json'
MAX_RETRIES = 3
TIMEOUT = 10
DELAY_BETWEEN_REQUESTS = 1.0
IMAGE_SIZE = (300, 450)  # Width x Height for consistent sizing

class CoverDownloader:
    def __init__(self):
        self.covers_dir = Path(COVERS_DIR)
        self.covers_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing cover mappings
        self.cover_mappings = self.load_cover_mappings()
        
        # Statistics
        self.stats = {
            'total_books': 0,
            'already_had_covers': 0,
            'new_downloads': 0,
            'failed_downloads': 0,
            'skipped': 0
        }
    
    def load_cover_mappings(self):
        """Load existing cover mappings from JSON file"""
        if os.path.exists(COVERS_DATABASE):
            try:
                with open(COVERS_DATABASE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cover mappings: {e}")
        return {}
    
    def save_cover_mappings(self):
        """Save cover mappings to JSON file"""
        try:
            with open(COVERS_DATABASE, 'w') as f:
                json.dump(self.cover_mappings, f, indent=2)
            print(f"✅ Saved cover mappings to {COVERS_DATABASE}")
        except Exception as e:
            print(f"❌ Error saving cover mappings: {e}")
    
    def get_book_filename(self, book_id, title, author):
        """Generate a safe filename for the book cover"""
        # Create a hash of title and author for uniqueness
        content = f"{title}_{author}".lower()
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # Clean title for filename
        safe_title = re.sub(r'[^\w\s-]', '', title)[:30]
        safe_title = re.sub(r'\s+', '_', safe_title)
        
        return f"book_{book_id}_{safe_title}_{content_hash}.jpg"
    
    def search_open_library(self, title, author):
        """Search Open Library API for book covers"""
        # Clean title and author for API search
        clean_title = re.sub(r'[^\w\s]', '', title).strip()
        clean_author = re.sub(r'[^\w\s]', '', author).strip()
        
        # URL encode the parameters
        encoded_title = urllib.parse.quote(clean_title)
        encoded_author = urllib.parse.quote(clean_author)
        
        # Multiple search strategies
        search_strategies = [
            f"https://openlibrary.org/search.json?title={encoded_title}&author={encoded_author}&limit=5",
            f"https://openlibrary.org/search.json?q={encoded_title}+{encoded_author}&limit=5",
            f"https://openlibrary.org/search.json?title={encoded_title}&limit=10"
        ]
        
        headers = {
            'User-Agent': 'BookCoverDownloader/1.0 (Educational Project)'
        }
        
        for strategy_num, search_url in enumerate(search_strategies, 1):
            try:
                print(f"    Strategy {strategy_num}: Searching Open Library...")
                response = requests.get(search_url, headers=headers, timeout=TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    docs = data.get('docs', [])
                    
                    # Look for books with cover images
                    for doc in docs:
                        if 'cover_i' in doc:
                            cover_id = doc['cover_i']
                            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                            print(f"    ✓ Found cover ID: {cover_id}")
                            return cover_url
                    
                    print(f"    ⚠ Strategy {strategy_num}: No covers found in results")
                else:
                    print(f"    ✗ Strategy {strategy_num}: HTTP {response.status_code}")
                
                time.sleep(0.5)  # Brief delay between strategies
                
            except requests.exceptions.Timeout:
                print(f"    ⏱ Strategy {strategy_num}: Timeout")
            except requests.exceptions.ConnectionError:
                print(f"    🔌 Strategy {strategy_num}: Connection error")
            except Exception as e:
                print(f"    ❌ Strategy {strategy_num}: {e}")
        
        return None
    
    def download_image(self, url, filepath):
        """Download and process an image"""
        try:
            headers = {
                'User-Agent': 'BookCoverDownloader/1.0 (Educational Project)'
            }
            
            response = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True)
            if response.status_code == 200:
                # Save original image
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Resize and optimize image
                try:
                    with Image.open(filepath) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        
                        # Resize maintaining aspect ratio
                        img.thumbnail(IMAGE_SIZE, Image.Resampling.LANCZOS)
                        
                        # Save optimized version
                        img.save(filepath, 'JPEG', quality=85, optimize=True)
                
                except Exception as e:
                    print(f"    ⚠ Image processing error: {e}")
                    # Keep the original file if processing fails
                
                return True
            else:
                print(f"    ❌ Download failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    ❌ Download error: {e}")
            return False
    
    def process_book(self, book_id, title, author):
        """Process a single book to download its cover"""
        print(f"\n📖 Processing: '{title}' by {author}")
        
        # Generate filename
        filename = self.get_book_filename(book_id, title, author)
        filepath = self.covers_dir / filename
        
        # Check if we already have this cover
        book_key = f"{book_id}_{title}_{author}"
        if book_key in self.cover_mappings:
            existing_file = self.cover_mappings[book_key]
            if os.path.exists(self.covers_dir / existing_file):
                print(f"  ✓ Already have cover: {existing_file}")
                self.stats['already_had_covers'] += 1
                return existing_file
        
        # Check if file already exists
        if filepath.exists():
            print(f"  ✓ File already exists: {filename}")
            self.cover_mappings[book_key] = filename
            self.stats['already_had_covers'] += 1
            return filename
        
        # Search for cover URL
        cover_url = self.search_open_library(title, author)
        
        if not cover_url:
            print(f"  ❌ No cover URL found")
            self.stats['failed_downloads'] += 1
            return None
        
        # Download the cover
        print(f"  📥 Downloading from: {cover_url}")
        
        for attempt in range(MAX_RETRIES):
            if self.download_image(cover_url, filepath):
                print(f"  ✅ Successfully downloaded: {filename}")
                self.cover_mappings[book_key] = filename
                self.stats['new_downloads'] += 1
                return filename
            else:
                if attempt < MAX_RETRIES - 1:
                    print(f"  ⏳ Retrying... (attempt {attempt + 2}/{MAX_RETRIES})")
                    time.sleep(2)
        
        print(f"  ❌ Failed to download after {MAX_RETRIES} attempts")
        self.stats['failed_downloads'] += 1
        return None
    
    def get_books_from_database(self):
        """Get all books from the SQLite database"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, title, author FROM books ORDER BY id')
            books = cursor.fetchall()
            
            conn.close()
            print(f"📚 Found {len(books)} books in database")
            return books
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
    
    def update_database_with_covers(self):
        """Update the database with local cover paths"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            updated_count = 0
            for book_key, filename in self.cover_mappings.items():
                # Extract book_id from the key
                try:
                    book_id = book_key.split('_')[0]
                    local_url = f"/static/covers/{filename}"
                    
                    cursor.execute(
                        'UPDATE books SET cover_url = ? WHERE id = ?',
                        (local_url, book_id)
                    )
                    updated_count += 1
                    
                except Exception as e:
                    print(f"Error updating book {book_key}: {e}")
            
            conn.commit()
            conn.close()
            
            print(f"✅ Updated {updated_count} book records in database")
            
        except Exception as e:
            print(f"❌ Database update error: {e}")
    
    def print_statistics(self):
        """Print download statistics"""
        print("\n" + "="*60)
        print("📊 DOWNLOAD STATISTICS")
        print("="*60)
        print(f"Total books processed: {self.stats['total_books']}")
        print(f"Already had covers: {self.stats['already_had_covers']}")
        print(f"New downloads: {self.stats['new_downloads']}")
        print(f"Failed downloads: {self.stats['failed_downloads']}")
        print(f"Skipped: {self.stats['skipped']}")
        
        success_rate = 0
        if self.stats['total_books'] > 0:
            covers_available = self.stats['already_had_covers'] + self.stats['new_downloads']
            success_rate = (covers_available / self.stats['total_books']) * 100
        
        print(f"Success rate: {success_rate:.1f}%")
        print("="*60)
    
    def run(self, limit=None):
        """Main execution method"""
        print("🚀 Starting Book Cover Download Process")
        print(f"📁 Covers directory: {self.covers_dir.absolute()}")
        
        # Get books from database
        books = self.get_books_from_database()
        if not books:
            print("❌ No books found in database!")
            return
        
        # Limit processing if specified
        if limit:
            books = books[:limit]
            print(f"⚠ Processing limited to first {limit} books")
        
        self.stats['total_books'] = len(books)
        
        # Process each book
        for i, (book_id, title, author) in enumerate(books, 1):
            print(f"\n[{i}/{len(books)}]", end=" ")
            
            try:
                self.process_book(book_id, title, author)
                
                # Save progress periodically
                if i % 10 == 0:
                    self.save_cover_mappings()
                    print(f"  💾 Progress saved ({i}/{len(books)})")
                
                # Rate limiting
                if i < len(books):  # Don't delay after the last book
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                    
            except KeyboardInterrupt:
                print("\n\n⏹ Process interrupted by user")
                break
            except Exception as e:
                print(f"  ❌ Unexpected error: {e}")
                self.stats['failed_downloads'] += 1
        
        # Final save and database update
        self.save_cover_mappings()
        self.update_database_with_covers()
        self.print_statistics()
        
        print("\n✅ Cover download process completed!")
        print(f"📁 Covers saved to: {self.covers_dir.absolute()}")
        print(f"📋 Mappings saved to: {os.path.abspath(COVERS_DATABASE)}")


def main():
    """Main function with command line argument handling"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download book covers for the reading challenge')
    parser.add_argument('--limit', type=int, help='Limit number of books to process (for testing)')
    parser.add_argument('--stats-only', action='store_true', help='Only show current statistics')
    
    args = parser.parse_args()
    
    downloader = CoverDownloader()
    
    if args.stats_only:
        # Show current statistics
        if os.path.exists(COVERS_DATABASE):
            print(f"📊 Current cover mappings: {len(downloader.cover_mappings)}")
            cover_files = list(downloader.covers_dir.glob("*.jpg"))
            print(f"📁 Cover files on disk: {len(cover_files)}")
        else:
            print("📊 No cover mappings found yet")
        return
    
    # Run the download process
    downloader.run(limit=args.limit)


if __name__ == '__main__':
    main()
