import json
import unittest

import desktop_logic as module
from spotify_desktop_auth import KEYRING_SERVICE, KeyringCacheHandler


CLIENT_ID = "C" * 32
PLAYLIST_ID = "P" * 22


class FakeKeyring:
    def __init__(self):
        self.values = {}

    def get_password(self, service, account):
        return self.values.get((service, account))

    def set_password(self, service, account, value):
        self.values[(service, account)] = value

    def delete_password(self, service, account):
        from keyring.errors import PasswordDeleteError

        key = (service, account)
        if key not in self.values:
            raise PasswordDeleteError("missing")
        del self.values[key]


class DesktopAppTests(unittest.TestCase):
    def test_validate_client_id(self):
        self.assertEqual(module.validate_client_id(CLIENT_ID), CLIENT_ID)
        with self.assertRaises(ValueError):
            module.validate_client_id("not valid!")

    def test_parse_playlist_input_accepts_id_and_urls(self):
        self.assertEqual(module.parse_playlist_input(PLAYLIST_ID), PLAYLIST_ID)
        self.assertEqual(
            module.parse_playlist_input(
                f"https://open.spotify.com/playlist/{PLAYLIST_ID}?si=example"
            ),
            PLAYLIST_ID,
        )
        self.assertEqual(
            module.parse_playlist_input(
                f"https://open.spotify.com/intl-de/playlist/{PLAYLIST_ID}"
            ),
            PLAYLIST_ID,
        )

    def test_parse_playlist_input_rejects_non_spotify_urls(self):
        with self.assertRaises(ValueError):
            module.parse_playlist_input(
                f"https://example.com/playlist/{PLAYLIST_ID}"
            )

    def test_keyring_cache_round_trip_and_clear(self):
        fake_keyring = FakeKeyring()
        cache = KeyringCacheHandler(CLIENT_ID, keyring_module=fake_keyring)
        token = {
            "access_token": "access",
            "refresh_token": "refresh",
            "expires_at": 123,
            "scope": "scope",
        }

        self.assertIsNone(cache.get_cached_token())
        cache.save_token_to_cache(token)
        self.assertEqual(cache.get_cached_token(), token)
        stored = fake_keyring.values[(KEYRING_SERVICE, cache.account)]
        self.assertEqual(json.loads(stored), token)
        self.assertTrue(cache.clear())
        self.assertFalse(cache.clear())


if __name__ == "__main__":
    unittest.main()
