# OmaPit · 0.5.0

Open-source grilling companion from [OmaUI Labs](https://github.com/omauilabs/OmaPit) for [Omarchy](https://github.com/basecamp/omarchy).

OmaPit lives in your Omarchy bar. It shows probe temperatures, raises alarms when a cook needs attention, plans a meal around a serving time and keeps a local journal of every cook. A browser view runs on the same data, including a phone-friendly view at the grill.

## Status

OmaPit is an early development release.

- **Tested:** the Python/SQLite store, the browser view, the installer and the bridges. The bridges are tested in CI against real Mosquitto, Home Assistant Core and ntfy servers.
- **Not yet run on Omarchy:** the native plugin. [OMARCHY-ACCEPTANCE.md](OMARCHY-ACCEPTANCE.md) is the checklist for that first run.
- **Experimental:** the CHEF iQ adapter. One CQ60 has delivered live readings; accuracy, battery, reconnection and alarms on real hardware are unverified. [COMPATIBILITY.md](COMPATIBILITY.md) lists exactly what has been tested.

OmaPit only reads temperatures. It never controls a grill, fan or probe, and it does not judge food safety. Trend ranges are experimental and decline to estimate when the data is unsuitable.

## What it does

- **Live cook:** large readings, manual entry, stale-reading warnings and an "At the grill" view for your phone.
- **Alarms:** target, high/low, stale data, battery and timers, with acknowledge, snooze and repeat. Alarms survive restarts. Delivery is by desktop notification, browser or optional ntfy push.
- **Meals:** one to eight foods, each with its own steps and targets, scheduled back from a serving time across named grills and zones.
- **Journal:** notes, fuel events, photos and outcomes. It also has recipes with scaling, comparisons with past cooks, CSV export and full backup/restore.
- **Thermometers:** a direct Bluetooth adapter for CHEF iQ probes, plus Home Assistant, MQTT and JSON import bridges for other devices.
- **Reference:** a 3D cut explorer, sauces, rubs, woods and cooker guides.

Everything is stored locally in SQLite. Nothing is sent anywhere unless you set up a bridge or notification service.

## Quick start

You need Python 3.9 or newer. Building the browser view also needs Node.js and npm.

### Browser view

```sh
cd preview
npm ci
npm run build
cd ..
python3 backend/omapit.py --db ./preview-cooks.sqlite3 --static preview/dist/client --seed-demo --serve 4176
```

Open http://127.0.0.1:4176. The server listens on this computer only. `--seed-demo` adds a labelled demo cook to an empty store; finish it before starting a real cook. To use it from a phone on your home network, set an access token as described under phone access in [INTEGRATIONS.md](INTEGRATIONS.md); this has not yet been tested on a real phone.

### Omarchy plugin

You need a recent Omarchy shell with plugin support.

```sh
python3 packaging/install.py --dry-run
python3 packaging/install.py
omarchy-shell shell rescanPlugins
omarchy plugin enable local.omapit
```

The widget appears in the right section of the bar; click it to open the cook journal. Your cooks are stored in `~/.local/share/omapit/cooks.sqlite3`, or `OMAPIT_DB` if set. [INSTALL.md](INSTALL.md) covers updating, rolling back and uninstalling.

The native panel covers the cook, foods, alarms, meal steps, recipes and trends. Photos, comparison charts and backup/restore are in the browser view.

### Bluetooth probes (optional)

Manual entry needs no extra packages. To read a CHEF iQ probe directly, install Bleak in a virtual environment and run OmaPit with that Python:

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-ble.txt
.venv/bin/python backend/omapit.py --db ./preview-cooks.sqlite3 --static preview/dist/client --serve 4176
```

For the Omarchy plugin, set `OMAPIT_PYTHON` to that Python instead, as described in [INSTALL.md](INSTALL.md). On Linux, Bluetooth must be enabled and reachable through BlueZ. On macOS, the Python needs Bluetooth permission. The MQTT bridge similarly needs `backend/requirements-bridge.txt`.

## Using a CHEF iQ probe

In Devices, start a 60-second scan with the probe out of its charger and near the computer. Select the probe during a cook to record its food and probe-ambient channels. After a restart, scan again to resume.

- Only readings received after you select the probe are recorded. Existing manual readings keep their source.
- A channel is marked stale after 30 seconds without data. Invalid sensors clear their value, and a missing battery reading is shown as unknown, never 0%.
- The model is shown as unknown when the probe doesn't report it. Unknown future protocol versions are rejected rather than guessed.
- Demo and replayed probes can never be selected for a live cook.

### Capture and replay

To help support a firmware version, capture one selected probe and replay it into a separate store:

```sh
.venv/bin/python backend/devices.py --db ./preview-cooks.sqlite3 scan --seconds 60 --address YOUR_PROBE_ADDRESS --capture ./probe-capture.jsonl
python3 backend/devices.py --db ./replay-cooks.sqlite3 replay ./probe-capture.jsonl
```

- **Address:** the scan's local identity for the probe, a MAC on Linux or a UUID on macOS. The command refuses to capture without one.
- **What a capture contains:** captures leave out the radio address and advertised name, and zero the address bytes inside known formats. Review a capture before sharing it, especially one in an unknown format.
- **Synthetic data:** to explore without a probe, replay `tests/fixtures/synthetic-chefiq.jsonl`, which is generated test data.

The decoder is adapted from [chefiq-ble](https://github.com/Invader444/chefiq-ble) under the MIT licence (`backend/adapters/CHEFIQ-LICENSE.txt`). To add another thermometer, see [ADAPTERS.md](ADAPTERS.md) and [ADAPTER-CANDIDATES.md](ADAPTER-CANDIDATES.md).

## Troubleshooting

Run `python3 backend/omapit.py diagnose` for a read-only report on your install, cook store, optional packages, probes and alarm monitor. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) explains each warning and how to recover a store.

## Documentation

| Topic | Document |
|---|---|
| Install, update, roll back | [INSTALL.md](INSTALL.md) |
| Supported thermometers | [COMPATIBILITY.md](COMPATIBILITY.md) |
| Home Assistant, MQTT, phone access, notifications | [INTEGRATIONS.md](INTEGRATIONS.md) |
| First run on Omarchy | [OMARCHY-ACCEPTANCE.md](OMARCHY-ACCEPTANCE.md) |
| Writing an adapter | [ADAPTERS.md](ADAPTERS.md) |
| Customising with an agent | [CUSTOMIZATION.md](CUSTOMIZATION.md) |
| Sharing hardware test results | [community/README.md](community/README.md) |
| Release history | [CHANGELOG.md](CHANGELOG.md) and [RELEASE-0.5.0.md](RELEASE-0.5.0.md) |
| Plans and release gates | [ROADMAP.md](ROADMAP.md) |
| Design, research and QA notes | [docs/](docs/README.md) |

Omarchy's plugin documentation: https://github.com/basecamp/omarchy/blob/master/docs/omarchy-shell.md

## Development

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s community -p 'test_*.py' -v
cd preview && npm test
```

CI also checks the QML for syntax errors, loads the plugin offscreen against stand-ins for Quickshell and Omarchy with the real backend behind them (`tests/test_qml_runtime.py`), and audits every browser view for WCAG 2.1 A/AA issues at desktop and phone widths. Neither QML check is a run on Omarchy; see [design-qa.md](docs/design-qa.md) and [RELEASE-ACCEPTANCE.md](docs/RELEASE-ACCEPTANCE.md) for what has been checked by hand.

## Contribute

Report bugs, Omarchy acceptance results and thermometer requests through the [issue forms](https://github.com/omauilabs/OmaPit/issues/new/choose). Report security problems privately as described in [SECURITY.md](SECURITY.md). Contributors and their agents should read [AGENTS.md](AGENTS.md) first.

## Licence

Original software and documentation are MIT licensed. The repository also includes owner-authorized AI culinary imagery, wordmarks, theme materials, 3D animal models and cut-region data, plus bundled fonts under the SIL Open Font License; see [ASSET-LICENSES.md](ASSET-LICENSES.md). Third-party dependencies keep their own licences.
