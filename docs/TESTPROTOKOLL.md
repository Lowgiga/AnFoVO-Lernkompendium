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

## 3. Build-Nachweis (Baseline, vor den Korrekturen)

```
.\gradlew.bat :app:assembleDebug   →  BUILD SUCCESSFUL in 4s
app-universal-debug.apk  4.264.711 Bytes
SHA256 9FE03490E0AA5D4C32B6B1043BE4D6CCDCF7E79D5F15AED0C36EF214F088E2B5
                        (identisch für arm64-v8a, universal, x86_64)
```

Abweichung zum Backup (CD02BC90…, 4.264.781 Bytes) geklärt: das frühere APK enthielt zusätzlich
die Datei `index.html.broken`; die ist entfernt. **Hinweis:** Der Build-Vorrat stammt vom Stand
vor den Phase-0-Korrekturen; ein Neuaufbau danach ist noch offen (Punkt 7).

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

| | vorher | nachher |
|---|---|---|
| bestanden | 82 / 99 | **95 / 99** |
| übersprungen | 1 | 1 |
| Fehlschläge | 18 | 4 |

Vorher/Nachher-Vergleich ist zulässig: Die 18 Altfehlschläge waren überwiegend eine
Folge der CSS-Auslagerung (Phase 0) – der Selbsttest suchte die Regeln im Inline-`<style>`,
das es nicht mehr gab.

### 5.1 Behobene Fehlschläge (19 → 0)

Alle CSS-abhängigen Prüfungen (Druckausgabe, Dark Mode, Fokus, Touch-Ziele, Animationen,
Kopfzeile, Abstände) nach Einführung von `cssSheets()`/`sheetText()` im Selbsttest-Block.
Ursache: reine Testschwäche, kein Produktivdefekt.

### 5.2 Offene Fehlschläge (4) – Befunde

**(1) Touch-Ziele ≥ 44 × 44 px — echter Produktivdefekt (WCAG 2.5.5/2.5.8-nah)**
Messwerte: `#assistToggle` 106 × 26 px, `#assistSpeech` 101 × 26 px; `min-height: auto`,
`min-width: auto`. Quelle: `assistent.js` (eigenes `<style>`-Element, Z. 24–41).
Wirkung: zwei dauerhaft sichtbare Schaltflächen unterschreiten das 44-px-Ziel deutlich.
Geplant: P1-05 (Touch-Ziele) bzw. P1-10 (Inline-Style auslagern).

**(2) Speicher-Schlüssel ohne Präfix — echter Produktivdefekt**
`anfoevo_assistent` und `anfoevo_speech` (`assistent.js` Z. 14) folgen nicht dem Präfix
`anfoevo_v2_`, das `app.js` für alle übrigen Schlüssel verwendet. Der Selbsttest prüft genau das.
Geplant: Umbenennen mit Migration der Bestandsdaten.

**(3) Buttons-Schwelle im Selbsttest — Testspezifikum, kein Produktivdefekt**
Zählung auf der Checkpoint-Seite bei 800 px: 38 Buttons im DOM, 0 in den Heftseiten
(`#pages`), **10 sichtbar**. Grenzwert des Tests ist 8; der Code-Kommentar dokumentiert
„v2.9.4: +3 (Update-Toast, Install-Prompt, Offline-Banner)", wurde aber nicht angehoben.
Die 10 sichtbaren = 8 Soll + 2 Assistenten-Schaltflächen (siehe (1)).
Empfehlung: Grenzwert auf 12 anheben und Kommentar korrigieren, damit mit diesen Overlays
konsistent bleiben; oder die Assistenten-Overlays aus der Zählung nehmen.

**(4) Druck-CSS-Erkennung — Testspezifikum, kein Produktivdefekt**
Zwei Teilpunkte:
- `@page`-Erkennung scheitert an Groß-/Kleinschreibung: Chrome serialisiert
  `@page { size: a4; margin: 15mm 14mm; }` (klein). Der Test prüft `/A4/` case-sensitiv.
  Fix im Test: `/A4/i`.
- `calc(6 * 1.45em + 1px)` wird von der CSSOM zu **`calc(8.7em + 1px)`** zusammengefasst
  (`.sitans .printval { min-height: calc(8.7em + 1px); }` in `@media print`). Der
  Quelltext-Vergleich greift deshalb nicht. Fix im Test: beide Schreibweisen akzeptieren.
Alle übrigen Druck-Prüfpunkte (Kopf aus, Lösungen aus, `border-bottom`, `break-inside`,
Reihenfolge der Ausfüllseiten, `content: none` auf `.src a::after`) bestehen.

### 5.3 Übersprungen (1)

„Desktop: Kopfzeileninhalt auf 90ch begrenzt und zentriert" – nur bei Viewport ≥ 1200 px
messbar; im Testausmaß 800 px übersprungen. Kein Defekt.

## 6. Prüfsummen (Stand nach den Korrekturen)

| Datei | Bytes | SHA-256 |
|-------|-------|---------|
| `assets/index.html` | 490.431 | `2789287ECE884F5CC4945C0363A22AA7A82B4AEA75AF72AD3532843D6336B350` |
| `assets/style.css` | 55.877 | `9218E0794D784DA005B3F0290825BA5AC76D5F451FB26FFCE789C7CBEDB1C639` |
| `assets/app.js` | 81.625 | `A98DBB2BECBC98DE64EA155E1104371BEA07130BB224A0D6AB2A7254B22DBC5F` |
| `assets/assistent.js` | 10.104 | `FE2CAD848B948E3258224A10CAD3061B20790DB230EC8C99DAABF9567B47472C` |
| `assets/robot-navigation.js` | 22.263 | `A9424CABE94BD87B17B5DB67D9F42CC72DDD060F6BC7871E95772B1208DEA057` |
| `assets/sw.js` | 2.555 | `32F5F7D318039F97FE3F1F6C473C63F86EC76910921861816F5BA641F5528DBC` |
| `assets/manifest.json` | 774 | `C7947A54C6D934900D3B4D1E5D801ACD287F3B8106624EA8E274315A03DEB85E` |

Vorher-Stand (mit beschnittenem `style.css`) zusätzlich in `BACKUP_2026_11_16_Phase1/SHA256SUMS.txt`
(78 Dateien, 13,62 MB).

## 7. Noch offene Arbeitspunkte

1. Neuaufbau der APK nach den Phase-0-Korrekturen (`assembleDebug`) mit Hash-Abnahme.
2. Gerätelauf auf SM_S931B (Install, `logcat`, `screencap`) für den korrigierten Stand.
3. Oberflächen offene Punkte V1–V7 aus `README-ANDROID.md` Abschnitt 10.
4. Selbsttest-Fixes aus 5.2 (3) und (4) – reine Testkorrekturen, zunächst zu dokumentieren,
   Umsetzung im Zuge von Phase 1.