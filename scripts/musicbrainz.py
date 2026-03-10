"""MusicBrainz API client for artist search, discography, and track listings."""

import sys

import musicbrainzngs

musicbrainzngs.set_useragent("lyrics-database", "0.1", "https://github.com/example")

# Release group primary types we care about
DEFAULT_TYPES = ["album", "ep"]


def search_artist(name: str) -> dict | None:
    """Search for an artist by name. Returns top match or None."""
    result = musicbrainzngs.search_artists(artist=name, limit=5)
    artists = result.get("artist-list", [])
    if not artists:
        print(f"No artist found for '{name}'", file=sys.stderr)
        return None

    top = artists[0]
    score = int(top.get("ext:score", 0))
    if score < 80:
        print(f"Warning: best match '{top['name']}' has low score ({score})", file=sys.stderr)

    return {
        "id": top["id"],
        "name": top["name"],
        "country": top.get("country", ""),
        "life_span": top.get("life-span", {}),
    }


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
