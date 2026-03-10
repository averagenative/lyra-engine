# Enrichment Vocabulary — Controlled Tags for Metadata

> Defines valid values for frontmatter enrichment fields (`mood`, `style`, `energy`, `themes`). Use these when enriching song files to keep tags consistent and searchable across the entire database.

## mood

Emotional character of the song. Pick 1-3 that best fit.

| Value | Description |
|-------|-------------|
| aggressive | Confrontational, combative energy |
| angry | Rage, fury, frustration |
| atmospheric | Spacious, immersive, enveloping |
| bleak | Hopeless, desolate |
| brooding | Dark contemplation, simmering tension |
| cathartic | Emotional release, purging |
| cold | Emotionally distant, sterile |
| dark | Generally ominous or shadowy |
| defiant | Resistant, rebellious, standing ground |
| dreamy | Hazy, floating, ethereal |
| energetic | High-energy, driving, propulsive |
| euphoric | Ecstatic, transcendent |
| haunting | Lingering unease, ghostly |
| heavy | Emotionally or sonically weighty |
| hopeful | Optimistic, forward-looking |
| introspective | Inward-focused, self-examining |
| melancholic | Deep sadness, wistful longing |
| menacing | Threatening, predatory |
| mournful | Grieving, lamenting |
| nostalgic | Longing for the past |
| peaceful | Calm, serene, at rest |
| playful | Light, humorous, irreverent |
| raw | Unfiltered, emotionally exposed |
| restless | Anxious, unable to settle |
| somber | Serious, grave |
| triumphant | Victorious, empowered |
| vulnerable | Exposed, unprotected |

## style

Production and sonic character. Pick 1-3.

| Value | Description |
|-------|-------------|
| abrasive | Harsh, grating, intentionally unpleasant textures |
| ambient | Atmospheric, textural, background-focused |
| angular | Dissonant, jerky, unpredictable rhythms |
| cinematic | Film-score quality, dramatic scope |
| clean | Polished, precise production |
| dense | Layered, thick, wall-of-sound |
| droning | Sustained, repetitive, hypnotic |
| dynamic | Wide contrast between quiet and loud |
| groovy | Rhythmically compelling, head-nodding |
| lo-fi | Raw, unpolished, deliberately rough |
| lush | Rich, full, layered harmonics |
| mechanical | Machine-like precision, robotic |
| minimal | Sparse, stripped-back |
| organic | Natural, warm, human |
| progressive | Complex structures, evolving arrangements |
| psychedelic | Mind-bending, altered-state |
| pummeling | Relentless physical impact |
| sludgy | Slow, thick, tar-like heaviness |
| spacious | Open, reverb-heavy, room to breathe |
| technical | Virtuosic, complex playing |
| theatrical | Dramatic, performative, over-the-top |

## energy

Dynamic profile of the song. Pick exactly 1.

| Value | Description |
|-------|-------------|
| building | Starts low, builds throughout |
| constant-high | Relentless high energy throughout |
| constant-low | Sustained low energy, meditative |
| dynamic | Significant shifts between high and low |
| explosive | Quiet sections erupting into intensity |
| fading | Starts strong, gradually diminishes |
| rolling | Waves of intensity, recurring builds and releases |
| steady-mid | Consistent moderate energy |

## themes

Lyrical subject matter. Pick 2-5 from this list or add new ones (but check existing tags first to avoid duplicates).

| Value | Description |
|-------|-------------|
| addiction | Substance dependence, compulsion |
| alienation | Feeling disconnected from society |
| anger | Rage and fury as central subject |
| betrayal | Broken trust, treachery |
| control | Power dynamics, manipulation |
| death | Mortality, dying, the afterlife |
| decay | Deterioration, entropy, rot |
| defiance | Resistance against authority or fate |
| despair | Hopelessness, existential dread |
| destruction | Ruin, annihilation |
| faith | Religion, spirituality, belief systems |
| freedom | Liberation, escape |
| grief | Loss, mourning |
| identity | Self-discovery, who you are |
| isolation | Loneliness, solitude |
| love | Romantic love, devotion |
| madness | Mental instability, psychosis |
| nature | Natural world, environment |
| nihilism | Meaninglessness, void |
| nostalgia | Past memories, longing for what was |
| pain | Physical or emotional suffering |
| politics | Social commentary, protest |
| power | Strength, domination, authority |
| rebellion | Fighting against the system |
| redemption | Finding salvation, making amends |
| self-destruction | Self-harm, recklessness |
| society | Social structures, culture |
| survival | Endurance, making it through |
| technology | Machines, digital world |
| transformation | Change, metamorphosis |
| violence | Physical aggression, brutality |
| war | Conflict, battle |

## Usage Guidelines

- Always use lowercase values exactly as listed
- For `mood`, `style`, `themes`: pick multiple (comma-separated in frontmatter)
- For `energy`: pick exactly one
- When in doubt between two similar tags, pick the more specific one
- New `themes` values are allowed but check the list first to avoid near-duplicates
- New `mood`, `style`, `energy` values should be proposed and added to this document before use
