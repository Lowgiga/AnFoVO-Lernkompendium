# Lern-Kompendium § 8 AnFöVO NRW – Android-Wrapper

**Stand:** v2.9.5 (versionCode 295) · Dokumentationsstand: 16.11.2026
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
│  ├─ index.html                  Shell + 70 Lernseiten + Selbsttest-Block (476 Zeilen)
│  ├─ style.css                   komplettes Styling, Design-Tokens, Light/Dark, Assistent (533 Zeilen)
│  ├─ app.js                      Programmlogik, Store, Suche, Modi (958 Zeilen)
│  ├─ assistent.js                Assistent: Hinweise, Lob, Sprache (238 Zeilen, Styling in style.css)
│  ├─ assistent.js                Assistenten-Blase + Sprachausgabe
│  ├─ robot-navigation.js         RobotNav: adaptive 3D-Navigation
│  ├─ sw.js                       Service Worker (cache-first, versioniert)
│  ├─ manifest.json               PWA-Manifest
│  ├─ icon-192.png, icon-512.png, icon-512-maskable.png
│  └─ bg/                         Hintergrund-Kacheln (58 Dateien)
├─ app/src/main/java/de/omega/lernkompendium/MainActivity.java   WebView + JS-Bridge
├─ app/src/main/AndroidManifest.xml
├─ app/build.gradle               versionCode 295, versionName '2.9.5'
├─ build-debug.ps1                Build-Hilfsskript
├─ README-ANDROID.md              dieses Dokument
├─ CHANGELOG.md                   Änderungsgeschichte
├─ docs/api-snapshot.txt          Regressionsvergleich (window.KOMP, CSS-Tokens, Keys)
├─ docs/TESTPROTOKOLL.md          Build-/Testnachweise, offene Punkte
└─ BACKUP_2026_11_16_Phase1/      Sicherungskopie + SHA256SUMS.txt
```

Kodierung aller Textdateien: **UTF-8 ohne BOM**. `index.html` verwendet LF-Zeilenenden.

## 3. Architektur

- **Android:** `MainActivity` lädt `file:///android_asset/index.html` in einer WebView. Origin
  `appassets.androidplatform.net`. Die Java-Bridge stellt `saveProgress` und `printPage` bereit;
  ohne Bridge fällt die App auf den Datei-Download zurück.
- **Web-Shell:** `index.html` enthält die gesamte Seitenstruktur (70 `<article class="page">`),
  Kopfzeile, Suche, Menü, Infoseite und den Selbsttest.
- **Styling:** `style.css` mit `:root`-Design-Tokens (Farben, Abstände, Radien, `--tap: 44px`),
  `prefers-color-scheme`-Dark-Mode, `prefers-reduced-motion`-Kill-Switch, `@media print`
  (A4-Arbeitsblatt) und `forced-colors`-Verträglichkeit.
- **Logik:** `app.js` – ES5-strikt (`var`, `function(){}`, keine Arrow-Funktionen/`let`/`const`).
  Datenmodell `DATA` (Seiten, Karteikarten, Quiz, Glossar), Zustand `S`, Store mit Präfix
  `anfoevo_v2_`, Export `window.KOMP` für Tests und Automation.
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
adb install -r .\app\build\outputs\apk\debug\app-debug.apk
adb logcat -s chromium:I            # WebView-Konsole
adb shell screencap /sdcard/p.png   # Bildschirmfoto
```

Geprüftes Zielgerät: **SM_S931B** (echtes Gerät, kein Emulator).

## 6. Signatur

- **Debug:** SDK-Debugsignatur, nur für Tests.
- **Release:** eigener, dauerhaft aufzubewahrender Keystore. **Nicht** im Repository speichern.
  Ein Schlüsselwechsel verhindert reguläre Updates einer installierten App.

## 7. Qualitätssicherung: Selbsttest

Die App bringt einen eigenen Funktionstest mit (99 Prüfungen). Er prüft Seitenstruktur, Suche,
Speicher, Druckausgabe, Barrierefreiheit und Design.

**Lokaler Start (Cache-Probleme vermeiden):**

```powershell
& "C:\Tools\jdk-21\jdk-21.0.13+9\bin\jwebserver.exe" -p 8099 -d "app\src\main\assets" -b 0.0.0.0
```

Dann im Browser aufrufen: `http://localhost:8099/index.html?test=1`

Wichtig: Der Service Worker arbeitet **cache-first**. Vor jeder Verifikation
Service-Worker-Registrierungen aufheben, `caches.keys()` löschen und die Seite mit einem
Cache-Buster (`?test=1&nocache=<Zeitstempel>`) neu laden – sonst werden veraltete Dateien
geliefert.

**Ergebnis vom 16.11.2026:** **99 / 99 bestanden**, 1 übersprungen (nur bei Viewport ≥ 1200 px
messbar). Einzelfälle und Messwerte in `docs/TESTPROTOKOLL.md`.
Hinweis für die Wiederholung: Der Service Worker arbeitet cache-first und matcht mit
`ignoreSearch: true` – ein Cache-Buster wie `?nocache=…` reicht **nicht**. Vor der Messung
Registrierungen aufheben, `caches.keys()` löschen und notfalls von einem frischen Origin laden,
sonst werden veraltete Dateien gemessen.

