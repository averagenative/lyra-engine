#!/usr/bin/env python3
"""Lyra Engine — Terminal UI for browsing the lyrics database."""

import subprocess
import sys
import os

# Add scripts dir to path so imports work when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Grid, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import (
    Footer, Header, Input, Label, ListItem, ListView, Static,
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
    """Count total artists, songs, songs with lyrics, and genre counts."""
    artist_count = 0
    song_count = 0
    lyrics_count = 0
    genres = {}
    if not DATABASE_ROOT.exists():
        return {"artists": 0, "songs": 0, "with_lyrics": 0, "genres": {}}
    for artist_dir in DATABASE_ROOT.iterdir():
        if not artist_dir.is_dir():
            continue
        if not (artist_dir / "_artist.md").exists():
            continue
        artist_count += 1
        fm, _ = read_md(artist_dir / "_artist.md")
        genre_str = fm.get("genre", "")
        if genre_str:
            for g in genre_str.split(","):
                g = g.strip()
                if g:
                    genres[g] = genres.get(g, 0) + 1
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
    return {
        "artists": artist_count,
        "songs": song_count,
        "with_lyrics": lyrics_count,
        "genres": genres,
    }


def lookup_artist_info(artist_name: str) -> dict | None:
    """Look up an artist in the database by name (case-insensitive)."""
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

LYRA_LOGO = """\
 _                        _____             _
| |   _   _ _ __ __ _    | ____|_ __   __ _(_)_ __   ___
| |  | | | | '__/ _` |   |  _| | '_ \\ / _` | | '_ \\ / _ \\
| |__| |_| | | | (_| |   | |___| | | | (_| | | | | |  __/
|_____\\__, |_|  \\__,_|   |_____|_| |_|\\__, |_|_| |_|\\___|
      |___/                            |___/"""


class HomeScreen(Static):
    """Splash/home screen with logo, stats, and menu."""

    def render_home(self, stats: dict) -> None:
        top_genres = sorted(stats.get("genres", {}).items(), key=lambda x: -x[1])[:6]
        genre_line = ", ".join(f"{g}" for g, _ in top_genres) if top_genres else "none yet"
        pct = (
            f"{stats['with_lyrics'] * 100 // stats['songs']}%"
            if stats["songs"] > 0
            else "N/A"
        )

        lines = [
            f"[bold cyan]{LYRA_LOGO}[/bold cyan]",
            "",
            f"[dim]A lyrics & style reference engine for AI music production[/dim]",
            "",
            f"[dim]{'─' * 58}[/dim]",
            "",
            f"  [bold]Database[/bold]",
            f"    Artists:  [bold]{stats['artists']}[/bold]",
            f"    Songs:    [bold]{stats['songs']}[/bold]  ({pct} with lyrics)",
            f"    Genres:   {genre_line}",
            "",
            f"[dim]{'─' * 58}[/dim]",
            "",
            "  [bold]Quick Actions[/bold]",
            "",
            "    [bold cyan]b[/bold cyan]  Browse       Artist / Album / Song browser with search",
            "    [bold cyan]s[/bold cyan]  Session      Start a songwriting session (7-question interview)",
            "    [bold cyan]p[/bold cyan]  Prompts      Launch the Suno prompt builder",
            "    [bold cyan]f[/bold cyan]  Find         Search songs by genre, mood, or keyword",
            "",
            f"[dim]{'─' * 58}[/dim]",
            "",
            "  [bold]CLI Commands[/bold]  [dim](run from terminal)[/dim]",
            "",
            "    [dim]fetch.py artist \"Name\"    Fetch full discography + lyrics",
            "    fetch.py missing --retry  Retry missing lyrics",
            "    fetch.py enrich --all     Enrich metadata for all songs",
            "    fetch.py similar \"Name\"   Find similar artists",
            "    fetch.py suggest          Suggest new artists to add",
            "    fetch.py discogs \"Name\"   Enrich from Discogs[/dim]",
            "",
            f"[dim]{'─' * 58}[/dim]",
            f"[dim]q quit  |  ? help  |  Tab between fields[/dim]",
        ]
        self.update("\n".join(lines))


class SongView(Static):
    """Display song frontmatter and lyrics."""

    def show_song(self, song_path: Path) -> None:
        fm, body = read_md(song_path)
        lines = []
        lines.append(f"[bold]{fm.get('title', '?')}[/bold]")
        lines.append(f"[dim]by[/dim] {fm.get('artist', '?')}")
        lines.append(f"[dim]from[/dim] {fm.get('album', '?')} ({fm.get('year', '?')})")
        lines.append("")

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


