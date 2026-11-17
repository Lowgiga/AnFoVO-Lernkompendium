# Testprotokoll – Lern-Kompendium § 8 AnFöVO NRW

Stand: 16.11.2026 · Bezug: v2.10.0 (versionCode 296) · Phase 0 (Refactoring/QS) **und** Phase 1
(Design-System + WCAG 2.2 AA) abgeschlossen; alle gemeldeten Defekte V1–V7 geschlossen.

## 1. Verifikationsgrundsatz

Ein erfolgreicher Build belegt nur die Kompilierbarkeit. Aussagefähig für die Qualität ist der
**app-eigene Funktionstest** (106 Prüfungen, Stand 2.10.0) im Browser plus ein Gerätelauf. Getrennt wird zwischen

- **verifizierten Fakten** (hier belegt) und
- **Schlussfolgerungen** (nicht selbst geprüft – im Text kenntlich gemacht).

## 2. Umgebung

| Zweck | Werkzeug |
|-------|----------|
| Java-Build | `C:\Tools\jdk-21\jdk-21.0.13+9` (JDK 21), Gradle 8.13 / AGP 8.13.2 |
| Android SDK | `C:\Android`, Platform 36, Build Tools 35.0.0 |
| Lokaler Webserver | `jwebserver.exe` (JDK 21), Ports 8099 (Vorlauf) bzw. 8096/8097/8094 (Läufe 2.10.0, frische Origins), Dokumentwurzel `app/src/main/assets` (absoluter Pfad, `-d` lehnt relative ab) |
| Browser | Chromium (Edge/Chrome) mit Entwicklerkonsole |
| Gerät | Samsung SM_S931B (echtes Gerät), `adb install -r`, `logcat`, `screencap` |
| Versionsverwaltung | `C:\Program Files\Git\cmd\git.exe` (nicht im PATH) |

## 3. Build-Nachweis

Zwei Aufbauten nachvollziehbar:

| Stand | APK | Bytes | SHA-256 |
|-------|-----|-------|---------|
| Baseline (vor den Korrekturen) | app-universal-debug | 4.264.711 | `9FE03490E0AA5D4C32B6B1043BE4D6CCDCF7E79D5F15AED0C36EF214F088E2B5` |
| nach Phase 0 + Assistent/Tests | app-universal-debug | 4.266.577 | `E3FFFEFAA61C1696B09E1EEC7CCFB961A45B217848A74D30FFD8D23AE7BDB482` |
| **2.10.0 (Phase-1-Abschluss)** | app-universal-debug | 4.284.397 | `575D6689E462671342B83D9182BDBC7690B07F858AE90E7FD541F79249507E78` |

Alle drei Varianten (`arm64-v8a`, `universal`, `x86_64`) tragen jeweils denselben Hash.
Größenzunahme +1.866 Bytes gegenüber der Baseline = wiederhergestellter CSS-Umfang,
die zusätzlichen Selbsttest-Helfer und die ausgelagerten Assistenten-Regeln.
Abweichung der Baseline zum Backup (CD02BC90…, 4.264.781 Bytes) geklärt: das frühere APK enthielt
zusätzlich die Datei `index.html.broken`; die ist entfernt.

**Integritätskontrolle nach jedem Build:** Die Dateien im Merge-Verzeichnis
(`app/build/intermediates/assets/debug/mergeDebugAssets/`) wurden per SHA-256 mit den Quellen
verglichen – `style.css`, `index.html`, `app.js`, `assistent.js` jeweils **identisch**. Die
Web-Assets im Paket entsprechen also dem geprüften Arbeitsstand.

**Zustandskontrolle 2.10.0 (weitergehend):** Zusätzlich zum Merge-Vergleich wurden **alle sieben
Text-Assets** aus dem fertigen APK entpackt und mit den Quellen verglichen – `index.html`,
`style.css`, `app.js`, `assistent.js`, `robot-navigation.js`, `sw.js`, `manifest.json` jeweils
**identisch**. `aapt2 dump badging` bestätigt `versionCode='296' versionName='2.10.0'`.

