# Security Policy

## Supported version

Security fixes are applied to the current `main` branch.

## Reporting a vulnerability

Use GitHub private vulnerability reporting or a private Security Advisory.
Never open a public issue containing credentials, refresh tokens, playlist
identifiers, account information, or exploit details.

## Credential handling

The application reads credentials only from environment variables and GitHub
Actions repository secrets:

- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`
- `SPOTIPY_REFRESH_TOKEN`

The application uses Spotipy's in-memory token cache and does not create a
plaintext `.cache` file. `.gitignore` also blocks common Spotipy cache names.

If a credential is exposed, immediately rotate the Client Secret, revoke the
old app authorization, generate a new refresh token, and replace the GitHub
Secrets. Removing a value from Git history does not revoke it.

## Embed fallback

The optional fallback reads public Spotify embed data without browser cookies.
The format is undocumented and treated as untrusted input. Only valid
22-character Spotify track IDs are accepted. The fallback then makes one
authenticated catalog request per track, which can consume API quota.
