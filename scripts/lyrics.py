"""Genius lyrics fetching with fuzzy title matching."""

import os
import sys
import time
from difflib import SequenceMatcher

import lyricsgenius

from config import GENIUS_SLEEP_SECONDS, FUZZY_MATCH_THRESHOLD

_genius = None


def init_genius() -> lyricsgenius.Genius:
    """Initialize the Genius client. Reads GENIUS_API_TOKEN from env."""
    global _genius
    if _genius is not None:
        return _genius

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
        if lines and ("Embed" in lines[-1]):
            lines = lines[:-1]
        lyrics = "\n".join(lines).strip()

    time.sleep(GENIUS_SLEEP_SECONDS)

    return lyrics or None, song.url
