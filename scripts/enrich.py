"""Heuristic-based enrichment: suggest mood, style, energy, and theme tags from lyrics."""

import argparse
import re
import sys
from pathlib import Path

from config import DATABASE_ROOT
from markdown import read_md, _write_md


# ---------------------------------------------------------------------------
# Controlled vocabulary (mirrors guides/ENRICHMENT_VOCABULARY.md)
# ---------------------------------------------------------------------------

VALID_MOODS = [
    "aggressive", "angry", "atmospheric", "bleak", "brooding", "cathartic",
    "cold", "dark", "defiant", "dreamy", "energetic", "euphoric", "haunting",
    "heavy", "hopeful", "introspective", "melancholic", "menacing", "mournful",
    "nostalgic", "peaceful", "playful", "raw", "restless", "somber",
    "triumphant", "vulnerable",
]

VALID_STYLES = [
    "abrasive", "ambient", "angular", "cinematic", "clean", "dense", "droning",
    "dynamic", "groovy", "lo-fi", "lush", "mechanical", "minimal", "organic",
    "progressive", "psychedelic", "pummeling", "sludgy", "spacious",
    "technical", "theatrical",
]

VALID_ENERGY = [
    "building", "constant-high", "constant-low", "dynamic", "explosive",
    "fading", "rolling", "steady-mid",
]

VALID_THEMES = [
    "addiction", "alienation", "anger", "betrayal", "control", "death",
    "decay", "defiance", "despair", "destruction", "faith", "freedom",
    "grief", "identity", "isolation", "love", "madness", "nature", "nihilism",
    "nostalgia", "pain", "politics", "power", "rebellion", "redemption",
    "self-destruction", "society", "survival", "technology", "transformation",
    "violence", "war",
]


# ---------------------------------------------------------------------------
# Keyword maps — words/phrases that hint at a tag
# ---------------------------------------------------------------------------

MOOD_KEYWORDS: dict[str, list[str]] = {
    "aggressive":   ["attack", "crush", "destroy", "smash", "fight"],
    "angry":        ["rage", "fury", "furious", "hate", "hatred", "wrath", "pissed"],
    "atmospheric":  ["echo", "drift", "vast", "space", "horizon"],
    "bleak":        ["hopeless", "barren", "wasteland", "nothing left", "void"],
    "brooding":     ["brood", "simmer", "smolder", "lurk", "beneath"],
    "cathartic":    ["release", "let go", "purge", "free at last", "finally free"],
    "cold":         ["frozen", "frost", "ice", "numb", "cold"],
    "dark":         ["shadow", "darkness", "night", "black", "abyss"],
    "defiant":      ["refuse", "resist", "never bow", "stand tall", "won't kneel",
                     "defy", "won't back down", "stand my ground"],
    "dreamy":       ["dream", "float", "haze", "shimmer", "clouds"],
    "energetic":    ["run", "rush", "charge", "adrenaline", "faster"],
    "euphoric":     ["ecstasy", "euphoria", "bliss", "transcend", "soaring"],
    "haunting":     ["ghost", "haunt", "linger", "specter", "phantom"],
    "heavy":        ["weight", "burden", "crush", "heavy", "gravity"],
    "hopeful":      ["hope", "tomorrow", "brighter", "believe", "new dawn"],
    "introspective": ["reflect", "wonder", "inside", "mirror", "question myself"],
    "melancholic":  ["tears", "weep", "sorrow", "sad", "cry", "mourn", "wistful",
                     "melancholy", "longing"],
    "menacing":     ["threat", "prey", "stalk", "menace", "devour"],
    "mournful":     ["grieve", "funeral", "lament", "loss", "requiem", "bury"],
    "nostalgic":    ["remember", "those days", "used to", "memory", "once was",
                     "looking back"],
    "peaceful":     ["calm", "serene", "still", "quiet", "peace", "gentle"],
    "playful":      ["laugh", "joke", "fun", "play", "silly", "grin"],
    "raw":          ["bleed", "exposed", "bare", "stripped", "open wound"],
    "restless":     ["can't sleep", "pacing", "restless", "anxious", "uneasy"],
    "somber":       ["grave", "solemn", "heavy heart", "somber"],
    "triumphant":   ["victory", "conquer", "overcome", "triumph", "champion",
                     "rise above", "glory"],
    "vulnerable":   ["fragile", "naked", "afraid", "helpless", "weak"],
}

