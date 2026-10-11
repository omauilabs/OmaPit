# OmaPit 0.4.0 — meal coordination

October 4, 2026. Builds the recommended guided setup → next-action panel → grill-aware planning → phone view order, with supporting service health, journal review, onboarding and performance improvements.

## Delivered

Guided setup creates a new meal atomically: one grill, up to eight foods, manual or available probe mappings, personal targets, capacity units, preheat/prep/cook/rest/optional hold durations, serving date and target alarms. Existing journals must be finished explicitly; setup never overwrites them. Additional independently controlled grills/zones can be added in Timeline.

Next actions prioritize unsnoozed/unacknowledged alarms, stale samples, elapsed running estimates and ready steps. Task starts persist, dependency checks prevent premature progression, and active grill conflicts reject starts. An expired estimate does not release a running grill reservation; completion requires confirmation. Grill scheduling can overlap compatible tasks within capacity and separate temperatures more than 25°F apart. Unknown temperatures reserve exclusive time. Resource allocation is a greedy planning heuristic, not globally optimized; feasible completion estimates depend on entered durations. Resources assume independent temperature control. Resting/holding tasks are off-grill by default; reserve another zone explicitly if they use equipment. Temperature changes between tasks need user-entered transition tasks where required; the app does not infer heating/cooling rates.

At the grill provides large readings, manual entry and alarm acknowledgement/snooze controls. On small screens it shows four navigation controls with an All tools expansion. `/#grill` opens this view directly. It needs a reachable service; authenticated HTTPS phone access remains an owner setup step. It does not add offline/background phone alerts.

Insights records next-time notes and compares estimated versus actual task durations where a start was recorded. Notes are your observations, rather than automatically inferred causes. A restored backup retains completed task timings, clears unfinished running states, pauses alarms and resets hardware mappings.

The background monitor publishes a committed heartbeat. Alerts exposes that health alongside delivery attempts. The companion systemd template supports startup and restart on failure; it is included but not installed on this Mac. Native QML includes guided main/optional-side setup, next actions, task starts and grill reservations. Full browser/native parity and Linux runtime acceptance are not claimed.

## Validation

- 69 Python tests passed, including atomic guided setup/rollback, capacity and temperature conflicts, forward/backward reservations, dependency guards, elapsed estimates retaining physical occupancy, backup/review preservation and committed HTTP monitor heartbeat.
- Four Sites packaging tests passed. Production build passed without chunk-size or circular-chunk warnings; application, runtime and charts are separate bundles (approximately 83 / 280 / 311 KB uncompressed). Later 0.4.x builds added a lazily loaded three.js bundle, split into two chunks in 0.4.2 to stay under the 500 KB warning; see RELEASE-0.4.2.md.
- Browser acceptance used an isolated database. Created chicken and corn through all three setup steps, started a preheat step, reloaded and confirmed persistence, logged a phone reading that triggered a target alarm, snoozed it and completed the step. Saved a next-time note and verified it after reload.
- Phone view and Timeline checked at 390 px; document width 375 px, with no horizontal overflow. Focused mobile navigation and full navigation expansion inspected. Viewport reset afterward. Final browser warning/error log empty.
- Keyboard navigation now focuses screen headings after a view change. Screen-reader and native accessibility testing remains open. Smaller-screen decorative effects use a capped 1× render scale; low-end GPU performance has not been benchmarked.
- Screenshots: preview-phone-v04.jpg and preview-companion-v04.jpg.

## Next acceptance: your CHEF iQ thermometer

Confirm the exact probe model and protocol, discover supported live packets, compare food and ambient readings with the manufacturer app, map the food channel, and verify original timestamps and stale behavior. Then test disconnect/reconnect, known battery data and alarm delivery while the browser is closed. CQ50/CQ60 remain experimental until this physical test. Native Linux, actual Home Assistant/MQTT endpoints, phone push and real-cook prediction calibration are separate open gates.
