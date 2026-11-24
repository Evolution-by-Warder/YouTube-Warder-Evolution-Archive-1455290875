# -*- coding: utf-8 -*-
"""Read-only YouTube TV OAuth device flow. No credentials shipped in the IPK.

Network calls run in Enigma2 worker threads. A device flow is deliberately
polled ONE request at a time by the UI timer, honoring the server interval.
Token files are private and never contain an account password.
"""
import json
import os
import re
import stat
import tempfile
import threading
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

CLIENT_PATH = Path("/etc/enigma2/warderyoutube-taapat-test-client.json")
# Keep test consent isolated: existing Warder tokens are never overwritten.
TOKEN_PATH = Path("/etc/enigma2/warderyoutube-taapat-test-token.json")
DEVICE_URL = "https://oauth2.googleapis.com/device/code"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"
SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
TAAPAT_SCOPE = "https://www.googleapis.com/auth/youtube"
LEGACY_DEVICE_URL = "https://accounts.google.com/o/oauth2/device/code"
LEGACY_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
LEGACY_DEVICE_GRANT = "http://oauth.net/grant_type/device/1.0"
CURRENT_DEVICE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"
CLIENT_ID = re.compile(r"^[0-9A-Za-z._-]{8,200}\.apps\.googleusercontent\.com$")
MAX_JSON = 64 * 1024
_LOCK = threading.RLock()  # token refresh/save/logout must not race


class SubscriptionsAuthError(Exception):
    """Only user-safe messages, never raw OAuth responses or token URLs."""


class ReauthorizationRequired(SubscriptionsAuthError):
    """Google explicitly invalidated the authorization; not a network outage."""


def _read_private_json(path):
    try:
        path = Path(path)
        st = path.lstat()
        if not stat.S_ISREG(st.st_mode) or st.st_mode & 0o077:
            raise SubscriptionsAuthError("OAuth file must be regular and mode 0600.")
        if st.st_size <= 0 or st.st_size > MAX_JSON:
            raise SubscriptionsAuthError("OAuth file is too large or empty.")
        with path.open("rb") as f:
            raw = f.read(MAX_JSON + 1)
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("OAuth JSON is not an object")
        return data
    except (OSError, ValueError, UnicodeError):
        raise SubscriptionsAuthError("OAuth account configuration is unavailable.")


def read_client(path=CLIENT_PATH):
    """Resolve developer's installed TV OAuth identity; never a user's key.

    A private receiver-local configuration can override the distributable TV
    client. An existing but invalid file must fail closed, not silently fall
    back to a different project (which could break stored refresh tokens).
    """
    target = Path(path)
    if target.exists() or target.is_symlink():
        info = _read_private_json(target)
    else:
        # Only the test branch uses this login profile; production identity
        # and its existing stored tokens remain untouched.
        from .taapat_oauth_compat import compatibility_client
        info = compatibility_client()
    client_id = info.get("client_id")
    secret = info.get("client_secret")
    if not isinstance(client_id, str) or not CLIENT_ID.fullmatch(client_id):
        raise SubscriptionsAuthError("YouTube TV sign-in is not configured by the plugin developer.")
    if not isinstance(secret, str) or len(secret) > 256 or not secret:
        raise SubscriptionsAuthError("Configure the matching Google OAuth TV client secret.")
    result = {"client_id": client_id, "client_secret": secret}
    if not (target.exists() or target.is_symlink()):
        # Known compatibility endpoints; never accept arbitrary token hosts
        # from an external configuration file.
        result.update({"scope": TAAPAT_SCOPE,
                       "device_url": LEGACY_DEVICE_URL,
                       "token_url": LEGACY_TOKEN_URL,
                       "device_grant": LEGACY_DEVICE_GRANT})
    return result


