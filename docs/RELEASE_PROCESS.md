# Release Process

Stand: 17. November 2026 · gilt für die Auslieferung aus diesem Repository
(Web über GitHub Pages, Android über `android/`).

## Versionierung

- `versionName` = `X.Y.Z` (SemVer-Logik: Y = Funktionsstand, Z = Korrekturen).
- `versionCode` = `X*100 + Y*10 + Z` (295 ↔ 2.9.5). Für 2.10+ wäre das
  `X*100 + Y*10 + Z` mit zweistelligem Y nicht mehr eindeutig – deshalb ab 3.0
  auf `X*100 + Y*10 + Z` mit Y ≤ 9 begrenzt bleiben oder das Schema erweitern.
- Die Versionskette muss an **fünf** Stellen gleich sein (automatisch geprüft von
  `tests/verify-build.py`, Check „Version chain is consistent"):
  1. `index.html` → `DATA.version` (und Titel-Kennung)
  2. `manifest.json` → `version`
  3. `sw.js` → `VERSION` / `BUILD` (Cache-Name!)
  4. `tests/package.json` → `version` (und `package-lock.json`)
  5. `android/app/build.gradle` → `versionName` / `versionCode`
- Zusätzlich anzupassen: `PROJECT_MANIFEST.json`, `android/app/src/main/AndroidManifest.xml`
  (`android:label`), `README.md`, `CHANGELOG.md`.

## Schritte

1. **Arbeitsstand:** Branch aktualisieren, working tree sauber, Parität grün
   (CI-Gate: Wurzel == `algorithm/` == Android-Assets).
2. **Statische Prüfung:** `python tests/verify-build.py` (Python ≥ 3.9) –
   null Fehler, alle 33 Checks.
3. **Browser-Tests:** `cd tests && npm ci && npm run test:all` (Node ≥ 20,
   Playwright; `CHROMIUM_PATH` nutzt einen lokalen Chromium statt des
   Bündel-Downloads). Enthält seit 17.11.2026 den automatisierten App-Selbsttest
   (`test:selftest`, 100 Prüfungen). Umgebung und Ergebnis bei null Fehlern
   festhalten.
4. **Version heben** (siehe „Versionierung") – inklusive `sw.js`-Cache-Name,
   sonst liefern Rückkehrer einen alten Stand aus.
5. **Prüfsummen:** `python tests/verify-build.py --out build/verify` erzeugt den
   Testbericht; SHA-256 der geänderten Release-Dateien (mindestens `index.html`,
   `robot-navigation.js`, `sw.js`, `manifest.json`) in
   `BUILD-REPORT-<version>.md` und `PROJECT_MANIFEST.json` eintragen (Arbeitsbaum-
   SHA-256, Zeilenenden wie im Checkout).
6. **Android:** `cd android && ./gradlew :app:assembleDebug` (oder
   `bundleRelease` mit `KOMPENDIUM_*`-Umgebungsvariablen für das Signieren),
   `apksigner verify` je APK.
7. **Committen:** konventionelle Message (`feat:`/`fix:`/`docs:`/`chore:`),
   Inhaltsänderungen an den 70 Lernseiten nur mit fokussiertem Diff und
   menschlichem Review (siehe `docs/CONTENT_PRESERVATION.md`).
8. **Tag + Release:** `git tag -a <version>` auf den Release-Commit,
   `git push origin <branch> --tags`; GitHub-Release mit den Prüfsummen aus
   dem Build-Report. Stand 18.11.2026: `v2.9.2`, `v2.9.4` und `v2.9.5` (nachträglich auf
   `dcc4388`) sind getaggt; ein GitHub-Release-Eintrag (mit Checksummen-Text) war nie
   angelegt – der Schritt ist nur Datenpflege im Reiter „Releases".
9. **Web:** Push auf `main` – GitHub Pages baut automatisch neu (Branch-Root,
   siehe `docs/GITHUB_PAGES.md`).

## Rollback

- **Inhalt:** `git revert <commit>` (behält Historie) oder
  `git reset --hard <letzter-guter-stand>` + Force-Push (nur mit Absprache –
  öffentliches Repo). Web-Fehler sind nach dem Pages-Neubau in Minuten korrigiert.
- **Service-Worker-Falle:** Der Cache-Name ändert sich nur mit `VERSION`/`BUILD`
  in `sw.js`. Ein Rollback ohne Cache-Bump liefert Rückkehrern weiter den neuen
  Stand aus dem Cache – also bei jedem Rollback den Cache-Name mitziehen.
- **Android:** `versionCode` muss bei einem Neu-Aufsetzen steigen, sonst
  verweigert das Gerät das Update (Signatur identisch).

## Nicht behaupten

Nie statische Checks als Browser-Tests ausgeben. CI-Status nur behaupten, wenn
ein Lauf sichtbar ist (Actions-Reiter); der Kontobilling-Status der Actions ist
eine Entscheidung des Kontoinhabers.