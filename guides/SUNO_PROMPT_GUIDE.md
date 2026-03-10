# Suno Prompt Guide — Style Prompt Reference

> Consolidated from prior research. Use this when generating Suno style prompts from the lyrics database.

## Suno Style Prompt Rules

- **Under 180 words / 1000 characters** (Suno's style field limit)
- **No artist names** — Suno strips them. Translate references into descriptive language.
- No stacked synonyms ("dark, brooding, ominous, foreboding" — pick one)
- No contradictory descriptors
- Use concrete instrumentation terms
- No narrative storytelling in the style prompt
- No overly abstract emotional language

## Style Prompt Structure

Single paragraph, this order:

1. **Genre + Era context** — anchor the sound
2. **Primary instrumentation** — specific instrument names
3. **Rhythm character** — beat feel, groove type
4. **Vocal description** — type, delivery, mic treatment
5. **Energy movement** — dynamic arc through the song
6. **Production texture** — analog/digital, lo-fi/clean, spatial character
7. **Tempo range** (optional) — BPM when it matters

## Non-Default Policy

Do NOT assume unless explicitly requested:
- Minor key
- Aggressive tone
- Industrial elements
- Male vocals
- Slow build into chaos
- Collapse metaphors
- Epic cinematic arc

## Prompt Building Framework (Detailed)

### Identity Block
Genre fusion, era/texture, energy trajectory.
> "Slow-building industrial rock with dark late-90s alternative industrial atmosphere and modern cinematic metal intensity."

### Palette Block
Instrument descriptions by class.
> "Thick low-tuned high-gain distorted guitars, analog synth drones, pulsing sub-bass, industrial percussion like distant machinery."

### Vocals Block
Vocal type, delivery changes per section, effects.
> "Deep male baritone, spoken at first, evolving to strained and distorted. Close-mic'd and dry in verses."

### Dynamics Block
How the song moves through sections.
> "Begins minimal and spacious. Gradually builds density. Climax feels chaotic and unraveling."

### Constraints Block
What to avoid.
> "Avoid polished modern rock sheen. Texture should feel analog, imperfect, and emotionally raw."

### Production Notes
Tempo, key, overall character.
> "Tempo 95-100 BPM. Minor key. Cinematic dynamic arc from restraint to density to collapse to stillness."

## Translating Artist References to Suno-Safe Descriptions

Since Suno strips artist names, use these sources to build descriptions:
- **AllMusic** (allmusic.com) — Styles, Moods, editorial descriptions
- **Discogs** — Genre and style tags
- **Rate Your Music** — Detailed community descriptors
- **MusicBrainz** — Open metadata tags
- **This database** — Read `_artist.md` for genre/style info, sample lyrics for thematic patterns

### Translation Process
1. Look up the artist's listed **Styles** and **Moods**
2. Note the **era** and production characteristics
3. Identify signature **instruments** and **vocal style**
4. Combine: era + genre + mood + production texture + instruments

### Example Translations

| Artist Reference | Suno-Safe Description |
|---|---|
| Nine Inch Nails (The Fragile) | late-90s alternative industrial, emotionally raw, layered analog synth textures, introspective darkness with dynamic builds |
| Nine Inch Nails (Pretty Hate Machine) | late-80s synth-driven industrial rock, sequenced electronic beats, cold wave influence, angular synths |
| Nine Inch Nails (The Downward Spiral) | mid-90s aggressive industrial rock, harsh noise textures, distorted vocals, layered abrasive production |
| Radiohead (Kid A) | experimental electronic rock, glitchy textures, ambient layers, emotionally detached, avant-garde pop structures |
| Massive Attack | trip-hop, dark atmospheric downtempo, heavy bass, cinematic moody textures, sparse and brooding |
| Depeche Mode | dark synthpop, melancholic electronic rock, warm analog synths, emotionally vulnerable baritone vocals |
| Tool | progressive alternative metal, complex time signatures, atmospheric tension, philosophical and introspective |
| Ministry (Psalm 69) | early-90s mechanical industrial metal, jackhammer guitar riffs, relentless pounding percussion, aggressive and abrasive |

## Meta-Tag Categories

| Category | Tags |
|----------|------|
| **Sound staging** | "wide stereo image", "organic reverb tail", "spacious decay", "intimate close-mic" |
| **Timbre** | "warm analog tone", "icy digital textures", "airy breath textures", "earthy organic" |
| **Motion** | "slow-evolving layers", "glacial pacing", "minimal rhythmic emphasis", "building intensity" |
| **Mix** | "clean mix high fidelity", "clear separation between instruments", "lo-fi texture" |
| **Loop** | "seamless loop", "loop-friendly", "soft reverb tail", "loop-ready" |

## Instrumental-Only Techniques

Three methods combined for best results:
1. **Style prompt**: Include "instrumental, no vocals" near the beginning
2. **Lyrics field**: Leave empty OR enter only `[Instrumental]`
3. **Negative prompting**: "no vocals, no singing, no humming, no choir, no voice"

## Suno Technical Notes

- **Model**: v5 (Sep 2025) — 44.1kHz stereo, superior prompt adherence
- **Studio**: Warp Markers, Remove FX, Alternates, Time Signature support (Feb 2026)
- **Output**: MP3 192kbps (all plans), WAV 48kHz lossless (Pro/Premier)
- **Stems**: Up to 12 time-aligned WAV stems via Studio
- **Credits**: ~5 credits per generation
- **Extend**: Up to 1 min per extension, chainable, "Get Whole Song" stitches together
