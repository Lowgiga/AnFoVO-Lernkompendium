# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/de/1.1.0/) – angepasst an dieses Projekt.
Versionsschema: MAJOR.MINOR.PATCH als `versionName`, dazu ein eigener `versionCode`.

## [Unveröffentlicht] – Arbeitsstand 16.11.2026

Korrekturen und Absicherung aus Phase 0 (Refactoring/Qualitätssicherung) vor Beginn von Phase 1.
Noch **kein** Versionssprung; die Build-Nummer bleibt 295 / 2.9.5.

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
- `BACKUP_2026_11_16_Phase1/` – 78 Dateien, 13,62 MB, mit `SHA256SUMS.txt`.
- `CHANGELOG.md`, `docs/TESTPROTOKOLL.md`, erweiterte `README-ANDROID.md` (Kodierungsfehler in
  Umlauten der alten Fassung dabei bereinigt).
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