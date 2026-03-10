## Why

There's no good way to feed an AI agent a curated, searchable corpus of song lyrics organized by artist, era, and style — and then use that corpus to generate new lyrics or style prompts for tools like Suno. Today, if you want to say "write lyrics in the vibe of Band X from the '90s" or "generate a Suno style prompt blending Band A and Band C," you have to manually gather lyrics, remember stylistic details, and craft prompts from scratch every time. This project creates a structured, AI-native lyrics database with automated ingestion and prompt generation tooling built on top of it.

## What Changes

- **Automated lyrics ingestion**: CLI tool that takes a band name, researches their full discography via MusicBrainz API, scaffolds a directory structure, and fetches lyrics via Genius API — fully automated.
- **AI-optimized file format**: Markdown files with YAML frontmatter containing progressive metadata (genre, mood, themes, style, energy). Low token cost, easy for agents to navigate via index files at each level (root, artist, album).
- **Suno style prompt generator**: Given one or more artists/songs from the database, generates Suno-compatible style/genre description prompts based on the actual lyrical and musical characteristics in the metadata. Follows proven Suno prompt structure: Genre + Era → Instrumentation → Rhythm → Vocals → Energy arc → Production texture. Keeps style prompts under 180 words / 1000 chars (Suno's limit). Translates artist references into Suno-safe descriptive language (no artist names — Suno strips them). Supports blending styles from multiple artists and targeting specific eras. Each `_artist.md` includes a `suno_style_description` field — a pre-written Suno-safe translation of that artist's sound, built using AllMusic/Discogs/RYM descriptors + the lyrics in the database.
- **Agent lyricist guide**: A prompt template and reference guide that teaches AI agents how to use the database effectively — how to analyze existing lyrics for patterns, how to blend styles from multiple artists, how to target specific eras or moods, and best practices for lyric writing prompts. Includes a 7-question song design interview (emotional center, perspective, aggression level, tempo/structure, vocal style, imagery, ending mood) and a prompt building framework (Identity → Palette → Vocals → Dynamics → Constraints → Production blocks). Includes a "Sound Designer" agent persona template for crafting production-aware prompts.
- **Song design workflow**: An agent-optimized workflow for designing songs end-to-end — from concept to lyrics to Suno prompt — using the database as a style reference. Includes the non-default policy (don't assume minor key, aggressive tone, male vocals, etc. unless requested). References Suno v5 capabilities (44.1kHz stereo, Studio multi-track editing, stem separation, Warp Markers) and the multi-pass building strategy (foundation → instruments → rhythm → texture → extend → remaster) for complex productions.

## Business Value Analysis

### Who Benefits

**Primary: The songwriter/producer (you)**
- Currently: Every songwriting session starts from zero. You remember a vibe you want but have to re-explain it to the AI each time, manually look up lyrics for reference, and reconstruct Suno prompt knowledge from scattered notes across 3+ projects.
- After: You say "write something that blends Radiohead's OK Computer melancholy with NIN's Fragile-era texture" and the agent pulls actual lyrics, reads pre-built Suno-safe style descriptions, and generates both lyrics and a production-ready Suno prompt in one pass.
- Time saved: ~30-60 minutes per song session on reference gathering and prompt crafting alone.

**Secondary: AI agents working on your behalf**
- Currently: Agents have no structured music knowledge. When asked to "write like Band X," they rely on training data — generic, uncontrollable, and not grounded in actual lyrics.
- After: Agents navigate a structured corpus with index files, frontmatter metadata, and explicit style guides. They produce more accurate, grounded output because they're referencing real lyrics, not hallucinated approximations.

### Problem Statement

The core problem is **context loss between creative sessions**. You have deep knowledge of what musical styles you want to draw from, but that knowledge lives in your head — not in a format AI agents can access. Every session requires rebuilding context: which bands, which eras, what the style actually sounds like in Suno-safe terms, what prompt structure works. Your existing Suno research is scattered across 3 project directories and isn't connected to actual lyrics.

This is a **creative infrastructure** problem, not a technical one. The database and tooling exist to make the creative act faster and more precise.

### Priority by Value Delivered

| Capability | Value | Priority |
|---|---|---|
| `lyrics-ingestion` | **High** — unlocks everything else. Without lyrics in the database, the guides and prompt generator have nothing to reference. One-time setup per artist, then it's there forever. | P0 — build first |
| `lyricist-guide` + `song-design-workflow` | **High** — this is where creative sessions actually speed up. The 7-question interview and prompt framework are already proven (existing research). Consolidating them here makes them accessible to any agent in any session. | P1 — build immediately after ingestion |
| `style-prompt-generator` (Suno descriptions in `_artist.md`) | **Medium-High** — eliminates the "translate artist name to Suno-safe language" step that currently requires manual AllMusic/Discogs research per artist. Compounds in value as more artists are added. | P1 — build alongside guides |
| Metadata enrichment (mood, themes, energy tags) | **Medium** — enables more precise filtering ("give me all melancholic songs from the '90s") but the database is useful without it. Can be filled in progressively. | P2 — enrich over time |
| Multi-pass Suno Studio workflow docs | **Low-Medium** — useful for complex productions but most songs don't need 6-pass builds. Nice to have in the guide, not blocking. | P3 — document when needed |

### What Happens If We Don't Build This

- Every songwriting/Suno session continues to start from scratch.
- Suno prompt knowledge stays scattered across `greentd/`, `music.dcmichael.com/`, and your memory.
- Agents produce generic "write like Radiohead" output instead of grounded, lyrics-informed style matching.
- You spend 30-60 minutes per session on context reconstruction that could be eliminated.
- As you explore more artists and styles, the problem compounds — more knowledge in your head that agents can't access.

The cost of *not* building this is small per session but multiplicative over time.

### Success Metrics

1. **Session startup time**: A songwriting session that previously required 30+ min of reference gathering should need < 5 min (agent reads database directly).
2. **Ingestion coverage**: 10+ artists fully ingested with lyrics within the first month of use.
3. **Suno prompt quality**: Style prompts generated from the database produce usable Suno output on first or second generation (vs. 4-5 iterations when crafting prompts from memory).
4. **Reuse rate**: The guides and artist style descriptions get referenced across multiple sessions — not written once and forgotten.
5. **Agent grounding**: When an agent is asked to "write in the style of X," it cites specific songs/lyrics from the database rather than relying on generic training data.

## Capabilities

### New Capabilities
- `lyrics-ingestion`: Automated CLI pipeline for fetching artist discographies (MusicBrainz) and lyrics (Genius API), generating structured markdown files with YAML frontmatter, and maintaining index files for navigation. Filters out bootlegs/live/compilations via MusicBrainz secondary types. Idempotent re-runs (skip existing, retry missing lyrics).
- `style-prompt-generator`: Tool that reads artist/song metadata and lyrics from the database to generate style description prompts for Suno and other AI music tools. Maintains per-artist `suno_style_description` in `_artist.md` — Suno-safe translations of each artist's sound. Supports blending styles from multiple artists, targeting specific eras, and the multi-pass Suno Studio workflow.
- `lyricist-guide`: Reference documentation and prompt templates that enable AI agents to effectively use the database for lyric writing — including style analysis patterns, era-based filtering, multi-artist style blending, song structure conventions, and a Sound Designer agent persona. Consolidated from existing research in `~/projects/music.dcmichael.com/` and `~/projects/greentd/`.
- `song-design-workflow`: End-to-end agent workflow for designing songs: concept → 7-question interview → style reference selection → lyric generation → Suno prompt generation → iteration. Includes non-default policy and Suno v5/Studio-aware production notes.

### Modified Capabilities
<!-- None — this is a greenfield project -->

## Impact

- **New dependencies**: `musicbrainzngs`, `lyricsgenius`, `python-slugify`, `pyyaml` (Python)
- **External services**: MusicBrainz API (free, no auth), Genius API (free token required), Suno (Pro $10/mo for generation)
- **File system**: Creates a potentially large directory tree (hundreds of .md files per artist)
- **API rate limits**: MusicBrainz auto-throttles to 1 req/sec; Genius needs manual 1.5s sleep between requests
- **MusicBrainz data quality**: Release groups include bootlegs, interviews, and unofficial releases tagged as "album." Filtering by secondary type (live, compilation, bootleg, demo) is required to get clean discographies.
- **Legal**: Song lyrics are copyrighted — this database is for personal use and AI research/prompting, not redistribution. Suno Pro grants commercial use rights for generated audio but not full ownership (evolving legal landscape).
- **Prior art**: Consolidates existing Suno research from `~/projects/greentd/game/audio/SUNO-RESEARCH.md`, `~/projects/music.dcmichael.com/song_prompt_suno_optimized.md`, and `~/projects/music.dcmichael.com/SUNO_PROMPT_GUIDE.md` into this project's `guides/` directory.
