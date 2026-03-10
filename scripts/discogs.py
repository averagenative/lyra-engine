"""Discogs API client for artist profiles, releases, and style/genre data."""

import os
import sys
import time

# Add scripts dir to path so imports work when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

from config import PROJECT_ROOT

# Discogs API base URL
BASE_URL = "https://api.discogs.com"

# User-Agent required by Discogs API
USER_AGENT = "LyraEngine/1.0 +https://github.com/averagenative/lyra-engine"

# Rate limiting: 60 requests/min for authenticated requests
_MIN_REQUEST_INTERVAL = 1.0  # 1 second between requests (safe margin)
_last_request_time = 0.0

_session = None


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


def _get_session() -> requests.Session:
    """Initialize and return a requests session with Discogs auth."""
    global _session
    if _session is not None:
        return _session

    _load_dotenv()
    token = os.environ.get("DISCOGS_API_TOKEN")
    if not token:
        print(
            "Error: DISCOGS_API_TOKEN environment variable not set.\n"
            "Get a personal access token at: https://www.discogs.com/settings/developers",
            file=sys.stderr,
        )
        sys.exit(1)

    _session = requests.Session()
    _session.headers.update({
        "Authorization": f"Discogs token={token}",
        "User-Agent": USER_AGENT,
    })
    return _session


def _rate_limit():
    """Sleep if needed to respect Discogs rate limits."""
    global _last_request_time
    now = time.monotonic()
    elapsed = now - _last_request_time
    if elapsed < _MIN_REQUEST_INTERVAL:
        time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.monotonic()


def _get(endpoint: str, params: dict | None = None) -> dict | None:
    """Make a GET request to the Discogs API with rate limiting."""
    session = _get_session()
    _rate_limit()

    url = f"{BASE_URL}{endpoint}" if endpoint.startswith("/") else endpoint
    try:
        resp = session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"Discogs API error: {e}", file=sys.stderr)
        return None


def search_artist(name: str) -> dict | None:
    """Search for an artist by name. Returns best match or None.

    Returns dict with: id, name, profile, resource_url, uri (Discogs page URL).
    """
    data = _get("/database/search", params={"q": name, "type": "artist"})
    if not data or not data.get("results"):
        print(f"No Discogs results for '{name}'", file=sys.stderr)
        return None

    # Find best match — prefer exact name match (case-insensitive)
    results = data["results"]
    best = results[0]
    for r in results:
        if r.get("title", "").lower() == name.lower():
            best = r
            break

    # Fetch full artist profile (search results don't include profile text)
    artist_data = _get(f"/artists/{best['id']}")
    if not artist_data:
        return {
            "id": best["id"],
            "name": best.get("title", name),
            "profile": "",
            "urls": [],
            "uri": best.get("uri", ""),
        }

    return {
        "id": artist_data["id"],
        "name": artist_data.get("name", name),
        "profile": artist_data.get("profile", ""),
        "urls": artist_data.get("urls", []),
        "uri": f"https://www.discogs.com/artist/{artist_data['id']}",
    }


def get_artist_releases(artist_id: int, page: int = 1) -> list[dict]:
    """Get an artist's releases from Discogs.

    Returns list of dicts with: title, year, type, label, id.
    """
    data = _get(f"/artists/{artist_id}/releases", params={
        "page": page,
        "per_page": 50,
        "sort": "year",
        "sort_order": "asc",
    })
    if not data or not data.get("releases"):
        return []

    releases = []
    for r in data["releases"]:
        releases.append({
            "id": r.get("id"),
            "title": r.get("title", ""),
            "year": r.get("year", 0),
            "type": r.get("type", ""),
            "role": r.get("role", ""),
            "label": r.get("label", ""),
        })

    return releases


def get_release(release_id: int) -> dict:
    """Get full release details from Discogs.

    Returns dict with: title, year, tracklist, genres, styles, labels, formats, notes.
    """
    data = _get(f"/releases/{release_id}")
    if not data:
        return {}

    tracklist = []
    for t in data.get("tracklist", []):
        if t.get("type_") == "track":
            tracklist.append({
                "position": t.get("position", ""),
                "title": t.get("title", ""),
                "duration": t.get("duration", ""),
            })

    labels = [l.get("name", "") for l in data.get("labels", [])]
    formats = [f.get("name", "") for f in data.get("formats", [])]

    return {
        "title": data.get("title", ""),
        "year": data.get("year", 0),
        "tracklist": tracklist,
        "genres": data.get("genres", []),
        "styles": data.get("styles", []),
        "labels": labels,
        "formats": formats,
        "notes": data.get("notes", ""),
    }


def get_artist_info(name: str) -> dict | None:
    """High-level: search for an artist and aggregate genre/style info from releases.

    Returns dict with: id, name, profile, urls, uri, genres, styles.
    Genres and styles are aggregated from the artist's first page of releases.
    """
    artist = search_artist(name)
    if not artist:
        return None

    # Fetch releases to aggregate genres and styles
    releases = get_artist_releases(artist["id"])

    all_genres = {}  # name -> count
    all_styles = {}  # name -> count

    # Sample up to 10 releases (main releases only, not appearances)
    sampled = 0
    for r in releases:
        if r.get("role", "").lower() not in ("main", ""):
            continue
        if r.get("type") not in ("release", "master"):
            continue
        if sampled >= 10:
            break

        # Fetch release details for genres/styles
        endpoint = "masters" if r["type"] == "master" else "releases"
        data = _get(f"/{endpoint}/{r['id']}")
        if not data:
            continue
        sampled += 1

        for g in data.get("genres", []):
            all_genres[g] = all_genres.get(g, 0) + 1
        for s in data.get("styles", []):
            all_styles[s] = all_styles.get(s, 0) + 1

    # Sort by frequency
    genres = sorted(all_genres, key=lambda g: -all_genres[g])
    styles = sorted(all_styles, key=lambda s: -all_styles[s])

    return {
        "id": artist["id"],
        "name": artist["name"],
        "profile": artist["profile"],
        "urls": artist["urls"],
        "uri": artist["uri"],
        "genres": genres,
        "styles": styles,
    }
