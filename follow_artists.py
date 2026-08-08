#!/usr/bin/env python3
"""Follow missing Spotify artists found in a playlist."""

import json
import os
import re
import sys
import time

import requests
import spotipy
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError


SCOPE = "playlist-read-private user-follow-read user-follow-modify"
DEFAULT_REDIRECT_URI = "http://127.0.0.1:8888/callback"
PLAYLIST_ID_PATTERN = re.compile(r"[0-9A-Za-z]{22}")
SPOTIFY_ID_PATTERN = re.compile(r"[0-9A-Za-z]{22}")
PLAYLIST_PAGE_SIZE = 50
LIBRARY_BATCH_SIZE = 40
EMBED_TIMEOUT_SECONDS = 30
DEFAULT_EMBED_REQUEST_DELAY_SECONDS = 0.35


def env_flag(name, default=False):
    """Parse a boolean environment variable."""
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be true or false, got {value!r}")


def env_nonnegative_float(name, default):
    """Parse a non-negative floating-point environment variable."""
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    parsed = float(value)
    if parsed < 0:
        raise ValueError(f"{name} must not be negative")
    return parsed


def require_env(name):
    """Return a required environment variable or stop with setup guidance."""
    value = os.getenv(name, "").strip()
    if not value:
        sys.exit(
            f"Missing environment variable: {name}. "
            "See the README setup instructions."
        )
    return value


def validate_playlist_id(value, name="SOURCE_PLAYLIST_ID"):
    """Validate and return a Spotify playlist ID."""
    playlist_id = value.strip()
    if not PLAYLIST_ID_PATTERN.fullmatch(playlist_id):
        raise ValueError(
            f"{name} must be a 22-character Spotify playlist ID, "
            "not a complete URL"
        )
    return playlist_id


def create_client():
    """Create a Spotify client backed by a refresh token and memory cache."""
    refresh_token = require_env("SPOTIPY_REFRESH_TOKEN")
    auth_manager = SpotifyOAuth(
        client_id=require_env("SPOTIPY_CLIENT_ID"),
        client_secret=require_env("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI") or DEFAULT_REDIRECT_URI,
        scope=SCOPE,
        open_browser=False,
        cache_handler=MemoryCacheHandler(
            token_info={
                "access_token": "",
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_at": 0,
                "scope": SCOPE,
            }
        ),
    )

    try:
        auth_manager.refresh_access_token(refresh_token)
    except SpotifyOauthError as exc:
        sys.exit(
            f"Spotify authentication failed: {exc}\n"
            "Check the client ID, client secret, refresh token, and redirect URI."
        )

    return spotipy.Spotify(
        auth_manager=auth_manager,
        requests_timeout=30,
        retries=0,
        status_retries=0,
    )


def api_error_message(action, exc):
    """Return an actionable message for a Spotify API error."""
    status = getattr(exc, "http_status", "?")
    headers = getattr(exc, "headers", None) or {}
    retry_after = headers.get("Retry-After") or headers.get("retry-after")

    if status == 429:
        wait = f" Retry-After: {retry_after} seconds." if retry_after else ""
        return (
            f"{action}: Spotify quota/rate limit reached (HTTP 429).{wait}\n"
            "Wait until the limit resets before starting another run."
        )
    if status == 403:
        return (
            f"{action}: Spotify denied access (HTTP 403).\n"
            "In Development Mode, the source playlist must be owned by the "
            "authenticated user or shared with them as a collaborator. Also "
            "verify the token scopes."
        )
    if status == 401:
        return (
            f"{action}: Spotify rejected the credentials (HTTP 401).\n"
            "Generate a new refresh token with the current Spotify app."
        )
    return f"{action} failed (HTTP {status}): {exc}"


def stop_for_api_error(action, exc):
    """Stop with an actionable message for a Spotify API error."""
    sys.exit(api_error_message(action, exc))


def _artist_from_object(artist):
    """Return a validated (artist ID, label) tuple or None."""
    artist_id = artist.get("id")
    if not artist_id or not SPOTIFY_ID_PATTERN.fullmatch(artist_id):
        return None
    return artist_id, artist.get("name") or artist_id


def playlist_artists(client, playlist_id):
    """Read every unique artist from all pages of an owned playlist."""
    artists = []
    seen = set()
    page = client.playlist_items(
        playlist_id,
        fields=(
            "items(item(id,type,artists(id,name)),"
            "track(id,type,artists(id,name))),next"
        ),
        limit=PLAYLIST_PAGE_SIZE,
        additional_types=("track",),
    )

    while page:
        for entry in page.get("items", []):
            track = entry.get("item") or entry.get("track")
            if not track or track.get("type") != "track":
                continue
            for raw_artist in track.get("artists") or []:
                artist = _artist_from_object(raw_artist)
                if artist and artist[0] not in seen:
                    seen.add(artist[0])
                    artists.append(artist)
        page = client.next(page) if page.get("next") else None

    return artists


