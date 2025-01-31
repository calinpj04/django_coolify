import os
import time
import json
import logging
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from django.core.cache import cache

logger = logging.getLogger(__name__)

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
def get_top_artists_and_songs_by_genre(request, genre):
    try:
        # Step 1: Get the access token from session
        access_token = request.session.get('access_token')
        logger.info(f"Access token retrieved from session: {access_token}")
        
        if not access_token:
            logger.error('Access token not found in session.')
            return JsonResponse({'error': 'Access token not found'}, status=400)

        # Step 2: Initialize Spotify client with the access token
        sp = Spotify(auth=access_token)
        
        # Step 3: Make the request to get top artists by genre
        try:
            top_artists = sp.search(q=f'genre:{genre}', type='artist', limit=10)
            if not top_artists['artists']['items']:
                logger.warning(f'No top artists found for genre: {genre}')
                return JsonResponse({'error': f'No top artists found for genre: {genre}'}, status=404)

            logger.info(f'Top artists found for genre: {genre}')
            return JsonResponse({'top_artists': top_artists['artists']['items']})

        except SpotifyException as e:
            logger.error(f'Spotify API error: {e}')
            return JsonResponse({'error': 'Failed to retrieve data from Spotify'}, status=500)

    except Exception as e:
        logger.error(f"Error in get_top_artists_and_songs_by_genre: {e}")
        return JsonResponse({'error': 'An error occurred while fetching the data'}, status=500)

    
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
        print("EXCEPTION", e)
        handle_rate_limit()
        return JsonResponse({'error': str(e)}, status=500)

def spotify_callback(request):
    try:
        # Step 1: Get the code from the callback URL
        code = request.GET.get('code')
        if not code:
            logger.error('No code received in the callback request.')
            return JsonResponse({'error': 'No code received'}, status=400)

        # Step 2: Get the access token using the code
        token_info = sp_oauth.get_access_token(code)
        if not token_info or 'access_token' not in token_info:
            logger.error(f'Failed to obtain access token: {token_info}')
            return JsonResponse({'error': 'Failed to obtain access token'}, status=500)
        
        access_token = token_info['access_token']
        
        # Step 3: Store the access token in the session
        request.session['access_token'] = access_token
        logger.info(f'Access token obtained and stored in session: {access_token}')
        
        # Check session contents
        logger.info(f"Session contents: {request.session.items()}")

        # Step 4: Redirect to the 'top-artists-by-genre' view with the pop genre
        return redirect('top-artists-by-genre', genre='pop')

    except Exception as e:
        logger.error(f"Error in spotify_callback: {e}")
        return JsonResponse({'error': 'An error occurred during callback handling'}, status=500)
