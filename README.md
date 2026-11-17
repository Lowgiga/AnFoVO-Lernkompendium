# Lern-Kompendium § 8 AnFöVO NRW – Android-Wrapper

**Stand:** v2.10.0 (versionCode 296) · Dokumentationsstand: 17.11.2026
**Status:** Phase 0 und Phase 1 abgeschlossen (Selbsttest 106/106); offen: Gerätelauf (G1) und
Phase 2 Lern-Assistent (→ 2.11.0). Details: Abschnitte 10 und 11.
**Package:** `de.omega.lernkompendium` · minSdk 29 · targetSdk / compileSdk 36

Inoffizielle Lernhilfe zur Basisqualifizierung nach § 8 AnFöVO NRW. Kein Ersatz für die
Kursunterlagen. Läuft vollständig offline – es wird keine externe Website als Laufzeitquelle
gebraucht.

---

## 1. Zweck

Ein natives Android-Paket (WebView-Wrapper) um eine lokale HTML-Lernanwendung. Die Lerninhalte,
das Styling und die gesamte Programmlogik liegen als Dateien in `app/src/main/assets/` und werden
aus dem APK-Asset-Verzeichnis geladen. Die Web-Anwendung ist gleichzeitig als PWA lauffähig.

## 2. Projektstruktur

```
AnFoeVO_AndroidWrapper_v2.9.1/
├─ app/src/main/assets/           Web-Anwendung (wird ins APK gepackt)
│  ├─ index.html                  Shell + 70 Lernseiten + Selbsttest-Block (496 Zeilen)
│  ├─ style.css                   komplettes Styling, Design-Tokens, Light/Dark/Auto, Assistent (543 Zeilen)
│  ├─ app.js                      Programmlogik, Store, Suche, Modi, Darstellung (973 Zeilen)
│  ├─ assistent.js                Assistent: Hinweise, Lob, Sprache (238 Zeilen, Styling in style.css)
│  ├─ robot-navigation.js         RobotNav: adaptive 3D-Navigation
│  ├─ sw.js                       Service Worker (cache-first, versioniert; Kern inkl. Stil + Logik)
│  ├─ manifest.json               PWA-Manifest
│  ├─ icon-192.png, icon-512.png, icon-512-maskable.png
│  └─ bg/                         Hintergrund-Kacheln (58 Dateien)
├─ app/src/main/java/de/omega/lernkompendium/MainActivity.java   WebView + JS-Bridge
├─ app/src/main/AndroidManifest.xml
├─ app/build.gradle               versionCode 296, versionName '2.10.0'
├─ build-debug.ps1                Build- und Prüfskript (JDK/SDK selbst ermittelnd)
├─ README.md                      dieses Dokument
├─ CHANGELOG.md                   Änderungsgeschichte
├─ docs/api-snapshot.txt          Regressionsvergleich (window.KOMP, CSS-Tokens, Keys)
├─ docs/TESTPROTOKOLL.md          Build-/Testnachweise, offene Punkte
├─ docs/ARBEITSPLAN-2.10.0.md     Plan und Abschlussprotokoll Version 2.10.0 (Phase 1)
├─ docs/VERCEL-DEPLOY.md          Web-Deployment-Anleitung (Vercel/GitHub Pages, Stand 17.11.2026)
├─ vercel.json                    Statisches Web-Deployment (Output: app/src/main/assets)
├─ gradlew                        Unix-Gradle-Wrapper (Linux/macOS/CI)
├─ app/src/main/assets/.gitignore  Ignoriert .vercel/ und .env* (Build-/Secret-Artefakte)
├─ backups/                       Sicherungssnapshots (nicht versioniert, je SHA256SUMS.txt)
│  ├─ 2026-11-16_phase0/          Stand vor Phase 0 (17 Dateien + Prüfsummen, nachgetragen)
│  ├─ 2026-11-16_phase1/          Stand nach Phase 1-Vorlauf (78 Dateien + Prüfsummen)
│  └─ 2026-11-16_abschluss/       Stand vor dem Phase-1-Abschluss 2.10.0 (94 Dateien + Prüfsummen)
└─ (Tool-Ordner build/ und .gradle/ – Build-Ausgaben, nicht versioniert)
```

