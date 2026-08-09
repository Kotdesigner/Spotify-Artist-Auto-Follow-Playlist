#!/usr/bin/env python3
"""Build the native desktop executable for the current operating system."""

import os
import plistlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "Playlist-Artist-Follower-for-Spotify"
APP_VERSION = "2.2.0"


def finalize_macos_bundle():
    """Set release metadata and refresh the outer ad-hoc signature."""
    app_bundle = ROOT / "dist" / f"{APP_NAME}.app"
    info_path = app_bundle / "Contents" / "Info.plist"
    with info_path.open("rb") as stream:
        info = plistlib.load(stream)
    info["CFBundleDisplayName"] = "Playlist Artist Follower for Spotify"
    info["CFBundleName"] = "Playlist Artist Follower for Spotify"
    info["CFBundleShortVersionString"] = APP_VERSION
    info["CFBundleVersion"] = APP_VERSION
    with info_path.open("wb") as stream:
        plistlib.dump(info, stream)
    subprocess.run(
        [
            "codesign",
            "--force",
            "--sign",
            "-",
            "--timestamp=none",
            str(app_bundle),
        ],
        check=True,
    )


def main():
    os.environ.setdefault(
        "PYINSTALLER_CONFIG_DIR",
        str(ROOT / "build" / ".pyinstaller-cache"),
    )
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "generate_icons.py")],
        check=True,
        cwd=ROOT,
    )

    add_data_separator = os.pathsep
    arguments = [
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        APP_NAME,
        "--collect-all",
        "keyring",
        "--add-data",
        f"{ROOT / 'assets' / 'app.png'}{add_data_separator}assets",
        "--distpath",
        str(ROOT / "dist"),
        "--workpath",
        str(ROOT / "build"),
        "--specpath",
        str(ROOT),
    ]

    if sys.platform == "win32":
        arguments.extend(
            [
                "--onefile",
                "--icon",
                str(ROOT / "assets" / "app.ico"),
                "--version-file",
                str(ROOT / "tools" / "windows_version_info.txt"),
            ]
        )
    elif sys.platform == "darwin":
        arguments.extend(
            [
                "--onedir",
                "--icon",
                str(ROOT / "assets" / "app.icns"),
                "--osx-bundle-identifier",
                "io.github.kotdesigner.playlist-artist-follower-for-spotify",
            ]
        )
    else:
        raise SystemExit("Desktop release builds currently support Windows and macOS.")

    arguments.append(str(ROOT / "desktop_app.py"))

    from PyInstaller.__main__ import run

    run(arguments)
    if sys.platform == "darwin":
        finalize_macos_bundle()


if __name__ == "__main__":
    main()
