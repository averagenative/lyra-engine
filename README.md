# Lyra Engine

A file-based lyrics and style reference engine in markdown, built for AI agents. Fetch full discographies with lyrics, genre/mood metadata, and Suno-compatible style descriptions — then use AI agents to write songs, blend styles, and generate production prompts.

## What It Does

- **Automated ingestion**: Say `fetch.py artist "Band Name"` and get a complete directory tree with lyrics, genre tags, and metadata from MusicBrainz + Genius
- **Style reference**: AI agents read artist lyrics and metadata to write new songs grounded in real styles
- **Suno prompt generation**: Translate any artist's sound into Suno-safe style prompts (no artist names — Suno strips them)
- **Style blending**: Combine elements from multiple artists (Crowbar's crushing weight + Portishead's trip-hop atmosphere)
- **Metadata filtering**: Search by genre, mood, era, themes, energy across the entire database

## Setup

```bash
git clone <repo-url> lyra-engine
cd lyra-engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### API Keys

| Service | Required? | How to Get | Used For |
|---------|-----------|------------|----------|
| **Genius** | Yes (for lyrics) | Free — sign up at [genius.com/api-clients](https://genius.com/api-clients), create an app, copy the "Client Access Token" | Fetching song lyrics |
| **MusicBrainz** | No key needed | Free, open API with rate limiting | Discography, track listings, genre/mood tags, artist relationships |

Add your Genius token to a `.env` file in the project root:

```bash
echo 'GENIUS_API_TOKEN=your_token_here' > .env
```

## CLI Usage

### Fetching Data

```bash
# Fetch full discography + lyrics for an artist
python scripts/fetch.py artist "Deftones"

# Scaffold albums/tracks only (no lyrics, no Genius API needed)
python scripts/fetch.py artist "Deftones" --albums-only

# Fetch a single album
python scripts/fetch.py album "Deftones" "White Pony"

# Include compilations, live albums, or singles
python scripts/fetch.py artist "NIN" --include-live --include-compilations --include-singles
```

### Managing Lyrics

```bash
# List all songs with missing lyrics
python scripts/fetch.py missing

# Filter to one artist
python scripts/fetch.py missing --artist "Keelhaul"

# Retry fetching missing lyrics from Genius
python scripts/fetch.py missing --retry

# Fetch/update a single song (search + Genius)
python scripts/fetch.py song "Paranoid Android" --artist "Radiohead"

# Provide a direct URL to scrape lyrics from
python scripts/fetch.py song "Paranoid Android" --url "https://genius.com/..."
```

### Metadata & Discovery

```bash
# Show database stats (artists, songs, genres, moods)
python scripts/fetch.py stats

# Re-fetch MusicBrainz tags for all existing data
python scripts/fetch.py refresh-tags

# Enrich songs with mood/style/energy/themes from lyrics analysis
python scripts/fetch.py enrich "Sleep"           # one artist
python scripts/fetch.py enrich --all             # all artists
python scripts/fetch.py enrich "Sleep" --dry-run # preview only

# Find similar artists via shared MusicBrainz tags
python scripts/fetch.py similar "Crowbar"

# Analyze genre gaps and suggest new artists to add
python scripts/fetch.py suggest

# Regenerate the root index
python scripts/fetch.py index
```

### Interactive Tools

```bash
# Browse the database (artists → albums → tracks → lyrics)
python scripts/tui.py

# Start a songwriting session from the TUI: press 's'
# Export session notes: press 'e'

# Build a Suno-compatible style prompt interactively
python scripts/suno_builder.py
# Live preview with char/word count, copy to clipboard: 'c', export: 'e'
```

## Directory Structure

```
lyra-engine/
  README.md
  CLAUDE.md              # Claude Code agent guide
  AGENTS.md              # Universal agent guide (agents.md convention)
  requirements.txt
  .env                   # GENIUS_API_TOKEN (gitignored)
  scripts/
    fetch.py             # CLI entry point
    musicbrainz.py       # MusicBrainz API client
    lyrics.py            # Genius lyrics fetching
    markdown.py          # Frontmatter/markdown generation
    enrich.py            # Heuristic metadata enrichment
    config.py            # Path helpers, constants
    tui.py               # Terminal UI browser
    suno_builder.py      # Interactive Suno prompt builder
  agents/
    lyricist.md          # Lyricist agent persona
    producer.md          # Music producer / Suno prompt agent
  guides/
    LYRICIST_GUIDE.md    # Song design workflow, style analysis, blending
    SUNO_PROMPT_GUIDE.md # Suno prompt rules, translations, techniques
    ARTIST_STYLE_TEMPLATE.md  # Template for writing Suno-safe descriptions
    ENRICHMENT_VOCABULARY.md  # Controlled vocabulary for metadata tags
  sessions/              # Exported songwriting sessions (gitignored)
  artists/               # All fetched data (gitignored)
    _index.md
    {Artist}/
      _artist.md         # Genre, tags, members, external links, suno_style_description
      {YYYY} - {Album}/
        _album.md        # Album metadata, genre, track listing
        {NN} - {Song}.md # YAML frontmatter + plain-text lyrics
```

## Using with AI Agents

This repo is designed to be used with AI coding agents like [Claude Code](https://claude.com/claude-code), OpenCode, or any agent that supports the [agents.md](https://agents.md) convention.

### Agent Personas

Two specialized agent personas are defined in `agents/`:

- **`agents/lyricist.md`** — Writes original lyrics grounded in database artists' styles. Runs the 7-question song design interview, analyzes vocabulary/metaphor/structure patterns, and blends styles from multiple artists.

- **`agents/producer.md`** — Generates Suno-compatible style prompts. Translates artist names to descriptive language, designs sonic palettes, manages multi-pass Studio builds.

### Workflow

```
1. CONCEPT       → Define idea, emotional center, perspective
2. STYLE REF     → Agent reads artists from the database
3. INTERVIEW     → 7-question song design (mood, aggression, structure, etc.)
4. LYRICS        → Agent writes lyrics with style constraints
5. SUNO PROMPT   → Agent generates style prompt (no artist names, <180 words)
6. GENERATE      → Paste into Suno, iterate
```

### Quick Start with Claude Code

```bash
# From the project root:
claude

# Then ask:
# "Write a song that blends Crowbar's sludge with Type O Negative's gothic theatricality"
# "Generate a Suno prompt for something that sounds like 90s trip-hop meets doom metal"
# "What genres are in the database? Show me all melancholic songs from the 2000s"
```

## Song Frontmatter Schema

```yaml
---
title: "Airbag"
artist: "Radiohead"
album: "OK Computer"
year: 1997
track_number: 1
genre: "alternative rock, art rock"
mood: "atmospheric, introspective"
themes:
- technology
- survival
- alienation
style: "dynamic, spacious"
energy: "building"
musicbrainz_tags:
- alternative rock
- art rock
musicbrainz_recording_id: "abc123"
genius_url: "https://genius.com/..."
fetched_at: "2026-03-10"
---
[plain text lyrics]
```

## Data Sources

- **[MusicBrainz](https://musicbrainz.org/)** — Open music database. Provides discographies, track listings, genre/mood community tags, artist relationships, and links to external services. Free API, no key required.
- **[Genius](https://genius.com/)** — Lyrics database. Provides song lyrics via API + page scraping. Free API key required.

## License

This project provides tooling for building a personal lyrics database. The lyrics themselves are copyrighted by their respective artists and publishers. This tool is intended for personal reference and AI-assisted songwriting research.