Kodierung aller Textdateien: **UTF-8 ohne BOM** (das BOM in `sw.js` wurde am 16.11.2026
entfernt – Verstoß gegen diese Regel). `index.html` verwendet LF-Zeilenenden; die übrigen
Dateien unter `app/src/main/assets/` Windows-Zeilenenden (CRLF). Einzelne Streu-CRLF-Zeilen
in `app.js`, `index.html`, `app/build.gradle`, `AndroidManifest.xml` und
`gradle-wrapper.properties` stammen aus der Projekthistorie und sind funktional ohne Belang.

## 3. Architektur

- **Android:** `MainActivity` lädt die App über den WebView-Asset-Lader als
  `https://appassets.androidplatform.net/assets/index.html` in einer WebView (gesicherte
  Herkunft, daher arbeiten Speicher und Bridge zuverlässig; `file:///android_asset/` wird
  nicht mehr benutzt). Die Java-Bridge stellt `saveProgress` und `printPage` bereit; ohne
  Bridge fällt die App auf den Datei-Download zurück.
- **Web-Shell:** `index.html` enthält die gesamte Seitenstruktur (70 `<article class="page">`),
  Kopfzeile, Suche, Menü, Infoseite und den Selbsttest.
- **Styling:** `style.css` mit `:root`-Design-Tokens (Farben, Abstände, Radien, `--tap: 44px`),
  Dark-Mode über `prefers-color-scheme` **oder** manuelle Wahl (`data-theme="hell|dunkel"`),
  `prefers-reduced-motion`-Kill-Switch, `@media print` (A4-Arbeitsblatt, immer hell) und
  `forced-colors`-Verträglichkeit (Token auf Systemfarben, 3D-Deko aus).
- **Logik:** `app.js` – ES5-strikt (`var`, `function(){}`, keine Arrow-Funktionen/`let`/`const`).
  Datenmodell `DATA` (Seiten, Karteikarten, Quiz, Glossar), Zustand `S`, Store mit Präfix
  `anfoevo_v2_`, Export `window.KOMP` für Tests und Automation. Die Darstellungswahl
  (`auto`/`hell`/`dunkel`) liegt in `S.prefs.theme` und wird per `data-theme` am
  Wurzelelement gesetzt; ein kleines Skript im `<head>` setzt die gespeicherte Wahl vor dem
  ersten Stil-Aufbringen (kein Farblitz).
- **Assistent:** `assistent.js` – Blase mit Umschalter und Sprachdialog.
- **Navigation:** `robot-navigation.js` – `window.RobotNav`, reagiert auf
  `kompendium:pagechange` / `kompendium:viewchange`.
- **Sicherheit (CSP in index.html):** `default-src 'self'; script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self';
  worker-src 'self'; manifest-src 'self'; object-src 'none'; base-uri 'none';
  form-action 'none'`. Externe Ressourcen sind damit ausgeschlossen; `eval` und `new Function`
  sind blockiert. **Der Assistent bleibt deshalb lokal und regelbasiert – kein Cloud-LLM.**

## 4. Build

Voraussetzungen: JDK 21 (geprüft), Android SDK Platform 36, Build Tools 35.0.0 oder neuer,
Gradle 8.13 zum Android Gradle Plugin 8.13.2.

```powershell
$env:JAVA_HOME="C:\Tools\jdk-21\jdk-21.0.13+9"
$env:ANDROID_HOME="C:\Android"
$env:PATH="$env:ANDROID_HOME\cmdline-tools\latest\bin;$env:JAVA_HOME\bin;$env:PATH"
.\gradlew.bat :app:assembleDebug
```

Oder kürzer: `.\build-debug.ps1`

Ausgabe: `app\build\outputs\apk\debug\app-universal-debug.apk` (sowie ABI-Varianten `arm64-v8a`
und `x86_64`).

Release braucht Keystore-Angaben über die Umgebungsvariablen `KOMPENDIUM_KEYSTORE`,
`KOMPENDIUM_STORE_PASSWORD`, `KOMPENDIUM_KEY_PASSWORD`, `KOMPENDIUM_KEY_ALIAS`.

## 5. Installation und Gerätetest

```powershell
adb install -r .\app\build\outputs\apk\debug\app-universal-debug.apk
adb logcat -s chromium:I            # WebView-Konsole
adb shell screencap /sdcard/p.png   # Bildschirmfoto
```

