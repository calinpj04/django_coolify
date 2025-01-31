from django.urls import path
from .views import get_top_artists_and_songs_by_genre, get_track_data, spotify_callback

urlpatterns = [
    path('top-artists/<str:genre>/', get_top_artists_and_songs_by_genre, name='top-artists-by-genre'),
    path('track/<str:track_id>/', get_track_data, name='get-track-data'),
    path('callback/', spotify_callback, name='spotify-callback'),
]
