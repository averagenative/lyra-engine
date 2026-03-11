#!/usr/bin/env python3
"""Lyra Engine MCP Server — expose the lyrics/style database to AI agents."""

import os
import sys
from pathlib import Path

# Add scripts dir to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP

from config import DATABASE_ROOT, PROJECT_ROOT, artist_dir, album_dir
from markdown import read_md, write_index
from enrich import (
    VALID_MOODS, VALID_STYLES, VALID_ENERGY, VALID_THEMES,
    iter_song_files, suggest_mood, suggest_themes, suggest_energy,
    suggest_style_from_context,
)

mcp = FastMCP(
    "lyra-engine",
    instructions=(
        "Lyra Engine is a file-based lyrics and style reference database for AI-assisted songwriting. "
        "Use these tools to browse artists, read lyrics, search by genre/mood/theme, "
        "generate Suno-compatible style prompts, and fetch new artists into the database."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _list_artist_dirs() -> list[Path]:
    """Return sorted list of artist directories that contain _artist.md."""
    if not DATABASE_ROOT.exists():
        return []
    return sorted(
        d for d in DATABASE_ROOT.iterdir()
        if d.is_dir() and (d / "_artist.md").exists()
    )


def _list_album_dirs(artist_path: Path) -> list[Path]:
    """Return sorted album directories for an artist."""
    return sorted(
        d for d in artist_path.iterdir()
        if d.is_dir() and (d / "_album.md").exists()
    )


def _list_song_files(album_path: Path) -> list[Path]:
    """Return sorted song files in an album directory."""
    return sorted(
        f for f in album_path.iterdir()
        if f.suffix == ".md" and f.name != "_album.md"
    )


def _find_artist_dir(name: str) -> Path | None:
    """Find an artist directory by case-insensitive match."""
    name_lower = name.lower()
    for d in _list_artist_dirs():
        fm, _ = read_md(d / "_artist.md")
        if fm.get("name", "").lower() == name_lower:
            return d
        if d.name.lower() == name_lower:
            return d
    return None


def _find_album_dir(artist_path: Path, album_query: str) -> Path | None:
    """Find an album directory by fuzzy name match."""
    query_lower = album_query.lower()
    for d in _list_album_dirs(artist_path):
        fm, _ = read_md(d / "_album.md")
        if query_lower in fm.get("title", "").lower():
            return d
        if query_lower in d.name.lower():
            return d
    return None


def _find_song_file(album_path: Path, song_query: str) -> Path | None:
    """Find a song file by title match."""
    query_lower = song_query.lower()
    for f in _list_song_files(album_path):
        fm, _ = read_md(f)
        if query_lower in fm.get("title", "").lower():
            return f
    return None


# ---------------------------------------------------------------------------
# Tools — Read/Browse
# ---------------------------------------------------------------------------

@mcp.tool()
def list_artists() -> str:
    """List all artists in the database with their primary genre and album count."""
    dirs = _list_artist_dirs()
    if not dirs:
        return "No artists in database. Use fetch_artist to add some."

    lines = []
    for d in dirs:
        fm, _ = read_md(d / "_artist.md")
        name = fm.get("name", d.name)
        genre = fm.get("genre", "")
        albums = fm.get("album_count", 0)
        country = fm.get("country", "")
        parts = [name]
        if genre:
            parts.append(f"[{genre.split(',')[0].strip()}]")
        if country:
            parts.append(f"({country})")
        parts.append(f"— {albums} albums")
        lines.append("  ".join(parts))

    return f"{len(lines)} artists:\n" + "\n".join(lines)


@mcp.tool()
def get_artist(name: str) -> str:
    """Get full artist metadata, style description, and discography listing.

    Args:
        name: Artist name (case-insensitive)
    """
    d = _find_artist_dir(name)
    if not d:
        return f"Artist '{name}' not found. Use list_artists to see available artists, or fetch_artist to add them."

    fm, body = read_md(d / "_artist.md")

    lines = [f"# {fm.get('name', name)}"]

    for key in ["genre", "mood", "country", "active_years", "suno_style_description"]:
        val = fm.get(key, "")
        if val:
            lines.append(f"**{key}**: {val}")

    members = fm.get("members", [])
    if members:
        lines.append(f"**members**: {', '.join(members)}")

    tags = fm.get("musicbrainz_tags", [])
    if tags:
        lines.append(f"**tags**: {', '.join(tags)}")

    # External links
    for key in ["allmusic_url", "lastfm_url", "discogs_url", "website"]:
        val = fm.get(key, "")
        if val:
            lines.append(f"**{key}**: {val}")

    lines.append("")
    lines.append(body)

    return "\n".join(lines)


@mcp.tool()
def get_album(artist: str, album: str) -> str:
    """Get album metadata and track listing.

    Args:
        artist: Artist name (case-insensitive)
        album: Album name or partial match
    """
    a_dir = _find_artist_dir(artist)
    if not a_dir:
        return f"Artist '{artist}' not found."

    al_dir = _find_album_dir(a_dir, album)
    if not al_dir:
        albums = _list_album_dirs(a_dir)
        names = [read_md(d / "_album.md")[0].get("title", d.name) for d in albums]
        return f"Album '{album}' not found for {artist}. Available: {', '.join(names)}"

    fm, body = read_md(al_dir / "_album.md")

    lines = [f"# {fm.get('title', album)} ({fm.get('year', '?')})"]
    for key in ["release_type", "genre", "mood", "track_count", "tracks_missing_lyrics"]:
        val = fm.get(key, "")
        if val:
            lines.append(f"**{key}**: {val}")

    lines.append("")
    lines.append(body)

    return "\n".join(lines)


@mcp.tool()
def get_song(artist: str, album: str, title: str) -> str:
    """Get a song's full lyrics and metadata.

    Args:
        artist: Artist name (case-insensitive)
        album: Album name or partial match
        title: Song title or partial match
    """
    a_dir = _find_artist_dir(artist)
    if not a_dir:
        return f"Artist '{artist}' not found."

    al_dir = _find_album_dir(a_dir, album)
    if not al_dir:
        return f"Album '{album}' not found for {artist}."

    song = _find_song_file(al_dir, title)
    if not song:
        songs = _list_song_files(al_dir)
        titles = [read_md(f)[0].get("title", f.stem) for f in songs]
        return f"Song '{title}' not found. Available: {', '.join(titles)}"

    fm, body = read_md(song)

    lines = [f"# {fm.get('title', title)}"]
    for key in ["artist", "album", "year", "track_number", "genre", "mood",
                "themes", "style", "energy"]:
        val = fm.get(key, "")
        if val and val != []:
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            lines.append(f"**{key}**: {val}")

    genius = fm.get("genius_url", "")
    if genius:
        lines.append(f"**genius_url**: {genius}")

    lines.append("")
    lines.append("## Lyrics")
    lines.append(body)

    return "\n".join(lines)


@mcp.tool()
def search_songs(
    artist: str = "",
    genre: str = "",
    mood: str = "",
    theme: str = "",
    energy: str = "",
    keyword: str = "",
    limit: int = 20,
) -> str:
    """Search songs by metadata fields or lyric keywords. All filters are AND-combined.

    Args:
        artist: Filter by artist name (partial match)
        genre: Filter by genre tag (partial match)
        mood: Filter by mood tag (partial match)
        theme: Filter by theme (partial match)
        energy: Filter by energy level (exact match)
        keyword: Search within lyrics text
        limit: Max results to return (default 20)
    """
    results = []

    for song_path, fm, body in _iter_all_songs():
        if artist and artist.lower() not in fm.get("artist", "").lower():
            continue
        if genre and genre.lower() not in fm.get("genre", "").lower():
            continue
        if mood and mood.lower() not in fm.get("mood", "").lower():
            continue
        if theme:
            themes = fm.get("themes", [])
            if isinstance(themes, list):
                theme_str = " ".join(str(t) for t in themes)
            else:
                theme_str = str(themes)
            if theme.lower() not in theme_str.lower():
                continue
        if energy and energy.lower() != fm.get("energy", "").lower():
            continue
        if keyword and keyword.lower() not in body.lower():
            continue

        results.append(fm)
        if len(results) >= limit:
            break

    if not results:
        return "No songs matched your search criteria."

    lines = [f"Found {len(results)} songs:"]
    for fm in results:
        title = fm.get("title", "?")
        art = fm.get("artist", "?")
        alb = fm.get("album", "?")
        year = fm.get("year", "?")
        g = fm.get("genre", "")
        m = fm.get("mood", "")
        line = f"- {art} — \"{title}\" ({alb}, {year})"
        if g:
            line += f" [{g}]"
        if m:
            line += f" {{{m}}}"
        lines.append(line)

    return "\n".join(lines)


def _iter_all_songs():
    """Yield (path, frontmatter, body) for every song in the database."""
    for a_dir in _list_artist_dirs():
        for al_dir in _list_album_dirs(a_dir):
            for song in _list_song_files(al_dir):
                fm, body = read_md(song)
                yield song, fm, body


@mcp.tool()
def get_stats() -> str:
    """Show database statistics: artist count, song count, genre/mood/theme distributions."""
    artists = _list_artist_dirs()
    if not artists:
        return "Database is empty."

    total_songs = 0
    missing_lyrics = 0
    genres = {}
    moods = {}
    themes = {}

    for a_dir in artists:
        for al_dir in _list_album_dirs(a_dir):
            for song in _list_song_files(al_dir):
                total_songs += 1
                fm, body = read_md(song)

                if "[Lyrics not found]" in body:
                    missing_lyrics += 1

                for g in (fm.get("genre", "") or "").split(","):
                    g = g.strip()
                    if g:
                        genres[g] = genres.get(g, 0) + 1

                for m in (fm.get("mood", "") or "").split(","):
                    m = m.strip()
                    if m:
                        moods[m] = moods.get(m, 0) + 1

                for t in (fm.get("themes", []) or []):
                    if isinstance(t, str) and t:
                        themes[t] = themes.get(t, 0) + 1

    lines = [
        f"**Artists**: {len(artists)}",
        f"**Songs**: {total_songs}",
        f"**Missing lyrics**: {missing_lyrics}",
        "",
        "**Top genres**: " + ", ".join(
            f"{g} ({c})" for g, c in sorted(genres.items(), key=lambda x: -x[1])[:15]
        ),
        "",
        "**Top moods**: " + ", ".join(
            f"{m} ({c})" for m, c in sorted(moods.items(), key=lambda x: -x[1])[:10]
        ),
        "",
        "**Top themes**: " + ", ".join(
            f"{t} ({c})" for t, c in sorted(themes.items(), key=lambda x: -x[1])[:10]
        ),
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tools — Fetch / Modify (these shell out to fetch.py to reuse existing logic)
# ---------------------------------------------------------------------------

@mcp.tool()
def fetch_artist(name: str, albums_only: bool = False) -> str:
    """Fetch an artist's discography and lyrics from MusicBrainz + Genius into the database.

    This may take several minutes for artists with large discographies.

    Args:
        name: Artist name to search for
        albums_only: If true, only scaffold albums/tracks without fetching lyrics (much faster)
    """
    import subprocess

    cmd = [
        sys.executable, str(PROJECT_ROOT / "scripts" / "fetch.py"),
        "artist", name,
    ]
    if albums_only:
        cmd.append("--albums-only")

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=600,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

    output = result.stdout
    if result.returncode != 0:
        output += f"\nSTDERR: {result.stderr}"
        return f"Fetch failed (exit {result.returncode}):\n{output}"

    return output


@mcp.tool()
def fetch_album(artist: str, album: str) -> str:
    """Fetch a single album's tracks and lyrics.

    Args:
        artist: Artist name
        album: Album name
    """
    import subprocess

    cmd = [
        sys.executable, str(PROJECT_ROOT / "scripts" / "fetch.py"),
        "album", artist, album,
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=300,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

    output = result.stdout
    if result.returncode != 0:
        output += f"\nSTDERR: {result.stderr}"
        return f"Fetch failed (exit {result.returncode}):\n{output}"

    return output


@mcp.tool()
def enrich_artist(name: str) -> str:
    """Run heuristic enrichment on an artist's songs to populate mood, style, energy, and themes.

    Args:
        name: Artist name (must already be in the database)
    """
    import subprocess

    cmd = [
        sys.executable, str(PROJECT_ROOT / "scripts" / "fetch.py"),
        "enrich", name,
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=300,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

    output = result.stdout
    if result.returncode != 0:
        output += f"\nSTDERR: {result.stderr}"

    return output or "Enrichment complete."


@mcp.tool()
def find_similar_artists(name: str) -> str:
    """Find artists similar to the given one by shared MusicBrainz tags.

    Args:
        name: Artist name (must already be in the database)
    """
    import subprocess

    cmd = [
        sys.executable, str(PROJECT_ROOT / "scripts" / "fetch.py"),
        "similar", name,
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=60,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

    return result.stdout or result.stderr or "No results."


@mcp.tool()
def list_missing(artist: str = "") -> str:
    """List songs that have placeholder lyrics (not yet fetched).

    Args:
        artist: Optionally filter to a specific artist
    """
    results = []
    for a_dir in _list_artist_dirs():
        fm_a, _ = read_md(a_dir / "_artist.md")
        artist_name = fm_a.get("name", a_dir.name)

        if artist and artist.lower() not in artist_name.lower():
            continue

        for al_dir in _list_album_dirs(a_dir):
            fm_al, _ = read_md(al_dir / "_album.md")
            album_title = fm_al.get("title", al_dir.name)

            for song in _list_song_files(al_dir):
                fm, body = read_md(song)
                if "[Lyrics not found]" in body:
                    results.append(f"- {artist_name} — \"{fm.get('title', song.stem)}\" ({album_title})")

    if not results:
        return "No missing lyrics found!"

    return f"{len(results)} songs with missing lyrics:\n" + "\n".join(results)


# ---------------------------------------------------------------------------
# Tools — Songwriting Support
# ---------------------------------------------------------------------------

@mcp.tool()
def get_suno_style(artist: str) -> str:
    """Get the Suno-compatible style description for an artist (no artist names, ready to paste).

    Args:
        artist: Artist name
    """
    d = _find_artist_dir(artist)
    if not d:
        return f"Artist '{artist}' not found."

    fm, _ = read_md(d / "_artist.md")
    desc = fm.get("suno_style_description", "")
    if not desc:
        return (
            f"No suno_style_description set for {fm.get('name', artist)}. "
            f"Their genre tags are: {fm.get('genre', 'none')}. "
            f"Their mood tags are: {fm.get('mood', 'none')}. "
            "You can write a description based on these and their music."
        )

    return f"**{fm.get('name', artist)}** Suno style:\n\n{desc}"


@mcp.tool()
def get_vocabulary() -> str:
    """Get the controlled vocabulary for enrichment tags (valid moods, styles, energy levels, and themes)."""
    lines = [
        "# Enrichment Vocabulary",
        "",
        f"**Moods** ({len(VALID_MOODS)}): {', '.join(VALID_MOODS)}",
        "",
        f"**Styles** ({len(VALID_STYLES)}): {', '.join(VALID_STYLES)}",
        "",
        f"**Energy** ({len(VALID_ENERGY)}): {', '.join(VALID_ENERGY)}",
        "",
        f"**Themes** ({len(VALID_THEMES)}): {', '.join(VALID_THEMES)}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Resources — Guides
# ---------------------------------------------------------------------------

@mcp.resource("lyra://guides/suno-prompt")
def suno_prompt_guide() -> str:
    """The Suno Prompt Guide — how to generate Suno style prompts from this database."""
    path = PROJECT_ROOT / "guides" / "SUNO_PROMPT_GUIDE.md"
    return path.read_text(encoding="utf-8")


@mcp.resource("lyra://guides/lyricist")
def lyricist_guide() -> str:
    """The Lyricist Guide — how to use this database for writing lyrics, including the 7-question song design interview."""
    path = PROJECT_ROOT / "guides" / "LYRICIST_GUIDE.md"
    return path.read_text(encoding="utf-8")


@mcp.resource("lyra://index")
def artist_index() -> str:
    """The root artist index with genre map and shared tags."""
    path = DATABASE_ROOT / "_index.md"
    if not path.exists():
        return "Index not generated yet. Run list_artists or fetch an artist first."
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
