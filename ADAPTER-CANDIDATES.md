# Thermometer adapter candidates

October 11, 2026. The roadmap's feasibility review of MEATER, ThermoPro, Inkbird, FireBoard and Combustion. This is a desk review of public documentation and source code. No hardware was used, and **none of these brands is supported** by OmaPit today; see [COMPATIBILITY.md](COMPATIBILITY.md) for what is.

Criteria from the roadmap: owner demand, a documented or local interface, a reusable implementation, licensing, firmware coverage, sample availability and maintenance cost. OmaPit's direct adapters listen to Bluetooth LE advertisements without connecting (see [ADAPTERS.md](ADAPTERS.md)). Anything that needs a connection, a vendor hub or a cloud account belongs on the bridge path: Home Assistant, MQTT or import.

## Summary

| Brand / models | How temperatures are sent | Vendor docs | Reusable code | Home Assistant core | Route for OmaPit |
|---|---|---|---|---|---|
| ThermoPro TempSpike TP960, TP962, TP970 | BLE advertisements | None | `thermopro-ble`, MIT, active | `thermopro` | **Direct adapter: best candidate** |
| Combustion Predictive Thermometer, Display, Booster | BLE advertisements; Display and Booster relay probe readings | Published BLE spec | `combustion-ble`, Apache-2.0, last release 2024 | None (custom component only) | Direct adapter, written from the spec |
| Inkbird iBBQ family (IBT-2X, IBT-4XS, IBT-6XS per Home Assistant) | BLE advertisements | None | `inkbird-ble`, MIT, active | `inkbird` | Direct adapter, after names are confirmed on hardware |
| Inkbird INT-11P and similar "wireless" probes | GATT connection | None | `inkbird-ble` | `inkbird` | Home Assistant bridge |
| ThermoPro TP25, TP902, TP920 | GATT connection (community reports, unverified) | None | Community projects only | Not in core `thermopro` | Home Assistant or later |
| MEATER (original; 2 Plus / Pro unknown) | GATT, single connection; Wi-Fi only via app or Block | Cloud REST API (beta) | `meater-python`, Apache-2.0, last release 2021 | `meater` (cloud) | Home Assistant or cloud |
| FireBoard (FBX2, Spark, FireBoard 2) | Wi-Fi to the vendor cloud | Cloud API | `fireboard-cloud-api-client`, MIT, single release 2021 | None | Cloud API or an MQTT bridge |

## By brand

### ThermoPro TempSpike (TP960, TP962, TP970)
- **Transport:** temperatures in manufacturer data in advertisements. `thermopro-ble` 1.1.4's parser matches only names starting `TP35`, `TP39`, `TP96` and `TP97`. It decodes:
  - a 23-byte TP97x frame with probe index, ambient, battery and three internal temperatures;
  - a 7- or 13-byte TP96x/TP97x frame;
  - TP35x/TP39x hygrometer frames.
- **Connections:** the library opens a GATT connection only to set the clock on hygrometers, which OmaPit, being read-only, would never do.
- **Licence:** MIT; release 1.1.4 on May 10, 2026, used by Home Assistant core's `thermopro` integration.
- **Risks:**
  - The encodings, including fixed temperature offsets, are reverse-engineered and could change with firmware.
  - TP97x reports °F only.
  - Other ThermoPro models (TP25, TP902, TP920) are reported to need a connection, so any claim must be scoped to TP96x/TP97x.
- Sources: https://github.com/bluetooth-devices/thermopro-ble, https://pypi.org/project/thermopro-ble/, https://github.com/home-assistant/core/tree/dev/homeassistant/components/thermopro

