#!/usr/bin/env python3
"""Suno Prompt Builder — Interactive TUI for constructing Suno style prompts."""

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
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Label, Static, TextArea

from config import DATABASE_ROOT, PROJECT_ROOT
from markdown import read_md

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUNO_CHAR_LIMIT = 1000
SUNO_WORD_LIMIT = 180

SESSIONS_DIR = PROJECT_ROOT / "sessions"

# Moods from ENRICHMENT_VOCABULARY.md
MOOD_OPTIONS = [
    "aggressive", "angry", "atmospheric", "bleak", "brooding", "cathartic",
    "cold", "dark", "defiant", "dreamy", "energetic", "euphoric", "haunting",
    "heavy", "hopeful", "introspective", "melancholic", "menacing", "mournful",
    "nostalgic", "peaceful", "playful", "raw", "restless", "somber",
    "triumphant", "vulnerable",
]

# Energy levels from ENRICHMENT_VOCABULARY.md
ENERGY_OPTIONS = [
    "building", "constant-high", "constant-low", "dynamic", "explosive",
    "fading", "rolling", "steady-mid",
]


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_genres_from_db() -> list[str]:
    """Collect unique genres from _artist.md files."""
    genres = set()
    if not DATABASE_ROOT.exists():
        return []
    for entry in sorted(DATABASE_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        artist_md = entry / "_artist.md"
        if not artist_md.exists():
            continue
        fm, _ = read_md(artist_md)
        genre_str = fm.get("genre", "")
        if genre_str:
            for g in genre_str.split(","):
                g = g.strip()
                if g:
                    genres.add(g)
    return sorted(genres)


def load_artists_with_style() -> dict[str, dict]:
    """Return dict of artist name -> {genre, suno_style_description}."""
    artists = {}
    if not DATABASE_ROOT.exists():
        return artists
    for entry in sorted(DATABASE_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        artist_md = entry / "_artist.md"
        if not artist_md.exists():
            continue
        fm, _ = read_md(artist_md)
        name = fm.get("name", entry.name)
        artists[name] = {
            "genre": fm.get("genre", ""),
            "suno_style_description": fm.get("suno_style_description", ""),
        }
    return artists


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True on success."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        pass
    # Fallback: try xclip, xsel, or wl-copy
    for cmd in [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"], ["wl-copy"], ["clip.exe"]]:
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
    """Live preview of the constructed Suno prompt with stats."""

    def update_preview(self, prompt: str) -> None:
        char_count = len(prompt)
        word_count = len(prompt.split()) if prompt.strip() else 0

        char_color = "green" if char_count <= SUNO_CHAR_LIMIT else "red"
        word_color = "green" if word_count <= SUNO_WORD_LIMIT else "red"

        lines = []
        lines.append("[bold underline]Suno Style Prompt Preview[/bold underline]")
        lines.append("")
        lines.append(
            f"[{char_color}]{char_count}[/{char_color}]/{SUNO_CHAR_LIMIT} chars  |  "
            f"[{word_color}]{word_count}[/{word_color}]/{SUNO_WORD_LIMIT} words"
        )
        lines.append("")
        lines.append("[dim]" + "\u2500" * 44 + "[/dim]")
        lines.append("")

        if prompt.strip():
            lines.append(prompt)
        else:
            lines.append("[dim]Fill in the fields on the left to build your prompt.[/dim]")

        lines.append("")
        lines.append("[dim]" + "\u2500" * 44 + "[/dim]")
        lines.append("")
        lines.append("[dim]c[/dim] Copy  |  [dim]e[/dim] Export  |  [dim]x[/dim] Clear  |  [dim]q[/dim] Quit")

        self.update("\n".join(lines))


class FieldLabel(Static):
    """A styled label for a form field."""


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class SunoBuilderApp(App):
    """Suno Prompt Builder TUI."""

    TITLE = "Suno Prompt Builder"

    CSS = """
    #main {
        height: 1fr;
    }
    #form-panel {
        width: 50%;
        border-right: solid $accent;
        padding: 1 2;
    }
    #preview-panel {
        width: 50%;
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
    #status-bar {
        dock: bottom;
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    Input {
        margin-bottom: 0;
    }
    PromptPreview {
        width: 100%;
        height: auto;
    }
    """

    BINDINGS = [
        Binding("c", "copy_prompt", "Copy", priority=True),
        Binding("e", "export_prompt", "Export", priority=True),
        Binding("x", "clear_fields", "Clear", priority=True),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self._db_genres = load_genres_from_db()
        self._db_artists = load_artists_with_style()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main"):
            with VerticalScroll(id="form-panel"):
                # Genre
                yield FieldLabel("[bold]Genre(s)[/bold]", classes="field-label")
                yield Label(
                    f"[dim]Available: {', '.join(self._db_genres[:12])}{'...' if len(self._db_genres) > 12 else ''}[/dim]",
                    classes="field-hint",
                )
                yield Input(
                    placeholder="e.g. industrial rock, dark ambient",
                    id="genre-input",
                )

                # Mood
                yield FieldLabel("[bold]Mood(s)[/bold]", classes="field-label")
                yield Label(
                    f"[dim]{', '.join(MOOD_OPTIONS[:10])}...[/dim]",
                    classes="field-hint",
                )
                yield Input(
                    placeholder="e.g. brooding, atmospheric, raw",
                    id="mood-input",
                )

                # Energy
                yield FieldLabel("[bold]Energy Level[/bold]", classes="field-label")
                yield Label(
                    f"[dim]{', '.join(ENERGY_OPTIONS)}[/dim]",
                    classes="field-hint",
                )
                yield Input(
                    placeholder="e.g. building",
                    id="energy-input",
                )

                # Instruments
                yield FieldLabel("[bold]Instruments[/bold]", classes="field-label")
                yield Label(
                    "[dim]Specific instruments and tones[/dim]",
                    classes="field-hint",
                )
                yield Input(
                    placeholder="e.g. downtuned guitars, analog synths, pulsing sub-bass",
                    id="instruments-input",
                )

                # Vocal style
                yield FieldLabel("[bold]Vocal Style[/bold]", classes="field-label")
                yield Label(
                    "[dim]Type, delivery, effects. Leave blank for instrumental.[/dim]",
                    classes="field-hint",
                )
                yield Input(
                    placeholder="e.g. deep baritone, strained and distorted, close-mic'd",
                    id="vocals-input",
                )

                # Structure hints
                yield FieldLabel("[bold]Structure Hints[/bold]", classes="field-label")
                yield Label(
                    "[dim]Dynamic arc, section cues[/dim]",
                    classes="field-hint",
                )
                yield Input(
                    placeholder="e.g. long instrumental intro, breakdown at 2:00",
                    id="structure-input",
                )

                # Reference artists
                yield FieldLabel("[bold]Reference Artist(s)[/bold]", classes="field-label")
                yield Label(
                    f"[dim]DB: {', '.join(sorted(self._db_artists.keys())[:8])}{'...' if len(self._db_artists) > 8 else ''}[/dim]",
                    classes="field-hint",
                )
                yield Input(
                    placeholder="e.g. Nine Inch Nails, Portishead",
                    id="reference-input",
                )

                # Production notes
                yield FieldLabel("[bold]Production Notes[/bold]", classes="field-label")
                yield Label(
                    "[dim]Tempo, texture, mix character[/dim]",
                    classes="field-hint",
                )
                yield Input(
                    placeholder="e.g. lo-fi texture, warm analog tone, 95 BPM",
                    id="production-input",
                )

            with VerticalScroll(id="preview-panel"):
                yield PromptPreview(id="prompt-preview")

        yield Static("Suno Prompt Builder | Tab between fields", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_preview()

    # -- Prompt building -----------------------------------------------------

    def _build_prompt(self) -> str:
        """Assemble the Suno style prompt from current field values.

        Follows the recommended order from SUNO_PROMPT_GUIDE.md:
        1. Genre + Era context
        2. Primary instrumentation
        3. Rhythm / energy
        4. Vocal description
        5. Energy movement / dynamics
        6. Production texture
        """
        parts: list[str] = []

        genre = self.query_one("#genre-input", Input).value.strip()
        mood = self.query_one("#mood-input", Input).value.strip()
        energy = self.query_one("#energy-input", Input).value.strip()
        instruments = self.query_one("#instruments-input", Input).value.strip()
        vocals = self.query_one("#vocals-input", Input).value.strip()
        structure = self.query_one("#structure-input", Input).value.strip()
        reference = self.query_one("#reference-input", Input).value.strip()
        production = self.query_one("#production-input", Input).value.strip()

        # 1. Genre + mood (identity block)
        identity_parts = []
        if genre:
            identity_parts.append(genre)
        if mood:
            identity_parts.append(mood)
        if energy:
            identity_parts.append(f"{energy} energy")
        if identity_parts:
            parts.append(", ".join(identity_parts) + ".")

        # 2. Reference artist descriptions (translated to Suno-safe language)
        if reference:
            ref_descriptions = self._resolve_references(reference)
            if ref_descriptions:
                parts.append(ref_descriptions)

        # 3. Instrumentation (palette block)
        if instruments:
            parts.append(instruments + ".")

        # 4. Vocals
        if vocals:
            parts.append(vocals + ".")
        elif not vocals:
            # If no vocal input given, don't add anything (user may want instrumental)
            pass

        # 5. Structure / dynamics
        if structure:
            parts.append(structure + ".")

        # 6. Production notes
        if production:
            parts.append(production + ".")

        prompt = " ".join(parts)
        # Clean up double periods
        prompt = prompt.replace("..", ".").replace(". .", ".")
        return prompt

    def _resolve_references(self, reference_text: str) -> str:
        """Look up reference artists in the DB and return their suno_style_description.

        If an artist is in the database with a suno_style_description, use that.
        Otherwise, include the name as-is (user may want to describe manually).
        """
        names = [n.strip() for n in reference_text.split(",") if n.strip()]
        descriptions = []

        for name in names:
            # Try exact match first, then case-insensitive
            matched = None
            if name in self._db_artists:
                matched = self._db_artists[name]
            else:
                for db_name, data in self._db_artists.items():
                    if db_name.lower() == name.lower():
                        matched = data
                        break

            if matched and matched["suno_style_description"]:
                descriptions.append(matched["suno_style_description"].rstrip("."))
            elif matched:
                # Artist in DB but no suno_style_description -- use genre
                genre = matched.get("genre", "")
                if genre:
                    descriptions.append(f"{genre} influence")

        if descriptions:
            return ". ".join(descriptions) + "."
        return ""

    def _refresh_preview(self) -> None:
        prompt = self._build_prompt()
        self.query_one("#prompt-preview", PromptPreview).update_preview(prompt)

    # -- Events --------------------------------------------------------------

    def on_input_changed(self, event: Input.Changed) -> None:
        self._refresh_preview()

    # -- Key bindings --------------------------------------------------------

    def _is_input_focused(self) -> bool:
        """Check if an Input widget currently has focus."""
        return isinstance(self.focused, Input)

    def action_copy_prompt(self) -> None:
        # If an Input is focused and user pressed 'c', type into it instead
        if self._is_input_focused():
            return
        prompt = self._build_prompt()
        if not prompt.strip():
            self._set_status("[yellow]Nothing to copy -- fill in some fields first.[/yellow]")
            return
        if copy_to_clipboard(prompt):
            self._set_status("[green]Copied to clipboard![/green]")
        else:
            self._set_status("[red]Clipboard not available. Use Export (e) instead.[/red]")

    def action_export_prompt(self) -> None:
        if self._is_input_focused():
            return
        prompt = self._build_prompt()
        if not prompt.strip():
            self._set_status("[yellow]Nothing to export -- fill in some fields first.[/yellow]")
            return

        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = SESSIONS_DIR / f"suno_prompt_{timestamp}.txt"

        # Build export content with metadata
        lines = []
        lines.append(f"# Suno Style Prompt")
        lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"# Characters: {len(prompt)} / {SUNO_CHAR_LIMIT}")
        lines.append(f"# Words: {len(prompt.split())} / {SUNO_WORD_LIMIT}")
        lines.append("")

        # Include field values for reference
        field_ids = [
            ("Genre", "genre-input"),
            ("Mood", "mood-input"),
            ("Energy", "energy-input"),
            ("Instruments", "instruments-input"),
            ("Vocals", "vocals-input"),
            ("Structure", "structure-input"),
            ("Reference", "reference-input"),
            ("Production", "production-input"),
        ]
        lines.append("# --- Field Values ---")
        for label, fid in field_ids:
            val = self.query_one(f"#{fid}", Input).value.strip()
            if val:
                lines.append(f"# {label}: {val}")
        lines.append("")
        lines.append("# --- Prompt ---")
        lines.append(prompt)
        lines.append("")

        filepath.write_text("\n".join(lines), encoding="utf-8")
        self._set_status(f"[green]Exported to {filepath.relative_to(PROJECT_ROOT)}[/green]")

    def action_clear_fields(self) -> None:
        if self._is_input_focused():
            return
        for widget in self.query(Input):
            widget.value = ""
        self._refresh_preview()
        self._set_status("Fields cleared.")

    def _set_status(self, text: str) -> None:
        self.query_one("#status-bar", Static).update(text)


if __name__ == "__main__":
    app = SunoBuilderApp()
    app.run()
