#### FOR SCRIPties ####

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# -----------------------------------------------------
# Project: Auto-Follow Spotify Artists from Playlist
# Author: KOTDESIGNER (by STV NMK)
# GitHub: https://github.com/Kotdesigner
# Email: kotdesigner@outlook.com
# Purpose: Automate following of artists from a Spotify playlist
# Created: January 2025, Kiel
# Open-Source Code for public use
# -----------------------------------------------------

# Display Author and Project Information
print("===================================")
print("Auto-Follow Spotify Artists")
print("Author: KOTDESIGNER (by STV NMK)")
print("GitHub: https://github.com/Kotdesigner")
print("Email: kotdesigner@outlook.com")
print("Created: January 2025, Kiel, Germany")
print("===================================\n")

# Spotify API Credentials
CLIENT_ID = 'YOUR-ID'  # Replace with your Client ID
CLIENT_SECRET = 'YOUR-SECRET-ID'  # Replace with your Client Secret
REDIRECT_URI = 'http://localhost:8888/callback'  # The Redirect URI you set in the Spotify App

# Authorization with Spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-follow-modify playlist-read-private"
))

def follow_artists_from_playlist(playlist_id):
    """
    Function to automatically follow all artists from a playlist.
    """
    # Fetch the tracks from the playlist
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    
    # Collect the artist IDs
    artist_ids = set()
    for item in tracks:
        track = item['track']
        artists = track['artists']
        for artist in artists:
            if artist['id']:
                artist_ids.add(artist['id'])  # Add only valid IDs
            else:
                print(f"Invalid artist ID found: {artist}")
    
    # Follow the artists in groups of up to 50 IDs (API limitation)
    artist_ids = list(artist_ids)
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        sp.user_follow_artists(batch)
        print(f"Following artists: {batch}")
    
    total_followed = len(artist_ids)
    print(f"Successfully followed {total_followed} artists.")
    
    # Display a celebratory smiley with the number of artists followed
    print("\n" + "=" * 40)
    print("     😊 SUCCESSFULLY COMPLETED 😊")
    print("=" * 40)
    print(f"🎵 Followed {total_followed} new artists! 🎵")
    print("""
           *****     *****
         **     ** **     **
        *         *         *
       *   O             O   *
       *        _______       *
        *      \\_____/      *
         **               **
           **           **
             **       **
               *******
                *****
                 ***
                  *
    """)

# Example: Provide a playlist ID
playlist_id = '7ccGpjk1kgoaZxtklvUEIS'  # Replace with the ID of your specific playlist
#playlist_id = '6yOAH8uxNHFgU0wtAyYi59'  # Replace with the ID of your specific playlist // Process multiple playlists by removing the # symbol. Add as many as needed per line
#playlist_id = '6NIbfXJFBfen5AYcNL2Wu6'  # Replace with the ID of your specific playlist

# Execute the function
follow_artists_from_playlist(playlist_id)
