# Customize OmaPit with your agent

OmaPit is designed for local customization and reviewable contributions. The browser product is in `preview/src`; Python data, transports and alerts are in `backend`; native Omarchy/QML entry points are the top-level QML files. Native Linux acceptance is still outstanding.

## Start safely

Ask your agent to read AGENTS.md and preview/AGENTS.md, identify your intended change and use a separate test database. Do not run a second backend against your cooking journal while testing migrations. Back up existing data before intentional migrations. Manual readings must continue to work without Bluetooth dependencies.

## Themes and UI

Supply `--background`, `--foreground`, `--accent` and `--accent-secondary`; the material layer derives surfaces from these roles. Keep decorative backgrounds independent of text contrast. Add logos in `preview/src/LogoSettings.jsx` and header scenes through `HeaderFire.jsx` / `HeaderScenes.js`, preserving default choices, saved preferences, keyboard names, reduced motion and offscreen pausing. Explorer catalogs live beside their components; add source attribution and accurate units for educational content.

## Adapters

Follow [ADAPTERS.md](ADAPTERS.md) for the adapter contract, required tests, capture format and compatibility rules. Keep transport → decoder → normalized samples → store separate. Missing battery/ambient is unknown; sentinel values are invalid; replay and historical imports cannot trigger live recording by default. Preserve timestamps and units. Test malformed, partial, future-version and multi-device data before proposing direct support. Use community reports to locate model/version gaps, not to certify whole brands.

## Contribute with an agent

Prepare a focused patch, relevant tests, a concise before/after explanation and evidence of browser validation. Your agent can generate and validate local hardware reports with community/benchmark.py. Automatic issue submission is available only after you explicitly opt in to a named repository. There is no global telemetry uploader and no report destination is configured in the distribution.

A suggested agent prompt is available in Settings → Make OmaPit better, together. Copying it does not authorize scanning, hardware tests or external submission.

## Verification

- Backend: `python3 -m unittest discover -s tests` from this directory.
- Benchmark collector: `python3 -m unittest discover -s community -p 'test_*.py'`.
- Native QML syntax: `python3 packaging/check_qml.py` (needs Qt's qmllint). It catches parse errors only; Quickshell and Omarchy types cannot be checked off Omarchy.
- Browser: build from preview with `npm run build`, then check affected desktop/mobile views, console errors, keyboard focus and motion preferences. Sites handoff also requires `npm run test:sites`.

Use an isolated checkout or local patch for personal customization. The public source repository is https://github.com/omauilabs/OmaPit. Release/install acceptance remains in progress. See ASSET-LICENSES.md before publishing bundled models or illustrations.