THEME_KEYWORDS: dict[str, list[str]] = {
    "addiction":        ["addict", "drunk", "high", "needle", "pill", "dose",
                         "sober", "bottle", "drug", "fix"],
    "alienation":       ["outcast", "don't belong", "alien", "stranger",
                         "outside", "misfit", "excluded"],
    "anger":            ["rage", "fury", "hate", "furious", "wrath", "pissed"],
    "betrayal":         ["betray", "backstab", "traitor", "deceive", "liar",
                         "trust", "two-faced", "stab in the back"],
    "control":          ["control", "manipulate", "puppet", "obey", "command",
                         "dominate", "submit"],
    "death":            ["death", "die", "dying", "dead", "kill", "grave",
                         "corpse", "funeral", "tomb", "mortal"],
    "decay":            ["rot", "decay", "rust", "crumble", "erode",
                         "deteriorate", "wither", "corrode"],
    "defiance":         ["defy", "resist", "refuse", "rebel", "won't bow",
                         "never kneel", "stand against"],
    "despair":          ["despair", "hopeless", "no way out", "give up",
                         "pointless", "meaningless", "dread"],
    "destruction":      ["destroy", "ruin", "annihilate", "demolish",
                         "obliterate", "wreckage", "shatter"],
    "faith":            ["god", "pray", "faith", "soul", "heaven", "hell",
                         "divine", "sacred", "spirit", "church", "sin",
                         "salvation", "angel", "demon"],
    "freedom":          ["free", "freedom", "escape", "liberate", "break free",
                         "unchained", "wings"],
    "grief":            ["grieve", "loss", "mourn", "funeral", "gone forever",
                         "miss you", "passed away"],
    "identity":         ["who am i", "identity", "self", "mask", "mirror",
                         "become", "true self"],
    "isolation":        ["alone", "lonely", "solitude", "isolated", "no one",
                         "empty room", "by myself"],
    "love":             ["love", "heart", "kiss", "darling", "beloved",
                         "embrace", "romance", "devotion", "desire"],
    "madness":          ["insane", "madness", "crazy", "lunatic", "psycho",
                         "voices", "losing my mind", "asylum"],
    "nature":           ["forest", "river", "mountain", "ocean", "sea", "sun",
                         "moon", "storm", "rain", "earth", "sky", "wind"],
    "nihilism":         ["nothing matters", "meaningless", "void", "empty",
                         "pointless", "absurd", "futile"],
    "nostalgia":        ["remember", "those days", "used to", "childhood",
                         "once upon", "looking back", "old days"],
    "pain":             ["pain", "hurt", "suffer", "agony", "ache", "wound",
                         "scar", "bleed", "sting"],
    "politics":         ["government", "protest", "revolution", "system",
                         "oppression", "justice", "corrupt", "regime",
                         "propaganda"],
    "power":            ["power", "king", "throne", "rule", "mighty",
                         "dominate", "conquer", "empire"],
    "rebellion":        ["rebel", "fight back", "uprising", "overthrow",
                         "anarchy", "disobey", "revolution"],
    "redemption":       ["redeem", "forgive", "salvation", "atone", "save",
                         "second chance", "born again"],
    "self-destruction": ["self-destruct", "reckless", "sabotage", "burn it down",
                         "own worst enemy", "tearing myself apart"],
    "society":          ["society", "culture", "masses", "civilization",
                         "conformity", "machine", "system"],
    "survival":         ["survive", "endure", "persist", "hold on", "keep going",
                         "make it through", "cling"],
    "technology":       ["machine", "digital", "circuit", "wired", "program",
                         "binary", "algorithm", "data", "screen"],
    "transformation":   ["transform", "change", "evolve", "metamorphosis",
                         "become", "rebirth", "shed my skin"],
    "violence":         ["blood", "blade", "stab", "fist", "gun", "bullet",
                         "slaughter", "bludgeon", "strike"],
    "war":              ["war", "battle", "soldier", "trench", "army",
                         "march", "bomb", "siege", "enemy"],
}


