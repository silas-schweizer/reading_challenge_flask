#!/usr/bin/env python3
"""
Local Book Cover Management System
Manages book covers stored locally and provides utilities for the Flask app.
"""

import os
import sqlite3
import json
import hashlib
import re
from pathlib import Path
from PIL import Image
import requests
import shutil

# Configuration - use absolute paths like app.py
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reading_challenge.db')
COVERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'covers')
COVERS_DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covers_mapping.json')
PLACEHOLDER_COVERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'covers', 'placeholders')
DEFAULT_COVER_URL = '/static/covers/default_book_cover.jpg'

class LocalCoverManager:
    def __init__(self):
        self.covers_dir = Path(COVERS_DIR)
        self.covers_dir.mkdir(parents=True, exist_ok=True)
        
        self.placeholders_dir = Path(PLACEHOLDER_COVERS_DIR)
        self.placeholders_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing cover mappings
        self.cover_mappings = self.load_cover_mappings()
        
        # Create default placeholder cover if it doesn't exist
        self.ensure_default_cover()
    
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
    
    def generate_book_filename(self, book_id, title, author):
        """Generate a safe filename for the book cover"""
        # Create a hash of title and author for uniqueness
        content = f"{title}_{author}".lower()
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # Clean title for filename
        safe_title = re.sub(r'[^\w\s-]', '', title)[:30]
        safe_title = re.sub(r'\s+', '_', safe_title)
        
        return f"book_{book_id}_{safe_title}_{content_hash}.jpg"
    
    def create_default_cover(self):
        """Create a simple default book cover image"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple default cover
            width, height = 300, 450
            background_color = (70, 130, 180)  # Steel Blue
            text_color = (255, 255, 255)  # White
            
            # Create image
            img = Image.new('RGB', (width, height), background_color)
            draw = ImageDraw.Draw(img)
            
            # Try to use a system font, fallback to default
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                # Fallback to default font
                try:
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                except:
                    font_large = None
                    font_small = None
            
            # Add text
            if font_large and font_small:
                # Book icon (simple rectangle)
                draw.rectangle([width//2-40, height//2-60, width//2+40, height//2+20], outline=text_color, width=3)
                
                # Text
                draw.text((width//2, height//2+50), "No Cover", font=font_large, fill=text_color, anchor="mm")
                draw.text((width//2, height//2+80), "Available", font=font_small, fill=text_color, anchor="mm")
            else:
                # Simple rectangle if fonts fail
                draw.rectangle([width//4, height//4, 3*width//4, 3*height//4], outline=text_color, width=5)
            
            # Save the default cover
            default_path = self.covers_dir / 'default_book_cover.jpg'
            img.save(default_path, 'JPEG', quality=85)
            
            print(f"✅ Created default book cover: {default_path}")
            return str(default_path)
            
        except Exception as e:
            print(f"❌ Error creating default cover: {e}")
            return None
    
    def ensure_default_cover(self):
        """Ensure a default cover exists"""
        default_path = self.covers_dir / 'default_book_cover.jpg'
        if not default_path.exists():
            self.create_default_cover()
    
    def get_cover_url(self, book_id, title, author):
        """Get the cover URL for a book, returning default if not available"""
        # Check if we have a specific cover for this book
        book_key = f"{book_id}_{title}_{author}"
        
        if book_key in self.cover_mappings:
            cover_filename = self.cover_mappings[book_key]
            cover_path = self.covers_dir / cover_filename
            if cover_path.exists():
                return f"/static/covers/{cover_filename}"
        
        # Check if there's a file with the expected name
        expected_filename = self.generate_book_filename(book_id, title, author)
        expected_path = self.covers_dir / expected_filename
        if expected_path.exists():
            # Add to mappings
            self.cover_mappings[book_key] = expected_filename
            self.save_cover_mappings()
            return f"/static/covers/{expected_filename}"
        
        # Return default cover
        return DEFAULT_COVER_URL
    
    def add_cover_manually(self, book_id, title, author, image_path):
        """Manually add a cover for a book from a local image file"""
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return False
            
            # Generate target filename
            filename = self.generate_book_filename(book_id, title, author)
            target_path = self.covers_dir / filename
            
            # Copy and process the image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize maintaining aspect ratio
                img.thumbnail((300, 450), Image.Resampling.LANCZOS)
                
                # Save optimized version
                img.save(target_path, 'JPEG', quality=85, optimize=True)
            
            # Update mappings
            book_key = f"{book_id}_{title}_{author}"
            self.cover_mappings[book_key] = filename
            self.save_cover_mappings()
            
            print(f"✅ Added cover for '{title}' by {author}: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding cover: {e}")
            return False
    
    def list_books_without_covers(self):
        """List all books that don't have covers"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, title, author FROM books ORDER BY id')
            books = cursor.fetchall()
            conn.close()
            
            books_without_covers = []
            for book_id, title, author in books:
                cover_url = self.get_cover_url(book_id, title, author)
                if cover_url == DEFAULT_COVER_URL:
                    books_without_covers.append((book_id, title, author))
            
            return books_without_covers
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
    
    def update_database_covers(self):
        """Update all books in the database with their current cover URLs"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, title, author FROM books')
            books = cursor.fetchall()
            
            updated_count = 0
            for book_id, title, author in books:
                cover_url = self.get_cover_url(book_id, title, author)
                cursor.execute(
                    'UPDATE books SET cover_url = ? WHERE id = ?',
                    (cover_url, book_id)
                )
                updated_count += 1
            
            conn.commit()
            conn.close()
            
            print(f"✅ Updated {updated_count} book records with cover URLs")
            return updated_count
            
        except Exception as e:
            print(f"❌ Database update error: {e}")
            return 0
    
    def get_statistics(self):
        """Get statistics about covers"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM books')
            total_books = cursor.fetchone()[0]
            
            conn.close()
            
            books_with_covers = 0
            books_without_covers = 0
            
            for book_id, title, author in self.get_all_books():
                cover_url = self.get_cover_url(book_id, title, author)
                if cover_url == DEFAULT_COVER_URL:
                    books_without_covers += 1
                else:
                    books_with_covers += 1
            
            return {
                'total_books': total_books,
                'books_with_covers': books_with_covers,
                'books_without_covers': books_without_covers,
                'cover_files': len(list(self.covers_dir.glob("*.jpg"))),
                'mappings': len(self.cover_mappings)
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def get_all_books(self):
        """Get all books from database"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, title, author FROM books ORDER BY id')
            books = cursor.fetchall()
            conn.close()
            
            return books
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Local Book Cover Management')
    parser.add_argument('--stats', action='store_true', help='Show cover statistics')
    parser.add_argument('--update-db', action='store_true', help='Update database with current cover URLs')
    parser.add_argument('--list-missing', action='store_true', help='List books without covers')
    parser.add_argument('--add-cover', nargs=3, metavar=('BOOK_ID', 'IMAGE_PATH', 'TITLE'), 
                       help='Add a cover manually: book_id image_path title')
    
    args = parser.parse_args()
    
    manager = LocalCoverManager()
    
    if args.stats:
        stats = manager.get_statistics()
        print("\n📊 COVER STATISTICS")
        print("=" * 40)
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print("=" * 40)
    
    elif args.update_db:
        print("🔄 Updating database with current cover URLs...")
        count = manager.update_database_covers()
        print(f"✅ Updated {count} book records")
    
    elif args.list_missing:
        books = manager.list_books_without_covers()
        print(f"\n📚 BOOKS WITHOUT COVERS ({len(books)} total)")
        print("=" * 60)
        for book_id, title, author in books:
            print(f"ID {book_id}: '{title}' by {author}")
        print("=" * 60)
    
    elif args.add_cover:
        book_id, image_path, title = args.add_cover
        # This is a simplified version - in practice you'd get author from DB
        print("⚠ Note: You'll need to provide the author name as well")
        print("Use the LocalCoverManager.add_cover_manually() method directly for full functionality")
    
    else:
        print("📖 Local Book Cover Manager")
        print("Use --help to see available options")


if __name__ == '__main__':
    main()