### Combustion Inc
- **Transport:** the probe advertises every 250 ms under vendor ID `0x09C7`. Each advertisement carries eight thermistor readings packed as 13-bit values, mode and battery-OK bits. Display and Booster nodes repeat probe readings in their own advertisements. Session IDs, full status and logs need a connection; live temperatures do not.
- **Documentation:** published by the vendor at https://github.com/combustion-inc/combustion-documentation. That repository states no licence, so OmaPit should implement from the description rather than copy text or code from it.
- **Reusable code:** `combustion-ble`, Apache-2.0, last release 0.3.3 in March 2024 (https://github.com/legrego/combustion_ble).
- **Risks:**
  - Readings relayed through a Display or Booster must be de-duplicated against direct ones.
  - The probe stops advertising in its charger.
  - No Home Assistant core integration exists to cross-check against.

### Inkbird
- **Transport:** the iBBQ family advertises temperatures, and `inkbird-ble` parses them passively. Some models need a GATT poll or notification, including the INT-11P-B, INT-11I-B, IDT-34c-B and IHT-2PB. The INT-12P was not found.
- **Licence:** MIT; release 1.7.1 on August 30, 2026, used by Home Assistant core's `inkbird` integration.
- **Risks:**
  - Home Assistant notes that most Inkbird devices need *active* scanning to be discovered, which differs from purely passive listening on BlueZ.
  - Home Assistant lists IBT-2X, IBT-4XS and IBT-6XS as supported, but which advertised names they use needs confirming on hardware.
- Sources: https://github.com/bluetooth-devices/inkbird-ble, https://pypi.org/project/inkbird-ble/, https://github.com/home-assistant/core/tree/dev/homeassistant/components/inkbird

### MEATER
- **Transport:** the original probe needs a GATT connection and allows only one, so a direct adapter would compete with the MEATER app, Block or MEATER+. Reverse-engineering covers only the original and Block probes on old firmware; MEATER 2 Plus and Pro are unknown.
- **Cloud:** a documented beta REST API (https://github.com/apption-labs/meater-cloud-public-rest-api) needs the account's email and password. It sees a probe only while the vendor app or Block is relaying it.
- **Code:** `meater-python`, Apache-2.0, cloud only, last release April 2021. Home Assistant core's `meater` integration uses it.
- **Route:** the Home Assistant bridge, which OmaPit already supports, or a future cloud adapter. Not a direct BLE adapter.

### FireBoard
- **Transport:** Wi-Fi to the FireBoard cloud. Bluetooth is described for setup only; no local temperature API was found.
- **Cloud:** a documented account API with a 200 calls per hour limit, so at best a poll every 18 seconds. The only Python client (`fireboard-cloud-api-client`, MIT) had a single release in 2021.
- **Route:** a cloud adapter or an MQTT bridge. No Home Assistant core integration.

## Recommendation

1. **ThermoPro TempSpike TP96x/TP97x first.** It is passive like CHEF iQ and has an actively maintained MIT parser used by Home Assistant. A first adapter should:
   - adapt that parser with attribution, as the CHEF iQ adapter does;
   - be scoped to the `TP96` and `TP97` name prefixes;
   - start as experimental with synthetic fixtures;
   - be promoted only after an owner's live session.
2. **Combustion second.** The protocol is the best documented of the five, but OmaPit needs a clean implementation from the spec, plus relay de-duplication.
3. **Inkbird iBBQ third.** Confirm advertised names and passive discovery on Linux before any claim.
4. **MEATER and FireBoard** owners can use the Home Assistant bridge (MEATER) or wait for a cloud adapter. A cloud adapter would need account credentials, which is a larger privacy decision than a local adapter.

Before writing any of these adapters, find an owner who can provide a short capture and a live session (see [community/README.md](community/README.md)). Synthetic fixtures alone cannot establish compatibility.

## Limits of this review

- **Documents only:** based on public documentation and source code as of the date above. No device was tested, and no protocol detail here was observed on hardware.
- **Sources not read directly:** this environment could not reach some GitHub repository pages, home-assistant.io or docs.fireboard.io directly. Repository licences were taken from PyPI metadata.
- **Spot checks:** I checked the `thermopro-ble` licence, release and parser scope, and the release metadata of the other four libraries, against PyPI and the published source. Other details come from the cited sources and were not checked independently.
