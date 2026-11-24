# -*- coding: utf-8 -*-
"""Rate a video in the signed-in user's actual YouTube account.

Only a deliberate video MENU action calls like_video. The account is checked
locally for menu visibility; token refresh and HTTP run in a worker thread.
Never put OAuth tokens in URLs, logs, or the Enigma2 settings.
"""
import re
import html
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
YOUTUBE_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
ENDPOINT = "https://www.googleapis.com/youtube/v3/videos/rate"
LIST_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"
CHANNELS_ENDPOINT = "https://www.googleapis.com/youtube/v3/channels"
PLAYLIST_ITEMS_ENDPOINT = "https://www.googleapis.com/youtube/v3/playlistItems"
PLAYLIST_ID = re.compile(r"^[A-Za-z0-9_-]{10,128}$")
MAX_RESPONSE_BYTES = 1024 * 1024



class VideoRatingError(Exception):
    """Only fixed error messages safe to display on a receiver."""


def can_like():
    """No network I/O: whether this receiver has a full YouTube login."""
    try:
        from .subscriptions_auth import account_connected, read_client
        return (account_connected()
                and read_client().get("scope") == YOUTUBE_WRITE_SCOPE)
    except Exception:
        # An incomplete or older read-only sign-in must not expose a write
        # action that cannot possibly succeed.
        return False


def like_video(video_id, opener=urlopen, timeout=8):
    """Set the signed-in user's YouTube rating to 'like' (no local favourite).

    Call from deferToThread, only after the user explicitly chose MENU/Like.
    The authorized Google endpoint should return HTTP 204 No Content.
    """
    if not isinstance(video_id, str) or not VIDEO_ID.fullmatch(video_id):
        raise VideoRatingError("Neplatné video na hodnotenie.")
    from .subscriptions_auth import (
        account_connected, read_client, access_token,
        SubscriptionsAuthError, ReauthorizationRequired
    )
    if not account_connected():
        raise VideoRatingError("Najprv sa prihlás do účtu YouTube.")
    try:
        if read_client().get("scope") != YOUTUBE_WRITE_SCOPE:
            raise VideoRatingError("Prihlásenie nepovoľuje hodnotenie videí.")
        token = access_token()
    except ReauthorizationRequired:
        raise VideoRatingError("Prihlásenie vypršalo. Pripoj účet YouTube znova.") from None
    except SubscriptionsAuthError:
        raise VideoRatingError("Nepodarilo sa overiť prihlásenie do YouTube.") from None
    if (not isinstance(token, str) or not token or len(token) > 8192
            or not token.isascii() or any(ord(c) < 33 or ord(c) == 127 for c in token)):
        raise VideoRatingError("Prihlásenie do YouTube je neplatné.")

    url = ENDPOINT + "?" + urlencode({"id": video_id, "rating": "like"})
    request = Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
        "User-Agent": "WarderYouTube/1.0",
    }, method="POST")
    try:
        from .data_auth import open_authorized
        response = open_authorized(request, opener, timeout)
        try:
            status = response.getcode()
        finally:
            response.close()
    except HTTPError as error:
        if error.code == 401:
            raise VideoRatingError("Prihlásenie vypršalo. Pripoj účet YouTube znova.") from None
        if error.code == 403:
            raise VideoRatingError("YouTube odmietol hodnotenie alebo vyčerpal limit.") from None
        raise VideoRatingError("YouTube neprijal hodnotenie videa.") from None
    except (URLError, OSError, TimeoutError):
        raise VideoRatingError("Nepodarilo sa spojiť s YouTube.") from None
    if status != 204:
        raise VideoRatingError("YouTube nepotvrdil hodnotenie videa.")
    return True


def parse_liked_videos(payload):
    """Parse only genuine videos from a user-authorized myRating=like reply."""
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise VideoRatingError("YouTube vrátil neplatný zoznam obľúbených.")
    items, seen = [], set()
    for entry in payload["items"][:50]:
        if not isinstance(entry, dict):
            continue
        vid = entry.get("id")
        snippet = entry.get("snippet")
        if (not isinstance(vid, str) or not VIDEO_ID.fullmatch(vid)
                or vid in seen or not isinstance(snippet, dict)):
            continue
        seen.add(vid)
        items.append({
            "video_id": vid,
            "title": html.unescape(str(snippet.get("title") or "YouTube video"))[:200],
            "channel": html.unescape(str(snippet.get("channelTitle") or ""))[:120],
            "published_at": str(snippet.get("publishedAt") or "")[:30],
            "thumbnail_url": "https://i.ytimg.com/vi/%s/mqdefault.jpg" % vid,
        })
    nxt = payload.get("nextPageToken") or ""
    if not isinstance(nxt, str) or len(nxt) > 150:
        nxt = ""
    return {"items": items, "next_page_token": nxt}


