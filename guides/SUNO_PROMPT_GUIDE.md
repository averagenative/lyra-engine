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
| Crowbar | heavy sludge doom metal, thick downtuned crushing riffs, slow groove-based rhythms, gravelly raw vocals, warm organic production |
| Type O Negative | dark gothic metal, deep baritone vocals, analog synth organ pads, deadpan delivery, slow plodding bass, theatrical melancholy |
| Deftones | heavy alternative metal with shoegaze textures, reverb-soaked layered guitars, breathy intimate vocals building to anthemic choruses, hypnotic groove |
| Opeth | progressive death metal, acoustic folk passages contrasting with heavy growled sections, dynamic quiet-loud architecture, intricate arrangements |
| Sleep | ultra-heavy stoner doom metal, massive fuzz-drenched guitar riffs, glacial tempos, droning repetitive grooves, hypnotic psychedelic heaviness |
| Cannibal Corpse | brutal death metal, blast beats, guttural growled vocals, rapid tremolo-picked guitars, relentless aggression, technical precision |
| Spiritbox | modern progressive metalcore, djent-influenced polyrhythmic guitars, clean ethereal female vocals contrasting with harsh screams, atmospheric electronic textures |
| Kublai Khan TX | aggressive beatdown hardcore with groove metal influence, breakdown-heavy, shouted vocals, crushing mid-tempo rhythms, raw pit energy |
| Sanguisugabogg | lo-fi death metal, sludgy downtuned grooves, guttural vocals, caveman riffs, raw filthy production |
| Portishead | dark trip-hop, melancholic downtempo, haunting female vocals, vinyl crackle textures, cinematic orchestral samples, sparse brooding atmosphere |

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

## Multi-Pass Studio Workflow

For complex productions, use Suno Studio's layered approach:

1. **Foundation pass** — Generate core rhythm and chord progression. Use a simplified prompt focusing on genre, tempo, and basic instrumentation.
2. **Instrument pass** — Add lead instruments and melodic elements using Alternates. Keep what works, regenerate what doesn't.
3. **Rhythm pass** — Refine the beat. Use stem separation to isolate drums, then layer additional percussion if needed.
4. **Texture pass** — Add ambient layers, effects, ear candy. Use "soft reverb tail", "atmospheric pad" type descriptors.
5. **Extend pass** — Build full arrangement via extensions. Each extension adds up to 1 minute. Use "Get Whole Song" to stitch.
6. **Remaster pass** — Use Studio's Remove FX and Warp Markers for final polish. Adjust timing, clean up artifacts.

### When to Use Multi-Pass

- Songs with multiple distinct sections (quiet intro → heavy verse → ambient bridge)
- Complex genre blends where a single prompt can't capture everything
- Tracks where specific instruments need to be prominent
- When the first generation is 80% right but needs targeted fixes

## Instrumental-Only Techniques

Three methods combined for best results:

1. **Style prompt**: Include "instrumental, no vocals" near the beginning
2. **Lyrics field**: Leave empty OR enter only `[Instrumental]`
3. **Negative prompting**: Add "no vocals, no singing, no humming, no choir, no voice" to the style prompt

### Troubleshooting Vocal Leakage

If vocals still appear:
- Move "instrumental" to the very start of the style prompt
- Add more specific negations: "no whispered vocals, no background vocals, no vocal harmonies"
- Use stem separation in Studio to isolate and remove vocal stems
- Try regenerating with Alternates — some takes will be cleaner than others
- Reduce prompt complexity — too many descriptors can confuse the model

## Post-Processing Reference

### Loop Creation (ffmpeg)
```bash
# Create seamless loop with crossfade
ffmpeg -i input.wav -af "afade=t=out:st=55:d=5" -t 60 output_fade.wav

# Trim to exact loop point
ffmpeg -i input.wav -ss 0.0 -to 30.0 -c copy loop.wav

# Crossfade loop (overlap start and end)
ffmpeg -i input.wav -filter_complex "[0]atrim=0:28[a];[0]atrim=26:30[b];[a][b]acrossfade=d=2:c1=tri:c2=tri" loop.wav
```

### Loudness Normalization
```bash
# EBU R128 normalization (-14 LUFS, standard for streaming)
ffmpeg -i input.wav -af loudnorm=I=-14:TP=-1:LRA=11 output.wav

# Game audio normalization (-16 LUFS, more headroom for SFX)
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-2:LRA=7 output.wav

# Measure loudness without processing
ffmpeg -i input.wav -af loudnorm=print_format=json -f null -
```

### Format Conversion
```bash
# WAV to OGG Vorbis (web/game audio, good compression)
ffmpeg -i input.wav -c:a libvorbis -q:a 6 output.ogg

# WAV to MP3 (universal compatibility)
ffmpeg -i input.wav -c:a libmp3lame -b:a 320k output.mp3

# MP3 to WAV (for editing, no quality gain)
ffmpeg -i input.mp3 output.wav
```

## Suno Technical Notes

- **Model**: v5 (Sep 2025) — 44.1kHz stereo, superior prompt adherence
- **Studio**: Warp Markers, Remove FX, Alternates, Time Signature support (Feb 2026)
- **Output**: MP3 192kbps (all plans), WAV 48kHz lossless (Pro/Premier)
- **Stems**: Up to 12 time-aligned WAV stems via Studio
- **Credits**: ~5 credits per generation
- **Extend**: Up to 1 min per extension, chainable, "Get Whole Song" stitches together
