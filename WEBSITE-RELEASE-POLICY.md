# Warder Evolution – povinná synchronizácia vydaní a webu

## Povinná synchronizácia oficiálneho webu pri každom vydaní (25. 11. 2026)

Vlastník výslovne nariadil pre všetky súčasné aj budúce projekty Evolution-by-Warder: **každé nové schválené a overené stabilné vydanie skinu/pluginu musí v tom istom vydávacom cykle aktualizovať aj https://warder-evolution.eu/.** Ide o povinný dokončovací krok, nie voliteľnú úlohu na neskôr. Súhlas s vydaním zahŕňa synchronizáciu v jeho rozsahu bez opakovaného schvaľovania.

- Over skutočne publikovaný stabilný GitHub release, tag, verziu, IPK, dostupnosť a kontrolný súčet artefaktu. Test-only, draft, prerelease a neoverené buildy neuvádzaj ako stabilné.
- V centrálnom repozitári YouTube-Warder-Evolution aktualizuj `docs/index.html` a produktový detail: verziu, status, priame odkazy na IPK a release notes, dátum overenia, popis zmien, funkcie, kompatibilitu, jazykovú podporu a ostatné reálne zmenené údaje vo všetkých štyroch jazykoch SK/EN/DE/RU. Pri dátových aktualizáciách bez nového IPK aktualizuj dotknuté verejné údaje, ak sa zmenili. Zachovaj nedotknuté produkty, grafiku, galérie a právne/autentifikačné stránky. Informačná bublina planéty preberá existujúci obsah detailu, nie duplicitné údaje.
- Pracuj cez webový PR z aktuálneho main, koordinuj súbežné zmeny. Po úspešnom webovom CI zlúč, over úspešné GitHub Pages nasadenie a správnu verejnú verziu a odkazy. Nedostupné verejné overenie či zlyhanie nasadenia zapíš ako blokáciu.
- V projektovom registri a webovej dokumentácii eviduj release/tag, webový PR/commit, testy a nasadenie. Vydanie neoznač za kompletne dokončené, kým nie je synchronizácia webu overená. Pri blokácii rozlišuj vydaný plugin od neaktualizovaného webu. Pri novom projekte doplň katalóg a detail s planétou podľa dokumentácie.
- Platí aj pre automatizované vydania. Samotný zápis pravidla nie je automatický cross-repository trigger; kým taký mechanizmus nie je preukázateľne zavedený, vykonáva synchronizáciu zodpovedný release Work/agent. Existujúce CI, bezpečnostné stop-podmienky a pravidlá autentifikácie zostávajú záväzné.

Centrálne pokyny: [zdroj webu](https://github.com/Evolution-by-Warder/YouTube-Warder-Evolution/tree/main/docs), [dokumentácia animácie](https://github.com/Evolution-by-Warder/YouTube-Warder-Evolution/blob/main/docs/WEBSITE-ORBIT.md).


## Mapa produktov

- FullHDGlass: `docs/fullhdglass.html`
- PiconHub: `docs/piconhub.html`
- Radio: `docs/radio.html`
- YouTube: `docs/youtube-warder.html`
- GSU: `docs/gsu.html`

Hlavný katalóg: `docs/index.html`. Dokumentácia: `docs/WEBSITE-PORTAL.md`, `docs/WEBSITE-ORBIT.md`.
