# OmaPit 0.5.0 — release groundwork

October 10, 2026. A developer pre-release. It includes everything in [0.4.2](docs/RELEASE-0.4.2.md), which was prepared but never tagged, plus the software groundwork for 1.0 below. It is not a verified catalog release: the native Omarchy plugin and hardware acceptance are still open.

## New since 0.4.2

**Adding devices and claiming compatibility**
- Device adapters plug into a registry with a checked contract instead of the code being hard-wired to CHEF iQ. CHEF iQ decoding is unchanged (adapter 0.2.0). See [ADAPTERS.md](ADAPTERS.md).
- [COMPATIBILITY.md](COMPATIBILITY.md) is generated from a validated manifest. A row can't claim more than its evidence: nothing is "implemented" without an OmaPit live test, and channels show as seen live only where a real observation exists.

**Installing and troubleshooting**
- `python3 packaging/install.py` installs or updates the Omarchy plugin. It refuses folders it didn't install, edited files and downgrades unless told otherwise, keeps a backup of the previous version outside the plugin folder, and never touches the cook store. See [INSTALL.md](INSTALL.md) for update, rollback and uninstall.
- `python3 backend/omapit.py diagnose` gives a read-only report on the install, cook store, optional packages, probes and alarm monitor. It never changes data, and it reports no cook names, notes, temperatures, device addresses or secrets. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

**Browser preview**
- Fonts are bundled with the app; the preview makes no third-party requests.
- Three accessibility fixes: the temperature unit button and logo choices now have accessible names that match their visible text, and the pepper heat scale is exposed as an image with a description.

**Testing**
- CI now runs on every push and pull request:
  - backend tests on Python 3.9 and 3.13;
  - the MQTT bridge against a real Mosquitto broker;
  - alarm delivery to a real self-hosted ntfy server;
  - a QML syntax check;
  - all browser unit and packaging tests;
  - an automated WCAG 2.1 A/AA audit of every browser view at desktop and phone widths.

## Software validation

- 120 backend tests pass, including 7 MQTT broker tests and 5 ntfy delivery tests that need their optional servers. 14 community benchmark tests pass.
- 44 browser unit and packaging tests pass. The production build has no warnings.
- The axe-core audit reports no violations in 24 views at both widths.
- `qmllint` finds no syntax errors in the native QML.
- The installer was exercised in a temporary home folder: install, update with backup, and diagnostics from the installed copy.

## Not verified

- **Native plugin:** the QML has not been loaded on Omarchy/Quickshell, and the installer has not been run on a real Omarchy setup. The QML check covers syntax only.
- **Hardware:** one CQ60 (protocol 4.0.0) delivered food readings during a hand-warming test on macOS Bluetooth. Accuracy, ambient, battery, range, reconnection, alarms on real cooks and Linux/BlueZ reception remain untested.
- **Integrations:** no Home Assistant instance or real MQTT thermometer publisher has been tested; the MQTT tests use a local test broker.
- **Notifications:** delivery to an ntfy server is tested; delivery from ntfy to a phone, desktop notifications and phone sound behavior are not.
- **Accessibility:** automated rules catch a subset of problems. Screen-reader testing has not been done.
- **Predictions:** evaluated only on synthetic sessions.

## Known limitations

- The lazily loaded three.js bundle is split into two chunks under Vite's size warning, but the total download is unchanged at about 640 KB.
- 3D cut models are committed directly (20–37 MB each), so clones are large.
- One active meal journal at a time; no fan or grill control and no food-safety assessment.
