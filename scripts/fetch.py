#!/usr/bin/env python3
"""Lyra Engine CLI — fetch discographies and lyrics."""

import argparse
import sys
import os

# Add scripts dir to path so imports work when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import artist_dir, album_dir, song_path
from musicbrainz import search_artist, get_discography, get_tracklist, get_release_group_tags, get_recording_tags, get_artist_relationships
from markdown import write_song, write_album, write_artist, write_index, read_md, update_tags
from lyrics import fetch_lyrics, fetch_lyrics_from_url, init_genius, web_search_lyrics


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

    # Fetch relationships (members, external links)
    relationships = get_artist_relationships(artist_info["id"])

    # Write artist metadata
    a_dir = artist_dir(name)
    write_artist(a_dir, name, artist_info["id"], artist_info["country"],
                 artist_info["life_span"], discography,
                 tags=artist_info.get("tags", []),
                 relationships=relationships)
    print(f"\nWrote {a_dir / '_artist.md'}")
    if artist_info.get("tags"):
        print(f"  Tags: {', '.join(artist_info['tags'][:8])}")
    if relationships.get("members"):
        print(f"  Members: {', '.join(relationships['members'][:6])}")

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
        rels = get_artist_relationships(artist_info["id"])
        write_artist(a_dir, name, artist_info["id"], artist_info["country"],
                     artist_info["life_span"],
                     [match],
                     tags=artist_info.get("tags", []),
                     relationships=rels)

    write_index()
    print(f"\nDone: {len(tracks)} tracks, {missing} missing lyrics.")


def cmd_refresh_tags(args):
    """Re-fetch MusicBrainz tags for all existing artists/albums/songs."""
    from config import DATABASE_ROOT
    import time

    artists_updated = 0
    albums_updated = 0
    songs_updated = 0

    for artist_entry in sorted(DATABASE_ROOT.iterdir()):
        artist_md = artist_entry / "_artist.md"
        if not artist_entry.is_dir() or not artist_md.exists():
            continue

        fm, _ = read_md(artist_md)
        artist_name = fm.get("name", artist_entry.name)
        artist_mbid = fm.get("musicbrainz_artist_id", "")

        if not artist_mbid:
            print(f"Skipping {artist_name}: no MusicBrainz ID")
            continue

        print(f"\n{'='*50}")
        print(f"Refreshing tags for {artist_name}...")

        # Fetch artist-level tags
        try:
            import musicbrainzngs
            artist_detail = musicbrainzngs.get_artist_by_id(artist_mbid, includes=["tags"])
            raw_tags = artist_detail["artist"].get("tag-list", [])
            artist_tags = [t["name"] for t in sorted(raw_tags, key=lambda t: -int(t["count"]))
                          if int(t["count"]) >= 1]
        except Exception as e:
            print(f"  Error fetching artist tags: {e}")
            artist_tags = []

        if artist_tags:
            update_tags(artist_md, artist_tags)
            artists_updated += 1
            print(f"  Artist tags: {', '.join(artist_tags[:8])}")
        else:
            print(f"  No artist tags found")

        # Process each album directory
        for album_entry in sorted(artist_entry.iterdir()):
            album_md = album_entry / "_album.md"
            if not album_entry.is_dir() or not album_md.exists():
                continue

            afm, _ = read_md(album_md)
            rg_id = afm.get("musicbrainz_release_group_id", "")
            album_title = afm.get("title", album_entry.name)

            if not rg_id:
                continue

            # Fetch album-level tags
            album_tags = get_release_group_tags(rg_id)
            if album_tags:
                update_tags(album_md, album_tags)
                albums_updated += 1
                print(f"  {album_title}: {', '.join(album_tags[:6])}")

            # Process songs in this album
            for song_file in sorted(album_entry.glob("*.md")):
                if song_file.name.startswith("_"):
                    continue

                sfm, _ = read_md(song_file)
                rec_id = sfm.get("musicbrainz_recording_id", "")
                if not rec_id:
                    continue

                song_tags = get_recording_tags(rec_id)
                # Use song tags if available, otherwise inherit album tags
                effective_tags = song_tags or album_tags
                if effective_tags:
                    update_tags(song_file, effective_tags)
                    songs_updated += 1

            time.sleep(0.5)  # Be nice to MusicBrainz API

    print(f"\n{'='*50}")
    print(f"Tags refreshed:")
    print(f"  Artists: {artists_updated}")
    print(f"  Albums: {albums_updated}")
    print(f"  Songs: {songs_updated}")


