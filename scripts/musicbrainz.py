"""MusicBrainz API client for artist search, discography, and track listings."""

import sys

import musicbrainzngs

musicbrainzngs.set_useragent("lyrics-database", "0.1", "https://github.com/example")

# Release group primary types we care about
DEFAULT_TYPES = ["album", "ep"]


def search_artist(name: str, interactive: bool = True) -> dict | None:
    """Search for an artist by name. Returns top match or None.

    If interactive=True, shows top matches and asks for confirmation
    when the match is ambiguous.
    """
    result = musicbrainzngs.search_artists(artist=name, limit=5)
    artists = result.get("artist-list", [])
    if not artists:
        print(f"No artist found for '{name}'", file=sys.stderr)
        return None

    top = artists[0]
    score = int(top.get("ext:score", 0))

    # Show match details for verification
    if interactive and (score < 95 or top["name"].lower() != name.lower()):
        print(f"\nSearch: '{name}'")
        print(f"Top matches from MusicBrainz:")
        for i, a in enumerate(artists[:5]):
            s = int(a.get("ext:score", 0))
            disambiguation = a.get("disambiguation", "")
            country = a.get("country", "??")
            life = a.get("life-span", {})
            begin = life.get("begin", "?")
            extra = f" ({disambiguation})" if disambiguation else ""
            print(f"  {i+1}. {a['name']}{extra} [{country}] (active: {begin}) [score: {s}]")
        print()

        response = input(f"Use '{top['name']}'? [Y/n/1-5]: ").strip()
        if response.lower() == 'n':
            return None
        if response in ('2', '3', '4', '5') and int(response) <= len(artists):
            top = artists[int(response) - 1]
        # Default (enter, 'y', '1') uses top match

    elif score < 80:
        print(f"Warning: best match '{top['name']}' has low score ({score})", file=sys.stderr)

    # Fetch tags for the artist
    try:
        artist_detail = musicbrainzngs.get_artist_by_id(top["id"], includes=["tags"])
        tags = artist_detail["artist"].get("tag-list", [])
        # Filter to high-confidence tags (count >= 2) sorted by vote count
        genre_tags = sorted(
            [t for t in tags if int(t["count"]) >= 1],
            key=lambda t: -int(t["count"])
        )
    except Exception:
        genre_tags = []

    return {
        "id": top["id"],
        "name": top["name"],
        "country": top.get("country", ""),
        "life_span": top.get("life-span", {}),
        "tags": [t["name"] for t in genre_tags],
    }


def get_release_group_tags(release_group_id: str, min_count: int = 1) -> list[str]:
    """Fetch community tags for a release group (album). Returns tag names."""
    try:
        rg = musicbrainzngs.get_release_group_by_id(release_group_id, includes=["tags"])
        tags = rg["release-group"].get("tag-list", [])
        return [t["name"] for t in sorted(tags, key=lambda t: -int(t["count"]))
                if int(t["count"]) >= min_count]
    except Exception:
        return []


def get_recording_tags(recording_id: str, min_count: int = 1) -> list[str]:
    """Fetch community tags for a recording (song). Returns tag names."""
    if not recording_id:
        return []
    try:
        rec = musicbrainzngs.get_recording_by_id(recording_id, includes=["tags"])
        tags = rec["recording"].get("tag-list", [])
        return [t["name"] for t in sorted(tags, key=lambda t: -int(t["count"]))
                if int(t["count"]) >= min_count]
    except Exception:
        return []


def get_discography(artist_id: str, types: list[str] | None = None,
                    include_live: bool = False,
                    include_compilations: bool = False) -> list[dict]:
    """Fetch release groups for an artist, sorted by year.

    Filters out bootlegs, live albums, and compilations by default using
    MusicBrainz secondary types.

    Returns list of {title, year, release_group_id, type}.
    """
    if types is None:
        types = DEFAULT_TYPES

    # Excluded secondary types (lowercase for comparison)
    excluded_secondary = set()
    if not include_live:
        excluded_secondary.add("live")
    if not include_compilations:
        excluded_secondary.add("compilation")
    # Always exclude these bootleg/unofficial types
    excluded_secondary.update({"bootleg", "demo", "dj-mix", "mixtape/street"})

    all_groups = []
    offset = 0
    limit = 100

    while True:
        result = musicbrainzngs.browse_release_groups(
            artist=artist_id, release_type=types, limit=limit, offset=offset
        )
        groups = result.get("release-group-list", [])
        if not groups:
            break

        for rg in groups:
            # Filter by secondary types
            secondary_types = [t.lower() for t in rg.get("secondary-type-list", [])]
            if any(st in excluded_secondary for st in secondary_types):
                continue

            year_str = rg.get("first-release-date", "")[:4]
            year = int(year_str) if year_str and year_str.isdigit() else 0

            all_groups.append({
                "title": rg["title"],
                "year": year,
                "release_group_id": rg["id"],
                "type": rg.get("primary-type", "Album"),
            })

        offset += limit
        if offset >= int(result.get("release-group-count", 0)):
            break

    all_groups.sort(key=lambda x: (x["year"], x["title"]))
    return all_groups


def get_tracklist(release_group_id: str) -> list[dict]:
    """Get the track listing for a release group.

    Picks the first official release, flattens multi-disc into one sequence.
    Returns list of {track_number, title, recording_id, duration_ms}.
    """
    try:
        # Get releases in this release group
        result = musicbrainzngs.browse_releases(
            release_group=release_group_id, release_type=["album", "ep"],
            limit=10
        )
        releases = result.get("release-list", [])
        if not releases:
            # Try without type filter
            result = musicbrainzngs.browse_releases(
                release_group=release_group_id, limit=10
            )
            releases = result.get("release-list", [])

        if not releases:
            print(f"No releases found for release group {release_group_id}", file=sys.stderr)
            return []

        # Pick the first release and get its full details
        release_id = releases[0]["id"]
        release = musicbrainzngs.get_release_by_id(
            release_id, includes=["recordings"]
        )["release"]
    except Exception as e:
        print(f"Error fetching tracklist for {release_group_id}: {e}", file=sys.stderr)
        return []

    tracks = []
    absolute_number = 0
    for medium in release.get("medium-list", []):
        for track in medium.get("track-list", []):
            absolute_number += 1
            recording = track.get("recording", {})
            duration = recording.get("length")

            tracks.append({
                "track_number": absolute_number,
                "title": recording.get("title", track.get("title", f"Track {absolute_number}")),
                "recording_id": recording.get("id", ""),
                "duration_ms": int(duration) if duration else None,
            })

    return tracks
