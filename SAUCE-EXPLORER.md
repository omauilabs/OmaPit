# Sauce Explorer

Available in the browser app at Plan → Sauces, or http://127.0.0.1:4176/#sauces.

## Implemented

- Eight styles: Kansas City red, Eastern Carolina vinegar, Lexington dip, Carolina gold, Alabama white, Memphis red, Texas-inspired pepper mop and Kentucky black dip.
- Regional tradition notes, suggested food pairings, use guidance and source links.
- Search by style, region or food; filter by sauce family.
- Editable ingredient parts, normalized live to the dinner batch. Add/remove ingredients and reset the starting blend.
- Named saved blends (latest 30) in this browser's local storage. Loading a blend uses current dinner quantities. Storage failures are shown; export remains available.
- Up to eight foods, purchased or cooked edible weights, pounds/kilograms with conversion, adjustable yield, coat count and coverage rate.
- Import a saved Cut Explorer meal draft, retaining weight/unit and choosing a food estimate. Review the estimate after importing.
- Text export of ingredients, allocation, food assumptions, method and source links through the existing export dialog.

## Quantity model

Table sauce = guests × chosen US tablespoons/guest × 14.7868 mL.
Cooked edible kg = purchased kg × chosen yield percentage, or directly entered cooked kg.
Glaze = sum(cooked edible kg × coats × chosen mL/kg/coat).
Reserve = (table + glaze) × reserve percentage.
Batch = table + glaze + reserve. The shopping headline rounds up to 25 mL; ingredient amounts use the exact batch. One US cup is 236.588 mL. Ingredient volumes are approximate and may not add to final mixed yield; measure and top up as needed.

Two US tablespoons/guest, 15% reserve, food yields and 60 mL/kg/coat are adjustable product planning assumptions. They are not sourced consumption standards. Bone-in edible yield varies substantially. Glaze coverage depends on surface area and application; using weight is an estimate.

## Boundaries

Regional descriptions are source-backed. Formulas are original OmaPit starting blends, untested in a kitchen; they are not copied restaurant recipes. Ingredient changes may require a different preparation method. Allergen notes are reminders to check actual ingredient labels, not exhaustive certification. Refrigerate perishable blends, reserve clean table sauce before raw-meat contact, and do not use these recipes for canning or shelf-stability claims.

Blends are browser-local, not stored in the backend journal or synchronized between machines. Dinner inputs are transient. This feature does not change an active cook. No new native Quickshell screen or hardware integration is claimed.

## Sources

- https://amazingribs.com/tested-recipes/barbecue-sauce-recipes/benchmark-barbecue-sauces/
- https://bbqchamps.com/the-different-regional-barbecue-styles/
- https://destination-bbq.com/sc-bbq-survey-2025/
- https://bigbobgibson.com/products/original-white-sauce
- https://www.moonlite.com/images/Media_Kit.pdf
- https://ask.fsis.usda.gov/article/Can-you-reuse-meat-marinade

## Validation

Six quantity/catalog/export tests plus the existing cut and Sites packaging checks pass (13 total). Production build passes with the existing lazy Three.js chunk-size warning. Browser evidence is recorded in sauce-explorer-qa.md after interaction and responsive checks.
