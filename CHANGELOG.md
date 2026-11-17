# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/de/1.1.0/) – angepasst an dieses Projekt.
Versionsschema: MAJOR.MINOR.PATCH als `versionName`, dazu ein eigener `versionCode`.

## [2.10.0] – versionCode 296 (Phase 1 abgeschlossen: Design-System + WCAG 2.2 AA)

*Auslieferungsstand 16.11.2026. Build: `.\build-debug.ps1` → drei ABIs, je 4.284.397 Bytes,
SHA256 `575D6689E462671342B83D9182BDBC7690B07F858AE90E7FD541F79249507E78`, Signatur OK;
Assets im Paket identisch mit den Quellen (Entpack-Vergleich). Selbsttest: 106/106 bestanden,
1 übersprungen.
Dieser Eintrag nimmt den unten stehenden Arbeitsstand „[Unveröffentlicht]" (Repository/Build-Skript)
mit auf – er ist erstmals Teil einer ausgelieferten Version.*

### Darstellung: Automatik / Hell / Dunkel

- **Manuelle Umschaltung** unter „☰ Mehr → 🌗 Darstellung" (Automatik → Hell → Dunkel →
  Automatik). Vorher folgte die App nur dem System (`prefers-color-scheme`); jetzt lässt sich
  Hell oder Dunkel dauerhaft wählen. Die Wahl liegt in `S.prefs.theme` und reist mit der Sicherung
  (Sicherung speichern/laden) mit.
- **`style.css`:** die dunklen Token zusätzlich als eigene Regel `:root[data-theme="dunkel"]`
  (in `@media screen`, damit der Druck hell bleibt); die beiden System-Dunkel-Regeln sind auf
  `:not([data-theme="hell"])` geschrieben, eine manuelle Hell-Wahl gewinnt also gegen einen
  dunklen Systemmodus. Die Druck-Regel wurde auf `html:root,html:root[data-theme]` angehoben,
  damit Druck auch bei manuellem Dunkel hell bleibt.
- **Kein Farblitz:** ein kurzes Skript im `<head>` setzt die gespeicherte Wahl vor dem ersten
  Stil-Aufbringen; ohne Speicher (z. B. `file://`) fällt es auf Automatik zurück.
- **`meta name="theme-color"`** folgt jetzt ebenfalls der Wahl (hell `#294b3d`, dunkel `#14181d`).

### Windows-Hohe-Kontraste (forced-colors)

- `@media (forced-colors:active)`: Token auf Systemfarben (Canvas/CanvasText/LinkText/
  ButtonFace/ButtonText/Highlight), dekorative 3D-Szene und Hintergrund ausgeblendet.
  Das README hatte diese Verträglichkeit bisher ohne Grundlage behauptet – sie existiert jetzt.

### Kontrast-Wächter (neuer Selbsttest)

- 13 Text-Tokenpaare (u. a. `--ink/--bg`, `--btnfg/--btnbg`, `--accfg/--acc`, `--warnfg/--warnbg`,
  `--ok/--okbg`, `--red/--redbg`, `--brand/--card`, `#fff/--hdr`, `#000/--mark`) werden in
  **Automatik, Hell und Dunkel** gemessen und müssen ≥ 4,5:1 bleiben. Gemessen werden diesmal
  aufgelöste Token-Werte – die frühere Messung über Inline-`var()` war unzuverlässig.

### Defekte geschlossen (V1–V7 – aus README Abschnitt 10)

- **V1 – Offline-Kern unvollständig:** `sw.js` nimmt jetzt `./style.css` und `./app.js` in den
  Cache-Kern auf. Folgefehler behoben: Nach dem ersten Start lieferte der Service Worker
  cache-first alte Stile und alte Logik aus. Cache-Version auf 2.10.0 gezogen
  (`anfoevo_v2_cache_2.10.0-web-pwa-2.10.0`).
- **V2 – Startbild-Farbe:** `manifest.json background_color` ist jetzt `#f4eee3` (= Token
  `--bg`, hell), vorher `#f5f6f7`. `theme_color` blieb `#294b3d` (= `--hdr`). Beides wird vom
  Selbsttest überwacht.
- **V4 – Versionsangabe:** `DATA.version` ist jetzt `"2.10.0"` (vorher `"2.7.0"`); der Selbsttest
  vergleicht DATA-, Manifest- und Titel-Version auf Gleichheit.
