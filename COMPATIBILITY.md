# Compatibility

<!-- Generated from assets/compatibility.json by `python3 backend/compatibility.py --write`. Edit the JSON, not this page. -->

OmaPit 0.4.2. Every row is scoped to one model, protocol, transport and adapter version. Nothing here is a claim about other firmware, other units of the same model or the whole brand.

**Experimental** means OmaPit decodes the format but it has not passed full owner acceptance on real hardware. **Seen live** lists channels observed from real hardware; it does not cover accuracy, range, reconnection or alarms. OmaPit only reads temperatures: no adapter controls a grill, fan or probe.

## Direct Bluetooth

| Model | Protocol | Adapter | Status | Seen live | Decoded, not yet seen live | Evidence |
|---|---|---|---|---|---|---|
| CHEF iQ CQ60 | 4.0.0 | chefiq 0.2.0 | Experimental | food | ambient, battery | maintainer live reception and hand-warming observation on one unit; remaining checks not run ([details](CHEFIQ-HARDWARE-TEST.md)) |
| CHEF iQ CQ60 | V3 / 5.0.0 | chefiq 0.2.0 | Experimental | — | food, ambient, battery | synthetic fixtures and upstream-reported verification |
| CHEF iQ CQ50 / older layouts | V2 / legacy | chefiq 0.2.0 | Experimental | — | food, ambient, battery | synthetic fixtures; older formats lack upstream live verification |

## Bridges and imports

A bridge carries readings from another system. Its status says nothing about which thermometers that system supports.

| Path | Status | Evidence | Hardware compatibility |
|---|---|---|---|
| JSON v1 | implemented | contract and HTTP tests | publisher-specific; not a universal thermometer API |
| Home Assistant REST entity polling | experimental transport | contract and mocked REST conversion tests | depends on installed integration; may depend on cloud |
| MQTT exact-topic subscription | experimental transport | contract tests; automated tests against a local Mosquitto 2.0 broker: live, retained, stale and out-of-order samples, reconnection, password auth and TLS verification. No real thermometer publisher tested | publisher must emit OmaPit schema v1 |

## Not supported yet

MEATER, ThermoPro, Inkbird, FireBoard, Combustion and other brands are candidates under review, not supported devices. Owners can help by sharing an aggregate report; see [community/README.md](community/README.md). Developers can add a device by following [ADAPTERS.md](ADAPTERS.md).