def liked_videos_page(page_token="", opener=urlopen, timeout=8):
    """Fetch one page of the signed-in user's actual YouTube likes.

    Local Warder favourites are untouched. All I/O must stay off the GUI
    thread. Do not silently report an empty list after 401/403.
    """
    if (not isinstance(page_token, str) or len(page_token) > 150
            or any(c in page_token for c in "\r\n\x00")):
        raise VideoRatingError("Neplatná stránka YouTube obľúbených.")
    from .subscriptions_auth import (
        account_connected, read_client, access_token,
        SubscriptionsAuthError, ReauthorizationRequired
    )
    if not account_connected():
        raise VideoRatingError("Najprv sa prihlás do účtu YouTube.")
    try:
        credentials = read_client()
        if credentials.get("scope") != YOUTUBE_WRITE_SCOPE:
            raise VideoRatingError("Toto prihlásenie nepovoľuje osobné hodnotenia.")
        token = access_token()
    except ReauthorizationRequired:
        raise VideoRatingError("Prihlásenie vypršalo. Pripoj účet YouTube znova.") from None
    except SubscriptionsAuthError:
        raise VideoRatingError("Nepodarilo sa overiť prihlásenie do YouTube.") from None
    if (not isinstance(token, str) or not token or len(token) > 8192
            or not token.isascii() or any(ord(c) < 33 or ord(c) == 127 for c in token)):
        raise VideoRatingError("Prihlásenie do YouTube je neplatné.")

    params = {"part": "snippet", "myRating": "like", "maxResults": 50}
    if page_token:
        params["pageToken"] = page_token
    request = Request(LIST_ENDPOINT + "?" + urlencode(params), headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
        "User-Agent": "WarderYouTube/1.0",
    })
    try:
        from .data_auth import open_authorized
        response = open_authorized(request, opener, timeout)
        try:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        finally:
            response.close()
    except HTTPError as error:
        if error.code == 401:
            raise VideoRatingError("Prihlásenie vypršalo. Pripoj účet YouTube znova.") from None
        if error.code == 403:
            raise VideoRatingError("YouTube nepovolil čítanie videí Páči sa mi.") from None
        raise VideoRatingError("YouTube obľúbené videá sú dočasne nedostupné.") from None
    except (URLError, OSError, TimeoutError):
        raise VideoRatingError("Nepodarilo sa spojiť s YouTube.") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise VideoRatingError("Zoznam obľúbených videí je príliš veľký.")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError):
        raise VideoRatingError("YouTube vrátil neplatnú odpoveď.") from None
    return parse_liked_videos(payload)


def like_and_save(video, rate=like_video, store=None):
    """A real YouTube Like immediately becomes a local favourite, once.

    The remote rating MUST succeed before local storage is touched. A
    failed receiver write does not pretend the YouTube operation failed.
    Run the entire operation in a worker, never on the Enigma2 GUI thread.
    """
    if not isinstance(video, dict):
        raise VideoRatingError("Neplatné video na hodnotenie.")
    identifier = video.get("video_id")
    if not isinstance(identifier, str) or not VIDEO_ID.fullmatch(identifier):
        raise VideoRatingError("Neplatné video na hodnotenie.")
    rate(identifier)
    try:
        if store is None:
            from .local_library import save_confirmed_youtube_like as store
        added = store(video)
    except Exception:
        return {"liked": True, "local_saved": False, "added": False}
    return {"liked": True, "local_saved": True, "added": bool(added)}


def _account_token():
    from .subscriptions_auth import (
        account_connected, read_client, access_token,
        SubscriptionsAuthError, ReauthorizationRequired
    )
    if not account_connected():
        raise VideoRatingError("Najprv sa prihlás do účtu YouTube.")
    try:
        if read_client().get("scope") != YOUTUBE_WRITE_SCOPE:
            raise VideoRatingError("Toto prihlásenie nepovoľuje osobné hodnotenia.")
        token = access_token()
    except ReauthorizationRequired:
        raise VideoRatingError("Prihlásenie vypršalo. Pripoj účet YouTube znova.") from None
    except SubscriptionsAuthError:
        raise VideoRatingError("Nepodarilo sa overiť prihlásenie do YouTube.") from None
    if (not isinstance(token, str) or not token or len(token) > 8192
            or not token.isascii()
            or any(ord(c) < 33 or ord(c) == 127 for c in token)):
        raise VideoRatingError("Prihlásenie do YouTube je neplatné.")
    return token


