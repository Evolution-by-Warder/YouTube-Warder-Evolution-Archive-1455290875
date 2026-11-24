"""Offline tests of YouTube Likes, account-only requests and one-way merge.

Never touches a real Google account or sends requests over the network.
"""
import importlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1] / "plugin/Plugins/Extensions/WarderYouTube"
PKG = "_yt_likes_sync_test"
pkg = types.ModuleType(PKG)
pkg.__path__ = [str(ROOT)]
sys.modules[PKG] = pkg
ratings = importlib.import_module(PKG + ".video_ratings")
sync = importlib.import_module(PKG + ".favourites_sync")
library = importlib.import_module(PKG + ".local_library")


def video(i, title=None):
    return {"video_id": ("%011d" % i), "title": title or ("Music " + str(i)),
            "channel": "Artist", "published_at": "2026-11-24T19:00:00Z"}


class Response(io.BytesIO):
    def __init__(self, data, status=200):
        super().__init__(json.dumps(data).encode("utf-8"))
        self.status = status
    def getcode(self):
        return self.status


class LikedVideoTests(unittest.TestCase):
    def test_genuine_likes_only_and_valid_pagination(self):
        import urllib.request
        collected = []
        token = "test-token-no-real-data"
        auth = types.ModuleType(PKG + ".subscriptions_auth")
        auth.account_connected = lambda: True
        auth.read_client = lambda: {"scope": ratings.YOUTUBE_WRITE_SCOPE}
        auth.access_token = lambda: token
        auth.SubscriptionsAuthError = type("SubscriptionsAuthError", (Exception,), {})
        auth.ReauthorizationRequired = type("ReauthorizationRequired", (Exception,), {})
        def response(request, timeout):
            collected.append(request)
            return Response({"items": [
                {"id": "abcdefghijk", "snippet": {"title": "Song &amp; title",
                                                  "channelTitle": "Artist"}},
                {"id": "invalid", "snippet": {"title": "Wrong"}},
                {"id": "abcdefghijk", "snippet": {"title": "Repeated"}},
            ], "nextPageToken": "next0-abc"})
        with patch.dict(sys.modules, {PKG + ".subscriptions_auth": auth}):
            data = ratings.liked_videos_page("previous-rn0", opener=response)
        self.assertEqual(data["next_page_token"], "next0-abc")
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["title"], "Song & title")
        query = parse_qs(urlsplit(collected[0].full_url).query)
        self.assertEqual(query["myRating"], ["like"])
        self.assertEqual(query["pageToken"], ["previous-rn0"])
        self.assertNotIn("key", query)
        self.assertNotIn("access_token", query)
        self.assertEqual(collected[0].get_header("Authorization"), "Bearer " + token)

    def test_like_is_real_post_and_not_local_favourite(self):
        auth = types.ModuleType(PKG + ".subscriptions_auth")
        auth.account_connected = lambda: True
        auth.read_client = lambda: {"scope": ratings.YOUTUBE_WRITE_SCOPE}
        auth.access_token = lambda: "fake-auth-token"
        auth.SubscriptionsAuthError = type("SubscriptionsAuthError", (Exception,), {})
        auth.ReauthorizationRequired = type("ReauthorizationRequired", (Exception,), {})
        issued = []
        def opener(request, timeout):
            issued.append(request)
            return Response({}, status=204)
        with patch.dict(sys.modules, {PKG + ".subscriptions_auth": auth}):
            self.assertTrue(ratings.like_video("abcdefghijk", opener=opener))
        req = issued[0]
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(urlsplit(req.full_url).netloc, "www.googleapis.com")
        self.assertEqual(parse_qs(urlsplit(req.full_url).query)["rating"], ["like"])
        self.assertEqual(req.get_header("Authorization"), "Bearer fake-auth-token")

    def test_403_is_error_not_empty_favourites(self):
        auth = types.ModuleType(PKG + ".subscriptions_auth")
        auth.account_connected = lambda: True
        auth.read_client = lambda: {"scope": ratings.YOUTUBE_WRITE_SCOPE}
        auth.access_token = lambda: "test"
        auth.SubscriptionsAuthError = type("SubscriptionsAuthError", (Exception,), {})
        auth.ReauthorizationRequired = type("ReauthorizationRequired", (Exception,), {})
        def forbidden(request, timeout):
            raise HTTPError(request.full_url, 403, "forbidden", {}, None)
        with patch.dict(sys.modules, {PKG + ".subscriptions_auth": auth}):
            with self.assertRaises(ratings.VideoRatingError):
                ratings.liked_videos_page(opener=forbidden)


class OneWaySyncTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "videos.json"

    def test_import_pages_merges_without_removing_local_or_uploading(self):
        library.toggle_favourite(video(1, title="Existing title"), self.path)
        library.record_opened(video(9), self.path)
        calls = []
        def fetch(token):
            calls.append(token)
            if token == "":
                return {"items": [video(1, title="Different title"), video(2)],
                        "next_page_token": "page2"}
            self.assertEqual(token, "page2")
            return {"items": [video(2), video(3)],
                    "next_page_token": ""}
        def merge(rows):
            return library.merge_youtube_favourites(rows, self.path)
        result = sync.sync_youtube_favourites(fetch_page=fetch, merge=merge)
        self.assertEqual(result["added"], 2)
        self.assertEqual(result["checked"], 3)
        self.assertEqual(calls, ["", "page2"])
        got = library.list_videos("favourites", self.path)
        self.assertEqual([x["video_id"] for x in got],
                         [video(i)["video_id"] for i in (1, 2, 3)])
        self.assertEqual(got[0]["title"], "Existing title")
        self.assertEqual(len(library.list_videos("history", self.path)), 1)
        self.assertEqual(sync.sync_youtube_favourites(fetch_page=fetch, merge=merge)["added"], 0)

    def test_failure_on_later_page_never_changes_local_file(self):
        library.toggle_favourite(video(1), self.path)
        original = self.path.read_bytes()
        def fetch(token):
            if not token:
                return {"items": [video(2)], "next_page_token": "second"}
            raise ratings.VideoRatingError("Quota exceeded")
        with self.assertRaises(ratings.VideoRatingError):
            sync.sync_youtube_favourites(
                fetch_page=fetch,
                merge=lambda rows: library.merge_youtube_favourites(rows, self.path))
        self.assertEqual(self.path.read_bytes(), original)

    def test_screen_close_cancels_before_writing_local_favourites(self):
        from threading import Event
        library.toggle_favourite(video(1), self.path)
        original = self.path.read_bytes()
        cancelled = Event()
        called = []
        def fetch(token):
            called.append(token)
            cancelled.set()
            return {"items": [video(2)], "next_page_token": ""}
        out = sync.sync_youtube_favourites(
            fetch_page=fetch, cancelled=cancelled,
            merge=lambda rows: library.merge_youtube_favourites(rows, self.path))
        self.assertTrue(out["cancelled"])
        self.assertEqual(called, [""])
        self.assertEqual(self.path.read_bytes(), original)

    def test_repeat_page_token_never_loops_or_writes(self):
        calls = []
        def fetch(token):
            calls.append(token)
            return {"items": [video(2)], "next_page_token": "loop"}
        with self.assertRaises(ratings.VideoRatingError):
            sync.sync_youtube_favourites(
                fetch_page=fetch,
                merge=lambda rows: self.fail("must not write on repeated token"))
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
