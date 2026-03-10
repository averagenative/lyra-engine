## 1. Foundation — Project Infrastructure (P0)

> Goal: Working project skeleton with dependencies, git, and clean test data.
> Delivers: A runnable project that an agent or human can clone and set up in < 5 min.

- [x] 1.1 Initialize git repo, create `requirements.txt` with dependencies (`musicbrainzngs`, `lyricsgenius`, `python-slugify`, `pyyaml`)
- [x] 1.2 Create Python venv and verify all dependencies install cleanly
- [x] 1.3 Create `CLAUDE.md` — agent navigation guide for the database layout, tooling commands, and conventions
- [x] 1.4 Create `scripts/config.py` — path helpers (`artist_dir`, `album_dir`, `song_path`), `sanitize_filename`, constants
- [x] 1.5 Clean up stale test data from initial Radiohead runs (bootleg/live dirs that leaked through before filtering fix)
- [x] 1.6 Add `.gitignore` (`.venv/`, `__pycache__/`, `.env`) and create initial commit

## 2. Lyrics Ingestion CLI — Core Pipeline (P0)

> Goal: `python scripts/fetch.py artist "Band Name"` produces a clean, complete directory tree with lyrics.
> Delivers: The database itself. Everything else depends on this.

- [x] 2.1 Implement `scripts/musicbrainz.py` — `search_artist()`, `get_discography()`, `get_tracklist()`
- [x] 2.2 Add secondary-type filtering to `get_discography()` to exclude bootlegs, demos, live, and compilations by default
- [x] 2.3 Implement `scripts/lyrics.py` — Genius client init, `fetch_lyrics()` with fuzzy title matching via `difflib.SequenceMatcher`
- [x] 2.4 Implement `scripts/markdown.py` — `write_song()`, `write_album()`, `write_artist()`, `write_index()` with YAML frontmatter generation
- [x] 2.5 Implement `scripts/fetch.py` — argparse CLI with `artist`, `album`, `index` subcommands, orchestrating the full pipeline
- [x] 2.6 Add idempotency logic — skip existing songs with lyrics, retry `[Lyrics not found]` placeholders, `--force` flag to override
- [x] 2.7 End-to-end test: run `fetch.py artist "Radiohead" --albums-only`, verify clean directory tree with correct album/track structure (no bootlegs, correct track counts)
- [x] 2.8 End-to-end test: run `fetch.py artist` with a small artist (3-4 albums) WITH lyrics fetching enabled (`GENIUS_API_TOKEN` set), verify lyrics populated in `.md` files
- [x] 2.9 Test `fetch.py album "Artist" "Album"` for single-album fetch (fixed: cmd_album was not passing include_live/include_compilations to get_discography)
- [x] 2.10 Test `fetch.py index` regeneration — verify `_index.md` lists all ingested artists

## 3. Ingestion Hardening (P0)

> Goal: The pipeline handles real-world data reliably across diverse artists.
> Delivers: Confidence to bulk-ingest 10+ artists without babysitting.

- [x] 3.1 Handle `--include-singles` flag — adds "single" to MusicBrainz type query, singles get their own year-titled directories
- [x] 3.2 Validate multi-disc album flattening — verified with Pink Floyd's The Wall (26 tracks flattened across 2 discs)
- [x] 3.3 Add network error handling — try/except on get_tracklist and fetch_lyrics, log and continue on failure
- [x] 3.4 Add progress output — album counter [N/total] and track counter NN/total in lyrics fetch
- [x] 3.5 Handle Genius edge cases — instrumental detection, robust trailing cleanup (Embed, digits, empty lines), timeout handling
- [ ] 3.6 Validate with target artist list: Deftones, Crowbar, Sleep (done), Type O Negative, Opeth, Nine Inch Nails — fix any issues found

## 4. Suno Style Descriptions & Prompt Generator (P1)

> Goal: Each `_artist.md` contains a `suno_style_description` field. An agent can read it and produce a Suno-ready prompt without manual research.
> Delivers: Eliminates the "translate artist name to Suno-safe language" bottleneck.

