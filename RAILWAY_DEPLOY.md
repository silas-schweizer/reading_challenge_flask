# Railway Configuration for Reading Challenge App

## Quick Deploy Instructions

1. Go to https://railway.app
2. Sign up/Login with GitHub
3. Click "New Project" 
4. Choose "Deploy from GitHub repo"
5. Select your reading_challenge_flask repository
6. Railway will auto-detect it's a Python app

## Environment Variables to Set in Railway Dashboard

After deployment, go to your project settings and add these environment variables:

```
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key-here
SILAS_PASSWORD_HASH=pbkdf2:sha256:600000$PGy3qJKD5uwUJM7e$ed89728d2982108cafbbcb10e56687bf09740ea8076ae651f9652bf4c223783f
NADINE_PASSWORD_HASH=pbkdf2:sha256:600000$KD2MOxh8V3MsvrZh$9d86f5a32244b84a3fa120417b1a3e9082848ba8bfaa8ebe35d1a03e2e250a7f
DATABASE_URL=sqlite:///reading_challenge.db
OPENLIBRARY_API_URL=https://openlibrary.org/search.json
PORT=8000
```

## Build Configuration

Railway should automatically detect the Python app and use:
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn wsgi:app`

The Procfile is already configured for this.

## Expected Results

After deployment, you'll get a URL like:
`https://reading-challenge-production-xxxx.up.railway.app`

The app should start successfully and Nadine can access it with:
- Username: n
- Password: n

You can access it with:
- Username: s  
- Password: s

## Troubleshooting

If the deployment fails:
1. Check the build logs in Railway dashboard
2. Ensure all environment variables are set
3. The database will be automatically created on first run
4. All 103 books from the CSV will be loaded

## Alternative: Manual CLI Deployment

If you have Railway CLI working, run:
```bash
railway login
railway new
railway up
railway open
```
