# Dokumentation: window.KOMP API & Abhängigkeiten (Phase 0 Bestandsaufnahme)

## 1. Übersicht

Dieses Dokument erfasst alle öffentlich zugänglichen Funktionen der `window.KOMP`-Schnittstelle sowie die Android-JavaScript-Bridge `KompendiumApp`. Es dient als Referenz für alle weiteren Refactoring-Schritte (Phase 1+).

**Wichtig:** Diese Schnittstelle muss zu 100 % unverändert erhalten bleiben, damit keine Funktionsverluste entstehen.

---

## 2. Android-JavaScript Bridge: `KompendiumApp`

In `MainActivity.java` registriert:
```java
webView.addJavascriptInterface(new AppBridge(), "KompendiumApp");
```

### 2.1 `KompendiumApp.saveProgress(String json)`
- **Aufruf:** `KompendiumApp.saveProgress(JSON.stringify(...))`
- **Wird aufgerufen von:** Klick auf `#exportlink` in `index.html` (via `onPageFinished` injected JavaScript)
- **Funktion:** Speichert JSON als Datei `anfoevo_v2_fortschritt.json` im Android Downloads-Ordner via `MediaStore.Downloads`
- **Rückgabe:** Keine (Toast-Erfolgs-/Fehlermeldung)
- **Verfügbarkeit:** NUR in der Android WebView. Auf einer reinen Web-Version ist `KompendiumApp` undefiniert.

### 2.2 `KompendiumApp.printPage()`
- **Aufruf:** `KompendiumApp.printPage()`
- **Wird aufgerufen von:** `window.print` Überschreibung in `onPageFinished` injected JavaScript
- **Funktion:** Druckt die WebView als PDF (ISO_A4, NO_MARGINS) via Android `PrintManager`
- **Rückgabe:** Keine
- **Verfügbarkeit:** NUR in der Android WebView.

---

## 3. window.KOMP JavaScript-API

Definiert in `app.js` (Zeile ~1580-1583 des Originals), exportiert als:

