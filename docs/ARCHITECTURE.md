# Architecture
## Runtime architecture
index.html is the self-contained application shell and offline runtime (HTML, CSS and the app IIFE inline; the page data and learning content are inside it). Existing learning content, navigation, search, progress, notes, quizzes and print behavior remain inside the preserved application.
algorithm/robot-navigation.js is the maintained source module for the deterministic RobotNav algorithm. **Since v2.9.5 (`dcc4388`) the engine is loaded as a standalone file**: `index.html` references it with `<script src="robot-navigation.js">`; there is no embedded copy any more. The extraction is proven offline-safe by the CI parity gate (root == algorithm == Android assets, byte-identical) and the browser harness; `sw.js` precaches the engine.
## Logical components
1. Content layer: existing learning pages and learning assets.
2. Presentation layer: hybrid book stage plus conventional accessible reading interface.
3. Navigation layer: table of contents, page navigation, search and progress.
4. RobotNav layer: DOM inventory, obstacle cache, position planner, motion controller and event scheduler.
5. Persistence layer: existing browser-local progress and note storage.
6. Quality layer: static build verification and browser harness.
7. PWA shell: root `manifest.json`, `sw.js`, icons, and `bg/` frames, mirrored byte-for-byte into the Android asset directory. Relative URLs target the GitHub Pages project subpath `/AnFoVO-Lernkompendium/`. The worker registers only for `http:` and `https:` and skips both `android_asset` and `appassets.androidplatform.net` (verified in `index.html`), so the Android app stays offline via the asset loader, not via the worker. **GitHub Pages is active** and publishes the branch root — see `docs/GITHUB_PAGES.md` for the verified state and the clean-surface option.
## RobotNav contract
- Deterministic browser-side behavior; no LLM, agent loop or external service.
- Treat text, buttons, inputs, dialogs, media, links and logos as hard obstacles.
- Place the mascot only in verified free space near page margins.
- Debounce or schedule layout/scroll events; avoid continuous expensive DOM scans.
- Stop or rest while reading and honor reduced-motion preferences.
- Fail closed: if safe placement cannot be established, hide the mascot rather than cover content.
## Target repository structure
See the root directory tree in README. assets/book and assets/robot are reserved for local visual assets. Keep the HTML self-contained until asset extraction is validated.
## Change boundaries
Visual and navigation changes must not rewrite learning text. Content changes require a separate review and a content-diff report. Preserve sources and prior release archives.
