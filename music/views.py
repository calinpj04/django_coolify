import os
import time
import json
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from django.core.cache import cache

# Replace with your own Spotify credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

# Authenticate and connect to Spotify API
sp_oauth = SpotifyOAuth(client_id='a2c3e831b9ab494999df8a96f4eda87c', client_secret='6d1aad7eeef4453e8f7695de2a433be5', redirect_uri='http://igs4ssw80gs0os0wo8o0k40g.webdev.envisionment.net/callback/', scope='user-top-read')

# Function to handle rate limits
def handle_rate_limit():
    while True:
        try:
            # Check the rate limit status from the Spotify API
            response = sp_oauth._get('https://api.spotify.com/v1/me/top/artists')  # Simple request to check the rate limit.
            return
        except SpotifyException as e:
            if e.http_status == 429:  # 429 is Too Many Requests
                reset_time = int(e.headers.get('Retry-After', 60))  # Retry-After is the time to wait in seconds
                print(f"Rate limit hit, retrying after {reset_time} seconds...")
                time.sleep(reset_time)
            else:
                raise e

# Function to fetch all songs by a given artist
def get_all_songs_by_artist(artist_id, sp):
    all_songs = []
    results = sp.artist_albums(artist_id, album_type='album', limit=50)

    while results:
        for album in results['items']:
            album_tracks = sp.album_tracks(album['id'])
            for track in album_tracks['items']:
                track_info = {
                    'name': track['name'],
                    'image': album['images'][0]['url'],
                    'stream_count': track['popularity'],
                }
                all_songs.append(track_info)

        if results['next']:
            results = sp.next(results)
        else:
            break

    return all_songs

# Function to fetch top artists and their songs by genre
def get_top_artists_and_songs_by_genre(request, genre, limit=50):
    # Get the access token
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return HttpResponseRedirect(auth_url)

    sp = Spotify(auth=token_info['access_token'])
    all_artist_songs = []

    # Check if the data is cached
    cached_data = cache.get(f'{genre}_top_songs')
    if cached_data:
        return JsonResponse(cached_data, safe=False)

    try:
        results = sp.search(q=f'genre:{genre}', type='artist', limit=limit)
        for artist in results['artists']['items']:
            artist_songs = get_all_songs_by_artist(artist['id'], sp)
            all_artist_songs.append({
                'artist': artist['name'],
                'songs': artist_songs
            })

        # Cache the data for 1 hour
        cache.set(f'{genre}_top_songs', all_artist_songs, timeout=3600)

    except SpotifyException as e:
        handle_rate_limit()
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse(all_artist_songs, safe=False)

def get_track_data(request, track_id):
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return HttpResponseRedirect(auth_url)

    sp = Spotify(auth=token_info['access_token'])
    try:
        track = sp.track(track_id)
        track_data = {
            'name': track['name'],
            'album': track['album']['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'release_date': track['album']['release_date'],
            'popularity': track['popularity'],
            'preview_url': track['preview_url'],
            'external_url': track['external_urls']['spotify']
        }
        return JsonResponse(track_data)
    except SpotifyException as e:
        handle_rate_limit()
        return JsonResponse({'error': str(e)}, status=500)

def spotify_callback(request):
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)
    return redirect('top-artists-by-genre', genre='pop')
