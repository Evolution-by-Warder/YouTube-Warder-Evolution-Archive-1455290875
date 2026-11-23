# YouTube Warder Evolution – aktuálny aktualizačný kanál

**Overené 23.11.2026:** aktuálne ostré vydanie `youtube-warder-v1.0.2`. `update/stable.json` ponúka `1.0.2`, oficiálny nemenný IPK na GitHub Releases, jeho presný SHA-256 a dĺžku. Staršie v1.0.1 a v1.0.0 sú záchranné/rollback verzie. `update/testing.json` má `release: null` a zatiaľ nesmie ponúkať neoverený TEST balík.

## Publikovanie budúcej verzie

1. Vytvoriť novú verziu až po schválení rozsahu, povinných CI a overení ochrany používateľských dát.
2. Vytvoriť nemenný GitHub Release `youtube-warder-vX.Y.Z` s názvom `enigma2-plugin-extensions-youtube-warder-evolution_X.Y.Z_all.ipk`.
3. Skontrolovať byte size, SHA-256, internú opkg identitu a schopnosť aktualizácie aj zo starších podporovaných balíkov.
4. Až potom publikovať `update/stable.json` s `schema: 1`, `product: "YouTube Warder Evolution"`, `channel: "stable"` a `release: {version,tag,url,sha256,bytes,notes}`.
5. Na GitHub Releases uchovávať **aktuálnu a najviac tri predošlé ostré verzie**; pred mazaniami preveriť aktívne URL a obnovu. Nepridávať inštalačné IPK do `main`.

Nainštalované staršie klienty používajú tú istú bezpečnú GitHub `main/update/stable.json` adresu. Updater verifikuje verziu, balík, checksum a veľkosť pred opkg.

Pozri [retention policy](../docs/RELEASE_RETENTION_POLICY.md) a jediný [spoločný checkpoint Warder Evolution](https://github.com/Evolution-by-Warder/FullHDGlass-Warder-Evolution/blob/main/docs/ECOSYSTEM-CLEANUP-CHECKPOINT-20261123.md).
