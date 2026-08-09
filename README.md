# Playlist Artist Follower for Spotify

[English](#english) · [Deutsch](#deutsch)

## English

A reusable open-source tool that automatically follows Spotify artists found
in a playlist selected by the user. Existing follows and duplicate artists are
skipped. Use the native Windows or macOS desktop app, run the Python source, or
automate it every Friday through your own GitHub Actions fork.

> This community project is not affiliated with or endorsed by Spotify.

### Use it with your own Spotify account

This repository is a tool, not a hosted service. Every user creates their own
Spotify Developer app. The desktop app needs only that app's Client ID; users
who want weekly automation create a fork and store their Client ID, Client
Secret, refresh token, and playlist ID in private GitHub settings. The public
repository contains no shared Spotify credentials, account data, or personal
playlist configuration.

### Features

- native desktop app for Windows, Apple Silicon Macs, and Intel Macs
- secure PKCE browser login without a Client Secret in the desktop app
- refresh tokens stored in the Windows Credential Manager or macOS Keychain
- current Spotify Web API behavior for Development Mode in 2026
- independent per-user configuration through GitHub Secrets and Variables
- complete playlist pagination instead of reading only the first page
- support for current `item` and compatible legacy `track` response fields
- duplicate artist removal while preserving source order
- checks the user's library and follows only missing artists
- API-compliant batches of no more than 40 artist URIs
- secure refresh-token authentication without plaintext `.cache` files
- `DRY_RUN` preview before changing the Spotify account
- manual and weekly GitHub Actions runs
- optional public embed fallback for inaccessible playlists

### Choose how to use it

| Option | Best for | Spotify credentials |
| --- | --- | --- |
| Desktop app | most users; manual scans on Windows or macOS | Client ID only; PKCE browser login |
| GitHub Actions | unattended weekly automation | Client ID, Client Secret, and refresh token as private Secrets |
| Python source | developers and local command-line use | depends on the selected entry point |

### Desktop app — recommended

Download the current build from
[GitHub Releases](https://github.com/Kotdesigner/Spotify-Artist-Auto-Follow-Playlist/releases):

- `Playlist-Artist-Follower-for-Spotify-Windows-x64.exe` for 64-bit Windows
- `Playlist-Artist-Follower-for-Spotify-macOS-Apple-Silicon.zip` for M-series Macs
- `Playlist-Artist-Follower-for-Spotify-macOS-Intel.zip` for Intel Macs

The public builds are currently unsigned. Windows SmartScreen or macOS
Gatekeeper may therefore show a warning. The source and reproducible build
workflow are included in this repository.

#### Desktop setup

1. Create your own app in the
   [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Add this exact Redirect URI and enable **Web API**:

   ```text
   http://127.0.0.1:8888/callback
   ```

3. Start the downloaded application.
4. Paste your Spotify **Client ID** and playlist link.
5. Keep **Dry run** enabled for the first scan.
6. Select **Connect and scan** and approve access in the browser.
7. Review the artist preview. Disable Dry run only when it is correct.

The desktop app never asks for a Client Secret. Spotify tokens are stored in
the operating-system credential store, not in a plaintext project file. Use
**Forget saved login** to remove them.

### Important Spotify limitation

In Development Mode, Spotify's playlist-items endpoint is available only for
playlists owned by the authenticated user or playlists where that user is a
collaborator. The Spotify app owner also needs an active Premium subscription.

The optional embed fallback can discover track IDs from some public playlists,
but it must then request every track individually to discover its artists. This
uses considerably more API quota, relies on an undocumented embed format, and
is disabled by default. Prefer an owned or collaborative source playlist.

Following artists can influence Release Radar and other recommendations, but
Release Radar also considers listening history and artists Spotify predicts the
listener will enjoy. Following is not the only input.

### Requirements for GitHub Actions

- GitHub account for automation
- Spotify Premium account for the owner of a Development Mode app
- Spotify Developer app with **Web API** enabled
- Python 3.12 for local setup
- source playlist owned by you or shared with you as a collaborator

### GitHub Actions setup

#### 1. Fork the repository

Select **Fork** at the top of this GitHub repository. The automation will run
inside your own fork with your own Spotify credentials and playlist.

Alternatively, clone your fork locally:

```bash
git clone https://github.com/YOUR-GITHUB-NAME/Spotify-Artist-Auto-Follow-Playlist.git
cd Spotify-Artist-Auto-Follow-Playlist
```

#### 2. Create a Spotify Developer app

1. Open the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Select **Create app**.
3. Enter an app name and description.
4. Add this exact Redirect URI:

   ```text
   http://127.0.0.1:8888/callback
   ```

5. Enable **Web API** and save.
6. Copy the **Client ID** and securely copy the **Client Secret**.

Do not use `localhost`; Spotify requires an explicit loopback IP address.

#### 3. Generate a refresh token

Run once on your computer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python get_refresh_token.py
```

Enter the Client ID and Client Secret when prompted, approve the requested
Spotify permissions in the browser, and copy the printed
`SPOTIPY_REFRESH_TOKEN`.

The refresh token is a password. Never commit it, post it in an issue, or put
it in a screenshot. This project deliberately uses an in-memory cache and does
not create Spotipy's plaintext `.cache` file.

#### 4. Add GitHub Secrets

In your fork, open:

**Settings → Secrets and variables → Actions → Secrets**

Create these repository secrets:

| Name | Value |
| --- | --- |
| `SPOTIPY_CLIENT_ID` | Client ID of the Spotify app |
| `SPOTIPY_CLIENT_SECRET` | Client Secret of the Spotify app |
| `SPOTIPY_REFRESH_TOKEN` | output from `get_refresh_token.py` |

#### 5. Add GitHub Variables

Open **Settings → Secrets and variables → Actions → Variables**:

| Name | Required | Default | Purpose |
| --- | --- | --- | --- |
| `SOURCE_PLAYLIST_ID` | yes | – | playlist whose artists will be followed |
| `SPOTIPY_REDIRECT_URI` | no | `http://127.0.0.1:8888/callback` | must match the token setup |
| `DRY_RUN` | recommended first | `false` | preview without following artists |
| `ALLOW_EMBED_FALLBACK` | no | `false` | try the quota-heavy public embed fallback |
| `EMBED_REQUEST_DELAY_SECONDS` | no | `0.35` | delay between fallback track requests |

The playlist ID is the 22-character part after `/playlist/` and before `?`:

```text
https://open.spotify.com/playlist/YOUR_PLAYLIST_ID?si=...
                                  ^^^^^^^^^^^^^^^^
```

Store only the ID, not the complete URL.

#### 6. Start a safe test

1. Set `DRY_RUN` to `true`.
2. Open **Actions → Follow Spotify artists → Run workflow**.
3. Check the artist preview in the workflow log.
4. If it is correct, set `DRY_RUN` to `false`.
5. Run the workflow again.

The workflow runs every Friday at **05:00 UTC**. Change the schedule in
`.github/workflows/follow-artists.yml` if needed. New forks without a
`SOURCE_PLAYLIST_ID` skip the job instead of failing.

### Run locally

Run the desktop interface from source:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python desktop_app.py
```

Or run the automation-oriented command-line script:

```bash
export SPOTIPY_CLIENT_ID='...'
export SPOTIPY_CLIENT_SECRET='...'
export SPOTIPY_REFRESH_TOKEN='...'
export SOURCE_PLAYLIST_ID='...'
export DRY_RUN='true'
python follow_artists.py
```

### How it works

1. Reads all playlist pages in source order.
2. Extracts every valid artist and removes source duplicates.
3. Checks artist URIs against the current user's library in batches of 40.
4. Prints a preview of missing artists.
5. Follows only missing artists, again in batches of 40.

A second run with an unchanged playlist follows nobody.

### Troubleshooting

#### HTTP 400 / Invalid redirect URI

Use exactly `http://127.0.0.1:8888/callback` in the Spotify Dashboard, token
generation, and optional GitHub variable.

#### HTTP 401

The Client ID, Client Secret, and refresh token must belong to the same Spotify
app. Generate a new refresh token after rotating the Client Secret.

#### HTTP 403 when reading the playlist

The authenticated user must own the playlist or be a collaborator. Copy tracks
into your own playlist if possible. The optional embed fallback may work for a
public playlist but uses one additional API request per track.

#### HTTP 429

Wait for Spotify's `Retry-After` period. Development Mode quota is shared by
all apps under one developer account. Avoid repeatedly running the embed
fallback.

### Development

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

See [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

### License

[MIT](LICENSE)

---

## Deutsch

Ein wiederverwendbares Open-Source-Werkzeug, das automatisch den Künstlern
einer vom Nutzer gewählten Spotify-Playlist folgt. Bereits gefolgte und
innerhalb der Quelle doppelte Künstler werden übersprungen. Es kann als native
Windows- oder macOS-App, direkt aus dem Python-Quellcode oder jeden Freitag
automatisch über einen eigenen GitHub-Actions-Fork ausgeführt werden.

> Dieses Community-Projekt ist nicht mit Spotify verbunden oder von Spotify
> unterstützt.

### Mit dem eigenen Spotify-Konto verwenden

Dieses Repository ist ein Werkzeug und kein gehosteter Dienst. Jeder Nutzer
erstellt eine eigene Spotify Developer App. Für die Desktop-App genügt deren
Client ID. Wer die wöchentliche Automatisierung verwenden möchte, erstellt
einen Fork und hinterlegt Client ID, Client Secret, Refresh-Token und
Playlist-ID in den privaten GitHub-Einstellungen. Das öffentliche Repository
enthält keine gemeinsam genutzten Spotify-Zugangsdaten, Kontodaten oder
persönlichen Playlist-Einstellungen.

### Funktionen

- native Desktop-App für Windows, Apple-Silicon-Macs und Intel-Macs
- sichere PKCE-Browseranmeldung ohne Client Secret in der Desktop-App
- Refresh-Token im Windows Credential Manager oder macOS-Schlüsselbund
- aktuelles Spotify-Web-API-Verhalten für Development Mode im Jahr 2026
- unabhängige Konfiguration pro Nutzer über GitHub Secrets und Variablen
- vollständige Playlist-Pagination statt nur der ersten Seite
- Unterstützung für das aktuelle Feld `item` und das kompatible alte `track`
- Duplikatprüfung bei Erhalt der Quellreihenfolge
- prüft die Bibliothek und folgt nur noch fehlenden Künstlern
- API-konforme Batches mit maximal 40 Künstler-URIs
- sichere Refresh-Token-Anmeldung ohne Klartextdatei `.cache`
- Vorschau über `DRY_RUN`, bevor das Spotify-Konto verändert wird
- manuelle und wöchentliche Ausführung über GitHub Actions
- optionaler öffentlicher Embed-Fallback für nicht erreichbare Playlists

### Verwendung auswählen

| Variante | Geeignet für | Spotify-Zugangsdaten |
| --- | --- | --- |
| Desktop-App | die meisten Nutzer; manuelle Läufe unter Windows oder macOS | nur Client ID; PKCE-Browseranmeldung |
| GitHub Actions | unbeaufsichtigte wöchentliche Automatisierung | Client ID, Client Secret und Refresh-Token als private Secrets |
| Python-Quellcode | Entwickler und lokale Kommandozeile | abhängig vom verwendeten Einstiegspunkt |

### Desktop-App — empfohlen

Den aktuellen Build unter
[GitHub Releases](https://github.com/Kotdesigner/Spotify-Artist-Auto-Follow-Playlist/releases)
herunterladen:

- `Playlist-Artist-Follower-for-Spotify-Windows-x64.exe` für 64-Bit-Windows
- `Playlist-Artist-Follower-for-Spotify-macOS-Apple-Silicon.zip` für Macs mit M-Prozessor
- `Playlist-Artist-Follower-for-Spotify-macOS-Intel.zip` für Intel-Macs

Die öffentlichen Builds sind aktuell nicht signiert. Windows SmartScreen oder
macOS Gatekeeper können deshalb eine Warnung anzeigen. Quellcode und
reproduzierbarer Build-Workflow befinden sich in diesem Repository.

#### Desktop-Einrichtung

1. Im [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   eine eigene App erstellen.
2. Exakt diese Redirect URI hinzufügen und **Web API** aktivieren:

   ```text
   http://127.0.0.1:8888/callback
   ```

3. Die heruntergeladene Anwendung starten.
4. Spotify **Client ID** und Playlist-Link einfügen.
5. Beim ersten Scan **Dry run** aktiviert lassen.
6. **Connect and scan** auswählen und den Zugriff im Browser bestätigen.
7. Die Künstler-Vorschau prüfen. Dry Run erst danach deaktivieren.

Die Desktop-App fragt niemals nach einem Client Secret. Spotify-Tokens werden
im Zugangsdaten-Speicher des Betriebssystems und nicht als Klartextdatei im
Projekt abgelegt. Mit **Forget saved login** können sie entfernt werden.

### Wichtige Spotify-Einschränkung

Im Development Mode kann Spotifys Playlist-Items-Endpunkt nur Playlists lesen,
die dem angemeldeten Nutzer gehören oder an denen er mitarbeitet. Der Besitzer
der Spotify-App benötigt außerdem ein aktives Premium-Abo.

Der optionale Embed-Fallback kann aus manchen öffentlichen Playlists Track-IDs
ermitteln. Danach muss jedoch jeder Track einzeln abgefragt werden, um seine
Künstler zu bestimmen. Das verbraucht deutlich mehr API-Quota, verwendet ein
undokumentiertes Embed-Format und ist standardmäßig deaktiviert. Eine eigene
oder kollaborative Quell-Playlist ist zuverlässiger.

Künstlern zu folgen kann Release Radar und andere Empfehlungen beeinflussen.
Spotify berücksichtigt aber auch den Hörverlauf und weitere Künstler, die dem
Hörer vermutlich gefallen. Folgen ist nicht das einzige Signal.

### Voraussetzungen für GitHub Actions

- GitHub-Konto für die Automatisierung
- Spotify Premium für den Besitzer einer Development-Mode-App
- Spotify Developer App mit aktivierter **Web API**
- Python 3.12 für die lokale Einrichtung
- eigene oder kollaborativ geteilte Quell-Playlist

### GitHub-Actions-Einrichtung

#### 1. Repository forken

Oben in diesem GitHub-Repository **Fork** auswählen. Die Automatisierung läuft
anschließend im eigenen Fork mit den eigenen Spotify-Zugangsdaten und der
eigenen Playlist.

Alternativ den eigenen Fork lokal klonen:

```bash
git clone https://github.com/DEIN-GITHUB-NAME/Spotify-Artist-Auto-Follow-Playlist.git
cd Spotify-Artist-Auto-Follow-Playlist
```

#### 2. Spotify Developer App erstellen

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) öffnen.
2. **Create app** auswählen.
3. App-Namen und Beschreibung eintragen.
4. Exakt diese Redirect URI hinzufügen:

   ```text
   http://127.0.0.1:8888/callback
   ```

5. **Web API** aktivieren und speichern.
6. **Client ID** und anschließend das **Client Secret** sicher kopieren.

Nicht `localhost` verwenden. Spotify verlangt eine explizite Loopback-IP.

#### 3. Refresh-Token erzeugen

Einmalig auf dem eigenen Computer ausführen:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python get_refresh_token.py
```

Client ID und Client Secret eingeben, die Spotify-Berechtigungen im Browser
bestätigen und den ausgegebenen `SPOTIPY_REFRESH_TOKEN` kopieren.

Der Refresh-Token ist ein Passwort. Niemals committen, in einem Issue posten
oder in einem Screenshot zeigen. Dieses Projekt verwendet absichtlich einen
Speicher-Cache und erzeugt keine Spotipy-Klartextdatei `.cache`.

#### 4. GitHub Secrets eintragen

Im eigenen Fork öffnen:

**Settings → Secrets and variables → Actions → Secrets**

Diese Repository-Secrets anlegen:

| Name | Inhalt |
| --- | --- |
| `SPOTIPY_CLIENT_ID` | Client ID der Spotify App |
| `SPOTIPY_CLIENT_SECRET` | Client Secret der Spotify App |
| `SPOTIPY_REFRESH_TOKEN` | Ausgabe von `get_refresh_token.py` |

#### 5. GitHub-Variablen eintragen

Unter **Settings → Secrets and variables → Actions → Variables**:

| Name | Erforderlich | Standard | Bedeutung |
| --- | --- | --- | --- |
| `SOURCE_PLAYLIST_ID` | ja | – | Playlist, deren Künstler gefolgt werden |
| `SPOTIPY_REDIRECT_URI` | nein | `http://127.0.0.1:8888/callback` | muss zur Token-Erzeugung passen |
| `DRY_RUN` | für ersten Test empfohlen | `false` | Vorschau ohne Künstlern zu folgen |
| `ALLOW_EMBED_FALLBACK` | nein | `false` | quota-intensiven Embed-Fallback versuchen |
| `EMBED_REQUEST_DELAY_SECONDS` | nein | `0.35` | Pause zwischen Fallback-Track-Abfragen |

Die Playlist-ID ist der 22 Zeichen lange Teil hinter `/playlist/` und vor `?`:

```text
https://open.spotify.com/playlist/DEINE_PLAYLIST_ID?si=...
                                  ^^^^^^^^^^^^^^^^^^
```

Nur die ID speichern, nicht die vollständige URL.

#### 6. Sicheren Test starten

1. `DRY_RUN` auf `true` setzen.
2. **Actions → Follow Spotify artists → Run workflow** öffnen.
3. Die Künstler-Vorschau im Workflow-Log kontrollieren.
4. Wenn alles stimmt, `DRY_RUN` auf `false` setzen.
5. Workflow erneut starten.

Der Workflow läuft jeden Freitag um **05:00 UTC**. Der Zeitplan kann in
`.github/workflows/follow-artists.yml` geändert werden. Neue Forks ohne
`SOURCE_PLAYLIST_ID` überspringen den Job, statt einen Fehler zu erzeugen.

### Lokal ausführen

Desktop-Oberfläche aus dem Quellcode starten:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python desktop_app.py
```

Oder das für Automatisierung vorgesehene Kommandozeilen-Skript verwenden:

```bash
export SPOTIPY_CLIENT_ID='...'
export SPOTIPY_CLIENT_SECRET='...'
export SPOTIPY_REFRESH_TOKEN='...'
export SOURCE_PLAYLIST_ID='...'
export DRY_RUN='true'
python follow_artists.py
```

### Funktionsweise

1. Liest alle Playlist-Seiten in Quellreihenfolge.
2. Extrahiert gültige Künstler und entfernt doppelte Künstler.
3. Prüft Künstler-URIs in 40er-Batches gegen die Nutzerbibliothek.
4. Zeigt eine Vorschau der noch nicht gefolgten Künstler.
5. Folgt ausschließlich fehlenden Künstlern, ebenfalls in 40er-Batches.

Ein zweiter Lauf mit unveränderter Playlist folgt niemandem erneut.

### Fehlerbehebung

#### HTTP 400 / Invalid redirect URI

Im Spotify Dashboard, bei der Token-Erzeugung und in der optionalen
GitHub-Variable exakt `http://127.0.0.1:8888/callback` verwenden.

#### HTTP 401

Client ID, Client Secret und Refresh-Token müssen aus derselben Spotify App
stammen. Nach einer Secret-Rotation einen neuen Refresh-Token erzeugen.

#### HTTP 403 beim Lesen der Playlist

Der angemeldete Nutzer muss Eigentümer oder Mitwirkender der Playlist sein.
Wenn möglich, die Tracks in eine eigene Playlist kopieren. Der optionale
Embed-Fallback kann bei einer öffentlichen Playlist funktionieren, benötigt
aber pro Track eine zusätzliche API-Abfrage.

#### HTTP 429

Spotifys `Retry-After`-Zeitraum abwarten. Die Development-Mode-Quota wird von
allen Apps eines Entwicklerkontos geteilt. Den Embed-Fallback nicht wiederholt
starten.

### Entwicklung

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Siehe [SECURITY.md](SECURITY.md) und [CONTRIBUTING.md](CONTRIBUTING.md).

### Lizenz

[MIT](LICENSE)