- **V7 – `window.KOMP` doppelt gesetzt:** Ein einziges `var API = {…}` entsteht vor `init()`,
  `init()` hängt nur noch `boot` an dieselbe Instanz; `window.KOMP = API` wird genau einmal
  zugewiesen. Unverändert: 53 Mitglieder + `boot` = 54 – kein Name entfernt oder umbenannt
  (Vergleich `docs/api-snapshot.txt`, nun als Selbsttest hinterlegt).

### Selbsttest: 99 → 106 Prüfungen

Neu: Offline-Kern (V1), Manifest-Farbe (V2), Versionsgleichheit (V4), `window.KOMP`-Schnittstelle
(V7), Darstellungsumschaltung mit Token-Wirkung, Kontrast-Wächter, Skip-Link. Alle bisherigen
99 Prüfungen bleiben unverändert und grün.

### Version 2.10.0 / versionCode 296

`app/build.gradle`, `index.html` (Titel, Fußzeile), `app.js` (`DATA.version`), `sw.js`
(VERSION/BUILD), `manifest.json` – alle Versionsangaben abgeglichen.

### Aufgeräumt

- **Repository logisch strukturiert:** die drei Sicherungsordner liegen jetzt unter einem
  gemeinsamen `backups/` (`2026-11-16_phase0/`, `2026-11-16_phase1/`, `2026-11-16_abschluss/` –
  nicht versioniert, jeweils mit `SHA256SUMS.txt`); `.gitignore` ignoriert `backups/`. Das
  Wurzelverzeichnis enthält jetzt nur noch Quellen, Build-Konfiguration, README/CHANGELOG und
  `docs/`.
- Menüknopf „🌗 Darstellung: Automatik" ergänzt (im Mehr-Menü, 44-px-Berührungsziel wie alle
  `.mi`).
- **BOM in `sw.js` entfernt** – die Datei begann mit einem UTF-8-BOM und verstoß damit gegen
  die eigene Regel „UTF-8 ohne BOM" (README Abschnitt 2). Fund aus dem Dokument-Abgleich
  vom 16.11.2026; die Regel gilt jetzt für alle Textdateien.
- **`docs/api-snapshot.txt` korrigiert:** 68 → **79** Token-Namen (elf zur Laufzeit gesetzte
  Eigenschaften – `--navh`, `--dir/--turn`, `--robot-nav-*` – fehlten in der Liste);
  `:root`-Zeilenreferenzen auf den Stand 2.10.0 gebracht.
- **`README.md` korrigiert:** Installation nennt jetzt den echten Dateinamen
  `app-universal-debug.apk` (vorher `app-debug.apk`, die es nicht gibt); Dateizahl 94 → 95;
  „geprüftes Zielgerät" → „Zielgerät" (Gerätelauf derzeit nicht ausführbar, s. TESTPROTOKOLL
  Abschnitt 7).
- `docs/ARBEITSPLAN-2.10.0.md` – Plan und Abstimmung des Phase-1-Abschlusses.
- `backups/2026-11-16_abschluss/` – 94 Dateien mit `SHA256SUMS.txt` vor den Änderungen.
- Web-Deployment vorbereitet (Commit `632cb94` … `f5e62c8`): `vercel.json` (Output
  `app/src/main/assets`, SW/Manifest `max-age=0`), `docs/VERCEL-DEPLOY.md`,
  Unix-`gradlew`, `packagingOptions`-Ausschluss für `.vercel`/`.env*` (Token-Leak-Fix),
  `.gitignore`-Härtung (Keystore/Secrets).

### Bekannt, noch offen (kein Code-Defekt)

- **G1 – Gerätelauf** auf SM_S931B: `adb devices` zeigt derzeit kein Gerät (USB-Debugging am
  Telefon bestätigen). Build, Selbsttest und Browser-Messungen sind erbracht.
- **G2 – Phase 2 (→ 2.11.0):** Lern-Assistent, Fahrplan in README Abschnitt 11.
- **G3 – Impressum-Platzhalter** in the App-Fußzeile (Anbieterangaben nach § 5 DDG): persönliche
  Angaben, nur vom Betreiber ausfüllbar – vor einer Veröffentlickeitung zu ergänzen.

---

## [Unveröffentlicht] – Arbeitsstand 16.11.2026

### Repository in Ordnung gebracht (16.11.2026)

- **Branch umbenannt** `master` → `main` (GitHub-Konvention; rein lokal, kein Remote).
- **`README-ANDROID.md` → `README.md`** umbenannt: GitHub zeigt standardmäßig `README.md` an, und
  der Inhalt beschreibt inzwischen das ganze Repository, nicht nur die Android-Hülle. Querverweise
  in `CHANGELOG.md` und `docs/TESTPROTOKOLL.md` angepasst.
