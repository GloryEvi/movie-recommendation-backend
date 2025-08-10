from django.contrib import admin

from django.contrib import admin
from .models import Movie, Genre, MovieGenre, UserFavorite


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'tmdb_id', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


class MovieGenreInline(admin.TabularInline):
    model = MovieGenre
    extra = 0


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'vote_average', 'popularity', 'created_at']
    list_filter = ['release_date', 'vote_average', 'genres']
    search_fields = ['title', 'overview']
    readonly_fields = ['tmdb_id', 'poster_url', 'backdrop_url', 'created_at', 'updated_at']
    inlines = [MovieGenreInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'tmdb_id', 'overview', 'release_date')
        }),
        ('Ratings & Popularity', {
            'fields': ('vote_average', 'popularity')
        }),
        ('Images', {
            'fields': ('poster_path', 'backdrop_path', 'poster_url', 'backdrop_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'movie__title']
    readonly_fields = ['created_at']