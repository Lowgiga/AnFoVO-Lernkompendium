# Changelog

Format: Keep a Changelog. Versionierung `X.Y.Z` ↔ `versionCode = X*100 + Y*10 + Z` (295 ↔ 2.9.5) –
Details in [docs/RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md).

## 25.11.2026 – Veröffentlichungsgate erfüllt

- **§-5-DDG-Impressum ergänzt:** Die bereitgestellten Anbieterangaben stehen jetzt in
  `IMPRESSUM.md` und im Impressum der Web-/Android-Oberfläche; der frühere
  Veröffentlichungs-Platzhalter ist entfernt.
- **Verifikation angepasst:** Der statische Verifier und sein Regressionstest verlangen nun
  die vollständigen Anbieterangaben in beiden Dokumenten und die Byte-Parität der beiden
  `index.html`-Kopien.
- **Service-Worker-Cache erhöht:** `web-pwa-2.9.5-legal.1` erzwingt bei Rückkehrern einen
  frischen Impressum-Stand statt des bisherigen cache-first-Bestands.
- **Veröffentlichungsdokumentation aktualisiert:** README, Pages-Dokumentation, Build-Report
  und Projektmanifest wurden auf den erfüllten Veröffentlichungsstand gebracht.

## 18.11.2026 – Wartung und Verifikation (auf `main`)

*Vollständige Nachprüfung aller Aussagen im Repository gegen den Code (fünf Perspektiven:
App-Code, Tests/CI, Dokumentation, Build/Deployment, Git).*

- **Versionen konsistent gemacht:** `DATA.version` in `index.html` war `2.7.0`, RobotNav-Kopf
  und `inspect()` `2.8.0` – beide auf `2.9.5` gezogen; `tests/verify-build.py` prüft die
  Versionskette jetzt automatisch (DATA = Manifest = `sw.js` = tests = Titel).
- **App-Selbsttest automatisiert:** `tests/selftest-app.cjs` fährt die 100 In-App-Prüfungen
  (`?test=1`) headless und ist in `npm run test:all` und CI eingebungen – lokal 100/100 grün.
- **`forced-colors` nachgerüstet:** Token auf Systemfarben, dekorative 3D-Szene und
  Canvas-Hintergrund schalten ab (reines CSS, additiv).
- **Hartkodierte Versions-Prüfung im RobotNav-Harness entschärft:** Erwartungswert wird aus
  der Engine-Datei gelesen (die `2.8.0`-Litane war zweimal veraltet).
- **`verify-build.py --out`:** Testberichte gehen nach `build/verify/` (gitignoriert) statt
  ins Wurzelverzeichnis – kein Tree-Drift mehr; CI lädt sie als Artefact hoch.
- **Dead Code entfernt:** `tests/run-browser-tests.py` (unbenutzbares Python-Duplikat),
  `tests/shots_tmp.cjs` (hartkodierter Temp-Pfad).
- **CI gehärtet:** `setup-python` 3.12, `setup-node` v7, `robot-navigation.js` (Wurzel) in
  Path-Filter und Parity-Liste, Concurrency, `timeout-minutes`, Gradle-Cache,
  Lizenz-Akzeptanz für `sdkmanager`, versionsunabhängiger Artefaktname.
- **`.gitignore` gehärtet:** `*.apk`, `*.aab`, `backups/`, `.vercel/`, `.env*`, IDE-,
  Pages- und Test-Muster – genau diese Lücken hatten den 80-MB-Baseline-Commit ermöglicht.