- **`build-debug.ps1` korrigiert:** Das Skript verlangte eine globale Gradle-Installation
  (`gradle` ist auf diesem Rechner nicht im PATH), prüfte nur die APK `app-debug.apk` und
  hinterließ JAVA_HOME/SDK undokumentiert. Es ermittelt jetzt beides selbst, baut über den
  Projekt-Wrapper `.\gradlew.bat`, prüft die Signatur aller drei ABIs und vergleicht die
  Web-Assets zwischen Quelle und Merge-Verzeichnis – genau das nachgewiesen funktionierende
  Verfahren.
- **GitHub-Anbindung hergestellt (16.11.2026).** Remote `origin` =
  `https://github.com/Lowgiga/AnFoVO-Lernkompendium.git`. Das dortige `main` tragt eine
  **getrennte Historie** (Standalone-PWA-Variante mit eigener Versionslinie bis v2.9.5 und
  eigenen Tags `v2.9.2`/`v2.9.4`); ein Überschreiben wäre Datenverlust gewesen. Deshalb liegt
  der lokale Stand vollständig auf dem Branch **`android-wrapper-2.10.0`** (HEAD `21add01`),
  Tags `v2.10.0` und `v2.9.5-baseline` sind mitgepusht. Die Entscheidung über die
  Zusammenführung (Pull-Request oder Force-Push) bleibt beim Betreiber.

Korrekturen und Absicherung aus Phase 0 (Refactoring/Qualitätssicherung) vor Beginn von Phase 1.
Dieser Arbeitsstand ist ab **[2.10.0]** (versionCode 296) ausgeliefert – der Eintrag dort
beschreibt den Gesamtstand.

### Behoben

- **`style.css` wiederhergestellt.** Die Datei war ab dem Zeichen ` --acc:#9e4626;` beschnitten:
  das öffnende `:root{` und die Token-Definitionen (Farben, Abstände, Radien, `--tap: 44px`,
  `color-scheme`), der `.skiplink`-Block und die zugehörigen `@keyframes` fehlten, am Ende stand
  ein `</style>`-Artefakt. Folge: **alle** Design-Tokens waren wirkungslos – die App lief ohne
  Farben, Abstände und Touch-Größen. Wiederherstellung aus der einzigen intakten Quelle
  (`app/build/intermediates/assets/release/mergeReleaseAssets/index.html`, Stand 14.11.2026).
  Prüfsumme: `9218E0794D784DA005B3F0290825BA5AC76D5F451FB26FFCE789C7CBEDB1C639`.
- **`app.js` geprüft: verlustfrei.** Zeilenweiser Vergleich mit dem Original ergab nur eine
  abweichende Zeile (Versionskommentar v2.9.4 → v2.9.5). Keine inhaltliche Änderung nötig.
- **Selbsttest-Harness repariert.** Der Funktionstest las CSS-Regeln ausschließlich über
  `$$('style')`; seit der Auslagerung von Styling und Logik in externe Dateien gibt es im
  Dokument kein Inline-`<style>` mehr. 19 CSS-abhängige Prüfungen meldeten deshalb fälschlich
  „fehlt". Neu: `cssSheets()` liest `document.styleSheets` (auch externe Blätter),
  `sheetText()` liefert den CSS-Rohtext. Ergebnis: 82/99 → **95/99**.

### Phase 1 (begonnen): Assistent und Selbsttest korrigiert

- **Berührungsziele (WCAG 2.2):** Die Schaltflächen `#assistToggle` und `#assistSpeech` maßen
  106 × 26 px bzw. 101 × 26 px. Sie erhalten jetzt `min-height/min-width: var(--tap)` (44 px) –
  Nachmessung 101 × 44 px bei 800 px, 106 × 44 px bei 360 px.
- **Speicherschlüssel auf das gemeinsame Präfix umgestellt:** `anfoevo_assistent` und
  `anfoevo_speech` heißen jetzt `anfoevo_v2_assistent` und `anfoevo_v2_speech`. Beim ersten
  Zugriff wird der Alt-Schlüssel übernommen und entfernt (`readKey()`); gespeicherte
  Einstellungen bleiben erhalten.
- **Assistent auf dem Smartphone erreichbar:** Die Blase wurde bei ≤ 760 px vollständig
  ausgeblendet – auf dem Haupt-Android-Format waren Assistent und beide Schalter nicht
  erreichbar. Jetzt wird sie bei ≤ 760 px am Safe-Area-Rand unten verankert, nimmt die volle
  Breite ein und ist als Fläche `pointer-events:none`, sodass sie keine Bedienung verdeckt.
  Beim Druck ist sie ausgeschaltet (`#object-stage,#assistBubble,#robot-nav-debug`).
