# Production Deployment Guide

## 🚨 Critical Changes for Production

### 1. Environment Setup
```bash
# Create a .env file with secure values:
cp .env.example .env

# Edit .env with your actual values:
SECRET_KEY=your-super-long-random-secret-key-at-least-32-characters
FLASK_ENV=production
SILAS_PASSWORD_HASH=your-bcrypt-hashed-password
NADINE_PASSWORD_HASH=your-bcrypt-hashed-password
```

### 2. Generate Secure Password Hashes
```python
# Run this Python script to generate secure password hashes:
from werkzeug.security import generate_password_hash

silas_hash = generate_password_hash("your_secure_silas_password")
nadine_hash = generate_password_hash("your_secure_nadine_password")

print(f"SILAS_PASSWORD_HASH={silas_hash}")
print(f"NADINE_PASSWORD_HASH={nadine_hash}")
```

### 3. Security Checklist
- [ ] **Change default passwords** from 'silas'/'nadine' to strong passwords
- [ ] **Set secure SECRET_KEY** (32+ random characters)
- [ ] **Remove debug mode** (FLASK_ENV=production)
- [ ] **Use HTTPS** in production
- [ ] **Set up proper database** (PostgreSQL for production)
- [ ] **Configure reverse proxy** (Nginx recommended)
- [ ] **Set up monitoring** and logging
- [ ] **Regular backups** of database

## Deployment Options

### Option 1: Heroku Deployment
```bash
# Install Heroku CLI, then:
heroku create your-reading-challenge-app
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set FLASK_ENV=production
heroku config:set SILAS_PASSWORD_HASH="your-hash"
heroku config:set NADINE_PASSWORD_HASH="your-hash"
git push heroku main
```

### Option 2: DigitalOcean/AWS/VPS
```bash
# On your server:
git clone your-repo
cd reading_challenge_flask
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key"
export FLASK_ENV=production

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

### Option 3: Docker Deployment
```bash
# Use the provided Dockerfile
docker build -t reading-challenge .
docker run -p 8000:8000 --env-file .env reading-challenge
```

## Production Database

For production, consider upgrading from SQLite to PostgreSQL:

1. Install PostgreSQL driver: `pip install psycopg2-binary`
2. Update DATABASE_URL in .env: `postgresql://user:pass@host/dbname`
3. Update config.py to handle PostgreSQL connections

## Monitoring & Maintenance

- Set up application monitoring (New Relic, DataDog, etc.)
- Configure log aggregation
- Set up automated backups
- Monitor disk space and performance
- Regular security updates

## SSL/HTTPS Setup

For production, always use HTTPS:
- Use Let's Encrypt for free SSL certificates
- Configure your reverse proxy (Nginx) to handle SSL termination
- Redirect HTTP to HTTPS

## Performance Optimization

- Use a CDN for static assets
- Implement caching (Redis/Memcached)
- Optimize database queries
- Use connection pooling for database
- Compress responses (gzip)

## Emergency Procedures

- Keep database backups in multiple locations
- Document rollback procedures
- Have monitoring alerts set up
- Maintain staging environment for testing