def cmd_song(args):
    """Fetch or update lyrics for a single song, optionally from a URL."""
    from config import DATABASE_ROOT
    import glob as globmod

    # Find the song file
    pattern = f"artists/*/**/*{args.song}*.md"
    matches = [p for p in DATABASE_ROOT.parent.glob(pattern)
               if not p.name.startswith("_")]

    # Also try artist-scoped search
    if args.artist:
        artist_pattern = f"artists/{args.artist}*/**/*{args.song}*.md"
        artist_matches = [p for p in DATABASE_ROOT.parent.glob(artist_pattern)
                          if not p.name.startswith("_")]
        if artist_matches:
            matches = artist_matches

    if not matches:
        print(f"No song file matching '{args.song}' found.", file=sys.stderr)
        if args.artist:
            print(f"  (searched in artists matching '{args.artist}')", file=sys.stderr)
        sys.exit(1)

    if len(matches) > 1:
        print(f"Multiple matches for '{args.song}':")
        for i, m in enumerate(matches[:10], 1):
            print(f"  {i}. {m.relative_to(DATABASE_ROOT.parent)}")
        try:
            choice = input("Which one? [1]: ").strip()
        except EOFError:
            choice = "1"
        idx = int(choice) - 1 if choice.isdigit() else 0
        song_file = matches[idx]
    else:
        song_file = matches[0]

    print(f"Song: {song_file.relative_to(DATABASE_ROOT.parent)}")

    fm, body = read_md(song_file)
    artist = fm.get("artist", "")
    title = fm.get("title", "")

    if args.url:
        # Fetch from provided URL
        print(f"Fetching lyrics from URL: {args.url}")
        lyrics = fetch_lyrics_from_url(args.url)
        if lyrics:
            fm["genius_url"] = args.url
            from markdown import _write_md
            _write_md(song_file, fm, lyrics)
            print(f"Updated with lyrics from URL ({len(lyrics)} chars)")
        else:
            print("Could not extract lyrics from URL.", file=sys.stderr)
    elif args.paste:
        # Read from stdin
        print("Paste lyrics below (Ctrl+D when done):")
        try:
            lyrics = sys.stdin.read().strip()
        except EOFError:
            lyrics = ""
        if lyrics:
            from markdown import _write_md
            _write_md(song_file, fm, lyrics)
            print(f"Updated with pasted lyrics ({len(lyrics)} chars)")
        else:
            print("No lyrics provided.", file=sys.stderr)
    else:
        # Try Genius
        init_genius()
        print(f"Searching Genius for '{title}' by {artist}...")
        lyrics, url = fetch_lyrics(artist, title)
        if lyrics:
            fm["genius_url"] = url or ""
            from markdown import _write_md
            _write_md(song_file, fm, lyrics)
            print(f"Updated with lyrics from Genius ({len(lyrics)} chars)")
        else:
            # Try fallback sources
            print("Not found on Genius. Trying fallback sources...")
            lyrics = web_search_lyrics(artist, title)
            if lyrics:
                from markdown import _write_md
                _write_md(song_file, fm, lyrics)
                print(f"Updated with lyrics from fallback ({len(lyrics)} chars)")
            else:
                print(f"Not found on any source. Try:")
                print(f"  --url <url>          Provide a direct lyrics URL")
                print(f"  --paste              Paste lyrics from stdin")


