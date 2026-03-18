# Lyra Engine

## What This Is
A file-based lyrics and style reference engine in markdown, optimized for AI/agent consumption. Each artist gets a directory, each album a subdirectory, each song a .md file with YAML frontmatter and plain-text lyrics.

## Directory Layout
- `artists/` — all fetched artist data (gitignored, locally generated)
  - `_index.md` — root listing of all artists
  - `{Artist}/` — one dir per artist
    - `_artist.md` — artist metadata + discography listing
    - `{YYYY} - {Album}/` — one dir per album
      - `_album.md` — album metadata + track listing
      - `{NN} - {Song}.md` — song file with frontmatter + lyrics

## Navigating
- To find all songs by an artist: read `artists/{Artist}/_artist.md` for the discography, then read any album dir.
- To find a specific song: the filename pattern is `{track_number} - {title}.md`.
- Files with `[Lyrics not found]` as the body are placeholders.

## Frontmatter Fields (songs)
- `title`, `artist`, `album`, `year`, `track_number` — always populated
- `genre`, `mood`, `themes`, `style`, `energy` — enrichment fields, may be empty
- `musicbrainz_recording_id`, `genius_url` — source IDs

## Tooling
- `python3 scripts/fetch.py artist "Band Name"` — fetch full discography + lyrics
- `python3 scripts/fetch.py artist "Band Name" --albums-only` — scaffold only, no lyrics
- `python3 scripts/fetch.py album "Band" "Album"` — fetch single album
- `python3 scripts/fetch.py song "Song Title" --artist "Artist"` — fetch/update lyrics for a single song
- `python3 scripts/fetch.py song "Song Title" --url "https://genius.com/..."` — fetch from specific URL
- `python3 scripts/fetch.py missing` — list all songs with missing lyrics
- `python3 scripts/fetch.py missing --retry` — retry fetching missing lyrics from Genius
- `python3 scripts/fetch.py refresh-tags` — re-fetch MusicBrainz tags for all existing artists/albums/songs
- `python3 scripts/fetch.py enrich "Artist"` — enrich songs with mood/style/energy/themes
- `python3 scripts/fetch.py similar "Artist"` — find similar artists via MusicBrainz tags
- `python3 scripts/fetch.py suggest` — analyze genre gaps and suggest new artists
- `python3 scripts/fetch.py stats` — show database statistics (artists, songs, genres, moods)
- `python3 scripts/fetch.py index` — regenerate root index (includes Genre Map + Shared Tags)
- `python3 scripts/tui.py` — interactive TUI browser (press `s` for songwriting session)
- `python3 scripts/suno_builder.py` — interactive Suno prompt builder with live preview
- Requires: `GENIUS_API_TOKEN` env var, `pip install -r requirements.txt`
- Set the token via one of:
  - Project `.env` file: `echo 'GENIUS_API_TOKEN=your-token' >> .env` (gitignored, auto-loaded by scripts)
  - Shell profile: `export GENIUS_API_TOKEN=your-token` in `~/.bashrc` or `~/.zshrc`

## When an Artist Isn't in the Database
If the user references an artist that isn't in `artists/`, offer to fetch them:
- `python3 scripts/fetch.py artist "Artist Name"` — fetches discography + lyrics
- `python3 scripts/fetch.py artist "Artist Name" --albums-only` — quick scaffold without lyrics
- After fetching, run `python3 scripts/fetch.py enrich "Artist Name"` to populate mood/style/energy/themes
- If you know the artist's style well enough, you can proceed without fetching — but note that you won't have their actual lyrics or suno_style_description to reference.

## Guides (for song creation)
- `guides/SUNO_PROMPT_GUIDE.md` — How to generate Suno style prompts from this database. Prompt structure, artist-to-description translations, meta-tags, technical notes.
- `guides/LYRICIST_GUIDE.md` — How to use this database for writing lyrics. Style analysis patterns, 7-question song design interview, blending styles, end-to-end workflow.

## Song Design Workflow
1. Pull reference songs from the database for style
2. Run the 7-question song design interview (see LYRICIST_GUIDE.md)
3. Write lyrics with style constraints
4. Generate Suno style prompt (see SUNO_PROMPT_GUIDE.md) — no artist names, under 180 words
5. Paste into Suno, iterate

