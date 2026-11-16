# Web-Deployment: Vercel (und GitHub Pages) – Stand 17.11.2026

Kurzanleitung und Entscheidungsgrundlage, das Lern-Kompendium dauerhaft im Web
laufen zu lassen. Geprüft an Code und Doku am 17.11.2026; Quellen sind verlinkt.

---

## 1. Ausgangslage (geprüft)

- Die Web-App unter `app/src/main/assets/` ist eine **reine statische PWA**: kein
  Build-Schritt, keine Paketverwaltung, kein Backend, keine externen Requests
  (CSP `default-src 'self'`, `connect-src 'self'`), alle Pfade relativ
  (`./manifest.json`, `bg/d/z00.webp`). Der Service Worker registriert sich nur
  auf http(s) (Z. 779-784 in `app.js`); auf dem Android-Asset-Origin bleibt er aus.
- `localStorage` mit In-Memory-Fallback; ohne APK-Bridge greifen automatisch die
  Web-Fallbacks (Sicherung = Datei-Download, Druck = Browser-Dialog).
- `vercel.json` (Repo-Wurzel) sagt Vercel: `outputDirectory = app/src/main/assets`,
  `cleanUrls`, `trailingSlash: false`, `sw.js` und `manifest.json` werden frisch
  ausgeliefert (`max-age=0, must-revalidate`) – nötig, weil der Service Worker
  cache-first arbeitet und sonst alte Stände überleben.
- **Live-Fund:** GitHub Pages ist aktiv und liefert bereits eine Web-Version aus –
  aber auf dem Stand **v2.9.5** (Branch `main`). Der aktuelle Stand 2.10.0 liegt
  auf Branch `android-wrapper-2.10.0`.

## 2. Warum Vercel passt (Grenzen, Stand der Doku)

