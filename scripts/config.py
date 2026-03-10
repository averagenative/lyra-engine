"""Path helpers, filename sanitization, and constants."""

import os
import re
from pathlib import Path

from slugify import slugify

# Project root is the parent of the scripts/ directory
DATABASE_ROOT = Path(__file__).resolve().parent.parent

# Rate limiting
GENIUS_SLEEP_SECONDS = 1.5

# Fuzzy match threshold for Genius title verification
FUZZY_MATCH_THRESHOLD = 0.7

# Characters illegal in filenames
_ILLEGAL_CHARS = re.compile(r'[<>:"/\\|?*]')


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use as a filename.

    Keeps spaces, capitalization, and unicode. Strips filesystem-illegal characters.
    Replaces ':' with ' -' before stripping.
    """
    name = name.replace(": ", " - ").replace(":", "-")
    name = _ILLEGAL_CHARS.sub("", name)
    name = name.strip(". ")
    return name


def artist_dir(artist_name: str) -> Path:
    return DATABASE_ROOT / sanitize_filename(artist_name)


def album_dir(artist_name: str, year: int, album_title: str) -> Path:
    album_folder = f"{year} - {sanitize_filename(album_title)}"
    return artist_dir(artist_name) / album_folder


def song_path(artist_name: str, year: int, album_title: str,
              track_number: int, song_title: str) -> Path:
    filename = f"{track_number:02d} - {sanitize_filename(song_title)}.md"
    return album_dir(artist_name, year, album_title) / filename