class SessionView(Static):
    """Display the session interview question or summary."""

    def show_question(self, question: dict, step: int, total: int) -> None:
        lines = [
            f"[bold]Songwriting Session[/bold]  \u2014  Question {step}/{total}",
            "",
            f"[bold]{question['label']}[/bold]",
            "",
            f"[dim]{question['prompt']}[/dim]",
        ]
        self.update("\n".join(lines))

    def show_summary(self, answers: dict, style_refs: list[dict]) -> None:
        lines = [
            "[bold]Songwriting Session \u2014 Summary[/bold]",
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
            raw = answers.get("reference_artists", "")
            if raw.strip():
                lines.append("")
                lines.append("[dim]No matching artists found in the database.[/dim]")

        lines.append("")
        lines.append("[dim]" + "\u2500" * 40 + "[/dim]")
        lines.append("[dim]Press [bold]e[/bold] to export  |  [bold]escape[/bold] to return home[/dim]")
        self.update("\n".join(lines))


class SearchResultsView(Static):
    """Display search results for the find/search mode."""

    def show_results(self, results: list[dict], query: str) -> None:
        if not results:
            self.update(f"[dim]No results for '{query}'[/dim]")
            return

        lines = [
            f"[bold]Search Results[/bold]  \u2014  {len(results)} matches for '{query}'",
            "",
        ]
        for r in results[:50]:  # Cap at 50 results
            marker = "[green]+[/green]" if r.get("has_lyrics") else "[red]-[/red]"
            lines.append(
                f"  {marker} [bold]{r['title']}[/bold]  "
                f"[dim]by[/dim] {r['artist']}  "
                f"[dim]from[/dim] {r['album']} ({r.get('year', '?')})"
            )
            meta_parts = []
            if r.get("genre"):
                meta_parts.append(f"genre:{r['genre']}")
            if r.get("mood"):
                meta_parts.append(f"mood:{r['mood']}")
            if r.get("energy"):
                meta_parts.append(f"energy:{r['energy']}")
            if meta_parts:
                lines.append(f"      [dim]{' | '.join(meta_parts)}[/dim]")

        if len(results) > 50:
            lines.append(f"\n  [dim]... and {len(results) - 50} more[/dim]")

        lines.append("")
        lines.append("[dim]Press [bold]escape[/bold] to return home[/dim]")
        self.update("\n".join(lines))


# ---------------------------------------------------------------------------
# Search helper
# ---------------------------------------------------------------------------

def search_songs(query: str) -> list[dict]:
    """Search songs across all artists by genre, mood, theme, or keyword."""
    results = []
    if not DATABASE_ROOT.exists():
        return results

    q = query.lower().strip()
    # Parse prefixed queries: genre:doom, mood:melancholic, energy:building, artist:sleep
    prefix = None
    if ":" in q:
        parts = q.split(":", 1)
        if parts[0] in ("genre", "mood", "energy", "style", "theme", "artist", "year"):
            prefix = parts[0]
            q = parts[1].strip()

    for artist_dir in sorted(DATABASE_ROOT.iterdir()):
        if not artist_dir.is_dir():
            continue
        if not (artist_dir / "_artist.md").exists():
            continue

        artist_fm, _ = read_md(artist_dir / "_artist.md")
        artist_name = artist_fm.get("name", artist_dir.name)

        # Artist-level filter
        if prefix == "artist":
            if q not in artist_name.lower():
                continue

        for album_dir in sorted(artist_dir.iterdir()):
            if not album_dir.is_dir():
                continue
            for song_file in sorted(album_dir.iterdir()):
                if song_file.name.startswith("_") or song_file.suffix != ".md":
                    continue
                fm, body = read_md(song_file)
                match = False

                if prefix == "genre":
                    match = q in fm.get("genre", "").lower()
                elif prefix == "mood":
                    match = q in fm.get("mood", "").lower()
                elif prefix == "energy":
                    match = q in fm.get("energy", "").lower()
                elif prefix == "style":
                    match = q in fm.get("style", "").lower()
                elif prefix == "theme":
                    themes = fm.get("themes", [])
                    if isinstance(themes, list):
                        match = any(q in t.lower() for t in themes)
                    else:
                        match = q in str(themes).lower()
                elif prefix == "year":
                    match = str(fm.get("year", "")) == q
                elif prefix == "artist":
                    match = True  # Already filtered at artist level
                else:
                    # General keyword search: title, lyrics, genre, mood, themes
                    match = (
                        q in fm.get("title", "").lower()
                        or q in fm.get("genre", "").lower()
                        or q in fm.get("mood", "").lower()
                        or q in body.lower()
                    )

                if match:
                    has_lyrics = body.strip() not in ("", "[Lyrics not found]")
                    results.append({
                        "title": fm.get("title", song_file.stem),
                        "artist": artist_name,
                        "album": fm.get("album", album_dir.name),
                        "year": fm.get("year", ""),
                        "genre": fm.get("genre", ""),
                        "mood": fm.get("mood", ""),
                        "energy": fm.get("energy", ""),
                        "has_lyrics": has_lyrics,
                        "path": song_file,
                    })

    return results


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class LyraApp(App):
    """Lyra Engine TUI."""

    TITLE = "Lyra Engine"

    CSS = """
    /* Home screen */
    #home-screen {
        height: 1fr;
        padding: 1 2;
    }

    /* Browser mode */
    #browser {
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

    /* Search/Find mode */
    #search-container {
        height: 1fr;
        padding: 1 2;
    }
    #search-input {
        dock: top;
    }
    #search-results {
        height: 1fr;
        padding: 1 2;
    }

    /* Status bar */
    #status-bar {
        dock: bottom;
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }

    /* Shared */
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
        Binding("b", "browse", "Browse", priority=True),
        Binding("s", "start_session", "Session", priority=True),
        Binding("p", "prompt_builder", "Prompts", priority=True),
        Binding("f", "find", "Find", priority=True),
        Binding("e", "export_session", "Export", show=False),
        Binding("escape", "go_back", "Back"),
        Binding("q", "quit", "Quit"),
        Binding("question_mark", "show_help", "Help", show=False),
    ]

    # Modes: home | browser | session | find
    current_mode = reactive("home")

    # Browser state
    view_level = reactive("artists")
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
        self._session_answers = {}
        self._session_style_refs = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Home screen
        with VerticalScroll(id="home-screen"):
            yield HomeScreen(id="home-view")

        # Browser mode
        yield Input(placeholder="Filter artists (or genre:tag)...", id="filter-input")
        with Horizontal(id="browser"):
            with Vertical(id="sidebar"):
                yield ListView(id="sidebar-list")
            with VerticalScroll(id="content"):
                yield SongView(id="song-view")

        # Session mode
        with VerticalScroll(id="session-container"):
            yield SessionView(id="session-view")
        yield Input(placeholder="", id="session-input")

        # Find/Search mode
        yield Input(
            placeholder="Search: genre:doom | mood:melancholic | artist:sleep | year:1997 | keyword...",
            id="search-input",
        )
        with VerticalScroll(id="search-container"):
            yield SearchResultsView(id="search-results")

        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._show_mode("home")
        self.query_one(HomeScreen).render_home(self._stats)
        self._populate_artist_list(self._all_artists)
        self._update_status()

    # -- Mode switching ------------------------------------------------------

    def _show_mode(self, mode: str) -> None:
        """Toggle visibility of all mode containers."""
        self.current_mode = mode

        # All containers
        widgets = {
            "home": ["#home-screen"],
            "browser": ["#filter-input", "#browser"],
            "session": ["#session-container", "#session-input"],
            "find": ["#search-input", "#search-container"],
        }

        # Hide everything
        for containers in widgets.values():
            for selector in containers:
                self.query_one(selector).display = False

        # Show the active mode
        for selector in widgets.get(mode, []):
            self.query_one(selector).display = True

        self._update_status()

    def _update_status(self) -> None:
        s = self._stats
        mode_label = self.current_mode.upper()
        bar = self.query_one("#status-bar", Static)
        bar.update(
            f" [{mode_label}]  "
            f"Artists: {s['artists']}  |  "
            f"Songs: {s['songs']}  |  "
            f"Lyrics: {s['with_lyrics']}  "
            f"[dim]|  b:browse  s:session  p:prompts  f:find  q:quit[/dim]"
        )

    # -- Actions: mode switches ----------------------------------------------

    def action_browse(self) -> None:
        if self._is_mode_input_focused():
            return
        self._session_active = False
        self._show_mode("browser")
        self.query_one(SongView).show_placeholder()
        self.query_one("#sidebar-list", ListView).focus()

    def action_start_session(self) -> None:
        if self._is_mode_input_focused():
            return
        self._session_step = 0
        self._session_answers = {}
        self._session_style_refs = []
        self._session_complete = False
        self._session_active = True
        self._show_mode("session")
        self._show_current_question()

    def action_prompt_builder(self) -> None:
        """Launch the Suno prompt builder as a subprocess."""
        if self._is_mode_input_focused():
            return
        builder_path = Path(__file__).parent / "suno_builder.py"
        if not builder_path.exists():
            self.notify("suno_builder.py not found", severity="error")
            return
        # Suspend and launch
        with self.suspend():
            subprocess.run([sys.executable, str(builder_path)])

    def action_find(self) -> None:
        if self._is_mode_input_focused():
            return
        self._session_active = False
        self._show_mode("find")
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
        search_input.focus()
        self.query_one(SearchResultsView).update(
            "[dim]Type a query above. Prefix with genre:, mood:, energy:, style:, "
            "theme:, artist:, or year: to filter by field.\n\n"
            "Examples:\n"
            "  genre:doom\n"
            "  mood:melancholic\n"
            "  artist:sleep\n"
            "  year:1997\n"
            "  darkness          (keyword search in title, genre, mood, lyrics)[/dim]"
        )

    def action_show_help(self) -> None:
        if self._is_mode_input_focused():
            return
        self._show_mode("home")
        self.query_one(HomeScreen).render_home(self._stats)

    def action_go_back(self) -> None:
        # Session -> home
        if self.current_mode == "session":
            self._session_active = False
            self._show_mode("home")
            self.query_one(HomeScreen).render_home(self._stats)
            return

        # Find -> home
        if self.current_mode == "find":
            self._show_mode("home")
            self.query_one(HomeScreen).render_home(self._stats)
            return

        # Browser: tracks -> albums -> artists -> home
        if self.current_mode == "browser":
            if self.view_level == "tracks" and self.current_artist_path:
                self._populate_album_list(self.current_artist_path)
                self.query_one(SongView).show_placeholder("Select an album.")
            elif self.view_level == "albums":
                self._populate_artist_list(self._all_artists)
                self.query_one(SongView).show_placeholder()
            else:
                # At artist level -> back to home
                self._show_mode("home")
                self.query_one(HomeScreen).render_home(self._stats)
            return

        # Home -> do nothing (q to quit)
        return

    # -- Helpers -------------------------------------------------------------

    def _is_mode_input_focused(self) -> bool:
        """Check if an Input widget has focus (don't intercept typing)."""
        return isinstance(self.focused, Input)

    # -- List population (browser) -------------------------------------------

    def _populate_artist_list(self, artists: list[dict]) -> None:
        lv = self.query_one("#sidebar-list", ListView)
        lv.clear()
        for a in artists:
            genre_hint = f"  [dim]{a['genre'].split(',')[0].strip()}[/dim]" if a["genre"] else ""
            item = ListItem(Label(f"{a['name']}{genre_hint}"))
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
            marker = "[green]+[/green]" if t["has_lyrics"] else "[red]-[/red]"
            display = f"{marker} {t['track_number']:02d}. {t['title']}"
            item = ListItem(Label(display))
            item.data = t  # type: ignore[attr-defined]
            lv.mount(item)
        self.current_album_path = album_path
        self.view_level = "tracks"

    # -- Session logic -------------------------------------------------------

    def _show_current_question(self) -> None:
        q = SESSION_QUESTIONS[self._session_step]
        sv = self.query_one("#session-view", SessionView)
        sv.show_question(q, self._session_step + 1, len(SESSION_QUESTIONS))
        inp = self.query_one("#session-input", Input)
        inp.value = ""
        inp.placeholder = q["prompt"]
        inp.focus()

    def _advance_session(self, value: str) -> None:
        key = SESSION_QUESTIONS[self._session_step]["key"]
        self._session_answers[key] = value.strip()
        self._session_step += 1

        if self._session_step < len(SESSION_QUESTIONS):
            self._show_current_question()
        else:
            self._finalize_session()

    def _finalize_session(self) -> None:
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
        self.query_one("#session-input").display = False

    def action_export_session(self) -> None:
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
        self.notify(f"Exported to {out_path.relative_to(PROJECT_ROOT)}")

    # -- Events --------------------------------------------------------------

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if self.current_mode != "browser":
            return
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
        # Session input
        if event.input.id == "session-input":
            if not self._session_active or self._session_complete:
                return
            value = event.value
            if not value.strip():
                return
            self._advance_session(value)
            return

        # Search input
        if event.input.id == "search-input":
            query = event.value.strip()
            if not query:
                return
            results = search_songs(query)
            self.query_one(SearchResultsView).show_results(results, query)
            return

    def on_input_changed(self, event: Input.Changed) -> None:
        # Only handle filter input for the browser
        if event.input.id != "filter-input":
            return
        if self.current_mode != "browser":
            return

        query = event.value.strip().lower()
        if self.view_level != "artists":
            return

        if query.startswith("genre:"):
            genre_q = query[len("genre:"):].strip()
            filtered = [
                a for a in self._all_artists
                if genre_q in a["genre"].lower()
            ]
        elif query.startswith("mood:"):
            mood_q = query[len("mood:"):].strip()
            filtered = [
                a for a in self._all_artists
                if mood_q in a["mood"].lower()
            ]
        else:
            filtered = [
                a for a in self._all_artists
                if query in a["name"].lower()
            ]
        self._populate_artist_list(filtered)


if __name__ == "__main__":
    app = LyraApp()
    app.run()