def cmd_missing(args):
    """List all songs with missing lyrics, optionally retry fetching."""
    from config import DATABASE_ROOT

    missing = []
    for artist_entry in sorted(DATABASE_ROOT.iterdir()):
        if not artist_entry.is_dir() or artist_entry.name.startswith("_"):
            continue
        for album_entry in sorted(artist_entry.iterdir()):
            if not album_entry.is_dir():
                continue
            for song_file in sorted(album_entry.glob("*.md")):
                if song_file.name.startswith("_"):
                    continue
                fm, body = read_md(song_file)
                if "[Lyrics not found]" in body:
                    rel = song_file.relative_to(DATABASE_ROOT)
                    missing.append((song_file, fm, rel))

    if not missing:
        print("No missing lyrics!")
        return

    print(f"Songs with missing lyrics: {len(missing)}\n")

    if args.artist:
        missing = [(f, fm, r) for f, fm, r in missing
                   if fm.get("artist", "").lower() == args.artist.lower()
                   or args.artist.lower() in str(r).lower()]
        print(f"  (filtered to '{args.artist}': {len(missing)} songs)\n")

    for song_file, fm, rel in missing:
        artist = fm.get("artist", "?")
        title = fm.get("title", "?")
        print(f"  {artist} — {title}")
        print(f"    {rel}")

    if args.retry:
        print(f"\nRetrying Genius for {len(missing)} songs...")
        init_genius()
        found = 0
        for song_file, fm, rel in missing:
            artist = fm.get("artist", "")
            title = fm.get("title", "")
            print(f"  {title} ... ", end="", flush=True)
            lyrics, url = fetch_lyrics(artist, title)
            if lyrics:
                fm["genius_url"] = url or ""
                from markdown import _write_md
                _write_md(song_file, fm, lyrics)
                found += 1
                print("OK")
            else:
                # Try fallback sources
                print("not on Genius, trying fallback sources...", end=" ", flush=True)
                lyrics = web_search_lyrics(artist, title)
                if lyrics:
                    from markdown import _write_md
                    _write_md(song_file, fm, lyrics)
                    found += 1
                    print("OK (fallback)")
                else:
                    print("still missing")
        print(f"\nRetry complete: {found}/{len(missing)} found")


def cmd_similar(args):
    """Find similar artists using MusicBrainz tags and show which are in the database."""
    from config import DATABASE_ROOT

    # Find the artist
    artist_info = search_artist(args.name)
    if not artist_info:
        sys.exit(1)

    name = artist_info["name"]
    tags = artist_info.get("tags", [])
    print(f"Artist: {name}")
    print(f"Tags: {', '.join(tags[:10])}")

    # Get which artists are already in the database
    db_artists = set()
    for entry in DATABASE_ROOT.iterdir():
        if entry.is_dir() and (entry / "_artist.md").exists():
            fm, _ = read_md(entry / "_artist.md")
            db_artists.add(fm.get("name", entry.name).lower())

    # Search MusicBrainz for artists with similar tags
    if not tags:
        print("\nNo tags available for similarity search.")
        return

    print(f"\nSearching for similar artists (by shared tags)...")
    import musicbrainzngs
    similar = {}

    # Use more specific/niche tags first (skip generic ones)
    generic_tags = {"rock", "metal", "electronic", "pop", "alternative", "indie",
                    "heavy metal", "pop/rock", "alternative rock"}
    specific_tags = [t for t in tags if t.lower() not in generic_tags]
    search_tags = (specific_tags or tags)[:5]

    for tag in search_tags:
        try:
            result = musicbrainzngs.search_artists(tag=tag, limit=50)
            for a in result.get("artist-list", []):
                a_name = a["name"]
                a_id = a["id"]
                score = int(a.get("ext:score", 0))
                if a_name.lower() == name.lower():
                    continue
                # Skip very generic matches (low relevance)
                if score < 50:
                    continue
                if a_id not in similar:
                    similar[a_id] = {"name": a_name, "tags": [], "score": 0,
                                     "country": a.get("country", "??"),
                                     "in_db": a_name.lower() in db_artists}
                similar[a_id]["tags"].append(tag)
                similar[a_id]["score"] += 1
        except Exception:
            continue

    # Sort by shared tag count, then by name
    ranked = sorted(similar.values(), key=lambda x: (-x["score"], x["name"]))

    print(f"\n{'─'*60}")
    print(f"{'Artist':<30} {'Country':>4} {'Shared Tags':>12} {'In DB':>6}")
    print(f"{'─'*60}")
    for s in ranked[:25]:
        in_db = " YES" if s["in_db"] else ""
        tags_str = ", ".join(s["tags"][:3])
        print(f"{s['name']:<30} {s['country']:>4} {tags_str:>12} {in_db:>6}")

    in_db_count = sum(1 for s in ranked[:25] if s["in_db"])
    print(f"\n{in_db_count} of top 25 similar artists already in database")


