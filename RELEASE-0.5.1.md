# OmaPit 0.5.1: native theme fixes

October 11, 2026. A developer pre-release that fixes how the native Omarchy plugin reads the theme, adds a runtime test for the native QML, and prepares the repository for public contributors. Everything in [0.5.0](docs/RELEASE-0.5.0.md) still applies. This is not a verified catalog release: the plugin has still not been run on a real Omarchy machine.

## Fixed

**The native panel's colours were undefined.** Omarchy's plugin documentation requires plugins to read the palette as `Commons.Color`, through `import qs.Commons as Commons`. In a QML file that imports QtQuick.Controls, a bare `Color` resolves to Qt's own type instead of Omarchy's palette, whatever the import order. `Main.qml` did exactly that, so the panel's background, text, border, error and alarm colours were all undefined. The panel and bar widget now use `Commons.Color`.

**An undocumented colour role.** The panel's borders used `Color.muted`, which Omarchy does not provide. The documented roles are `foreground`, `background`, `accent` and `urgent`. The border colour is now derived from the theme's foreground, so it still follows the theme.

**Fixed text sizes.** Native text now follows Omarchy's type scale, which grows with the theme's `[font] base-size`. The panel, meal workbench, chart labels, checkboxes and bar widget all scale with `Style.font.body`. At the default size every size is unchanged.

**Smaller fixes.**
- The meal workbench's "Add food" button no longer sets its enabled state to a non-boolean value when no cook is active.
- The chart's last time label is no longer clipped at the right edge.

## New

- **QML runtime test.** CI loads the real plugin offscreen against stand-ins for Quickshell and Omarchy, with the real Python backend behind them, and fails on any QML warning. The run covers:
  - every view on an empty store;
  - a full manual cook: create, reading, note, unit switch, each dialog, finish;
  - the demo cook and a saved cook's history;
  - a larger font size.

  The stand-ins expose only the palette and type scale Omarchy documents. The test refuses Bluetooth scanning and device selection. With the 0.5.0 QML it fails on the colour bugs above.
- **Home Assistant bridge tested in CI** against a real local Home Assistant Core. The test covers unit conversion, Home Assistant's own timestamps, unavailable and stale entities, and token checks.
- **[OMARCHY-ACCEPTANCE.md](OMARCHY-ACCEPTANCE.md):** a step-by-step checklist and results template for the first run on Omarchy.
- **[ADAPTER-CANDIDATES.md](ADAPTER-CANDIDATES.md):** a review of whether MEATER, ThermoPro, Inkbird, FireBoard and Combustion thermometers could be supported, and how. No new brand is supported.
- **For contributors:**
  - issue forms for bugs, Omarchy acceptance results and thermometer requests;
  - [SECURITY.md](SECURITY.md) for private vulnerability reports;
  - a rewritten README and a [CHANGELOG.md](CHANGELOG.md);
  - design, research and QA notes moved to [docs/](docs/README.md).
- **CI actions** moved to their Node 24 releases.

## Software validation

All of these passed in CI on `main` after PR #15, and the backend, QML and browser tests also passed locally:
- **Backend:** tests pass on Python 3.9 and 3.13, along with the community benchmark tests.
- **Bridges and delivery:** the MQTT broker, ntfy delivery and Home Assistant Core tests pass against real local servers.
- **Native QML:** `qmllint` finds no syntax errors, and the QML runtime test passes all four scenarios.
- **Browser:** the unit and packaging tests pass, and the axe-core WCAG 2.1 A/AA audit reports no violations in any view at desktop and phone widths.
- **Rendered check:** an offscreen render of the panel at the default and a larger font size shows themed colours and scaled text.

## Not verified

- **Native plugin:** not yet run on Omarchy or Quickshell. The runtime test proves OmaPit's own QML loads cleanly against stand-ins built from Omarchy's documentation, not that real Quickshell behaves the same. [OMARCHY-ACCEPTANCE.md](OMARCHY-ACCEPTANCE.md) checks 2.2 and 4.3 cover this release's fixes.
- **Hardware:** unchanged from 0.5.0. One CQ60 delivered food readings in a hand-warming test. Accuracy, ambient, battery, range, reconnection, alarms on real cooks and Linux/BlueZ reception are untested.
- **Integrations:**
  - No thermometer has been tested through Home Assistant, and no real MQTT publisher has been tested.
  - Phone notification receipt is untested.
  - Screen-reader testing has not been done.

## Upgrading

Run `python3 packaging/install.py` from the new checkout, then restart Omarchy's shell. This release does not migrate the cook store. See [INSTALL.md](INSTALL.md).
