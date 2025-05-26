#!/usr/bin/env python3

"""
Password hash generator for production deployment.
Run this script to generate secure password hashes for the .env file.
"""

from werkzeug.security import generate_password_hash
import getpass
import sys

def generate_password_hashes():
    print("=== Reading Challenge Password Hash Generator ===")
    print("This will help you generate secure password hashes for production.")
    print()
    
    try:
        print("Enter password for Silas:")
        silas_password = getpass.getpass("Silas password: ")
        if len(silas_password) < 8:
            print("Warning: Password should be at least 8 characters long!")
        
        print("\nEnter password for Nadine:")
        nadine_password = getpass.getpass("Nadine password: ")
        if len(nadine_password) < 8:
            print("Warning: Password should be at least 8 characters long!")
        
        # Generate hashes
        silas_hash = generate_password_hash(silas_password)
        nadine_hash = generate_password_hash(nadine_password)
        
        print("\n" + "="*60)
        print("Generated Password Hashes")
        print("="*60)
        print("\nAdd these lines to your .env file:")
        print()
        print(f"SILAS_PASSWORD_HASH={silas_hash}")
        print(f"NADINE_PASSWORD_HASH={nadine_hash}")
        print()
        print("IMPORTANT: Keep these hashes secure and don't share them!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_password_hashes()
