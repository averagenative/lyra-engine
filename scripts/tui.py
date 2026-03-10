#!/usr/bin/env python3
"""Lyra Engine — Terminal UI for browsing the lyrics database."""

import sys
import os

# Add scripts dir to path so imports work when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import (
    Button, Footer, Header, Input, Label, ListItem, ListView, Static,
)

from config import DATABASE_ROOT, PROJECT_ROOT
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


def lookup_artist_info(artist_name: str) -> dict | None:
    """Look up an artist in the database by name (case-insensitive).

    Returns a dict with name, genre, suno_style_description, or None.
    """
    if not DATABASE_ROOT.exists():
        return None
    name_lower = artist_name.strip().lower()
    for entry in DATABASE_ROOT.iterdir():
        if not entry.is_dir():
            continue
        artist_md = entry / "_artist.md"
        if not artist_md.exists():
            continue
        fm, _ = read_md(artist_md)
        db_name = fm.get("name", entry.name)
        if db_name.lower() == name_lower:
            return {
                "name": db_name,
                "genre": fm.get("genre", ""),
                "suno_style_description": fm.get("suno_style_description", ""),
            }
    return None


# ---------------------------------------------------------------------------
# Session questions
# ---------------------------------------------------------------------------

SESSION_QUESTIONS = [
    {
        "key": "mood",
        "label": "Mood / Emotion",
        "prompt": "What emotional center? (e.g. defiant, melancholic, accusatory, quiet reflection)",
    },
    {
        "key": "aggression",
        "label": "Aggression Level",
        "prompt": "Sonic aggression 1-10 (or a trajectory like '2 -> 8')",
    },
    {
        "key": "structure",
        "label": "Structure",
        "prompt": "Song structure? (verse-chorus, through-composed, slow build, clean verse / chaotic chorus, etc.)",
    },
    {
        "key": "perspective",
        "label": "Perspective",
        "prompt": "Who is speaking? (1st person, 3rd person narrator, the observer, etc.)",
    },
    {
        "key": "themes",
        "label": "Themes",
        "prompt": "What is the song about? Key imagery or metaphors.",
    },
    {
        "key": "vocal_style",
        "label": "Vocal Style",
        "prompt": "Vocal approach? (clean, screamed, whispered, half-spoken, layered harmonies, etc.)",
    },
    {
        "key": "reference_artists",
        "label": "Reference Artists",
        "prompt": "Which database artists to draw from? (comma-separated)",
    },
]


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
# Songwriting Session Screen (inline, no Screen subclass)
# ---------------------------------------------------------------------------

