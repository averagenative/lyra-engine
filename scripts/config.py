"""Path helpers, filename sanitization, and constants."""

import os
import re
from pathlib import Path

from slugify import slugify

# Project root is the parent of the scripts/ directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# All artist data lives under artists/ subdirectory
DATABASE_ROOT = PROJECT_ROOT / "artists"

# Rate limiting
GENIUS_SLEEP_SECONDS = 1.5

# Fuzzy match threshold for Genius title verification
FUZZY_MATCH_THRESHOLD = 0.7

# Characters illegal in filenames
_ILLEGAL_CHARS = re.compile(r'[<>:"/\\|?*]')


# Max bytes for a single path component (ext4/most filesystems limit is 255)
_MAX_COMPONENT_BYTES = 255


def _truncate_to_bytes(name: str, max_bytes: int) -> str:
    """Truncate a string so its UTF-8 encoding fits within max_bytes.

    Truncates at character boundaries (never splits a multi-byte char).
    """
    encoded = name.encode("utf-8")
    if len(encoded) <= max_bytes:
        return name
    # Decode back, replacing the tail — this respects char boundaries
    truncated = encoded[:max_bytes].decode("utf-8", errors="ignore").rstrip()
    return truncated


def sanitize_filename(name: str, max_bytes: int = _MAX_COMPONENT_BYTES) -> str:
    """Sanitize a string for use as a filename.

    Keeps spaces, capitalization, and unicode. Strips filesystem-illegal characters.
    Replaces ':' with ' -' before stripping. Truncates to fit filesystem limits.
    """
    name = name.replace(": ", " - ").replace(":", "-")
    name = _ILLEGAL_CHARS.sub("", name)
    name = name.strip(". ")
    name = _truncate_to_bytes(name, max_bytes)
    return name


def artist_dir(artist_name: str) -> Path:
    return DATABASE_ROOT / sanitize_filename(artist_name)


def album_dir(artist_name: str, year: int, album_title: str) -> Path:
    prefix = f"{year} - "
    # Reserve bytes for the prefix so the album title fits
    max_title_bytes = _MAX_COMPONENT_BYTES - len(prefix.encode("utf-8"))
    album_folder = prefix + sanitize_filename(album_title, max_bytes=max_title_bytes)
    return artist_dir(artist_name) / album_folder


def song_path(artist_name: str, year: int, album_title: str,
              track_number: int, song_title: str) -> Path:
    prefix = f"{track_number:02d} - "
    suffix = ".md"
    # Reserve bytes for prefix and suffix
    max_title_bytes = (_MAX_COMPONENT_BYTES
                       - len(prefix.encode("utf-8"))
                       - len(suffix.encode("utf-8")))
    filename = prefix + sanitize_filename(song_title, max_bytes=max_title_bytes) + suffix
    return album_dir(artist_name, year, album_title) / filename
