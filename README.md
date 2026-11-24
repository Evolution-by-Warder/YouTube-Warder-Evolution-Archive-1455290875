# YouTube – Warder Evolution

## Stable release: 1.0.3 (24 November 2026)

YouTube – Warder Evolution is a native Enigma2 YouTube plugin for OpenATV and OpenPLi.

### Features
- Native Full HD remote-control UI: Home, categories, search and subscriptions.
- YouTube TV-code sign-in, real account subscriptions and YouTube likes.
- One-way automatic import of the account's liked videos into receiver-local favourites on each plugin launch; favourites and viewing history remain on the receiver.
- MENU action to Like a selected video on YouTube and save it immediately as a local favourite.
- GStreamer playback fallback and ExtePlayer3 integration.
- Quick category selection, including compatibility fixes for different Enigma2 MenuList APIs.
- Automated IPK installation checks for ServiceApp, ExtePlayer3, Python modules and yt-dlp.
- Telnet installation/upgrade/reinstall/uninstall messages with Warder-style separators, clear status and GUI restart instruction.
- Classic native Settings list with selectable account, player, video quality and optional Enigma2 main-menu shortcut (default disabled).

### Compatibility testing
- OpenATV 7.6: functional testing performed.
- OpenPLi 9.2: functional testing performed.
- OpenPLi Scarthgap (GigaBlue Quad 4K Pro): RC4 user-confirmed functional; RC6 upgrade completed without package-manager error.
- TV-code account sign-in and basic YouTube account use have been verified on a receiver in the 1.0.2 test series.
- Version 1.0.3 builds on that working test, with automatic favourites sync and verified source/packaging tests; final receiver checks of the 1.0.3 build are separate from CI.

### Installer notes
`opkg` installs the ServiceApp and ExtePlayer3 package dependencies.
After `opkg` exits, the dependency helper verifies Python modules and yt-dlp. On applicable OpenPLi images it can install `python3-profile`, `python3-pip`, and `python3-certifi` as necessary, then install a compatible yt-dlp version.
Logs: `/tmp/warder-youtube-deps.log`. An Internet connection and working feeds are required for missing dependencies.

### Release package
`enigma2-plugin-extensions-youtube-warder-evolution_1.0.3_all.ipk`

SHA-256: see the verified `update/stable.json` manifest for the current release.

Release notes: [RELEASE_NOTES_1.0.3.md](RELEASE_NOTES_1.0.3.md).

Release register: [RELEASE_REGISTER.md](RELEASE_REGISTER.md).

**Build and verification:** GitHub Actions builds the stable IPK from the matching `main` source and packages it with its versioned release notes. The `update/stable.json` manifest supplies the published asset size and SHA-256 digest.

### Background
The UI uses a lightweight blue style, native Enigma2 controls, and a 1920×1080 layout. Third-party component licenses and attributions must be preserved.
