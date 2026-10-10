# OmaPit · 0.4.2

Open-source grilling companion from [OmaUI Labs](https://github.com/omauilabs/OmaPit).

An Omarchy grilling companion with persistent alarms, independent foods/probes, flexible workflows, a dated meal timeline, personal recipes, a local cook journal and experimental temperature trend ranges.

## Status

The Python/SQLite store and browser preview are working and tested. Native QML plugin source is included but has not been run on Linux/Quickshell. This is an initial development build, not a verified catalog release.

Manual temperature entry, labeled demo data, and an experimental CHEF iQ BLE adapter are implemented. A CQ60 / protocol 4.0.0 unit has delivered live food/tip readings during a hand-warming test. Accuracy, ambient, battery, reconnection and cook alarms remain unverified. No fan/grill control or food-safety assessment is implemented. Short-term trend ranges are experimental and abstain for stale, sparse, flat, changing or distant-target data; they are not validated finish forecasts. Flexible food workflows and dated serving goals are implemented in Meal and Timeline. The old single-cook brisket checklist remains for legacy/demo sessions. One active meal journal can hold independent foods across multiple named grills/zones; multiple active meal journals are not implemented.

## Notifications in 0.4.2

Browser notification status, permission and test controls now live in a bell popover beside Devices and the unit toggle. The panel links to alarm rules and delivery health, closes on Escape or outside click, and shows an attention dot for actionable alarms. Urgent cook alarms remain visible separately.

See [0.4.2 release notes](RELEASE-0.4.2.md) for validation and open gates.

## Navigation in 0.4.1

Primary areas are Cook, Plan and Journal. Cook contains Live cook, At the grill, Foods & probes and Alerts. Plan contains Timeline and New meal. Journal contains Cookbook, Recipes and Insights. Devices is a utility control. The browser remembers the last selected view in each area during the session. Native QML uses the same grouping; runtime acceptance remains open.

## New in 0.4.0

- Guided meal setup builds one to eight foods, a grill reservation plan, dated serving goal and optional target reminders atomically.
- Your next move combines important alarms, stale readings, running steps and upcoming tasks. Start and completion are explicit and persist after reload.
- Grill scheduling uses space units and cooking temperatures. Unknown temperatures reserve exclusive time; temperatures within 25°F can overlap if capacity permits. This is a planning heuristic, not measured grill behavior.
- At the grill offers large readings, manual entry and acknowledge/snooze controls, with focused mobile navigation. Use `/#grill` to open it directly.
- Insights includes planned versus recorded durations and a saved next-time observation. Completed timing and lessons survive backups.
- Service heartbeat, clearer device onboarding, a companion systemd restart template, keyboard heading focus and smaller browser bundles support the new flows.

See [0.4.0 acceptance](RELEASE-0.4.0.md). Native setup/next-action/reservation controls are included as QML source; Linux runtime and screen-reader acceptance remain open.

## Visual bundle

The repository includes owner-authorized AI culinary imagery, wordmarks, theme materials, Meshy animal models, cut-region data, and animation assets. See ASSET-LICENSES.md. Local journals and sensor reports remain excluded.

Build the browser bundle from a fresh checkout before running it:

```sh
cd preview
npm ci
npm run build
cd ..
```

## Run the included browser preview

Python 3 is sufficient for the prebuilt preview. From this directory:

```sh
python3 backend/omapit.py --db ./preview-cooks.sqlite3 --static preview/dist/client --seed-demo --serve 4176
```

Open http://127.0.0.1:4176. The server binds only to loopback. `--seed-demo` seeds only an empty store. Finish that demo before starting a manual cook. The Cookbook retains completed sessions. Insights adds outcomes/photos, per-food comparison and CSV/full-cook export; Recipes provides whole-journal backup/restore. This development preview is not a hosted service.

To rebuild after changing the React preview:

```sh
cd preview
npm ci
npm run build
```

## Try the native plugin on Omarchy

Requires a recent Omarchy shell with plugin support and Python 3. Review the source first. Copy this project's `manifest.json`, QML files, `backend/` and `assets/` into a new directory:

```text
~/.config/omarchy/plugins/local.omapit/
```

Do not overwrite an existing directory. Then run the documented Omarchy commands:

```sh
omarchy-shell shell rescanPlugins
omarchy plugin enable local.omapit
```

The widget is declared for the right bar section. Click it to open the cook journal. Native mode invokes the Python helper directly; no HTTP server is needed. Native storage is `$XDG_DATA_HOME/omapit/cooks.sqlite3`, defaulting to `~/.local/share/omapit/cooks.sqlite3`. `OMAPIT_DB` can override the store location. Native surfaces use current Omarchy foreground/background tokens; amber and blue retain their temperature meanings. The native Meal workbench exposes food workflows, probe mappings, alarms, meal steps, recipes and trend summaries. Photo attachment, comparison charts and download/restore UI are in the browser companion. Full native/browser feature parity is not claimed.

Native acceptance still required: QML loading, bar placement, panel open/close, dialogs, theme switching, keyboard navigation, window sizing, and end-to-end persistence on the target Linux machine.

## Troubleshooting

Run `python3 backend/omapit.py diagnose` for a read-only report on your install, cook store, optional packages, probes and alarm monitor. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) explains each warning and how to recover a store.