# ---------------------------------------------------------------------------
# Heuristic analysers
# ---------------------------------------------------------------------------

def _lyrics_text(body: str) -> str:
    """Return the lyrics body stripped of markdown section headers."""
    lines = body.strip().splitlines()
    return "\n".join(l for l in lines if not l.startswith("#"))


def suggest_energy(body: str) -> str | None:
    """Estimate energy from structural cues."""
    text = _lyrics_text(body)
    if not text.strip():
        return None

    lines = [l for l in text.splitlines() if l.strip()]
    line_count = len(lines)

    # Count exclamation marks
    exclamations = text.count("!")

    # Uppercase ratio (ignoring section labels)
    alpha_chars = [c for c in text if c.isalpha()]
    if not alpha_chars:
        return "steady-mid"
    upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)

    # Section count (lines that look like [Verse], [Chorus], etc.)
    section_re = re.compile(r"^\[.*\]$", re.MULTILINE)
    sections = len(section_re.findall(text))

    # Simple scoring
    intensity = 0.0
    intensity += min(exclamations / 10.0, 1.0) * 0.3
    intensity += min(upper_ratio / 0.5, 1.0) * 0.3
    intensity += min(line_count / 60.0, 1.0) * 0.2
    intensity += min(sections / 8.0, 1.0) * 0.2

    if intensity > 0.7:
        return "constant-high"
    elif intensity > 0.5:
        return "rolling"
    elif intensity > 0.3:
        return "steady-mid"
    else:
        return "constant-low"


def _match_keywords(text: str, keyword_map: dict[str, list[str]],
                    limit: int = 0) -> list[str]:
    """Return tags whose keywords appear in *text*, sorted by match count."""
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for tag, keywords in keyword_map.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count:
            scores[tag] = count
    ranked = sorted(scores, key=lambda t: -scores[t])
    return ranked[:limit] if limit else ranked


def suggest_mood(body: str) -> list[str]:
    """Suggest up to 3 mood tags from lyrics keywords."""
    text = _lyrics_text(body)
    return _match_keywords(text, MOOD_KEYWORDS, limit=3)


def suggest_themes(body: str) -> list[str]:
    """Suggest up to 5 theme tags from lyrics keywords."""
    text = _lyrics_text(body)
    return _match_keywords(text, THEME_KEYWORDS, limit=5)


