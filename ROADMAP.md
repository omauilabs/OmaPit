# OmaPit roadmap

Updated October 3, 2026. Scope: an Omarchy grilling companion with broad, evidence-backed thermometer compatibility and a useful cook journal. CHEF iQ CQ50 and CQ60 are both first-release integration targets. Exact ownership/model identification is not a prerequisite for developing the adapter architecture.

## Product promise

See the temperatures that matter, know when readings stop arriving, record decisions, and make the next cook better. Keep working locally where possible. Support multiple brands through adapters and bridges without requiring the maintainer to own every product.

Current baseline: manual readings, explicit demo, temperature history, wrap checklist, cooking stages, notes, fuel events, local SQLite history, browser JSON export. Storage and browser workflows tested. Native QML source exists but Linux runtime acceptance is outstanding. Experimental CHEF iQ decoder, BLE scan worker, selection, recording, and replay tools are implemented in 0.2.0. CQ60 protocol 4.0.0 live reception and warming response have been observed; complete hardware acceptance and native Linux testing remain open.

## Release sequence

| Milestone | Deliverable and user value | Completion gate |
|---|---|---|
| 0.2 — Device foundation | One device can expose food, ambient and battery channels; device picker; last-seen time; honest disconnected/stale states; capture/replay tooling | Automated fixtures cover multiple probes, partial updates, invalid values, unknown versions, restart and dropout; no fabricated live values |
| 0.3 — CHEF iQ alpha | Direct local BLE adapter targeting CQ50 and CQ60; one probe with internal and ambient channels; optional battery; automatic journal recording | Parser replay tests pass; at least one real-device session validates discovery, changing readings, loss/recovery and restart. Other variants stay experimental until independently tested |
| 0.4 — Omarchy beta | Native bar/widget installation, theme behavior, keyboard operation, multi-probe cook screen; configurable temperature and stale-data alerts | Linux/Quickshell acceptance; several-hour cook test; sleep/wake and adapter loss; alerts fire once per intended episode and recover correctly |
| 0.5 — Broad compatibility | Home Assistant entity bridge, documented MQTT ingestion, versioned JSON/CSV import; map sensors to foods and ambient positions | Contract tests plus real end-to-end bridge session; preserved timestamps and units; retained/stale MQTT samples cannot masquerade as fresh readings |
| 0.6 — Better cooks | Recipe-specific stages, editable targets, full event timeline, cook comparison, export/backup; explainable trend and stall suggestions | Useful workflow for brisket, poultry and short cooks; no hard-coded wrap prerequisite for every recipe; insufficient-data states tested |
| 1.0 — Public release | Published compatibility matrix, reproducible package, migration/rollback documentation, adapter developer guide, troubleshooting diagnostics | Native and persistence acceptance complete; no unsupported compatibility claims; published install/update path exercised on a clean Omarchy setup |

These are scope milestones, not promised dates. Hardware evidence and Linux validation determine readiness. Native testing can proceed alongside device work.

## How to cover hardware without buying it all

1. Reuse maintained protocol libraries where their license, interface and fixtures fit. Pin dependencies and record the upstream version/commit used.
2. Build adapters around protocol families and capabilities, not brand-name conditionals in the UI.
3. Ask volunteer owners for short local captures and a structured acceptance report. Do not require account passwords or cloud tokens in reports. No community outreach has been sent.
4. Replay captured advertisements through the exact production parser and store. Synthetic fixtures test failure handling; they do not establish device compatibility.
5. Use Home Assistant and MQTT as bridge paths for existing integrations. This expands ingestion options, but does not mean OmaPit directly supports every device available in those ecosystems.
6. Borrow hardware or recruit an owner only for gaps recordings cannot settle: discovery, radio range, pairing, firmware differences, reconnect behavior, power states and app coexistence. Buy a representative device only when it unblocks a high-priority protocol family.

A recording can prove decoding for those bytes. It cannot prove reliable live connectivity, battery accuracy, usable range or every firmware revision.

## Compatibility evidence

Maintain one row per model + firmware/protocol + transport + tested adapter version. Track these independently:

- Implementation: planned / experimental / implemented.
- Evidence: synthetic tests / real capture replay / owner-tested live / maintainer-tested live.
- Availability: direct BLE / bridge required / import only.

