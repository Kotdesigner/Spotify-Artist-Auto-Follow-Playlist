# Changelog

## 2.0.0 - 2026-08-09

- migrated artist following to Spotify's current generic library API through
  Spotipy 2.26
- migrated playlist reads to the current playlist-items response format
- added full pagination and 40-item library batches
- added checks that skip artists already followed
- replaced plaintext token caching with an in-memory refresh-token workflow
- added dry runs, actionable errors, tests, and GitHub Actions
- added an optional, quota-conscious public embed fallback
