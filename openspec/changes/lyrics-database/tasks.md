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
- [x] 3.6 Validate with target artist list — all 11 artists fetched successfully (Deftones, Crowbar, Sleep, Type O Negative, Opeth, NIN, Spiritbox, Kublai Khan TX, Cannibal Corpse, Sanguisugabogg, Portishead). Added `refresh-tags` command and moved data to `artists/` directory.

## 4. Suno Style Descriptions & Prompt Generator (P1)

> Goal: Each `_artist.md` contains a `suno_style_description` field. An agent can read it and produce a Suno-ready prompt without manual research.
> Delivers: Eliminates the "translate artist name to Suno-safe language" bottleneck.

- [x] 4.1 Add `suno_style_description` field to `_artist.md` frontmatter schema (empty string by default, filled per-artist)
- [x] 4.2 Add `suno_style_description` field to `_album.md` frontmatter schema — album-level style can differ from artist-level (documented in ARTIST_STYLE_TEMPLATE.md)
- [x] 4.3 Write `suno_style_description` for 3 initial artists (Deftones, Crowbar, Type O Negative) by analyzing database lyrics and MusicBrainz tags
- [x] 4.4 Create `guides/ARTIST_STYLE_TEMPLATE.md` — fill-in template with research process, sonic signature fields, validation checklist, and 3 worked examples
- [x] 4.5 Add example artist translations to `guides/SUNO_PROMPT_GUIDE.md` — added all 11 database artists (sludge, death metal, gothic, metalcore, trip-hop, stoner doom, hardcore, progressive)

## 5. Lyricist Guide & Song Design Workflow (P1)

> Goal: Any AI agent picking up this repo can run a complete songwriting session — from concept to Suno-ready output — without external context.
> Delivers: The creative session speedup (30-60 min saved per session).

- [x] 5.1 Create `guides/SUNO_PROMPT_GUIDE.md` — style prompt rules, structure, non-default policy, meta-tag categories, Suno technical notes
- [x] 5.2 Create `guides/LYRICIST_GUIDE.md` — 7-question song design interview, lyrics writing rules, style blending instructions, end-to-end workflow
- [x] 5.3 Add Sound Designer persona to `guides/LYRICIST_GUIDE.md` — generalized from River Stone Audio, covers genre fluency, production knowledge, Suno workflow
- [x] 5.4 Add Style Blending worked example — Crowbar + Type O Negative blend with full walkthrough: read data → sample lyrics → identify elements → write lyrics → generate prompt
- [x] 5.5 Add era-based filtering instructions — directory name patterns, frontmatter grep commands, era+genre combinations
- [x] 5.6 Validation: ran Crowbar+Portishead blend session. Found gaps: Portishead 0 lyrics, missing suno_style_descriptions, empty enrichment fields. Fixed: added sonic-only reference fallback path to guide, ran enrichment on all artists (1225/1758 songs enriched).

## 5B. Agent Definitions (P1)

> Goal: Specialized agent personas defined using agents.md convention for any AI coding agent to adopt.
> Delivers: Drop-in agent definitions for songwriting sessions.

- [x] 5B.1 Create `AGENTS.md` — universal agent guide (project overview, commands, data layout, schema reference)
- [x] 5B.2 Create `agents/lyricist.md` — lyricist agent persona with database navigation, style analysis, song design interview, writing rules
- [x] 5B.3 Create `agents/producer.md` — music producer agent with Suno mastery, style translation, multi-pass builds, meta-tags

## 6. Metadata Enrichment (P2)

> Goal: Frontmatter fields (`genre`, `mood`, `themes`, `style`, `energy`) are populated, enabling precise filtering.
> Delivers: "Give me all melancholic songs from the '90s" actually works.

- [x] 6.4 Add `genre`/`mood` population from MusicBrainz tags during ingestion — auto-classified at artist, album, and song levels. Added `refresh-tags` command for backfilling.
- [x] 6.1 Define controlled vocabulary — `guides/ENRICHMENT_VOCABULARY.md` with valid values for `mood` (27 values), `style` (21 values), `energy` (8 values), `themes` (32 values)
- [x] 6.2 Create `scripts/enrich.py` — heuristic-based enrichment (keyword matching for mood/themes, energy scoring, genre-to-style mapping). Includes `--dry-run`, `--llm` mode for LLM prompts. Registered as `fetch.py enrich` subcommand.
- [x] 6.3 Enriched all artists: 1225/1758 songs enriched (mood: 1077, themes: 1172, energy: 1225, style: 966). Sleep piloted first.

