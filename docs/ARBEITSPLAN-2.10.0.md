# Arbeitsplan und Abschluss – v2.10.0 (Phase 1: Design-System + WCAG 2.2 AA)

Stand: 16.11.2026 · Bezug: v2.9.5 (versionCode 295) → v2.10.0 (versionCode 296) · **abgeschlossen**.
Ziel war: Phase 1 strukturiert abschließen, alle offenen echten Defekte (V1, V2, V4, V7)
schließen, Version 2.10.0 ausliefern, Phase 2 (Lern-Assistent) dokumentiert als nächsten
Schritt zurückstellen.

Grundsatz wie im TESTPROTOKOLL: **verifizierte Fakten** und **Schlussfolgerungen** werden
getrennt. Jede Änderung ist mit Build + Selbsttest + API-Diff abgesichert; vor den Änderungen
Backup + SHA-256 (`backups/2026-11-16_abschluss/`, 94 Dateien).

## 1. Offene echte Defekte schließen (README Abschnitt 10) – alle erledigt

| # | Befund | Umsetzung | Nachweis |
|---|--------|-----------|----------|
| V1 | `sw.js` nahm `./style.css` und `./app.js` nicht in den Offline-Kern auf – Stil und Logik nach dem ersten Start im Cache veraltet | Beide Dateien in `ASSETS`; Cache-Version auf 2.10.0 gezogen | Selbsttest „Offline-Kern" |
| V2 | `manifest.json` `background_color: #f5f6f7` ≠ CSS `--bg: #f4eee3` – Splash-Farbe weicht ab | `background_color` = `#f4eee3` | Selbsttest „Startbild-Farbe" (auch `theme_color` = `--hdr`) |
| V4 | `DATA.version` war `"2.7.0"`, `versionName` `2.9.5` – Export-/Versionsangabe falsch | `DATA.version` = `"2.10.0"` | Selbsttest „Version stimmt überein" |
| V7 | `window.KOMP` wurde doppelt gesetzt (Objekt-Literal und `.boot` in `init()`) – API nur wegen der aktuellen Reihenfolge vollständig | Ein einziges `var API = {…}` vor `init()`; `init()` hängt nur noch `API.boot` daran; `window.KOMP = API` genau einmal | Selbsttest „window.KOMP": 53 Namen + `boot` = 54, kein Name entfernt |

## 2. Phase-1-Restpunkte (README Abschnitt 11) – alle erledigt

| Planpunkt | Stand vorher | Umsetzung in 2.10.0 |
|-----------|--------------|---------------------|
| Theme light/dark/auto | nur `prefers-color-scheme` (auto) | Manuelle Umschaltung „🌗 Darstellung: Automatik → Hell → Dunkel" im Mehr-Menü; `data-theme` am Wurzelelement; dunkle Token als eigene `@media screen`-Regel; Systemwahl bleibt Standard; Wahl in `S.prefs.theme` (reist mit der Sicherung); `<head>`-Bootstrap verhindert den Farblitz |
| Kontrast-Wächter | Kontraste einzeln behauptet, nicht überwacht | Selbsttest misst **13 Textpaar-Token in Automatik, Hell und Dunkel** (39 Messungen), je ≥ 4,5:1. Erste Fassung maß über Inline-`var()` und ergab transparente Hintergründe – jetzt werden aufgelöste Token-Werte gemessen |
| Fokus-Management | `:focus-visible`, Skip-Link vorhanden, aber Skip-Link nicht testbelegt | Skip-Link-Test ergänzt; Bestand verifiziert |
| Touch-Ziele & Reflow | 44 px (`--tap`) erledigt (Vorlauf) | unverändert, testbelegt |
| Textskalierung | rem/em-Basis, `clamp()` | testbelegt (Typografie-Test) |
| Reduced-Motion / System-Oszillationen | Kill-Switch vorhanden | zusätzlich `forced-colors`-Verträglichkeit ergänzt (Token auf Systemfarben, 3D-Deko aus) – das README hatte sie bislang ohne Grundlage behauptet |
| Semantik/Screenreader-Pass | Landmarks, `aria-live`, `lang` vorhanden | testbelegt (Überschriften, Statusmeldungen) |
| Typografie-Raster | Tokens `--s1…--s6`, `--r`, `clamp()` | testbelegt |
| Design-System-Token-Datei | Token leben in `style.css :root` | Bewusst **keine** Dateiauslagerung: die 79 Token-Namen (68 Design-Token + 11 Laufzeit-Token) sind bereits die Design-Grundlage und in `docs/api-snapshot.txt` erfasst; eine Zweitdatei würde CSP, Service-Worker-Kern und Wartung ohne Nutzen vergrößern |

