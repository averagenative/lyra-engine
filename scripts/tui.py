#!/usr/bin/env python3
"""Lyra Engine — Terminal UI for browsing the lyrics database."""

import sys
import os

# Add scripts dir to path so imports work when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, Static

from config import DATABASE_ROOT
from markdown import read_md


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_artists() -> list[dict]:
    """Return a sorted list of artist dicts with name, genre, path."""
    artists = []
    if not DATABASE_ROOT.exists():
        return artists
    for entry in sorted(DATABASE_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        artist_md = entry / "_artist.md"
        if not artist_md.exists():
            continue
        fm, _ = read_md(artist_md)
        artists.append({
            "name": fm.get("name", entry.name),
            "genre": fm.get("genre", ""),
            "mood": fm.get("mood", ""),
            "path": entry,
        })
    return artists


def load_albums(artist_path: Path) -> list[dict]:
    """Return sorted album dicts for an artist directory."""
    albums = []
    for entry in sorted(artist_path.iterdir()):
        if not entry.is_dir():
            continue
        album_md = entry / "_album.md"
        if album_md.exists():
            fm, _ = read_md(album_md)
            albums.append({
                "title": fm.get("title", entry.name),
                "year": fm.get("year", ""),
                "path": entry,
            })
        else:
            # Directory exists but no _album.md — use folder name
            albums.append({
                "title": entry.name,
                "year": "",
                "path": entry,
            })
    return albums


def load_tracks(album_path: Path) -> list[dict]:
    """Return sorted track dicts for an album directory."""
    tracks = []
    for entry in sorted(album_path.iterdir()):
        if entry.name.startswith("_") or not entry.suffix == ".md":
            continue
        fm, body = read_md(entry)
        has_lyrics = body.strip() not in ("", "[Lyrics not found]")
        tracks.append({
            "title": fm.get("title", entry.stem),
            "track_number": fm.get("track_number", 0),
            "has_lyrics": has_lyrics,
            "path": entry,
        })
    tracks.sort(key=lambda t: t["track_number"])
    return tracks


def compute_stats() -> dict:
    """Count total artists, songs, and songs with lyrics."""
    artist_count = 0
    song_count = 0
    lyrics_count = 0
    if not DATABASE_ROOT.exists():
        return {"artists": 0, "songs": 0, "with_lyrics": 0}
    for artist_dir in DATABASE_ROOT.iterdir():
        if not artist_dir.is_dir():
            continue
        if not (artist_dir / "_artist.md").exists():
            continue
        artist_count += 1
        for album_dir in artist_dir.iterdir():
            if not album_dir.is_dir():
                continue
            for song_file in album_dir.iterdir():
                if song_file.name.startswith("_") or song_file.suffix != ".md":
                    continue
                song_count += 1
                _, body = read_md(song_file)
                if body.strip() not in ("", "[Lyrics not found]"):
                    lyrics_count += 1
    return {"artists": artist_count, "songs": song_count, "with_lyrics": lyrics_count}


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------

class SongView(Static):
    """Display song frontmatter and lyrics."""

    def show_song(self, song_path: Path) -> None:
        fm, body = read_md(song_path)
        lines = []
        lines.append(f"[bold]{fm.get('title', '?')}[/bold]")
        lines.append(f"[dim]by[/dim] {fm.get('artist', '?')}")
        lines.append(f"[dim]from[/dim] {fm.get('album', '?')} ({fm.get('year', '?')})")
        lines.append("")

        # Tags section
        tag_fields = [
            ("Genre", "genre"),
            ("Mood", "mood"),
            ("Themes", "themes"),
            ("Style", "style"),
            ("Energy", "energy"),
        ]
        for label, key in tag_fields:
            val = fm.get(key, "")
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val) if val else ""
            if val:
                lines.append(f"[bold]{label}:[/bold] {val}")

        lines.append("")
        lines.append("[dim]" + "\u2500" * 40 + "[/dim]")
        lines.append("")
        lines.append(body)

        self.update("\n".join(lines))

    def show_placeholder(self, text: str = "Select a song to view lyrics.") -> None:
        self.update(f"[dim]{text}[/dim]")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class LyricsApp(App):
    """Lyra Engine TUI."""

    CSS = """
    #main {
        height: 1fr;
    }
    #sidebar {
        width: 36;
        border-right: solid $accent;
    }
    #sidebar-list {
        height: 1fr;
    }
    #content {
        width: 1fr;
        padding: 1 2;
    }
    #filter-input {
        dock: top;
    }
    #stats-bar {
        dock: bottom;
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    ListView {
        height: 1fr;
    }
    ListItem {
        padding: 0 1;
    }
    ListItem Label {
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("q", "quit", "Quit"),
    ]

    # Reactive state
    view_level = reactive("artists")  # artists | albums | tracks
    current_artist_path: Path | None = None
    current_album_path: Path | None = None

    def __init__(self):
        super().__init__()
        self._all_artists = load_artists()
        self._stats = compute_stats()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="Filter artists (or genre:tag)...", id="filter-input")
        with Horizontal(id="main"):
            with Vertical(id="sidebar"):
                yield ListView(id="sidebar-list")
            with VerticalScroll(id="content"):
                yield SongView(id="song-view")
        yield Static(self._stats_text(), id="stats-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._populate_artist_list(self._all_artists)
        self.query_one(SongView).show_placeholder()

    # -- Stats ---------------------------------------------------------------

    def _stats_text(self) -> str:
        s = self._stats
        return (
            f" Artists: {s['artists']}  |  "
            f"Songs: {s['songs']}  |  "
            f"With lyrics: {s['with_lyrics']}"
        )

    # -- List population -----------------------------------------------------

    def _populate_artist_list(self, artists: list[dict]) -> None:
        lv = self.query_one("#sidebar-list", ListView)
        lv.clear()
        for a in artists:
            item = ListItem(Label(a["name"]))
            item.data = a  # type: ignore[attr-defined]
            lv.mount(item)
        self.view_level = "artists"

    def _populate_album_list(self, artist_path: Path) -> None:
        albums = load_albums(artist_path)
        lv = self.query_one("#sidebar-list", ListView)
        lv.clear()
        for a in albums:
            display = f"{a['year']} - {a['title']}" if a["year"] else a["title"]
            item = ListItem(Label(display))
            item.data = a  # type: ignore[attr-defined]
            lv.mount(item)
        self.current_artist_path = artist_path
        self.view_level = "albums"

    def _populate_track_list(self, album_path: Path) -> None:
        tracks = load_tracks(album_path)
        lv = self.query_one("#sidebar-list", ListView)
        lv.clear()
        for t in tracks:
            marker = "+" if t["has_lyrics"] else "-"
            display = f"[{marker}] {t['track_number']:02d}. {t['title']}"
            item = ListItem(Label(display))
            item.data = t  # type: ignore[attr-defined]
            lv.mount(item)
        self.current_album_path = album_path
        self.view_level = "tracks"

    # -- Events --------------------------------------------------------------

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        data = getattr(item, "data", None)
        if data is None:
            return

        if self.view_level == "artists":
            self._populate_album_list(data["path"])
            self.query_one(SongView).show_placeholder("Select an album.")
        elif self.view_level == "albums":
            self._populate_track_list(data["path"])
            self.query_one(SongView).show_placeholder("Select a track.")
        elif self.view_level == "tracks":
            self.query_one(SongView).show_song(data["path"])

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.strip().lower()

        # Only filter when at artist level
        if self.view_level != "artists":
            return

        if query.startswith("genre:"):
            genre_q = query[len("genre:"):].strip()
            filtered = [
                a for a in self._all_artists
                if genre_q in a["genre"].lower()
            ]
        else:
            filtered = [
                a for a in self._all_artists
                if query in a["name"].lower()
            ]
        self._populate_artist_list(filtered)

    def action_go_back(self) -> None:
        if self.view_level == "tracks" and self.current_artist_path:
            self._populate_album_list(self.current_artist_path)
            self.query_one(SongView).show_placeholder("Select an album.")
        elif self.view_level == "albums":
            self._populate_artist_list(self._all_artists)
            self.query_one(SongView).show_placeholder()
        # At artist level, escape does nothing extra


if __name__ == "__main__":
    app = LyricsApp()
    app.run()
