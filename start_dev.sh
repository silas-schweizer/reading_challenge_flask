#!/bin/bash
# start_dev.sh - Script to start both Flask backend and React frontend

echo "🚀 Starting Reading Challenge Development Environment"
echo "=================================================="

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the reading_challenge_flask directory."
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down development servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

echo "🐍 Starting Flask backend on port 5000..."
# Start Flask backend in the background
FLASK_ENV=development python app.py &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 3

echo "⚛️  Starting React frontend on port 3000..."
# Start React frontend in the background
cd frontend
npm start &
REACT_PID=$!

# Go back to main directory
cd ..

echo ""
echo "✅ Development servers started!"
echo "🌐 Flask Backend: http://localhost:5000"
echo "🌐 React Frontend: http://localhost:3000"
echo "🌐 API Endpoints: http://localhost:5000/api/*"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for background processes
wait
