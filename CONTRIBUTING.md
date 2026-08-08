# Contributing

Contributions are welcome.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Build the desktop application on Windows or macOS:

```bash
python -m pip install -r requirements-build.txt
python tools/build_desktop.py
```

PyInstaller is not a cross-compiler. Test Windows builds on Windows and macOS
builds on the corresponding Mac architecture.

Keep credentials, cache files, playlist IDs, local paths, and account data out
of commits and test fixtures. Add or update unit tests for behavior changes.
Use fake clients for tests; do not modify a real Spotify account during CI.