def _account_json_get(endpoint, params, token, opener=urlopen, timeout=8):
    """Read a fixed official Google API endpoint without forwarding tokens."""
    request = Request(endpoint + "?" + urlencode(params), headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
        "User-Agent": "WarderYouTube/1.0",
    })
    try:
        from .data_auth import open_authorized
        response = open_authorized(request, opener, timeout)
        try:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        finally:
            response.close()
    except HTTPError as error:
        if error.code == 401:
            raise VideoRatingError("Prihlásenie vypršalo. Pripoj účet YouTube znova.") from None
        if error.code == 403:
            raise VideoRatingError("YouTube nepovolil čítanie obľúbených videí.") from None
        raise VideoRatingError("YouTube obľúbené videá sú dočasne nedostupné.") from None
    except (URLError, OSError, TimeoutError):
        raise VideoRatingError("Nepodarilo sa spojiť s YouTube.") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise VideoRatingError("Odpoveď YouTube je príliš veľká.")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError):
        raise VideoRatingError("YouTube vrátil neplatnú odpoveď.") from None
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise VideoRatingError("YouTube vrátil neplatný zoznam obľúbených.")
    return data


def liked_playlist_id(opener=urlopen, timeout=8):
    """Find the authorized user's special Likes playlist via channels.list.

    If the service does not return this special playlist, the caller may
    fall back to videos.list(myRating=like), which is capped at 1,000 videos.
    """
    result = _account_json_get(
        CHANNELS_ENDPOINT, {"part": "contentDetails", "mine": "true"},
        _account_token(), opener=opener, timeout=timeout)
    for channel in result["items"]:
        if not isinstance(channel, dict):
            continue
        details = channel.get("contentDetails") or {}
        related = details.get("relatedPlaylists") if isinstance(details, dict) else {}
        likes = related.get("likes") if isinstance(related, dict) else None
        if isinstance(likes, str) and PLAYLIST_ID.fullmatch(likes):
            return likes
    return ""


def parse_liked_playlist_items(payload):
    """Preserve the remote Likes playlist order (newest likes first)."""
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise VideoRatingError("YouTube vrátil neplatný zoznam obľúbených.")
    result, seen = [], set()
    for entry in payload["items"][:50]:
        if not isinstance(entry, dict):
            continue
        snippet, details = entry.get("snippet"), entry.get("contentDetails")
        if not isinstance(snippet, dict):
            continue
        details = details if isinstance(details, dict) else {}
        resource = snippet.get("resourceId") or {}
        resource = resource if isinstance(resource, dict) else {}
        identifier = details.get("videoId") or resource.get("videoId")
        if (not isinstance(identifier, str)
                or not VIDEO_ID.fullmatch(identifier)
                or identifier in seen
                or snippet.get("title") in ("Private video", "Deleted video")):
            continue
        seen.add(identifier)
        result.append({
            "video_id": identifier,
            "title": html.unescape(str(snippet.get("title") or "YouTube video"))[:200],
            "channel": html.unescape(str(
                snippet.get("videoOwnerChannelTitle") or snippet.get("channelTitle") or ""))[:120],
            "published_at": str(details.get("videoPublishedAt")
                                or snippet.get("publishedAt") or "")[:30],
            "thumbnail_url": "https://i.ytimg.com/vi/%s/mqdefault.jpg" % identifier,
        })
    token = payload.get("nextPageToken") or ""
    if not isinstance(token, str) or len(token) > 150:
        token = ""
    return {"items": result, "next_page_token": token}


def liked_playlist_page(playlist_id, page_token="", opener=urlopen, timeout=8):
    """Read an authenticated page of the system-generated Liked Videos playlist."""
    if not isinstance(playlist_id, str) or not PLAYLIST_ID.fullmatch(playlist_id):
        raise VideoRatingError("Neplatný playlist Páči sa mi.")
    if (not isinstance(page_token, str) or len(page_token) > 150
            or any(c in page_token for c in "\r\n\x00")):
        raise VideoRatingError("Neplatná stránka YouTube obľúbených.")
    params = {"part": "snippet,contentDetails", "playlistId": playlist_id,
              "maxResults": 50}
    if page_token:
        params["pageToken"] = page_token
    payload = _account_json_get(
        PLAYLIST_ITEMS_ENDPOINT, params, _account_token(),
        opener=opener, timeout=timeout)
    return parse_liked_playlist_items(payload)
