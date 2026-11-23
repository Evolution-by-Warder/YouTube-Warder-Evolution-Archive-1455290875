# YouTube Warder Evolution — retencia vydaní (23.11.2026)

Schválené pravidlo vlastníka: **najnovšie ostré vydanie a najviac tri staršie ostré vydania**. Tieto vydania sa uchovávajú na GitHub Releases, nie ako rastúca zbierka IPK v `main`. Zdrojové súbory, skutočné opkg identity, Google OAuth konfiguráciu, súkromné nastavenia, testy a rozpracované PR neodstraňovať.

V súčasnosti existujú iba tri ostré vydania:

1. `youtube-warder-v1.0.2` — aktuálne
2. `youtube-warder-v1.0.1`
3. `youtube-warder-v1.0.0`

`update/stable.json` smeruje na `v1.0.2`, s kontrolou SHA-256 a byte length. `update/testing.json` má `release: null`; nepublikuj testovací IPK ani netvor ďalšie vydanie len kvôli retencii. `main` nemá samostatné `packages/`, `build/`, `dist/` s historickými IPK. Existujúce zložky s testovacou dokumentáciou a aktívne draft PR sa zachovávajú.

Pred odstránením konkrétneho TEST/RC Release najprv potvrď, že nemá aktívny updater, používateľský odkaz alebo jedinú obnovovaciu kópiu. Zmazanie Release, jeho assetov a Git tagu sú rozdielne operácie. Git históriu neprepisovať, žiadne force-push.

Spoločný checkpoint: [FullHDGlass/docs/ECOSYSTEM-CLEANUP-CHECKPOINT-20261123.md](https://github.com/Evolution-by-Warder/FullHDGlass-Warder-Evolution/blob/main/docs/ECOSYSTEM-CLEANUP-CHECKPOINT-20261123.md).
