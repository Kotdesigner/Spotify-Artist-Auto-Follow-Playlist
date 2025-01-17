# Spotify-Artist-Auto-Follow-Playlist
Python-based tool that automates the process of following artists featured in a specific Spotify playlist.
----------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------
Auto-Follow Spotify Artists by KOTDESIGNER

Auto-Follow Spotify Artists is a Python-based tool developed by BEBØRG, designed to simplify and automate the process of following all artists featured in your Spotify playlists. By following these artists, your Release Radar playlist will stay updated with their latest releases—ensuring you never miss out on new music from your favorites.
Key Features

    Automated Artist Following
    Automatically follow all artists from any Spotify playlist. No manual interaction required!

    Playlist Integration
    Supports playlists of any size and allows you to process multiple playlists to keep your library fresh.

    Release Radar Optimization
    Ensures your Release Radar stays relevant by featuring updates from the artists you enjoy.

    Efficient Batch Processing
    Handles large playlists with Spotify API-compliant batching for smooth execution.

    User-Friendly
    Designed for all levels of experience. Windows and Mac users can use this tool effortlessly via GUI or as an executable file.

Why Use This Tool?

Spotify's Release Radar only features music from artists you follow. By automating the process of following all artists in your playlists, this tool ensures your music library stays fresh, relevant, and reflective of your current taste. It saves time and guarantees you’re always updated with new releases from the artists you love.
How It Works

    The tool retrieves all tracks from the specified Spotify playlist.
    It extracts unique artist IDs from those tracks.
    Automatically sends follow requests for all identified artists to Spotify.

How to Use
Windows Users

    Download the spotify_auto_follow__byKOTDESIGNER.exe file.
    Double-click to launch the program.
    Enter your Spotify credentials (Client ID and Client Secret) and your Playlist ID.
    Click "Follow Artists," and the tool will handle the rest—no coding knowledge required!

Mac Users

For macOS, use the .py script with the following steps:

    Ensure Python 3 is installed. If not, download it from python.org.
    Open Terminal and navigate to the folder containing the script:

    cd /path/to/your/folder
    Run the script:
    python3 spotify_auto_follow__byKOTDESIGNER.py
    
    The graphical interface will appear, allowing you to enter your Spotify credentials and Playlist ID to start the process.

Auto-Follow Spotify Artists by KOTDESIGNER

Auto-Follow Spotify Artists is a Python-based tool developed by BEBØRG, designed to simplify and automate the process of following all artists featured in your Spotify playlists. By following these artists, your Release Radar playlist will stay updated with their latest releases—ensuring you never miss out on new music from your favorites.
Key Features

    Automated Artist Following
    Automatically follow all artists from any Spotify playlist. No manual interaction required!

    Playlist Integration
    Supports playlists of any size and allows you to process multiple playlists to keep your library fresh.

    Release Radar Optimization
    Ensures your Release Radar stays relevant by featuring updates from the artists you enjoy.

    Efficient Batch Processing
    Handles large playlists with Spotify API-compliant batching for smooth execution.

    User-Friendly
    Designed for all levels of experience. Windows and Mac users can use this tool effortlessly via GUI or as an executable file.

Why Use This Tool?

Spotify's Release Radar only features music from artists you follow. By automating the process of following all artists in your playlists, this tool ensures your music library stays fresh, relevant, and reflective of your current taste. It saves time and guarantees you’re always updated with new releases from the artists you love.
How It Works

    The tool retrieves all tracks from the specified Spotify playlist.
    It extracts unique artist IDs from those tracks.
    Automatically sends follow requests for all identified artists to Spotify.

How to Use
Windows Users

    Download the spotify_auto_follow__byKOTDESIGNER.exe file.
    Double-click to launch the program.
    Enter your Spotify credentials (Client ID and Client Secret) and your Playlist ID.
    Click "Follow Artists," and the tool will handle the rest—no coding knowledge required!

Mac Users

For macOS, use the .py script with the following steps:

    Ensure Python 3 is installed. If not, download it from python.org.
    Open Terminal and navigate to the folder containing the script:

cd /path/to/your/folder

Run the script:

    python3 spotify_auto_follow__byKOTDESIGNER.py

    The graphical interface will appear, allowing you to enter your Spotify credentials and Playlist ID to start the process.

For Tech Enthusiasts ;)

If you want to explore or customize the Python script directly:

    Setup Spotify Developer Account:
        Visit Spotify Developer Dashboard.
        Log in and create a new app:
            Name: Follow-Spotify-Playlist
            Redirect URI: http://localhost:8888/callback
        Save the app and copy your Client ID and Client Secret.
    Install Dependencies:
        Ensure Python 3 is installed.
        Install Spotipy:

    pip install spotipy

Edit the Script:

    Update the placeholders for Client ID, Client Secret, and Redirect URI:

    CLIENT_ID = 'YOUR-USER-ID'
    CLIENT_SECRET = 'YOUR-SECRET-ID'
    REDIRECT_URI = 'http://localhost:8888/callback'
    Replace the placeholder playlist ID:
    playlist_id = 'YOUR-PLAYLIST-ID'

Run the Script:

    python spotify_auto_follow__byKOTDESIGNER.py

How to Get Required Credentials
Client ID and Client Secret

    Visit the Spotify Developer Dashboard.
    Log in with your Spotify account.
    Create a new app or select an existing one.
    Copy the Client ID displayed.
    Click Show Client Secret to copy your secret key.

Playlist ID

    Open Spotify and navigate to the desired playlist.
    Click on the "..." menu → Share → Copy Link to Playlist.
    Paste the link and extract the part after /playlist/ and before ?:
        Example: https://open.spotify.com/playlist/7ccGpjk1kgoaZxtklvUEIS?si=xyz
        Playlist ID: 7ccGpjk1kgoaZxtklvUEIS.

Requirements

    A Spotify Developer account for API credentials.
    Python (for tech enthusiasts or Mac users).
    Spotipy library (pip install spotipy).

With spotify_auto_follow__byKOTDESIGNER, staying updated with your favorite artists has never been easier. Whether you're a music enthusiast or a tech-savvy developer, this tool caters to all—ensuring your Spotify experience is always in tune with your preferences. 🎶
