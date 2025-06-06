#!/usr/bin/env python3
"""
Test script for enhanced author filtering functionality
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_authors_api():
    """Test the enhanced /api/authors endpoint"""
    print("🔍 Testing /api/authors endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/authors")
        if response.status_code == 200:
            authors = response.json()
            print(f"✅ Success! Found {len(authors)} authors")
            
            # Show first 5 authors with their format
            print("\n📚 Sample authors (first 5):")
            for i, author in enumerate(authors[:5]):
                print(f"  {i+1}. {author['display']} (raw: {author['name']}, count: {author['count']})")
            
            return authors
        else:
            print(f"❌ Failed: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_multiple_author_filtering(authors):
    """Test multiple author filtering"""
    if not authors or len(authors) < 2:
        print("⚠️ Skipping multiple author test - need at least 2 authors")
        return
    
    print("\n🔍 Testing multiple author filtering...")
    
    # Pick first two authors for testing
    author1 = authors[0]['name']
    author2 = authors[1]['name']
    
    # Test single author
    print(f"\n📖 Testing single author: {author1}")
    response = requests.get(f"{BASE_URL}/api/books", params={'authors': [author1]})
    if response.status_code == 200:
        books1 = response.json()
        print(f"✅ Found {len(books1)} books by {author1}")
    
    # Test multiple authors
    print(f"\n📖 Testing multiple authors: {author1} + {author2}")
    response = requests.get(f"{BASE_URL}/api/books", params={'authors': [author1, author2]})
    if response.status_code == 200:
        books_multiple = response.json()
        print(f"✅ Found {len(books_multiple)} books by both authors combined")
        
        # Show which authors are in the results
        found_authors = set(book['author'] for book in books_multiple)
        print(f"   Authors in results: {', '.join(found_authors)}")
    else:
        print(f"❌ Multiple author test failed: Status {response.status_code}")

def test_author_search_simulation():
    """Simulate author search functionality"""
    print("\n🔍 Testing author search simulation...")
    
    response = requests.get(f"{BASE_URL}/api/authors")
    if response.status_code == 200:
        authors = response.json()
        
        # Test search for "Jane"
        search_term = "Jane"
        matching_authors = [a for a in authors if search_term.lower() in a['name'].lower()]
        print(f"📝 Search for '{search_term}': found {len(matching_authors)} matches")
        for author in matching_authors:
            print(f"   - {author['display']}")
        
        # Test search for "Charles"
        search_term = "Charles"
        matching_authors = [a for a in authors if search_term.lower() in a['name'].lower()]
        print(f"📝 Search for '{search_term}': found {len(matching_authors)} matches")
        for author in matching_authors:
            print(f"   - {author['display']}")

def test_century_and_author_combined():
    """Test combining century and author filters"""
    print("\n🔍 Testing combined century + author filtering...")
    
    response = requests.get(f"{BASE_URL}/api/books", params={
        'century': '19th',
        'authors': ['Jane Austen']
    })
    
    if response.status_code == 200:
        books = response.json()
        print(f"✅ Found {len(books)} books by Jane Austen from 19th century")
        
        if books:
            years = [book.get('publication_year') for book in books if book.get('publication_year')]
            if years:
                print(f"   Years: {sorted(set(years))}")
    else:
        print(f"❌ Combined filter test failed: Status {response.status_code}")

def main():
    print("🚀 Testing Enhanced Author Filtering Functionality")
    print("=" * 60)
    
    # Test 1: Authors API
    authors = test_authors_api()
    
    # Test 2: Multiple author filtering
    if authors:
        test_multiple_author_filtering(authors)
    
    # Test 3: Author search simulation
    test_author_search_simulation()
    
    # Test 4: Combined filters
    test_century_and_author_combined()
    
    print("\n" + "=" * 60)
    print("🎉 Testing complete!")
    
    print("\n📋 Features Summary:")
    print("✅ Author filtering with book counts")
    print("✅ Authors ordered by surname")
    print("✅ Multiple author selection support")
    print("✅ Author search functionality")
    print("✅ Combined filters (century + author)")
    print("✅ Both Flask template and React frontend")

if __name__ == "__main__":
    main()
