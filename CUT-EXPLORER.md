# Cut Explorer

Open Plan → Cuts in the browser companion. The selected direction uses a large animal model on the left, a cut inspector on the right and cut cards below.

## Working behavior

- Beef, pork, lamb and goat; 32 U.S.-named cuts.
- Real locally bundled glTF geometry, rendered with Three.js. Orbit, zoom and reset.
- Card selection highlights the parent region. A model region click filters the cards; multiple-cut regions require an explicit cut choice.
- Region buttons provide the same selection without mouse raycasting or WebGL.
- Search, species selection, planning weight and lb/kg controls.
- Add to meal keeps a browser-local next-meal draft. New meal pre-fills the cut and workflow. It never changes an active cook.
- Weight remains a planning note; it does not infer cooking times or temperatures.

## Boundaries

Cut boundaries are an anatomical overview, not an authoritative carcass dissection. Internal muscles highlight a parent primal. U.S. names are the initial catalog; regional cut systems have not been implemented. Butcher review is required before claiming anatomical accuracy.

The 3D assets are stylized, refined CC0 meshes rather than the high-detail sculpture in the design mockup. Native Quickshell rendering of this 3D view is not implemented; use the browser companion. Hardware connectivity is unrelated to this feature and remains subject to the existing test plan.

## Assets and references

Animal base meshes: [Farm and Working Animals HD, 3DAssets.dev](https://3dassets.dev/packs/farm-and-working-animals-hd), CC0 1.0, AI-generated per publisher. Meshes were refined for continuous surfaces and app regions. License: https://creativecommons.org/publicdomain/zero/1.0/

Meat images were generated for this prototype and are illustrative.

Cut naming references:

- https://www.beefitswhatsfordinner.com/cuts
- https://new.pork.org/cuts/
- https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/meat-catfish/lamb-farm-table
- https://cals.cornell.edu/nys-4-h-animal-science-programs/livestock/goats/goat-educational-resources/goat-product-id-study-guide