def suggest_style_from_context(artist_fm: dict | None,
                               album_fm: dict | None) -> list[str]:
    """Inherit style tags from artist/album genre and musicbrainz_tags."""
    # Map common genre keywords to style tags
    genre_to_style: dict[str, str] = {
        "ambient": "ambient",
        "progressive": "progressive",
        "psychedelic": "psychedelic",
        "lo-fi": "lo-fi",
        "lofi": "lo-fi",
        "shoegaze": "lush",
        "noise": "abrasive",
        "drone": "droning",
        "doom": "sludgy",
        "sludge": "sludgy",
        "grindcore": "pummeling",
        "industrial": "mechanical",
        "electronic": "mechanical",
        "post-rock": "cinematic",
        "math rock": "angular",
        "technical": "technical",
        "death metal": "technical",
        "funk": "groovy",
        "jazz": "organic",
        "folk": "organic",
        "acoustic": "organic",
        "minimalist": "minimal",
        "minimal": "minimal",
        "chamber": "lush",
        "orchestral": "cinematic",
        "opera": "theatrical",
        "cabaret": "theatrical",
        "punk": "lo-fi",
        "garage": "lo-fi",
        "black metal": "abrasive",
        "thrash": "pummeling",
        "stoner": "groovy",
    }

    combined_tags: list[str] = []
    for fm in (artist_fm, album_fm):
        if not fm:
            continue
        genre_str = fm.get("genre", "")
        if genre_str:
            combined_tags.extend(t.strip().lower() for t in genre_str.split(","))
        mb_tags = fm.get("musicbrainz_tags", [])
        if isinstance(mb_tags, list):
            combined_tags.extend(t.lower() for t in mb_tags)

    styles: list[str] = []
    seen: set[str] = set()
    for tag in combined_tags:
        for keyword, style in genre_to_style.items():
            if keyword in tag and style not in seen:
                styles.append(style)
                seen.add(style)
    return styles[:3]


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def iter_song_files(artist_name: str | None = None):
    """Yield (song_path, artist_dir, album_dir) for matching songs."""
    if artist_name:
        # Find artist dirs that match
        for entry in sorted(DATABASE_ROOT.iterdir()):
            if not entry.is_dir():
                continue
            artist_md = entry / "_artist.md"
            if not artist_md.exists():
                continue
            fm, _ = read_md(artist_md)
            name = fm.get("name", entry.name)
            if name.lower() != artist_name.lower():
                continue
            yield from _songs_in_artist(entry)
    else:
        # All artists
        for entry in sorted(DATABASE_ROOT.iterdir()):
            if entry.is_dir() and (entry / "_artist.md").exists():
                yield from _songs_in_artist(entry)


def _songs_in_artist(artist_path: Path):
    for album_entry in sorted(artist_path.iterdir()):
        if not album_entry.is_dir():
            continue
        for song_file in sorted(album_entry.glob("*.md")):
            if song_file.name.startswith("_"):
                continue
            yield song_file, artist_path, album_entry


# ---------------------------------------------------------------------------
# LLM prompt generation
# ---------------------------------------------------------------------------

def build_llm_prompt(fm: dict, body: str) -> str:
    """Build a prompt that could be sent to an LLM for richer enrichment."""
    title = fm.get("title", "Unknown")
    artist = fm.get("artist", "Unknown")
    album = fm.get("album", "Unknown")
    year = fm.get("year", "")
    genre = fm.get("genre", "")

    return f"""\
You are a music metadata analyst. Read the lyrics below and suggest enrichment
tags from the controlled vocabulary provided.

SONG: {title}
ARTIST: {artist}
ALBUM: {album} ({year})
GENRE: {genre}

LYRICS:
{body.strip()}

---
Using ONLY the values listed below, suggest tags for this song.

MOOD (pick 1-3): {', '.join(VALID_MOODS)}
STYLE (pick 1-3): {', '.join(VALID_STYLES)}
ENERGY (pick exactly 1): {', '.join(VALID_ENERGY)}
THEMES (pick 2-5): {', '.join(VALID_THEMES)}

Respond in this exact YAML format:
mood: [tag1, tag2]
style: [tag1, tag2]
energy: tag
themes: [tag1, tag2, tag3]
"""


# ---------------------------------------------------------------------------
# Main enrichment logic
# ---------------------------------------------------------------------------