def cmd_stats(args):
    """Show database statistics: genres, moods, artists, song counts."""
    from config import DATABASE_ROOT
    from collections import Counter

    genres = Counter()
    moods = Counter()
    artists = []
    total_songs = 0
    total_with_lyrics = 0

    for artist_entry in sorted(DATABASE_ROOT.iterdir()):
        artist_md = artist_entry / "_artist.md"
        if not artist_entry.is_dir() or not artist_md.exists():
            continue

        fm, _ = read_md(artist_md)
        artist_name = fm.get("name", artist_entry.name)
        artist_genre = fm.get("genre", "")
        song_count = 0
        lyrics_count = 0

        for album_entry in sorted(artist_entry.iterdir()):
            if not album_entry.is_dir():
                continue
            for song_file in album_entry.glob("*.md"):
                if song_file.name.startswith("_"):
                    continue
                song_count += 1
                sfm, body = read_md(song_file)

                # Count lyrics
                if body.strip() and "[Lyrics not found]" not in body:
                    lyrics_count += 1

                # Collect genres/moods
                g = sfm.get("genre", "")
                m = sfm.get("mood", "")
                if g:
                    for tag in [t.strip() for t in g.split(",")]:
                        if tag:
                            genres[tag] += 1
                if m:
                    for tag in [t.strip() for t in m.split(",")]:
                        if tag:
                            moods[tag] += 1

        artists.append((artist_name, artist_genre, song_count, lyrics_count))
        total_songs += song_count
        total_with_lyrics += lyrics_count

    # Print summary
    print(f"{'='*60}")
    print(f"LYRA ENGINE STATS")
    print(f"{'='*60}")
    print(f"\nArtists: {len(artists)}  |  Songs: {total_songs}  |  With lyrics: {total_with_lyrics}")
    print(f"\n{'─'*60}")
    print(f"{'Artist':<25} {'Genre':<25} {'Songs':>6} {'Lyrics':>7}")
    print(f"{'─'*60}")
    for name, genre, songs, lyrics in artists:
        g = genre[:24] if genre else "(none)"
        print(f"{name:<25} {g:<25} {songs:>6} {lyrics:>7}")

    if genres:
        print(f"\n{'─'*60}")
        print(f"GENRES (by song count):")
        for tag, count in genres.most_common(30):
            print(f"  {tag:<35} {count:>5} songs")

    if moods:
        print(f"\n{'─'*60}")
        print(f"MOODS (by song count):")
        for tag, count in moods.most_common(20):
            print(f"  {tag:<35} {count:>5} songs")


