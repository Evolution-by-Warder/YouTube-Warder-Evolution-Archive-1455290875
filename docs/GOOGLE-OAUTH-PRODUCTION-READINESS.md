# Google OAuth production readiness — YouTube Warder Evolution

Prepared 18 November 2026. This is a readiness guide, **not** a claim of Google's approval.

## Project identity
- Enigma2 plugin: **YouTube Warder Evolution** (stable source: `1.0.2`).
- Google authentication: OAuth 2.0 TV / limited-input device flow; existing client must be retained.
- Requested scope: `https://www.googleapis.com/auth/youtube.readonly` only.
- Purpose: read subscriptions and related account metadata for the signed-in user, never modify a Google/YouTube account.
- Optional: public browsing/player and locally saved favourites/history do not require Google account sign-in.
- Official web: `https://warder-evolution.eu/` — homepage reached successfully via HTTPS in the owner's browser on 23 November 2026. Intended YouTube-specific page: `https://warder-evolution.eu/youtube.html` (verify that subpage separately before submitting it to Google).
- Privacy: `https://warder-evolution.eu/privacy.html`.
- Terms: `https://warder-evolution.eu/terms.html`.
- Authorized domain: `warder-evolution.eu`.
- Contact/support: https://github.com/Evolution-by-Warder/YouTube-Warder-Evolution/issues

## Steps that depend on the external provider
1. DNS and HTTPS for `https://warder-evolution.eu/` were confirmed working by the owner on 23 November 2026 (direct browser screenshot of the loaded homepage). Historical DNS SERVFAIL/REFUSED is **resolved** for this tested path and must not be repeated as a current project blocker. Verify individual OAuth-facing `/youtube.html`, `/privacy.html` and `/terms.html` URLs independently before any Google verification submission; this homepage test alone does not certify those pages or Google's separate approval.
2. In Google Search Console, verify the DNS **domain property** `warder-evolution.eu` with the Google-provided TXT record. Never invent the record or delete existing GitHub Pages A/CNAME entries.
3. In Google Cloud Console / Google Auth Platform / Branding, enter the exact homepage, privacy and terms URLs above and authorized domain. Preserve the **same** original OAuth client ID; no credential rotation without planning a migration.
4. In Data Access, check that no broader scopes were added. Only `youtube.readonly` is needed by current code.
5. In Audience, confirm External / In production after Google prerequisites, then complete any Branding and Data Access verification in Verification Center. Publishing alone does not guarantee sensitive-scope approval.
6. Provide a short video demonstration when Google requests it: launch Enigma2 plugin, use public browsing without login, open TV-device login, authorize with **test account only**, display real subscriptions, disconnect account. Obscure account emails, device codes, tokens and private information.
7. Confirm user-facing Google account login end to end on a receiver after Google approves. Never publish Google user tokens.

## Technical scope justification (for verification form)
`youtube.readonly` is required to display the user's personal YouTube subscriptions and associated channel/video metadata inside the native Enigma2 TV interface. The request is initiated only when the user chooses to connect their Google account with the official Google TV-device OAuth flow. The plugin does not write to YouTube accounts and the read-only scope is the narrowest authorization that supports personal subscriptions. OAuth access and refresh tokens remain on the user's own receiver; the project does not operate a remote account-token collection service.

## Google references
- https://support.google.com/cloud/answer/15549049
- https://support.google.com/cloud/answer/13464321
- https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification
- https://developers.google.com/youtube/data/guides/authentication

Do **not** build/release a new IPK solely for the website or OAuth consent configuration.
