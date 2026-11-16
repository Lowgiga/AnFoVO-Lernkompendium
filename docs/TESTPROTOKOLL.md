# Testprotokoll – Lern-Kompendium § 8 AnFöVO NRW

Stand: 16.11.2026 · Bezug: v2.9.5 (versionCode 295) · Phase 0 (Refactoring/QS) abgeschlossen,
Phase 1 noch nicht begonnen.

## 1. Verifikationsgrundsatz

Ein erfolgreicher Build belegt nur die Kompilierbarkeit. Aussagefähig für die Qualität ist der
**app-eigene Funktionstest** (99 Prüfungen) im Browser plus ein Gerätelauf. Getrennt wird zwischen

- **verifizierten Fakten** (hier belegt) und
- **Schlussfolgerungen** (nicht selbst geprüft – im Text kenntlich gemacht).

## 2. Umgebung

| Zweck | Werkzeug |
|-------|----------|
| Java-Build | `C:\Tools\jdk-21\jdk-21.0.13+9` (JDK 21), Gradle 8.13 / AGP 8.13.2 |
| Android SDK | `C:\Android`, Platform 36, Build Tools 35.0.0 |
| Lokaler Webserver | `jwebserver.exe` (JDK 21), Port 8099, Dokumentwurzel `app/src/main/assets` |
| Browser | Chromium (Edge/Chrome) mit Entwicklerkonsole |
| Gerät | Samsung SM_S931B (echtes Gerät), `adb install -r`, `logcat`, `screencap` |
| Versionsverwaltung | `C:\Program Files\Git\cmd\git.exe` (nicht im PATH) |

## 3. Build-Nachweis

Zwei Aufbauten nachvollziehbar:

| Stand | APK | Bytes | SHA-256 |
|-------|-----|-------|---------|
| Baseline (vor den Korrekturen) | app-universal-debug | 4.264.711 | `9FE03490E0AA5D4C32B6B1043BE4D6CCDCF7E79D5F15AED0C36EF214F088E2B5` |
| nach Phase 0 + Assistent/Tests | app-universal-debug | 4.266.577 | `E3FFFEFAA61C1696B09E1EEC7CCFB961A45B217848A74D30FFD8D23AE7BDB482` |

Alle drei Varianten (`arm64-v8a`, `universal`, `x86_64`) tragen jeweils denselben Hash.
Größenzunahme +1.866 Bytes gegenüber der Baseline = wiederhergestellter CSS-Umfang,
die zusätzlichen Selbsttest-Helfer und die ausgelagerten Assistenten-Regeln.
Abweichung der Baseline zum Backup (CD02BC90…, 4.264.781 Bytes) geklärt: das frühere APK enthielt
zusätzlich die Datei `index.html.broken`; die ist entfernt.

**Integritätskontrolle nach jedem Build:** Die Dateien im Merge-Verzeichnis
(`app/build/intermediates/assets/debug/mergeDebugAssets/`) wurden per SHA-256 mit den Quellen
verglichen – `style.css`, `index.html`, `app.js`, `assistent.js` jeweils **identisch**. Die
Web-Assets im Paket entsprechen also dem geprüften Arbeitsstand.

**Wiederholungsbau am 16.11.2026:** `.\build-debug.ps1` bzw. `.\gradlew.bat :app:assembleDebug`
meldet „34 up-to-date" – seit dem Bau `E3FFFEFA…` haben sich nur Dokumentation und das
Build-Skript geändert, die Quellen unter `app/src/main/assets/` sind unverändert. Die APK-Hashes
gelten daher unverändert weiter; der Selbsttest auf einem frischen Server (Port 8097) bestätigt
erneut **99 / 99**.

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

| | Start | nach Phase 0 | nach Phase 1 (Assistent/Tests) |
|---|---|---|---|
| bestanden | 82 / 99 | 95 / 99 | **99 / 99** |
| übersprungen | 1 | 1 | 1 |
| Fehlschläge | 18 | 4 | 0 |

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

## 6. Prüfsummen (Stand nach Phase-0- und Assistenten-Korrekturen)

| Datei | Bytes | SHA-256 |
|-------|-------|---------|
| `assets/index.html` | 490.523 | `803B8A09E639A000C0A36B02C4949C39CC3A644701EEE07754AFA2D6AAD2137D` |
| `assets/style.css` | 57.685 | `AA23E2664970A112EE8FBBA937617B21218C73EC0CA40979E070C57E9655D05B` |
| `assets/app.js` | 81.625 | `A98DBB2BECBC98DE64EA155E1104371BEA07130BB224A0D6AB2A7254B22DBC5F` |
| `assets/assistent.js` | 9.177 | `80553AF403FE4327F46812A0B0345B36110DB239DAB1C7DA0F4013687919D79D` |
| `assets/robot-navigation.js` | 22.263 | `A9424CABE94BD87B17B5DB67D9F42CC72DDD060F6BC7871E95772B1208DEA057` |
| `assets/sw.js` | 2.555 | `32F5F7D318039F97FE3F1F6C473C63F86EC76910921861816F5BA641F5528DBC` |
| `assets/manifest.json` | 774 | `C7947A54C6D934900D3B4D1E5D801ACD287F3B8106624EA8E274315A03DEB85E` |

**API-Regressionskontrolle:** `window.KOMP` weiterhin **54 Mitglieder** (53 im Objekt-Literal +
`boot` aus `init()`), `window.RobotNav` vorhanden, 70 Lernseiten. Kein Mitglied entfernt oder
umbenannt – Vergleichsbasis `docs/api-snapshot.txt`.

Vorher-Stände in `BACKUP_2026_11_16_Phase1/SHA256SUMS.txt` (78 Dateien, 13,62 MB).

## 7. Noch offene Arbeitspunkte

1. **Gerätelauf auf SM_S931B** (Install, `logcat`, `screencap`): Derzeit nicht ausführbar.
   `adb devices` zeigt kein Gerät, obwohl Windows das Telefon sieht
   („SAMSUNG Android ADB Interface", Treiber 2.21.4.0) – Status „Unknown", ohne Problemcode.
   Das ist der typische Zustand eines gesperrten/bildschirmlosen Telefons oder einer nicht
   bestätigten USB-Debugging-Abfrage; das lässt sich nur am Gerät selbst beheben
   (Bildschirm entsperren, USB-Debugging-Abfrage bestätigen, evtl. Kabel neu anstecken).
   Alle übrigen Nachweise (Build, Selbsttest, Browser-Messungen) sind erbracht.
2. Offene Punkte V1, V2, V4, V7 aus `README.md` Abschnitt 10 – V3, V5 und V6 sind
   mit dem Assistenten-Durchgang erledigt (siehe 5.2 und 5.4).
3. Phase-1-Fahrplan gemäß `README.md` Abschnitt 11 (Design-System-Token-Datei,
   Theme-Schalter, Kontrast-Wächter, Fokus-Management, Textskalierung).