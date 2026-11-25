# Warder Evolution – animovaný planetárny ekosystém
Schválené vlastníkom 25. 11. 2026. Lebka je pevný stred, planéty obiehajú plynulo dookola. Pôvodný PNG sa nemení.

## Kde je zdroj
- `docs/portal-orbit.js` – výpočet polohy, generovanie planét, ikony, počet, ovládanie.
- `docs/portal-orbit.css` – vzhľad, rozmery, rýchlosť a animácia.
- `docs/index.html` – zdrojový katalóg projektov, odkazy a voliteľné atribúty planét.
- `tests/test_website_portal.py`, `tools/verify_website_portal_browser.py` – regresné testy.

## Pridanie projektu
Pridaj jeho bežnú kartu `article.product` do `#products .products` s odkazom `a.product-card-link`. Planéta vznikne automaticky podľa názvu a odkazu. Voliteľné atribúty karty: `data-planet-icon="display|grid|radio|play|gear|star"`, `data-planet-color="#hex"`, `data-planet-name="kratší názov"`. Bez atribútov sa použije hviezda, názov z karty a jej farebný akcent. Nie je potrebné upravovať zoznam planét. Počet a rovnomerné uhly sa prepočítajú aj pri dynamickej zmene katalógu.

## Úprava pohybu
V CSS uprav `--orbit-period:38s` (jedna otáčka za 38 sekúnd), veľkosť planét alebo polomer `inset:13%` na .planet-track a .o1 súčasne. Opačná rotácia vnútornej vrstvy drží názvy vodorovne. Pozastavenie tlačidlom, myšou alebo klávesovým fokusom; rešpektuje prefers-reduced-motion. Pri veľkom počte projektov sa planéty zmenšujú; pri ďalšom rozšírení over čitateľnosť na mobile a podľa potreby pridaj ďalšiu dráhu. Po úprave zdrojov zmeň verziu ich URL v index.html a na všetkých produktových stránkach s animáciou. Nepoužívaj statický obrázok alebo GIF ako náhradu animácie.

## Jedna planéta na produktovej stránke
Každá z piatich produktových stránok používa rovnaké súbory JS/CSS ako hlavná stránka. Priamo v `detail-hero-grid` je `hero-visual` s atribútom `data-orbit-mode="single"` a atribútmi `data-planet-name`, `data-planet-icon`, `data-planet-color`. Zodpovedajú karte produktu na hlavnej stránke. Pri novom produkte skopíruj tento prvok z existujúcej stránky a nastav tieto tri údaje; spoločný motor netreba meniť. Na hlavnej stránke je planéta odkaz na produkt; na detaile je tlačidlom, ktoré otvorí kompaktnú informačnú bublinu. Animácia sa pozastaví počas otvorenia. Obsah sa preberá v aktuálnom jazyku z `.detail-intro`, `.detail-copy .ver`, `.detail-copy .status` a prvých troch `.feature-card h3`; nepíše sa duplicitne. Zatvorenie krížikom, Escape alebo kliknutím mimo bubliny. Ostatné funkcie animácie vrátane tlačidla pozastavenia a systémového obmedzenia pohybu sú spoločné. Sekcia produktu používa spoločnú triedu `hero` a rovnaké súvislé pozadie ako hlavná stránka. Animácia je priamym prvkom mriežky, bez rámu, samostatného pozadia, tieňa alebo obalového panelu. Staré `detail-visual` a `orbit-showroom` sa nepoužívajú. Opravený PNG lebky je rovnaký ako na hlavnej stránke. Pôvodné produktové grafiky zostávajú v katalógu a repozitároch, nie sú prepisované.

## Komunitné planéty a rezervné miesta (25. 11. 2026)
Na hlavnej stránke je v `docs/index.html` jediná upraviteľná konfigurácia `template#community-planets`. Cieľ je osem planét (`data-target-count="8"`): prednosť majú všetky vlastné projekty, zvyšné miesta vyplnia menšie externé planéty v poradí odkazov v šablóne. Pri pridaní šiesteho projektu automaticky zostanú prvé dve komunitné planéty, pri siedmom prvá a pri ôsmom žiadna; od deviateho projektu sa zobrazia všetky vlastné projekty. Poradie, odkazy, symboly a farby komunitných planét je možné zmeniť na jednom mieste bez zásahu do motora. Ak chce vlastník zachovať konkrétnu komunitu, presuň jej odkaz na začiatok. Externé odkazy otvárajú novú kartu s noopener noreferrer; nejde o vlastné produkty ani tvrdenie o partnerstve. Na detailoch zostáva iba príslušná produktová planéta s informačnou bublinou. Rýchlosť a smer sú spoločné. Pri rozšírení skontroluj čitateľnosť na mobile.

## Návrat na hlavnú stránku cez lebku
Na produktových stránkach je stredová lebka v natívnom odkaze `a.skull-home[href="index.html"]`, s lokalizovaným prístupným názvom SK/EN/DE/RU. Funguje kliknutím, dotykom aj klávesom Enter rovnako ako logo v hlavičke. Zachováva rovnaké rozmery, grafiku a súvislé pozadie; nie je to prekrytie. Na hlavnej stránke je lebka naďalej neinteraktívnym stredom. Planéty a ich správanie ostávajú samostatné. Pri novom produkte použi rovnaký natívny odkaz.