```javascript
window.KOMP = {
  // === Speicher & State ===
  Store,           // Speicher-Abstraktion (localStorage mit Fallback)
  S,               // Aktueller Anwendungszustand (gaps, done, cards, quiz, notes, darf, exam, endtest, prefs)
  state: function(){ return S; },          // Gibt den aktuellen State zurück
  mode: function(){ return mode; },         // Gibt den aktuellen Modus zurück (blaettern, inhalt, suche, etc.)

  // === Navigation & Modus ===
  setMode,         // setMode(m) - Modus wechseln: 'inhalt','blaettern','suche','geschafft','karten','exam','foto','fortschritt','quellen','info'
  goTo,            // goTo(i) - Zu Index i springen
  goToId,          // goToId(id) - Zu Seite mit data-id springen
  next,            // next() - Nächste Seite
  prev,            // prev() - Vorherige Seite
  rebuild,         // rebuild(keepId, force) - Liste neu aufbauen
  list: function(){ return list; },   // Gibt alle Seiten zurück
  idx: function(){ return idx; },     // Gibt aktuellen Index zurück
  weiter,          // weiter() - Weiter (mit LE-Checkpoint-Handling)
  stepInfo,        // stepInfo(a) - Schritt-Info für aktuelle Seite

  // === Antworten & Interaktion ===
  answer,          // answer(mod, qi, oi) - Multiple-Choice-Antwort (Checkpoint)
  darfAnswer,      // darfAnswer(i, v) - Ja/Nein/Absprache-Antwort
  endAnswer,       // endAnswer(k, v) - Abschluss-Test-Antwort
  openSolution,    // openSolution(a, open) - Lösung einer Seite öffnen/schließen
  evalTask,        // evalTask(task) - Aufgabe auswerten
  setGap,          // setGap(g, val) - Lückentext-Eintrag setzen
  checkGap,        // checkGap(g, val) - Lückentext prüfen
  normAns,         // normAns(s) - Antwort normalisieren (für Vergleich)
  isDone,          // isDone(a) - Prüfen ob Seite erledigt
  clearAll,        // clearAll(ask) - Alle Daten löschen (mit Bestätigung)
  restoreAll,      // restoreAll() - Alle gespeicherten Daten wiederherstellen

  // === Druck ===
  prePrint,        // prePrint() - Vor dem Druck vorbereiten
  postPrint,       // postPrint() - Nach dem Druck zurücksetzen
  setPrintOrder,   // setPrintOrder() - Druckreihenfolge setzen
  onlyFillOn,      // onlyFillOn() - Prüfen ob nur Ausfüllseiten angezeigt werden
  syncAllBox,      // syncAllBox() - Checkbox "Alle Seiten zeigen" synchronisieren
  setTempAll: function(v){ tempAll=!!v; syncAllBox(); },  // Temporär alle Seiten anzeigen

  // === Prüfungsfragen (Karten) ===
  showCard,        // showCard() - Aktuelle Karte anzeigen
  flip,            // flip() - Karte umdrehen (Lösung zeigen)
  rate,            // rate(v) - Karte bewerten (known/unsure/unknown)
  sureCount,       // sureCount(mod) - Anzahl sicherer Fragen pro Modul

  // === Selbstcheck (Exam) ===
  startExam,       // startExam(n) - Neuen Selbstcheck mit n Fragen starten
  evalExam,        // evalExam() - Selbstcheck auswerten

  // === Fortschritt ===
  updateProgress,  // updateProgress() - Fortschrittsanzeige aktualisieren
  flashSaved,      // flashSaved() - "Gespeichert"-Flash anzeigen

  // === Suche ===
  focusSearch,     // focusSearch() - Suchfeld fokussieren
  onScroll,        // onScroll() - Scroll-Handler
  norm,            // norm(s) - Text normalisieren (für Suche)
  findRanges,      // findRanges(s, terms) - Trefferpositionen finden
  highlight,       // highlight(terms) - Treffer im Text markieren

  // === Menü ===
  openMenu,        // openMenu() - "Mehr"-Menü öffnen
  closeMenu,       // closeMenu() - "Mehr"-Menü schließen

  // === Export/Import ===
  exportData,      // exportData() - Alle Daten als JSON-Objekt exportieren
  importData,      // importData(obj) - JSON-Daten importieren

  // === Sonstiges ===
  handleSwipe,     // handleSwipe(dx, dy) - Wisch-Geste verarbeiten
  bg: function(){ return BG; },       // Hintergrund-Objekt zurückgeben
  bgTurn,          // bgTurn(dir) - Hintergrund-Seitenumblättern-Animation
  openMenu, openMenu, closeMenu,      // Duplikat in Original
};
```

### 3.1 Interne Strukturen (nicht öffentlich, aber relevant)

| Struktur | Inhalt |
|---|---|
| `S.gaps` | Lückentext-Eingaben `{ key: wert }` |
| `S.done` | Erledigte Seiten `{ id: true }` |
| `S.cards` | Prüfungskarten-Bewertungen `{ index: 'known'\|'unsure'\|'unknown' }` |
| `S.quiz` | Checkpoint-Antworten `{ mod: { qi: oi } }` |
| `S.notes` | Notizen-Eingaben `{ id: text }` |
| `S.darf` | "Darf ich das?"-Antworten `{ index: 'ja'\|'nein'\|'absprache' }` |
| `S.exam` | Selbstcheck-Ergebnis `{ date, score, total, per }` |
| `S.endtest` | Abschluss-Test-Antworten `{ k: wert }` |
| `S.prefs` | Benutzereinstellungen `{ onlyfill, mode, pos }` |
| `DATA` | Statische Daten: `version`, `cardmods`, `glossary`, `modules`, `cards`, `quiz` |
| `HEFT_MAPPING` | Kursheft-Zuordnung `{ le: {...}, seiten: {...} }` |
| `pages` | Array aller `article.page`-Elemente |
| `list` | Gefilterte/sortierte Seitenliste für aktuellen Modus |
| `idx` | Aktueller Index in `list` |
| `mode` | Aktueller Anzeigemodus |

