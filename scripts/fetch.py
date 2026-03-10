#!/usr/bin/env python3
"""Lyrics Database CLI — fetch discographies and lyrics."""

import argparse
import sys
import os

# Add scripts dir to path so imports work when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import artist_dir, album_dir, song_path
from musicbrainz import search_artist, get_discography, get_tracklist, get_release_group_tags, get_recording_tags
from markdown import write_song, write_album, write_artist, write_index
from lyrics import fetch_lyrics, init_genius


def has_lyrics(path):
    """Check if a song file exists and has real lyrics (not placeholder)."""
    if not path.exists():
        return False
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return "[Lyrics not found]" not in content


def cmd_artist(args):
    """Fetch full discography and lyrics for an artist."""
    # Search for the artist
    artist_info = search_artist(args.name)
    if not artist_info:
        sys.exit(1)

    name = artist_info["name"]
    print(f"Found: {name} (MusicBrainz: {artist_info['id']})")

    # Build type list based on flags
    types = ["album", "ep"]
    if args.include_singles:
        types.append("single")

    # Fetch discography
    discography = get_discography(
        artist_info["id"], types=types,
        include_live=args.include_live,
        include_compilations=args.include_compilations,
    )
    if not discography:
        print("No releases found.", file=sys.stderr)
        sys.exit(1)

    print(f"\nDiscography ({len(discography)} releases):")
    for album in discography:
        print(f"  {album['year']} - {album['title']} ({album['type']})")

    # Write artist metadata
    a_dir = artist_dir(name)
    write_artist(a_dir, name, artist_info["id"], artist_info["country"],
                 artist_info["life_span"], discography,
                 tags=artist_info.get("tags", []))
    print(f"\nWrote {a_dir / '_artist.md'}")
    if artist_info.get("tags"):
        print(f"  Tags: {', '.join(artist_info['tags'][:8])}")

    # Initialize Genius if we need lyrics
    if not args.albums_only:
        init_genius()

    # Process each album
    total_tracks = 0
    total_fetched = 0
    total_missing = 0
    total_skipped = 0

    for album_idx, album in enumerate(discography, 1):
        print(f"\n--- [{album_idx}/{len(discography)}] {album['year']} - {album['title']} ---")

        # Get track listing
        tracks = get_tracklist(album["release_group_id"])
        if not tracks:
            print("  No tracks found, skipping.", file=sys.stderr)
            continue

        # Fetch album-level tags
        album_tags = get_release_group_tags(album["release_group_id"])
        if album_tags:
            print(f"  Tags: {', '.join(album_tags[:6])}")

        al_dir = album_dir(name, album["year"], album["title"])
        missing_lyrics = 0

        for track in tracks:
            total_tracks += 1
            s_path = song_path(name, album["year"], album["title"],
                               track["track_number"], track["title"])

            # Idempotency: skip if already fetched with lyrics
            if not args.force and has_lyrics(s_path):
                total_skipped += 1
                print(f"  {track['track_number']:2d}. {track['title']} [skipped]")
                continue

            lyrics_text = None
            genius_url = ""

            # Fetch per-song tags from MusicBrainz
            song_tags = get_recording_tags(track["recording_id"])

            if not args.albums_only:
                print(f"  {track['track_number']:2d}/{len(tracks)} {track['title']} ... ", end="", flush=True)
                lyrics_text, genius_url = fetch_lyrics(name, track["title"])
                if lyrics_text:
                    total_fetched += 1
                    print("OK")
                else:
                    missing_lyrics += 1
                    total_missing += 1
                    print("not found")
            else:
                print(f"  {track['track_number']:2d}. {track['title']}")
                missing_lyrics += 1
                total_missing += 1

            write_song(s_path, track["title"], name, album["title"],
                       album["year"], track["track_number"],
                       recording_id=track["recording_id"],
                       genius_url=genius_url or "",
                       lyrics=lyrics_text,
                       tags=song_tags or album_tags)

        # Write album metadata
        write_album(al_dir, album["title"], name, album["year"],
                    album["type"], tracks,
                    release_group_id=album["release_group_id"],
                    tracks_missing_lyrics=missing_lyrics,
                    tags=album_tags)

    # Regenerate index
    write_index()

    # Summary
    print(f"\n{'='*50}")
    print(f"Summary for {name}:")
    print(f"  Albums: {len(discography)}")
    print(f"  Total tracks: {total_tracks}")
    if not args.albums_only:
        print(f"  Lyrics fetched: {total_fetched}")
        print(f"  Missing lyrics: {total_missing}")
    print(f"  Skipped (existing): {total_skipped}")


