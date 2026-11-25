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
V CSS uprav `--orbit-period:38s` (jedna otáčka za 38 sekúnd), veľkosť planét alebo polomer `inset:13%` na .planet-track a .o1 súčasne. Opačná rotácia vnútornej vrstvy drží názvy vodorovne. Pozastavenie tlačidlom, myšou alebo klávesovým fokusom; rešpektuje prefers-reduced-motion. Pri veľkom počte projektov sa planéty zmenšujú; pri ďalšom rozšírení over čitateľnosť na mobile a podľa potreby pridaj ďalšiu dráhu. Po úprave zdrojov zmeň verziu ich URL v index.html. Nepoužívaj statický obrázok alebo GIF ako náhradu animácie.
