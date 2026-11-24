"""Local media library: atomic storage, bounds, deduplication and privacy."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "plugin/Plugins/Extensions/WarderYouTube/local_library.py")
spec = importlib.util.spec_from_file_location("warder_local_library_test", SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def video(n, **kw):
    result = {
        "video_id": ("%011d" % n),
        "title": "Adele video %d" % n,
        "channel": "Music",
        "thumbnail_url": "https://attacker.invalid/private?token=SECRET",
        "signed_url": "https://rr1.googlevideo.com/?sig=SECRET",
        "api_key": "SECRET"
    }
    result.update(kw)
    return result


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "library.json"

    def test_favourites_toggle_survives_reload_and_is_private(self):
        self.assertEqual(m.list_videos("favourites", self.path), [])
        self.assertTrue(m.toggle_favourite(video(1), self.path))
        self.assertEqual(len(m.list_videos("favourites", self.path)), 1)
        saved = self.path.read_text("utf-8")
        self.assertNotIn("SECRET", saved)
        self.assertNotIn("attacker", saved)
        self.assertIn("mqdefault.jpg", saved)
        self.assertFalse(m.toggle_favourite(video(1), self.path))
        self.assertEqual(m.list_videos("favourites", self.path), [])

    def test_history_reopens_video_moves_to_front(self):
        for n in (1, 2, 3, 1):
            m.record_opened(video(n), self.path)
        self.assertEqual([x["video_id"] for x in m.list_videos("history", self.path)],
                         ["00000000001", "00000000003", "00000000002"])
        self.assertEqual(m.list_videos("favourites", self.path), [])

    def test_history_limit_and_favourites_limit(self):
        for n in range(105):
            m.record_opened(video(n), self.path)
        self.assertEqual(len(m.list_videos("history", self.path)), 100)
        self.assertEqual(m.list_videos("history", self.path)[0]["video_id"], "00000000104")
        self.assertEqual(m.list_videos("history", self.path)[-1]["video_id"], "00000000005")
        for n in range(205):
            m.toggle_favourite(video(n), self.path)
        self.assertEqual(len(m.list_videos("favourites", self.path)), 205)

    def test_merge_liked_videos_preserves_local_favourites_and_history(self):
        m.toggle_favourite(video(1, title="Local edited title"), self.path)
        m.record_opened(video(3), self.path)
        incoming = [video(2), video(1, title="Remote title"), video(2),
                    video(4, video_id="not-a-video-id"), video(5)]
        result = m.merge_youtube_favourites(incoming, self.path)
        self.assertEqual(result["added"], 2)
        saved = m.list_videos("favourites", self.path)
        self.assertEqual([v["video_id"] for v in saved],
                         [video(1)["video_id"], video(2)["video_id"], video(5)["video_id"]])
        self.assertEqual(saved[0]["title"], "Local edited title")
        self.assertEqual(len(m.list_videos("history", self.path)), 1)
        self.assertNotIn("SECRET", self.path.read_text("utf-8"))
        self.assertEqual(m.merge_youtube_favourites(incoming, self.path)["added"], 0)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_merge_capacity_never_evicts_local_items(self):
        m.toggle_favourite(video(1), self.path)
        incoming = [video(i) for i in range(2, m.LIMITS["favourites"] + 7)]
        merged = m.merge_youtube_favourites(incoming, self.path)
        self.assertEqual(merged["total"], m.LIMITS["favourites"])
        self.assertTrue(merged["capacity_reached"])
        saved = m.list_videos("favourites", self.path)
        self.assertEqual(saved[0]["video_id"], video(1)["video_id"])
        self.assertIn(video(2)["video_id"], {v["video_id"] for v in saved})
        self.assertNotIn(video(m.LIMITS["favourites"]+6)["video_id"],
                         {v["video_id"] for v in saved})
        self.assertEqual(m.merge_youtube_favourites(incoming, self.path)["added"], 0)

    def test_corrupt_library_is_not_overwritten_by_youtube_merge(self):
        self.path.write_text("{BROKEN", encoding="utf-8")
        with self.assertRaises(m.LibraryError):
            m.merge_youtube_favourites([video(1)], self.path)
        self.assertEqual(self.path.read_text("utf-8"), "{BROKEN")

    def test_remove_and_clear_affect_only_selected_list(self):
        m.record_opened(video(1), self.path)
        m.toggle_favourite(video(1), self.path)
        self.assertTrue(m.remove_video("history", video(1)["video_id"], self.path))
        self.assertFalse(m.remove_video("history", video(1)["video_id"], self.path))
        self.assertEqual(len(m.list_videos("favourites", self.path)), 1)
        m.clear_videos("favourites", self.path)
        self.assertEqual(m.list_videos("favourites", self.path), [])
        self.assertEqual(m.list_videos("history", self.path), [])

    def test_bad_id_never_reaches_file(self):
        with self.assertRaises(m.LibraryError):
            m.record_opened(video(1, video_id="invalid"), self.path)
        with self.assertRaises(m.LibraryError):
            m.toggle_favourite(video(1, video_id="https://attacker/"), self.path)
        self.assertFalse(self.path.exists())

    def test_corrupted_json_not_overwritten(self):
        self.path.write_text("{BROKEN", encoding="utf-8")
        with self.assertRaises(m.LibraryError):
            m.toggle_favourite(video(1), self.path)
        self.assertEqual(self.path.read_text("utf-8"), "{BROKEN")

    def test_unexpected_schema_and_duplicate_ids_are_rejected(self):
        for data in (
            {"schema": 2, "favourites": [], "history": []},
            {"schema": 1, "favourites": [video(1), video(1)], "history": []},
        ):
            self.path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(m.LibraryError):
                m.list_videos("favourites", self.path)

    def test_file_restricted_permissions_and_atomic_no_temporary_leftovers(self):
        import os
        m.record_opened(video(1), self.path)
        mode = self.path.stat().st_mode & 0o777
        self.assertEqual(mode, 0o600)
        self.assertEqual(list(self.path.parent.glob(".warder-youtube-*.tmp")), [])

    def test_normalization_trims_bad_text_and_unsafe_url(self):
        m.toggle_favourite(video(1, title=" X " * 100, channel="A" * 200), self.path)
        saved = m.list_videos("favourites", self.path)[0]
        self.assertLessEqual(len(saved["title"]), 200)
        self.assertEqual(len(saved["channel"]), 120)
        self.assertEqual(saved["thumbnail_url"],
                         "https://i.ytimg.com/vi/00000000001/mqdefault.jpg")


if __name__ == "__main__":
    unittest.main()
