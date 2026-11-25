# Build report — AnFöVO Learning Compendium v2.9.5

## Team integration: standalone RobotNav architecture

- Adopted the parallel wrapper workstream: `index.html` now loads the RobotNav engine via `<script src="robot-navigation.js">` instead of an inline embedded block; the engine file is a first-class asset.
- `sw.js` precaches `./robot-navigation.js` and supports a `skip-waiting` message for faster service-worker updates.
- Learning content unchanged: the embedded `DATA` literal differs from v2.9.4 only in the `DATA.version` metadata (`2.7.0` → `2.9.5`). The raw literal SHA-256 values are `784d2d3325a0232b3fce12cdd7c597691a86ce0dcbbc95700ba028b0af958859` (v2.9.4) and `d20941f4fb08a573ad317191e45d113baea318d735bfd1a6969a65bffd9120ad` (v2.9.5); after normalizing only that version field, both literals are byte-identical and hash to the v2.9.5 value. The v2.9.4 animation overhaul (compositor-only transform/opacity, rAF-throttled parallax, reduced-motion aware) is carried over.
- Byte parity restored across all surfaces: root `index.html` == repo Android assets; `robot-navigation.js` identical in root, `algorithm/`, Android assets, and (at v2.9.5 release time) wrapper assets.
  **Update 17.11.2026:** The wrapper workstream has since moved to v2.10.0 (modular style.css/app.js/assistent.js, versionCode 296), so its copies have diverged by design. Parity within THIS repository (root == algorithm == android assets) is enforced by CI; the wrapper branch is a separate product line.
- Verification updated for the new architecture: `tests/verify-build.py` now checks the script reference and byte-parity of the engine copies (root ↔ `algorithm/` ↔ Android assets) instead of the embedded-block match; PWA precache expectation extended to 65 entries.

## Verified

- Android metadata: `de.omega.lernkompendium`, version `2.9.5`, version code `295`, min SDK 29, target SDK 36.
- Main CI run `45576060676` (commit `bc08f8965ac4`) succeeded on 25.11.2026, including static verification, browser tests, debug APK build, APK signature verification and artifact upload. The Pages deployment run `45576058286` also succeeded.
- The CI debug artifact `AnFoeVO-debug-apks/app-arm64-v8a-debug.apk` has SHA-256 `f9e2102437c0ff42ed9fe1cb362606e0bdbae618a6f8109514611b1b9f0ba298`. Its packaged `assets/index.html` is 628957 bytes with SHA-256 `242e2822d64d85fa4b9fbdee11aac74c88350f65337b6492a6e9479e7d1740dd`, matching the canonical repository blob.
- A separate local debug build with `applicationIdSuffix ".debug"` was installed side-by-side on the Galaxy S25 as `de.omega.lernkompendium.debug`; the release-signed v2.9.3 app remained installed and untouched. Cold start succeeded (66-317 ms) and the v2.9.5 assets rendered offline without a fatal exception. The interactive seven-point smoke checklist remains open in owner task `wq8cx2`.
- Clean local release build (Gradle 8.13, JDK 21, SDK 36, Build-Tools 36.0.0): `:app:assembleRelease` and `:app:bundleRelease` successful. `apksigner verify` passed; release certificate DN `CN=AnFoeVO Lernkompendium, OU=Development, O=Lowgiga, L=NRW, ST=NRW, C=DE`.
- Canonical source asset hashes used by the current build:
  - `assets/index.html` = `242E2822D64D85FA4B9FBDEE11AAC74C88350F65337B6492A6E9479E7D1740DD` (628957 B)
  - `assets/sw.js` = `D2A9DCEE65DE82FED29CCD3BA4F1A8D9F8E3FBC45745DD6FEC564637D49894B6`
  - `assets/robot-navigation.js` = `BC063B694F2C91EAD1995F0CE3B6894E81A15E2F7DE465232FB0BE5AC7FC5095` (21879 B)
- Static verification: 33/33.
- Browser suite `npm run test:all` green: RobotNav harness, smoke (70 pages, 0 errors), PWA subpath (65 precached entries incl. the engine file) and the 100/100 in-app self-test.

## Historical local wrapper artifacts (17.11.2026)

| Artifact | SHA-256 |
| --- | --- |
| `app-arm64-v8a-debug.apk` | `844CFC34106886B994ADC7D078F1749E283B848701182286F65321BA884645F7` |
| `app-arm64-v8a-release.apk` | `063FF7D92657C354C467931743D9C1B879EA0055B31FD0E3E6F4E217D69BA1FB` |
| `app-release.aab` | `180D5E4F112F8A444FD259C173F2AFA7D8055286E915559CD34E1880BA04457A` |

## Status

- Service worker cache: `anfoevo_v2_cache_2.9.5-web-pwa-2.9.5`; `2.9.4` no longer present.
- Galaxy S25 verification is current: release v2.9.3 remains installed; a separate v2.9.5 debug app was installed side-by-side and cold-started successfully. Only the interactive seven-point smoke checklist is still open.
- GitHub Release v2.9.4 (animation update, embedded architecture) remains published; v2.9.5 is the canonical follow-up with the standalone-engine architecture.
- GitHub Pages is public and the live `index.html` still contains the DDG Impressum placeholder; the documented publication gate is therefore not met. The placeholder must be replaced with real legal-contact details or Pages must be disabled.

## Rebuild

```powershell
$env:ANDROID_HOME="C:\Users\doli\Downloads\android-sdk"
$env:KOMPENDIUM_KEYSTORE="C:\Users\doli\Downloads\AnFoeVO-Release-Keystore\anfoevo-release.jks"
$env:KOMPENDIUM_STORE_PASSWORD="<see AnFoeVO-Release-Keystore\CREDENTIALS.txt>"
$env:KOMPENDIUM_KEY_PASSWORD="<see AnFoeVO-Release-Keystore\CREDENTIALS.txt>"
$env:KOMPENDIUM_KEY_ALIAS="anfoevo-release"
Set-Location android
.\gradlew.bat --no-daemon clean :app:assembleDebug :app:assembleRelease :app:bundleRelease
```

Run the Gradle command from the repository's `android/` directory as shown above. Repo checks from the repository root: `python tests/verify-build.py`; `cd tests; npm run test:all`.