def embed_playlist_track_ids(playlist_id, session=requests):
    """Read ordered track IDs from Spotify's undocumented public embed JSON."""
    url = f"https://open.spotify.com/embed/playlist/{playlist_id}"
    response = session.get(
        url,
        timeout=EMBED_TIMEOUT_SECONDS,
        headers={"User-Agent": "spotify-artist-auto-follow/2.0"},
    )
    response.raise_for_status()

    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        response.text,
        re.DOTALL,
    )
    if not match:
        raise ValueError("Spotify embed does not contain __NEXT_DATA__")

    data = json.loads(match.group(1))
    track_ids = []

    def collect(value):
        if isinstance(value, str) and value.startswith("spotify:track:"):
            track_id = value.removeprefix("spotify:track:")
            if SPOTIFY_ID_PATTERN.fullmatch(track_id):
                track_ids.append(track_id)
        elif isinstance(value, dict):
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(data)
    unique_ids = list(dict.fromkeys(track_ids))
    if not unique_ids:
        raise ValueError("Spotify embed does not contain track IDs")
    return unique_ids


def artists_from_track_ids(
    client,
    track_ids,
    request_delay_seconds=0,
    progress=None,
):
    """Resolve artist IDs using one catalog request per embed track."""
    artists = []
    seen = set()
    for index, track_id in enumerate(track_ids):
        track = client.track(track_id)
        for raw_artist in track.get("artists") or []:
            artist = _artist_from_object(raw_artist)
            if artist and artist[0] not in seen:
                seen.add(artist[0])
                artists.append(artist)
        if progress:
            progress(index + 1, len(track_ids))
        if request_delay_seconds and index + 1 < len(track_ids):
            time.sleep(request_delay_seconds)
    return artists


def read_source_artists(
    client,
    playlist_id,
    allow_embed_fallback=False,
    request_delay_seconds=DEFAULT_EMBED_REQUEST_DELAY_SECONDS,
    logger=print,
    fallback_progress=None,
):
    """Read artists through the API, optionally falling back to the embed."""
    try:
        return playlist_artists(client, playlist_id)
    except SpotifyException as exc:
        status = getattr(exc, "http_status", None)
        if status not in {403, 404} or not allow_embed_fallback:
            raise

    logger(
        "Source playlist is unavailable through the Web API; trying the "
        "optional public embed fallback."
    )
    logger(
        "Warning: resolving embed tracks requires one Spotify API request per "
        "track and can consume Development Mode quota."
    )
    track_ids = embed_playlist_track_ids(playlist_id)
    return artists_from_track_ids(
        client,
        track_ids,
        request_delay_seconds=request_delay_seconds,
        progress=fallback_progress,
    )


def batch(values, size=LIBRARY_BATCH_SIZE):
    """Yield API-sized list chunks."""
    for start in range(0, len(values), size):
        yield values[start:start + size]


def unfollowed_artists(client, artists, progress=None):
    """Return only artists the current user does not already follow."""
    missing = []
    checked = 0
    for artist_batch in batch(artists):
        uris = [f"spotify:artist:{artist_id}" for artist_id, _ in artist_batch]
        statuses = client.current_user_saved_items(uris)
        if len(statuses) != len(artist_batch):
            raise ValueError("Spotify returned an unexpected follow-status response")
        missing.extend(
            artist
            for artist, is_followed in zip(artist_batch, statuses)
            if not is_followed
        )
        checked += len(artist_batch)
        if progress:
            progress(checked, len(artists))
    return missing


def follow_artists(client, artists, progress=None):
    """Follow artists in batches accepted by the current library endpoint."""
    followed = 0
    for artist_batch in batch(artists):
        client.user_follow_artists(
            [artist_id for artist_id, _ in artist_batch]
        )
        followed += len(artist_batch)
        if progress:
            progress(followed, len(artists))


def main():
    try:
        playlist_id = validate_playlist_id(require_env("SOURCE_PLAYLIST_ID"))
        dry_run = env_flag("DRY_RUN", default=False)
        allow_embed_fallback = env_flag(
            "ALLOW_EMBED_FALLBACK",
            default=False,
        )
        request_delay = env_nonnegative_float(
            "EMBED_REQUEST_DELAY_SECONDS",
            DEFAULT_EMBED_REQUEST_DELAY_SECONDS,
        )
    except ValueError as exc:
        sys.exit(f"Configuration error: {exc}")

    print(f"Source playlist: {playlist_id}")
    print(f"Dry run: {dry_run}")
    print(f"Embed fallback: {allow_embed_fallback}")
    client = create_client()

    try:
        artists = read_source_artists(
            client,
            playlist_id,
            allow_embed_fallback=allow_embed_fallback,
            request_delay_seconds=request_delay,
        )
        missing = unfollowed_artists(client, artists)
    except SpotifyException as exc:
        stop_for_api_error("Could not inspect playlist artists", exc)
    except (requests.RequestException, json.JSONDecodeError, ValueError) as exc:
        sys.exit(f"Could not inspect playlist artists: {exc}")

    print(f"Unique artists in source: {len(artists)}")
    print(f"Already followed: {len(artists) - len(missing)}")
    print(f"New artists: {len(missing)}")

    if not missing:
        print("Nothing to do; every source artist is already followed.")
        return

    print("Preview of artists to follow:")
    for artist_id, name in missing[:20]:
        print(f"  - {name}: https://open.spotify.com/artist/{artist_id}")
    if len(missing) > 20:
        print(f"  ... and {len(missing) - 20} more")

    if dry_run:
        print("Dry run enabled; no artists were followed.")
        return

    try:
        follow_artists(client, missing)
    except SpotifyException as exc:
        stop_for_api_error("Could not follow artists", exc)

    print(f"Successfully followed {len(missing)} new artists.")


if __name__ == "__main__":
    main()
