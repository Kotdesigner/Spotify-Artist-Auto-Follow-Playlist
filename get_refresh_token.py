#!/usr/bin/env python3
"""Create the one-time Spotify refresh token used by GitHub Actions."""

import os
from getpass import getpass

from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth


SCOPE = "playlist-read-private user-follow-read user-follow-modify"
DEFAULT_REDIRECT_URI = "http://127.0.0.1:8888/callback"


def main():
    client_id = os.getenv("SPOTIPY_CLIENT_ID") or input("Client ID: ").strip()
    client_secret = (
        os.getenv("SPOTIPY_CLIENT_SECRET")
        or getpass("Client Secret: ").strip()
    )
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", DEFAULT_REDIRECT_URI)

    if not client_id or not client_secret:
        raise SystemExit("Client ID and Client Secret are required.")

    print(f"\nRedirect URI: {redirect_uri}")
    print("This URI must match the Spotify Developer Dashboard exactly.\n")

    cache = MemoryCacheHandler()
    auth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPE,
        cache_handler=cache,
        open_browser=True,
    )
    auth.get_access_token(
        auth.get_auth_response(),
        as_dict=False,
        check_cache=False,
    )
    token_info = cache.get_cached_token()
    refresh_token = token_info.get("refresh_token") if token_info else None
    if not refresh_token:
        raise SystemExit("Spotify did not return a refresh token.")

    print("\n" + "=" * 70)
    print("SPOTIPY_REFRESH_TOKEN:")
    print(refresh_token)
    print("=" * 70)
    print("\nStore this value as a GitHub Actions repository secret.")
    print("Never commit it or paste it into an issue, screenshot, or log.")


if __name__ == "__main__":
    main()
