# Prototype Instructions

Run the local server yourself and open the preview in the browser available to this environment. Do not give the user server-start instructions when you can run it.

Before making substantial visual changes, use the Product Design plugin's `get-context` skill when the visual source is unclear or no longer matches the current goal. When the user gives durable prototype-specific design feedback, preferences, or decisions, record them in `AGENTS.md`.

When implementing from a selected generated mock, treat that image as the source of truth for layout, component anatomy, density, spacing, color, typography, visible content, and hierarchy.

Build app UI in `src/`. Keep `.openai/hosting.json`, `worker/index.js`, `scripts/prepare-sites-build.mjs`, and `tests/sites-worker.test.mjs` intact so the same local prototype can be handed to Sites. Before a Sites handoff, run `npm run build` and `npm run test:sites`; the build must leave `dist/client/index.html`, `dist/server/index.js`, and `dist/.openai/hosting.json`.

## Navigation preference

The user finds the flat main navigation too long and busy. Keep primary navigation organized around Cook, Plan and Journal; show only the selected area's views in contextual navigation. Devices stays a separate utility control. Preserve every existing destination and alarm attention access.

Notification permission/status and test controls belong in a bell popover at the top right, alongside Devices and the °F/°C toggle, rather than a persistent full-width bar. Keep urgent cook alarms visible.

## Cut Explorer preference

The user selected the first Cut Explorer mockup: a dominant 3D animal on the left, cut inspector on the right, and synchronized cut cards underneath. Keep it under Plan → Cuts. Beef, pork, lamb and goat share one selection state between cards and mesh regions. Use real geometry, orbit/zoom/reset and accessible text selection. Never silently change an active cook while browsing cuts. Source visual: ../omapit-cut-explorer/01-anatomical-workbench.png (resolved at outputs/omapit-cut-explorer in this workspace). Region maps need butcher review before anatomical-accuracy claims.

## Sauce Explorer

Keep Sauce Explorer under Plan → Sauces. It should cover regional barbecue traditions as well as sauce families, let users customize and save blends, and calculate quantity from guest count and multiple foods. Separate table portions from finishing coats; count table portions once per guest. Show editable raw-to-edible-cooked yield and all volume assumptions. Recipes are original, untested starting blends, not restaurant formulas or shelf-stable recipes. Preserve active cooks while users browse or plan sauces.

Center primary navigation on the app width independently of the brand and utility widths, and center contextual subnavigation below it. Keep mobile navigation on its own centered row.

Sauce library cards use distinct photoreal sauce backgrounds matching each regional style’s color, viscosity and spice texture. Keep type and region labels readable over a dark scrim.

Background material should be theme agnostic: derive gradients and surfaces from theme background/foreground/accent roles, use restrained neutral grain and soft layered shadows, and preserve content readability.

Animal highlights must follow each imported sculpture's visible seams. Preserve textured materials and derive render masks and ray picking from the same model-specific region data. Do not reuse the former primitive model's bounding-box slices. Deer has Buck/Doe variants with a shared venison catalog; antlers, head and tail must stay unassigned.

## Meal explorers

The user requested Rubs, then a separate grilled Veggies explorer, then Bread, then regional Sides. Keep all six explorers accessible through one centered Plan explorer selector, preserving Cuts and Sauces and direct hash destinations. Rub amounts use grams, normalized weight parts and editable application rate; show salt/sugar contribution and never infer existing seasoning. Food portions use editable guest count, portion and reserve. Save to a shared local dinner list, without changing the active cook. Regional context is linked to primary sources; original recipes and portions are untested estimates.

Navigation labels should have contextually correct Phosphor icons next to them. Preserve readable text, centered main/context navigation and the compact explorer selector; decorative icons must not duplicate accessible names. The explorer selector shows the current explorer's icon alongside it.

## Logo settings
Provide Meat, BBQ equipment and Burning charcoal wordmarks in Settings. Meat is the default; remember an explicit choice locally and show it in the main app header. Keep Settings a utility instead of another primary navigation area.