def cmd_suggest(args):
    """Analyze database and suggest new artists based on genre gaps and diversity."""
    from config import DATABASE_ROOT
    from collections import Counter
    import musicbrainzngs

    # 1. Scan all artists, collect genre and tag data
    db_artists = set()
    genre_counter = Counter()
    tag_counter = Counter()
    artist_genres = {}

    for artist_entry in sorted(DATABASE_ROOT.iterdir()):
        artist_md = artist_entry / "_artist.md"
        if not artist_entry.is_dir() or not artist_md.exists():
            continue

        fm, _ = read_md(artist_md)
        artist_name = fm.get("name", artist_entry.name)
        db_artists.add(artist_name.lower())

        # Collect genre
        genre = fm.get("genre", "")
        if genre:
            for g in [t.strip() for t in genre.split(",")]:
                if g:
                    genre_counter[g] += 1
                    artist_genres.setdefault(g, []).append(artist_name)

        # Collect musicbrainz_tags
        mb_tags = fm.get("musicbrainz_tags", [])
        if isinstance(mb_tags, str):
            mb_tags = [t.strip() for t in mb_tags.split(",")]
        if mb_tags:
            for t in mb_tags:
                t = t.strip()
                if t:
                    tag_counter[t] += 1

    if not db_artists:
        print("No artists found in database.")
        return

    print(f"{'='*60}")
    print(f"GENRE DIVERSITY ANALYSIS")
    print(f"{'='*60}")
    print(f"\nArtists in database: {len(db_artists)}")

    # 2. Well-covered genres (sorted by count descending)
    print(f"\n{'─'*60}")
    print(f"WELL-COVERED GENRES:")
    well_covered = [(g, c) for g, c in genre_counter.most_common() if c >= 2]
    if well_covered:
        for g, c in well_covered:
            names = ", ".join(artist_genres[g][:4])
            extra = f" (+{c - 4} more)" if c > 4 else ""
            print(f"  {g:<30} {c:>3} artists  ({names}{extra})")
    else:
        print("  (none — no genre has 2+ artists yet)")

    # 3. Identify gap genres — genres that appear in tags but have few artists
    # Combine genre and tag data; gap = appears in tags but has <=1 artist in genre_counter
    all_known_tags = set(tag_counter.keys()) | set(genre_counter.keys())
    gap_genres = []
    for tag in all_known_tags:
        artist_count = genre_counter.get(tag, 0)
        if artist_count <= 1:
            tag_mentions = tag_counter.get(tag, 0) + artist_count
            if tag_mentions >= 1:
                gap_genres.append((tag, artist_count, tag_mentions))

    # Sort by tag mentions descending (most referenced but least covered)
    gap_genres.sort(key=lambda x: (-x[2], x[0]))

    print(f"\n{'─'*60}")
    print(f"UNDER-REPRESENTED GENRES:")
    if gap_genres:
        for tag, artist_count, mentions in gap_genres[:20]:
            status = f"{artist_count} artist(s)" if artist_count else "0 artists"
            print(f"  {tag:<30} {status}, mentioned {mentions}x in tags")
    else:
        print("  (no gaps detected)")

    # 4. Search MusicBrainz for artists in gap genres
    print(f"\n{'─'*60}")
    print(f"SUGGESTED ARTISTS TO ADD:")
    print(f"{'─'*60}")

    suggestions_found = 0
    search_genres = [g for g, _, _ in gap_genres[:10]]  # Top 10 gap genres

    if not search_genres:
        print("  (no gap genres to search for)")
    else:
        for genre in search_genres:
            try:
                result = musicbrainzngs.search_artists(tag=genre, limit=10)
            except Exception as e:
                print(f"  [{genre}] Search error: {e}")
                continue

            candidates = []
            for a in result.get("artist-list", []):
                a_name = a["name"]
                score = int(a.get("ext:score", 0))
                if a_name.lower() in db_artists:
                    continue
                if score < 50:
                    continue
                # Filter out non-artist entries
                if a_name.lower() in ("various artists", "[unknown]"):
                    continue
                candidates.append({
                    "name": a_name,
                    "country": a.get("country", "??"),
                    "score": score,
                })

            if candidates:
                print(f"\n  [{genre}]")
                for c in candidates[:5]:
                    suggestions_found += 1
                    print(f"    {c['name']:<35} ({c['country']}, score: {c['score']})")

    print(f"\n{'='*60}")
    print(f"Total suggestions: {suggestions_found}")


