#!/usr/bin/env python3

import sqlite3
import requests
import re
import urllib.parse

DATABASE_PATH = 'reading_challenge.db'

def get_cover_image(title, author):
    try:
        # Clean title and author for API search
        clean_title = re.sub(r'[^\w\s]', '', title).strip()
        clean_author = re.sub(r'[^\w\s]', '', author).strip()
        
        # URL encode the parameters
        encoded_title = urllib.parse.quote(clean_title)
        encoded_author = urllib.parse.quote(clean_author)
        
        # Search Open Library API (use HTTPS)
        search_url = f"https://openlibrary.org/search.json?title={encoded_title}&author={encoded_author}&limit=1"
        
        print(f"Searching URL: {search_url}")
        
        headers = {
            'User-Agent': 'ReadingChallenge/1.0 (https://github.com/reading-challenge)'
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {data}")
            if data.get('docs') and len(data['docs']) > 0:
                book = data['docs'][0]
                print(f"Book data: {book}")
                if 'cover_i' in book:
                    cover_id = book['cover_i']
                    # Use HTTPS for cover images
                    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                    print(f"Found cover for '{title}' by {author}: {cover_url}")
                    return cover_url
                else:
                    print(f"No cover_i field for '{title}' by {author}")
            else:
                print(f"No search results for '{title}' by {author}")
        else:
            print(f"API request failed for '{title}' by {author}: Status {response.status_code}")
            
    except Exception as e:
        print(f"Error fetching cover for '{title}' by {author}: {e}")
    
    return None

if __name__ == "__main__":
    # Test with a book we know should have covers
    print("Testing with Le Père Goriot...")
    result = get_cover_image("Le Père Goriot", "Honoré de Balzac")
    print(f"Result: {result}")
    
    print("\nTesting with Fathers and Sons...")
    result = get_cover_image("Fathers and Sons", "Ivan Turgenev")
    print(f"Result: {result}")
