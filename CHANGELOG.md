# Changelog

Highlights of each release, newest first. Each release has fuller notes and validation limits where linked.

## Unreleased

- **Native theme fix.** The panel and bar widget now read Omarchy's palette as `Commons.Color`, as Omarchy's plugin documentation requires. A bare `Color` resolves to Qt's own type in files that import QtQuick.Controls, so the panel's background, text, border and alarm colours were undefined. The `muted` border colour, which Omarchy does not provide, is now derived from the theme's foreground.
- **QML runtime test.** CI loads the plugin offscreen against stand-ins for Quickshell and Omarchy, with the real backend behind them, and fails on any QML warning. It walks every view, a full manual cook, the demo and a saved cook. It does not replace a run on Omarchy.
- Issue forms, a security policy, a rewritten README and the adapter feasibility review ([ADAPTER-CANDIDATES.md](ADAPTER-CANDIDATES.md)).

## 0.5.0

An adapter registry and guide, a generated compatibility page, a plugin installer with update and rollback, read-only diagnostics, bundled fonts, accessibility fixes, and CI against real MQTT and ntfy servers. See [0.5.0 release notes](RELEASE-0.5.0.md) for validation and open gates.

## 0.4.2: notification bell

Browser notification status, permission and test controls now live in a bell popover beside Devices and the unit toggle. The panel links to alarm rules and delivery health, closes on Escape or outside click, and shows an attention dot for actionable alarms. Urgent cook alarms remain visible separately.

See [0.4.2 release notes](docs/RELEASE-0.4.2.md) for validation and open gates.

## 0.4.1: navigation

Primary areas are Cook, Plan and Journal. Cook contains Live cook, At the grill, Foods & probes and Alerts. Plan contains Timeline and New meal. Journal contains Cookbook, Recipes and Insights. Devices is a utility control. The browser remembers the last selected view in each area during the session. Native QML uses the same grouping; runtime acceptance remains open.

## 0.4.0: meal coordination

- Guided meal setup builds one to eight foods, a grill reservation plan, dated serving goal and optional target reminders atomically.
- Your next move combines important alarms, stale readings, running steps and upcoming tasks. Start and completion are explicit and persist after reload.
- Grill scheduling uses space units and cooking temperatures. Unknown temperatures reserve exclusive time; temperatures within 25°F can overlap if capacity permits. This is a planning heuristic, not measured grill behavior.
- At the grill offers large readings, manual entry and acknowledge/snooze controls, with focused mobile navigation. Use `/#grill` to open it directly.
- Insights includes planned versus recorded durations and a saved next-time observation. Completed timing and lessons survive backups.
- Service heartbeat, clearer device onboarding, a companion systemd restart template, keyboard heading focus and smaller browser bundles support the new flows.

See [0.4.0 acceptance](docs/RELEASE-0.4.0.md). Native setup/next-action/reservation controls are included as QML source; Linux runtime and screen-reader acceptance remain open.

## 0.3.0: workbench

The five recommended software stages are implemented:

1. Persistent target/high-low, stale-data, battery and timer alarms with buffer, repeat, acknowledgement, snooze and recovery hysteresis.
2. Independent foods, named zones, editable targets/steps, manual readings and live probe mappings.
3. Versioned JSON/HA/MQTT ingestion, compatibility manifest, opt-in authenticated phone serving and optional notification transports.
4. Dated serving goals, task dependencies, changing-duration replanning, recipe import/editor/scaling/cooking mode, outcomes/photos, CSV and portable backup/restore.
5. Conservative trend ranges, a held-out evaluation tool and per-food previous-cook comparison.

See [INTEGRATIONS.md](INTEGRATIONS.md) for setup, credentials, payload contracts, notification limitations and migration/rollback. See [RELEASE-ACCEPTANCE.md](docs/RELEASE-ACCEPTANCE.md) for tested boundaries. The synthetic evaluation is intentionally small: one stable case is estimated and five changing/stalled/cooling/dropout cases abstain. It does not prove accuracy on real cooks. CI tests the bridges against a real local Mosquitto broker, Home Assistant Core and ntfy server (see INTEGRATIONS.md). No real phone, thermometer publisher or native Linux shell was tested. No hardware was purchased.

## 0.2.1: live fire effects

The browser build renders procedural WebGL fire in the logo, advected smoke and glowing ember particles over the grill. These are decorative atmosphere, independent of measured temperatures. They are real-time shaders, not video files. The Atmosphere switch pauses motion and remembers the preference. System reduced-motion renders a still frame. Animation pauses when hidden/offscreen, caps resolution at 1.5 device pixels and targets 30 frames per second. WebGL-unavailable devices receive a static flame mark; the atmosphere disappears gracefully. Context-loss restoration handlers are included but were not force-tested.

This effect is implemented and visually checked in the browser preview. Native QML retains its existing presentation; a Qt shader port and native rendering acceptance remain outstanding. No native visual parity is claimed.

## 0.2.0: device foundation

Experimental CHEF iQ decoder, Bluetooth scan worker, probe selection, recording, and capture/replay tools.

Database schema v1 adds devices, channels, samples, cook associations and reading provenance. The first migration creates `DATABASE.before-devices-v1.bak`. To roll back, stop all OmaPit processes, preserve the current database, restore that backup to its original filename, and use the previous build. Later device data is not present in the pre-migration backup.