def cmd_album(args):
    """Fetch a single album."""
    artist_info = search_artist(args.artist)
    if not artist_info:
        sys.exit(1)

    name = artist_info["name"]
    print(f"Found artist: {name}")

    # Find the album in discography — search broadly
    types = ["album", "ep", "single"]
    discography = get_discography(
        artist_info["id"], types=types,
        include_live=True, include_compilations=True,
    )

    target = args.album.lower()
    match = None
    for album in discography:
        if album["title"].lower() == target:
            match = album
            break

    if not match:
        # Try partial match
        for album in discography:
            if target in album["title"].lower():
                match = album
                break

    if not match:
        print(f"Album '{args.album}' not found. Available:", file=sys.stderr)
        for album in discography:
            print(f"  {album['year']} - {album['title']}", file=sys.stderr)
        sys.exit(1)

    print(f"Found album: {match['year']} - {match['title']}")

    init_genius()

    tracks = get_tracklist(match["release_group_id"])
    if not tracks:
        print("No tracks found.", file=sys.stderr)
        sys.exit(1)

    # Fetch album-level tags
    album_tags = get_release_group_tags(match["release_group_id"])
    if album_tags:
        print(f"  Tags: {', '.join(album_tags[:6])}")

    al_dir = album_dir(name, match["year"], match["title"])
    missing = 0

    for track in tracks:
        s_path = song_path(name, match["year"], match["title"],
                           track["track_number"], track["title"])

        if not args.force and has_lyrics(s_path):
            print(f"  {track['track_number']:2d}. {track['title']} [skipped]")
            continue

        song_tags = get_recording_tags(track["recording_id"])

        print(f"  {track['track_number']:2d}. {track['title']} ... ", end="", flush=True)
        lyrics_text, genius_url = fetch_lyrics(name, track["title"])
        if lyrics_text:
            print("OK")
        else:
            missing += 1
            print("not found")

        write_song(s_path, track["title"], name, match["title"],
                   match["year"], track["track_number"],
                   recording_id=track["recording_id"],
                   genius_url=genius_url or "",
                   lyrics=lyrics_text,
                   tags=song_tags or album_tags)

    write_album(al_dir, match["title"], name, match["year"],
                match["type"], tracks,
                release_group_id=match["release_group_id"],
                tracks_missing_lyrics=missing,
                tags=album_tags)

    # Ensure artist file exists
    a_dir = artist_dir(name)
    if not (a_dir / "_artist.md").exists():
        write_artist(a_dir, name, artist_info["id"], artist_info["country"],
                     artist_info["life_span"],
                     [match],
                     tags=artist_info.get("tags", []))

    write_index()
    print(f"\nDone: {len(tracks)} tracks, {missing} missing lyrics.")


def cmd_index(args):
    """Regenerate the root index."""
    write_index()
    print("Regenerated _index.md")


def main():
    parser = argparse.ArgumentParser(
        description="Lyrics Database — fetch discographies and lyrics"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # artist subcommand
    p_artist = sub.add_parser("artist", help="Fetch full discography + lyrics")
    p_artist.add_argument("name", help="Artist name")
    p_artist.add_argument("--albums-only", action="store_true",
                          help="Scaffold directory structure only, skip lyrics")
    p_artist.add_argument("--force", action="store_true",
                          help="Re-fetch even if files exist")
    p_artist.add_argument("--include-compilations", action="store_true",
                          help="Include compilation albums")
    p_artist.add_argument("--include-live", action="store_true",
                          help="Include live albums")
    p_artist.add_argument("--include-singles", action="store_true",
                          help="Include singles")
    p_artist.set_defaults(func=cmd_artist)

    # album subcommand
    p_album = sub.add_parser("album", help="Fetch a single album")
    p_album.add_argument("artist", help="Artist name")
    p_album.add_argument("album", help="Album title")
    p_album.add_argument("--force", action="store_true",
                          help="Re-fetch even if files exist")
    p_album.set_defaults(func=cmd_album)

    # index subcommand
    p_index = sub.add_parser("index", help="Regenerate root index")
    p_index.set_defaults(func=cmd_index)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