def _post(url, params, opener=urlopen):
    request = Request(url, data=urlencode(params).encode("ascii"), headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "User-Agent": "WarderYouTube/0.0.8",
    })
    try:
        response = opener(request, timeout=8)
    except HTTPError as exc:
        response = exc  # Device polling returns expected errors as HTTP 428/403.
    except (URLError, OSError, TimeoutError):
        raise SubscriptionsAuthError("Google authorization service is unavailable.")
    try:
        raw = response.read(MAX_JSON + 1)
    except (OSError, ValueError):
        raise SubscriptionsAuthError("Could not read the Google authorization response.")
    finally:
        response.close()
    if len(raw) > MAX_JSON:
        raise SubscriptionsAuthError("Google authorization response is too large.")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError):
        raise SubscriptionsAuthError("Invalid Google authorization response.")
    if not isinstance(data, dict):
        raise SubscriptionsAuthError("Invalid Google authorization response.")
    return data


def request_device_code(client, opener=urlopen):
    scope = client.get("scope", SCOPE)
    if scope not in (SCOPE, TAAPAT_SCOPE):
        raise SubscriptionsAuthError("Invalid YouTube permission request.")
    url = client.get("device_url", DEVICE_URL)
    if url not in (DEVICE_URL, LEGACY_DEVICE_URL):
        raise SubscriptionsAuthError("Invalid YouTube authorization endpoint.")
    response = _post(url, {
        "client_id": client["client_id"], "scope": scope,
    }, opener)
    try:
        device_code = response["device_code"]
        user_code = response["user_code"]
        url = response.get("verification_url") or response["verification_uri"]
        expires = int(response["expires_in"])
        interval = int(response.get("interval", 5))
        if (not isinstance(device_code, str) or not 10 <= len(device_code) <= 1000
                or not isinstance(user_code, str) or not 2 <= len(user_code) <= 64
                or not isinstance(url, str) or not url.startswith("https://")
                or urlsplit(url).hostname not in ("google.com", "www.google.com", "accounts.google.com")
                or not 30 <= expires <= 3600):
            raise ValueError("bad device response")
    except (KeyError, ValueError, TypeError):
        raise SubscriptionsAuthError("Google did not provide a valid TV login code.")
    return {"device_code": device_code, "user_code": user_code,
            "verification_url": url, "expires_in": expires,
            "interval": max(5, min(60, interval))}


def poll_device_code(client, device_code, opener=urlopen):
    url = client.get("token_url", TOKEN_URL)
    grant = client.get("device_grant", CURRENT_DEVICE_GRANT)
    if url not in (TOKEN_URL, LEGACY_TOKEN_URL) or grant not in (
            CURRENT_DEVICE_GRANT, LEGACY_DEVICE_GRANT):
        raise SubscriptionsAuthError("Invalid YouTube token endpoint.")
    response = _post(url, {
        "client_id": client["client_id"], "client_secret": client["client_secret"],
        "device_code": device_code,
        "grant_type": grant,
    }, opener)
    error = response.get("error")
    if error in ("authorization_pending", "slow_down"):
        return error, None
    if error == "access_denied":
        raise SubscriptionsAuthError("YouTube account access was denied.")
    if error == "expired_token":
        raise SubscriptionsAuthError("The YouTube login code has expired.")
    if error:
        raise SubscriptionsAuthError("YouTube authorization failed.")
    return "connected", _normalize_tokens(
        response, required_scope=client.get("scope", SCOPE))


def _normalize_tokens(response, old_refresh=None, required_scope=SCOPE):
    token = response.get("access_token")
    refresh = response.get("refresh_token") or old_refresh
    scope = response.get("scope", required_scope)
    if required_scope not in (SCOPE, TAAPAT_SCOPE):
        raise SubscriptionsAuthError("Invalid YouTube permission request.")
    if (not isinstance(token, str) or not token or len(token) > 8192
            or not isinstance(refresh, str) or not refresh or len(refresh) > 8192
            or not isinstance(scope, str) or required_scope not in scope.split()):
        raise SubscriptionsAuthError("Read-only YouTube permission was not granted.")
    try:
        lifespan = int(response["expires_in"])
    except (TypeError, ValueError, KeyError):
        lifespan = 3600
    if lifespan < 1:
        raise SubscriptionsAuthError("Google token lifetime is invalid.")
    return {"access_token": token, "refresh_token": refresh,
            "expires_at": int(time.time()) + min(lifespan, 86400)}


def save_tokens(tokens, path=TOKEN_PATH):
    """Atomically persist only owner-granted tokens behind the shared lock."""
    with _LOCK:
        return _save_tokens_locked(tokens, path)


