"""Markdown/frontmatter generation for all file types."""

import os
from collections import defaultdict
from datetime import date
from itertools import combinations
from pathlib import Path

import yaml

from config import DATABASE_ROOT

# Known mood/descriptor tags (not genres) from MusicBrainz community tags
_MOOD_TAGS = {
    "atmospheric", "cold", "dark", "melancholic", "melancholy", "aggressive",
    "heavy", "brutal", "intense", "ethereal", "dreamy", "hypnotic", "groovy",
    "emotional", "existential", "futuristic", "introspective", "political",
    "angry", "sad", "happy", "epic", "calm", "energetic", "psychedelic",
    "lo-fi", "noisy", "ambient", "minimalist", "complex", "technical",
    "melodic", "dissonant", "haunting", "uplifting", "somber", "raw",
}


def _classify_tags(tags: list[str]) -> tuple[list[str], list[str]]:
    """Split MusicBrainz tags into genre tags and mood/descriptor tags."""
    genres = []
    moods = []
    for tag in tags:
        if tag.lower() in _MOOD_TAGS:
            moods.append(tag)
        else:
            genres.append(tag)
    return genres, moods


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
               genius_url: str = "", lyrics: str | None = None,
               tags: list[str] | None = None):
    """Write a song .md file."""
    # Separate genre tags from mood/descriptor tags
    genre_tags, mood_tags = _classify_tags(tags or [])

    frontmatter = {
        "title": title,
        "artist": artist,
        "album": album,
        "year": year,
        "track_number": track_number,
        "genre": ", ".join(genre_tags) if genre_tags else "",
        "mood": ", ".join(mood_tags) if mood_tags else "",
        "themes": [],
        "style": "",
        "energy": "",
        "musicbrainz_tags": tags or [],
        "musicbrainz_recording_id": recording_id,
        "genius_url": genius_url or "",
        "fetched_at": str(date.today()),
    }

    body = lyrics if lyrics else "[Lyrics not found]"
    _write_md(path, frontmatter, body)


def write_album(path: Path, title: str, artist: str, year: int,
                release_type: str, tracks: list[dict],
                release_group_id: str = "", tracks_missing_lyrics: int = 0,
                tags: list[str] | None = None):
    """Write an _album.md file."""
    album_path = path / "_album.md"

    genre_tags, mood_tags = _classify_tags(tags or [])

    frontmatter = {
        "type": "album",
        "title": title,
        "artist": artist,
        "year": year,
        "release_type": release_type,
        "genre": ", ".join(genre_tags) if genre_tags else "",
        "mood": ", ".join(mood_tags) if mood_tags else "",
        "musicbrainz_tags": tags or [],
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
                 life_span: dict, discography: list[dict],
                 tags: list[str] | None = None,
                 relationships: dict | None = None):
    """Write an _artist.md file."""
    artist_path = path / "_artist.md"

    begin = life_span.get("begin", "")
    end = life_span.get("end", "present")
    active = f"{begin}-{end}" if begin else ""

    genre_tags, mood_tags = _classify_tags(tags or [])
    rels = relationships or {}

    frontmatter = {
        "type": "artist",
        "name": name,
        "musicbrainz_artist_id": artist_id,
        "genre": ", ".join(genre_tags) if genre_tags else "",
        "mood": ", ".join(mood_tags) if mood_tags else "",
        "musicbrainz_tags": tags or [],
        "suno_style_description": "",
        "country": country,
        "active_years": active,
        "members": rels.get("members", []),
        "fetched_at": str(date.today()),
        "album_count": len(discography),
    }

    # Add external links if available
    for key, url in rels.get("external_links", {}).items():
        frontmatter[key] = url

    lines = [f"# {name}", "", "## Discography"]
    for album in discography:
        lines.append(f"- {album['year']} - {album['title']} ({album['type']})")

    if rels.get("members"):
        lines.extend(["", "## Members"])
        for member in rels["members"]:
            lines.append(f"- {member}")

    _write_md(artist_path, frontmatter, "\n".join(lines))


def read_md(path: Path) -> tuple[dict, str]:
    """Read a markdown file with YAML frontmatter. Returns (frontmatter_dict, body)."""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return {}, content

    # Split on the second '---'
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n")
    return frontmatter, body


def update_tags(path: Path, tags: list[str]):
    """Update only the tag-related fields in an existing markdown file's frontmatter."""
    fm, body = read_md(path)
    if not fm:
        return

    genre_tags, mood_tags = _classify_tags(tags)

    fm["genre"] = ", ".join(genre_tags) if genre_tags else ""
    fm["mood"] = ", ".join(mood_tags) if mood_tags else ""
    fm["musicbrainz_tags"] = tags

    # Ensure suno_style_description exists for artist files
    if fm.get("type") == "artist" and "suno_style_description" not in fm:
        fm["suno_style_description"] = ""

    _write_md(path, fm, body)


def write_index():
    """Regenerate _index.md by scanning for _artist.md files."""
    # Generic tags too broad to be interesting for the Shared Tags section
    _GENERIC_TAGS = {
        "rock", "metal", "pop", "electronic", "hip hop", "jazz", "blues",
        "country", "folk", "punk", "classical", "soul", "r&b", "reggae",
        "latin", "world", "experimental", "indie", "alternative",
        "singer-songwriter", "instrumental", "acoustic", "hardcore",
        "american", "british", "canadian",
    }

    artists = []
    # Map: artist name -> {genre, tags}
    artist_data = {}

    for entry in sorted(DATABASE_ROOT.iterdir()):
        if entry.is_dir() and (entry / "_artist.md").exists():
            fm, _ = read_md(entry / "_artist.md")
            name = fm.get("name", entry.name)
            artists.append((name, entry.name))

            genre_str = fm.get("genre", "")
            primary_genre = ""
            if genre_str:
                primary_genre = genre_str.split(",")[0].strip()

            mb_tags = fm.get("musicbrainz_tags", [])
            if not isinstance(mb_tags, list):
                mb_tags = []

            artist_data[name] = {
                "primary_genre": primary_genre,
                "tags": set(t.lower() for t in mb_tags),
            }

    frontmatter = {
        "type": "index",
        "artist_count": len(artists),
        "last_updated": str(date.today()),
    }

    lines = ["# Lyra Engine", "", "## Artists"]
    for name, dirname in artists:
        lines.append(f"- [{name}]({dirname}/_artist.md)")

    # --- Genre Map ---
    genre_map = defaultdict(list)
    for name, data in artist_data.items():
        pg = data["primary_genre"]
        if pg:
            genre_map[pg].append(name)

    if genre_map:
        lines.extend(["", "## Genre Map"])
        for genre in sorted(genre_map):
            lines.append(f"")
            lines.append(f"### {genre}")
            for artist_name in sorted(genre_map[genre]):
                lines.append(f"- {artist_name}")

    # --- Shared Tags ---
    # Find pairs of artists that share at least one niche tag
    shared_pairs = []
    artist_names = sorted(artist_data.keys())
    for a, b in combinations(artist_names, 2):
        niche_a = artist_data[a]["tags"] - _GENERIC_TAGS - _MOOD_TAGS
        niche_b = artist_data[b]["tags"] - _GENERIC_TAGS - _MOOD_TAGS
        common = niche_a & niche_b
        if common:
            shared_pairs.append((a, b, sorted(common)))

    if shared_pairs:
        lines.extend(["", "## Shared Tags"])
        for a, b, tags in sorted(shared_pairs):
            lines.append(f"- {a}, {b}: {', '.join(tags)}")

    _write_md(DATABASE_ROOT / "_index.md", frontmatter, "\n".join(lines))