Zielgerät für den Gerätetest: **SM_S931B** (echtes Gerät, kein Emulator). Der letzte
Gerätelauf ist derzeit nicht ausführbar (`adb devices` zeigt kein Gerät – USB-Debugging
am Telefon bestätigen); Nachweise in `docs/TESTPROTOKOLL.md` Abschnitt 7.

## 6. Signatur

- **Debug:** SDK-Debugsignatur, nur für Tests.
- **Release:** eigener, dauerhaft aufzubewahrender Keystore. **Nicht** im Repository speichern.
  Ein Schlüsselwechsel verhindert reguläre Updates einer installierten App.

## 7. Qualitätssicherung: Selbsttest

Die App bringt einen eigenen Funktionstest mit (106 Prüfungen). Er prüft Seitenstruktur, Suche,
Speicher, Druckausgabe, Barrierefreiheit und Design – dazu seit 2.10.0 den Offline-Kern des
Service Workers, die Manifest-Farbe, die Versionsübereinstimmung, die `window.KOMP`-Schnittstelle,
die Darstellungsumschaltung, den Kontrast-Wächter (13 Textpaar-Token in Automatik, Hell und
Dunkel, je ≥ 4,5:1) und den Skip-Link.

**Lokaler Start (Cache-Probleme vermeiden):**

```powershell
# -d braucht einen ABSOLUTEN Pfad (jwebserver lehnt relative ab)
& "C:\Tools\jdk-21\jdk-21.0.13+9\bin\jwebserver.exe" -p 8099 -d "$(Resolve-Path 'app\src\main\assets')" -b 127.0.0.1
```

Dann im Browser aufrufen: `http://localhost:8099/index.html?test=1`

Wichtig: Der Service Worker arbeitet **cache-first**. Vor jeder Verifikation
Service-Worker-Registrierungen aufheben, `caches.keys()` löschen und die Seite mit einem
Cache-Buster (`?test=1&nocache=<Zeitstempel>`) neu laden – sonst werden veraltete Dateien
geliefert.

**Ergebnis vom 16.11.2026:** **106 / 106 bestanden**, 1 übersprungen (nur bei Viewport ≥ 1200 px
messbar). Einzelfälle und Messwerte in `docs/TESTPROTOKOLL.md`.
Hinweis für die Wiederholung: Der Service Worker arbeitet cache-first und matcht mit
`ignoreSearch: true` – ein Cache-Buster wie `?nocache=…` reicht **nicht**. Vor der Messung
Registrierungen aufheben, `caches.keys()` löschen und notfalls von einem frischen Origin laden,
sonst werden veraltete Dateien gemessen.

## 8. Barrierefreiheit

Ziel: **WCAG 2.2 AA**. Bereits umgesetzt: `lang="de"`, Skip-Link, `main`-Landmark, h1–h3-Hierarchie,
`aria-live`-Statusmeldungen, `:focus-visible`, 44-px-Berührungsziele (`--tap`), Reflow-Verhalten,
`prefers-reduced-motion`, Druckausgabe als A4-Arbeitsblatt. Seit 2.10.0 zusätzlich:
Darstellungsumschaltung Automatik/Hell/Dunkel (`☰ Mehr → 🌗 Darstellung`), `forced-colors`-Token
auf Systemfarben und der **Kontrast-Wächter** im Selbsttest: 13 Textpaar-Token werden in allen
drei Darstellungszuständen gemessen und müssen ≥ 4,5:1 bleiben (hell wie dunkel).

## 9. Versionierung, Backups, Git