def enrich_song(song_file: Path, artist_path: Path, album_path: Path,
                *, dry_run: bool = False, llm: bool = False) -> dict | None:
    """Analyse one song and optionally write enrichment tags.

    Returns a dict describing changes, or None if nothing to do.
    """
    fm, body = read_md(song_file)
    if not fm:
        return None

    # Skip songs without lyrics
    if "[Lyrics not found]" in body or not body.strip():
        return None

    # Load artist/album frontmatter for style inheritance
    artist_md = artist_path / "_artist.md"
    album_md = album_path / "_album.md"
    artist_fm = read_md(artist_md)[0] if artist_md.exists() else None
    album_fm = read_md(album_md)[0] if album_md.exists() else None

    changes: dict[str, object] = {}

    # --- mood ---
    existing_mood = fm.get("mood", "")
    if not existing_mood:
        suggested = suggest_mood(body)
        if suggested:
            changes["mood"] = ", ".join(suggested)

    # --- themes ---
    existing_themes = fm.get("themes", [])
    # themes may be a list or a comma-separated string
    if isinstance(existing_themes, str):
        existing_themes = [t.strip() for t in existing_themes.split(",") if t.strip()]
    if not existing_themes:
        suggested = suggest_themes(body)
        if suggested:
            changes["themes"] = suggested

    # --- energy ---
    existing_energy = fm.get("energy", "")
    if not existing_energy:
        suggested = suggest_energy(body)
        if suggested:
            changes["energy"] = suggested

    # --- style ---
    existing_style = fm.get("style", "")
    if not existing_style:
        suggested = suggest_style_from_context(artist_fm, album_fm)
        if suggested:
            changes["style"] = ", ".join(suggested)

    if not changes and not llm:
        return None

    # LLM prompt mode
    if llm:
        prompt = build_llm_prompt(fm, body)
        title = fm.get("title", song_file.stem)
        artist = fm.get("artist", "")
        print(f"\n{'='*60}")
        print(f"LLM PROMPT — {artist} — {title}")
        print(f"{'='*60}")
        print(prompt)

    if changes and not dry_run:
        for key, value in changes.items():
            fm[key] = value
        _write_md(song_file, fm, body)

    return changes


def cmd_enrich(args):
    """Entry point for the enrich subcommand."""
    artist_name = None if args.all else args.artist
    if not args.all and not args.artist:
        print("Provide an artist name or --all to process everything.",
              file=sys.stderr)
        sys.exit(1)

    total = 0
    enriched = 0
    field_counts: dict[str, int] = {"mood": 0, "themes": 0, "energy": 0, "style": 0}

    for song_file, artist_path, album_path in iter_song_files(artist_name):
        total += 1
        changes = enrich_song(song_file, artist_path, album_path,
                              dry_run=args.dry_run, llm=args.llm)
        if changes:
            enriched += 1
            rel = song_file.relative_to(DATABASE_ROOT)
            prefix = "[dry-run] " if args.dry_run else ""
            print(f"  {prefix}{rel}")
            for field, value in changes.items():
                field_counts[field] = field_counts.get(field, 0) + 1
                if isinstance(value, list):
                    value = ", ".join(value)
                print(f"    {field}: {value}")

    # Summary
    print(f"\n{'='*50}")
    mode = "DRY-RUN " if args.dry_run else ""
    print(f"{mode}Enrichment summary:")
    print(f"  Songs scanned: {total}")
    print(f"  Songs enriched: {enriched}")
    for field in ("mood", "themes", "energy", "style"):
        if field_counts[field]:
            print(f"    {field}: {field_counts[field]}")


# ---------------------------------------------------------------------------
# Standalone entry point (also usable via fetch.py enrich)
# ---------------------------------------------------------------------------

def _build_parser(parser: argparse.ArgumentParser | None = None):
    if parser is None:
        parser = argparse.ArgumentParser(
            description="Suggest enrichment tags for song files"
        )
    parser.add_argument("artist", nargs="?", default=None,
                        help="Artist name to process")
    parser.add_argument("--all", action="store_true",
                        help="Process all artists")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview suggestions without writing")
    parser.add_argument("--llm", action="store_true",
                        help="Print an LLM prompt per song instead of heuristic tags")
    parser.set_defaults(func=cmd_enrich)
    return parser


if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    parser = _build_parser()
    args = parser.parse_args()
    args.func(args)
