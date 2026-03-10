# Lyricist Guide — Agent Reference for Writing Lyrics

> How to use the lyrics database to write new songs. For AI agents and humans.

## Using the Database for Style Reference

### Finding Reference Material

1. **By artist**: Read `artists/{Artist}/_artist.md` for discography and genre overview
2. **By era**: Filter albums by year in directory names (e.g., `artists/*/199*` for 90s)
3. **By mood/theme**: Search frontmatter `mood` and `themes` fields across song files
4. **By genre**: Search frontmatter `genre` fields across all songs (e.g., grep for `genre:.*sludge`)

### Analyzing an Artist's Style

To capture a "vibe," read 3-5 representative songs and look for:
- **Vocabulary patterns** — formal/casual, poetic/blunt, abstract/concrete
- **Metaphor density** — heavy imagery vs. direct statements
- **Perspective** — first person confessional, third person narrative, second person accusatory
- **Recurring themes** — alienation, love, politics, surrealism, nature, technology
- **Structural habits** — verse/chorus/bridge patterns, line lengths, rhyme schemes
- **Emotional register** — angry, melancholic, euphoric, detached, vulnerable

### Blending Styles from Multiple Artists

1. Read `_artist.md` for each artist to understand their broad style
2. Sample 2-3 songs from each that best represent what you want to blend
3. Identify the specific elements to take from each:
   - Artist A's vocabulary/imagery + Artist B's song structure
   - Artist A's emotional register + Artist B's thematic concerns
   - Artist A's verse style + Artist B's chorus hooks
4. Write with those constraints explicitly in mind

### Sonic-Only Reference (When Lyrics Aren't Available)

If an artist has no lyrics in the database (body is `[Lyrics not found]`), you can still use them as a style reference:

1. Read `_artist.md` for `genre`, `mood`, `musicbrainz_tags`, and `suno_style_description`
2. Check the translation table in `guides/SUNO_PROMPT_GUIDE.md` for a Suno-safe description
3. Use album-level tags from `_album.md` to understand era-specific sound
4. Derive vocal/atmospheric qualities from genre conventions (e.g., trip-hop → haunting female vocals, sparse atmosphere)
5. Focus on the **sonic palette** rather than lyrical style when blending

This is the fallback path — use it when referencing artists for their sound rather than their words.

## Song Design Interview (7 Questions)

Before writing lyrics, answer these to define the song's direction:

### 1. Emotional Center
What's the dominant tone?
- Regretful architect ("I knew better but I did it anyway")
- Accusatory ("You built this and dragged us into it")
- Collective tragedy ("We all believed the myth")
- Quiet post-collapse reflection ("The ashes are still warm")
- Defiant ("I'll burn it down myself before it falls")
- Or combine two

### 2. Perspective
Who is speaking?
- The builder / creator
- The observer watching it unfold
- The judgmental force (nature, consequence, truth)
- The fragile thing being destroyed
- A survivor walking through wreckage
- An outside narrator

### 3. Sonic Aggression Level (1-10)
- 1-3: Moody, brooding, atmospheric, restrained
- 4-6: Building tension, dynamic contrast, emotional weight
- 7-8: Heavy, mechanical, pounding, aggressive
- 9-10: Overwhelming density, wall of noise, maximum intensity
- Or a trajectory: "starts at 2, builds to 8"

### 4. Tempo & Structure
- Slow build that explodes
- Immediate assault
- Clean verse / chaotic chorus
- Spoken-word verse / melodic chorus
- Cascading build / collapse / silence
- Other

### 5. Vocal Style
- Whispered / intimate
- Deep baritone, close-mic'd
- Layered distorted harmonies
- Raw shouted / screamed
- Half-spoken, half-sung
- Vocals that evolve through the song

### 6. Key Imagery / Metaphors
Suggest 4-6 relevant metaphors based on the concept. Pick or add your own.

### 7. Ending Mood
- Collapse and scream
- Slow dying pulse
- Acceptance and stillness
- Bitter realization
- Rebuild hinted
- Cascading failure
- Abrupt silence

## Lyrics Writing Rules

- Clear sections with markers: `[Verse 1]`, `[Chorus]`, `[Bridge]`, `[Outro]`
- Strong chorus hook — memorable, repeatable
- Avoid overcomplicated metaphors — if it needs explaining, simplify
- Maintain consistent perspective within a section
- Keep lines performable — say them out loud, they should feel natural to sing
- Avoid excessive word count — concise > verbose
- Rhyme scheme should serve the song, not force it — near-rhymes and slant rhymes are fine

## End-to-End Song Design Workflow

```
1. CONCEPT
   Define the idea, emotional center, perspective
   ↓
2. STYLE REFERENCE
   Pull reference songs from the database
   Identify what elements to draw from
   ↓
3. SONG DESIGN INTERVIEW
   Answer the 7 questions above
   ↓
4. LYRICS
   Write lyrics following the constraints
   ↓
5. SUNO STYLE PROMPT
   Generate using SUNO_PROMPT_GUIDE.md
   Translate artist references to Suno-safe language
   ↓
6. GENERATE & ITERATE
   Paste into Suno, review output, adjust prompt/lyrics
```

## Output Format

When delivering a complete song:

### Production Style Prompt
Single paragraph. No commentary. No artist names. Ready to paste into Suno's style field.

### Lyrics
```
[Verse 1]
...

[Chorus]
...

[Verse 2]
...

[Bridge]
...

[Outro]
...
```

### Regeneration Tips (Optional)
Short, tactical adjustments if the first generation isn't right.

---

## Sound Designer Persona

When running a full songwriting session, adopt this persona to guide both lyrics and production decisions:

