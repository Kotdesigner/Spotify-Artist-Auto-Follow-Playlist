#!/usr/bin/env python3
"""Cross-platform desktop interface for Spotify Artist Auto-Follow."""

import logging
import queue
import threading
import webbrowser

import requests
import tkinter as tk
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError
from tkinter import messagebox, scrolledtext, ttk

from desktop_logic import parse_playlist_input, validate_client_id
from follow_artists import (
    DEFAULT_REDIRECT_URI,
    api_error_message,
    follow_artists,
    read_source_artists,
    unfollowed_artists,
    validate_playlist_id,
)
from spotify_desktop_auth import (
    KeyringCacheHandler,
    TokenStorageError,
    create_pkce_client,
)


APP_NAME = "Spotify Artist Auto-Follow"
APP_VERSION = "2.1.0"


class DesktopApp:
    """Tkinter interface that keeps network work off the UI thread."""

    BACKGROUND = "#10131A"
    PANEL = "#191E29"
    INPUT = "#242B3A"
    TEXT = "#F4F7FB"
    MUTED = "#A8B1C2"
    ACCENT = "#7C5CFF"
    ACCENT_ACTIVE = "#927AFF"
    SUCCESS = "#45D483"
    ERROR = "#FF6B78"

    def __init__(self, root):
        self.root = root
        self.messages = queue.Queue()
        self.worker = None
        self.running = False

        root.title(f"{APP_NAME} {APP_VERSION}")
        root.geometry("820x720")
        root.minsize(720, 620)
        root.configure(bg=self.BACKGROUND)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._configure_styles()
        self._build_interface()
        self.root.after(100, self._poll_messages)

    def _configure_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("App.TFrame", background=self.BACKGROUND)
        style.configure("Panel.TFrame", background=self.PANEL)
        style.configure(
            "Title.TLabel",
            background=self.BACKGROUND,
            foreground=self.TEXT,
            font=("Arial", 24, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.BACKGROUND,
            foreground=self.MUTED,
            font=("Arial", 11),
        )
        style.configure(
            "PanelTitle.TLabel",
            background=self.PANEL,
            foreground=self.TEXT,
            font=("Arial", 12, "bold"),
        )
        style.configure(
            "PanelText.TLabel",
            background=self.PANEL,
            foreground=self.MUTED,
            font=("Arial", 10),
        )
        style.configure(
            "Field.TLabel",
            background=self.PANEL,
            foreground=self.TEXT,
            font=("Arial", 10, "bold"),
        )
        style.configure(
            "App.TEntry",
            fieldbackground=self.INPUT,
            foreground=self.TEXT,
            insertcolor=self.TEXT,
            bordercolor=self.INPUT,
            padding=9,
        )
        style.configure(
            "Accent.TButton",
            background=self.ACCENT,
            foreground="#FFFFFF",
            font=("Arial", 11, "bold"),
            padding=(18, 10),
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.ACCENT_ACTIVE), ("disabled", "#4A475F")],
            foreground=[("disabled", "#B6B4C0")],
        )
        style.configure(
            "Secondary.TButton",
            background=self.INPUT,
            foreground=self.TEXT,
            padding=(12, 8),
            borderwidth=0,
        )
        style.map("Secondary.TButton", background=[("active", "#30394C")])
        style.configure(
            "App.TCheckbutton",
            background=self.PANEL,
            foreground=self.TEXT,
            font=("Arial", 10),
        )
        style.map(
            "App.TCheckbutton",
            background=[("active", self.PANEL)],
            foreground=[("active", self.TEXT)],
        )
        style.configure(
            "App.Horizontal.TProgressbar",
            troughcolor=self.INPUT,
            background=self.ACCENT,
            bordercolor=self.INPUT,
            lightcolor=self.ACCENT,
            darkcolor=self.ACCENT,
        )

    def _build_interface(self):
        outer = ttk.Frame(self.root, style="App.TFrame", padding=(32, 26))
        outer.pack(fill="both", expand=True)

        ttk.Label(
            outer,
            text=APP_NAME,
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            outer,
            text=(
                "Follow every missing artist from your playlist — securely, "
                "with your own Spotify account."
            ),
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 18))

        panel = ttk.Frame(outer, style="Panel.TFrame", padding=22)
        panel.pack(fill="x")
        panel.columnconfigure(0, weight=1)

        ttk.Label(
            panel,
            text="Your Spotify connection",
            style="PanelTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            panel,
            text=(
                "The browser login uses PKCE. No Client Secret is required, "
                "and tokens are stored in your operating-system keychain."
            ),
            style="PanelText.TLabel",
            wraplength=720,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(3, 16))

        ttk.Label(panel, text="Spotify Client ID", style="Field.TLabel").grid(
            row=2,
            column=0,
            sticky="w",
        )
        self.client_id = tk.StringVar()
        self.client_entry = ttk.Entry(
            panel,
            textvariable=self.client_id,
            style="App.TEntry",
        )
        self.client_entry.grid(row=3, column=0, sticky="ew", pady=(5, 5))

        link_row = ttk.Frame(panel, style="Panel.TFrame")
        link_row.grid(row=4, column=0, sticky="ew", pady=(0, 14))
        ttk.Label(
            link_row,
            text=f"Redirect URI: {DEFAULT_REDIRECT_URI}",
            style="PanelText.TLabel",
        ).pack(side="left")
        ttk.Button(
            link_row,
            text="Open Developer Dashboard",
            command=lambda: webbrowser.open("https://developer.spotify.com/dashboard"),
            style="Secondary.TButton",
        ).pack(side="right")

        ttk.Label(
            panel,
            text="Playlist link or ID",
            style="Field.TLabel",
        ).grid(row=5, column=0, sticky="w")
        self.playlist = tk.StringVar()
        self.playlist_entry = ttk.Entry(
            panel,
            textvariable=self.playlist,
            style="App.TEntry",
        )
        self.playlist_entry.grid(row=6, column=0, sticky="ew", pady=(5, 14))

        options = ttk.Frame(panel, style="Panel.TFrame")
        options.grid(row=7, column=0, sticky="ew")
        self.dry_run = tk.BooleanVar(value=True)
        self.embed_fallback = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options,
            text="Dry run — preview only",
            variable=self.dry_run,
            style="App.TCheckbutton",
        ).pack(side="left")
        ttk.Checkbutton(
            options,
            text="Allow public embed fallback (uses more API quota)",
            variable=self.embed_fallback,
            style="App.TCheckbutton",
        ).pack(side="left", padx=(24, 0))

        actions = ttk.Frame(panel, style="Panel.TFrame")
        actions.grid(row=8, column=0, sticky="ew", pady=(18, 0))
        self.start_button = ttk.Button(
            actions,
            text="Connect and scan",
            command=self._start,
            style="Accent.TButton",
        )
        self.start_button.pack(side="left")
        self.forget_button = ttk.Button(
            actions,
            text="Forget saved login",
            command=self._forget_login,
            style="Secondary.TButton",
        )
        self.forget_button.pack(side="left", padx=(10, 0))

        self.progress = ttk.Progressbar(
            outer,
            mode="indeterminate",
            style="App.Horizontal.TProgressbar",
        )
        self.progress.pack(fill="x", pady=(18, 8))
        self.status = tk.StringVar(value="Ready. Start with Dry run enabled.")
        self.status_label = tk.Label(
            outer,
            textvariable=self.status,
            bg=self.BACKGROUND,
            fg=self.MUTED,
            anchor="w",
            font=("Arial", 10, "bold"),
        )
        self.status_label.pack(fill="x", pady=(0, 8))

        self.log = scrolledtext.ScrolledText(
            outer,
            height=12,
            wrap="word",
            bg="#0B0E13",
            fg="#DDE4F0",
            insertbackground="#DDE4F0",
            selectbackground=self.ACCENT,
            relief="flat",
            padx=14,
            pady=12,
            font=("Courier", 10),
            state="disabled",
        )
        self.log.pack(fill="both", expand=True)

        footer = ttk.Label(
            outer,
            text=(
                "Open source · Each user supplies their own Spotify Client ID · "
                "No shared account or credentials"
            ),
            style="Subtitle.TLabel",
        )
        footer.pack(anchor="w", pady=(10, 0))

        self.client_entry.focus_set()

    def _append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _emit(self, kind, *values):
        self.messages.put((kind, values))

    def _start(self):
        if self.running:
            return
        try:
            client_id = validate_client_id(self.client_id.get())
            playlist_id = parse_playlist_input(self.playlist.get())
        except ValueError as exc:
            messagebox.showerror("Check your input", str(exc), parent=self.root)
            return

        self.running = True
        self.start_button.configure(state="disabled")
        self.forget_button.configure(state="disabled")
        self.progress.start(12)
        self.status.set("Connecting to Spotify…")
        self.status_label.configure(fg=self.ACCENT_ACTIVE)
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self._append_log(f"Playlist: https://open.spotify.com/playlist/{playlist_id}")
        self._append_log(f"Dry run: {self.dry_run.get()}")

        self.worker = threading.Thread(
            target=self._run,
            args=(
                client_id,
                playlist_id,
                self.dry_run.get(),
                self.embed_fallback.get(),
            ),
            daemon=True,
        )
        self.worker.start()

    def _run(self, client_id, playlist_id, dry_run, allow_embed_fallback):
        try:
            client, auth_manager, cache_handler = create_pkce_client(client_id)
            saved_login = cache_handler.get_cached_token() is not None
            if saved_login:
                self._emit("log", "Using the saved operating-system keychain login.")
            else:
                self._emit("log", "Opening Spotify login in your web browser…")
            self._emit("status", "Waiting for Spotify authorization…")
            auth_manager.get_access_token()
            self._emit("log", "Spotify authorization successful.")

            self._emit("status", "Reading every playlist page…")
            artists = read_source_artists(
                client,
                playlist_id,
                allow_embed_fallback=allow_embed_fallback,
                logger=lambda message: self._emit("log", message),
                fallback_progress=lambda done, total: self._fallback_progress(
                    done,
                    total,
                ),
            )
            if not artists:
                raise ValueError(
                    "No artists were found. Confirm that the playlist contains tracks "
                    "and is owned by you or shared with you as a collaborator."
                )

            self._emit("log", f"Unique artists found: {len(artists)}")
            self._emit("status", "Checking which artists you already follow…")
            missing = unfollowed_artists(
                client,
                artists,
                progress=lambda done, total: self._emit(
                    "status",
                    f"Checking followed artists: {done}/{total}",
                ),
            )

            followed_count = len(artists) - len(missing)
            self._emit("log", f"Already followed: {followed_count}")
            self._emit("log", f"New artists: {len(missing)}")

            if not missing:
                self._emit("done", True, "Every playlist artist is already followed.")
                return

            self._emit("log", "")
            self._emit("log", "Artists to follow:")
            for artist_id, name in missing[:30]:
                self._emit(
                    "log",
                    f"  • {name} — https://open.spotify.com/artist/{artist_id}",
                )
            if len(missing) > 30:
                self._emit("log", f"  … and {len(missing) - 30} more")

            if dry_run:
                self._emit(
                    "done",
                    True,
                    f"Dry run complete. {len(missing)} artists would be followed.",
                )
                return

            self._emit("status", "Following missing artists…")
            follow_artists(
                client,
                missing,
                progress=lambda done, total: self._emit(
                    "status",
                    f"Following artists: {done}/{total}",
                ),
            )
            self._emit(
                "done",
                True,
                f"Successfully followed {len(missing)} new artists.",
            )
        except SpotifyException as exc:
            self._emit(
                "done",
                False,
                api_error_message("Spotify request failed", exc),
            )
        except SpotifyOauthError as exc:
            self._emit(
                "done",
                False,
                f"Spotify authorization failed: {exc}",
            )
        except TokenStorageError as exc:
            self._emit("done", False, str(exc))
        except requests.RequestException as exc:
            self._emit("done", False, f"Network request failed: {exc}")
        except ValueError as exc:
            self._emit("done", False, str(exc))
        except Exception as exc:  # defensive boundary for a desktop application
            logging.exception("Unexpected desktop application error")
            self._emit("done", False, f"Unexpected error: {exc}")

    def _fallback_progress(self, done, total):
        if done == total or done == 1 or done % 10 == 0:
            self._emit(
                "status",
                f"Resolving public embed tracks: {done}/{total}",
            )

    def _forget_login(self):
        try:
            client_id = validate_client_id(self.client_id.get())
        except ValueError as exc:
            messagebox.showerror("Client ID required", str(exc), parent=self.root)
            return
        if not messagebox.askyesno(
            "Forget saved login",
            "Remove the saved Spotify login from the operating-system keychain?",
            parent=self.root,
        ):
            return
        try:
            removed = KeyringCacheHandler(client_id).clear()
        except TokenStorageError as exc:
            messagebox.showerror("Keychain error", str(exc), parent=self.root)
            return
        message = "Saved login removed." if removed else "No saved login was found."
        self.status.set(message)
        self.status_label.configure(fg=self.SUCCESS)
        self._append_log(message)

    def _poll_messages(self):
        try:
            while True:
                kind, values = self.messages.get_nowait()
                if kind == "log":
                    self._append_log(values[0])
                elif kind == "status":
                    self.status.set(values[0])
                elif kind == "done":
                    success, message = values
                    self.running = False
                    self.progress.stop()
                    self.start_button.configure(state="normal")
                    self.forget_button.configure(state="normal")
                    self.status.set(message)
                    self.status_label.configure(
                        fg=self.SUCCESS if success else self.ERROR
                    )
                    self._append_log("")
                    self._append_log(message)
                    if not success:
                        messagebox.showerror("Spotify operation failed", message)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_messages)

    def _on_close(self):
        if self.running and not messagebox.askyesno(
            "Close application",
            "A Spotify operation is still running. Close anyway?",
            parent=self.root,
        ):
            return
        self.root.destroy()


def main():
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    DesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
