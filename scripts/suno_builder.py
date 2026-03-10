#!/usr/bin/env python3
"""Suno Prompt Builder — Interactive TUI for constructing Suno style prompts.

Build prompts by selecting artists, albums, and songs from the database.
The builder reads metadata (genre, mood, energy, style, suno_style_description)
and assembles a Suno-compatible style prompt with live preview.

Key bindings (when not typing in a field):
  c  Copy prompt to clipboard
  e  Save prompt to sessions/ folder as a text file
  x  Clear all selections and fields
  q  Quit
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add scripts dir to path so imports work when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, Static

from config import DATABASE_ROOT, PROJECT_ROOT
from markdown import read_md

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUNO_CHAR_LIMIT = 1000
SUNO_WORD_LIMIT = 180
SESSIONS_DIR = PROJECT_ROOT / "sessions"

MOOD_OPTIONS = [
    "aggressive", "angry", "atmospheric", "bleak", "brooding", "cathartic",
    "cold", "dark", "defiant", "dreamy", "energetic", "euphoric", "haunting",
    "heavy", "hopeful", "introspective", "melancholic", "menacing", "mournful",
    "nostalgic", "peaceful", "playful", "raw", "restless", "somber",
    "triumphant", "vulnerable",
]

ENERGY_OPTIONS = [
    "building", "constant-high", "constant-low", "dynamic", "explosive",
    "fading", "rolling", "steady-mid",
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_full_db() -> list[dict]:
    """Load all artists with their albums and metadata."""
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
        artist = {
            "name": fm.get("name", entry.name),
            "genre": fm.get("genre", ""),
            "mood": fm.get("mood", ""),
            "suno_style": fm.get("suno_style_description", ""),
            "tags": fm.get("musicbrainz_tags", []),
            "path": entry,
            "albums": [],
        }
        # Load albums
        for adir in sorted(entry.iterdir()):
            if not adir.is_dir():
                continue
            album_md = adir / "_album.md"
            if not album_md.exists():
                continue
            afm, _ = read_md(album_md)
            album = {
                "title": afm.get("title", adir.name),
                "year": afm.get("year", ""),
                "genre": afm.get("genre", ""),
                "mood": afm.get("mood", ""),
                "suno_style": afm.get("suno_style_description", ""),
                "path": adir,
            }
            artist["albums"].append(album)
        artists.append(artist)
    return artists


def collect_genres(artists: list[dict]) -> list[str]:
    """Unique genres across all artists."""
    genres = set()
    for a in artists:
        for g in a["genre"].split(","):
            g = g.strip()
            if g:
                genres.add(g)
    return sorted(genres)


def collect_moods(artists: list[dict]) -> list[str]:
    """Unique moods across all artists + standard vocabulary."""
    moods = set(MOOD_OPTIONS)
    for a in artists:
        for m in a["mood"].split(","):
            m = m.strip()
            if m:
                moods.add(m)
    return sorted(moods)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True on success."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        pass
    for cmd in [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"],
                ["wl-copy"], ["clip.exe"]]:
        try:
            proc = subprocess.run(cmd, input=text.encode(), capture_output=True, timeout=3)
            if proc.returncode == 0:
                return True
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired, OSError):
            continue
    return False


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------

class PromptPreview(Static):
    """Live prompt preview with char/word counts and action hints."""

    def update_preview(self, prompt: str, selections: dict) -> None:
        char_count = len(prompt)
        word_count = len(prompt.split()) if prompt.strip() else 0

        char_color = "green" if char_count <= SUNO_CHAR_LIMIT else "red"
        word_color = "green" if word_count <= SUNO_WORD_LIMIT else "red"

        lines = [
            "[bold underline]Suno Style Prompt[/bold underline]",
            "",
            f"[{char_color}]{char_count}[/{char_color}]/{SUNO_CHAR_LIMIT} chars  |  "
            f"[{word_color}]{word_count}[/{word_color}]/{SUNO_WORD_LIMIT} words",
            "",
        ]

        # Show what's selected
        if selections.get("artists"):
            lines.append(f"[bold]Artists:[/bold] {', '.join(selections['artists'])}")
        if selections.get("albums"):
            lines.append(f"[bold]Albums:[/bold] {', '.join(selections['albums'])}")
        if selections.get("artists") or selections.get("albums"):
            lines.append("")

        lines.append("[dim]" + "\u2500" * 48 + "[/dim]")
        lines.append("")

        if prompt.strip():
            lines.append(prompt)
        else:
            lines.append(
                "[dim]Select artists/albums from the left panel, then\n"
                "adjust genre, mood, and other fields below.\n\n"
                "The prompt auto-builds from your selections + fields.[/dim]"
            )

        lines.append("")
        lines.append("[dim]" + "\u2500" * 48 + "[/dim]")
        lines.append("")
        lines.append(
            "[bold cyan]c[/bold cyan] Copy to clipboard    "
            "[bold cyan]e[/bold cyan] Save to sessions/    "
            "[bold cyan]x[/bold cyan] Clear all    "
            "[bold cyan]q[/bold cyan] Quit"
        )
        lines.append("")
        lines.append(
            "[dim]Copy puts the prompt text on your clipboard for pasting into Suno.\n"
            "Save writes a timestamped file to sessions/ with the prompt + your settings.[/dim]"
        )

        self.update("\n".join(lines))


class SelectionInfo(Static):
    """Shows metadata about selected artist/album."""

    def show_artist(self, artist: dict) -> None:
        lines = [
            f"[bold]{artist['name']}[/bold]",
            "",
        ]
        if artist["genre"]:
            lines.append(f"[bold]Genre:[/bold] {artist['genre']}")
        if artist["mood"]:
            lines.append(f"[bold]Mood:[/bold] {artist['mood']}")
        if artist["suno_style"]:
            lines.append("")
            lines.append("[bold]Suno Style Description:[/bold]")
            # Wrap long descriptions
            desc = artist["suno_style"]
            lines.append(f"[dim]{desc}[/dim]")
        if artist["albums"]:
            lines.append("")
            lines.append(f"[bold]Albums:[/bold] {len(artist['albums'])}")
            for alb in artist["albums"][:8]:
                lines.append(f"  {alb['year']} - {alb['title']}")
            if len(artist["albums"]) > 8:
                lines.append(f"  [dim]... and {len(artist['albums']) - 8} more[/dim]")

        lines.append("")
        lines.append("[dim]Enter: toggle select  |  Escape: back[/dim]")
        self.update("\n".join(lines))

    def show_album(self, album: dict) -> None:
        lines = [
            f"[bold]{album['title']}[/bold] ({album.get('year', '?')})",
            "",
        ]
        if album.get("genre"):
            lines.append(f"[bold]Genre:[/bold] {album['genre']}")
        if album.get("mood"):
            lines.append(f"[bold]Mood:[/bold] {album['mood']}")
        if album.get("suno_style"):
            lines.append("")
            lines.append("[bold]Suno Style Description:[/bold]")
            lines.append(f"[dim]{album['suno_style']}[/dim]")
        lines.append("")
        lines.append("[dim]Enter: toggle select  |  Escape: back[/dim]")
        self.update("\n".join(lines))

    def show_empty(self) -> None:
        self.update("[dim]Select an artist to see details.[/dim]")


class FieldLabel(Static):
    """A styled label for a form field."""


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class SunoBuilderApp(App):
    """Suno Prompt Builder — build prompts from your database."""

    TITLE = "Suno Prompt Builder"

    CSS = """
    #main-layout {
        height: 1fr;
    }

    /* Left: browser panel */
    #browser-panel {
        width: 30;
        border-right: solid $accent;
    }
    #browser-filter {
        dock: top;
    }
    #browser-list {
        height: 1fr;
    }

    /* Middle: info + form */
    #middle-panel {
        width: 1fr;
        border-right: solid $accent;
    }
    #selection-info {
        height: auto;
        max-height: 40%;
        padding: 1 2;
        border-bottom: solid $surface;
    }
    #form-area {
        height: 1fr;
        padding: 1 2;
    }
    .field-label {
        margin-top: 1;
        color: $accent;
    }
    .field-hint {
        color: $text-muted;
        margin-bottom: 0;
    }
    Input {
        margin-bottom: 0;
    }

    /* Right: preview */
    #preview-panel {
        width: 42%;
        padding: 1 2;
    }
    PromptPreview {
        width: 100%;
        height: auto;
    }

    /* Status */
    #status-bar {
        dock: bottom;
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }

    /* List styling */
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
        Binding("c", "copy_prompt", "Copy to clipboard", priority=True),
        Binding("e", "export_prompt", "Save to sessions/", priority=True),
        Binding("x", "clear_all", "Clear all", priority=True),
        Binding("escape", "go_back", "Back"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self._db = load_full_db()
        self._db_genres = collect_genres(self._db)
        self._db_moods = collect_moods(self._db)

        # Selection state
        self._selected_artists: list[dict] = []  # Artist dicts
        self._selected_albums: list[dict] = []   # Album dicts

        # Browser state: "artists" or "albums"
        self._browser_level = "artists"
        self._browsing_artist: dict | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main-layout"):
            # Left: artist/album browser
            with Vertical(id="browser-panel"):
                yield Input(placeholder="Filter...", id="browser-filter")
                yield ListView(id="browser-list")

            # Middle: selection info + form fields
            with Vertical(id="middle-panel"):
                yield SelectionInfo(id="selection-info")
                with VerticalScroll(id="form-area"):
                    yield FieldLabel("[bold]Genre(s)[/bold]", classes="field-label")
                    yield Label(
                        f"[dim]{', '.join(self._db_genres[:10])}{'...' if len(self._db_genres) > 10 else ''}[/dim]",
                        classes="field-hint",
                    )
                    yield Input(placeholder="auto-filled from selection, or type custom", id="genre-input")

                    yield FieldLabel("[bold]Mood(s)[/bold]", classes="field-label")
                    yield Label(
                        f"[dim]{', '.join(MOOD_OPTIONS[:8])}...[/dim]",
                        classes="field-hint",
                    )
                    yield Input(placeholder="auto-filled from selection, or type custom", id="mood-input")

                    yield FieldLabel("[bold]Energy[/bold]", classes="field-label")
                    yield Label(f"[dim]{', '.join(ENERGY_OPTIONS)}[/dim]", classes="field-hint")
                    yield Input(placeholder="e.g. building, explosive", id="energy-input")

                    yield FieldLabel("[bold]Instruments[/bold]", classes="field-label")
                    yield Input(placeholder="e.g. downtuned guitars, analog synths", id="instruments-input")

                    yield FieldLabel("[bold]Vocal Style[/bold]", classes="field-label")
                    yield Input(placeholder="e.g. deep baritone, strained. blank = instrumental", id="vocals-input")

                    yield FieldLabel("[bold]Structure[/bold]", classes="field-label")
                    yield Input(placeholder="e.g. long intro, breakdown at 2:00", id="structure-input")

                    yield FieldLabel("[bold]Production[/bold]", classes="field-label")
                    yield Input(placeholder="e.g. lo-fi texture, 95 BPM, warm analog", id="production-input")

            # Right: live preview
            with VerticalScroll(id="preview-panel"):
                yield PromptPreview(id="prompt-preview")

        yield Static("Tab: next field | Enter: select | Esc: back | c: copy | e: save | x: clear", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._populate_artist_browser()
        if not self._db:
            self.query_one(SelectionInfo).update(
                "[bold yellow]No artists in the database yet.[/bold yellow]\n\n"
                "Fetch some data first:\n\n"
                "  [bold cyan]python3 scripts/fetch.py artist \"Deftones\"[/bold cyan]\n"
                "  [bold cyan]python3 scripts/fetch.py artist \"Crowbar\"[/bold cyan]\n\n"
                "Then relaunch the prompt builder."
            )
        else:
            self.query_one(SelectionInfo).show_empty()
        self._refresh_preview()

    # -- Browser population --------------------------------------------------

    def _populate_artist_browser(self, filter_text: str = "") -> None:
        """Show artist list, with selection markers."""
        self._browser_level = "artists"
        lv = self.query_one("#browser-list", ListView)
        lv.clear()

        selected_names = {a["name"] for a in self._selected_artists}
        q = filter_text.lower()

        for artist in self._db:
            if q and q not in artist["name"].lower() and q not in artist["genre"].lower():
                continue
            marker = "[green]*[/green] " if artist["name"] in selected_names else "  "
            genre_hint = f" [dim]{artist['genre'].split(',')[0].strip()}[/dim]" if artist["genre"] else ""
            item = ListItem(Label(f"{marker}{artist['name']}{genre_hint}"))
            item.data = artist  # type: ignore[attr-defined]
            lv.mount(item)

    def _populate_album_browser(self, artist: dict) -> None:
        """Show albums for a specific artist."""
        self._browser_level = "albums"
        self._browsing_artist = artist
        lv = self.query_one("#browser-list", ListView)
        lv.clear()

        # Back item
        back_item = ListItem(Label("[dim]<< Back to artists[/dim]"))
        back_item.data = {"_back": True}  # type: ignore[attr-defined]
        lv.mount(back_item)

        selected_titles = {f"{a['title']}" for a in self._selected_albums}
        for album in artist["albums"]:
            marker = "[green]*[/green] " if album["title"] in selected_titles else "  "
            display = f"{marker}{album.get('year', '?')} - {album['title']}"
            item = ListItem(Label(display))
            item.data = album  # type: ignore[attr-defined]
            lv.mount(item)

    # -- Selection management ------------------------------------------------

    def _toggle_artist(self, artist: dict) -> None:
        """Toggle artist selection and auto-fill fields."""
        existing = [a for a in self._selected_artists if a["name"] == artist["name"]]
        if existing:
            self._selected_artists = [a for a in self._selected_artists if a["name"] != artist["name"]]
        else:
            self._selected_artists.append(artist)
        self._auto_fill_from_selection()
        # Refresh browser to show updated markers
        self._populate_artist_browser(self.query_one("#browser-filter", Input).value.strip())

    def _toggle_album(self, album: dict) -> None:
        """Toggle album selection."""
        existing = [a for a in self._selected_albums if a["title"] == album["title"]]
        if existing:
            self._selected_albums = [a for a in self._selected_albums if a["title"] != album["title"]]
        else:
            self._selected_albums.append(album)
        self._auto_fill_from_selection()
        if self._browsing_artist:
            self._populate_album_browser(self._browsing_artist)

    def _auto_fill_from_selection(self) -> None:
        """Auto-fill genre/mood from selected artists and albums."""
        genres = set()
        moods = set()

        for a in self._selected_artists:
            for g in a["genre"].split(","):
                g = g.strip()
                if g:
                    genres.add(g)
            for m in a["mood"].split(","):
                m = m.strip()
                if m:
                    moods.add(m)

        for alb in self._selected_albums:
            for g in alb.get("genre", "").split(","):
                g = g.strip()
                if g:
                    genres.add(g)
            for m in alb.get("mood", "").split(","):
                m = m.strip()
                if m:
                    moods.add(m)

        # Only auto-fill if the field is empty or was previously auto-filled
        genre_input = self.query_one("#genre-input", Input)
        mood_input = self.query_one("#mood-input", Input)

        if genres:
            genre_input.value = ", ".join(sorted(genres))
        if moods:
            mood_input.value = ", ".join(sorted(moods))

        self._refresh_preview()

    # -- Prompt building -----------------------------------------------------

    def _build_prompt(self) -> str:
        """Assemble Suno prompt from selections + field values."""
        parts: list[str] = []

        genre = self.query_one("#genre-input", Input).value.strip()
        mood = self.query_one("#mood-input", Input).value.strip()
        energy = self.query_one("#energy-input", Input).value.strip()
        instruments = self.query_one("#instruments-input", Input).value.strip()
        vocals = self.query_one("#vocals-input", Input).value.strip()
        structure = self.query_one("#structure-input", Input).value.strip()
        production = self.query_one("#production-input", Input).value.strip()

        # 1. Genre + mood identity block
        identity = []
        if genre:
            identity.append(genre)
        if mood:
            identity.append(mood)
        if energy:
            identity.append(f"{energy} energy")
        if identity:
            parts.append(", ".join(identity) + ".")

        # 2. Suno style descriptions from selected artists (translated to safe language)
        for artist in self._selected_artists:
            if artist["suno_style"]:
                parts.append(artist["suno_style"].rstrip(".") + ".")

        # 3. Album-level suno style descriptions
        for album in self._selected_albums:
            if album.get("suno_style"):
                parts.append(album["suno_style"].rstrip(".") + ".")

        # 4. Instrumentation
        if instruments:
            parts.append(instruments + ".")

        # 5. Vocals
        if vocals:
            parts.append(vocals + ".")

        # 6. Structure / dynamics
        if structure:
            parts.append(structure + ".")

        # 7. Production notes
        if production:
            parts.append(production + ".")

        prompt = " ".join(parts)
        prompt = prompt.replace("..", ".").replace(". .", ".")
        return prompt

    def _get_selections_summary(self) -> dict:
        return {
            "artists": [a["name"] for a in self._selected_artists],
            "albums": [f"{a.get('year', '?')} - {a['title']}" for a in self._selected_albums],
        }

    def _refresh_preview(self) -> None:
        prompt = self._build_prompt()
        selections = self._get_selections_summary()
        self.query_one("#prompt-preview", PromptPreview).update_preview(prompt, selections)

    # -- Events --------------------------------------------------------------

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        data = getattr(event.item, "data", None)
        if data is None:
            return

        # Back button
        if isinstance(data, dict) and data.get("_back"):
            self._populate_artist_browser(self.query_one("#browser-filter", Input).value.strip())
            self.query_one(SelectionInfo).show_empty()
            return

        if self._browser_level == "artists":
            # Enter on artist: drill into albums
            self.query_one(SelectionInfo).show_artist(data)
            self._toggle_artist(data)
        elif self._browser_level == "albums":
            self.query_one(SelectionInfo).show_album(data)
            self._toggle_album(data)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "browser-filter":
            if self._browser_level == "artists":
                self._populate_artist_browser(event.value.strip())
            return
        # Any form field change -> refresh preview
        self._refresh_preview()

    def action_go_back(self) -> None:
        if self._browser_level == "albums":
            self._populate_artist_browser(self.query_one("#browser-filter", Input).value.strip())
            self.query_one(SelectionInfo).show_empty()

    # -- Key bindings --------------------------------------------------------

    def _is_input_focused(self) -> bool:
        return isinstance(self.focused, Input)

    def action_copy_prompt(self) -> None:
        if self._is_input_focused():
            return
        prompt = self._build_prompt()
        if not prompt.strip():
            self._set_status("[yellow]Nothing to copy \u2014 select some artists first.[/yellow]")
            return
        if copy_to_clipboard(prompt):
            self._set_status("[green]Prompt copied to clipboard! Paste into Suno.[/green]")
        else:
            self._set_status("[red]Clipboard not available. Press e to save to file instead.[/red]")

    def action_export_prompt(self) -> None:
        if self._is_input_focused():
            return
        prompt = self._build_prompt()
        if not prompt.strip():
            self._set_status("[yellow]Nothing to save \u2014 select some artists first.[/yellow]")
            return

        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = SESSIONS_DIR / f"suno_prompt_{timestamp}.txt"

        lines = [
            "# Suno Style Prompt",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"# Characters: {len(prompt)} / {SUNO_CHAR_LIMIT}",
            f"# Words: {len(prompt.split())} / {SUNO_WORD_LIMIT}",
            "",
        ]

        # Selected references
        if self._selected_artists:
            lines.append("# --- Selected Artists ---")
            for a in self._selected_artists:
                lines.append(f"# {a['name']} ({a['genre']})")
            lines.append("")
        if self._selected_albums:
            lines.append("# --- Selected Albums ---")
            for a in self._selected_albums:
                lines.append(f"# {a.get('year', '?')} - {a['title']}")
            lines.append("")

        # Field values
        field_ids = [
            ("Genre", "genre-input"),
            ("Mood", "mood-input"),
            ("Energy", "energy-input"),
            ("Instruments", "instruments-input"),
            ("Vocals", "vocals-input"),
            ("Structure", "structure-input"),
            ("Production", "production-input"),
        ]
        lines.append("# --- Field Values ---")
        for label, fid in field_ids:
            val = self.query_one(f"#{fid}", Input).value.strip()
            if val:
                lines.append(f"# {label}: {val}")
        lines.append("")

        lines.append("# --- Prompt (paste this into Suno) ---")
        lines.append(prompt)
        lines.append("")

        filepath.write_text("\n".join(lines), encoding="utf-8")
        rel = filepath.relative_to(PROJECT_ROOT)
        self._set_status(f"[green]Saved to {rel} \u2014 prompt is at the bottom of the file.[/green]")

    def action_clear_all(self) -> None:
        if self._is_input_focused():
            return
        self._selected_artists.clear()
        self._selected_albums.clear()
        for widget in self.query(Input):
            widget.value = ""
        self._populate_artist_browser()
        self.query_one(SelectionInfo).show_empty()
        self._refresh_preview()
        self._set_status("Cleared all selections and fields.")

    def _set_status(self, text: str) -> None:
        self.query_one("#status-bar", Static).update(text)


if __name__ == "__main__":
    app = SunoBuilderApp()
    app.run()
