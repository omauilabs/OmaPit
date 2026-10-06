# OmaPit 0.4.2 — developer preview

October 5, 2026. Tagged as a pre-release. This is a software milestone for the browser preview and Python store; it is not a verified catalog release.

## Since 0.4.0

- 0.4.1: navigation grouped into Cook, Plan and Journal, with Devices as a separate utility. The browser remembers the last view per area during the session.
- 0.4.2: browser notification status, permission and test controls moved into a bell popover beside Devices and the unit toggle. Urgent cook alarms stay visible separately.
- Also in this build: Equipment & fire guides, the Meat market USDA snapshot, cut and sauce explorers, and the owner-authorized visual bundle (see ASSET-LICENSES.md and ROADMAP.md).
- Continuous integration runs the Python, community benchmark and packaging tests plus the production build on every push and pull request.
- The lazily loaded three.js bundle is split into two chunks so the production build is free of size warnings (see Bundle size).

## Software validation

- 69 Python tests and 14 community benchmark tests pass.
- Four Sites packaging tests pass. `npm ci` and `npm run build` succeed from a fresh checkout without chunk-size warnings.
- The preview server started against an isolated database with `--seed-demo`; desktop and 390 px layouts rendered without horizontal overflow or page errors.
- 3D cut viewer, checked in Chromium with software WebGL: the beef model loads, card and model selection highlight the matching region, and Rotate works. The only failed request was `/favicon.ico`; the app has no favicon.

### Bundle size

three.js builds as two chunks, `three-renderer` (about 358 KB uncompressed, 88 KB gzip) and `three` (about 285 KB, 76 KB gzip). Both load lazily, in parallel, only when the cut explorer opens a 3D model; neither is preloaded with the initial page. Each is under Vite's 500 KB warning, so the production build is warning-free again.

The split does not reduce total bytes: it was a single 640 KB chunk before. The WebGL renderer alone minifies to about 529 KB, so a real reduction would need a lighter renderer. That remains open work.

## Not verified

- **Native plugin:** the QML has not been loaded on Linux/Quickshell. Bar placement, panel open/close, dialogs, theme switching, keyboard navigation, window sizing, screen readers and end-to-end persistence remain open.
- **Hardware:** a CQ60 (protocol 4.0.0) delivered food readings during a hand-warming test (CHEFIQ-HARDWARE-TEST.md). Accuracy, ambient, battery, reconnection, range and alarm delivery remain unverified.
- **Integrations and delivery:** real Home Assistant/MQTT endpoints, desktop/ntfy notifications, phone push and background delivery during sleep or network loss.
- **Predictions:** evaluated only on synthetic sessions; real-cook accuracy and interval calibration are not claimed.
- **Notifications:** browser permission and notification delivery were not exercised for the bell popover.

## Known limitations

- The browser preview loads DM Sans and JetBrains Mono from Google Fonts; offline it falls back to system fonts.
- 3D cut models are committed directly (20–37 MB each), so clones are large.
- One active meal journal at a time; no fan/grill control or food-safety assessment.
