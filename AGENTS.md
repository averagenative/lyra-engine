# AGENTS.md — Lyra Engine

## Project Overview

A file-based lyrics and style reference engine in markdown, optimized for AI agent consumption. Contains discographies, lyrics, and genre/mood metadata for use in songwriting, style analysis, and Suno prompt generation.

## Dev Environment

- Python 3.12+ with venv: `.venv/bin/python`
- Install: `pip install -r requirements.txt`
- Requires `GENIUS_API_TOKEN` in `.env` file (get free at genius.com/api-clients)
- MusicBrainz API requires no auth

## Commands

- `python scripts/fetch.py artist "Band Name"` — fetch full discography + lyrics
- `python scripts/fetch.py artist "Band Name" --albums-only` — scaffold only, skip lyrics
- `python scripts/fetch.py album "Artist" "Album"` — fetch single album
- `python scripts/fetch.py refresh-tags` — re-fetch MusicBrainz tags for all existing data
- `python scripts/fetch.py stats` — show database statistics (genres, moods, counts)
- `python scripts/fetch.py index` — regenerate root index

## Data Layout

All fetched data lives in `artists/` (gitignored):

```
artists/
  _index.md                          # Root listing of all artists
  {Artist Name}/
    _artist.md                       # Artist metadata, genre, discography
    {YYYY} - {Album Title}/
      _album.md                      # Album metadata, genre, track listing
      {NN} - {Song Title}.md         # Song frontmatter + plain-text lyrics
```

## Frontmatter Schema

Songs have: `title`, `artist`, `album`, `year`, `track_number`, `genre`, `mood`, `themes`, `style`, `energy`, `musicbrainz_tags`, `musicbrainz_recording_id`, `genius_url`, `fetched_at`

Albums have: `type`, `title`, `artist`, `year`, `release_type`, `genre`, `mood`, `musicbrainz_tags`, `track_count`, `musicbrainz_release_group_id`

Artists have: `type`, `name`, `musicbrainz_artist_id`, `genre`, `mood`, `musicbrainz_tags`, `suno_style_description`, `country`, `active_years`

## Agent Personas

Specialized agent definitions in `agents/`:

- `agents/lyricist.md` — Writes lyrics using the database as style reference
- `agents/producer.md` — Generates Suno-compatible style prompts and manages the production workflow

## Guides

- `guides/LYRICIST_GUIDE.md` — Style analysis, song design interview, blending instructions
- `guides/SUNO_PROMPT_GUIDE.md` — Suno prompt rules, artist translations, meta-tags

## Generated Songs (`songs/`)

When you write lyrics, **always save them to `songs/`** as `{YYYY-MM-DD}-{song-slug}.md`. This directory is gitignored (personal per user). Each file has YAML frontmatter (`title`, `created_at`, `project`, `track_ref`, `style_influences`, `themes`, `vocal_style`) followed by plain-text lyrics with section headers in `[brackets]` and delivery notes in `(parentheses)`. This corpus enables pattern analysis — spotting reused words, overused phrases, and stylistic ruts.

## Conventions

- Plain text lyrics, no HTML
- One line per lyric line, blank line between sections
- Track numbers zero-padded to 2 digits
- Suno style prompts must NOT contain artist names (Suno strips them)
- `[Lyrics not found]` = placeholder; `[Instrumental]` = confirmed instrumental