Never promote an entire brand based on one device. “Upstream verified” describes upstream evidence, not an OmaPit hardware test.

| Initial target | Path | Evidence available today | OmaPit status |
|---|---|---|---|
| CHEF iQ CQ60, supported V3 format | Direct BLE advertisements | Upstream library reports CQ60 verification with protocol 5.0.0 | Implemented experimentally; no OmaPit live test |
| CHEF iQ CQ50 / older layouts | Direct BLE advertisements | Upstream library implements V2/legacy but explicitly lacks real-hardware verification | Implemented experimentally; captures needed |
| Home Assistant temperature entities | Bridge | General integration approach; exact entities depend on installed device integration | Planned |
| MQTT publishers | Versioned ingestion contract | No universal thermometer MQTT schema is assumed | Planned |
| Other thermometer brands | Bridge first; direct adapter after feasibility review | Not assessed in this roadmap | Candidates, not supported |

Evaluate MEATER, ThermoPro, Inkbird, FireBoard and Combustion as candidates using: owner demand, documented/local interface, reusable implementation, licensing, firmware coverage, sample availability and maintenance cost. Do not promise a direct adapter before that review.

## Adapter and data design

Flow: transport → device decoder → normalized readings → cook store → QML/browser views and alert engine. Keep transport packages optional so manual mode stays usable without Bluetooth dependencies.

A device has stable local identity, reported model/firmware when available, adapter ID/version and capabilities. A reading has device/channel ID, semantic role (food/ambient/battery), value and unit, received time, source sample time if available, and quality. Record source type (manual/BLE/bridge/import/demo) and selected cook association.

Normalize incoming temperatures to the existing database's Fahrenheit convention for the first migration; convert only at display boundaries. Preserve original unit/value metadata for diagnostics. Do not silently reinterpret existing records. Add a versioned migration with backup/rollback documentation before modifying stored cooks.

Missing battery is unknown, never 0%. Reject sentinel/invalid readings. Never merge two probes into one identity. Preserve per-channel timestamps when advertisements carry partial updates. Unknown protocol layouts should produce an unsupported-format state, not guessed temperatures. Historical imports and replay data never become live alerts by default.

For CHEF iQ, label the second channel “Probe ambient.” It is measured at the probe, not a dedicated grate sensor. Replace the two-wired-probe illustration/labels with a wireless-probe view when that device is selected. Keep a generic layout for separately attached pit probes.

BLE and Wi-Fi are separate coverage paths: a direct BLE adapter needs a receiver near enough to the probe. It does not inherit the vendor hub's remote range. A nearby bridge may address placement; cloud access is a separately evaluated adapter.

## Capture and owner-test workflow

Local diagnostic command should list candidate devices, then capture only the selected device. Record relative timestamps, manufacturer/service payloads, protocol identification, RSSI and tool version. Replace hardware addresses with consistent aliases and remove unrelated scan data; let the owner inspect the bundle before sharing. Store no credentials. Document fixture origin, permission to redistribute, firmware when known and expected decoded values.

Owner acceptance: wake probe; observe plausible changing temperatures against the vendor display; confirm food/ambient channel mapping; dock/undock; allow readings to stop; restore reception; restart OmaPit; test multiple probes if available. Observe vendor-app coexistence rather than assume it. Use the probe within its manufacturer's operating instructions. Initial telemetry work is read-only; grill/fan control is a separate future scope.

## Immediate backlog, in dependency order

- [x] Add device/channel/source schema and migration tests.
- [x] Define adapter interface and compatibility manifest. See ADAPTERS.md; `backend/compatibility.py` validates claims.
- [x] Add recorded-data replay and malformed/partial/unknown-packet fixtures.
- [x] Wrap the CHEF iQ parser; dispatch by detected protocol, not guessed purchase year.
- [x] Add local scan/capture command and optional BLE dependencies.
- [x] Implement device selection, ambient/food mapping and freshness UI.
- [ ] Validate with the user's existing thermometer; request other-model captures only where needed.
- [ ] Run native Linux acceptance and correct QML issues before claiming Omarchy-ready status.

## Research sources and limitations

Reviewed October 3, 2026:

