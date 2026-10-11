# CHEF iQ replacement roadmap

Updated October 5, 2026. Scope: this owner's CQ60 thermometer and everyday cooking workflow. This is a target, not a claim of completed parity. Mini Oven and pressure-cooker controls are outside this thermometer scope.

## What passed

Real Bluetooth food and four tip readings were received on macOS. Hand warming raised food temperature from 25.1°C to 33.0°C. No live cook was started or modified. See CHEFIQ-HARDWARE-TEST.md. This proves reception and response, not calibrated accuracy.

## Recommended build and acceptance order

| Priority | Capability | Current evidence / gap | Acceptance gate |
|---|---|---|---|
| 1 | Trustworthy sensor readings | Food and tips received; ambient invalid and battery unavailable | Compare simultaneous readings with CHEF iQ at room temperature, warming and cooling. Resolve protocol 4 ambient/battery fields; never substitute invented values. Confirm reported food aggregation against the manufacturer's output. |
| 2 | Reliable receiver | Local BLE scan works; persistent cook path untested | Wake, return to charger, rescan, move out of range and return. Verify stale warnings, automatic recovery, restart behavior and no duplicate samples. |
| 3 | Full cook monitoring | Cook assignment, journal, graphs and alarms exist; hardware integration not accepted | Start a separate test cook; assign this probe; verify saved timestamps and temperatures, disconnect handling, alarm threshold crossing and audible/background notifications. Preserve sample cooks. |
| 4 | Cook guidance | Presets, planning and prediction tools exist; no accuracy equivalence established | Cut/doneness presets, placement instructions, remove-from-heat and rest workflow. Evaluate ETA and carryover against real cooks; show uncertainty and suppress unreliable estimates. |
| 5 | Multiple probes / food items | One physical probe tested | Test independent targets, graphs and alerts with additional owner/community hardware. Label unverified devices. Replay alone does not establish hardware compatibility. |
| 6 | Phone and remote monitoring | Direct BLE is local; does not equal vendor Wi-Fi range | Secure companion access, reconnection and notification delivery with permission/access controls. Investigate documented hub integration; do not assume a public CHEF iQ cloud API. |
| 7 | Hub audio and device management | Hub speaker, pairing, charging status and firmware control not verified | Confirm supported protocol/API before controlling the hub. Keep vendor firmware/update path until a supported alternative is proven. |
| 8 | Convenience parity | Vendor offers recipes, presets, favorites, sharing and shopping integrations | Original guided recipes, saved configurations and shared cook viewing. Shopping integration is optional; vendor recipe/video catalog is not licensed for copying. |

## Remaining tests before a real cook

1. Side-by-side manufacturer app comparison with timestamps, including warming and cooling. Do not use hands as an accuracy reference.
2. Resolve ambient and battery reporting. An unavailable value is not evidence that the sensor is defective.
3. Charger/wake, range loss/recovery and receiver restart checks.
4. A deliberately created non-cooking test session for recording and alarm delivery, then inspect its persisted history. No changes to the existing demo.
5. Finally, a supervised real cook using the manufacturer's placement and temperature limits and an independent reference thermometer. Test ambient, prediction, carryover/rest and alerts. A long-session test is needed for reliability claims.

## Replacement decision

Everyday local monitoring can become independent once sensor correctness, persistent recording and alarms pass. Full manufacturer-app replacement remains conditional on remote/hub/device-management support. Keep CHEF iQ available for comparison and firmware updates until these gates pass. Desktop browser functionality does not imply iOS Live Activities or native background notification parity.

## Official feature baseline

- [CHEF iQ app](https://chefiq.com/pages/chef-iq-app): guided video recipes, thousands of presets, Live Activities, temperature guide, shopping integrations, time estimation, device sharing and light/dark themes.
- [iQ Sense product page](https://chefiq.com/products/iq-sense?variant=41324717277259): probe-to-hub Bluetooth, hub-to-phone Wi-Fi, flip reminders, rest timers and hub speaker alerts. Current-generation specifications must not be applied to the owner’s older probe.
- [Publisher's App Store listing](https://apps.apple.com/gb/app/chef-iq/id1496378504): live graphs, ambient alerts, hub audio, Wi-Fi/Bluetooth monitoring and over-the-air updates.

Sources describe marketed capabilities across supported products; availability can vary with hardware generation and app version. This owner's unit is CQ60 / protocol 4.0.0, so compatibility must be established on that unit.
