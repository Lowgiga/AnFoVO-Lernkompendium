# GitHub Pages

**Stand: 17.11.2026 – verifiziert (Live-Abruf).** GitHub Pages ist für dieses Repository
**aktiv** und liefert die Web-App aus:

- Projekt-Site: `https://lowgiga.github.io/AnFoVO-Lernkompendium/` (Antwort 200, Titel
  „Lern-Kompendium § 8 AnFöVO NRW – v2.9.5", 70 Lernseiten, PWA installierbar).

## Was heute wirklich published wird (wichtig)

Veröffentlicht wird der **Branch-Root von `main`**, nicht der bereinigte Surface. Verifiziert
öffentlich abrufbar sind daher auch:

- `android/README-ANDROID.md` (Quellcode-Hinweise der WebView-Hülle)
- `tests/verify-build.py` (Test-Quellcode)
- `TESTBERICHT_v2.9.5.txt`, `SHA256SUMS_*`, `BUILD-REPORT-*`
- `gradle/wrapper/gradle-wrapper.jar`

Der Abruf ist harmlos (keine Secrets im Repo, Signing nur über Umgebungsvariablen), aber es
ist **nicht** die beabsichtigte Veröffentlichungsfläche. `scripts/prepare-pages-surface.sh`
bereitet genau diese bereinigte Flche (`dist/pages/`) vor – ihre Ausgabe wird derzeit von
**keiner** Automation konsumiert.

**Versionsdrift Live vs. Repository:** Die Live-Seite liefert `index.html` mit 619.449 Bytes,
das Repository hat 630.032 Bytes (Stand `dcc4388`, RobotNav als eigene Datei). Der letzte
Pages-Bau stammt damit aus einem etwas älteren 2.9.5-Stand. Nach dem nächsten Push auf `main`
mit Pages-Quelle „Branch-Root" baut GitHub die Site automatisch neu.

## Bereit auf diesem Branch

- `index.html` linkt `./manifest.json`, `./icon-192.png` und ein Apple-Touch-Icon.
- `manifest.json` nutzt relative `start_url`/`scope` (`./`), die Installation bleibt im
  Projekt-Unterpfad.
- `sw.js` precacht die Hlle, Icons, `robot-navigation.js` und beide `bg/d`- and `bg/m`-
  Bildstze; Cache-Name `anfoevo_v2_cache_2.9.5-web-pwa-2.9.5`.
- `.nojekyll` ist vorhanden, ein Pages-Bau läuft ohne Jekyll.
- Die Service-Worker-Registrierung läuft nur bei `http:`/`https:`. **Korrektur zur früheren
  Doku:** Im WebView wird **nicht** registriert – `index.html` (Registrierungsblock,
  „PWA: register only on http(s)") kehrt für `appassets.androidplatform.net` vorzeitig zurück.
  Die Offline-Fähigkeit der App kommt dort vom Asset-Lader, nicht vom Service Worker. Die
  `ServiceWorkerControllerCompat`-Einrichtung in `MainActivity` ist somit wirkungslos, aber
  harmlos; eine Entscheidung dazu ist offen (Doku-Punkt C4 im Technical-Audit-Abgleich).
- `index.html`, `manifest.json`, `sw.js`, `robot-navigation.js`, Icons und `bg/` sind
  byte-identisch unter `android/app/src/main/assets/`.

## Bereinigte Verffentlichungsflche (optional)

`scripts/prepare-pages-surface.sh` kopiert nur die Web-Hlle nach `dist/pages/` (gitignored):

- `index.html`, `manifest.json`, `sw.js`, **`robot-navigation.js`**
- `icon-192.png`, `icon-512.png`, `icon-512-maskable.png`
- `bg/`
- `.nojekyll`
- `LICENSE`

(Die Liste war unvollstndig: `robot-navigation.js` wird seit dem Skript kopiert und von
`sw.js` precached, war aber nicht dokumentiert.)

Das Skript nimmt ein Ziel nur unter `dist/` oder außerhalb des Repos an, löscht das Repository
nie und ersetzt ein Ziel nur bei vorhandenem `.pages-surface`-Marker. Es ändert keine
Repository-Einstellungen. Wer die bereinigte Fläche live schalten will, stellt die
Pages-Quelle in den Repository-Einstellungen auf „GitHub Actions" und ergänzt einen Deploy-
Workflow (Skript → `actions/upload-pages-artifact` → `actions/deploy-pages`); dann fallen
`android/`, `tests/`, Gradle-Wrapper und die Berichte aus dem öffentlichen Angebot heraus.

## Veröffentlichungsgate – derzeit offen

GitHub Pages ist bereits öffentlich erreichbar. Das erforderliche Gate ist deshalb **noch nicht
erfüllt**: Bis zur Entscheidung muss entweder der Impressum-Platzhalter ersetzt oder GitHub Pages
deaktiviert werden.

1. Das §-5-DDG-Impressum-Platzhalter (`[vor Veröffentlichung ergänzen: Name, Anschrift,
   Kontakt]`) ist im live ausgelieferten Stand enthalten und wird von `tests/verify-build.py`
   erzwungen. Eigene Angaben eintragen, nichts erfinden.
2. Repository frei von Heft-Fotos, Heft-Wortlaut und persönlichen Notizen halten.
3. Seiten-Cache-Hinweis: GitHub Pages erlaubt keine eigenen `Cache-Control`-Header. `sw.js`
   arbeitet cache-first; Rückkehrer können daher kurz einen alten Stand ziehen, bis der
   Worker aktualisiert.
4. Merge/Release nur, wenn du es willst – dieses Dokument ändert keine Einstellungen.