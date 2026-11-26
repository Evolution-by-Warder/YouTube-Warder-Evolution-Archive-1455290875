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

## 2026-11-26 — ďalší checkpoint PR #41

HEAD `c9311d2f8d70947193147557bee43acc5fe831c6`: plný poľský katalóg 357 kľúčov dopĺňa ruský; runtime načítava UTF-8 JSON iba z povolených jazykových kódov, podporuje aliasy a zachováva English fallback. Nové regresné testy preverujú zhodu kľúčov so všetkými pôvodnými slovníkmi, formátovacie argumenty a reálne použitie externého katalógu. CI `test` job 139658378354 SUCCESS na uvedenom SHA. Zostáva 15 chýbajúcich jazykov (hu, fr, it, es, al, el, et, fa, lt, nl, pt, ro, tr, uk, zh), explicitná finálna kontrola 21/21, audit reálne používaných reťazcov a stabilný release 1.0.4. Žiadna zmena autentifikácie, používateľských dát, existujúceho IPK ani feedu. Webový PR #40 bol nasadený cez Pages run 45738429500 SUCCESS; verejná stránka mimo GitHub spojenia neoverená. Produkcia 1.0.3.

## 2026-11-26 — rozšírenie na 14 z 21 jazykov, PR #41

HEAD `4a0c37ee6895dd450bd029410246e7807e6242b0`: desať kompletných externých UTF-8 katalógov po 357 kľúčoch (ru, pl, fr, es, it, hu, pt, zh, uk, nl) + štyri pôvodné runtime slovníky. Kontrola formátovacích argumentov pred každým commitom. Predchádzajúci HEAD `5fbda4d860a2b2f741d501af215d2fa6847bc320` CI test job 139661010967 SUCCESS; najnovší HEAD: test 139661429964: completed/success. Zostáva sedem katalógov al, el, et, fa, lt, ro, tr, finálna kontrola všetkých 21 jazykov a audit reálne používaných reťazcov. Neaktivovať verziu 1.0.4 pred kompletnou lokalizáciou a úspešným CI. Produkčné IPK 1.0.3, feed, autentifikácia a používateľské údaje nezmenené.


## 2026-11-26 — Romanian localization checkpoint

Commit `68e16fb618370078c4dc02665e6084f16c30058c`: Romanian full 357-key catalogue added; exact key count and ordered format placeholders verified before write. Candidate now contains 15/21 languages (11 external catalogues + 4 original runtime dictionaries). Remaining: al, el, et, fa, lt, tr; keyboard and additional runtime audit; version/notes and verified stable publication. PR #41 stays draft; production 1.0.3 and feeds unchanged. CI at checkpoint: test success.

## 2026-11-26 — 1.0.4 stable release candidate, PR #41

All 21 runtime languages: four original dictionaries and 17 actual translated UTF-8 catalogues of 357 keys. Additional 57 runtime messages in all 21 languages include playback, OAuth, live subscriptions, keyboard and every explicit updater error; numeric opkg return code retained. Fallback keyboard coverage expanded (Chinese uses ASCII/pinyin fallback; native image keyboard determines IME availability); secret input remains masked ASCII. Exact tested predecessor `884b735850ec96aa8b17f36192ef8cff2f1829e5`, CI test job 139691268547 SUCCESS. Candidate advances source/control/README to 1.0.4, adds stable IPK locale inclusion regression and public asset byte comparison before stable manifest publication. No release, tag or feed change until exact candidate CI success and merge. Existing authentication, user data and graphics unchanged. Physical receiver validation remains separate from CI.

CI job 139691568215 failed on `e4fd551a134a563ec079f1ac1982bfd1cca95545` (450 tests, 2 failures + 2 errors): previous version assertion and strict IPK updater rejected JSON payload files. Rather than weaken the whitelist (which would still leave installed 1.0.3 receivers unable to upgrade), build a deterministic data-only Python resource from the exact translated JSON source, verify all catalogues are identical to source and run the existing strict IPK validator on the stable archive. No change to the legacy updater path checks or to any already released package.

## 2026-11-26 — YouTube 1.0.4 stable publication verified

PR #41 exact reviewed HEAD `4fec39d92c488d3faaafaf102097666c9a4243a3`, CI job 139692079769: 450 tests passed. Merged `d7ee03a84c0ee83bfa33dd05f31d0a52f54923e5`; tag `youtube-warder-v1.0.4` points to that commit. Canonical release job 139692238484 SUCCESS, 450 tests, verified unauthenticated public download byte-for-byte before stable feed update. Public IPK `enigma2-plugin-extensions-youtube-warder-evolution_1.0.4_all.ipk`, 739858 bytes, SHA-256 `ffba1d61982a9c09fdeef0d971992fb3832d5e72cb04b282985a2bc0cc93769f`; release asset metadata and `update/stable.json` at `0f7fac07633f7ba48e4799ed3c780844bcf644cc` match. The old testing feed remains unchanged. No public TEST release. Source 17×357 actual translated catalogue entries + four original dictionaries; 57 additional messages across 21 languages. Native 50-key fallback supports language-specific input within layout constraints (Chinese uses ASCII/pinyin; native image IME determines full Chinese input). Existing updater whitelist preserved; exact JSON data packaged as a deterministic data-only Python module. No change to authentication or user data. This web PR updates all four marketing languages and correct stable download links; Pages deployment still needs verification. Physical receiver testing not claimed.


## 2026-11-26 — Website deployment verified

Web PR #42, merge/main `3ca95748126b8d0ca3b9151c71e77469e67452e0`, GitHub Pages [run 45755609359](https://github.com/Evolution-by-Warder/YouTube-Warder-Evolution/actions/runs/45755609359) completed SUCCESS at the exact merge SHA. SK/EN/DE/RU website version 1.0.4 and release links are deployed by Pages. GitHub release asset SHA-256 `ffba1d61982a9c09fdeef0d971992fb3832d5e72cb04b282985a2bc0cc93769f`, 739858 bytes, matches live main stable feed. Direct public custom-domain browser access was not independently performed, in accordance with the GitHub-only scope. No change to plugin, feeds, authentication, graphics or data.

## 2026-11-26 — GSU r5 web synchronization candidate

GSU PR #14, source `9e03199394ca498d30120cca5cf184752e0f1bbf`, canonical publisher 45763722273, IPK 3812194 B, SHA-256 `17de1b2624dd90b77d2c8c05ceba997e683c2d66d888212dda21e31233ef7085`. Production record confirms native matrices and published IPK/sidecar verification. Main and original-python314 stable feed r5 match. SK/EN/DE/RU catalogue and detail now show r5 and actual 21 languages, lifecycle changes, correct downloads. Pages deployment pending. Separate PR #15 version-normalization effort is not yet production and is not advertised. Other product cards, artwork, account data and runtime unchanged.