## Sauce pour
The user rejected the basic pour effect. Keep the visual test as a live rendered animation without video, hands or bottle. Aim for a heavy viscous stream, smooth impact folds, irregular spreading pool and realistic wet lighting. Preserve Pause/Replay, reduced-motion handling and offscreen pausing. Do not claim a physically validated fluid simulation.

The sauce pour lands on the top edge of the hero card, not inside its content. Continual pouring should spread along that edge, overflow the exterior left/right sides, and form detached falling drops. Keep text readable and controls clickable.

The sauce pour is visible on the regular Sauce Explorer page by default, without a special query parameter. Provide Pause, Replay and Hide/Show controls. Keep the stream shorter and thicker; corner runoff should be continuous without resetting the hanging ribbon length.

Cut Explorer offers two selectable views: 3D view with synchronized model/cards, and Cards only with the full cut grid and no animal model. Preserve animal/variant and selected cut across view changes; cards-only opens cut details on demand.

The Live Cook sample introduction should be a compact banner with a clear demo label, concise explanation and separate setup action, leaving the active cook hero prominent. Preserve offline guidance and active-cook data.

Chicken and turkey belong in both Cut Explorer views, with whole-bird, breast, wing, thigh and drumstick cards. Whole-bird selection highlights all mapped meat panels, not head/feet/tail. Preserve recognizable sculptural anatomy and align regions to the imported poultry mesh.

Peppers is a separate Plan explorer with source-linked Scoville ranges, regional associations, flavor, form, grilling notes and comparisons. Heat is a range, not a batch measurement; logarithmic bars must be labeled. Keep regions distinct from exclusive birthplace claims and preserve active cooks.

Cut highlights must have exclusive triangle ownership shared by rendering and picking, without interpolated boundary wedges or floating spillover. Audit both sides of every imported sculpture and leave engraved separators unassigned. Automatic bright-ridge flood fills are insufficient visual acceptance.

## Preparation guides
Keep Knives & cutting and Hunter’s guide as separate Plan selector destinations. Cover knife families, grain, trimming, portioning and poultry; keep hunter field care, skinning, cooling, breakdown and storage source linked. Clearly distinguish big-game instructions from bird techniques. Persist a personal readiness checklist without certifying safety; preserve active cooks.

## Equipment & fire
Provide a separate Plan guide for cooker types, setup/shutdown, wood and fuel, methods, maintenance and troubleshooting. Save cooker-type preferences locally without implying hardware control. Keep exact-model ignition, clearance, fuel compatibility and emergency instructions authoritative; distinguish hot smoking from cold-smoke preservation. Wood pairings are suggestions, not measured or exclusive rules.

## Meat market
Keep market data provenance visible: reporting date, scope, grade, condition, unit and advertising-outlet count. Dated snapshots must never masquerade as live store prices. Preserve distinctions among advertised retail benchmarks, monthly retail averages and user-entered local quotes. Meal costs use editable edible cooked yield and reserve, with transparent raw-weight calculations; no active cook mutation.

## Header and explorer readability
The main header has live detailed pixel-fire animation beneath the controls, with sparks and smoke; respect motion settings and keep utility popovers unclipped. Explorer right-side detail panels need readable body type, generous line spacing, stronger contrast and clear labels across every family. Hero photo labels require a legible backing and contrast.

Primary Cook/Plan/Journal navigation stays transparent over the animated header with a continuous contrast scrim, no individual dark boxes. Pixel fire needs fine square pixels and narrow detailed tongues rather than horizontally broad stretched flames. Meat Market is a dedicated Plan subnav destination outside the explorer dropdown; preserve its direct hash route.

Explorer browse cards use subject-specific photographic backgrounds with a dark gradient for readable overlaid text. Match each market cut, rub blend, pepper variety, cooker, hardwood, bread, side, vegetable and knife; do not use one generic category image. Generated photographs remain illustrative, not brand or species certification. Preserve selected borders and keyboard focus.

