#!/usr/bin/env python3
"""Package PyInstaller output with an architecture-specific release name."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "Playlist-Artist-Follower-for-Spotify"


def main():
    basename = os.environ.get("ARTIFACT_BASENAME", "").strip()
    if not basename:
        raise SystemExit("ARTIFACT_BASENAME is required")

    release_dir = ROOT / "release"
    release_dir.mkdir(parents=True, exist_ok=True)

    if sys.platform == "win32":
        source = ROOT / "dist" / f"{APP_NAME}.exe"
        destination = release_dir / f"{basename}.exe"
        destination.unlink(missing_ok=True)
        shutil.copy2(source, destination)
    elif sys.platform == "darwin":
        source = ROOT / "dist" / f"{APP_NAME}.app"
        destination = release_dir / f"{basename}.zip"
        destination.unlink(missing_ok=True)
        subprocess.run(
            [
                "ditto",
                "-c",
                "-k",
                "--sequesterRsrc",
                "--keepParent",
                str(source),
                str(destination),
            ],
            check=True,
        )
    else:
        raise SystemExit("Release packaging supports Windows and macOS.")

    print(f"Packaged {destination}")


if __name__ == "__main__":
    main()
