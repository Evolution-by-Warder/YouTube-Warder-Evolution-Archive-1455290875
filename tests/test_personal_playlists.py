"""Personal YouTube playlists remain tied to the owner's OAuth account.

No user API key, Google credentials, or network calls are needed for tests.
"""
import ast
import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1] / "plugin/Plugins/Extensions/WarderYouTube"


def load(name):
    spec = importlib.util.spec_from_file_location("_personal_playlist_" + name,
                                                   ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


api = load("subscriptions_api")
rail = load("home_subscription_rail")
USER_PLAYLIST = "PL" + "A" * 22
OTHER_PLAYLIST = "PL" + "B" * 22
CHANNEL = "UC" + "C" * 22


class Reply(io.BytesIO):
    def __init__(self, data):
        super().__init__(json.dumps(data).encode("utf-8"))


class PlaylistTests(unittest.TestCase):
    def test_private_playlists_are_real_account_data_and_page_safely(self):
        requests = []

        def opener(request, timeout):
            requests.append(request)
            params = parse_qs(urlsplit(request.full_url).query)
            self.assertEqual(urlsplit(request.full_url).path,
                             "/youtube/v3/playlists")
            self.assertEqual(params.get("mine"), ["true"])
            self.assertEqual(params.get("part"), ["snippet"])
            self.assertNotIn("key", params)
            self.assertNotIn("access_token", params)
            self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
            if len(requests) == 1:
                return Reply({"items": [
                    {"id": USER_PLAYLIST, "snippet": {"title": "My private playlist"}},
                    {"id": "bad", "snippet": {"title": "Invalid ID"}},
                    {"id": USER_PLAYLIST, "snippet": {"title": "Duplicate"}}
                ], "nextPageToken": "page-two"})
            self.assertEqual(params.get("pageToken"), ["page-two"])
            return Reply({"items": [
                {"id": OTHER_PLAYLIST,
                 "snippet": {"title": "My &amp; family favourites"}}
            ]})

        result = api.user_playlists_list("test-token", opener=opener)
        self.assertEqual(result, [
            {"playlist_id": USER_PLAYLIST, "title": "My private playlist"},
            {"playlist_id": OTHER_PLAYLIST, "title": "My & family favourites"}
        ])
        self.assertEqual(len(requests), 2)

    def test_personal_playlists_are_shown_before_many_followed_channels(self):
        result = rail.subscription_chips(
            [{"channel_id": CHANNEL, "title": "Artist"}],
            connected=True,
            playlists=[
                {"playlist_id": USER_PLAYLIST, "title": "Personal favourites"},
                {"playlist_id": USER_PLAYLIST, "title": "Duplicated"},
                {"playlist_id": "../invalid", "title": "Invalid"}
            ])
        self.assertEqual([chip["kind"] for chip in result],
                         ["recent", "playlist", "channel"])
        self.assertEqual(result[1]["playlist_id"], USER_PLAYLIST)
        self.assertTrue(result[1]["label"].startswith("PL: "))
        self.assertFalse(rail.subscription_chips([], connected=False,
                                                 playlists=[{"playlist_id": USER_PLAYLIST,
                                                             "title": "Private"}]))

    def test_selected_playlist_fetches_actual_items_from_account_in_order(self):
        # Extract the production worker without importing Enigma2 GUI widgets.
        source = ast.parse((ROOT / "ui.py").read_text(encoding="utf-8"))
        selected = next(node for node in source.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == "_load_personal_channel_videos")
        pkg = types.ModuleType("_playlist_worker")
        pkg.__path__ = [str(ROOT)]
        auth = types.ModuleType("_playlist_worker.subscriptions_auth")
        auth.access_token = lambda: "test-personal-access"
        backend = types.ModuleType("_playlist_worker.subscriptions_api")
        called = []

        def fetch(playlist_id, token, limit=12):
            called.append((playlist_id, token, limit))
            return [{"video_id": "abcdefghijk", "title": "First"},
                    {"video_id": "zbcdefghijk", "title": "Second"}]

        backend.playlist_videos = fetch
        backend.uploads_playlists = lambda *args: self.fail("Channel API used")
        backend.SubscriptionsApiError = ValueError
        env = {"__package__": "_playlist_worker"}
        with patch.dict(sys.modules, {
            "_playlist_worker": pkg,
            "_playlist_worker.subscriptions_auth": auth,
            "_playlist_worker.subscriptions_api": backend
        }):
            exec(compile(ast.Module(body=[selected], type_ignores=[]),
                         str(ROOT / "ui.py"), "exec"), env)
            result = env["_load_personal_channel_videos"](
                {"kind": "playlist", "playlist_id": USER_PLAYLIST},
                [{"channel_id": CHANNEL}], batch_index=5)
        self.assertEqual([v["title"] for v in result], ["First", "Second"])
        self.assertEqual(called, [(USER_PLAYLIST, "test-personal-access", 200)])

    def test_api_rejects_unsigned_playlist_data(self):
        with self.assertRaises(api.SubscriptionsApiError):
            api.user_playlists_list("", opener=lambda *args: None)


if __name__ == "__main__":
    unittest.main()