## Validation

```sh
python3 -m unittest discover -s tests -v
```

The automated tests cover storage, devices, the adapter registry and compatibility claims, read-only diagnostics, alert episodes/restarts/jitter, independent foods, bridge contracts, schedule cycles, recipes, backup/restore, source isolation, predictions and HTTP authentication/background alarms. Browser checks exercised wrap gating, note persistence after reload, unit persistence, manual readings, archive/history, responsive overflow, and modal keyboard handling. Production preview build passed. See `design-qa.md` for visual scope and limits.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the release sequence, adapter architecture, compatibility evidence, and community capture/testing strategy. CHEF iQ CQ50 and CQ60 are both initial targets; [COMPATIBILITY.md](COMPATIBILITY.md) lists exactly what has been tested. Decoding, optional scanning, selection and automatic recording are implemented experimentally; CQ60 protocol 4.0.0 live reception has been observed on one unit; complete acceptance for it and other models remains open. Broader coverage will use direct adapters, Home Assistant, MQTT and imports as appropriate. To add a thermometer, see [ADAPTERS.md](ADAPTERS.md).

Official plugin documentation: https://github.com/basecamp/omarchy/blob/master/docs/omarchy-shell.md

## CHEF iQ experimental adapter

The Devices screen starts a 60-second local scan. Select a receiving probe during a real cook to record its food and ambient channels automatically. The discovery worker continues receiving while a live cook is selected; after its discovery window, it stops when that cook finishes or switches to manual mode. After an application/computer restart, scan again to resume reception. Demo and replay probes cannot be selected. The adapter decodes newer V3, V2 and legacy layouts; older layouts remain experimental. Unknown future major protocols are rejected. The screen labels model as unknown when it is not reported, and never infers model from purchase date.