## 7. Advanced Suno Workflow Documentation (P3)

> Goal: Complex production techniques are documented for when needed.
> Delivers: Reference material for multi-pass Studio builds and post-processing.

- [x] 7.1 Add multi-pass Suno Studio workflow to `guides/SUNO_PROMPT_GUIDE.md` — the 6-pass strategy (foundation → instruments → rhythm → texture → extend → remaster)
- [x] 7.2 Add Suno v5/Studio capability reference — already in guide: Warp Markers, stem separation, Alternates, Time Signature support, credit costs
- [x] 7.3 Add post-processing reference — ffmpeg commands for loop creation, loudness normalization, format conversion
- [x] 7.4 Add instrumental-only techniques section — three-method approach (style prompt + lyrics field + negative prompting) with troubleshooting for vocal leakage

## 8. TUI & Interactive Tools (P2)

> Goal: A terminal UI for browsing the database, selecting genres/moods, and running songwriting sessions.
> Delivers: Interactive workflow that doesn't require memorizing CLI commands.

- [x] 8.1 Create `scripts/tui.py` — textual-based TUI for browsing artists → albums → tracks → lyrics with genre search/filter
- [x] 8.2 Add genre/mood filter — type `genre:doom` in search to filter artists by genre tags
- [x] 8.3 Add songwriting session mode — press `s` in TUI, walks through 7-question interview, shows style references from database, export with `e` to sessions/ directory
- [x] 8.4 Add Suno prompt builder — standalone `scripts/suno_builder.py` TUI with live preview, char/word count, genre/mood/energy selection, reference artist lookup, clipboard copy (`c`), export (`e`)

## 9. Artist Relationships & Discovery (P2)

> Goal: Understand who inspired each artist and suggest similar artists, both in and outside the database.
> Delivers: "I like Crowbar, who else should I listen to?" and "what influenced this band's sound?"

- [x] 9.1 Add MusicBrainz artist relationships to ingestion — fetch members, external links (AllMusic, Last.fm, Discogs, Metal Archives, RYM URLs)
- [x] 9.2 Store relationships in `_artist.md` frontmatter — `members` list, external link URLs. New artists auto-populate on fetch.
- [x] 9.3 Create `fetch.py similar "Artist"` command — query MusicBrainz for artists sharing niche tags, show which are in the database
- [x] 9.4 Create `fetch.py suggest` command — analyze genre/mood patterns across the database and suggest artists that would fill gaps or complement existing collection. Filters "Various Artists"/unknown, requires score >= 50.
- [x] 9.5 Add Genre Map and Shared Tags sections to `_index.md` — groups artists by primary genre, finds pairs sharing niche tags (excludes generic/mood tags)

## 10. Documentation & README (P1)

> Goal: A README.md that explains the project to humans who work with AI agents.
> Delivers: Anyone can clone the repo, understand the purpose, and start using it with Claude/OpenCode/scripts.

- [x] 10.1 Create `README.md` — project overview, setup (with API key instructions + links), CLI usage, agent integration, directory structure, frontmatter schema
- [x] 10.2 Rename project to "Lyra Engine" — updated README, CLAUDE.md, AGENTS.md, fetch.py, tui.py, musicbrainz.py, markdown.py, _index.md

## 11. External Data Sources (P3)

> Goal: Enrich the database with data from additional sources beyond MusicBrainz and Genius.
> Delivers: Richer artist bios, album reviews, and style descriptions for better Suno prompt generation.

- [x] 10.1 Research AllMusic data access — **no public API**. Heavy anti-bot protections (Cloudflare, dynamic rendering). Web scraping is fragile and not recommended for automated ingestion. Manual reference only.
- [ ] 10.2 Add AllMusic scraper to ingestion pipeline — **deferred** (no reliable API/scraping path)
- [ ] 10.3 Add album review summaries from AllMusic to `_album.md` — **deferred** (depends on 10.2)
- [x] 10.4 Evaluate Discogs API — **viable**. Free public API with OAuth (discogs.com/developers). Provides genres, styles, tracklists, label info, artist profiles. Rate limit: 60 req/min authenticated.
- [ ] 10.5 Add lyrics URL fallback — when Genius fails, search alternative lyrics sites (AZLyrics, MetroLyrics) via web search
