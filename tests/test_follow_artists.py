import unittest
from unittest import mock

import follow_artists as module


ARTIST_A = "A" * 22
ARTIST_B = "B" * 22
ARTIST_C = "C" * 22
TRACK_A = "1" * 22
TRACK_B = "2" * 22


class FakePlaylistClient:
    def playlist_items(self, playlist_id, **kwargs):
        self.playlist_id = playlist_id
        self.kwargs = kwargs
        return {
            "items": [
                {
                    "item": {
                        "type": "track",
                        "artists": [
                            {"id": ARTIST_A, "name": "Artist A"},
                            {"id": ARTIST_B, "name": "Artist B"},
                        ],
                    }
                },
                {"item": {"type": "episode", "artists": []}},
            ],
            "next": "page-2",
        }

    def next(self, page):
        return {
            "items": [
                {
                    "track": {
                        "type": "track",
                        "artists": [
                            {"id": ARTIST_A, "name": "Duplicate A"},
                            {"id": ARTIST_C, "name": "Artist C"},
                        ],
                    }
                }
            ],
            "next": None,
        }


class FakeEmbedResponse:
    text = (
        '<script id="__NEXT_DATA__" type="application/json">'
        '{"tracks":["spotify:track:' + TRACK_A + '",'
        '"spotify:track:' + TRACK_B + '",'
        '"spotify:track:' + TRACK_A + '"],'
        '"ignore":"spotify:episode:' + TRACK_A + '"}'
        "</script>"
    )

    def raise_for_status(self):
        return None


class FakeEmbedSession:
    def get(self, url, timeout, headers):
        self.url = url
        self.timeout = timeout
        self.headers = headers
        return FakeEmbedResponse()


class FakeTrackClient:
    def __init__(self):
        self.calls = []

    def track(self, track_id):
        self.calls.append(track_id)
        if track_id == TRACK_A:
            return {"artists": [{"id": ARTIST_A, "name": "Artist A"}]}
        return {
            "artists": [
                {"id": ARTIST_A, "name": "Artist A"},
                {"id": ARTIST_B, "name": "Artist B"},
            ]
        }


class FakeLibraryClient:
    def __init__(self):
        self.check_calls = []
        self.follow_calls = []

    def current_user_saved_items(self, uris):
        self.check_calls.append(uris)
        return [uri.endswith(ARTIST_A) for uri in uris]

    def user_follow_artists(self, ids):
        self.follow_calls.append(ids)


class FollowArtistsTests(unittest.TestCase):
    def test_env_flag(self):
        with mock.patch.dict(module.os.environ, {"FLAG": "yes"}):
            self.assertTrue(module.env_flag("FLAG"))
        with mock.patch.dict(module.os.environ, {"FLAG": "off"}):
            self.assertFalse(module.env_flag("FLAG", default=True))
        with mock.patch.dict(module.os.environ, {}, clear=True):
            self.assertTrue(module.env_flag("FLAG", default=True))

    def test_validate_playlist_id(self):
        playlist_id = "1" * 22
        self.assertEqual(module.validate_playlist_id(playlist_id), playlist_id)
        with self.assertRaises(ValueError):
            module.validate_playlist_id(
                "https://open.spotify.com/playlist/not-an-id"
            )

    def test_playlist_artists_paginates_and_deduplicates(self):
        client = FakePlaylistClient()
        self.assertEqual(
            module.playlist_artists(client, "1" * 22),
            [
                (ARTIST_A, "Artist A"),
                (ARTIST_B, "Artist B"),
                (ARTIST_C, "Artist C"),
            ],
        )
        self.assertEqual(client.kwargs["limit"], 50)

    def test_embed_track_ids_are_ordered_and_deduplicated(self):
        session = FakeEmbedSession()
        self.assertEqual(
            module.embed_playlist_track_ids("1" * 22, session=session),
            [TRACK_A, TRACK_B],
        )
        self.assertIn("/embed/playlist/", session.url)

    def test_artists_from_track_ids_deduplicates(self):
        client = FakeTrackClient()
        self.assertEqual(
            module.artists_from_track_ids(client, [TRACK_A, TRACK_B]),
            [(ARTIST_A, "Artist A"), (ARTIST_B, "Artist B")],
        )
        self.assertEqual(client.calls, [TRACK_A, TRACK_B])

    def test_unfollowed_artists_uses_40_item_batches(self):
        artists = [(f"{number:022d}", str(number)) for number in range(85)]
        artists[0] = (ARTIST_A, "Already followed")
        client = FakeLibraryClient()
        missing = module.unfollowed_artists(client, artists)
        self.assertEqual(len(client.check_calls), 3)
        self.assertEqual([len(call) for call in client.check_calls], [40, 40, 5])
        self.assertNotIn((ARTIST_A, "Already followed"), missing)
        self.assertEqual(len(missing), 84)

    def test_follow_artists_uses_40_item_batches(self):
        artists = [(f"{number:022d}", str(number)) for number in range(81)]
        client = FakeLibraryClient()
        module.follow_artists(client, artists)
        self.assertEqual(
            [len(call) for call in client.follow_calls],
            [40, 40, 1],
        )


if __name__ == "__main__":
    unittest.main()
