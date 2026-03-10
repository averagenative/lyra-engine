# Lyricist Guide — Agent Reference for Writing Lyrics

> How to use the lyrics database to write new songs. For AI agents and humans.

## Using the Database for Style Reference

### Finding Reference Material

1. **By artist**: Read `{Artist}/_artist.md` for discography and genre overview
2. **By era**: Filter albums by year in the directory names (e.g., all `199*` dirs)
3. **By mood/theme**: Search frontmatter `mood` and `themes` fields (when enriched)
4. **By genre**: Search frontmatter `genre` fields across all songs

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