- Statische Seiten zählen bei Vercel **nicht als Build** (»Hosting static files
  such as an index.html file is not classed as a build«,
  <https://vercel.com/docs/limits>). Hobby reicht für dieses Projekt:
  100 Deployments/Tag, 5 Deploy-Hooks pro Projekt, 60 Hook-Aufrufe/Stunde,
  Quell-Upload-Limit 100 MB (das Projekt ist ~3 MB).
- Bekannte Vercel-PWA-Probleme aus der Community (Stack Overflow/GitHub
  Discussions) betreffen fast ausnahmslos **Bundler-Builds** (Workbox/next-pwa
  »bad precaching response«, SW in `/_next/static`, SvelteKit-SW-Scope). Für ein
  handgeschriebenes SW-Skript im Wurzelordner der Ausgabe – wie hier – greifen
  diese Fallen nicht. Lehre daraus: `sw.js` **muss** im Wurzelverzeichnis der
  Ausgabedateien liegen, damit der Scope auf die ganze Seite passt. Genau so ist
  `vercel.json` gebaut.
- Deploy-Hook: eine URL, die per POST ohne Login ein Deployment auslöst
  (<https://vercel.com/docs/deploy-hooks>). Basis für Option C.

## 3. Drei Wege, das Kompendium live zu bekommen

### Weg A – Vercel-Token + CLI (schnellster Weg, einmalig ~2 Minuten)

Wer die Schritte nicht klicken will, gibt einmalig einen Token weiter; das
Deployment läuft dann vom eigenen PC aus (`npx vercel@latest --prod --yes
--token <TOKEN>`). Der Token wird **nirgends gespeichert, nicht committet, nicht
ins Repo geschrieben**; danach kann er auf <https://vercel.com/account/tokens>
wieder gelöscht werden. Danach trotzdem Weg B Schritt 4 setzen (Production
Branch), damit künftige Pushes automatisch deployen.

### Weg B – Vercel-Git-Integration (danach vollautomatisch, empfohlen)

1. <https://vercel.com/signup> → »Continue with GitHub«.
2. <https://vercel.com/new> → Repo `AnFoVO-Lernkompendium` → **Import**.
3. Framework: **Other** · Build Command: *leer* · Output Directory:
   `app/src/main/assets` → **Deploy**.
4. Project → **Settings → Git → Production Branch**: `main` ersetzen durch
   `android-wrapper-2.10.0` → Save → **Deployments → ⋯ → Redeploy**.

Schritt 4 ist Pflicht: `main` enthält älteren Stand (2.9.5) ohne `vercel.json`;
ohne die Umstellung würde Vercel den falschen Zweig ausliefern.

### Weg C – GitHub Actions + Deploy-Hook (optional, ohne Token im Repo)

Wenn das Projekt in Vercel existiert: Settings → Git → Deploy Hooks → Hook für
Branch `android-wrapper-2.10.0` anlegen, URL als Repository-Secret
`VERCEL_DEPLOY_HOOK` hinterlegen, dann z. B.:

```yaml
name: Vercel Deploy Hook
on:
  push:
    branches: [android-wrapper-2.10.0]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: curl -fsS -X POST "$VERCEL_DEPLOY_HOOK_URL"
        env:
          VERCEL_DEPLOY_HOOK_URL: ${{ secrets.VERCEL_DEPLOY_HOOK }}
```

Nur sinnvoll, wenn die native Git-Integration (Weg B) nicht genutzt werden soll.

### Seitenhinweis GitHub Pages

Pages läuft bereits (`https://lowgiga.github.io/AnFoVO-Lernkompendium/`), aber
aus `main` = v2.9.5. Wer Pages behalten will: Settings → Pages → Source auf
Branch `android-wrapper-2.10.0` umstellen. Vercel und Pages parallel zu betreiben
ist möglich, aber unnötig – eine Quelle reicht.

## 4. Nach dem Deployment: korrekte Nutzung

1. **Versionsabgleich prüfen:** Live-URL öffnen → Titel/Fußzeile zeigt
   `2.10.0`; Selbsttest unter `https://<domain>/?test=1` (106/106 erwartet;
   vor Wiederholmessung SW-Registrierung aufheben und `caches.keys()` löschen,
   siehe README Abschnitt 7).
2. **Update-Regel:** Code ändern → committen → pushen (Vercel deployt
   automatisch). Zusätzlich in `sw.js` `VERSION`/`BUILD` erhöhen, sonst liefert
   der cache-first-Cache bei Rückkehrern den alten Stand.
3. **PWA:** Auf dem Handy in Chrome öffnen → »Zum Startbildschirm hinzufügen«.
   Das APK bleibt parallel für die reine Offline-Verteilung.
4. **Sicherungen/Druck:** laufen im Browser über Download bzw. Druckdialog.

## 5. Bekannte Störquellen (kein Eingreifen nötig, nur Wissen)

- **Gradle-Dependency-Submission (rot):** GitHub legt für Gradle-Projekte
  automatisch ein »dynamic«-Workflow an (`dynamic/dependency-graph/
  auto-submission`); es scheitert, weil der Runner nicht das projektübliche
  JDK 21 bereitstellt. Abschaltbar: Settings → Code security and analysis →
  Dependency graph. **Ohne Einfluss auf Vercel** – Vercel deployt die Dateien,
  nicht die Actions-Ergebnisse.
- **Impressum (G3 aus README Abschnitt 10):** Fußzeilen-Platzhalter vor einer
  öffentlich beworbenen URL füllen (§ 5 DDG); für private Nutzung bedeutungslos.

## 6. Risiken für »dauerhaft«

- Kostenloser Hobby-Tarif ist für **nicht-kommerzielle** Nutzung vorgesehen;
  bei Unsicherheit → Pro-Tarif. Seiten selbst ändern sich nie; nur das Konto
  (bzw. GitHub-Zugriff) muss existieren.
- Repo/Branch darf nicht gelöscht werden; `backups/` und Git-Tags
  (`v2.10.0`, `v2.9.5-baseline`) halten den Stand zusätzlich fest.