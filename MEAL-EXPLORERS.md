# OmaPit meal explorers

Implemented October 4, 2026. Open the local app at http://127.0.0.1:4176/#rubs and use the centered Plan → Explore selector.

## Coverage

- **Rubs:** six original starting blends; food/pairing search; editable ingredient weight parts; additional spices; normalized grams; lb/kg conversion; adjustable application rate; salt and sugar per kg of food; local saved blends with load/delete; recipe export.
- **Veggies:** ten commonly grilled vegetables, from corn and asparagus to cauliflower and cabbage. Search and cooking-style filters, preparation, direct/indirect guidance, readiness cues, pairing and service notes.
- **Bread:** six bread choices, including toast, sourdough, flatbread, buns, cornbread and garlic bread. Toast versus bake filtering, preparation, service order and ingredient checks.
- **Sides:** eight dishes associated with Texas, Kansas City, North Carolina and Memphis. Region/name search, preparation suggestions, hot/cold cooking approach, make-ahead notes and pairings.
- **Dinner list:** shared local list across all four explorers, editable quantity assumptions before adding, item removal and text export. It does not alter the active cook, meal goals, timeline or probe data.

All six explorer destinations (including existing Cuts and Sauces) share one compact selector. Cook / Plan / Journal remain the primary navigation. Each explorer has a direct hash URL, and reload preserves the destination. Browse choices are local component state; saved rubs and dinner-list records survive browser reloads. They are not synced between browsers or devices.

## Quantities and content boundaries

Food estimates use guests × portion × (1 + reserve%). Prepared edible mass is different from raw shopping weight; this version intentionally labels that distinction. Whole pieces are rounded up for presentation. Portions are estimates, especially when several sides are served.

Rub estimates use raw food weight in kg × application g/kg. Ingredient parts are weight ratios, not volume measures. Salt/sugar calculations include the blend only, never existing brining or seasoning. Formulas are original, untested starting blends. Bread baking and hushpuppies refer users to their tested recipes rather than inventing precise cooking times.

Regional associations are examples, not exclusive definitions or restaurant recipe reproductions. Food photographs are AI-generated illustrative editorial assets. Original PNGs and exact prompts are in `explorer-images/`; optimized WebPs are bundled with the app. Content and formulas still need kitchen testing; no hardware acceptance is implied.

## Primary references

- [Weber vegetable grilling](https://www.weber.com/US/en/blog/tips-techniques/top-tips-for-grilling-vegetables/weber-48939.html): preparation and broad grate contact.
- [Weber cooking methods](https://contact-emea.weber.com/hc/en-ie/articles/360000623338-Stand-up-Kettle-Cooking-Methods): direct/indirect methods, including baking.
- [Weber rub ingredient context](https://weberseasonings.com/products/weber-original-dry-rub/): salt, sugar and spice ingredients. The app does not reproduce this product's formula.
- [Franklin Barbecue menu](https://franklinbbq.com/menu/): Texas menu context for pinto beans and potato salad.
- [Joe's Kansas City menu](https://www.joeskc.com/pages/restaurant-menu): beans and slaw menu context.
- [Visit North Carolina barbecue traditions](https://www.visitnc.com/list/taste-north-carolina-barbecue-styles-history-new-twists): pork, slaw and hushpuppies context.
- [Rendezvous menu](https://hogsfly.com/restaurant-menu/): Memphis sides context. The app's variations are original suggestions.

## Validation

Production build and 18 tests passed: existing Cut, Sauce and Sites regressions plus quantity rounding, gram conservation, equivalent weight units, invalid-input rejection and catalog checks.

Chrome verification on the production server exercised selection, vegetable search/filter, side region filter, rub editing/saving/loading, shared dinner quantities, combined export contents and reload persistence. QA dinner records were removed through the UI after testing. SQLite snapshots confirmed cooks, readings, events, foods, goals and plan tasks were unchanged.

Desktop and 390px mobile layouts were visually inspected. Mobile selection cards use a horizontal rail above the inspector, and the Plan selector fits alongside Timeline and New meal. Hardware and native OS packaging remain separate work.
