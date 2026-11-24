"""Offline integration checks for the separate Taapat TV-login test profile.

No Google account, user tokens, or external network are contacted.
"""
import importlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import types
import unittest
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[1] / "plugin/Plugins/Extensions/WarderYouTube"
PACKAGE = "_warder_taapat_test"
pkg = types.ModuleType(PACKAGE)
pkg.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = pkg
compat = importlib.import_module(PACKAGE + ".taapat_oauth_compat")
auth = importlib.import_module(PACKAGE + ".subscriptions_auth")


class Response(io.BytesIO):
    def __init__(self, value):
        super().__init__(json.dumps(value).encode("utf-8"))

    def close(self):
        super().close()


class TVCompatibilityTests(unittest.TestCase):
    def test_embedded_profile_is_usable_without_receivers_api_file(self):
        client = auth.read_client()
        self.assertTrue(auth.CLIENT_ID.fullmatch(client["client_id"]))
        self.assertTrue(client["client_secret"])
        self.assertEqual(client["scope"], auth.TAAPAT_SCOPE)
        self.assertEqual(client["device_url"], auth.LEGACY_DEVICE_URL)
        self.assertEqual(client["token_url"], auth.LEGACY_TOKEN_URL)
        self.assertEqual(client["device_grant"], auth.LEGACY_DEVICE_GRANT)
        self.assertNotEqual(auth.TOKEN_PATH.name,
                            "warderyoutube-oauth-token.json")
        self.assertNotEqual(auth.CLIENT_PATH.name,
                            "warderyoutube-oauth-client.json")

    def test_existing_receiver_client_override_still_supports_modern_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oauth.json"
            values = {"client_id": "12345678-abcdefgh.apps.googleusercontent.com",
                      "client_secret": "test-only"}
            path.write_text(json.dumps(values), encoding="utf-8")
            path.chmod(0o600)
            self.assertEqual(auth.read_client(path), values)

    def test_device_code_uses_taapat_scope_and_endpoint(self):
        client = auth.read_client()
        captured = []
        def opener(req, timeout):
            captured.append(req)
            return Response({
                "device_code": "device-code-value",
                "user_code": "ABCD-1234",
                "verification_url": "https://www.google.com/device",
                "expires_in": 1200,
                "interval": 7,
            })
        result = auth.request_device_code(client, opener=opener)
        self.assertEqual(result["user_code"], "ABCD-1234")
        self.assertEqual(captured[0].full_url, auth.LEGACY_DEVICE_URL)
        params = parse_qs(captured[0].data.decode("ascii"))
        self.assertEqual(params["client_id"], [client["client_id"]])
        self.assertEqual(params["scope"], [auth.TAAPAT_SCOPE])
        self.assertNotIn("client_secret", params)

    def test_poll_and_token_refresh_use_compat_client_and_never_urls(self):
        client = auth.read_client()
        captured = []
        def opener(req, timeout):
            captured.append(req)
            params = parse_qs(req.data.decode("ascii"))
            self.assertEqual(req.full_url, auth.LEGACY_TOKEN_URL)
            self.assertEqual(params["client_id"], [client["client_id"]])
            if len(captured) == 1:
                self.assertEqual(params["grant_type"], [auth.LEGACY_DEVICE_GRANT])
                return Response({"access_token": "TEST-user-token",
                                 "refresh_token": "TEST-refresh-token",
                                 "scope": auth.TAAPAT_SCOPE,
                                 "expires_in": 3600})
            self.assertEqual(params["grant_type"], ["refresh_token"])
            self.assertEqual(params["refresh_token"], ["TEST-refresh-token"])
            return Response({"access_token": "TEST-refreshed",
                             "scope": auth.TAAPAT_SCOPE,
                             "expires_in": 3600})
        state, issued = auth.poll_device_code(
            client, "device-code-value", opener=opener)
        self.assertEqual(state, "connected")
        self.assertEqual(issued["refresh_token"], "TEST-refresh-token")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test-tokens.json"
            auth.save_tokens({"access_token": "expired",
                              "refresh_token": issued["refresh_token"],
                              "expires_at": 1}, path)
            result = auth.access_token(client=client, path=path, opener=opener)
            self.assertEqual(result, "TEST-refreshed")
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(len(captured), 2)
        self.assertNotIn("TEST-refresh-token", captured[1].full_url)

    def test_mismatched_scope_is_rejected(self):
        client = auth.read_client()
        with self.assertRaises(auth.SubscriptionsAuthError):
            auth.poll_device_code(
                client, "device",
                opener=lambda req, timeout: Response({
                    "access_token": "fake-access",
                    "refresh_token": "fake-refresh",
                    "scope": "https://www.googleapis.com/auth/drive.readonly",
                    "expires_in": 3600,
                }))


if __name__ == "__main__":
    unittest.main()