def save_tokens_if_active(tokens, cancelled, path=TOKEN_PATH):
    """Ignore a queued login save after its screen was closed/cancelled."""
    with _LOCK:
        if cancelled.is_set():
            return False
        return _save_tokens_locked(tokens, path, cancelled=cancelled)


def _save_tokens_locked(tokens, path, cancelled=None):
    # Never store credentials in opkg, Enigma config, debug logs or /tmp.
    target = Path(path)
    payload = json.dumps(tokens, separators=(",", ":")).encode("utf-8")
    if len(payload) > MAX_JSON:
        raise SubscriptionsAuthError("YouTube tokens could not be saved.")
    temporary = None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".warderyoutube-oauth-", dir=str(target.parent))
        with os.fdopen(fd, "wb") as f:
            os.fchmod(f.fileno(), 0o600)
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        if cancelled is not None and cancelled.is_set():
            return False
        os.replace(temporary, str(target))
        os.chmod(str(target), 0o600)
        return True
    except OSError:
        raise SubscriptionsAuthError("Could not save private YouTube account tokens.")
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def account_connected(path=TOKEN_PATH):
    try:
        data = _read_private_json(path)
    except SubscriptionsAuthError:
        return False
    return isinstance(data.get("refresh_token"), str) and bool(data["refresh_token"])


def clear_tokens(path=TOKEN_PATH):
    try:
        Path(path).unlink()
    except FileNotFoundError:
        return
    except OSError:
        raise SubscriptionsAuthError("Could not disconnect the YouTube account.")


def disconnect_account(path=TOKEN_PATH, opener=urlopen):
    """Revoke Google access if possible and always discard local tokens.

    Serialize against token refresh and storage: a concurrent old refresh
    must NEVER resurrect the account after the user confirms sign-out.
    Run solely in a worker, not on the Enigma2 GUI thread.
    """
    with _LOCK:
        return _disconnect_locked(path, opener)


def _disconnect_locked(path, opener):
    try:
        data = _read_private_json(path)
    except SubscriptionsAuthError:
        clear_tokens(path=path)
        return False
    refresh = data.get("refresh_token")
    revoked = False
    try:
        if isinstance(refresh, str) and 0 < len(refresh) <= 8192:
            request = Request(REVOKE_URL,
                              data=urlencode({"token": refresh}).encode("ascii"),
                              headers={"Content-Type": "application/x-www-form-urlencoded",
                                       "User-Agent": "WarderYouTube/0.0.8"})
            try:
                response = opener(request, timeout=8)
                try:
                    revoked = bool(getattr(response, "status", None) == 200
                                   or response.getcode() == 200)
                finally:
                    response.close()
            except (HTTPError, URLError, OSError, TimeoutError):
                revoked = False
    finally:
        clear_tokens(path=path)
    return revoked


def access_token(client=None, path=TOKEN_PATH, opener=urlopen):
    """Refresh on demand. Never return an expired token to a Google API call."""
    with _LOCK:
        data = _read_private_json(path)
        try:
            expiry = int(data.get("expires_at") or 0)
        except (ValueError, TypeError):
            expiry = 0
        if (isinstance(data.get("access_token"), str)
                and data["access_token"] and
                expiry > int(time.time()) + 90):
            return data["access_token"]
        refresh = data.get("refresh_token")
        if not isinstance(refresh, str) or not refresh:
            raise SubscriptionsAuthError("Connect your YouTube account first.")
        credentials = client or read_client()
        url = credentials.get("token_url", TOKEN_URL)
        if url not in (TOKEN_URL, LEGACY_TOKEN_URL):
            raise SubscriptionsAuthError("Invalid YouTube token endpoint.")
        response = _post(url, {
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "refresh_token": refresh, "grant_type": "refresh_token",
        }, opener)
        if response.get("error") == "invalid_grant":
            raise ReauthorizationRequired("YouTube authorization expired. Connect the account again.")
        if response.get("error"):
            raise SubscriptionsAuthError("Google authorization service is unavailable.")
        updated = _normalize_tokens(
            response, old_refresh=refresh,
            required_scope=credentials.get("scope", SCOPE))
        save_tokens(updated, path=path)
        return updated["access_token"]
