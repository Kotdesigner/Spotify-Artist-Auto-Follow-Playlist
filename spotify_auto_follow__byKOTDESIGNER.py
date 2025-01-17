import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from tkinter import messagebox


# -----------------------------------------------------
# Project: Auto-Follow Spotify Artists from Playlist
# Author: KOTDESIGNER (by STV NMK)
# Developed by: BEBØRG
# GitHub: https://github.com/Kotdesigner
# Email: kotdesigner@outlook.com
# Purpose: Automate following of artists from a Spotify playlist
# Created: January 2025, Kiel
# Open-Source Code for public use
# -----------------------------------------------------

def follow_artists_from_playlist(client_id, client_secret, playlist_id):
    """
    Function to automatically follow all artists from a playlist.
    """
    try:
        # Initialize Spotify client
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri='http://localhost:8888/callback',
            scope="user-follow-modify playlist-read-private"
        ))

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
        
        total_followed = len(artist_ids)
        messagebox.showinfo("Success", f"Successfully followed {total_followed} artists!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Helper functions for info buttons
def show_client_id_info():
    info = (
        "To get your Spotify Client ID:\n"
        "1. Go to the Spotify Developer Dashboard: https://developer.spotify.com/dashboard/applications\n"
        "2. Log in with your Spotify account.\n"
        "3. Click 'Create an App' or select an existing app.\n"
        "4. Copy the Client ID displayed on the application page."
    )
    messagebox.showinfo("Client ID Information", info)

def show_client_secret_info():
    info = (
        "To get your Spotify Client Secret:\n"
        "1. Go to the Spotify Developer Dashboard: https://developer.spotify.com/dashboard/applications\n"
        "2. Log in with your Spotify account.\n"
        "3. Click 'Create an App' or select an existing app.\n"
        "4. Click 'Show Client Secret' to view and copy your secret key."
    )
    messagebox.showinfo("Client Secret Information", info)

def show_playlist_id_info():
    info = (
        "To get your Spotify Playlist ID:\n"
        "1. Open Spotify and navigate to your playlist.\n"
        "2. Click the '...' menu and select 'Share > Copy link to playlist'.\n"
        "3. The link will look like this:\n"
        "   https://open.spotify.com/playlist/7ccGpjk1kgoaZxtklvUEIS?si=432d8f2b24b14865\n"
        "4. Extract the part after '/playlist/' and before '?' (e.g., 7ccGpjk1kgoaZxtklvUEIS).\n"
        "5. Use this as the Playlist ID."
    )
    messagebox.showinfo("Playlist ID Information", info)


# GUI Setup
def create_gui():
    def on_submit():
        client_id = client_id_entry.get().strip()
        client_secret = client_secret_entry.get().strip()
        playlist_id = playlist_entry.get().strip()

        if not client_id or not client_secret:
            messagebox.showwarning("Input Required", "Please enter your Client ID and Client Secret.")
            return
        if not playlist_id:
            messagebox.showwarning("Input Required", "Please enter a valid Playlist ID.")
            return

        follow_artists_from_playlist(client_id, client_secret, playlist_id)

    # Create the main window
    root = tk.Tk()
    root.title("Spotify Auto-Follow")
    root.geometry("600x450")
    root.configure(bg="#f5f5f5")

    # Add widgets for Client ID and Client Secret
    title_label = tk.Label(root, text="Spotify Auto-Follow Tool", font=("Helvetica", 18, "bold"), bg="#f5f5f5", fg="#333")
    title_label.pack(pady=15)

    subtitle_label = tk.Label(root, text="Developed by BEBØRG", font=("Helvetica", 12, "italic"), bg="#f5f5f5", fg="#555")
    subtitle_label.pack(pady=5)

    instructions_label = tk.Label(root, text="Enter your Spotify API credentials and Playlist ID to follow artists.", font=("Helvetica", 10), bg="#f5f5f5", fg="#555")
    instructions_label.pack(pady=5)

    # Client ID
    client_id_label = tk.Label(root, text="Spotify Client ID:", font=("Helvetica", 12), bg="#f5f5f5", fg="#333")
    client_id_label.pack(pady=5)
    client_id_frame = tk.Frame(root, bg="#f5f5f5")
    client_id_frame.pack(pady=5)
    client_id_entry = tk.Entry(client_id_frame, width=40, font=("Helvetica", 10))
    client_id_entry.pack(side="left", padx=5)
    client_id_info_button = tk.Button(client_id_frame, text="?", command=show_client_id_info, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", width=2, relief="flat")
    client_id_info_button.pack(side="left")

    # Client Secret
    client_secret_label = tk.Label(root, text="Spotify Client Secret:", font=("Helvetica", 12), bg="#f5f5f5", fg="#333")
    client_secret_label.pack(pady=5)
    client_secret_frame = tk.Frame(root, bg="#f5f5f5")
    client_secret_frame.pack(pady=5)
    client_secret_entry = tk.Entry(client_secret_frame, width=40, font=("Helvetica", 10), show="*")
    client_secret_entry.pack(side="left", padx=5)
    client_secret_info_button = tk.Button(client_secret_frame, text="?", command=show_client_secret_info, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", width=2, relief="flat")
    client_secret_info_button.pack(side="left")

    # Playlist ID
    playlist_label = tk.Label(root, text="Spotify Playlist ID:", font=("Helvetica", 12), bg="#f5f5f5", fg="#333")
    playlist_label.pack(pady=5)
    playlist_frame = tk.Frame(root, bg="#f5f5f5")
    playlist_frame.pack(pady=5)
    playlist_entry = tk.Entry(playlist_frame, width=40, font=("Helvetica", 10))
    playlist_entry.pack(side="left", padx=5)
    playlist_info_button = tk.Button(playlist_frame, text="?", command=show_playlist_id_info, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", width=2, relief="flat")
    playlist_info_button.pack(side="left")

    # Submit Button
    submit_button = tk.Button(root, text="Follow Artists", command=on_submit, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", padx=10, pady=5, relief="flat")
    submit_button.pack(pady=15)

    # Footer
    footer_frame = tk.Frame(root, bg="#f5f5f5")
    footer_frame.pack(side="bottom", fill="x", pady=10)
    footer_label = tk.Label(
        footer_frame,
        text="Developed by BEBØRG | Author: KOTDESIGNER (by STV NMK)\nGitHub: Kotdesigner | Email: kotdesigner@outlook.com",
        font=("Helvetica", 9),
        bg="#f5f5f5",
        fg="#888"
    )
    footer_label.pack()

    # Run the GUI loop
    root.mainloop()


# Run the GUI
if __name__ == "__main__":
    create_gui()