## MCP Server
- `python3 scripts/mcp_server.py` — run the MCP server (stdio transport)
- Exposes 13 tools: `list_artists`, `get_artist`, `get_album`, `get_song`, `search_songs`, `get_stats`, `fetch_artist`, `fetch_album`, `enrich_artist`, `find_similar_artists`, `list_missing`, `get_suno_style`, `get_vocabulary`
- Exposes 3 resources: `lyra://guides/suno-prompt`, `lyra://guides/lyricist`, `lyra://index`
- Add to Claude Code MCP config (`~/.claude/mcp.json`):
  ```json
  {
    "mcpServers": {
      "lyra-engine": {
        "command": "/home/dmichael/projects/lyra-engine/.venv/bin/python",
        "args": ["/home/dmichael/projects/lyra-engine/scripts/mcp_server.py"],
        "env": {
          "GENIUS_API_TOKEN": "your-token-here"
        }
      }
    }
  }
  ```
- The `GENIUS_API_TOKEN` env var is required for fetch/enrich tools; read-only tools (browse, search, stats) work without it

## Additional Research (Artist Deep Dives)

Say `"additional research for [Artist]"` to trigger a deep research workflow covering all key instruments. This goes beyond what's in the database and produces:

### Guitar
1. **Guitar interplay** — how multiple guitarists interact (harmony, counterpoint, textural contrast)
2. **Signature riff characteristics** — picking technique, palm muting, tuning, scales/modes, rhythmic patterns
3. **Tone and gear** — amp voicing, EQ approach, gain structure, effects

### Drums
4. **Drumming style** — stick technique, kick patterns (single/double/trigger), snare tone and placement
5. **Rhythmic approach** — polyrhythmic vs straight, odd time signatures, tempo tendencies, cymbal work
6. **Feel and dynamics** — mechanical precision vs loose groove, how the drummer shapes energy across sections

### Vocals
7. **Vocal range and technique** — clean vs harsh ratio, screaming technique (fry, false cord, guttural), register shifts
8. **Delivery and cadence** — how vocals sit rhythmically (on-beat, syncopated, percussive), lyrical phrasing patterns
9. **Section variation** — how vocal approach changes between verse/chorus/breakdown, mic technique, effects

### Integration & Translation
10. **Rhythm section integration** — how guitars, drums, and vocals lock together as a unit
11. **Key song examples** showcasing each technique
12. **Suno prompt translation** — all findings converted to Suno-safe descriptive language (no artist names), with recommended Weirdness, Style Influence, and Exclude Styles settings

Results are saved to Claude memory as `reference_[artist]_deep_dive.md` so they compound across sessions. Completed deep dives so far:
- Lamb of God

This workflow exists because generic genre terms in Suno prompts aren't enough — specific technique descriptions (e.g., "dual guitar interplay with contrasting mid-heavy and scooped tones" vs just "groove metal") push Suno toward the right sound. Drum and vocal specifics are equally important for steering Suno away from default delivery and beat patterns.

## Interaction Patterns

- **Adding artists**: `"add [Artist] to our local DB"` — fetches via `fetch.py artist`, reports results
- **Batch adds**: Multiple artists can be requested at once and will be fetched in parallel
- **Songwriting sessions**: Provide a theme/style/artist reference and get lyrics + Suno prompt + settings. Lyrics are optimized for Suno (syllable count, meter, hard consonants — see `guides/SUNO_PROMPT_GUIDE.md` for pitfalls)
- **Suno prompts always include**: Style prompt text, Weirdness %, Style Influence %, Exclude Styles list
- **Recurring themes**: Anti-imperialism, empire decline, historical power cycles are a consistent songwriting interest — draw from these proactively
- **Style prompts must never contain artist names** — Suno strips them. Translate to descriptive language

## Conventions
- Plain text lyrics, no HTML
- One line per lyric line, blank line between sections
- Track numbers are zero-padded to 2 digits
- Suno style prompts must NOT contain artist names (Suno strips them)
- Use `.venv/bin/python` to run scripts (venv in project root)
