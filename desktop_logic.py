"""Input parsing shared by the desktop application and unit tests."""

import re
from urllib.parse import urlparse

from follow_artists import validate_playlist_id


CLIENT_ID_PATTERN = re.compile(r"[A-Za-z0-9]{16,64}")


def validate_client_id(value):
    """Validate a Spotify Client ID without assuming one exact future length."""
    client_id = value.strip()
    if not CLIENT_ID_PATTERN.fullmatch(client_id):
        raise ValueError(
            "Client ID must contain 16 to 64 letters or numbers. "
            "Copy it from your Spotify Developer app settings."
        )
    return client_id


def parse_playlist_input(value):
    """Accept either a Spotify playlist ID or an open.spotify.com URL."""
    candidate = value.strip()
    if not candidate:
        raise ValueError("Enter a Spotify playlist link or playlist ID.")
    if re.fullmatch(r"[0-9A-Za-z]{22}", candidate):
        return candidate

    parsed = urlparse(candidate)
    if parsed.scheme in {"http", "https"} and parsed.netloc.lower() in {
        "open.spotify.com",
        "www.open.spotify.com",
    }:
        parts = [part for part in parsed.path.split("/") if part]
        try:
            playlist_index = parts.index("playlist")
            playlist_id = parts[playlist_index + 1]
        except (ValueError, IndexError):
            playlist_id = ""
        if playlist_id:
            return validate_playlist_id(playlist_id)

    raise ValueError(
        "Use a 22-character Spotify playlist ID or a complete "
        "https://open.spotify.com/playlist/... link."
    )
