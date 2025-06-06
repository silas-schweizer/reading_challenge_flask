#!/usr/bin/env python3
"""
Test script to verify author filtering functionality
"""
import sqlite3
import requests
import json

def test_database():
    """Test database author data"""
    print("=== Testing Database ===")
    conn = sqlite3.connect('reading_challenge.db')
    cursor = conn.cursor()
    
    # Get total authors
    cursor.execute('SELECT COUNT(DISTINCT author) FROM books')
    author_count = cursor.fetchone()[0]
    print(f"Total unique authors: {author_count}")
    
    # Get top authors
    cursor.execute('SELECT author, COUNT(*) as book_count FROM books GROUP BY author ORDER BY book_count DESC LIMIT 5')
    top_authors = cursor.fetchall()
    print("\nTop 5 authors by book count:")
    for author, count in top_authors:
        print(f"  {author}: {count} books")
    
    conn.close()

def test_api():
    """Test API endpoints"""
    print("\n=== Testing API Endpoints ===")
    base_url = "http://localhost:5000"
    
    try:
        # Test authors endpoint
        response = requests.get(f"{base_url}/api/authors", timeout=5)
        if response.status_code == 200:
            authors = response.json()
            print(f"✓ /api/authors: {len(authors)} authors returned")
            print(f"  First 3 authors: {authors[:3]}")
        else:
            print(f"✗ /api/authors: Status {response.status_code}")
        
        # Test books with author filter
        test_author = "Jane Austen"
        response = requests.get(f"{base_url}/api/books", params={"author": test_author}, timeout=5)
        if response.status_code == 200:
            books = response.json()
            print(f"✓ /api/books?author={test_author}: {len(books)} books returned")
            if books:
                print(f"  Sample book: {books[0]['title']}")
        else:
            print(f"✗ /api/books with author filter: Status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ API connection error: {e}")

if __name__ == "__main__":
    test_database()
    test_api()
    print("\n=== Test Complete ===")
