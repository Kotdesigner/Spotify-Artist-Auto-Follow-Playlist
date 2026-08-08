# Changelog

## 2.1.0 - 2026-08-09

- added a cross-platform desktop GUI with Dry Run and progress reporting
- added Spotify Authorization Code with PKCE, requiring no Client Secret in
  the desktop app
- added native operating-system keychain storage for refresh tokens
- added reproducible PyInstaller builds for Windows x64, Apple Silicon Macs,
  and Intel Macs
- added original generated application icons and architecture-specific release
  packages

## 2.0.0 - 2026-08-09

- migrated artist following to Spotify's current generic library API through
  Spotipy 2.26
- migrated playlist reads to the current playlist-items response format
- added full pagination and 40-item library batches
- added checks that skip artists already followed
- replaced plaintext token caching with an in-memory refresh-token workflow
- added dry runs, actionable errors, tests, and GitHub Actions
- added an optional, quota-conscious public embed fallback
