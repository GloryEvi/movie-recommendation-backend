from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    # Genre endpoints
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    
    # Movie endpoints
    path('trending/', views.trending_movies, name='trending-movies'),
    path('popular/', views.popular_movies, name='popular-movies'),
    path('search/', views.search_movies, name='search-movies'),
    path('genre/', views.movies_by_genre, name='movies-by-genre'),
    path('<int:tmdb_id>/', views.MovieDetailView.as_view(), name='movie-detail'),
    
    # User favorites
    path('favorites/', views.UserFavoriteListView.as_view(), name='user-favorites'),
    path('favorites/<int:pk>/', views.UserFavoriteDetailView.as_view(), name='user-favorite-detail'),
    
    # User profile
    path('profile/', views.user_profile, name='user-profile'),
]