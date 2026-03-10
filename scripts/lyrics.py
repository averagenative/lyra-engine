"""Genius lyrics fetching with fuzzy title matching."""

import os
import sys
import time
from difflib import SequenceMatcher

import lyricsgenius

from config import PROJECT_ROOT, GENIUS_SLEEP_SECONDS, FUZZY_MATCH_THRESHOLD

_genius = None


def _load_dotenv():
    """Load .env file from project root if it exists."""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def init_genius() -> lyricsgenius.Genius:
    """Initialize the Genius client. Reads GENIUS_API_TOKEN from env or .env file."""
    global _genius
    if _genius is not None:
        return _genius

    _load_dotenv()
    token = os.environ.get("GENIUS_API_TOKEN")
    if not token:
        print(
            "Error: GENIUS_API_TOKEN environment variable not set.\n"
            "Get a free token at: https://genius.com/api-clients",
            file=sys.stderr,
        )
        sys.exit(1)

    _genius = lyricsgenius.Genius(token, verbose=False, remove_section_headers=False)
    _genius.excluded_terms = ["(Remix)", "(Live)"]
    return _genius


def _normalize(text: str) -> str:
    """Normalize a string for fuzzy comparison."""
    import re
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def _title_matches(expected: str, actual: str) -> bool:
    """Check if the returned title is a fuzzy match for the expected title."""
    ratio = SequenceMatcher(None, _normalize(expected), _normalize(actual)).ratio()
    return ratio >= FUZZY_MATCH_THRESHOLD


def _clean_lyrics(lyrics: str) -> str:
    """Clean up raw lyrics text (remove headers, trailing junk, detect instrumentals)."""
    lines = lyrics.split("\n")
    # Remove song title header that lyricsgenius prepends
    if lines and lines[0].strip().endswith("Lyrics"):
        lines = lines[1:]
    # Remove trailing "Embed" or number+Embed
    while lines and ("Embed" in lines[-1] or lines[-1].strip() == ""):
        lines.pop()
    # Remove trailing digit-only lines (e.g., "123Embed" leaves "123")
    while lines and lines[-1].strip().isdigit():
        lines.pop()
    cleaned = "\n".join(lines).strip()

    # Detect instrumentals
    cleaned_lower = cleaned.lower().replace(" ", "")
    if cleaned_lower in ("", "[instrumental]", "(instrumental)", "instrumental"):
        cleaned = "[Instrumental]"

    return cleaned


def fetch_lyrics(artist: str, title: str) -> tuple[str | None, str | None]:
    """Fetch lyrics for a song.

    Returns (lyrics_text, genius_url) or (None, None) if not found.
    """
    genius = init_genius()

    try:
        song = genius.search_song(title, artist)
    except Exception as e:
        print(f"  Error fetching '{title}': {e}", file=sys.stderr)
        return None, None

    if song is None:
        return None, None

    # Verify the match
    if not _title_matches(title, song.title):
        print(
            f"  Skipping '{title}': Genius returned '{song.title}' (poor match)",
            file=sys.stderr,
        )
        return None, None

    lyrics = _clean_lyrics(song.lyrics) if song.lyrics else None

    time.sleep(GENIUS_SLEEP_SECONDS)

    return lyrics or None, song.url


def _slugify_for_azlyrics(text: str) -> str:
    """Convert text to AZLyrics URL slug: lowercase, no spaces/special chars."""
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9]", "", text)
    return text


