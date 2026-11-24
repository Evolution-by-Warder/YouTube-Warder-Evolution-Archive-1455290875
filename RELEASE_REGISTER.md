# YouTube Warder Evolution – register vydaní a overení

## 2026-11-24 – verzia 1.0.3

**Rozsah schválený vlastníkom:** nové ostré IPK po testovacej sérii 1.0.2~test1 až 1.0.2~test5, spolu so zápisom všetkých zmien do projektu. Príprava pokračuje z testovacej vetvy bez opakovania hotových úloh.

**Funkcie:** TV prihlásenie k skutočnému účtu, skutočné osobné Odbery, MENU → Páči sa mi na YouTube, okamžité miestne uloženie úspešného hodnotenia, automatický jednosmerný import do Obľúbených, bezpečné stránkovanie, 6 000 miestnych obľúbených, zachovanie Histórie.

**Opravy z prijímacieho testovania:** krátko viditeľný TV kód (nesprávny parameter), prázdny náhľad Obľúbených pred stlačením OK, chýbajúce novo označené video v miestnych Obľúbených, poradie najnovších hodnotení.

**Dáta:** nezmazať miestne Obľúbené ani Históriu; nevkladať tokeny do logov; pri upgrade zachovať bezpečne identifikovaný testovací účet. Staršie verzie 1.0.0 až 1.0.2 zostávajú ako samostatné vydania.

**Overenie pred produkciou:** GitHub Actions testy, kontrola zostaveného IPK, zhoda verzie/sha256, samotný publikovaný GitHub Release a produkčný `update/stable.json`. Žiadne tvrdenie o vydaní nie je potvrdené iba týmto záznamom.

**Súvisiace práce:** [PR #11](https://github.com/Evolution-by-Warder/YouTube-Warder-Evolution/pull/11) – vývojová séria; produkčná vetva `release/youtube-warder-1.0.3-20261124`. Podrobnosti: [RELEASE_NOTES_1.0.3.md](RELEASE_NOTES_1.0.3.md).