class SessionView(Static):
    """Display the session interview question or summary."""

    def show_question(self, question: dict, step: int, total: int) -> None:
        lines = [
            f"[bold]Songwriting Session[/bold]  —  Question {step}/{total}",
            "",
            f"[bold]{question['label']}[/bold]",
            "",
            f"[dim]{question['prompt']}[/dim]",
        ]
        self.update("\n".join(lines))

    def show_summary(self, answers: dict, style_refs: list[dict]) -> None:
        lines = [
            "[bold]Songwriting Session — Summary[/bold]",
            "",
        ]
        display_labels = {q["key"]: q["label"] for q in SESSION_QUESTIONS}
        for q in SESSION_QUESTIONS:
            key = q["key"]
            val = answers.get(key, "")
            lines.append(f"[bold]{display_labels[key]}:[/bold] {val}")

        if style_refs:
            lines.append("")
            lines.append("[dim]" + "\u2500" * 40 + "[/dim]")
            lines.append("")
            lines.append("[bold]Style References[/bold]")
            for ref in style_refs:
                lines.append("")
                lines.append(f"  [bold]{ref['name']}[/bold]")
                if ref["genre"]:
                    lines.append(f"  Genre: {ref['genre']}")
                if ref["suno_style_description"]:
                    lines.append(f"  Suno style: {ref['suno_style_description']}")
                if not ref["genre"] and not ref["suno_style_description"]:
                    lines.append("  [dim](no additional info in database)[/dim]")
        else:
            # Check if any artists were entered but not found
            raw = answers.get("reference_artists", "")
            if raw.strip():
                lines.append("")
                lines.append("[dim]No matching artists found in the database.[/dim]")

        lines.append("")
        lines.append("[dim]" + "\u2500" * 40 + "[/dim]")
        lines.append("[dim]Press [bold]e[/bold] to export  |  [bold]escape[/bold] to return to browser[/dim]")
        self.update("\n".join(lines))


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
    /* Session mode */
    #session-container {
        height: 1fr;
        padding: 2 4;
    }
    #session-view {
        height: 1fr;
    }
    #session-input {
        dock: bottom;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("s", "start_session", "Session", priority=True),
        Binding("e", "export_session", "Export", show=False),
        Binding("q", "quit", "Quit"),
    ]

    # Reactive state
    view_level = reactive("artists")  # artists | albums | tracks
    current_artist_path: Path | None = None
    current_album_path: Path | None = None

    # Session state
    _session_active: bool = False
    _session_step: int = 0
    _session_answers: dict = {}
    _session_style_refs: list[dict] = []
    _session_complete: bool = False

    def __init__(self):
        super().__init__()
        self._all_artists = load_artists()
        self._stats = compute_stats()
        # Reinitialize mutable per-instance state
        self._session_answers = {}
        self._session_style_refs = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Browser mode widgets
        yield Input(placeholder="Filter artists (or genre:tag)...", id="filter-input")
        with Horizontal(id="main"):
            with Vertical(id="sidebar"):
                yield ListView(id="sidebar-list")
            with VerticalScroll(id="content"):
                yield SongView(id="song-view")

        # Session mode widgets (hidden initially)
        with VerticalScroll(id="session-container"):
            yield SessionView(id="session-view")
        yield Input(placeholder="", id="session-input")

        yield Static(self._stats_text(), id="stats-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._populate_artist_list(self._all_artists)
        self.query_one(SongView).show_placeholder()
        # Hide session widgets
        self.query_one("#session-container").display = False
        self.query_one("#session-input").display = False

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

    # -- Browser / Session toggle -------------------------------------------

    def _show_browser(self) -> None:
        """Switch to browser mode, hiding session widgets."""
        self.query_one("#filter-input").display = True
        self.query_one("#main").display = True
        self.query_one("#session-container").display = False
        self.query_one("#session-input").display = False
        self._session_active = False
        self._session_complete = False

    def _show_session(self) -> None:
        """Switch to session mode, hiding browser widgets."""
        self.query_one("#filter-input").display = False
        self.query_one("#main").display = False
        self.query_one("#session-container").display = True
        self.query_one("#session-input").display = True
        self._session_active = True

    # -- Session logic -------------------------------------------------------

    def action_start_session(self) -> None:
        """Begin a new songwriting session."""
        if self._session_active:
            return
        self._session_step = 0
        self._session_answers = {}
        self._session_style_refs = []
        self._session_complete = False
        self._show_session()
        self._show_current_question()

    def _show_current_question(self) -> None:
        """Display the current session question."""
        q = SESSION_QUESTIONS[self._session_step]
        sv = self.query_one("#session-view", SessionView)
        sv.show_question(q, self._session_step + 1, len(SESSION_QUESTIONS))
        inp = self.query_one("#session-input", Input)
        inp.value = ""
        inp.placeholder = q["prompt"]
        inp.focus()

    def _advance_session(self, value: str) -> None:
        """Record the current answer and move to the next question or summary."""
        key = SESSION_QUESTIONS[self._session_step]["key"]
        self._session_answers[key] = value.strip()
        self._session_step += 1

        if self._session_step < len(SESSION_QUESTIONS):
            self._show_current_question()
        else:
            self._finalize_session()

    def _finalize_session(self) -> None:
        """Build style references and show the session summary."""
        # Parse reference artists
        raw = self._session_answers.get("reference_artists", "")
        artist_names = [n.strip() for n in raw.split(",") if n.strip()]
        self._session_style_refs = []
        for name in artist_names:
            info = lookup_artist_info(name)
            if info:
                self._session_style_refs.append(info)

        self._session_complete = True
        sv = self.query_one("#session-view", SessionView)
        sv.show_summary(self._session_answers, self._session_style_refs)

        # Hide the input now that questions are done
        self.query_one("#session-input").display = False

    def action_export_session(self) -> None:
        """Export the completed session to a timestamped file."""
        if not self._session_active or not self._session_complete:
            return

        sessions_dir = PROJECT_ROOT / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = sessions_dir / f"session_{timestamp}.md"

        lines = [
            "# Songwriting Session",
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## Song Design Interview",
            "",
        ]
        for q in SESSION_QUESTIONS:
            key = q["key"]
            val = self._session_answers.get(key, "")
            lines.append(f"### {q['label']}")
            lines.append(val)
            lines.append("")

        if self._session_style_refs:
            lines.append("## Style References")
            lines.append("")
            for ref in self._session_style_refs:
                lines.append(f"### {ref['name']}")
                if ref["genre"]:
                    lines.append(f"- **Genre:** {ref['genre']}")
                if ref["suno_style_description"]:
                    lines.append(f"- **Suno style:** {ref['suno_style_description']}")
                lines.append("")

        out_path.write_text("\n".join(lines), encoding="utf-8")
        self.notify(f"Session exported to {out_path.relative_to(PROJECT_ROOT)}")

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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter in the session input."""
        if not self._session_active or self._session_complete:
            return
        if event.input.id != "session-input":
            return
        value = event.value
        if not value.strip():
            return
        self._advance_session(value)

    def on_input_changed(self, event: Input.Changed) -> None:
        # Only handle filter input for the browser
        if event.input.id != "filter-input":
            return

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
        # If in session mode, return to browser
        if self._session_active:
            self._show_browser()
            return

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
