# Spotify-Artist-Auto-Follow-Playlist
Python-based tool that automates the process of following artists featured in a specific Spotify playlist.
----------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------
Description

Auto-Follow Spotify Artists is a Python-based automation tool that ensures you never miss a new release by automatically following all the artists featured in your Spotify playlists. Simply provide a playlist ID, and the tool will handle the rest.

This tool automatically follows artists in your playlists, helping you stay updated with their latest releases in your Release Radar.
Key Features

    Automated Artist Following: Automatically follows all artists featured in a given Spotify playlist.
    Playlist Integration: Processes playlists, making it easy to follow artists from your favorite collections.
    Release Radar Optimization: Ensures your Release Radar is updated with music from artists you enjoy.
    Efficient Batch Processing: Handles large playlists by following artists in batches, adhering to Spotify's API limits.
    Easy-to-Use: Simply provide a playlist link and let the tool take care of the rest.

How It Works

    The tool retrieves all tracks from the specified Spotify playlist.
    Extracts unique artist IDs associated with those tracks.
    Automatically sends follow requests for all identified artists.

Installation and Setup

    Spotify Developer Account Setup:
        Visit the Spotify Developer Dashboard and log in with your Spotify account.
        Click "Create an App":
            Name: Follow-Spotify-Playlist
            Redirect URI: http://localhost:8888/callback       || Leave this adress!
        Save the app.
        Copy the Client ID and Client Secret (click Show Secret Key) for later use.

Install Python and Dependencies:
        Ensure you have Python installed on your system.
        Install the required library spotipy:
        pip install spotipy

Download the Python Script:

    Copy the provided script into a new file, e.g., Spotify-Auto_Follow_Playlist_by-kotdesigner.py.

Edit the Script:

    Replace the placeholders with your Spotify API credentials which u got from your spotify developer homepage:

    CLIENT_ID = 'YOUR-USER-ID'  # Replace with your Spotify Client ID
    CLIENT_SECRET = 'YOUR-SECRET-ID'  # Replace with your Spotify Client Secret
    REDIRECT_URI = 'http://localhost:8888/callback'  # Use the Redirect URI from your Spotify app

Specify the playlist ID:

    Find your playlist link (right-click on the playlist → Share → Copy Link).
    Extract the playlist ID (the part after /playlist/ and before ?):

    Example: https://open.spotify.com/playlist/7ccGpjk1kgoaZxtklvUEIS?si=432d8f2b24b14865
    Playlist ID: 7ccGpjk1kgoaZxtklvUEIS

Update the playlist ID in the script:

        playlist_id = '7ccGpjk1kgoaZxtklvUEIS'  # Replace with your playlist ID '.....................'

Run the Script:

    Open your terminal or command prompt.
    Run the script:

        python Spotify-Auto_Follow_Playlist_by-kotdesigner.py