**Wiederholungsbau am 16.11.2026:** `.\build-debug.ps1` bzw. `.\gradlew.bat :app:assembleDebug`
meldet „34 up-to-date" – seit dem Bau `E3FFFEFA…` haben sich nur Dokumentation und das
Build-Skript geändert, die Quellen unter `app/src/main/assets/` sind unverändert. Die APK-Hashes
gelten daher unverändert weiter; der Selbsttest auf einem frischen Server (Port 8097) bestätigt
erneut **99 / 99**.

**Hinweis zur Zählung (Stand 2.10.0):** Die oben genannte 99/99-Messung bezieht sich auf den
Zwischenstand *vor* der Erweiterung des Selbsttest-Blocks. Der endgültige Stand (Commit
`2f34241`) enthält 7 zusätzliche Prüfungen (V1–V7) und ergibt **106 / 106**. Die Zählung
„99 / 99" bleibt als historischer Meilenstein (Phase 1, Assistent/Tests) dokumentiert.

**Build-Skript korrigiert:** `build-debug.ps1` verwies auf ein SDK-Verzeichnis und eine globale
Gradle-Installation (`gradle --version`, `gradle` ist auf diesem Rechner **nicht** im PATH) und
prüfte nur die APK `app-debug.apk`. Das Skript ermittelt jetzt JAVA_HOME und ANDROID_HOME
selbst (beide SDK-Pfade auf diesem Rechner sind vollständig; `local.properties` fehlt, daher
entscheidet `ANDROID_HOME`), baut über den Projekt-Wrapper `.\gradlew.bat`, prüft die Signatur
aller drei ABIs und vergleicht die Web-Assets zwischen Quelle und Merge-Verzeichnis.

## 4. Browser-Baseline

`http://localhost:8099/index.html` – geprüft nach Wiederherstellung von `style.css`:

- Konsolenfehler: **0** (einzige Meldungen: `navigator.vibrate` wird ohne Nutzer-Tap blockiert –
  das ist ein Chromium-Richtlinienhinweis, kein App-Fehler)
- `window.KOMP` aktiv: **54 Mitglieder** (53 im Objekt-Literal, `boot` ergänzt durch `init()`)
- Lernseiten: **70** (`article.page`) · Titel: „Lern-Kompendium § 8 AnFöVO NRW – v2.9.5"
- `window.RobotNav` vorhanden · Service Worker verfügbar
- Design-Token `--tap: 44px` greift (Nachweis für wirksames Styling)

## 5. Selbsttest – Ergebnis

Aufruf: `http://localhost:8099/index.html?test=1` (Query-Parameter nötig; ein reiner
`#selftest`-Hash lädt die Seite nicht neu).

| | Start | nach Phase 0 | nach Phase 1 (Assistent/Tests) | **nach 2.10.0 (Phase 1 abgeschlossen)** |
|---|---|---|---|---|
| bestanden | 82 / 99 | 95 / 99 | **99 / 99** | **106 / 106** |
| übersprungen | 1 | 1 | 1 | 1 |
| Fehlschläge | 18 | 4 | 0 | 0 |

