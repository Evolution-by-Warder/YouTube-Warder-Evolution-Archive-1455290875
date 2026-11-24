# YouTube Warder Evolution 1.0.3

**Ostré vydanie – 24. novembra 2026**

## Novinky
- Jednoduché prihlásenie do skutočného YouTube účtu pomocou TV kódu a automatické obnovenie uloženého prihlásenia.
- Sekcia **Odbery** zobrazuje osobné odbery prihláseného používateľa.
- Pri vybranom videu pribudla v **MENU** akcia **Označiť Páči sa mi na YouTube**. Hodnotenie sa odošle do používateľovho účtu až po jeho výbere.
- Úspešne označené video sa okamžite bezpečne uloží aj medzi miestne **Obľúbené**, bez duplicít alebo nechceného odobratia.
- Pri **každom spustení pluginu** prebehne na pozadí jednosmerné doplnenie chýbajúcich videí Páči sa mi z YouTube do Obľúbených. Bez stlačenia OK a bez odosielania miestnych Obľúbených na YouTube.
- Najnovšie videá sa zobrazujú pred staršími, import zostáva atomický a neodstraňuje existujúce položky. Kapacita miestnych Obľúbených je 6 000 videí.
- Pre väčšie účty sa plugin pokúsi použiť osobný playlist Páči sa mi, s bezpečným záložným načítavaním najnovších 1 000 videí, ak playlist nie je dostupný.
- Pri sťahovaní veľkého zoznamu sa prvá stránka sprístupní priebežne; výpadok API, opakované stránkovanie alebo zatvorenie obrazovky nesmie vymazať existujúce údaje.
- Opravené spracovanie TV kódu a opakovaných autorizácií; dočasná chyba siete neukončí platný kód predčasne.

## Zachované údaje a funkcie
- **História** zostáva históriou prehrávania cez tento prijímač. Celú webovú históriu pozerania YouTube API nesprístupňuje.
- Pôvodné miestne Obľúbené, ich názvy, história, nastavenia prehrávača a ostatné funkcie zostávajú zachované.
- Pri aktualizácii z overenej testovacej verzie sa existujúce lokálne prihlásenie prenesie do produkčného úložiska, iba ak je dostupný jednoznačný bezpečný tokenový súbor.
- Výsledné zdrojové kódy neobsahujú heslá používateľov ani ich osobné tokeny.

## Inštalácia
Balík: `enigma2-plugin-extensions-youtube-warder-evolution_1.0.3_all.ipk`

```sh
opkg install /tmp/enigma2-plugin-extensions-youtube-warder-evolution_1.0.3_all.ipk
```

Po inštalácii obnov GUI Enigma2.

## Kontrola a stav
Zdrojové a balíkové testy sa spúšťajú pred publikovaním. Automatické testy nenahrádzajú kontrolu všetkých prijímačov; fungovanie jednotlivých typov obrazu a správanie externého YouTube API sa môže líšiť. Staršie stabilné vydania zostávajú na GitHub Releases zachované.