- **Inline-CSS ausgelagert:** Der `<style>`-Block, den `assistent.js` zur Laufzeit injizierte,
  liegt jetzt in `style.css`. Damit gibt es nur noch eine Stilquelle; der Selbsttest und das
  Design-System sehen die Regeln. `assistent.js` damit von 10.104 auf 9.177 Byte geschrumpft.
- **Zwei falsch negative Testangaben korrigiert** (ein Test, der korrektes Verhalten als Fehler
  meldet, überdeckt echte Rückfälle): die Button-Schwelle von 8 auf 12 angehoben und kommentiert
  (8 Kernschaltflächen + 2 Druck + 2 Assistent + bis zu 3 PWA-Meldungen); die `@page`-Erkennung
  case-insensitiv (Chrome schreibt `size: a4` klein) und die `calc(6 * 1.45em + 1px)`-Prüfung
  akzeptiert die von der CSSOM zusammengefasste Form `calc(8.7em + 1px)`.
- **Ergebnis: 99 / 99 Selbsttests bestanden**, 1 übersprungen (nur bei Viewport ≥ 1200 px
  messbar). `window.KOMP` unverändert mit 54 Mitgliedern.

### Hinzugefügt

- `docs/api-snapshot.txt` – Baseline des `window.KOMP`-Exports (53 Mitglieder im Objekt-Literal;
  `boot` wird zur Laufzeit ergänzt, live 54), 68 CSS-Token-Namen, localStorage-Schlüssel.
  Vergleichsbasis für spätere Regressionsprüfungen.
- `backups/2026-11-16_phase1/` – 78 Dateien, 13,62 MB, mit `SHA256SUMS.txt`.
- `CHANGELOG.md`, `docs/TESTPROTOKOLL.md`, erweiterte `README.md` (Kodierungsfehler in Umlauten
  der alten Fassung dabei bereinigt; die Datei hieß vorher `README-ANDROID.md`).
- Git-Repository mit Baseline-Commit `1637bb5` und Tag `v2.9.5-baseline`; `.gitignore` für
  `build/`, `*.apk`, `local.properties`, `BACKUP_*/`.
- **Repository bereinigt:** `.gitignore` war in der Baseline versehentlich nicht angelegt
  worden – verfolgt waren 1058 Dateien aus `app/build/`, 96 aus den beiden Backup-Ordnern,
  15 aus `.gradle/` und 12 APK-Dateien. Verfolgung aufgehoben (nicht destruktiv: alle Dateien
  bleiben auf der Platte; die Blöcke stehen weiter in der Historie). Danach 94 versionierte
  Dateien statt 1263 – nur noch Quellen und Dokumentation.

### Bekannt, noch offen

Vier Selbsttest-Fehlerläufe sind **reale** Befunde, keine Testschwächen im Detail (siehe
`docs/TESTPROTOKOLL.md`): Berührungsziele des Assistenten (26 px), Speicherschlüssel
`anfoevo_assistent` ohne Präfix, Schwelle der Button-Zählung im Selbsttest, `@page`-Erkennung
nach der CSS-Auslagerung. Behandlung in Phase 1 / W6.

---

## [2.9.5] – versionCode 295 (ausgeliefert)

*Dieser Eintrag wurde aus dem Code-Stand zusammengetragen (Quellen: Versionsangaben in
`app/build.gradle`, `index.html`-Titel, Code-Kommentare in `app.js`); es liegt keine gepflegte
Änderungshistorie vor. Angaben ohne eigene Prüfung sind als Schlussfolgerung zu lesen.*

- Version `2.9.5`, `versionCode 295`, `applicationId de.omega.lernkompendium`, minSdk 29,
  targetSdk/compileSdk 36.
- PWA-Erweiterungen (Update-Toast, Install-Hinweis, Offline-Banner, Tastaturkurzbefehle,
  History-Behandlung) – laut Code-Kommentar „PWA-Erweiterungen v2.9.5" in `app.js`.
- Assistent mit Blase, Umschalter und Sprachdialog (`assistent.js`).
- Adaptive 3D-Navigation `RobotNav` (`robot-navigation.js`, v2.8.0).
- 70 Lernseiten mit Zuordnung zum Kursheft, Lückentexten, Lösungen, Quellenzeilen,
  Abschlusstests und A4-Druckausgabe.