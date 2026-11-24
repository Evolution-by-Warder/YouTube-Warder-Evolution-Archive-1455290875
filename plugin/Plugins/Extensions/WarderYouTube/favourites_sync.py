# -*- coding: utf-8 -*-
"""One-way refresh of the receiver's favourites from real YouTube account likes.

Runs entirely in a background worker when the owner opens Favourites. Never
uploads local favourites or clears either list; token and credentials remain
confined to the existing account reader.
"""
from .local_library import LIMITS, merge_youtube_favourites
from .video_ratings import (liked_videos_page, liked_playlist_id,
                            liked_playlist_page, VideoRatingError)

MAX_SYNC_PAGES = 110  # Up to 5,500 items when Likes playlist is accessible.
RECENT_API_PAGES = 20  # videos.list(myRating=like) is capped at 1,000.


def sync_youtube_favourites(fetch_page=None,
                            merge=merge_youtube_favourites, cancelled=None,
                            progress=None):
    """Fetch a bounded, deduplicated snapshot before one atomic local merge.

    If YouTube fails at any page, do not modify the receiver's favourites.
    A repeating page token is treated as a truncated response, not an infinite
    loop. Existing favourites always take precedence and are never removed.
    """
    # Prefer the system Likes playlist, which can expose more than the 1,000
    # most recent items returned by videos.list(myRating=like).
    using_playlist = False
    if fetch_page is None:
        try:
            playlist_id = liked_playlist_id()
        except VideoRatingError:
            playlist_id = ""
        if playlist_id:
            using_playlist = True
            fetch_page = lambda token: liked_playlist_page(playlist_id, token)
        else:
            fetch_page = liked_videos_page
    videos, identifiers, tokens = [], set(), set()
    next_page = ""
    truncated = False
    first_page_added = 0
    for page_index in range(MAX_SYNC_PAGES if using_playlist else RECENT_API_PAGES):
        if cancelled is not None and cancelled.is_set():
            return {"cancelled": True, "added": 0}
        try:
            page = fetch_page(next_page)
        except VideoRatingError:
            if not using_playlist or page_index != 0:
                raise
            # Special Likes playlist access varies. Keep the existing
            # authenticated rating-list reader as a safe fallback.
            using_playlist = False
            fetch_page = liked_videos_page
            page = fetch_page("")
        if not isinstance(page, dict) or not isinstance(page.get("items"), list):
            raise VideoRatingError("YouTube vrátil neplatné údaje obľúbených.")
        for item in page["items"]:
            if not isinstance(item, dict):
                continue
            identifier = item.get("video_id")
            if isinstance(identifier, str) and identifier not in identifiers:
                identifiers.add(identifier)
                videos.append(item)
        if page_index == 0 and progress is not None and videos:
            # Fast path: a 5,000-item playlist may require many API pages.
            # Save the latest 50 likes immediately; the complete merge later
            # remains ordered and deduplicated.
            partial = merge(videos)
            first_page_added = partial["added"]
            try:
                progress(partial)
            except Exception:
                pass  # Background sync must survive a closed GUI callback.
        next_token = page.get("next_page_token") or ""
        if not isinstance(next_token, str) or len(next_token) > 150:
            raise VideoRatingError("YouTube vrátil neplatné stránkovanie obľúbených.")
        if not next_token:
            break
        if not using_playlist and page_index + 1 >= RECENT_API_PAGES:
            truncated = True
            break
        if next_token in tokens:
            raise VideoRatingError("YouTube zopakoval stránku obľúbených.")
        tokens.add(next_token)
        next_page = next_token
    else:
        truncated = bool(next_page)
    # A closed screen cannot create a delayed local import. The merge itself
    # remains an atomic operation protected by the local-library lock.
    if cancelled is not None and cancelled.is_set():
        return {"cancelled": True, "added": 0}
    merged = merge(videos)
    return {"added": merged["added"] + first_page_added,
            "total": merged["total"],
            "capacity_reached": merged["capacity_reached"],
            "truncated": truncated,
            "checked": len(videos),
            "source": "likes_playlist" if using_playlist else "recent_api"}
