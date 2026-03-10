# Lyrics Database

## What This Is
A file-based lyrics database in markdown, optimized for AI/agent consumption. Each artist gets a directory, each album a subdirectory, each song a .md file with YAML frontmatter and plain-text lyrics.

## Directory Layout
- `_index.md` — root listing of all artists
- `{Artist}/` — one dir per artist
  - `_artist.md` — artist metadata + discography listing
  - `{YYYY} - {Album}/` — one dir per album
    - `_album.md` — album metadata + track listing
    - `{NN} - {Song}.md` — song file with frontmatter + lyrics

## Navigating
- To find all songs by an artist: read `{Artist}/_artist.md` for the discography, then read any album dir.
- To find a specific song: the filename pattern is `{track_number} - {title}.md`.
- Files with `[Lyrics not found]` as the body are placeholders.

## Frontmatter Fields (songs)
- `title`, `artist`, `album`, `year`, `track_number` — always populated
- `genre`, `mood`, `themes`, `style`, `energy` — enrichment fields, may be empty
- `musicbrainz_recording_id`, `genius_url` — source IDs

## Tooling
- `python scripts/fetch.py artist "Band Name"` — fetch full discography + lyrics
- `python scripts/fetch.py artist "Band Name" --albums-only` — scaffold only, no lyrics
- `python scripts/fetch.py album "Band" "Album"` — fetch single album
- `python scripts/fetch.py index` — regenerate root index
- Requires: `GENIUS_API_TOKEN` env var, `pip install -r requirements.txt`

## Guides (for song creation)
- `guides/SUNO_PROMPT_GUIDE.md` — How to generate Suno style prompts from this database. Prompt structure, artist-to-description translations, meta-tags, technical notes.
- `guides/LYRICIST_GUIDE.md` — How to use this database for writing lyrics. Style analysis patterns, 7-question song design interview, blending styles, end-to-end workflow.

## Song Design Workflow
1. Pull reference songs from the database for style
2. Run the 7-question song design interview (see LYRICIST_GUIDE.md)
3. Write lyrics with style constraints
4. Generate Suno style prompt (see SUNO_PROMPT_GUIDE.md) — no artist names, under 180 words
5. Paste into Suno, iterate

## Conventions
- Plain text lyrics, no HTML
- One line per lyric line, blank line between sections
- Track numbers are zero-padded to 2 digits
- Suno style prompts must NOT contain artist names (Suno strips them)
- Use `.venv/bin/python` to run scripts (venv in project root)
