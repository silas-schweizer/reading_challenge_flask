#!/bin/bash

# Reading Challenge Flask App - Production Deployment Script
# This script helps deploy the application to various platforms

set -e

echo "=== Reading Challenge Flask App Deployment ==="
echo

# Check if we're in the right directory
if [[ ! -f "app.py" || ! -f "requirements.txt" ]]; then
    echo "Error: Please run this script from the reading_challenge_flask directory"
    exit 1
fi

echo "✓ Found application files"

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo "Warning: .env file not found. Creating from example..."
    cp .env.example .env
    echo "Please edit .env file with your actual values before deployment!"
fi

echo "✓ Environment file ready"

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Test the application works
echo "Testing application startup..."
FLASK_ENV=production python -c "
import app
print('Application imports successfully')
"

echo "✓ Application startup test passed"

echo
echo "=== Deployment Options ==="
echo "1. Heroku Deployment:"
echo "   git add ."
echo "   git commit -m 'Deploy reading challenge app'"
echo "   heroku create your-reading-challenge-app"
echo "   heroku config:set FLASK_ENV=production"
echo "   heroku config:set SECRET_KEY=\$(python -c 'import secrets; print(secrets.token_hex(32))')"
echo "   heroku config:set SILAS_PASSWORD_HASH=\$(grep SILAS_PASSWORD_HASH .env | cut -d= -f2)"
echo "   heroku config:set NADINE_PASSWORD_HASH=\$(grep NADINE_PASSWORD_HASH .env | cut -d= -f2)"
echo "   git push heroku main"
echo
echo "2. Railway Deployment:"
echo "   railway new"
echo "   railway add"
echo "   railway up"
echo
echo "3. Docker Deployment:"
echo "   docker build -t reading-challenge ."
echo "   docker run -d -p 8000:8000 --env-file .env reading-challenge"
echo
echo "4. Local Production Test:"
echo "   ~/.local/bin/gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app"
echo

echo "=== Next Steps ==="
echo "1. Edit .env with secure SECRET_KEY if deploying to production"
echo "2. Choose a deployment method above"
echo "3. Test the deployed application"
echo "4. Share the URL with Nadine for beta testing"
echo

echo "✓ Deployment preparation complete!"
