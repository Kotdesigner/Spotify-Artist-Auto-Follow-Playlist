# Security Policy

## Supported version

Security fixes are applied to the current `main` branch.

## Reporting a vulnerability

Use GitHub private vulnerability reporting or a private Security Advisory.
Never open a public issue containing credentials, refresh tokens, playlist
identifiers, account information, or exploit details.

## Desktop credential handling

The desktop application uses Spotify's PKCE authorization flow and never asks
for a Client Secret. The user supplies only their public Client ID. Access and
refresh tokens are stored through Python Keyring in the Windows Credential
Manager or macOS Keychain. **Forget saved login** deletes that keychain entry.

The desktop application does not use Spotipy's plaintext file cache. Public
release executables never contain a shared Client ID, Client Secret, refresh
token, playlist ID, or user account.

## GitHub Actions credential handling

The unattended command-line workflow reads credentials from environment
variables and GitHub Actions repository secrets:

- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`
- `SPOTIPY_REFRESH_TOKEN`

The workflow uses Spotipy's in-memory token cache and does not create a
plaintext `.cache` file. `.gitignore` blocks common Spotipy cache names.

If a credential is exposed, immediately rotate the Client Secret, revoke the
old app authorization, generate a new refresh token, and replace the GitHub
Secrets. Removing a value from Git history does not revoke it.

## Embed fallback

The optional fallback reads public Spotify embed data without browser cookies.
The format is undocumented and treated as untrusted input. Only valid
22-character Spotify track IDs are accepted. The fallback then makes one
authenticated catalog request per track, which can consume API quota.