```
You are an experienced music producer and sound designer with deep knowledge across
metal, industrial, electronic, gothic, sludge, progressive, and alternative genres.
Your specialties:

MUSICAL EXPERTISE:
- Genre-fluid production spanning heavy music, electronic, ambient, and experimental
- Understanding of how era affects production texture (80s gated reverb, 90s analog
  warmth, 2000s digital clarity, modern hybrid approaches)
- Modal and tonal composition beyond basic major/minor
- Dynamic arrangement — knowing when to add density and when to strip back

PRODUCTION KNOWLEDGE:
- Instrument-specific vocabulary (pickup types, amp characteristics, synth architectures)
- Frequency spectrum management — keeping instruments in their own space
- Stereo imaging and spatial design
- Loudness and dynamic range appropriate to genre

SUNO-SPECIFIC KNOWLEDGE:
- Style prompts under 180 words, no artist names, concrete descriptors
- Multi-pass Studio builds for complex productions
- Stem separation for mixing and remixing
- "instrumental, no vocals" combined with [Instrumental] for instrumental tracks

CREATIVE PROCESS:
1. Concept → define emotional center, perspective, and sonic vision
2. Reference → pull from the lyrics database for grounded style analysis
3. Interview → 7-question song design to nail down specifics
4. Write → lyrics that serve the music, not the other way around
5. Produce → style prompt that captures the vision without artist names
6. Iterate → tactical adjustments based on generation results
```

## Style Blending — Worked Example

### Concept: Blend Crowbar + Type O Negative

**Goal**: A song that combines Crowbar's crushing sludge weight with Type O Negative's gothic theatricality and synth textures.

### Step 1: Read Artist Data

**Crowbar** (`artists/Crowbar/_artist.md`):
- Genre: sludge metal, doom metal
- Mood: heavy, raw, emotionally direct
- Key traits: Downtuned crushing riffs, gravelly vocals, groove-based heaviness, themes of suffering and defiance

**Type O Negative** (`artists/Type O Negative/_artist.md`):
- Genre: gothic metal, doom metal, gothic rock
- Mood: melancholic, dark, theatrical
- Key traits: Deep baritone vocals, analog synths, deadpan delivery, gothic imagery, dark humor

### Step 2: Sample Lyrics

**From Crowbar** — direct, visceral, emotionally raw:
> "Time heals nothing / I can't forget your face"
> Vocabulary: concrete, blunt, pain-focused. Minimal metaphor. First-person suffering.

**From Type O Negative** — theatrical, darkly playful, literary:
> "She was beautiful like a rainbow / Not one of those brief ones"
> Vocabulary: gothic imagery, dark humor, melodramatic. Third-person narrative mixed with confession.

### Step 3: Identify Elements to Blend

| Element | Take From | Reason |
|---------|-----------|--------|
| Song structure | Crowbar | Slow, crushing, groove-based |
| Vocal approach | Type O Negative | Baritone melodic delivery with spoken sections |
| Lyrical vocabulary | Both | Crowbar's directness + Type O's gothic imagery |
| Instrumentation | Both | Crowbar's crushing guitars + Type O's synth pads |
| Emotional register | Blend | Crowbar's raw pain filtered through Type O's dark theatricality |
| Themes | Blend | Suffering + gothic romanticism = "beautiful decay" |

### Step 4: Write Lyrics

```
[Verse 1]
Cathedral walls of rust and ruin
Every crack a year of silence kept
I built this shrine from broken things
And prayed to gods that never wept

[Chorus]
Let it fall — let it all come down
Beautiful in the way it breaks
Crown of thorns on a hollow king
Every scar a monument we make

[Verse 2]
The organ hums through flooded halls
Stained glass shadows on the floor
I held your name like burning coal
And watched it eat through to the core

[Bridge]
(Spoken, deadpan)
They say the building was condemned years ago
But something still moves in the basement
Something that remembers what it was

[Outro]
Let it fall... let it fall...
Beautiful... in the way... it breaks
```

### Step 5: Generate Suno Style Prompt

> Gothic-tinged sludge doom metal with theatrical atmosphere and crushing low-end weight. Heavy downtuned guitars deliver slow, grinding riffs over plodding bass and deliberate kick-heavy drums. Analog synth organ pads add dark cathedral-like texture beneath the distortion. Deep resonant baritone vocals shift between melodic sung passages and deadpan spoken-word sections. Production is warm and massive — thick guitar tones layered with reverb-soaked synths creating a cavernous, cinematic soundscape. Energy moves slowly and deliberately, building from brooding verses to anthemic crushing choruses. The mood is melancholic grandeur — sorrow expressed through monumental heaviness.

### Step 6: Evaluate

- Crowbar elements: crushing riffs, groove-based pacing, emotional directness, wall of sound
- Type O elements: baritone vocals, spoken sections, organ/synth textures, gothic imagery, theatrical flair
- Blend result: something that sounds like neither band specifically, but feels like both

## Era-Based Filtering

### Finding Songs by Decade

Directory names encode year, making era-based searches easy:

```bash
# All 90s albums across all artists
ls artists/*/199*

# All 2000s albums
ls artists/*/200*

# All albums from a specific year
ls artists/*/1994*

# Find all songs from 90s alternative artists
find artists/ -path "*/199*/*.md" ! -name "_*"
```

### Frontmatter-Based Filtering

```bash
# All songs tagged as "doom metal"
grep -rl "genre:.*doom metal" artists/

# All melancholic songs
grep -rl "mood:.*melancholic" artists/

# All songs from a specific year
grep -rl "^year: 1994" artists/
```

### Era + Genre Combinations

To find "90s sludge metal":
1. List 90s albums: `ls artists/*/199*`
2. Check genre tags: `grep "genre:" artists/*/199*/_album.md`
3. Read matching songs for style reference
