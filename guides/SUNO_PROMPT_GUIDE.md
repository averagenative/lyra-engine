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
| Mudvayne (L.D. 50) | early-2000s technical progressive metal with jazz-fusion bass, downtuned angular staccato riffs, prominent slap-and-tap bass as lead instrument, polyrhythmic odd-time drumming with jazz ghost notes, violent shifts between guttural screams and melodic singing, mathematical rhythmic complexity, tight compressed production |
| Mudvayne (The End of All Things to Come) | dark atmospheric progressive metal, jazz-influenced bass, spacious quiet verses building to crushing downtuned heaviness, angular dissonant riffs over polyrhythmic odd-time drums, wide dynamic vocal range from haunting melodies to guttural screams, mathematical precision |
| Slipknot (self-titled/Iowa era) | late-90s extreme groove metal, heavily downtuned dual-guitar palm-muted chugging over relentless double bass drums, layered multi-percussion assault with industrial found-object hits, turntable scratches and horror-noise samples, raw analog production, harsh screamed vocals alternating with guttural growls, suffocating wall-of-sound density |
| Slipknot (Vol. 3/All Hope Is Gone era) | mid-2000s heavy groove metal with melodic hooks, thick downtuned drop-B guitar riffs with dissonant lead lines, aggressive double-kick drumming over polyrhythmic auxiliary percussion, harsh screamed verses building to anthemic melodic choruses, polished compressed production, turntable textures and atmospheric sampling |
| Slipknot (We Are Not Your Kind era) | modern atmospheric heavy metal, angular dissonant guitar riffs over pounding groove-metal rhythms, electronic textures and glitch samples layered into dense metal production, dynamic shifts between spacious dark verses and crushing walls of distortion, extreme vocal range from whispered menace to guttural screams to soaring melodies |
| Mudvayne (Lost and Found) | heavy groove metal with technical progressive bass, downtuned palm-muted chugging, aggressive slap bass driving rhythm, polyrhythmic drumming, assertive male vocals alternating fierce screams and confident melody |

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

## Hard Lessons: Heavy/Extreme Metal Prompts

These patterns were discovered through extensive trial and error generating groove metal / extreme metal tracks (March 2026).

### Style Prompt Pitfalls

- **Keep style prompts short and blunt** — the more descriptive words you give Suno, the more it cherry-picks the wrong ones and drifts
- **Explicit negatives matter** — "No melody, no clean singing, no rap, no spoken word" actively prevents drift. Without them, Suno will sneak in melodic passages
- **"Tribal" triggers Soulfly/Sepultura world-music percussion** — use "mechanical" or "relentless" instead for heavy drumming
- **"Nine-piece chaotic energy" or anything Slipknot-adjacent** triggers nu-metal rap-rock vocal delivery
- **"Scandinavian extreme metal"** can overcorrect into black metal shrieks — be specific about what vocal style you want
- **"Gang-vocal chants"** — Suno reads "chants" as singalong/melodic. Drop it or say "shouted group vocals"
- **Dynamic arc language** ("building to", "menacing stomp building to explosive") gives Suno permission to create melodic shape and go radio-rock. Cut it for heavy genres
- **"Anthemic"** will make anything sound like arena rock. Avoid for extreme metal

### Lyric Pitfalls That Cause Vocal Style Drift

- **Too many syllables per line → rap cadence** — if lines are dense/wordy (8+ syllables strung together with internal rhyme), Suno defaults to rap-rock delivery to fit them in
- **Iambic meter → sing-song/butt-rock** — lines with steady da-DUM da-DUM da-DUM rhythm get sung like Nickelback. Break the meter with uneven line lengths and hard consonant clusters
- **Poetic/literary language → radio rock** — clean metaphors and complete sentences sound "pretty" to Suno. Use fragmented, visceral, first-person language instead
- **Multi-syllable words in breakdowns → electronic/bouncy** — "Complicit in the turning" went electronic. Single-word barks ("Kneel / Crawl / Bleed / FALL") are Suno-proof
- **Political commentary voice → spoken word/rap** — observational third-person political lyrics trigger speech-like delivery. First-person body-horror/visceral voice stays screamed

### What Works for Extreme Metal

- **Short style prompt** (~60-80 words), blunt genre terms, explicit negatives
- **4-6 syllables per line** in verses — fragments, not sentences
- **Broken meter** — alternate between short and long lines, no steady rhythm
- **Hard consonants** — "stripped", "gorged", "chokes", "scrape" — ugly mouth-feel that can't be sung pretty
- **First-person visceral voice** — "I can feel it in the walls" not "The empire crumbles"
- **Single-word or two-word breakdowns** — least room for Suno to improvise wrong
- **Explicit language helps** — "fuck" and "shit" anchor Suno in aggressive vocal delivery

