from django.shortcuts import render

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Movie, Genre, UserFavorite
from .serializers import (
    MovieSerializer, MovieListSerializer, GenreSerializer,
    UserFavoriteSerializer, UserSerializer
)
from .services import TMDbService


class GenreListView(generics.ListAPIView):
    """List all genres"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(summary="List all movie genres")
    def get(self, request, *args, **kwargs):
        # Ensure genres are fetched from TMDb
        tmdb_service = TMDbService()
        tmdb_service.fetch_genres()
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="Get trending movies",
    parameters=[
        OpenApiParameter('time_window', OpenApiTypes.STR, description='Time window: day or week'),
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number')
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def trending_movies(request):
    """Get trending movies from TMDb"""
    time_window = request.GET.get('time_window', 'day')
    page = int(request.GET.get('page', 1))
    
    if time_window not in ['day', 'week']:
        return Response(
            {'error': 'time_window must be "day" or "week"'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    tmdb_service = TMDbService()
    movies, total_pages = tmdb_service.fetch_trending_movies(time_window, page)
    
    serializer = MovieListSerializer(movies, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'page': page,
        'total_pages': total_pages,
        'count': len(movies)
    })


@extend_schema(
    summary="Get popular movies",
    parameters=[
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number')
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def popular_movies(request):
    """Get popular movies from TMDb"""
    page = int(request.GET.get('page', 1))
    
    tmdb_service = TMDbService()
    movies, total_pages = tmdb_service.fetch_popular_movies(page)
    
    serializer = MovieListSerializer(movies, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'page': page,
        'total_pages': total_pages,
        'count': len(movies)
    })


@extend_schema(
    summary="Search movies",
    parameters=[
        OpenApiParameter('q', OpenApiTypes.STR, description='Search query', required=True),
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number')
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_movies(request):
    """Search movies by title"""
    query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))
    
    if not query:
        return Response(
            {'error': 'Search query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    tmdb_service = TMDbService()
    movies, total_pages = tmdb_service.search_movies(query, page)
    
    serializer = MovieListSerializer(movies, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'page': page,
        'total_pages': total_pages,
        'count': len(movies),
        'query': query
    })


@extend_schema(
    summary="Get movies by genre",
    parameters=[
        OpenApiParameter('genre', OpenApiTypes.STR, description='Genre name', required=True),
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number')
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def movies_by_genre(request):
    """Get movies filtered by genre"""
    genre_name = request.GET.get('genre', '').strip()
    page = int(request.GET.get('page', 1))
    
    if not genre_name:
        return Response(
            {'error': 'Genre parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    tmdb_service = TMDbService()
    movies, total_pages = tmdb_service.get_movies_by_genre(genre_name, page)
    
    if not movies and total_pages == 0:
        return Response(
            {'error': f'Genre "{genre_name}" not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = MovieListSerializer(movies, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'page': page,
        'total_pages': total_pages,
        'count': len(movies),
        'genre': genre_name
    })


class MovieDetailView(generics.RetrieveAPIView):
    """Get detailed movie information"""
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]
    lookup_field = 'tmdb_id'
    
    @extend_schema(summary="Get movie details by TMDb ID")
    def get(self, request, *args, **kwargs):
        tmdb_id = kwargs.get('tmdb_id')
        
        # Try to get from database first
        try:
            movie = Movie.objects.get(tmdb_id=tmdb_id)
        except Movie.DoesNotExist:
            # Fetch from TMDb API
            tmdb_service = TMDbService()
            movie = tmdb_service.fetch_movie_details(tmdb_id)
            
            if not movie:
                return Response(
                    {'error': 'Movie not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = MovieSerializer(movie, context={'request': request})
        return Response(serializer.data)


class UserFavoriteListView(generics.ListCreateAPIView):
    """List user favorites and add new favorite"""
    serializer_class = UserFavoriteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user)
    
    @extend_schema(summary="List user's favorite movies")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(summary="Add movie to favorites")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserFavoriteDetailView(generics.DestroyAPIView):
    """Remove movie from favorites"""
    serializer_class = UserFavoriteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user)
    
    @extend_schema(summary="Remove movie from favorites")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(summary="Get current user profile")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user's profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
