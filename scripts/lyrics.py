"""Genius lyrics fetching with fuzzy title matching."""

import os
import sys
import time
from difflib import SequenceMatcher

import lyricsgenius

from config import DATABASE_ROOT, GENIUS_SLEEP_SECONDS, FUZZY_MATCH_THRESHOLD

_genius = None


def _load_dotenv():
    """Load .env file from project root if it exists."""
    env_path = DATABASE_ROOT / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def init_genius() -> lyricsgenius.Genius:
    """Initialize the Genius client. Reads GENIUS_API_TOKEN from env or .env file."""
    global _genius
    if _genius is not None:
        return _genius

    _load_dotenv()
    token = os.environ.get("GENIUS_API_TOKEN")
    if not token:
        print(
            "Error: GENIUS_API_TOKEN environment variable not set.\n"
            "Get a free token at: https://genius.com/api-clients",
            file=sys.stderr,
        )
        sys.exit(1)

    _genius = lyricsgenius.Genius(token, verbose=False, remove_section_headers=False)
    _genius.excluded_terms = ["(Remix)", "(Live)"]
    return _genius


def _normalize(text: str) -> str:
    """Normalize a string for fuzzy comparison."""
    import re
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def _title_matches(expected: str, actual: str) -> bool:
    """Check if the returned title is a fuzzy match for the expected title."""
    ratio = SequenceMatcher(None, _normalize(expected), _normalize(actual)).ratio()
    return ratio >= FUZZY_MATCH_THRESHOLD


def fetch_lyrics(artist: str, title: str) -> tuple[str | None, str | None]:
    """Fetch lyrics for a song.

    Returns (lyrics_text, genius_url) or (None, None) if not found.
    """
    genius = init_genius()

    try:
        song = genius.search_song(title, artist)
    except Exception as e:
        print(f"  Error fetching '{title}': {e}", file=sys.stderr)
        return None, None

    if song is None:
        return None, None

    # Verify the match
    if not _title_matches(title, song.title):
        print(
            f"  Skipping '{title}': Genius returned '{song.title}' (poor match)",
            file=sys.stderr,
        )
        return None, None

    lyrics = song.lyrics
    if lyrics:
        # Clean up: remove the song title header that lyricsgenius prepends
        lines = lyrics.split("\n")
        if lines and lines[0].strip().endswith("Lyrics"):
            lines = lines[1:]
        # Remove trailing "Embed" or number+Embed
        while lines and ("Embed" in lines[-1] or lines[-1].strip() == ""):
            lines.pop()
        # Remove trailing digit-only lines (e.g., "123Embed" leaves "123")
        while lines and lines[-1].strip().isdigit():
            lines.pop()
        lyrics = "\n".join(lines).strip()

        # Detect instrumentals
        lyrics_lower = lyrics.lower().replace(" ", "")
        if lyrics_lower in ("", "[instrumental]", "(instrumental)", "instrumental"):
            lyrics = "[Instrumental]"

    time.sleep(GENIUS_SLEEP_SECONDS)

    return lyrics or None, song.url