- **Git** ist eingerichtet (Commit `1637bb5` „Baseline v2.9.5 vor Phase 1", Tag `v2.9.5-baseline`).
  Git liegt unter `C:\Program Files\Git\cmd\git.exe` und ist **nicht** im PATH – Aufrufe mit
  vollem Pfad. `.gitignore` ignoriert `build/`, `.gradle/`, `*.apk`, `local.properties` und
  `backups/`.
- **GitHub:** Remote `origin` = `https://github.com/Lowgiga/AnFoVO-Lernkompendium.git`.
  Der lokale `main` liegt dort auf dem Branch **`android-wrapper-2.10.0`** (HEAD `21add01`),
  nachverfolgt mit `git push -u origin main:refs/heads/android-wrapper-2.10.0`; Tags
  `v2.10.0` und `v2.9.5-baseline` sind ebenfalls gepusht.
  **Wichtig:** Das entfernte `main` (`1baa119`) ist eine **getrennte Projekthistorie**
  (Standalone-PWA-Variante, u. a. Tags `v2.9.2`/`v2.9.4`) – es wurde **bewusst nicht**
  überschrieben. Ein Force-Push wäre Datenverlust; die Zusammenführung liegt beim Betreiber
  (Pull-Request-Vorschlag: `…/pull/new/android-wrapper-2.10.0`).
  Die Baseline enthielt versehentlich noch 1263 Dateien (u. a. 1058 aus `app/build/` und die
  APKs); seit der Bereinigung sind **99 Dateien** versioniert (Stand 2.10.0 inklusive
  `docs/ARBEITSPLAN-2.10.0.md`) – ausschließlich Quellen und Dokumentation.
- **Backups** werden vor jedem destruktiven Schritt angelegt, inklusive `SHA256SUMS.txt`, und
  liegen gesammelt unter `backups/` (nicht versioniert).
- **Versionslauf:** 2.9.5 (ausgeliefert) → **2.10.0 (Phase 1: Design-System + WCAG 2.2 AA,
  abgeschlossen)** → 2.11.0 (Phase 2: Lern-Assistent). versionCode 295 → 296 → 297.

## 10. Bekannte offene Punkte (Stand 16.11.2026)

| # | Fund | Auswirkung | Stand |
|---|------|------------|-------|
| V1 | `sw.js` cached `./style.css` und `./app.js` **nicht** | Styles/Logik nach erstem Start veraltet | **behoben 16.11.2026** (beide im Offline-Kern, Cache 2.10.0) |
| V2 | `manifest.json` `background_color` ≠ CSS `--bg` | Splash-Farbe weicht ab | **behoben 16.11.2026** (`#f4eee3`, per Selbsttest überwacht) |
| V3 | `assistent.js` blendete die Blase bei ≤ 760 px **ganz aus** und injizierte ein eigenes `<style>`-Element | Assistent auf dem Telefon unerreichbar, CSS-Doppelspur | **behoben 16.11.2026** |
| V4 | `DATA.version` ist `"2.7.0"`, `versionName` ist `2.9.5` | Export-/Versionsangabe falsch | **behoben 16.11.2026** (`2.10.0`, Übereinstimmung per Selbsttest) |
| V5 | `anfoevo_assistent` ohne Präfix `anfoevo_v2_` | Speicherschlüssel-Inkonsistenz | **behoben 16.11.2026** (mit Migration) |
| V6 | Assistenten-Schaltflächen nur 26 px hoch | Touch-Ziel < 44 px | **behoben 16.11.2026** (44 px) |
| V7 | `window.KOMP` wird zweimal gesetzt: Literal (Z. 758) und `.boot` (Z. 746/755 in `init()`) | API nur deshalb vollständig, weil `init()` danach läuft – fragil | **behoben 16.11.2026** (ein Objekt, einmal zugewiesen) |

**Alle sieben gemeldeten Defekte sind geschlossen.** Weiter offen (dokumentiert, kein Code-Defekt):

| # | Punkt | Grund | nächster Schritt |
|---|-------|-------|-----------------|
| G1 | Gerätelauf auf SM_S931B (Install, `logcat`, `screencap`) | USB-Debugging am Telefon derzeit nicht bestätigt (`adb devices` zeigt kein Gerät) | Am Gerät entsperren + Debugging-Abfrage bestätigen, dann `adb install -r` |
| G2 | Phase 2: Lern-Assistent | eigene Leistungsbeschreibung, nächstes Versionspaket 2.11.0 | Fahrplan wie unten |
| G3 | Impressum-Platzhalter in der Fußzeile der App („Name, Anschrift, Kontakt" nach § 5 DDG) | Persönliche Anbieterangaben – nur vom Betreiber ausfüllbar | Vor einer Veröffentlichung (Download/Store) ergänzen; für private Nutzung bedeutungslos |

## 11. Nächste Schritte

- **Phase 1 (→ 2.10.0) ist abgeschlossen** (16.11.2026): Design-System-Token (in `style.css`,
  79 Namen (68 Design-Token + 11 zur Laufzeit gesetzte, Vergleich in `docs/api-snapshot.txt`),
  Darstellung Automatik/Hell/Dunkel,
  Kontrast-Wächter, Fokus-Management (Skip-Link testbelegt), 44-px-Touch-Ziele, Reflow,
  Textskalierung (rem/em), Reduced-Motion/Kill-Switch, `forced-colors`-Verträglichkeit,
  Semantik/Screenreader-Pass, Typografie-Raster — belegt durch 106/106 Selbsttests.
  Arbeitsplan und Abstimmungspunkte: `docs/ARBEITSPLAN-2.10.0.md`.
- **Phase 2 (→ 2.11.0):** kontextbewusster, lokal regelbasierter Lern-Assistent (Chat-Panel als
  Bottom-Sheet, Slash-Befehle, Fehleranalyse, adaptiver Quiz, Lernziel-Modus, Sprachdialog,
  RobotNav-Anbindung). Regel aus Abschnitt 3 bleibt: der Assistent bleibt lokal und regelbasiert,
  kein Cloud-LLM.
- Reihenfolge: Architektur/Stabilität zuerst, dann Barrierefreiheit und Design, dann Lernlogik.

## 12. Konventionen für Änderungen

- JavaScript bleibt **ES5-strikt**; camelCase für Namen, UPPER_SNAKE für Konstanten.
- CSS in kompakten Zeilen, kebab-case, ausschließlich über Design-Tokens.
- `window.KOMP` ist öffentliche Schnittstelle: **kein Mitglied entfernen oder umbenennen**.
  Vergleichsbasis: `docs/api-snapshot.txt`.
- Android-Assets und Web-Version bleiben synchron; jede Änderung mit Build + Selbsttest +
  API-Diff + Browser-Test + Gerätetest absichern.
- Vor destruktiven Änderungen: Backup + SHA-256 + Build-Verify. Kein Blind-Ändern.

## 13. Betrieb, Wiederherstellung, Veröffentlichung

**Rollback auf einen früheren Stand:**
- Git-Commit zurücksetzen: `git reset --hard <commit>` (z. B. `befe779` für den Ausgangsstand
  v2.9.5, `2f34241` für den Phase-1-Abschluss). Die Backups unter `backups/` sind dazu
  unabhängig nutzbar.
- Backup wiederherstellen: Ordnerinhalt aus `backups/<datum>/` in `app/src/main/assets/`
  kopieren; Prüfsummen mit `SHA256SUMS.txt` abgleichen; dann `.\build-debug.ps1`.
- Service-Worker-Cache beim Testen: Registrierungen aufheben, `caches.keys()` löschen,
  frischen Origin (neuen Port) nutzen – sonst werden veraltete Dateien gemessen.

**GitHub:**
- Remote `origin` = `https://github.com/Lowgiga/AnFoVO-Lernkompendium.git`.
- Lokaler `main` liegt auf Branch `android-wrapper-2.10.0` (HEAD `21add01`); Push:
  `git push origin HEAD:android-wrapper-2.10.0`. Tags: `git push origin --tags`.
- Das entfernte `main` ist eine getrennte Historie (Standalone-PWA) – nicht blind
  überschreiben; Zusammenführung über Pull-Request
  (`…/pull/new/android-wrapper-2.10.0`).

**Web-Deployment (Vercel / GitHub Pages):**
- Anleitung und Entscheidungsgrundlage in `docs/VERCEL-DEPLOY.md`; Konfiguration in
  `vercel.json` (Output `app/src/main/assets`). `sw.js` und `manifest.json` werden
  frisch ausgeliefert (`max-age=0, must-revalidate`).
- Das `.vercel/`-Verzeichnis und `.env*` enthalten möglicherweise Secrets (OIDC-Token) und
  dürfen nie versioniert werden (`.gitignore` deckt sie ab); bei versehentlichem Einpacken
  in den Build greift `packagingOptions` in `app/build.gradle`.

**Vor einer Veröffentlichung (Store/Download):**
- Impressum-Platzhalter in der App-Fußzeile füllen (G3).
- Release-Keystore über `KOMPENDIUM_KEYSTORE` etc. setzen; `.\gradlew.bat :app:bundleRelease`.
- Datenschutz/Privacy-Policy-Verweis ergänzen (Vorlage `PRIVACY_POLICY.md` im Remote-Repo).