### 3.2 CSS-Klassen und Data-Attribute (für JS-Abhängigkeiten)

Die App verlässt sich auf folgende HTML-Klassen und Data-Attribute:

| Selektor/Attribut | Bedeutung |
|---|---|
| `article.page[data-id="..."]` | Jede Lernseite |
| `article.page[data-fill="1"]` | Ausfüllseite (zählt für Fortschritt) |
| `article.page[data-le="1..11"]` | Lerneinheits-Zuordnung |
| `article.page[data-mod="E\|M1..M7\|A"]` | Modul-Zuordnung |
| `article.page[data-type="aufgabe\|zusammenfassung\|situation\|querverweis\|notizen\|checkpoint"]` | Seitentyp |
| `.gap[data-key="..."]` | Lücke mit Schlüssel |
| `.gap-in` | Eingabefeld für Lücke |
| `fieldset[data-mod][data-q="..."]` | Multiple-Choice-Frage |
| `fieldset.darf[data-i="..."][data-a="..."]` | Ja/Nein/Absprache-Frage |
| `fieldset.et[data-k="..."][data-right="..."]` | Abschluss-Test-Frage |
| `details.loesung` | Lösungselement |
| `#exportlink` | Export-Link (triggers `KompendiumApp.saveProgress`) |
| `#markdone` | "Diese Seite erledigt"-Button |
| `#allsol` | "Alle Lösungen dieser Seite zeigen"-Button |

---

## 4. Abhängigkeiten zwischen den Dateien

```
index.html
  ├── style.css (alle Styles)
  ├── app.js (window.KOMP API, gesamte Logik)
  ├── robot-navigation.js (RobotNav v2.8.0, eigenständig)
  ├── assistent.js (Assistent v1.0, eigenständig)
  └── manifest.json (PWA-Manifest)

sw.js (Service Worker, eigenständig, cachet index.html + Assets)

MainActivity.java (Android)
  ├── WebViewAssetLoader (lädt index.html aus assets/)
  ├── ServiceWorkerControllerCompat (SW-Support)
  ├── KompendiumApp JS-Bridge (saveProgress, printPage)
  └── onPageFinished injects JS für #exportlink und window.print
```

---

## 5. Synchronisation Android-Asset ↔ Web-Version

| Aspekt | Android (WebView) | Web (PWA/GitHub Pages) | Handlungsbedarf |
|---|---|---|---|
| Entry-Point | `https://appassets.androidplatform.net/assets/index.html` | `./index.html` | Pfade in `sw.js` prüfen |
| JS-Bridge `KompendiumApp` | ✅ Verfügbar | ❌ Undefiniert | `window.KOMP` muss fehlende Bridge abfangen |
| Speicher | `localStorage` + `KompendiumApp.saveProgress` (Downloads) | `localStorage` + `download()` (client-seitig) | `exportData`/`importData` bereits vorhanden |
| Datei-Import | `<input type="file">` | `<input type="file">` | ✅ Bereits vorhanden |
| Offline-Cache | `sw.js` + `WebViewAssetLoader` | `sw.js` | ✅ Bereits vorhanden |
| Druck | `KompendiumApp.printPage()` | `window.print()` | `printWithSolutions` nutzt `window.print()` |

---

## 6. Versionskonsistenz (Stand November 2026)

| Datei | Version |
|---|---|
| `build.gradle` (app) | `versionCode 295`, `versionName '2.9.5'` |
| `manifest.json` | `"version": "2.9.5"` |
| `sw.js` | `VERSION = '2.9.5'`, `BUILD = 'web-pwa-2.9.5'` |
| `index.html` (title) | `v2.9.5` |
| `README-ANDROID.md` | `v2.9.5` |

**Alle stimmen überein.** Bei jeder Änderung müssen alle 5 Stellen synchron aktualisiert werden.

---

## 7. Backup-Checksummen (SHA-256)

