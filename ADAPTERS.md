# Writing a device adapter

An adapter teaches OmaPit to read one thermometer family's raw transport data. This guide covers direct Bluetooth LE advertisement adapters, the only direct transport today. Devices that need a vendor app, a Wi-Fi hub, a cloud account or a GATT connection should arrive through a bridge instead: Home Assistant, MQTT or JSON import. See [INTEGRATIONS.md](INTEGRATIONS.md).

Read [AGENTS.md](AGENTS.md) and [CUSTOMIZATION.md](CUSTOMIZATION.md) first. Develop against a separate test database, and never scan or run hardware tests unless the device owner asked you to.

## Where an adapter sits

```text
BLE advertisement ─▶ adapters.match() ─▶ adapter.decode() ─▶ devices.ingest() ─▶ store ─▶ browser / QML / alerts
  (bleak, optional)    picks the adapter    bytes → channels    freshness, cook
                       by company ID                           recording, replay
```

An adapter is a pure function of bytes. It never opens the database, the network or Bluetooth. `backend/devices.py` owns transport, identity, freshness, stale detection, cook recording and capture files, so every adapter inherits the same safety behaviour.

## The contract

Create `backend/adapters/<id>.py` with these module attributes. `backend/adapters/__init__.py` checks them at import and refuses to start with an invalid adapter.

| Name | Purpose |
|---|---|
| `ADAPTER_ID` | Short stable identifier, such as `chefiq`. Stored in capture files. |
| `ADAPTER_VERSION` | `major.minor.patch`. Bump it whenever decoded output can change. Compatibility evidence is scoped to this version. |
| `NAME` | Vendor or family name shown to people. |
| `TRANSPORT` | `ble-advertisement`. |
| `DEFAULT_NAME` | Device name used when the advertisement carries none. |
| `payload_from(manufacturer_data)` | Receives the advertisement's `{company_id: bytes}` map. Return this adapter's payload, or `None` if the advertisement is not yours. Check length bounds here. |
| `decode(payload)` | Return the decoded dictionary below. Raise `ValueError` for anything you do not recognise. |
| `model_from_name(name)` | Model label derived from the advertised name, or `'Unknown'`. |
| `redact(payload)` | Return a copy that is safe to share in a capture: zero serial numbers, MAC-derived bytes and any other per-unit identifier. |

`decode` returns:

```python
{
    'protocol': '5.0.0',          # what the device reported, not what you assumed
    'format': 'v3',               # your internal layout name
    'evidence': 'experimental',   # or 'upstream-verified' for a layout an upstream project verified on hardware
    'channels': {'food': 73.2, 'ambient': 120.5, 'battery': 80, 'tip1': 70.0},
    'adapter': ADAPTER_ID,
    'adapter_version': ADAPTER_VERSION,
}
```

Channels:

- `food` and `ambient` are temperatures in °C. `battery` is a percentage from 0 to 100. Extra probe-tip temperatures use `tip1`, `tip2` and so on.
- Include a channel only when this packet carries it. A status packet that holds only battery must not include temperatures; `devices.py` relies on that to keep stale temperatures stale.
- Use `None` for a channel the packet carries but whose value is a sensor-error sentinel or out of range. That clears the previous value instead of leaving an old reading looking fresh.
- Never invent a value. A missing battery is unknown, never 0%.

## Rules

- Dispatch by the protocol the device reports, never by purchase year or a guess. Unknown, truncated and future-version layouts raise `ValueError`; OmaPit then shows the device as unsupported.
- Keep one physical probe as one identity. Never merge two probes.
- Keep transport packages optional. Manual mode must work without Bluetooth dependencies installed.
- Reuse a maintained protocol library where its licence fits. Record the upstream project, file and licence in the module docstring, and add the licence file beside the adapter.

## Tests

Add `tests/test_<id>.py`. `tests/test_devices.py` and `tests/test_adapters.py` show the patterns. Cover at least:

- Every layout you decode, with expected values.
- Malformed input: empty, too short, too long, wrong packet type.
- Partial packets: only some channels present, and status packets that must not freshen temperatures.
- Missing and invalid values: sentinels clear channels; missing battery stays unknown.
- Future protocol versions are rejected.
- Stale data: an old packet leaves the device `stale`, and delayed packets cannot overwrite newer state.
- Several devices of your kind at once stay separate.
- `redact` removes every per-unit identifier.

Synthetic fixtures test failure handling only. They never establish that real hardware works.

## Captures and replay

`python3 backend/devices.py --db TEST.db scan --seconds 60 --capture probe.jsonl --address <ADDRESS>` records one selected device to a JSON Lines file. Run it only with the device owner's permission. Each line is:

```json
{"schema": 1, "adapter": "chefiq", "device": "probe-1", "name": "CHEF iQ probe", "relative_seconds": 1.5, "payload_hex": "...", "rssi": -60}
```

The address is replaced by an alias and the payload passes through `redact`. Lines without `adapter` predate the registry and are read as `chefiq`. `python3 backend/devices.py --db TEST.db replay probe.jsonl` replays a capture through the same parser and store. Replayed devices can never be selected for a cook or trigger alerts.

## Claiming compatibility

All compatibility claims live in [assets/compatibility.json](assets/compatibility.json), one row per model + protocol + transport + adapter version. [COMPATIBILITY.md](COMPATIBILITY.md) is generated from it: after editing the JSON, run `python3 backend/compatibility.py --write`. `python3 backend/compatibility.py` validates both, and the test suite runs the same checks. The validator rejects:

- rows without a registered `adapter` or an `adapter_version`, or with an `adapter_version` newer than the shipped adapter;
- `implementation: "implemented"` without an OmaPit live test (`omapit_live_test: true`). Start every new row as `experimental`;
- roles outside `food`, `ambient` and `battery`, or a role listed as both verified and unverified;
- an `app_version` that differs from `manifest.json`, and any claim of hardware control.

Promotion from experimental needs an owner's live session covering the checks in [community/README.md](community/README.md), reviewed by a maintainer. One unit never certifies a whole brand or firmware family.

## Known limits

- Only BLE advertisement adapters are supported. Connection-based (GATT) protocols need transport work in `devices.py` first.
- The devices table stores the adapter version but not the adapter ID. That is unambiguous with one adapter; the second adapter should add an `adapter` column through a versioned, backed-up migration.
