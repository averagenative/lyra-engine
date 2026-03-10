"""Markdown/frontmatter generation for all file types."""

import os
from datetime import date
from pathlib import Path

import yaml

from config import DATABASE_ROOT


def _write_md(path: Path, frontmatter: dict, body: str):
    """Write a markdown file with YAML frontmatter."""
    path.parent.mkdir(parents=True, exist_ok=True)

    # Use default_flow_style=False for readable YAML
    fm = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)

    with open(path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(fm)
        f.write("---\n\n")
        f.write(body)
        f.write("\n")


def write_song(path: Path, title: str, artist: str, album: str, year: int,
               track_number: int, recording_id: str = "",
               genius_url: str = "", lyrics: str | None = None):
    """Write a song .md file."""
    frontmatter = {
        "title": title,
        "artist": artist,
        "album": album,
        "year": year,
        "track_number": track_number,
        "genre": "",
        "mood": "",
        "themes": [],
        "style": "",
        "energy": "",
        "musicbrainz_recording_id": recording_id,
        "genius_url": genius_url or "",
        "fetched_at": str(date.today()),
    }

    body = lyrics if lyrics else "[Lyrics not found]"
    _write_md(path, frontmatter, body)


def write_album(path: Path, title: str, artist: str, year: int,
                release_type: str, tracks: list[dict],
                release_group_id: str = "", tracks_missing_lyrics: int = 0):
    """Write an _album.md file."""
    album_path = path / "_album.md"

    frontmatter = {
        "type": "album",
        "title": title,
        "artist": artist,
        "year": year,
        "release_type": release_type,
        "track_count": len(tracks),
        "musicbrainz_release_group_id": release_group_id,
        "fetched_at": str(date.today()),
        "tracks_fetched": len(tracks),
        "tracks_missing_lyrics": tracks_missing_lyrics,
    }

    lines = [f"# {title} ({year})", "", "## Track Listing"]
    for t in tracks:
        lines.append(f"{t['track_number']}. {t['title']}")

    _write_md(album_path, frontmatter, "\n".join(lines))


def write_artist(path: Path, name: str, artist_id: str, country: str,
                 life_span: dict, discography: list[dict]):
    """Write an _artist.md file."""
    artist_path = path / "_artist.md"

    begin = life_span.get("begin", "")
    end = life_span.get("end", "present")
    active = f"{begin}-{end}" if begin else ""

    frontmatter = {
        "type": "artist",
        "name": name,
        "musicbrainz_artist_id": artist_id,
        "genres": [],
        "country": country,
        "active_years": active,
        "fetched_at": str(date.today()),
        "album_count": len(discography),
    }

    lines = [f"# {name}", "", "## Discography"]
    for album in discography:
        lines.append(f"- {album['year']} - {album['title']} ({album['type']})")

    _write_md(artist_path, frontmatter, "\n".join(lines))


def write_index():
    """Regenerate _index.md by scanning for _artist.md files."""
    artists = []
    for entry in sorted(DATABASE_ROOT.iterdir()):
        if entry.is_dir() and (entry / "_artist.md").exists():
            # Read artist name from frontmatter
            with open(entry / "_artist.md", encoding="utf-8") as f:
                content = f.read()
            # Quick parse: find name in frontmatter
            name = entry.name  # fallback
            for line in content.split("\n"):
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip("'\"")
                    break
            artists.append((name, entry.name))

    frontmatter = {
        "type": "index",
        "artist_count": len(artists),
        "last_updated": str(date.today()),
    }

    lines = ["# Lyrics Database", "", "## Artists"]
    for name, dirname in artists:
        lines.append(f"- [{name}]({dirname}/_artist.md)")

    _write_md(DATABASE_ROOT / "_index.md", frontmatter, "\n".join(lines))
