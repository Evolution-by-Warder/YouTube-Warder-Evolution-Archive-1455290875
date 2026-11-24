# -*- coding: utf-8 -*-
"""One-way refresh of the receiver's favourites from real YouTube account likes.

Runs entirely in a background worker when the owner opens Favourites. Never
uploads local favourites or clears either list; token and credentials remain
confined to the existing account reader.
"""
from .local_library import LIMITS, merge_youtube_favourites
from .video_ratings import liked_videos_page, VideoRatingError

MAX_SYNC_PAGES = 40  # 40 x 50 = 2000 entries max per refresh.


def sync_youtube_favourites(fetch_page=liked_videos_page,
                            merge=merge_youtube_favourites):
    """Fetch a bounded, deduplicated snapshot before one atomic local merge.

    If YouTube fails at any page, do not modify the receiver's favourites.
    A repeating page token is treated as a truncated response, not an infinite
    loop. Existing favourites always take precedence and are never removed.
    """
    videos, identifiers, tokens = [], set(), set()
    next_page = ""
    truncated = False
    for page_index in range(MAX_SYNC_PAGES):
        page = fetch_page(next_page)
        if not isinstance(page, dict) or not isinstance(page.get("items"), list):
            raise VideoRatingError("YouTube vrátil neplatné údaje obľúbených.")
        for item in page["items"]:
            if not isinstance(item, dict):
                continue
            identifier = item.get("video_id")
            if isinstance(identifier, str) and identifier not in identifiers:
                identifiers.add(identifier)
                videos.append(item)
        next_token = page.get("next_page_token") or ""
        if not isinstance(next_token, str) or len(next_token) > 150:
            raise VideoRatingError("YouTube vrátil neplatné stránkovanie obľúbených.")
        if not next_token:
            break
        if next_token in tokens:
            raise VideoRatingError("YouTube zopakoval stránku obľúbených.")
        tokens.add(next_token)
        next_page = next_token
    else:
        truncated = bool(next_page)
    # A full local collection is not altered; the merge routine never evicts.
    merged = merge(videos)
    return {"added": merged["added"],
            "total": merged["total"],
            "capacity_reached": merged["capacity_reached"],
            "truncated": truncated,
            "checked": len(videos)}