## 3. Version 2.10.0 / versionCode 296 – alle Versionsangaben abgeglichen

`app/build.gradle` (296 / 2.10.0) · `index.html` (Titel, Fußzeile) · `app.js` (`DATA.version`) ·
`sw.js` (VERSION/BUILD) · `manifest.json` (version). Übereinstimmung per Selbsttest überwacht;
`aapt2 dump badging` bestätigt `versionCode='296' versionName='2.10.0'` im Paket.

## 4. Selbsttest-Erweiterung (99 → 106 Prüfungen)

1. Service-Worker-Kern enthält `style.css` und `app.js`
2. `manifest.json background_color` = Licht-Token `--bg` (und `theme_color` = `--hdr`)
3. Version: `DATA.version` = Manifest-Version = Titel-Kennung
4. `window.KOMP`: genau einmal gesetzt, 53 Namen + `boot`, kein Name entfernt
5. Darstellung umschalten: Auto/Hell/Dunkel, `data-theme` wirkt auf Token, Wahl wird gespeichert
6. Kontrast-Wächter: 13 Token-Paare in drei Zuständen ≥ 4,5:1
7. Skip-Link: vorhandenes, fokussierbar, bei Fokus sichtbar

## 5. Nachweis – erbracht (16.11.2026)

- **Build:** `.\build-debug.ps1` → drei ABIs (arm64-v8a, universal, x86_64), je 4.284.397 Bytes,
  SHA256 `575D6689…`, Signatur OK; Assets Quelle ↔ Merge identisch; zusätzlich **alle sieben
  Text-Assets** aus dem fertigen APK entpackt und mit den Quellen verglichen (identisch);
  `aapt2 dump badging`: `versionCode='296' versionName='2.10.0'`.
- **Selbsttest:** frische Origins (jwebserver, Ports 8096/8097/8094), **106 / 106 bestanden**,
  1 übersprungen. Konsolenmeldungen: nur der bekannte Chromium-Hinweis zu `navigator.vibrate`
  ohne Nutzer-Tap.
- **Darstellung im Browser-Lauf:** Wahl übersteht ein Neuladen; `meta name="theme-color"` folgt.
- **Dokumentation:** `README.md` (Stand 2.10.0, offene Punkte, Phase 2), `CHANGELOG.md`
  ([2.10.0]), `docs/TESTPROTOKOLL.md` (Build-Hashes, 5.5 neue Prüfungen, Prüfsummen),
  `docs/api-snapshot.txt` (KOMP-Hinweis V7, localStorage/Theme), dieses Dokument.

## 6. Entwicklungsstand / Schlussstrich

- **Abgeschlossen mit 2.10.0:** Phase 0 (Refactoring/QS), Phase 1 (Design-System + WCAG 2.2 AA),
  alle gemeldeten echten Defekte V1–V7.
- **Bewusst zurückgestellt (nächste Version 2.11.0, Phase 2):** kontextbewusster, lokal
  regelbasierter Lern-Assistent (Chat-Panel als Bottom-Sheet, Slash-Befehle, Fehleranalyse,
  adaptiver Quiz, Lernziel-Modus) – wie in README Abschnitt 11 beschrieben. Der Assistent
  bleibt lokal und regelbasiert, kein Cloud-LLM.
- **Voraussetzung für den Gerätelauf** (SM_S931B): USB-Debugging am Telefon bestätigen; alle
  übrigen Nachweise (Build, Selbsttest, Browser-Messungen) sind erbracht.