Live scanning needs Python 3 and Bleak in the interpreter running OmaPit. For a dedicated environment:

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-ble.txt
.venv/bin/python backend/omapit.py --db ./preview-cooks.sqlite3 --static preview/dist/client --serve 4176
```

Native mode uses `OMAPIT_PYTHON` if set in the shell environment, otherwise `python3` from PATH; that interpreter must have Bleak available. On Linux the Bluetooth adapter must be enabled and accessible through BlueZ. On macOS the interpreter needs system Bluetooth permission. OmaPit reports dependency/scan failures in Devices. No Bluetooth scan was performed during this development pass.

A selected probe records only new readings received after selection. A status packet does not refresh food/ambient channels. Channels become stale after 30 seconds; invalid sensors clear their current value. Battery can be missing or stale independently. The current chart stores same-packet valid food/ambient pairs; raw channel samples preserve partial updates for export. Live source selection can be changed back to manual mode. Existing manual samples keep their provenance.

### Capture and replay

Capture only one selected device; the command refuses to capture without `--address`. Addresses refer to the local scan identity (MAC on Linux, UUID on macOS). Captures omit the radio address and advertised name; embedded address bytes in known legacy/status formats are zeroed. Review files before sharing, especially unknown formats, which may contain unrecognized identifiers. Nothing is uploaded automatically.

```sh
.venv/bin/python backend/devices.py --db ./preview-cooks.sqlite3 scan --seconds 60 --address YOUR_PROBE_ADDRESS --capture ./probe-capture.jsonl
python3 backend/devices.py --db ./replay-cooks.sqlite3 replay ./probe-capture.jsonl
```

A replay uses isolated device IDs and cannot record a live cook. The included `tests/fixtures/synthetic-chefiq.jsonl` is generated test data, not a real-device capture. Replay it to explore the device cards:

```sh
python3 backend/devices.py --db ./preview-cooks.sqlite3 replay tests/fixtures/synthetic-chefiq.jsonl
```

Database schema v1 adds devices, channels, samples, cook associations and reading provenance. The first migration creates `DATABASE.before-devices-v1.bak`. To roll back, stop all OmaPit processes, preserve the current database, restore that backup to its original filename, and use the previous build. Later device data is not present in the pre-migration backup.

Protocol documentation is adapted from [chefiq-ble](https://github.com/Invader444/chefiq-ble); upstream MIT attribution is included in `backend/adapters/CHEFIQ-LICENSE.txt`. The decoder avoids Home Assistant dependencies; transport uses optional Bleak. Upstream CQ60 5.0.0 verification is not an OmaPit live test.

## Live fire effects (0.2.1)

The browser build renders procedural WebGL fire in the logo, advected smoke and glowing ember particles over the grill. These are decorative atmosphere, independent of measured temperatures. They are real-time shaders, not video files. The Atmosphere switch pauses motion and remembers the preference. System reduced-motion renders a still frame. Animation pauses when hidden/offscreen, caps resolution at 1.5 device pixels and targets 30 frames per second. WebGL-unavailable devices receive a static flame mark; the atmosphere disappears gracefully. Context-loss restoration handlers are included but were not force-tested.

This effect is implemented and visually checked in the browser preview. Native QML retains its existing presentation; a Qt shader port and native rendering acceptance remain outstanding. No native visual parity is claimed.

## Workbench release (0.3.0)

The five recommended software stages are implemented:

1. Persistent target/high-low, stale-data, battery and timer alarms with buffer, repeat, acknowledgement, snooze and recovery hysteresis.
2. Independent foods, named zones, editable targets/steps, manual readings and live probe mappings.
3. Versioned JSON/HA/MQTT ingestion, compatibility manifest, opt-in authenticated phone serving and optional notification transports.
4. Dated serving goals, task dependencies, changing-duration replanning, recipe import/editor/scaling/cooking mode, outcomes/photos, CSV and portable backup/restore.
5. Conservative trend ranges, a held-out evaluation tool and per-food previous-cook comparison.

See [INTEGRATIONS.md](INTEGRATIONS.md) for setup, credentials, payload contracts, notification limitations and migration/rollback. See [RELEASE-ACCEPTANCE.md](RELEASE-ACCEPTANCE.md) for tested boundaries. The synthetic evaluation is intentionally small: one stable case is estimated and five changing/stalled/cooling/dropout cases abstain. It does not prove accuracy on real cooks. No real phone, MQTT broker, Home Assistant instance, external push destination or native Linux shell was tested. No hardware was purchased.

## Customize and contribute

Original software and documentation use the MIT license. See [CUSTOMIZATION.md](CUSTOMIZATION.md) for agent-assisted changes and [community/README.md](community/README.md) for local benchmark collection, validation and destination-specific opt-in submission. Settings explains the workflow and provides an agent prompt. No repository, uploader or scheduler is enabled by default. Media redistribution review remains separate: [ASSET-LICENSES.md](ASSET-LICENSES.md).
