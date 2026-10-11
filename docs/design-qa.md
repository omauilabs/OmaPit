# OmaPit design and verification

Compared the source concept in `../plugin-designs/omapit.png` against the rendered `preview-desktop.png` together.

Preserved: Tokyo Night palette, prominent blue/amber readings, overhead kettle asset, chart with next-action column, four-stage timeline, dinner target and event journal. Replaced fictional shell surroundings with an explicitly labeled local-preview bar. Removed unconnected weather, device identity and prediction claims. The generated kettle is an illustration, not an identified connected grill.

Desktop: 1280 px wide full-page screenshot inspected. All panels and footer rendered, no collisions. Mobile: 390 px viewport, DOM document width 390 px (no horizontal overflow); responsive single-column layout observed, but the browser's screenshot scaling prevented a high-confidence pixel-level mobile inspection. Full native layout remains unverified.

Browser workflow verified: required wrap checks, stage progression to wrap, save note, change unit, reload persistence, finish and archive, create manual cook, enter two readings, inspect completed history, restore an explicit demo. Modal focus wraps via Shift+Tab. Browser error/warning log empty on the final built page. JSON export exists but the downloaded file was not inspected during this pass.

Storage: 9 tests passed. Production build passed (605 KB JS bundle warning; code splitting remains a future optimization). Native QML was checked against official palette declarations and corrected to supported tokens, but no QML runtime/compiler is available on this Mac. Do not infer native acceptance from browser results.

## 0.2.0 device build

Added Devices navigation and two-channel cards. Desktop screenshot `preview-devices.png` inspected; 390 px mobile screenshot inspected with no horizontal overflow. Temperature-unit switching updates both cards. Browser error/warning log empty. Cards use synthetic replay fixtures, not real device readings. BLE scan failure, capture address redaction, parser formats, source isolation, per-channel freshness, migration and recording are covered by 24 passing tests. Production build passed after restoring locked dependencies. No radio scan or Linux QML runtime test performed.

## 0.2.1 live fire

Visually inspected the live logo and grill effects in the running browser. All three WebGL canvases compiled and rendered without console warnings/errors. Captured two frames and confirmed changed pixels separately in the logo and grill regions. Atmosphere pause held all frame counters unchanged; resume increased them. System reduced-motion and visibility/offscreen behavior are implemented; system preference switching and context loss were not force-tested. Screenshot: `preview-fire.png`. Native effects remain unported.

## 0.3.0 meal workbench

All five software stages completed. Desktop and 390 px mobile workbench views inspected; no horizontal overflow across Meal, Timeline, Recipes, Insights, Alerts and Devices. Timeline screenshots saved as preview-timeline.jpg and preview-timeline-mobile.jpg. Recipe and photo persistence verified after reload; complete backup contents verified including the photo. Actual in-app browser Blob download remains unconfirmed, with a copyable export dialog provided. 59 Python tests and four Sites packaging tests passed; frontend build passed with a bundle-size warning. Final browser warning/error logs empty. See RELEASE-ACCEPTANCE.md for hardware, native and prediction limits.

## 0.4.0 guided coordination

Guided two-food setup, task persistence, phone manual reading → target alert → snooze, explicit task completion and saved next-time notes exercised in an isolated browser journal. Phone view and Timeline inspected at 390 px with no horizontal overflow. Mobile navigation was corrected from five cramped columns to a focused four-control row with All tools expansion. Screenshots saved as preview-phone-v04.jpg and preview-companion-v04.jpg. Final browser log empty. Production build is split into application/runtime/charts without Vite size warnings. 69 Python and four packaging tests pass. Native QML controls remain source-only; no Linux runtime or screen-reader acceptance occurred.

## 0.4.1 navigation organization

Replaced the flat ten-item primary bar with Cook, Plan and Journal. Each shows only its contextual views; Devices remains a separate utility. Browser area switching and remembered Recipes selection verified, primary labels checked, and a 390 px phone screenshot inspected with document width 375 px and no horizontal overflow. Viewport reset. Browser console warning/error log empty. Production build and four Sites packaging tests passed. Updated native QML grouping, with native runtime acceptance still open. Screenshots: preview-navigation.jpg and preview-navigation-mobile.jpg.

## 0.4.2 notification bell

Moved the browser notification bar into a top-right bell beside Devices and the unit toggle. Desktop/mobile panel placement inspected; mobile document width 375 px at a 390 px viewport, without horizontal overflow. Verified opening, Escape dismissal, outside-click dismissal and the link to alarm rules/delivery health. Permission and notification delivery were not exercised. Urgent cook alarm banners remain separate. Production build and four packaging tests passed; final browser warning/error log empty. Screenshot: preview-notifications.jpg.
