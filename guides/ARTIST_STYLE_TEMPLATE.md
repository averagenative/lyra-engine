# Artist Style Template — Suno-Safe Description Writing Guide

> Use this template to write a `suno_style_description` for any artist in the database. The result should be a single paragraph that captures the artist's sound without using their name.

## Research Process

### Step 1: Read the Database

- Open `artists/{Artist}/_artist.md` — note genre, mood, musicbrainz_tags, era (active_years)
- Open 2-3 `_album.md` files — note how genre/mood shifts across albums
- Read 3-5 representative songs — note vocabulary, emotional register, imagery

### Step 2: Identify Sonic Signature

Fill in these fields by analyzing the data:

```
Primary Genre(s):     _______________
Era / Decade:         _______________
Subgenre Modifiers:   _______________

Guitar Tone:          _______________ (e.g., "thick downtuned", "jangly clean", "shoegaze reverb")
Bass Character:       _______________ (e.g., "deep melodic", "distorted rumble", "synth bass")
Drum Feel:            _______________ (e.g., "thunderous kick-heavy", "mechanical", "jazz-influenced")
Keys / Synths:        _______________ (e.g., "analog synth drones", "organ pads", "none")
Other Instruments:    _______________ (e.g., "strings", "samples", "turntables")

Vocal Type:           _______________ (e.g., "deep baritone", "female soprano", "dual vocalists")
Vocal Delivery:       _______________ (e.g., "whispered verses, screamed chorus", "deadpan", "melodic")
Vocal Character:      _______________ (e.g., "emotionally raw", "detached", "theatrical")

Tempo Range:          _______________ (e.g., "slow 60-80 BPM", "mid-tempo 100-120", "fast 160+")
Energy Arc:           _______________ (e.g., "quiet-loud dynamics", "relentless intensity", "slow build")
Dynamic Range:        _______________ (e.g., "huge contrast", "consistently heavy", "subtle shifts")

Production Texture:   _______________ (e.g., "warm analog", "sterile digital", "lo-fi", "pristine")
Spatial Character:    _______________ (e.g., "cavernous reverb", "dry and intimate", "wide stereo")
Mix Aesthetic:        _______________ (e.g., "wall of sound", "clear separation", "muddy and raw")
```

### Step 3: Write the Description

Combine into a single paragraph following this order:

1. **Genre + Era** — "Heavy sludge doom metal from the early 1990s..."
2. **Instrumentation** — "Thick downtuned guitars with sustained crushing riffs..."
3. **Rhythm** — "...over slow to mid-tempo rhythms emphasizing weight and groove"
4. **Vocals** — "Vocals are raw and gravelly, mid-range delivery..."
5. **Energy** — "Energy oscillates between crushing despair and defiant empowerment..."
6. **Production** — "Production is warm and organic, guitar tones thick and syrupy..."

### Step 4: Validate

- [ ] Under 180 words / 1000 characters?
- [ ] No artist names anywhere?
- [ ] No stacked synonyms (pick ONE descriptor per quality)?
- [ ] No contradictions?
- [ ] Uses concrete instrument names, not vague terms?
- [ ] Captures what makes THIS artist different from others in their genre?

## Examples

### Deftones (Alternative Metal / Shoegaze)
> Heavy alternative metal with shoegaze-influenced textures from the early 2000s, blending introspective vulnerability with dense atmospheric production. Layered, reverb-soaked guitars create a shimmering yet crushing sonic landscape over deep melodic bass and steady, hypnotic drumming. Rhythmic foundation emphasizes groove and meditative tension rather than speed — songs build gradually from quiet, breathy verses into powerful anthemic choruses. Vocals are intimate and evocative, delivered with quiet intensity that swells into haunting sung hooks and chant-like repetitions, emphasizing melody and atmosphere over aggression. Production is pristine and layered, creating space while maintaining crushing density. Energy is hypnotic and darkly introspective — melodic yet ominous, aggressive yet emotionally vulnerable, with architectural dynamics between quietude and overwhelming sound.

### Crowbar (Sludge / Doom Metal)
> Heavy sludge-influenced doom metal rooted in the early 1990s Louisiana metal scene. Thick downtuned guitars with sustained crushing riffs dominate over slow to mid-tempo rhythms emphasizing weight and groove. Vocals are raw and emotionally direct — gravelly mid-range delivery with minimal melodic ornamentation, conveying pain and introspection. Heavily distorted bass, thunderous drums with prominent kick patterns, and minimal lead guitar maintain a wall-of-sound approach. Production is warm and organic despite heaviness — guitar tones are thick and syrupy, not sterile — creating an almost hypnotic meditative quality despite abrasive content. Energy oscillates between crushing despair and defiant empowerment, with consistent emphasis on groove-based heaviness rather than technical virtuosity or speed.

### Type O Negative (Gothic Metal)
> Deep dark gothic metal with theatrical flair from the early 90s underground. Resonant baritone vocals drive hypnotic melancholic melodies over heavy drop-tuned guitars anchored by prominent analog synthesizers and deep plodding bass. Vocal delivery oscillates between deadpan spoken-word verses and melodic choruses, occasionally shifting into raw emotional outbursts. Rhythms move deliberately slow to mid-tempo with industrial-tinged production balancing organic heaviness against synthetic textures like organ and synth pads. The aesthetic is morose yet darkly theatrical — cinematic, introspective, and unapologetically bleak, embracing gothic horror imagery blended with dark humor and pagan mysticism.

## Album-Level Descriptions

Artists often sound different across eras. When an album diverges significantly from the artist's overall sound, write an album-level `suno_style_description` in `_album.md`. Use the same template but focus on what makes that specific album distinct.

Example: An artist's early work might be "raw lo-fi garage punk" while their later albums are "polished art rock with orchestral arrangements." These need separate descriptions.
