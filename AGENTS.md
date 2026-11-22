# YouTube-Warder-Evolution – pravidlá pre prácu

## Trvalé pravidlo dokončovania schválenej práce (22. 11. 2026)

Toto pravidlo výslovne požadoval vlastník pre **všetky projekty Evolution-by-Warder**. Je nadradené starším všeobecným formuláciám o opakovanom schvaľovaní každého merge, IPK a produkčného zápisu.

1. **Jedno schválenie na konkrétny rozsah.** Ak vlastník schválil pomenovanú úpravu, celú dávku, vydanie alebo vopred definovanú automatickú aktualizáciu, súhlas zahŕňa aj obvyklé dokončovacie kroky v tomto rozsahu: vytvorenie PR, absolvovanie povinných testov, zlúčenie do `main`, zostavenie/vydanie príslušného finálneho balíka (ak projekt balíky vydáva) a aktualizáciu produkčného kanála. **Nepýtaj sa znovu na ten istý súhlas pri každom kroku ani v novom chate/Worku.** Rozsah a zdroj schválenia zapíš do PR a projektového denníka.
2. **Dokončenie po úspešnej verifikácii.** Pokiaľ rozsah zahŕňa produkčné vydanie a všetky povinné relevantné CI/regresné testy prejdú, bezpečne dokonči merge → release → verifikáciu skutočne publikovaného artefaktu/SHA-256 → aktualizáciu produkcie. Ak je nastavená schválená automatizácia, nech postup vykoná ona. Nevydávaj zbytočné medziverzie a nenechávaj hotové, schválené PR otvorené iba kvôli opakovanému žiadaniu.
3. **Žiadne neautorizované rozšírenie.** Test-only/draft, nová neschválená funkcia, zmena schválenej grafiky, neoverená licencia, zásah do súkromných dát, mazaní/zálohovaní či zmena autentifikácie nesmú byť ticho považované za schválené na produkciu. V týchto prípadoch si vyžiadaj jedno nové konkrétne schválenie.
4. **Povinné stop-podmienky.** Zlyhané alebo neúplné CI, zmena očakávaného SHA, nejasná identita artefaktu, konflikt vetvy, nedostatočné oprávnenia, bezpečnostná chyba alebo neoverená publikácia blokujú merge/vydanie. Skutočný stav a blokáciu zapíš; nikdy netvrď, že automatický merge či release prebehol, ak nie je doložený na GitHube.
5. **Trvalé odovzdanie.** Každý nový chat/Work načíta tieto pravidlá, aktuálny `main`, otvorené PR, CI, posledné vydanie a projektový register. Pokračuj od posledného overeného kroku a dokonči už schválenú prácu bez návratu na staré opakované schvaľovanie. Zachovaj používateľské súbory, existujúce schválené picony a históriu.

Toto je záväzné pravidlo práce vo všetkých repozitároch; **samo vloženie tohto textu nespúšťa GitHub automatizáciu**. Ak chýba mechanizmus automatického vykonania, odlíš pripravenú politiku od reálne aktivovaného workflowu.

## Ochrana a vydávanie

- Používaj iba existujúce autorizované pripojenia a chráň používateľské nastavenia, tokeny, pluginy a osobné dáta.
- Vydaj iba artefakty spadajúce do schváleného rozsahu a so všetkými povinnými testami, overenou veľkosťou a SHA-256. V prípade bezpečnostného konfliktu alebo neschváleného rozšírenia zastav publikovanie.
