import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import Movie, Genre, MovieGenre
import logging

logger = logging.getLogger(__name__)


class TMDbService:
    """Service class for TMDb API interactions"""
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.headers = {'Authorization': f'Bearer {self.api_key}'}
    
    def _make_request(self, endpoint, params=None):
        """Make HTTP request to TMDb API"""
        url = f"{self.base_url}/{endpoint}"
        default_params = {'api_key': self.api_key}
        
        if params:
            default_params.update(params)
            
        try:
            response = requests.get(url, params=default_params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request failed: {e}")
            return None
    
    def fetch_genres(self):
        """Fetch and cache movie genres from TMDb"""
        cache_key = 'tmdb_genres'
        genres_data = cache.get(cache_key)
        
        if not genres_data:
            genres_data = self._make_request('genre/movie/list')
            if genres_data:
                cache.set(cache_key, genres_data, settings.CACHE_TIMEOUT['GENRES'])
        
        if genres_data and 'genres' in genres_data:
            for genre_data in genres_data['genres']:
                Genre.objects.get_or_create(
                    tmdb_id=genre_data['id'],
                    defaults={'name': genre_data['name']}
                )
        
        return Genre.objects.all()
    
    def fetch_trending_movies(self, time_window='day', page=1):
        """Fetch trending movies from TMDb"""
        cache_key = f'trending_movies_{time_window}_{page}'
        movies_data = cache.get(cache_key)
        
        if not movies_data:
            endpoint = f'trending/movie/{time_window}'
            movies_data = self._make_request(endpoint, {'page': page})
            if movies_data:
                cache.set(cache_key, movies_data, settings.CACHE_TIMEOUT['TRENDING_MOVIES'])
        
        if movies_data and 'results' in movies_data:
            movies = []
            for movie_data in movies_data['results']:
                movie = self._create_or_update_movie(movie_data)
                if movie:
                    movies.append(movie)
            return movies, movies_data.get('total_pages', 1)
        
        return [], 0
    
    def fetch_popular_movies(self, page=1):
        """Fetch popular movies from TMDb"""
        cache_key = f'popular_movies_{page}'
        movies_data = cache.get(cache_key)
        
        if not movies_data:
            movies_data = self._make_request('movie/popular', {'page': page})
            if movies_data:
                cache.set(cache_key, movies_data, settings.CACHE_TIMEOUT['POPULAR_MOVIES'])
        
        if movies_data and 'results' in movies_data:
            movies = []
            for movie_data in movies_data['results']:
                movie = self._create_or_update_movie(movie_data)
                if movie:
                    movies.append(movie)
            return movies, movies_data.get('total_pages', 1)
        
        return [], 0
    
    def fetch_movie_details(self, tmdb_id):
        """Fetch detailed movie information"""
        cache_key = f'movie_details_{tmdb_id}'
        movie_data = cache.get(cache_key)
        
        if not movie_data:
            movie_data = self._make_request(f'movie/{tmdb_id}')
            if movie_data:
                cache.set(cache_key, movie_data, settings.CACHE_TIMEOUT['MOVIE_DETAILS'])
        
        if movie_data:
            return self._create_or_update_movie(movie_data, detailed=True)
        
        return None
    
    def search_movies(self, query, page=1):
        """Search movies by title"""
        if not query.strip():
            return [], 0
            
        cache_key = f'search_movies_{query}_{page}'
        movies_data = cache.get(cache_key)
        
        if not movies_data:
            params = {'query': query, 'page': page}
            movies_data = self._make_request('search/movie', params)
            if movies_data:
                cache.set(cache_key, movies_data, 1800)  # Cache for 30 minutes
        
        if movies_data and 'results' in movies_data:
            movies = []
            for movie_data in movies_data['results']:
                movie = self._create_or_update_movie(movie_data)
                if movie:
                    movies.append(movie)
            return movies, movies_data.get('total_pages', 1)
        
        return [], 0
    
    def _create_or_update_movie(self, movie_data, detailed=False):
        """Create or update movie in database"""
        try:
            # Parse release date
            release_date = None
            if movie_data.get('release_date'):
                try:
                    release_date = timezone.datetime.strptime(
                        movie_data['release_date'], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    pass
            
            # Create or update movie
            movie, created = Movie.objects.update_or_create(
                tmdb_id=movie_data['id'],
                defaults={
                    'title': movie_data.get('title', ''),
                    'overview': movie_data.get('overview', ''),
                    'release_date': release_date,
                    'vote_average': movie_data.get('vote_average', 0.0),
                    'popularity': movie_data.get('popularity', 0.0),
                    'poster_path': movie_data.get('poster_path', ''),
                    'backdrop_path': movie_data.get('backdrop_path', ''),
                }
            )
            
            # Handle genres if present
            if 'genres' in movie_data:  # Detailed movie data
                genre_ids = [genre['id'] for genre in movie_data['genres']]
            elif 'genre_ids' in movie_data:  # Basic movie data
                genre_ids = movie_data['genre_ids']
            else:
                genre_ids = []
            
            if genre_ids:
                # Ensure genres exist
                self.fetch_genres()
                
                # Clear existing genre relationships
                MovieGenre.objects.filter(movie=movie).delete()
                
                # Add new genre relationships
                for genre_id in genre_ids:
                    try:
                        genre = Genre.objects.get(tmdb_id=genre_id)
                        MovieGenre.objects.get_or_create(movie=movie, genre=genre)
                    except Genre.DoesNotExist:
                        continue
            
            return movie
            
        except Exception as e:
            logger.error(f"Error creating/updating movie {movie_data.get('id')}: {e}")
            return None
    
    def get_movies_by_genre(self, genre_name, page=1):
        """Get movies filtered by genre"""
        try:
            genre = Genre.objects.get(name__iexact=genre_name)
            movies = Movie.objects.filter(genres=genre).order_by('-popularity')
            
            # Paginate results
            start = (page - 1) * 20
            end = start + 20
            paginated_movies = movies[start:end]
            total_pages = (movies.count() + 19) // 20  # Ceiling division
            
            return list(paginated_movies), total_pages
            
        except Genre.DoesNotExist:
            return [], 0