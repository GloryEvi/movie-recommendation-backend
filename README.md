# 🎬 Movie Recommendation Backend

A robust Django REST API backend for movie recommendations with user authentication, favorites, and caching.

## 🚀 Features

- **Movie Data Integration**: Real-time data from TMDb API
- **User Authentication**: JWT-based secure authentication
- **User Favorites**: Save and manage favorite movies
- **Genre Filtering**: Browse movies by genre
- **Redis Caching**: High-performance caching for API responses
- **API Documentation**: Interactive Swagger documentation
- **Docker Support**: Containerized deployment

## 🛠️ Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Caching**: Redis
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: drf-spectacular (Swagger)
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- TMDb API Key

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd movie-recommendation-backend
```

### 2. Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create `.env` file:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=movie_db
DB_USER=postgres
DB_PASSWORD=your-password
TMDB_API_KEY=your-tmdb-api-key
REDIS_URL=redis://localhost:6379/1
```

### 4. Database Setup
```bash
# Create PostgreSQL database
createdb movie_db

# Run migrations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start Services
```bash
# Start Redis
redis-server

# Start Django
python manage.py runserver
```

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

## 📚 API Documentation

Visit `http://localhost:8000/api/docs/` for interactive Swagger documentation.

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `POST /api/auth/change-password/` - Change password

### Movies
- `GET /api/movies/trending/` - Get trending movies
- `GET /api/movies/popular/` - Get popular movies
- `GET /api/movies/search/?q=query` - Search movies
- `GET /api/movies/genre/?genre=action` - Movies by genre
- `GET /api/movies/{tmdb_id}/` - Movie details

### Favorites
- `GET /api/movies/favorites/` - List user favorites
- `POST /api/movies/favorites/` - Add to favorites
- `DELETE /api/movies/favorites/{id}/` - Remove from favorites

### Genres
- `GET /api/movies/genres/` - List all genres

## 🔧 Usage Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

### Get Trending Movies
```bash
curl -X GET http://localhost:8000/api/movies/trending/
```

### Add Movie to Favorites
```bash
curl -X POST http://localhost:8000/api/movies/favorites/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 1}'
```

## 🗄️ Database Schema

### Models Overview
- **User**: Django's built-in user model
- **Movie**: Core movie data from TMDb
- **Genre**: Movie categories
- **MovieGenre**: Many-to-many bridge table
- **UserFavorite**: User's favorite movies

### Key Relationships
- User ↔ Movie (through UserFavorite)
- Movie ↔ Genre (through MovieGenre)

## ⚡ Performance Features

### Caching Strategy
- **Trending Movies**: 1 hour cache
- **Popular Movies**: 1 hour cache
- **Movie Details**: 24 hour cache
- **Genres**: 1 week cache

### Database Optimization
- Indexed on tmdb_id, popularity, vote_average
- Optimized queries with select_related/prefetch_related
- Unique constraints for data integrity

## 🛡️ Security Features

- JWT token-based authentication
- Password validation
- CORS protection
- SQL injection prevention (Django ORM)
- Rate limiting ready

## 📈 Scalability

- Redis caching reduces API calls
- Database indexing for fast queries
- Pagination for large datasets
- Docker containerization for easy scaling

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

## 📱 Frontend Integration

The API is designed to work with any frontend framework:
- React/Vue.js/Angular
- Mobile apps (React Native, Flutter)
- Desktop applications

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure secure SECRET_KEY
- [ ] Set up production database
- [ ] Configure Redis instance
- [ ] Set ALLOWED_HOSTS
- [ ] Configure static files serving

### Supported Platforms
- Railway
- Render
- Heroku
- AWS/GCP/Azure



## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request



---

**Built with ❤️ for ProDev Backend Engineering Program**