- [chefiq-ble](https://pypi.org/project/chefiq-ble/): passive CQ50/CQ60 advertisement parser, food/ambient/battery fields, V3 CQ60 verification and explicit V2/legacy verification limits. MIT; Python >=3.11. Evaluate dependencies before adoption.
- [CHEF iQ Home Assistant integration](https://github.com/ITSpecialist111/ChefIQ_Probe_HomeAssistant_Integration): existing community CQ60 integration to evaluate as a reference/bridge, not a guarantee of OmaPit compatibility.
- [Home Assistant Bluetooth](https://www.home-assistant.io/integrations/bluetooth/): transport ecosystem reference for future bridge design.

The checked backlog reflects implementation in 0.2.0. Live hardware acceptance remains outstanding.

## Visual enhancement progress — 0.2.1

Browser logo fire, grill smoke and ember shaders are implemented and visually verified. Motion preference, still-frame reduced-motion handling, hidden/offscreen pausing and static fallback are included. Qt shader integration and native acceptance remain part of the Omarchy beta milestone.

## Competitive review priorities — October 3, 2026

See [competitive research](COMPETITIVE-RESEARCH.md) for primary sources, parity assessment and acceptance targets. Prioritize software work in this order while hardware acceptance remains independent:

1. Persistent alert engine: target, pit bounds, stale data, known battery and timers; replay/restart verification.
2. Flexible recipe steps and editable targets, then multiple foods/probes and simultaneous timers.
3. Versioned bridge ingestion and compatibility evidence; phone awareness with explicit delivery limitations.
4. Dated meal execution timeline, richer journal, recipe import and backup/restore.
5. Evaluated prediction ranges and previous-cook learning.

The existing numbered releases remain scope milestones. These priorities bring alert and workflow development forward without claiming completion of the CHEF iQ live test or native acceptance. FireBoard is the alert/journal benchmark; Weber and MEATER guide execution parity; Crouton already combines recipes with Combustion hardware. Coordinated timers and recipe/probe integration are established ideas, so differentiation rests on mixed hardware, transparent reliability and integrated meal execution.

## Recommended software build order — implemented in 0.3.0

Updated October 4, 2026. The competitor-informed software sequence is implemented; the original hardware/native release gates remain outstanding.

| Stage | Implementation | Acceptance boundary |
|---|---|---|
| 1 · Reliable monitoring | Persistent alarm rules/episodes/history; threshold/stale/battery/timer; repeat, buffer, acknowledgement, snooze, recovery margin | Automated replay/restart tests and independent HTTP monitor test pass. Actual native/phone delivery pending |
| 2 · Flexible execution | Multi-food workflows, editable targets/steps, independent stages, probe mapping, named grill zones | Store tests and browser food/alarm workflow exercised. One active meal journal |
| 3 · Bridges and phone awareness | JSON contract, HA polling, exact-topic MQTT, model/evidence manifest, token-protected LAN mode, optional notify-send/ntfy | Contract/authentication tests and mocked desktop delivery pass. Real HA/broker/phone/push pending |
| 4 · Meal timeline and journal | Dated serving goal, dependency scheduling, editable durations, recipes/import/scaling/cooking mode, photos/outcomes, comparisons, CSV, backup/restore | Automated scheduling/persistence/restore tests and browser import/timeline/outcome workflows exercised. Independent tasks may overlap; resource capacity is not inferred |
| 5 · Predictions and personal learning | Experimental short-term trend ranges, abstention, held-out evaluator and per-food overlays with outcome notes | Synthetic behavior evaluation; no real-cook accuracy or calibrated intervals claimed |

Native Meal workbench source exposes core food/alarms/timeline/recipe/trend controls. Browser-only photos/comparison/download features remain identified. Qt shader parity and Linux runtime acceptance still remain from the original roadmap.

Next evidence gates: real CHEF iQ owner session; Linux/Quickshell load and keyboard/accessibility checks; HA/MQTT acceptance; real phone and notification tests; diverse recorded cooks for prediction evaluation. No additional feature backlog is silently marked complete by these software results.

## 0.4.0 meal coordination — October 4, 2026

Implemented guided setup, combined next actions, explicit grill capacity/temperature reservations and a focused phone view. Added actual task starts, saved next-time observations, service heartbeat, device onboarding, companion restart template and browser bundle splitting. See RELEASE-0.4.0.md for tested behavior and planning assumptions. Next gate is owner CHEF iQ hardware testing; Linux runtime, real notification delivery and prediction calibration remain open.

## 0.4.1 navigation — October 4, 2026

Grouped navigation around Cook, Plan and Journal with context-specific views and a separate Devices utility. Browser remembers the last view per area during the session. Native source follows the same grouping; Linux runtime remains unverified.

## 0.4.2 notification bell — October 5, 2026

Moved browser notification status, permission and test controls into a bell popover. Tagged as a developer pre-release with continuous integration for the software tests and build. three.js now builds as two lazily loaded chunks so the production build is free of size warnings; total bytes are unchanged. Added a favicon and phone home-screen icon. See RELEASE-0.4.2.md. Native Linux runtime and CHEF iQ field acceptance remain the gates before a stable release.

## Cut explorer expansion — requested October 4, 2026

Planned additions, after correcting and verifying the existing animal highlight alignment:

- [ ] Boar.
- [ ] Bison.
- [ ] Rabbit.
- [ ] Reindeer.

Each animal needs its own textured 3D model, species-specific cut catalog, realistic cut photos, and surface-aligned selectable regions. Model selection and cut-card selection must stay synchronized through rotation and zoom. Do not assume existing pork, beef or deer maps fit the new meshes.

Completion gates: inspect every region from both sides and oblique views; verify card-to-model and model-to-card selection; review anatomical labels and any shared panels; research and source species-specific cooking guidance before publishing it. These are roadmap items, not currently available species. Boar is listed once despite appearing twice in the request.

## Equipment & fire — October 4, 2026

Implemented 16 cooker families, eight woods with suggested food pairings, fuel-form compatibility notes, ten cooking methods, maintenance and seven troubleshooting topics. Each cooker has setup/shutdown guidance and linked owner references. Local cooker preferences and per-cooker checklists support setup/shutdown tracking, reset for the next cook and checklist-aware text exports. Checkmarks record user actions; they do not verify appliance safety or control hardware.

Remaining product work includes selected Atelier themes, poultry GLB integration, additional animal models and source-backed meat-market data. Hardware and native acceptance remain independent gates.

## Meat market — first source-backed slice

Added Plan → Meat market with nine reviewed beef records from the USDA October 2, 2026 advertised-retail report, national and selected regional views, searchable grade/cut labels, source page links and stale-snapshot labeling. The meal budget uses cooked portions, raw-to-edible-cooked yield, reserve and either the dated benchmark or an entered local quote; exports preserve the basis. This is a static reviewed snapshot, not a live aggregator.

Next data gates: automated dated ingestion with source archives and extraction validation; broader USDA pork/poultry coverage; BLS monthly context; equivalent-category comparisons only; retailer adapters and actual pack-size quotes. Missing categories remain missing, not synthetic prices. BLS and wholesale feeds are not integrated yet.

### Dinner meat budget extension

The Meat Market now saves a local multi-meat shopping list, with editable per-meat portions, yield, reserve, price basis and optional store notes for local quotes. Saved line prices are fixed until edited; combined totals add raw pounds and cost without summing overlapping guest counts. Editing updates a saved item, and list export retains each source/basis. This remains meat-only and does not imply live price ingestion or retailer availability.

## CHEF iQ replacement acceptance

See [CHEFIQ-PARITY.md](CHEFIQ-PARITY.md) for the prioritized sensor, reliability, cook-monitoring, guidance, remote and hub acceptance gates. The CQ60 hand-warming test proves live food/tip reception only; ambient, battery, accuracy and real-cook reliability remain open.

## UI polish and agent contributions — October 5, 2026

Shared theme-derived form surfaces, readable help panels, consistent card spacing, focus states and mobile form behavior are implemented. Settings includes agent customization and benchmark-sharing guidance. Original code/documentation have an MIT license; media redistribution audit remains outstanding.

Community tooling provides read-only selected-device aggregation, strict schema validation, local review previews, explicit repository opt-in, revocation and GitHub issue submission with fingerprint lookup. Submission tests use mocked GitHub responses. No public issue has been sent, destination configured or recurring uploader installed.

Next release gates: create the official repository; configure contributor issue routing; audit bundled asset redistribution; exercise the issue submission path against that repository with a consenting owner; review reports before compatibility promotion. Hardware testing resumes when the owner requests it.
