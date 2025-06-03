# React Frontend for Reading Challenge

This is the experimental React frontend for the Classic Literature Reading Challenge Flask application.

## 🚀 Quick Start

### Option 1: Run Both Backend and Frontend (Recommended)
```bash
# From the main project directory
./start_dev.sh
```

This will start:
- Flask backend on http://localhost:5000
- React frontend on http://localhost:3000

### Option 2: Run Separately

**Start Flask Backend:**
```bash
# From main directory
python app.py
```

**Start React Frontend:**
```bash
# From frontend directory
cd frontend
npm start
```

## 📱 Frontend Features

- **Modern React Interface**: Built with React 18 and React Router
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time API Integration**: Connects to Flask backend via REST API
- **User Authentication**: Login system with session management
- **Book Management**: Browse, filter, and mark books as read
- **Review System**: Add ratings and reviews for completed books
- **Progress Tracking**: Visual progress indicators and statistics

## 🛠️ Tech Stack

- **React 18** - Core framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **CSS3** - Modern styling with animations
- **Flask-CORS** - Cross-origin resource sharing

## 📁 Project Structure

```
frontend/
├── public/           # Static assets
├── src/
│   ├── components/   # React components
│   │   ├── BookList.js      # Main book listing
│   │   ├── BookDetail.js    # Individual book view
│   │   ├── Login.js         # Authentication
│   │   └── About.js         # About page
│   ├── App.js        # Main app component
│   └── App.css       # Global styles
└── package.json      # Dependencies
```

## 🔌 API Endpoints

The React frontend communicates with these Flask API endpoints:

- `GET /api/books` - Get all books with filtering
- `GET /api/book/:id` - Get book details with reviews
- `GET /api/stats` - Get reading statistics
- `POST /api/auth/login` - User authentication
- `POST /api/auth/logout` - User logout
- `GET /api/auth/user` - Get current user
- `POST /api/mark_read/:id/:reader` - Mark book as read
- `POST /api/add_review/:id` - Add book review

## 🎨 Design Features

- **Gradient Hero Section**: Eye-catching header with progress stats
- **Card-based Layout**: Clean, modern book cards with cover images
- **Smart Filtering**: Filter by reader status and century
- **Hover Effects**: Smooth animations and transitions
- **Loading States**: Spinners and loading indicators
- **Error Handling**: User-friendly error messages
- **Mobile Responsive**: Optimized for all screen sizes

## 🔐 Authentication

Users can log in with:
- **Silas**: Username `s` + password
- **Nadine**: Username `n` + password

Authenticated users can:
- Mark their own books as read
- Add reviews and ratings
- See personalized content

## 🚀 Development

To modify the frontend:

1. Edit components in `src/components/`
2. Update styles in the corresponding `.css` files
3. The development server will hot-reload changes
4. Test API integration with the Flask backend

## 🌐 Production Build

To create a production build:

```bash
cd frontend
npm run build
```

This creates a `build/` directory with optimized static files that can be served by Flask or a web server.

## 🔄 Hybrid Setup

This setup allows running both the traditional Flask templates and the React frontend simultaneously:

- **Flask templates**: http://localhost:5000
- **React frontend**: http://localhost:3000
- **API endpoints**: http://localhost:5000/api/*

Users can choose which interface to use, making this a great experimental setup for comparing both approaches.