def cmd_discogs(args):
    """Fetch Discogs data and enrich existing _artist.md."""
    from discogs import get_artist_info
    from markdown import _write_md

    name = args.name
    adir = artist_dir(name)
    artist_file = adir / "_artist.md"

    # Find existing artist file (try case-insensitive match)
    if not artist_file.exists():
        from config import DATABASE_ROOT
        found = False
        for entry in DATABASE_ROOT.iterdir():
            if entry.is_dir() and (entry / "_artist.md").exists():
                fm, _ = read_md(entry / "_artist.md")
                if fm.get("name", "").lower() == name.lower():
                    adir = entry
                    artist_file = entry / "_artist.md"
                    found = True
                    break
        if not found:
            print(f"Error: No existing artist file found for '{name}'.", file=sys.stderr)
            print("Run 'fetch.py artist' first to create the artist.", file=sys.stderr)
            sys.exit(1)

    print(f"Fetching Discogs data for '{name}'...")
    info = get_artist_info(name)
    if not info:
        print("Could not find artist on Discogs.", file=sys.stderr)
        sys.exit(1)

    print(f"  Discogs match: {info['name']} (id: {info['id']})")
    print(f"  Discogs URL:   {info['uri']}")
    if info["genres"]:
        print(f"  Genres:        {', '.join(info['genres'])}")
    if info["styles"]:
        print(f"  Styles:        {', '.join(info['styles'])}")
    if info["profile"]:
        profile_preview = info["profile"][:120]
        if len(info["profile"]) > 120:
            profile_preview += "..."
        print(f"  Profile:       {profile_preview}")

    # Read existing frontmatter and body
    fm, body = read_md(artist_file)
    if not fm:
        print(f"Error: Could not parse frontmatter in {artist_file}", file=sys.stderr)
        sys.exit(1)

    # Update frontmatter with Discogs data
    updated = []
    if info["profile"]:
        fm["discogs_profile"] = info["profile"]
        updated.append("discogs_profile")
    if info["styles"]:
        fm["discogs_styles"] = info["styles"]
        updated.append("discogs_styles")
    if info["uri"]:
        fm["discogs_url"] = info["uri"]
        updated.append("discogs_url")
    if info["genres"]:
        fm["discogs_genres"] = info["genres"]
        updated.append("discogs_genres")

    if updated:
        _write_md(artist_file, fm, body)
        print(f"\nUpdated {artist_file}:")
        for field in updated:
            print(f"  + {field}")
    else:
        print("\nNo new data to add.")


def cmd_index(args):
    """Regenerate the root index."""
    write_index()
    print("Regenerated _index.md")


def main():
    parser = argparse.ArgumentParser(
        description="Lyra Engine — fetch discographies and lyrics"
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

    # song subcommand
    p_song = sub.add_parser("song", help="Fetch/update lyrics for a single song")
    p_song.add_argument("song", help="Song title (partial match)")
    p_song.add_argument("--artist", help="Artist name (narrows search)")
    p_song.add_argument("--url", help="Genius URL to scrape lyrics from")
    p_song.add_argument("--paste", action="store_true",
                        help="Paste lyrics from stdin")
    p_song.set_defaults(func=cmd_song)

    # missing subcommand
    p_missing = sub.add_parser("missing", help="List/retry songs with missing lyrics")
    p_missing.add_argument("--artist", help="Filter to specific artist")
    p_missing.add_argument("--retry", action="store_true",
                           help="Retry fetching from Genius")
    p_missing.set_defaults(func=cmd_missing)

    # similar subcommand
    p_similar = sub.add_parser("similar", help="Find similar artists via MusicBrainz tags")
    p_similar.add_argument("name", help="Artist name")
    p_similar.set_defaults(func=cmd_similar)

    # refresh-tags subcommand
    p_refresh = sub.add_parser("refresh-tags", help="Re-fetch MusicBrainz tags for all artists")
    p_refresh.set_defaults(func=cmd_refresh_tags)

    # stats subcommand
    p_stats = sub.add_parser("stats", help="Show database statistics (genres, moods, counts)")
    p_stats.set_defaults(func=cmd_stats)

    # suggest subcommand
    p_suggest = sub.add_parser("suggest", help="Suggest new artists based on genre gaps and diversity")
    p_suggest.set_defaults(func=cmd_suggest)

    # discogs subcommand
    p_discogs = sub.add_parser("discogs", help="Enrich artist with Discogs profile/styles")
    p_discogs.add_argument("name", help="Artist name")
    p_discogs.set_defaults(func=cmd_discogs)

    # index subcommand
    p_index = sub.add_parser("index", help="Regenerate root index")
    p_index.set_defaults(func=cmd_index)

    # enrich subcommand
    from enrich import cmd_enrich, _build_parser as _enrich_parser
    p_enrich = sub.add_parser("enrich",
                              help="Suggest enrichment tags (mood, style, energy, themes)")
    _enrich_parser(p_enrich)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