### Example: Working Extreme Groove Metal Prompt

> Extreme low-tuned 8-string groove metal. Polyrhythmic palm-muted chugging, mechanical double bass drums, dissonant angular guitar riffs. Harsh screamed male vocals, guttural and abrasive throughout. No melody, no clean singing, no rap, no spoken word. Industrial percussion hits. Claustrophobic wall-of-sound production. Mathematical rhythmic complexity. Mid-tempo crushing heaviness. Diminished minor key. 105-115 BPM.

## Artist Deep Dive: Slipknot-Style Prompt Engineering

Slipknot is one of the hardest bands to translate into Suno prompts because of their unique instrumentation (nine members), vocal diversity, and the fact that obvious descriptors like "nine-piece chaotic energy" trigger nu-metal rap-rock in Suno rather than the intended heavy groove metal. This section documents their signature techniques and how to translate each into Suno-safe language.

### Guitar: Dual-Guitar Dynamic

**Mick Thomson (#7) — Rhythm/Low-End**
- Death metal roots (played in Body Pit with Paul Gray; influenced by Internal Bleeding, Morbid Angel)
- Primary tuning: Drop B (B-F#-B-E-G#-C#) across most of their discography
- Signature technique: heavy palm-muted chugging, percussive staccato riffing, repetitive groove-locked patterns
- Gear evolution: B.C. Rich Warlocks with dual EMG humbuckers -> Ibanez MTM with Seymour Duncan EMTY Blackout pickups -> Jackson Double Rhoads/Soloist -> ESP with Fishman pickups
- Effects: Maxon OD820 overdrive, Death by Audio Fuzz War, MXR Carbon Copy delay, Electro-Harmonix Bassballs envelope filter
- Strings: d'Addario EXL117 (medium-top/extra-heavy-bottom, built for drop tuning)

**Jim Root (#4) — Lead/Atmospheric**
- Unusual for metal: plays Fender signature Telecaster, Jazzmaster, and Stratocaster models (single-humbucker configurations)
- Amps: Orange Rockerverb heads live; Bogner Uberschall and Mesa Boogie Mark IIC in studio
- EMG Retroactive pickups (later signature set)
- Provides higher-register melodic leads, dissonant textures, and atmospheric guitar layers
- Introduced guitar solos and acoustic passages starting on Vol. 3 (2004)
- Described his role: "In both bands, I fulfill both roles... Mick has some solos" — twin-guitar interplay rather than strict rhythm/lead split

**Suno translation**: "heavily downtuned drop-B dual-guitar attack, percussive palm-muted chugging locked to the kick drums, dissonant angular lead lines over crushing low-end riffs" — avoid "twin guitar harmonies" (triggers Iron Maiden-style melodic metal)

### Percussion: The Three-Percussionist Wall

**Joey Jordison (#1) / Jay Weinberg / Eloy Casagrande — Drums**
- Jordison: self-taught, then trained in R&B and jazz technique (credited this for his musical diversity)
- Blast beats, rapid double bass drum patterns, death metal speed combined with groove-metal pocket
- Rolling Stone described the combined percussion as "suffocating"

**Shawn "Clown" Crahan (#6) — Custom Percussion**
- Hits custom keg drums, metal barrels, baseball bats on industrial objects
- Creates non-pitched, industrial-sounding percussive accents

**Chris Fehn (#3) / Michael Pfaff — Custom Percussion**
- Additional layer of auxiliary percussion reinforcing Crahan's industrial hits
- Concert toms, modified drums, found-object percussion

**Combined effect**: Three simultaneous percussion sources create a dense rhythmic wall — conventional kit drumming (double bass, blast beats) layered with non-pitched industrial strikes and auxiliary tom patterns. This is the signature that makes Slipknot sound "bigger" than a standard metal band.

**Suno translation**: "relentless double bass drums under layered industrial percussion hits, metallic found-object strikes reinforcing the beat, dense polyrhythmic drum assault" — do NOT use "tribal percussion" (triggers Soulfly world-music) or "nine-piece chaotic energy" (triggers rap-rock)

### DJ/Sampler Elements

**Sid Wilson (#0) — Turntables/Keys**
- Contributes scratching, horror-like noise, sound effects, background textures
- Also a jungle/drum-and-bass DJ (solo career as DJ Starscream)
- Role evolved from prominent turntable scratches (self-titled, Iowa) to more integrated electronic textures (later albums)

**Craig Jones (#5) — Sampling/Keyboards**
- Programmed samples, atmospheric pads, noise elements
- Less visible but provides the electronic "glue" between sections

**Suno translation**: "turntable scratch accents and horror-noise samples woven into heavy guitars" (for early era) or "electronic textures and glitch samples layered into dense metal production" (for later era) — avoid "DJ" alone (triggers hip-hop)

### Vocal Style: Corey Taylor's Range

Taylor deploys at least five distinct vocal modes, often within the same song:

| Mode | Description | Song Examples | Suno Trigger Risk |
|------|-------------|---------------|-------------------|
| **Guttural death growl** | Low, guttural, sub-bass vocal register | "People = Shit" verses, "Disasterpiece" | Low risk — Suno handles growls well |
| **High-pitched scream** | Strained, aggressive, mid-to-high range | "(sic)", "Heretic Anthem", "Eyeless" | Low risk with "harsh screamed vocals" |
| **Melodic clean singing** | Full-voiced, anthemic, rock tenor | "Duality" chorus, "Vermilion Pt. 2", "Snuff", "Dead Memories" | HIGH RISK — Suno over-indexes on melody and goes radio-rock |
| **Spoken word/menacing** | Whispered or spoken, building tension | "Iowa" (title track), "Gently" intro | Medium risk — can trigger spoken-word poetry delivery |
| **Rap cadence** | Rhythmic, hip-hop-influenced delivery | "Spit It Out", early tracks | HIGH RISK — Suno will latch onto this and go full rap-rock |

**Suno translation for aggressive tracks**: "harsh screamed male vocals, guttural and abrasive, with occasional anthemic melodic breaks" — the key is making clean singing the exception, not the rule. For mixed vocal tracks, specify "predominantly harsh screamed vocals with brief melodic chorus hooks" to prevent Suno from defaulting to singing throughout.

**Suno translation for melodic tracks** (Duality, Vermilion, Snuff type): "aggressive alternative metal vocals alternating between strained melodic singing and harsh screams, emotionally raw delivery"

### Tone and Production Evolution

| Album | Year | Producer | Sonic Character |
|-------|------|----------|-----------------|
| **Slipknot** | 1999 | Ross Robinson | Raw, chaotic, live-feel. Drums recorded in 3 days. Entire album mixed on analog equipment (month-long mix of "Purity" alone). Robinson cut experimental sections for straightforward metal attack. Dense percussion/turntable/sample layering. |
| **Iowa** | 2001 | Ross Robinson | Darker, more technical. Robinson captured precision over raw energy. Death metal influence increased. NME: "every possible space covered in scrawl and cymbals: guitars, percussion, electronic squall, subhuman screaming." Less hip-hop, more extreme metal. 15-minute title track. |
| **Vol. 3** | 2004 | Rick Rubin | First melodic structures, guitar solos, acoustic instruments. Polished production. "Differing textures." BBC: "hyperactive bass drums, complex compelling riffs, ridiculously fast fretwork." Rolling Stone: "newer extremes... tunefulness and traditional song structures." |
| **All Hope Is Gone** | 2008 | Dave Fortman | Most eclectic. Full groove metal with death metal and thrash elements. All nine members writing. Taylor+Root+Wilson+Crahan worked on "oblique, arty pieces." Band members later criticized it as rushed. Mixed by Colin Richardson. |
| **We Are Not Your Kind** | 2019 | Greg Fidelman | Atmospheric, experimental. Angular dissonance. Electronic textures more integrated. Dynamic range from spacious to crushing. |

**Key production insight for Suno**: The Ross Robinson era (1999-2001) is best translated as "raw analog production, claustrophobic wall-of-sound density, every frequency saturated." The Rubin and later era is "polished compressed production with dynamic contrast between sparse and dense sections."

### Key Song Technical Breakdowns

**"Wait and Bleed" (1999)** — Drop B, 165 BPM. Melodic chorus hook over aggressive verses. Taylor's first showcase of scream-to-melody range. Fast double bass under relatively simple riff structure. The song that proved Slipknot could write hooks. *Suno approach*: aggressive alternative metal, fast tempo, harsh verses with melodic chorus breaks.

**"(sic)" (1999)** — Drop B, staccato palm-muted riff locked to kick drum. Turntable scratches prominent. Pure aggression, no clean vocals. Repetitive hypnotic groove. *Suno approach*: repetitive downtuned groove metal, turntable scratch accents, harsh vocals throughout.

**"People = Shit" (2001)** — Drop B, blast beat intro, death metal intensity. MusicBrainz tags include death metal, deathgrind. Relentless double bass, layered percussion. Taylor at most aggressive. *Suno approach*: extreme groove metal bordering on death metal, blast beats, guttural screamed vocals, industrial percussion hits.

**"Disasterpiece" (2001)** — Drop B, Grammy-winning. Opens with Taylor screaming "I wanna slit your throat and fuck the wound." Maximum density — all nine members at full volume. Death metal influence most apparent. *Suno approach*: extreme downtuned metal, suffocating layered percussion, harsh guttural vocals, claustrophobic production.

**"Duality" (2004)** — Drop B, 135 BPM. Anthemic verse-chorus structure with melodic hook ("I push my fingers into my eyes"). Heavy palm-muted verse riff, open melodic chorus. First big Slipknot "single" with traditional song structure. *Suno approach*: heavy alternative metal with anthemic melodic choruses, downtuned chugging verses building to emotional hooks, harsh-to-clean vocal dynamics.

**"Before I Forget" (2004)** — Drop B, groove-locked riff, melodic chorus. Grammy for Best Metal Performance. Demonstrates the Pantera-influenced groove hallmark. *Suno approach*: mid-tempo groove metal, thick rhythmic palm-muted riff, melodic singing over heavy instrumentation.

**"Psychosocial" (2008)** — Drop B, groove metal anthem. Staccato riff, gang-vocal chant chorus. MusicBrainz: groove metal, rhythmic. Thrash metal guitar work with melodic vocal hooks. *Suno approach*: driving groove metal, rhythmic staccato guitar riffs, shouted group vocal hooks over double-kick drumming.

**"Sulfur" (2008)** — Written by Jordison and Root in one evening. Melodic lead guitar over heavy rhythm section. Clean singing prominent. *Suno approach*: atmospheric heavy metal, melodic guitar leads over crushing rhythm section, strained emotional singing with harsh screamed bridges.

**"The Devil in I" (2014)** — Post-Gray/Jordison era. Mature songwriting, atmospheric intro building to heavy groove. Dynamic range. *Suno approach*: dark atmospheric groove metal, spacious intro building to crushing mid-tempo heaviness, emotionally strained vocals.

### Suno Prompt Templates

**Template: Early Slipknot (Self-Titled/Iowa) — Pure Aggression**

> Extreme downtuned groove metal. Percussive palm-muted drop-B guitar chugging locked to relentless double bass drums, layered industrial percussion hits and metallic strikes reinforcing every beat. Harsh screamed male vocals, guttural and unrelenting. Turntable scratch accents and horror-noise samples. Raw analog claustrophobic wall-of-sound production. No clean singing, no melody, no rap. 130-170 BPM.

- **Weirdness**: 45-55%
- **Style Influence**: 70-80%
- **Exclude**: pop rock, radio rock, melodic, clean vocals, rap, hip-hop, spoken word

**Template: Mid-Era Slipknot (Vol. 3/All Hope Is Gone) — Groove + Melody**

> Heavy groove metal with anthemic hooks. Thick downtuned dual-guitar palm-muted chugging over pounding double-kick drums and layered auxiliary percussion. Harsh screamed verses building to strained melodic choruses with emotional intensity. Polished compressed production with dense layered instrumentation. Electronic textures and turntable accents woven into heavy guitars. 120-140 BPM.

- **Weirdness**: 35-45%
- **Style Influence**: 60-70%
- **Exclude**: pop rock, radio rock, arena rock, rap, hip-hop, acoustic, folk

**Template: Late Slipknot (WANYK/TESF) — Atmospheric + Heavy**

> Dark atmospheric groove metal with experimental electronic textures. Angular dissonant guitar riffs over pounding mid-tempo drums, glitch samples and ambient noise layered into crushing distorted guitars. Wide dynamic shifts from spacious menacing verses to suffocating walls of sound. Harsh screamed vocals alternating with strained emotional melodies. Modern compressed production. 110-130 BPM.

- **Weirdness**: 50-60%
- **Style Influence**: 65-75%
- **Exclude**: pop rock, radio rock, arena rock, nu-metal rap-rock, clean production, bright

### Critical Suno Pitfalls for Slipknot-Style

- **"Nine-piece chaotic energy"** -> triggers nu-metal rap-rock. Use "layered industrial percussion hits reinforcing double-kick drums" instead
- **"Chaotic" alone** -> Suno reads as "messy/unstructured" rather than "dense/intense." Use "suffocating" or "claustrophobic" or "dense wall-of-sound"
- **"Turntablist"** -> triggers hip-hop. Use "turntable scratch accents" or "electronic noise textures"
- **"Percussion ensemble"** -> triggers world music. Use "layered industrial percussion" or "metallic found-object strikes"
- **"Dual vocals"** -> Suno may add a second vocalist. Use "harsh screamed vocals with occasional melodic breaks" for one singer doing both
- **"Groove metal"** alone works well but may land closer to Pantera/Lamb of God than Slipknot — add "layered industrial percussion" and "electronic textures" to differentiate
- **"Alternative metal"** alone -> too vague, can trigger Deftones-style shoegaze or RHCP funk-metal. Pair with "groove metal" and specific instrumentation

## Suno Generation Settings

Beyond the style prompt, Suno exposes three settings that significantly shape output. These interact with the style prompt and should be tuned together.

### Weirdness (0-100%)

Controls how much Suno deviates from conventional song structure, melody, and arrangement.

| Range | Effect | Best For |
|-------|--------|----------|
| 0-20% | Very conventional, predictable | Pop, radio rock, anything that needs to sound "normal" |
| 25-40% | Slight edge, minor surprises | Hard rock, metal, post-grunge — structured but not sterile |
| 40-55% | Noticeable experimentation | Progressive, industrial, sludge — room for texture and chaos |
| 55-75% | Significant deviation | Experimental, noise rock, avant-garde — expect the unexpected |
| 75-100% | Full chaos | Ambient, drone, sound design — less "song," more "experience" |

**Key insight**: Low weirdness + heavy style prompt can produce overly clean, "default singer" results even for aggressive genres. If the output sounds too polished or commercial, bump weirdness up 10-15% before rewriting the prompt.

### Style Influence (0-100%)

Controls how strongly Suno follows your style prompt vs. its own interpretation.

| Range | Effect | Best For |
|-------|--------|----------|
| 0-30% | Style prompt is a loose suggestion | When you want Suno to surprise you |
| 35-50% | Balanced — Suno follows the vibe but improvises | General use, first attempts |
| 50-70% | Strong adherence to your descriptors | Specific genre targets, when your prompt is dialed in |
| 70-85% | Very literal interpretation | Niche genres, precise production goals |
| 85-100% | Maximum control | When you know exactly what you want and the prompt is proven |

**Key insight**: High style influence only works well with a good prompt. A vague prompt at 80% influence will produce repetitive, flat results. A specific prompt at 80% will lock in exactly what you want.

### Exclude Styles

A comma-separated list of styles/genres Suno should actively avoid. This is often more effective than trying to describe what you want — it removes the failure modes.

**Common exclusion sets by target genre:**

| Target Sound | Exclude |
|--------------|---------|
| Heavy metal / hard rock | pop, electronic, synth, jazz, funk, country |
| Raw / aggressive metal | pop rock, radio rock, arena rock, melodic, clean vocals |
| Industrial / dark | acoustic, folk, bright, upbeat, cheerful |
| Lo-fi / raw production | polished, hi-fi, overproduced, commercial |
| Extreme metal | melodic, singing, rap, spoken word, clean |

**Key insight**: If Suno keeps drifting toward a "default" vocal delivery or production style, exclusions are often the fastest fix. Adding `pop rock, radio rock, melodic` eliminates the most common drift targets for heavy genres.

### Settings Interaction

These three settings interact — here are proven combinations:

| Goal | Weirdness | Style Influence | Exclusions |
|------|-----------|-----------------|------------|
| Clean radio rock | 15-25% | 50-60% | experimental, noise, lo-fi |
| Early 2000s metal | 35-45% | 60-70% | pop rock, radio rock, arena rock, melodic |
| Raw sludge / doom | 45-55% | 55-65% | pop, melodic, clean, bright |
| Experimental / industrial | 55-70% | 65-75% | pop, acoustic, folk, country |
| Extreme metal | 40-50% | 70-80% | melodic, singing, rap, spoken word, clean |

## Suno Technical Notes

- **Model**: v5 (Sep 2025) — 44.1kHz stereo, superior prompt adherence
- **Studio**: Warp Markers, Remove FX, Alternates, Time Signature support (Feb 2026)
- **Output**: MP3 192kbps (all plans), WAV 48kHz lossless (Pro/Premier)
- **Stems**: Up to 12 time-aligned WAV stems via Studio
- **Credits**: ~5 credits per generation
- **Extend**: Up to 1 min per extension, chainable, "Get Whole Song" stitches together