- **Dokumente auf Ist-Zustand gebracht:** `docs/GITHUB_PAGES.md` (Pages ist live und
  published den Branch-Root – verifiziert; vorher „nicht aktiviert"), `docs/TECHNICAL_AUDIT.md`
  (32→33 Checks, RobotNav standalone, Zeilenzahlen), `docs/CONTENT_PRESERVATION.md`
  (100/100 statt 97/100), `docs/ARCHITECTURE.md`, `.github/copilot-instructions.md` und
  `.github/skills/robotnav/SKILL.md` („embedded runtime" → standalone), `docs/RELEASE_PROCESS.md`
  (echter Prozess mit Versionierungsschema, Rollback, SW-Cache-Falle), README
  (CI-Status widerspruchlos, Barrierefreiheits-Abschnitt, Test-Voraussetzungen).
- **Hashes korrigiert:** `PROJECT_MANIFEST.json` und `BUILD-REPORT-v2.9.5.md` nannten
  `5461f6fe…`/629.905 B; real `2BD1DEC4…`/630.032 B (Arbeitsbaum-SHA-256; Wurzel und
  Android-Assets byte-identisch). Wrapper-Paritätsaussage im Build-Report als historisch
  markiert (Wrapper-Zweig ist seit v2.10.0 divergiert).
- **Datenschutzerklärung:** defektes Dateiende („PY") entfernt.
- **Externe Badge-Bilder:** fünf Vercel-gehostete Anzeigebilder aus der README entfernt
  (auf Wunsch des Betreibers); es bleibt ein Hosting-Werkzeug (GitHub Pages).
- **Release-Tag nachgezogen:** `v2.9.5` liegt jetzt auf dem Release-Commit `dcc4388`
  (angelegt und gepuscht am 18.11.2026; die Vorgänger-Tags `v2.9.2`/`v2.9.4` hatten ihre
  Releases markiert, für 2.9.5 fehlte er).
- **Offen (Dokumentiert, kein Code-Defekt; Stand 18.11.2026):** GitHub Pages ist bereits öffentlich erreichbar;
  das Veröffentlichungsgate war damals nicht erfüllt. Der Impressum-Platzhalter (§ 5 DDG)
  musste durch echte Angaben ersetzt werden (dabei Verifier, Regressionstest und beide
  `index.html`-Kopien gemeinsam aktualisieren) oder GitHub Pages muss deaktiviert werden;
  zwei konkurrierende Dark-Mode-Paletten (visueller Eingriff, daher nicht umgesetzt);
  Monster-Zeilen im HTML (Inhaltsdiff); Gerätetest v2.9.5 (Gerät offline).

## 2.9.5 – 2026-11-14

- Adopted the standalone RobotNav architecture from the wrapper workstream: `index.html` now loads `robot-navigation.js` via `<script src>` instead of an inline embedded block; the service worker precaches the engine file and supports `skip-waiting`.
- Added byte-parity checks for the engine copies (root ↔ `algorithm/` ↔ Android assets) and extended the PWA precache expectation.
- Learning content unchanged (the embedded `DATA` payload is byte-identical apart from the `DATA.version` metadata; raw and normalized hashes are documented in the v2.9.5 build report); animation overhaul from v2.9.4 carried over.
- Bumped to v2.9.5 / versionCode 295.

## 2.9.4 – 2026-11-14

- Redesigned the book/robot page-turn animation to compositor-only `transform`/`opacity`.
- Throttled the stage parallax with `requestAnimationFrame` via `--par-x`/`--par-y`.
- Softened the page-turn gestures (book nudge, leaf turn, robot gesture/nod/climb).
- Bumped to v2.9.4 / versionCode 294.

## 2.9.3 – 2026-11-14

- Aligned all version references to v2.9.3 (`index.html`, `sw.js`, manifest) and updated the version assertions.

## 2.9.2 – 2026-11-14

- Release preparation: selector fixes, script-tag fix, README conflict resolution, version 2.9.2 (PR #5).
- Restored the complete WebView asset set in Android (bg frames, sw.js, manifest, RobotNav, PWA icons).
- Enforced Android asset and project quality gates in CI.
- Added Copilot skills (Android WebView, quality/release, RobotNav, web learning app) and project instructions.
- Added the privacy policy for the Play Store listing and enabled GitHub Pages in the README (live URL).
- Marked release signing configured and added the pixel comparison record.

## 2.9.1 – 2026-11-12

- Added a matching Android WebView wrapper and built a debug APK with Gradle 8.13 / AGP 8.13.2.
- Fixed the Android round-icon resource reference so the APK resource-linking step succeeds.
- Restored static and Playwright browser validation to the Android CI workflow, including test-path triggers.
- Restricted the documented Gradle runtime to supported JDK 17 or 21.
- Verified ARM64, universal and x86_64 debug APK signatures with APK Signature Scheme v2.
- Updated the mascot to a silver metallic appearance with graphite visor and ice-blue eye lighting.
- Prepared the repository root as an installable offline PWA for the GitHub Pages project subpath `/AnFoVO-Lernkompendium/` and mirrored `manifest.json`, `sw.js`, icons and `bg/` to the Android assets.
- Added `scripts/prepare-pages-surface.sh` for a local web-only directory.
- Preserved the learning content and standalone offline runtime; verified the 70-page app in local Chrome.

## 2.9.0

- Hybrid 3D book presentation refined; mascot changed to a white ceramic/metal visual treatment.
- Added architecture, design-system, content-preservation and release-process documentation.
- Static checks: 20 passed, 0 failed; browser interaction tests not yet verified at that point.