Der Lauf vom 16.11.2026 erfolgte auf **frischen Origins** (jwebserver, Ports 8096, 8097 und
8094 – jeweils neuer Port, damit kein Service-Worker-Cache aus einem Vorlauf greift) – genau das
im Protokoll beschriebene Verfahren. Ergebnis (bei jedem der drei Läufe identisch):
**106 / 106 bestanden**, 1 übersprungen („Desktop: Kopfzeileninhalt auf 90ch begrenzt und
zentriert", nur bei Viewport ≥ 1200 px messbar). Konsolenmeldungen: nur der bekannte
Chromium-Hinweis auf `navigator.vibrate` ohne Nutzer-Tap (Richtlinienhinweis, kein App-Fehler).

Vergleich zulässig: Die 18 Altfehlschläge waren überwiegend eine Folge der CSS-Auslagerung
(Phase 0) – der Selbsttest suchte die Regeln im Inline-`<style>`, das es nicht mehr gab.

> **Wichtig für jede Wiederholung:** Der Service Worker arbeitet cache-first und matcht mit
> `ignoreSearch: true` – ein Cache-Buster wie `?nocache=…` greift **nicht** für die eingebundenen
> Dateien. Zusätzlich hält der Browser eine eigene HTTP-Ablage vor. Verlässliches Vorgehen:
> Service-Worker-Registrierungen aufheben, `caches.keys()` löschen, **und** die Seite von einem
> frischen Origin laden (im Protokoll: zweiter Server auf Port 8098). Sonst werden veraltete
> Dateien gemessen – genau dieses Fall führte zwischenzeitlich zu einem Scheinergebnis
> (95/99 statt 97/99), weil der SW die alte `assistent.js` lieferte.

### 5.1 Behobene Fehlschläge (18 → 0, dann 4 → 0)

Die CSS-abhängigen Prüfungen (Druckausgabe, Dark Mode, Fokus, Touch-Ziele, Animationen,
Kopfzeile, Abstände) nach Einführung von `cssSheets()`/`sheetText()` im Selbsttest-Block.
Ursache: reine Testschwäche, kein Produktivdefekt.

### 5.2 Die vier letzten Fehlschläge – Befunde, Einordnung, Korrektur

**(1) Touch-Ziele ≥ 44 × 44 px — echter Produktivdefekt, behoben**
Messwerte vorher: `#assistToggle` 106 × 26 px, `#assistSpeech` 101 × 26 px; `min-height: auto`,
`min-width: auto`. Quelle: der Inline-`<style>`-Block in `assistent.js`.
Wirkung: zwei dauerhaft sichtbare Schaltflächen unterschreiten das 44-px-Berührungsziel deutlich.
**Behoben:** Die Assistenten-Regeln liegen jetzt in `style.css` (P1-10) und die Schaltflächen
erhalten `min-height:var(--tap);min-width:var(--tap)`. Nachmessung: 101 × 44 px bei 800 px
Viewport, 106 × 44 px bei 360 px.

**(2) Speicher-Schlüssel ohne Präfix — echter Produktivdefekt, behoben**
`anfoevo_assistent` und `anfoevo_speech` folgten nicht dem Präfix `anfoevo_v2_`, das `app.js`
für alle übrigen Schlüssel verwendet. **Behoben:** neue Schlüssel
`anfoevo_v2_assistent` / `anfoevo_v2_speech` mit einmaliger Migration (`readKey()`): beim ersten
Zugriff wird der Alt-Schlüssel übernommen und entfernt. Nachweis im Browser: nur noch
`anfoevo_v2_*`-Schlüssel vorhanden, der übernommene Wert („aus") blieb erhalten.

**(3) Buttons-Schwelle im Selbsttest — Testspezifikum, korrigiert**
Zählung auf der Checkpoint-Seite: 38 Buttons im DOM, 0 in den Heftseiten (`#pages`),
**10 sichtbar** gegen eine Schwelle von 8. Die 10 = 8 Kernschaltflächen + 2 Assistenten-
Schaltflächen; bedingt kommen bis zu 3 PWA-Meldungen (Update, Install, Offline) hinzu. Der
Code-Kommentar nannte nur die PWA-Meldungen und war deshalb unvollständig.
**Korrigiert:** Schwelle 12, Kommentar im Test auf die tatsächliche Zusammensetzung
aktualisiert. Die Aussagekraft bleibt erhalten (v2.2-Startansicht: 212 sichtbare Buttons).

**(4) Druck-CSS-Erkennung — Testspezifikum, korrigiert**
Zwei Teilpunkte, beide reine Testschwächen:
- Chrome serialisiert `@page { size: a4; … }` klein; der Test prüfte `/A4/` case-sensitiv.
- Die CSSOM fasst `calc(6 * 1.45em + 1px)` zu `calc(8.7em + 1px)` zusammen
  (`.sitans .printval { min-height: calc(8.7em + 1px); }` in `@media print`), der
  Quelltext-Vergleich griff deshalb nicht.
**Korrigiert:** `/A4/i` in beiden Prüfungen und eine Altform-Tabelle für die `calc`-Angabe.
Das Druck-CSS selbst war durchgehend intakt – Kopf aus, Lösungen aus, `border-bottom`,
`break-inside`, Reihenfolge der Ausfüllseiten, `content: none` auf `.src a::after`.
*Anmerkung zum Vorgehen:* Ein Test, der korrektes Verhalten als Fehler meldet, ist selbst ein
Defekt, weil er echte Rückfälle überdeckt. Deswegen korrigiert statt nur dokumentiert.

### 5.3 Übersprungen (1)

„Desktop: Kopfzeileninhalt auf 90ch begrenzt und zentriert" – nur bei Viewport ≥ 1200 px
messbar; im Testausmaß 800 px übersprungen. Kein Defekt.

### 5.4 Zusätzlich behoben: Assistent auf dem Smartphone

Vorher blendete `assistent.js` die Blase bei ≤ 760 px **vollständig aus**
(`@media(max-width:760px){#assistBubble{display:none}}`) – auf dem Haupt-Android-Format war der
Assistent damit unerreichbar, einschließlich der Schalter für Assistent und Sprache.
Jetzt: die Regeln liegen in `style.css`, bei ≤ 760 px wird die Blase am Safe-Area-Rand
unten verankert (`left/right: var(--s2)`, `bottom: calc(var(--s2) + env(safe-area-inset-bottom))`,
volle Breite) und die Blase selbst ist `pointer-events:none`, nur die Schaltflächen sind
anklickbar – sie verdeckt keine Bedienung. Messung in einem 360-px-Iframe:
`display: block`, `visibility: visible`, linke Kante 8 px, Breite 329 px, also voll im Bild.
Zusätzlich ist `#assistBubble` in die bestehende Druckregel
(`#object-stage,#assistBubble,#robot-nav-debug{display:none!important}`) aufgenommen, damit die
Blende nicht auf dem A4-Arbeitsblatt landet.

### 5.5 Neu in 2.10.0 (Phase-1-Abschluss): sieben zusätzliche Prüfungen

1. **Offline-Kern** – `sw.js` nennt `./style.css` und `./app.js` im Cache-Kern (V1). Gemessen
   wird der ausgelieferte `sw.js`-Text (synchrones XMLHttpRequest; nur über http(s) prüfbar,
   sonst übersprungen).
2. **Startbild-Farbe** – `manifest.json` `background_color` = Licht-Token `--bg` (`#f4eee3`),
   `theme_color` = `--hdr` (V2).
3. **Versionsgleichheit** – `DATA.version` = Manifest-Version = Titel-Kennung (V4); alle drei
   stehen auf `2.10.0`.
4. **`window.KOMP`** – genau eine Zuweisung, 53 Mitglieder + `boot` = 54, kein Name gegenüber
   `docs/api-snapshot.txt` entfernt (V7). Der Test prüft namentlich alle 53 Vergleichsnamen.
5. **Darstellung** – der Menüknopf cycling Automatik → Hell → Dunkel → Automatik; `data-theme`
   schaltet die Token wirksam um (`--bg`: `#f4eee3` hell / `#14181d` dunkel); die dunkle Regel
   liegt in `@media screen` (Druck bleibt hell); `forced-colors`-Regel vorhanden; die Wahl wird
   in `S.prefs.theme` gespeichert (mit Sicherung wandernd).
6. **Kontrast-Wächter** – 13 Text-Tokenpaare, je in Automatik, Hell und Dunkel ≥ 4,5:1.
   *Hinweis zum Messverfahren:* die erste Fassung maß über Inline-`var()` und ergab in der
   Prüfumgebung transparente Hintergründe (ein Pseudomesswert von 1,00 bei `#000/--mark` deckte
   das auf). Gemessen werden jetzt die **aufgelösten** Token-Werte – alle 39 Messungen bestehen.
7. **Skip-Link** – erstes Element der Seite, Ziel `#maincontent`, `:focus`-Regel mit
   Positionswechsel vorhanden.

Zusätzlich verifiziert (nicht als Prüfung, sondern im Browser-Lauf): die Darstellungswahl
übersteht ein Neuladen (lokaler Speicher), `meta name="theme-color"` folgt der Wahl
(`#14181d` in Dunkel).

## 6. Prüfsummen (Stand 2.10.0, 16.11.2026)

| Datei | Bytes | SHA-256 |
|-------|-------|---------|
| `assets/index.html` | 496.759 | `3CF879A1E3A93D7D97B7CA707BE49968DB3248493E58563B25BA99612850DAD3` |
| `assets/style.css` | 59.542 | `7BD0C7691A1CA50019210ADDF5A21F212014CF268A02ABC491A717F60442E43A` |
| `assets/app.js` | 83.325 | `E282D0F717A6608852CBBB00A07D9BD45500D686C6BC455179DE6DF7E0443C93` |
| `assets/assistent.js` | 9.177 | `80553AF403FE4327F46812A0B0345B36110DB239DAB1C7DA0F4013687919D79D` |
| `assets/robot-navigation.js` | 22.263 | `A9424CABE94BD87B17B5DB67D9F42CC72DDD060F6BC7871E95772B1208DEA057` |
| `assets/sw.js` | 2.731 | `BA49470A0EAA975EAE7B1A94A7226FDCC72D6EFF7E4E31C09E6A5BAD372630AA` |
| `assets/manifest.json` | 775 | `29A984DAF209E3B0554CD303E00862669D5B97CA12074339DB6E1386E515D574` |

**API-Regressionskontrolle:** `window.KOMP` weiterhin **54 Mitglieder** (53 im Objekt-Literal +
`boot` aus `init()`), `window.RobotNav` vorhanden, 70 Lernseiten. Kein Mitglied entfernt oder
umbenannt – Vergleichsbasis `docs/api-snapshot.txt`. Die Konsole des Browser-Laufs meldet
`Object.keys(window.KOMP).length === 54`.

Vorher-Stände in `backups/2026-11-16_phase1/SHA256SUMS.txt` (78 Dateien, 13,62 MB) und
`backups/2026-11-16_abschluss/SHA256SUMS.txt` (94 Dateien, Stand vor 2.10.0); der älteste
Stand (vor Phase 0) liegt in `backups/2026-11-16_phase0/`.

## 7. Noch offene Arbeitspunkte (Stand 2.10.0)

1. **Gerätelauf auf SM_S931B** (Install, `logcat`, `screencap`): Derzeit nicht ausführbar.
   `adb devices` zeigt kein Gerät, obwohl Windows das Telefon sieht
   („SAMSUNG Android ADB Interface", Treiber 2.21.4.0) – Status „Unknown", ohne Problemcode.
   Das ist der typische Zustand eines gesperrten/bildschirmlosen Telefons oder einer nicht
   bestätigten USB-Debugging-Abfrage; das lässt sich nur am Gerät selbst beheben
   (Bildschirm entsperren, USB-Debugging-Abfrage bestätigen, evtl. Kabel neu anstecken).
   Alle übrigen Nachweise (Build, Selbsttest, Browser-Messungen) sind erbracht.
2. **Phase 2 (→ 2.11.0):** Lern-Assistent – Fahrplan in `README.md` Abschnitt 11. Kein
   Code-Defekt, sondern die nächste Leistungsbeschreibung.
3. Die Punkte V1–V7 aus `README.md` Abschnitt 10 sind **alle geschlossen** (siehe 5.5);
   die Design-Token bewusst in `style.css` belassen (Begründung im Arbeitsplan
   `docs/ARBEITSPLAN-2.10.0.md`).