Header animations are selectable in Settings: pixel fire, detailed falling meats, and detailed falling grilling utensils. Save locally, preserve motion preferences and readable navigation. Use recognizable textured sprites with square pixels, varied drift and gentle rotation.

Cutting lessons use realistic photographic illustrations with separate crisp SVG technique overlays, step selection, show/hide guides and enlargement. Fibers and cut lines must cross correctly. Clearly distinguish serving a cooked poultry breast from raw joint breakdown; generated images are introductory examples, not universal anatomical maps.

Heat-path schematics use cooker-specific realistic cutaways for all sixteen cooker types. Separate dominant heat-transfer paths from airflow, with numbered components and a native dialog enlargement. Do not depict drum cookers as universally baffled, griddles/contact grills as convection cookers, or conventional offsets as reverse-flow. Generated cutaways remain teaching examples, not model-specific engineering schematics.

Hunter’s guide is for novices. Provide stage- and species-specific realistic learning imagery, plain-language anatomy/processing definitions, what-to-look-at captions, labels and enlargement. Deer imagery does not stand in for hog or birds. External field-dressing orientation images are not incision maps; pair deer procedure stages with verified Minnesota DNR demonstrations. Keep generated illustration boundaries clear and preserve cooling, contamination and disease guidance.

Backup restore has a theme-role-based panel, styled native file control, explicit selected-file review and Restore action, and a clear explanation when the journal is not empty. Preserve the empty-journal restriction. Main nav uses one soft continuous reading scrim to prevent the animated background drowning the labels, without boxed primary buttons.

Sauce pour now uses animated pixel art exclusively, replacing the realistic fluid renderer. Keep crisp square pixels, a recognizable thick BBQ sauce stream beginning at the subnav border, pooling on the hero's top lip and runoff outside the card. Preserve Pause/Replay/Hide, reduced-motion and offscreen pausing.

The pixel sauce pour is ambient with no visible controls. Match its palette to the selected regional sauce (including gold, white, vinegar and dark dip). The hero uses the selected sauce card's photograph under a dark readable scrim; keep all text and links legible and preserve reduced-motion/offscreen handling. This supersedes the earlier Pause/Replay/Hide preference.

Use title case for every sauce style name, including its last word: Kansas City Red, Carolina Gold, Alabama White, Texas Pepper Mop and Kentucky Black Dip. Preserve user-entered custom blend names.

Additional selectable pixel-art header scenes: Professional kitchen with working cooks, Smoke only with no flames/embers, and Backyard BBQ with people. Keep periodic seamless motion, readable nav, local persistence and motion/visibility handling. Scene detail includes equipment, food, work surfaces and environment rather than generic falling sprites.

Logo Settings now includes a fourth Animated pixel art wordmark: hand-drawn OmaPit glyphs with cast-iron/copper bevel texture, moving ember highlights, flames, sparks and smoke. It is a real canvas animation, not a video. Preserve default Meat, saved selection, accessible brand name and reduced-motion/global-motion/offscreen handling. Four choices use a balanced two-column grid.

Keep sauce-pour spacing compact: the desktop intro-to-card gap is 28px, and mobile has only a 12px card offset. The stream still starts flush at the subnav border, pooling on the hero edge. Do not restore the former 120px/80px empty spacing.

Sauce form controls use theme surfaces and spin-button-free numeric inputs (preserve number validation/keyboard behavior). Weight/Unit are concise visible labels with full food-index accessible names and a 90px unit column. Pixel runoff must connect to the pool through overlapping rounded corner pixels, with rounded hanging bulbs rather than disconnected square ribbons.

