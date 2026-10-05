# Always-visible probe monitor

A sticky monitor appears above the main header on every route, independent of active cook source. Each detected non-replay thermometer shows Food and Ambient temperatures in the chosen unit. The cook-selected thermometer appears first; additional probes remain accessible in the horizontally scrollable monitor.

The existing API polling refreshes readings every five seconds. Each channel ages independently. Live requires a finite, valid reading, a fresh flag, an available service, and an original sample timestamp within 30 seconds. Stale values are explicitly last readings with their age. Invalid/missing channels show no reading; service loss marks retained values offline. Demo recordings and replay captures are never presented as live probe data.

The pixel probe illustration is vector art, with a crisp animated pixel signal on fresh channels. Global motion and reduced-motion preferences stop animation without stopping telemetry. Clicking Probe monitor opens Devices without scanning or changing cook mappings.

Validation: four focused tests passed, desktop and 390px mobile browser checks passed, no browser console errors observed. After scrolling, monitor top position was 0px. Plan/Hot sauces navigation preserved the monitor. Existing CQ60 food sample appeared as a last reading, while its invalid ambient channel remained unavailable. No hardware scan or active cook mutation was performed.

Screenshots: probe-header-desktop.png and probe-header-mobile.png. New physical sensor readings and native Linux behavior remain untested in this UI pass.
