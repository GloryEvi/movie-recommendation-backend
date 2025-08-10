from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, Genre, UserFavorite


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model"""
    
    class Meta:
        model = Genre
        fields = ['id', 'name', 'tmdb_id']


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie model"""
    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.ReadOnlyField()
    backdrop_url = serializers.ReadOnlyField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'title', 'overview', 'release_date',
            'vote_average', 'popularity', 'poster_path', 'backdrop_path',
            'poster_url', 'backdrop_url', 'genres', 'is_favorited',
            'created_at', 'updated_at'
        ]
    
    def get_is_favorited(self, obj):
        """Check if movie is favorited by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFavorite.objects.filter(
                user=request.user, movie=obj
            ).exists()
        return False


class MovieListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for movie lists"""
    genres = serializers.StringRelatedField(many=True, read_only=True)
    poster_url = serializers.ReadOnlyField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'title', 'release_date', 'vote_average',
            'popularity', 'poster_url', 'genres', 'is_favorited'
        ]
    
    def get_is_favorited(self, obj):
        """Check if movie is favorited by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFavorite.objects.filter(
                user=request.user, movie=obj
            ).exists()
        return False


class UserFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for UserFavorite model"""
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserFavorite
        fields = ['id', 'movie', 'movie_id', 'created_at']
    
    def validate_movie_id(self, value):
        """Validate that movie exists"""
        try:
            Movie.objects.get(id=value)
            return value
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie does not exist.")
    
    def create(self, validated_data):
        """Create favorite, handling duplicates"""
        movie_id = validated_data.pop('movie_id')
        movie = Movie.objects.get(id=movie_id)
        user = self.context['request'].user
        
        favorite, created = UserFavorite.objects.get_or_create(
            user=user,
            movie=movie
        )
        
        if not created:
            raise serializers.ValidationError("Movie is already in favorites.")
        
        return favorite


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    favorites_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'favorites_count']
    
    def get_favorites_count(self, obj):
        """Get user's total favorites count"""
        return obj.favorites.count()