Main header nav now uses a compact, bounded segmented pill with a selected surface, replacing the former central radial scrim. This supersedes the earlier transparent-nav preference. Kitchen/backyard are continuous full-width environments with distinct stations and a walking runner/guest, rather than repeated scene tiles. Smoke-only is a dense continuous turbulent field, never rectangular puff particles. Use accumulated active time, stable frame buckets and 60fps scene motion; pausing/visibility/resize must preserve phase rather than jump to wall time.

Animated pixel wordmark uses tighter one-cell kerning and a continuous fire bed rendered behind the letters, never individual flames attached to letter tops. Glyphs stay opaque and legible; animation uses stable 60fps time buckets.

Keep the top status bar visible on Cook, Plan explorers and Journal alike; hiding it on explorer pages shifts the header when changing sections. Reserve the root scrollbar gutter so short/long pages keep the same horizontal layout.

## Shared polish and community contributions
Keep forms and help messages readable, use theme roles for surfaces and focus states, and preserve photograph readability. Hardware testing is paused until the owner resumes it. Community benchmark contributions must be explicit opt-in to a named repository, aggregate-only and validated; live observation does not certify accuracy or untested features. Preserve manual mode and active journals during customizations. See ../AGENTS.md and ../community/README.md.

Settings uses compact Wordmark, Header & motion, and Community & agents tabs. Keep keyboard arrow/Home/End navigation, a global animation checkbox, default-off sharing guidance and an inspectable agent prompt. Do not turn a UI preference into hardware or upload authorization.

On narrow screens, keep the sauce stream along the intro’s right edge with reserved text space, landing on the hero top lip without running through the title. Keep the pool clipped to the card lip and connected runoff. Sauce motion follows the app-wide animation switch and live reduced-motion changes.

## Flavor libraries
Hot Sauces is a separate Plan explorer with an editable maker by ingredient weight. Keep regional, chef, commercial-reference and original-variation labels distinct. Reference links support culinary context; independent home proportions must never be presented as proprietary brand formulas or kitchen-tested authentic recipes. Do not estimate customized sauce Scoville ratings, pH, fermentation success or shelf stability. Keep source, preparation, allergens, preparation-loss caveats and refrigeration guidance in recipe exports. Preserve saved recipe identifiers and the active cook when expanding catalogs. Photographic sauce and rub cards need contextually appropriate textures and readable dark overlays.

Keep a sticky probe monitor above the main header on every view. Display actual device channels independently of demo/manual cook readings, with per-channel Live, last-reading age, unavailable and service-offline states. Replay captures never appear as live telemetry. Preserve unit preferences, global/reduced motion and the paused hardware-testing boundary.

Meat Market uses a compact two-column introduction: “Know the price. Plan the plate.” on the left and the dated source snapshot on the right, aligned with the dinner workbench. Stack on narrow screens. Keep search and price cards close to this introduction. Historical charts must distinguish weekly advertised prices, monthly retail averages and wholesale values; never join mismatched cut/grade/region series.

Sauce pour pixel art now uses a fine 1.25 CSS-pixel drawing grid instead of coarse 4px blocks, with 60Hz frame buckets, traveling specular ribbons, viscous ripples, connected quarter-round corner runoff and rounded accelerating droplets. Preserve compact layout, selected palette, readable card contents, phase continuity, reduced motion and offscreen pausing.

Themes follow the selected Material Atelier concept: Steakhouse, Backyard BBQ, American Football, Thanksgiving and Christmas, plus Omarchy. Settings → Themes provides previews and explicit Apply; persist locally under omapit-theme-v1. Preserve logo, header animation, motion and active journal independently. Use the shared theme registry and semantic color roles. Light themes retain ivory text over dark photographic cards. New theme records must pass base/panel contrast tests. Original generated material artwork has no team branding.

Scrollbars use slim theme-derived thumbs/tracks across the app, with no bright native trough. Sauce library reserves a small gutter. Sauce runoff uses mirrored quarter-annulus corners that join the top pool to the exterior vertical drips; avoid rectangular patches, wedges or detached runoff.
