"""PKCE authentication and operating-system keychain storage for the GUI."""

import hashlib
import json
import secrets

import keyring
import spotipy
from keyring.errors import KeyringError, PasswordDeleteError
from spotipy.cache_handler import CacheHandler
from spotipy.oauth2 import SpotifyPKCE

from follow_artists import DEFAULT_REDIRECT_URI, SCOPE


KEYRING_SERVICE = "Playlist Artist Follower for Spotify"
LEGACY_KEYRING_SERVICE = "Spotify Artist Auto-Follow"


class TokenStorageError(RuntimeError):
    """Raised when the operating-system credential store cannot be used."""


class KeyringCacheHandler(CacheHandler):
    """Store Spotipy token dictionaries in the native OS credential store."""

    def __init__(self, client_id, keyring_module=keyring):
        digest = hashlib.sha256(client_id.encode("utf-8")).hexdigest()[:24]
        self.account = f"spotify-pkce-{digest}"
        self.keyring = keyring_module

    def get_cached_token(self):
        value = self._get_password(KEYRING_SERVICE)
        migrated = False
        if not value:
            value = self._get_password(LEGACY_KEYRING_SERVICE)
            migrated = bool(value)
        if not value:
            return None
        try:
            token_info = json.loads(value)
        except json.JSONDecodeError as exc:
            raise TokenStorageError(
                "The saved Spotify login is damaged. Use 'Forget saved login' "
                "and connect again."
            ) from exc
        if not isinstance(token_info, dict):
            raise TokenStorageError("The saved Spotify login has an invalid format.")
        if migrated:
            self.save_token_to_cache(token_info)
            try:
                self.keyring.delete_password(LEGACY_KEYRING_SERVICE, self.account)
            except (KeyringError, PasswordDeleteError):
                pass
        return token_info

    def _get_password(self, service):
        try:
            return self.keyring.get_password(service, self.account)
        except KeyringError as exc:
            raise TokenStorageError(
                "The operating-system credential store could not be read."
            ) from exc

    def save_token_to_cache(self, token_info):
        try:
            self.keyring.set_password(
                KEYRING_SERVICE,
                self.account,
                json.dumps(token_info, separators=(",", ":")),
            )
        except KeyringError as exc:
            raise TokenStorageError(
                "The operating-system credential store could not save the login."
            ) from exc

    def clear(self):
        removed = False
        for service in (KEYRING_SERVICE, LEGACY_KEYRING_SERVICE):
            try:
                self.keyring.delete_password(service, self.account)
                removed = True
            except PasswordDeleteError:
                continue
            except KeyringError as exc:
                raise TokenStorageError(
                    "The operating-system credential store could not remove the login."
                ) from exc
        return removed


def create_pkce_client(client_id, redirect_uri=DEFAULT_REDIRECT_URI):
    """Create a Spotify client that uses PKCE and native keychain storage."""
    cache_handler = KeyringCacheHandler(client_id)
    auth_manager = SpotifyPKCE(
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=secrets.token_urlsafe(32),
        scope=SCOPE,
        cache_handler=cache_handler,
        open_browser=True,
        requests_timeout=30,
    )
    client = spotipy.Spotify(
        auth_manager=auth_manager,
        requests_timeout=30,
        retries=0,
        status_retries=0,
    )
    return client, auth_manager, cache_handler
