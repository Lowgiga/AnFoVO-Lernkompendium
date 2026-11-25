# GitHub Pages

**Stand: 25.11.2026 – verifiziert (Live-Abruf nach Deployment von `7820a49`).** GitHub Pages
ist für dieses Repository **aktiv** und liefert die Web-App aus:

- Projekt-Site: `https://lowgiga.github.io/AnFoVO-Lernkompendium/` (Antwort 200, Titel
  „Lern-Kompendium § 8 AnFöVO NRW – v2.9.5", 70 Lernseiten, PWA installierbar).
- Für den Impressum-Stand verifizierter Deployment-Commit:
  `7820a492bc30fbb83e59bd2c1ea4cd321d232da2`; Pages-Lauf `45629740818` und
  Projektvalidierung `45629742055` erfolgreich.

## Was heute wirklich published wird (wichtig)

Veröffentlicht wird der **Branch-Root von `main`**, nicht der bereinigte Surface. Verifiziert
öffentlich abrufbar sind daher auch:

- `android/README-ANDROID.md` (Quellcode-Hinweise der WebView-Hülle)
- `tests/verify-build.py` (Test-Quellcode)
- `TESTBERICHT_v2.9.5.txt`, `SHA256SUMS_*`, `BUILD-REPORT-*`
- `gradle/wrapper/gradle-wrapper.jar`

Der Abruf ist harmlos (keine Secrets im Repo, Signing nur über Umgebungsvariablen), aber es
ist **nicht** die beabsichtigte Veröffentlichungsfläche. `scripts/prepare-pages-surface.sh`
bereitet genau diese bereinigte Fläche (`dist/pages/`) vor – ihre Ausgabe wird derzeit von
**keiner** Automation konsumiert.

**Live vs. Repository:** Der Drift vom 17.11.2026 ist behoben. Der direkte Abruf der Live-Seite
liefert `index.html` mit 629.155 Bytes und SHA-256
`826c85e98ce08e070b15494318368999a111e58bc77777786fbaa146bdd371cb`; das entspricht exakt dem
kanonischen Git-Blob aus `main`-Commit `7820a49`. Ein Windows-Checkout mit
`core.autocrlf=true` kann wegen CRLF größere lokale Bytezahlen anzeigen; Linux-CI, APK und
GitHub Pages verwenden denselben LF-Blob.

## Bereit auf diesem Branch

- `index.html` linkt `./manifest.json`, `./icon-192.png` und ein Apple-Touch-Icon.
- `manifest.json` nutzt relative `start_url`/`scope` (`./`), die Installation bleibt im
  Projekt-Unterpfad.
- `sw.js` precacht die Hülle, Icons, `robot-navigation.js` und beide `bg/d`- and `bg/m`-
  Bilddateien; Cache-Name `anfoevo_v2_cache_2.9.5-web-pwa-2.9.5-legal.1`.
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

`scripts/prepare-pages-surface.sh` kopiert nur die Web-Hülle nach `dist/pages/` (gitignored):

- `index.html`, `manifest.json`, `sw.js`, **`robot-navigation.js`**
- `icon-192.png`, `icon-512.png`, `icon-512-maskable.png`
- `bg/`
- `.nojekyll`
- `LICENSE`
- `IMPRESSUM.md`

(Die Liste war unvollständig: `robot-navigation.js` wird seit dem Skript kopiert und von
`sw.js` precached, war aber nicht dokumentiert.)

Das Skript nimmt ein Ziel nur unter `dist/` oder außerhalb des Repos an, löscht das Repository
nie und ersetzt ein Ziel nur bei vorhandenem `.pages-surface`-Marker. Es ändert keine
Repository-Einstellungen. Wer die bereinigte Fläche live schalten will, stellt die
Pages-Quelle in den Repository-Einstellungen auf „GitHub Actions" und ergänzt einen Deploy-
Workflow (Skript → `actions/upload-pages-artifact` → `actions/deploy-pages`); dann fallen
`android/`, `tests/`, Gradle-Wrapper und die Berichte aus dem öffentlichen Angebot heraus.

## Technisches Veröffentlichungsgate – erfüllt; rechtliche Identität/Anschrift offen (25.11.2026)

GitHub Pages bleibt öffentlich erreichbar. Das technische Impressum-Gate ist geschlossen und live
geprüft. Die automatisierten Nachweise bestätigen Veröffentlichung und Konsistenz der gelieferten
Angaben, nicht deren rechtliche Vollständigkeit:

1. `index.html` enthält die konfigurierten Anbieterangaben direkt in der Fußzeile; `IMPRESSUM.md`
   dokumentiert dieselben Angaben als eigenständige Datei. Der frühere sichtbare
   Veröffentlichungs-Platzhalter wurde entfernt.
2. `tests/verify-build.py` verlangt Name, Anschrift, Kontakt-E-Mail sowie unterstützte Inline-HTML-
   und Inline-Markdown-Kontaktlinks in beiden Dokumenten. Das `mailto:`-Ziel muss exakt dem konfigurierten
   Ziel entsprechen, und das sichtbare E-Mail-Label wird whitespace-normalisiert geprüft; Links in
   Kommentaren, Codeblöcken, `<pre>`-, Script-, Template- oder Textarea-Inhalten sowie in
   `hidden`-Anchors zählen nicht. GFM-Autolinks und Reference-Links sind bewusst nicht Teil des
   unterstützten Scopes und zählen nicht. Der Regressionstest
   `test_impressum_requires_provider_details` mutiert Platzhalter, Name, Anschrift, Linkziel,
   Link-Markup und verborgene Linkquellen unabhängig voneinander.
3. Direkter Live-Abruf nach Pages-Lauf `45629740818`: `index.html` antwortet mit HTTP 200,
   629.155 Bytes und SHA-256
   `826c85e98ce08e070b15494318368999a111e58bc77777786fbaa146bdd371cb`; `IMPRESSUM.md` und `sw.js`
   antworten ebenfalls mit HTTP 200 und enthalten dieselben Angaben bzw. den Cache-Namen
   `web-pwa-2.9.5-legal.1`.
4. Browser-Prüfung der Live-Seite: 70 Lernseiten, kein sichtbarer Veröffentlichungs-Platzhalter,
   sichtbare Angaben „Lowgiga“, „New York 11354 USA“ und „Vid80gmx@gmail.com“ sowie ein funktionierendes
   natives `mailto:`-Ziel.
5. `index.html` und `android/app/src/main/assets/index.html` bleiben byte-identisch; auch die im
   CI-Artefakt `AnFoeVO-debug-apks` verpackte `assets/index.html` und die Live-Datei haben denselben
   SHA-256-Wert. Der In-App-Selbsttest prüft die sichtbaren Angaben und den Kontakt-Link zusätzlich
   zur Laufzeit.
6. Die rechtliche Identität, Vollständigkeit der Anschrift sowie gegebenenfalls Rechtsform und
   Vertretungsberechtigung bleiben eine separate Owner-Bestätigung; automatisierte String- und
   Linkprüfungen können diese rechtliche Frage nicht ersetzen.
7. Repository frei von Heft-Fotos, Heft-Wortlaut und persönlichen Notizen halten.
8. Seiten-Cache-Hinweis: GitHub Pages erlaubt keine eigenen `Cache-Control`-Header. `sw.js`
   arbeitet cache-first; Rückkehrer können daher kurz einen alten Stand ziehen, bis der
   Worker aktualisiert.
