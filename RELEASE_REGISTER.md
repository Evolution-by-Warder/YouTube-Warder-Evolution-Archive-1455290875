# YouTube Warder Evolution – register vydaní a overení

## 2026-11-24 – verzia 1.0.3

**Rozsah schválený vlastníkom:** nové ostré IPK po testovacej sérii 1.0.2~test1 až 1.0.2~test5, spolu so zápisom všetkých zmien do projektu. Príprava pokračuje z testovacej vetvy bez opakovania hotových úloh.

**Funkcie:** vylepšená stabilita autentifikačného kódu a obnovenia relácie, skutočné osobné Odbery, MENU → Páči sa mi na YouTube, okamžité miestne uloženie úspešného hodnotenia, automatický jednosmerný import do Obľúbených, bezpečné stránkovanie, 6 000 miestnych obľúbených, zachovanie Histórie.

**Opravy z prijímacieho testovania:** krátko viditeľný TV kód (nesprávny parameter), prázdny náhľad Obľúbených pred stlačením OK, chýbajúce novo označené video v miestnych Obľúbených, poradie najnovších hodnotení.

**Dáta:** nezmazať miestne Obľúbené ani Históriu; nevkladať tokeny do logov; pri upgrade zachovať bezpečne identifikovaný testovací účet. Staršie verzie 1.0.0 až 1.0.2 zostávajú ako samostatné vydania.

**Overené ostré vydanie:** GitHub Actions testy a zostavenie úspešné; `youtube-warder-v1.0.3` bol publikovaný 24. 11. 2026 s IPK `enigma2-plugin-extensions-youtube-warder-evolution_1.0.3_all.ipk` (620 630 bajtov, SHA-256 `a0305e178d168d7d13f00eef1e70077d18a37757ea74191944695a2bef9e8c5f`), čo potvrdzuje `update/stable.json` v `main`. Oprava iba textového popisu nemení IPK ani jeho SHA-256.

**Verejný popis:** Používaj neutrálne vyjadrenie „Vylepšený autentifikačný kód, stabilita autorizácie a automatické obnovovanie relácie“. Neprezentuj autentifikáciu ako úplne nové prihlasovanie a neuvádzaj pôvod technického riešenia v marketingovom popise. Technické testy a záznamy zostávajú pravdivé.

**Súvisiace práce:** [PR #11](https://github.com/Evolution-by-Warder/YouTube-Warder-Evolution/pull/11) – vývojová séria; produkčná vetva `release/youtube-warder-1.0.3-20261124`. Podrobnosti: [RELEASE_NOTES_1.0.3.md](RELEASE_NOTES_1.0.3.md).

## 2026-11-26 – synchronizácia webu (schválená nočná dávka)

FullHDGlass v1.0.94: PR #206, HEAD `697a98d27b8a490676f68e04c4871b0ec5a5078e`, 25/25 CI, merge `3e2b7107f1b2af584f21335815a1be5594d0f5bf`, GitHub asset SHA-256 `9dd3300cafffcdaa522b308c22dda863b6bc47ee190ba3f6c24ba235bbcd6028`. PiconHub v0.1.46: PR #110, HEAD `52fe05f39c8b2d4d8ed70ca82334a57457fe9e57`, 7/7 relevantných CI, merge `8b68eacfdd8522542e69f4cb5f5cb691fb278fd8`, GitHub asset SHA-256 `e8cca6447aac6dbffafba09fadf702e7200674003bf9ae5cebab84340619ab1b`. Webový kandidát aktualizuje SK/EN/DE/RU, odkazy a reálnu podporu PiconHub 21 jazykov. Nasadenie Pages zatiaľ neoverené. GSU 13.41-r4 a YouTube 1.0.3 ponechané bez zmeny; rozšírenie jazykov nepublikované. Radio 0.2.2 ponechané bez prázdneho vydania.

## 2026-11-26 – 21-language localization candidate (incomplete)

Base `e6f45880f89ba4cdcdfd0e323f502b2aca8f5eb5`. Union of existing four runtime dictionaries: 357 source keys (English map 161, Slovak 343, Czech 342, German 343). Russian full 357-key catalogue staged, placeholder sequences checked against English. Remaining 16 languages and runtime integration/tests not complete. No version bump or stable feed change; do not merge partial draft. Existing authentication, data and playback unchanged.
