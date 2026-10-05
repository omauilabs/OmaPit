# UI polish and community foundation

October 5, 2026.

## Implemented

- Shared theme-derived form and button surfaces, rounded panels, restrained shadows, stronger labels and body text, placeholder contrast and keyboard focus.
- Consistent headings and padding for cook forms, Devices, Journal and Settings. Narrow forms stack without losing their visible labels.
- Settings now separates Wordmark, Header & motion, and Community & agents. Tabs support arrow/Home/End keys. One global animation preference controls the sauce pour as well as existing header/logo/grill effects; it tolerates unavailable browser storage.
- The mobile sauce stream runs beside the intro rather than across its title. Pool growth stays within the card lip, with connected corner runoff.
- Settings provides inspectable/copyable agent instructions and default-off contribution guidance.
- Original software/docs have MIT licensing, customization/contribution contracts, a hardware issue template and explicit media-release boundaries.
- Community benchmark tooling: read-only selected-device aggregation, JSON Schema plus stricter privacy/evidence validation, local review preview, named-repository opt-in, revocation, fingerprint lookup and GitHub CLI submission.
- A local report was generated from existing CQ60 data, without scanning or modifying a cook. It records reception only, with all physical acceptance checks not-run. The compatibility manifest records that narrow evidence without claiming full acceptance.

## Verified

Production browser build passed. Fourteen benchmark tests passed, including strict metadata filtering, impossible aggregate rejection, replay/source isolation, read-only selected-device collection, explicit opt-in, destination integrity and mocked submission/deduplication. Existing backend suite: 69 tests passed, including HTTP tests on a temporary loopback port.

Desktop alarm forms and Settings were visually inspected. At 390×844, the top-level layouts of Sauces, Rubs, Veggies, Peppers, Bread, Sides, Equipment, Knives, Hunter's guide, Cuts, Market, Recipes, Insights, Devices, Cookbook and all four Cook views were inspected. Checked views showed no root horizontal overflow. Settings keyboard selection and motion off/on worked; the original enabled motion preference was restored. Browser console errors were empty. Temporary viewport override was reset.

Screenshots: ui-polish-alerts.png, community-settings-desktop.png and ui-polish-sauces-mobile.png.

## Remaining boundaries

No new hardware tests ran. Full feature/long-cook acceptance remains open. This UI pass did not re-certify anatomical cut highlighting, educational illustration accuracy or native Linux/QML parity.

No upload, GitHub issue, sharing configuration or scheduler was created. Submission is exercised with mocks; real repository routing needs the official destination and an opted-in owner. Pattern checks cannot identify every arbitrary secret placed in a model/version field, so owners must inspect metadata. Reports need maintainer review before compatibility promotion.

Bundled media redistribution rights and public release/install workflow still need review. The code license does not grant rights to third-party models, media or trademarks.