## 8. Barrierefreiheit

Ziel: **WCAG 2.2 AA**. Bereits umgesetzt: `lang="de"`, Skip-Link, `main`-Landmark, h1–h3-Hierarchie,
`aria-live`-Statusmeldungen, `:focus-visible`, 44-px-Berührungsziele (`--tap`), Reflow-Verhalten,
`prefers-reduced-motion`, Druckausgabe als A4-Arbeitsblatt. Kontrastwerte der Textpaare liegen
eigener Berechnung nach alle ≥ 4,5:1.

## 9. Versionierung, Backups, Git

- **Git** ist eingerichtet (Commit `1637bb5` „Baseline v2.9.5 vor Phase 1", Tag `v2.9.5-baseline`).
  Git liegt unter `C:\Program Files\Git\cmd\git.exe` und ist **nicht** im PATH – Aufrufe mit
  vollem Pfad. `.gitignore` ignoriert `build/`, `*.apk`, `local.properties`, `BACKUP_*/`.
  Die Baseline enthielt versehentlich noch 1263 Dateien (u. a. 1058 aus `app/build/` und die
  APKs); seit der Bereinigung sind **94 Dateien** versioniert – ausschließlich Quellen und
  Dokumentation.
- **Backups** werden vor jedem destruktiven Schritt angelegt, inklusive `SHA256SUMS.txt`.
- **Versionslauf:** 2.9.5 (ausgeliefert) → 2.10.0 (Phase 1: Design-System + WCAG) →
  2.11.0 (Phase 2: AI-Lern-Assistent). versionCode 295 → 296 → 297.

## 10. Bekannte offene Punkte (Stand 16.11.2026)

| # | Fund | Auswirkung | Stand |
|---|------|------------|-------|
| V1 | `sw.js` cached `./style.css` und `./app.js` **nicht** | Styles/Logik nach erstem Start veraltet | offen (W6) |
| V2 | `manifest.json` `background_color: #f5f6f7` ≠ CSS `--bg: #f4eee3` | Splash-Farbe weicht ab | offen (W6) |
| V3 | `assistent.js` blendete die Blase bei ≤ 760 px **ganz aus** und injizierte ein eigenes `<style>`-Element | Assistent auf dem Telefon unerreichbar, CSS-Doppelspur | **behoben 16.11.2026** |
| V4 | `DATA.version` ist `"2.7.0"`, `versionName` ist `2.9.5` | Export-/Versionsangabe falsch | offen (W6) |
| V5 | `anfoevo_assistent` ohne Präfix `anfoevo_v2_` | Speicherschlüssel-Inkonsistenz | **behoben 16.11.2026** (mit Migration) |
| V6 | Assistenten-Schaltflächen nur 26 px hoch | Touch-Ziel < 44 px | **behoben 16.11.2026** (44 px) |
| V7 | `window.KOMP` wird zweimal gesetzt: Literal (Z. 758) und `.boot` (Z. 746/755 in `init()`) | API nur deshalb vollständig, weil `init()` danach läuft – fragil | offen (W6) |

## 11. Nächste Schritte

- **Phase 1 (→ 2.10.0):** Design-System-Token-Datei, Theme light/dark/auto, Kontrast-Wächter,
  Fokus-Management, Touch-Ziele & Reflow, Textskalierung, Reduced-Motion-/System-Oszillationen,
  Semantik/Screenreader-Pass, Typografie-Raster.
  Bereits erledigt (16.11.2026): Touch-Ziele der Assistenten-Schaltflächen (44 px), Auslagerung
  des Inline-Styles aus `assistent.js` in `style.css`, Speicherschlüssel-Präfix, Erreichbarkeit
  des Assistenten auf dem Smartphone.
- **Phase 2 (→ 2.11.0):** kontextbewusster, lokal regelbasierter Lern-Assistent (Chat-Panel als
  Bottom-Sheet, Slash-Befehle, Fehleranalyse, adaptiver Quiz, Lernziel-Modus, Sprachdialog,
  RobotNav-Anbindung).
- Reihenfolge: Architektur/Stabilität zuerst, dann Barrierefreiheit und Design, dann Lernlogik.

## 12. Konventionen für Änderungen

- JavaScript bleibt **ES5-strikt**; camelCase für Namen, UPPER_SNAKE für Konstanten.
- CSS in kompakten Zeilen, kebab-case, ausschließlich über Design-Tokens.
- `window.KOMP` ist öffentliche Schnittstelle: **kein Mitglied entfernen oder umbenennen**.
  Vergleichsbasis: `docs/api-snapshot.txt`.
- Android-Assets und Web-Version bleiben synchron; jede Änderung mit Build + Selbsttest +
  API-Diff + Browser-Test + Gerätetest absichern.
- Vor destruktiven Änderungen: Backup + SHA-256 + Build-Verify. Kein Blind-Ändern.