Erstellt am 16.11.2026, gespeichert in `BACKUP_2026_11_16_Phase0/`:

| Datei | SHA-256 |
|---|---|
| `app/src/main/assets/index.html` | `F875EE8C229A765F4E4CFEB16DDAED253DF667F3040497021E21788803A18417` |
| `app/src/main/assets/style.css` | `3A79CC1501F9EE7927E8AF631C23762BE92EE36DD9D774AD910BFE7FEA9333F7` |
| `app/src/main/assets/app.js` | `A98DBB2BECBC98DE64EA155E1104371BEA07130BB224A0D6AB2A7254B22DBC5F` |
| `app/src/main/assets/robot-navigation.js` | `A9424CABE94BD87B17B5DB67D9F42CC72DDD060F6BC7871E95772B1208DEA057` |
| `app/src/main/assets/assistent.js` | `FE2CAD848B948E3258224A10CAD3061B20790DB230EC8C99DAABF9567B47472C` |
| `app/src/main/assets/manifest.json` | `C7947A54C6D934900D3B4D1E5D801ACD287F3B8106624EA8E274315A03DEB85E` |
| `app/src/main/assets/sw.js` | `32F5F7D318039F97FE3F1F6C473C63F86EC76910921861816F5BA641F5528DBC` |
| `app/src/main/AndroidManifest.xml` | `1D1C0B6CE7BB9ACF9CF93E273404E341C13C78653D7E9F6CB7A547430B1C4EDD` |
| `app/build.gradle` | `3DE28093D7070150F609EEBE707CC2C3BF1454FA1175346242E59B2677A17EF9` |
| `build.gradle` | `96A33EDB21D173DA2C36F5312F50CDFB9F71D9F5078C081C81F2D029547F6CB9` |
| `gradle.properties` | `D6EDBC44206270CA0230BF5512DBEF7796926221D776B24895C59A0D7F28A972` |
| `settings.gradle` | `2ACADD2ECA66A153D4BEF78E933C831491AD96C1D51C9F665A2A5A6FE16A6F98` |
| `README-ANDROID.md` | `26AE3503900BBCA9697BBA0D6179653BB7514A1ACF28180909ED82E61E9D83CB` |
| `app-arm64-v8a-debug.apk` | `CD02BC901C357A52FD68536167116A4DC51F0FDD220302CAC7367D12BD14BA77` |
| `app-universal-debug.apk` | `CD02BC901C357A52FD68536167116A4DC51F0FDD220302CAC7367D12BD14BA77` |
| `app-x86_64-debug.apk` | `CD02BC901C357A52FD68536167116A4DC51F0FDD220302CAC7367D12BD14BA77` |

---

## 8. Abnahmekriterien Phase 0 (erfüllt)

| Kriterium | Status |
|---|---|
| Repository-Bestand gesichert (SHA-256) | ✅ |
| Ist-Zustand dokumentiert | ✅ |
| `index.html` Struktur analysiert | ✅ |
| CSS/JS modular ausgelagert | ✅ |
| `window.KOMP` API dokumentiert | ✅ |
| Android-JavaScript-Bridge dokumentiert | ✅ |
| Gradle-Build erfolgreich | ✅ (`BUILD SUCCESSFUL` in 2s) |
| Keine Funktionsverluste (API intakt) | ✅ |

---

## 9. Nächste Schritte (Phase 1+)

Vor jedem weiteren Schritt:
1. **Backup erneut erstellen** (neue SHA-256)
2. **Änderung in einer Datei** (CSS oder JS)
3. **Gradle-Build** muss `BUILD SUCCESSFUL` liefern
4. **Funktionstest** der betroffenen API-Methoden

Empfohlene Reihenfolge:
1. Phase 1: Design-System & Barrierefreiheit (WCAG 2.2 AA)
2. Phase 2: Assistent → Kontextbewusster AI-Lern-Bot
3. Phase 3: Top-10-Ideen (SRS, Adaptive Difficulty, AI-Fehleranalyse, etc.)