def scrape_lyrics_from_url(url: str) -> str | None:
    """Generic lyrics scraper that works with common lyrics sites.

    Supports AZLyrics, MetroLyrics, and other sites with common patterns.
    For Genius URLs, delegates to fetch_lyrics_from_url.
    For Musixmatch, skips gracefully (they block scraping).

    Returns cleaned lyrics text or None.
    """
    import re
    import requests
    from bs4 import BeautifulSoup, Comment

    # Redirect Genius URLs to the dedicated function
    if "genius.com" in url:
        return fetch_lyrics_from_url(url)

    # Musixmatch blocks scraping — skip gracefully
    if "musixmatch.com" in url:
        print("  Musixmatch blocks scraping, skipping.", file=sys.stderr)
        return None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        page = requests.get(url, headers=headers, timeout=15)
        if page.status_code != 200:
            return None
        soup = BeautifulSoup(page.text, "html.parser")
    except Exception as e:
        print(f"  Error fetching URL: {e}", file=sys.stderr)
        return None

    lyrics_text = None

    # AZLyrics: div with no class after the specific comment
    if "azlyrics.com" in url:
        comments = soup.find_all(string=lambda text: isinstance(text, Comment)
                                 and "azlyrics.com content" in text.lower())
        if comments:
            # The lyrics div is the next sibling div after the comment
            comment = comments[0]
            lyrics_div = comment.find_next("div")
            if lyrics_div:
                lyrics_text = lyrics_div.get_text(separator="\n")
        if not lyrics_text:
            # Fallback: look for the main lyrics div by structure
            ringtone = soup.find("div", class_="ringtone")
            if ringtone:
                lyrics_div = ringtone.find_next_sibling("div")
                if lyrics_div and not lyrics_div.get("class"):
                    lyrics_text = lyrics_div.get_text(separator="\n")

    # MetroLyrics: <div id="lyrics-body-text">
    elif "metrolyrics.com" in url:
        container = soup.find("div", id="lyrics-body-text")
        if container:
            lyrics_text = container.get_text(separator="\n")

    # Generic fallback: look for elements with class/id containing "lyrics" or "songtext"
    if not lyrics_text:
        for attr in ["id", "class"]:
            for keyword in ["lyrics", "songtext"]:
                candidates = soup.find_all(
                    lambda tag: tag.name in ("div", "section", "pre")
                    and tag.get(attr)
                    and keyword in (
                        " ".join(tag[attr]) if isinstance(tag[attr], list)
                        else str(tag[attr])
                    ).lower()
                )
                # Pick the largest candidate by text length
                for candidate in candidates:
                    text = candidate.get_text(separator="\n")
                    if text and len(text) > 50:
                        if not lyrics_text or len(text) > len(lyrics_text):
                            lyrics_text = text

    if not lyrics_text:
        return None

    # Clean the result
    lines = lyrics_text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Skip common ad/header junk
        if any(junk in line.lower() for junk in [
            "submit corrections", "writer(s):", "lyrics licensed",
            "lyrics provided by", "lyrics powered by",
            "unfortunately, we are not licensed",
        ]):
            continue
        cleaned_lines.append(line)

    # Normalize: collapse multiple blank lines into one
    result_lines = []
    prev_blank = False
    for line in cleaned_lines:
        if not line:
            if not prev_blank:
                result_lines.append("")
            prev_blank = True
        else:
            result_lines.append(line)
            prev_blank = False

    result = "\n".join(result_lines).strip()
    return result if len(result) > 20 else None


def web_search_lyrics(artist: str, title: str) -> str | None:
    """Search for lyrics using predictable URL patterns on common lyrics sites.

    Tries AZLyrics as a best-effort fallback when Genius fails.
    Returns cleaned lyrics text or None.
    """
    # Try AZLyrics: https://www.azlyrics.com/lyrics/{artist_slug}/{title_slug}.html
    artist_slug = _slugify_for_azlyrics(artist)
    title_slug = _slugify_for_azlyrics(title)

    if not artist_slug or not title_slug:
        return None

    # Strip leading "the" from artist for AZLyrics convention
    if artist_slug.startswith("the"):
        artist_slug_nothe = artist_slug[3:]
    else:
        artist_slug_nothe = None

    urls_to_try = [
        f"https://www.azlyrics.com/lyrics/{artist_slug}/{title_slug}.html",
    ]
    if artist_slug_nothe:
        urls_to_try.append(
            f"https://www.azlyrics.com/lyrics/{artist_slug_nothe}/{title_slug}.html"
        )

    for url in urls_to_try:
        lyrics = scrape_lyrics_from_url(url)
        if lyrics:
            return lyrics

    return None


def fetch_lyrics_from_url(url: str) -> str | None:
    """Scrape lyrics from a Genius URL directly.

    Returns cleaned lyrics text or None.
    """
    genius = init_genius()

    try:
        # lyricsgenius can scrape lyrics from a URL
        from bs4 import BeautifulSoup
        import requests

        page = requests.get(url, timeout=15)
        soup = BeautifulSoup(page.text, "html.parser")

        # Genius stores lyrics in divs with data-lyrics-container="true"
        containers = soup.find_all("div", attrs={"data-lyrics-container": "true"})
        if not containers:
            return None

        lyrics_parts = []
        for container in containers:
            # Replace <br> with newlines
            for br in container.find_all("br"):
                br.replace_with("\n")
            lyrics_parts.append(container.get_text())

        raw = "\n".join(lyrics_parts)
        return _clean_lyrics(raw) if raw.strip() else None

    except Exception as e:
        print(f"  Error scraping URL: {e}", file=sys.stderr)
        return None
