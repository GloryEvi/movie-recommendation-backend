from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    """Genre model for categorizing movies"""
    tmdb_id = models.IntegerField(unique=True, help_text="TMDb genre ID")
    name = models.CharField(max_length=100, help_text="Genre name")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Genres"
    
    def __str__(self):
        return self.name


class Movie(models.Model):
    """Movie model with essential TMDb data"""
    tmdb_id = models.IntegerField(unique=True, help_text="TMDb movie ID")
    title = models.CharField(max_length=200, help_text="Movie title")
    overview = models.TextField(blank=True, help_text="Movie plot summary")
    release_date = models.DateField(null=True, blank=True, help_text="Release date")
    vote_average = models.FloatField(
        default=0.0, 
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Average rating (0-10)"
    )
    popularity = models.FloatField(default=0.0, help_text="TMDb popularity score")
    poster_path = models.CharField(max_length=200, blank=True, help_text="Poster image path")
    backdrop_path = models.CharField(max_length=200, blank=True, help_text="Backdrop image path")
    
    # Many-to-many relationship with Genre through MovieGenre
    genres = models.ManyToManyField(Genre, through='MovieGenre', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-popularity', '-vote_average']
        indexes = [
            models.Index(fields=['tmdb_id']),
            models.Index(fields=['-popularity']),
            models.Index(fields=['-vote_average']),
            models.Index(fields=['release_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'Unknown'})"
    
    @property
    def poster_url(self):
        """Return full poster URL"""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None
    
    @property
    def backdrop_url(self):
        """Return full backdrop URL"""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{self.backdrop_path}"
        return None


class MovieGenre(models.Model):
    """Bridge table for Movie-Genre many-to-many relationship"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('movie', 'genre')
        verbose_name_plural = "Movie Genres"
    
    def __str__(self):
        return f"{self.movie.title} - {self.genre.name}"


class UserFavorite(models.Model):
    """User's favorite movies"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_at']
        verbose_name_plural = "User Favorites"
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
