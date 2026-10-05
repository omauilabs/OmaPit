# OmaPit 0.3.0 acceptance record

October 4, 2026. All five recommended software build stages are implemented. This is a software milestone; field acceptance remains open.

| Stage | Delivered |
|---|---|
| Alerts | Persistent temperature, stale-data, battery and timer rules; buffering, hysteresis, repeats, acknowledgement and snooze; background evaluation |
| Meal workbench | Multiple foods and grill zones within one active meal, editable personal targets and steps, independent stages and probe mappings |
| Integrations and phone | Timestamp-preserving JSON, Home Assistant and MQTT adapters; authenticated remote access configuration; opt-in desktop and ntfy delivery |
| Planning and journal | Dated serving goals, dependency-aware editable timeline, personal recipe import/editor/scaling, step timers, notes, ratings, photos, CSV and complete backup/restore |
| Predictions and comparison | Experimental trend ranges with abstention, explicit timeline adoption, per-food elapsed-time comparisons and held-out evaluation |

## Verified

- 59 Python tests passed, including transactions, migrations, alarms, source freshness/isolation, bridge contracts, restore validation, prediction abstention, HTTP authentication/origin guards and background timers without browser polling.
- Production frontend build passed. Four Sites packaging tests passed.
- Browser workflows exercised against a separate acceptance database: foods, targets, steps, planning, recipes, alerts, journal photos and persistence. Desktop and 390 px mobile layouts checked across six workbench views, with no horizontal overflow. Final browser warning/error log was empty.
- Backup export dialog was parsed and contained one cook, two foods and its photo. The in-app browser did not report a completed Blob download; the export dialog provides the complete contents for copying as a fallback. Clipboard delivery itself was not exercised.
- Screenshots: preview-timeline.jpg and preview-timeline-mobile.jpg. Test data did not replace the original preview journal.

## Prediction evidence

PREDICTION-EVALUATION.json contains six synthetic sessions: one scored linear case and five abstentions. Zero error and full interval coverage apply only to that one synthetic case; they do not establish real-cook accuracy or calibrated confidence. Estimates are experimental, can be unavailable, and do not determine food safety. Personal targets require independent confirmation.

## Open acceptance gates

- Physical CHEF iQ CQ50/CQ60 connection, reconnection, radio range and probe placement.
- Actual Home Assistant/MQTT endpoints and phone/network behavior. Contract tests do not verify vendor hardware compatibility.
- Real desktop/ntfy notifications, background-service installation and delivery during sleep/network loss. Delivery is best effort; transport acceptance does not prove a person saw an alert.
- Linux Quickshell runtime, accessibility and native layout. Workbench QML source is included; browser photos, exports and detailed comparison remain browser features. Native fire effects are not ported.
- Real completed cook datasets for prediction accuracy, interval calibration and comparisons.
- Browser code splitting: the production JS bundle exceeds Vite's 500 KB warning threshold.

The serving planner uses user durations and dependencies. It does not infer shared grill capacity. The app supports one active meal with multiple foods, rather than independent simultaneous meal journals. Remote access is disabled by default; use the documented authenticated HTTPS proxy/tunnel setup before phone access beyond localhost.