- [ ] 4.1 Add `suno_style_description` field to `_artist.md` frontmatter schema (empty string by default, filled per-artist)
- [ ] 4.2 Add `suno_style_description` field to `_album.md` frontmatter schema — album-level style can differ from artist-level (e.g., Radiohead's Kid A vs. The Bends)
- [ ] 4.3 Write `suno_style_description` for 3 initial artists by researching AllMusic/Discogs/RYM and analyzing their lyrics in the database — document the research process so it's repeatable
- [ ] 4.4 Create `guides/ARTIST_STYLE_TEMPLATE.md` — a fill-in template for writing Suno-safe artist descriptions, with the translation process (AllMusic lookup → extract Styles/Moods → combine with era + production texture + instruments)
- [ ] 4.5 Add example artist translations to `guides/SUNO_PROMPT_GUIDE.md` covering multiple genres (not just industrial/alternative — add pop, hip-hop, folk, electronic examples from the user's actual library)

## 5. Lyricist Guide & Song Design Workflow (P1)

> Goal: Any AI agent picking up this repo can run a complete songwriting session — from concept to Suno-ready output — without external context.
> Delivers: The creative session speedup (30-60 min saved per session).

- [x] 5.1 Create `guides/SUNO_PROMPT_GUIDE.md` — style prompt rules, structure, non-default policy, meta-tag categories, Suno technical notes
- [x] 5.2 Create `guides/LYRICIST_GUIDE.md` — 7-question song design interview, lyrics writing rules, style blending instructions, end-to-end workflow
- [ ] 5.3 Add the "Sound Designer" agent persona to `guides/LYRICIST_GUIDE.md` — adapted from the "River Stone Audio" persona in `~/projects/greentd/game/audio/SUNO-RESEARCH.md`, generalized beyond game audio
- [ ] 5.4 Add a "Style Blending" worked example to the guide — pick 2 artists from the database, walk through the full process: read `_artist.md` → sample lyrics → identify elements to blend → write lyrics → generate Suno prompt
- [ ] 5.5 Add era-based filtering instructions — how to find "all '90s alternative" or "2000s electronic" across the database using directory names and frontmatter
- [ ] 5.6 Validation: run a full songwriting session using only the database and guides (no external research). Identify any gaps where the agent needs information not in the repo, and fill them.

## 6. Metadata Enrichment (P2)

> Goal: Frontmatter fields (`genre`, `mood`, `themes`, `style`, `energy`) are populated, enabling precise filtering.
> Delivers: "Give me all melancholic songs from the '90s" actually works.

- [ ] 6.1 Define the controlled vocabulary for each enrichment field — list valid values for `mood`, `style`, `energy` to keep tags consistent across artists
- [ ] 6.2 Create `scripts/enrich.py` — a script that reads song files and uses an LLM (via API or agent) to suggest tags based on lyrics content, writing them back to frontmatter
- [ ] 6.3 Enrich one complete artist as a pilot — verify tag quality, adjust vocabulary if needed
- [ ] 6.4 Add `genre` population from MusicBrainz tags during ingestion (MusicBrainz has genre/tag data on artists and release groups) — so at least genre is auto-populated on first fetch

## 7. Advanced Suno Workflow Documentation (P3)

> Goal: Complex production techniques are documented for when needed.
> Delivers: Reference material for multi-pass Studio builds and post-processing.

- [ ] 7.1 Add multi-pass Suno Studio workflow to `guides/SUNO_PROMPT_GUIDE.md` — the 6-pass strategy (foundation → instruments → rhythm → texture → extend → remaster)
- [ ] 7.2 Add Suno v5/Studio capability reference — Warp Markers, stem separation, Alternates, Time Signature support, credit costs
- [ ] 7.3 Add post-processing reference — ffmpeg commands for loop creation, loudness normalization, format conversion (from existing `SUNO-RESEARCH.md`)
- [ ] 7.4 Add instrumental-only techniques section — three-method approach (style prompt + lyrics field + negative prompting) with troubleshooting for when vocals leak through
