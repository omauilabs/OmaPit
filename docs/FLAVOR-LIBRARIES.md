# Flavor libraries and maker

Implemented October 5, 2026. Plan → Explore → Hot sauces adds 24 distinct hot-sauce profiles and an independent editable maker. BBQ Sauces expanded from 8 to 30; Rubs from 6 to 30. Existing styles and saved-recipe identifiers remain available.

## What authenticity means in this release

Cards distinguish a documented regional style, a named cook’s variation, a commercial reference, and an original OmaPit variation. Each reference entry links to its culinary source. Regional traditions have household variations; the application does not claim one universal formula. All maker proportions are independent home interpretations awaiting kitchen trials. They are not copied restaurant recipes or reverse-engineered commercial products.

Examples include Mexican árbol and ancho salsas, Thai sriracha, Caribbean pepper sauces, Tunisian harissa, Ecuadorian ají criollo, chimichurri, chermoula, Japanese yakitori tare, Cantonese char siu, Santa Maria seasoning, berbere, ras el hanout, baharat and shichimi. Dry jerk is explicitly an adaptation rather than a substitute for fresh Scotch bonnet and scallion marinade. Quick Louisiana Red is explicitly fresh, rather than aged.

## Sources reviewed

- [TABASCO hot sauce family](https://www.tabasco.com/products/hot-sauces/) and [Original Red](https://www.tabasco.com/products/hot-sauces/original-red-sauce/): commercial flavor context; Original Red ages peppers up to three years.
- [Frank’s Original Cayenne](https://www.franksredhot.com/en-ca/products/franks-redhot-original-cayenne-pepper-sauce): cayenne, vinegar and garlic profile.
- [Cholula](https://www.cholula.com/en-us/): árbol and piquín commercial context.
- [Mely Martínez: árbol salsa](https://www.mexicoinmykitchen.com/chile-de-arbol-salsa-recipe/), [verde](https://www.mexicoinmykitchen.com/salsa-verde-recipe/), [habanero emulsion](https://www.mexicoinmykitchen.com/creamy-habanero-salsa/), [ancho–árbol](https://www.mexicoinmykitchen.com/ancho-arbol-chile-pepper-salsa/), [habanero tomatillo](https://www.mexicoinmykitchen.com/habanero-tomatillo-salsa-recipe/).
- [Pailin Chongchitnant: sriracha](https://hot-thai-kitchen.com/sriracha-hot-sauce/).
- [Lee Kum Kee sambal](https://usa.lkk.com/en/industrial/products/sambal-oelek), [Nando’s PERi-PERi](https://www.nandos.co.uk/UK/cook/medium-peri-peri-sauce): commercial style context.
- [Chris De La Rosa: Caribbean pepper sauce](https://caribbeanpot.com/traditional-caribbean-pepper-sauce/), [pineapple peppersauce](https://caribbeanpot.com/grilled-caribbean-pineapple-peppersauce/), [guava peppersauce](https://caribbeanpot.com/insanely-good-guava-peppersauce-hot-sauce/), [guava BBQ](https://caribbeanpot.com/caribbean-guava-bbq-sauce-julymonthofgrilling/). OmaPit does **not** adopt the source’s room-temperature storage suggestion for a customized blend.
- [Suzy Karadsheh: harissa](https://www.themediterraneandish.com/harissa-recipe/), [harissa honey](https://www.themediterraneandish.com/harissa-honey-chicken/), [chermoula](https://www.themediterraneandish.com/chermoula-recipe/), [baharat](https://www.themediterraneandish.com/baharat-spice-blend/), [za’atar](https://www.themediterraneandish.com/what-is-zaatar-and-how-to-use-it-11-best-zaatar-recipes/).
- [Ottolenghi and Tamimi: zhoug adaptation](https://ottolenghi.co.uk/pages/recipes/crispy-chicken-carlin-peas-zhoug).
- [Layla Pujol: ají criollo](https://www.laylita.com/recetas/aji-criollo/), [chimichurri](https://www.laylita.com/recipes/traditional-chimichurri-sauce/).
- [Kenji López-Alt: Peruvian-style green sauce](https://www.seriouseats.com/peruvian-style-grilled-chicken-with-green-sauce-recipe): chef adaptation.
- [Nami: yakitori](https://www.justonecookbook.com/yakitori/), [shichimi](https://www.justonecookbook.com/shichimi-togarashi/).
- [Maangchi: spicy bulgogi](https://www.maangchi.com/recipe/spicy-bulgogi), [Nagi: char siu](https://www.recipetineats.com/chinese-barbecue-pork-char-siu/), [Thai satay](https://www.recipetineats.com/beef-satay-with-thai-peanut-sauce/).
- [Santa Maria Valley official cookbooks](https://santamariavalley.com/barbecue/cookbooks/), [Visit Jamaica: jerk](https://www.visitjamaica.com/blog/post/the-secret-to-true-jamaican-jerk/).
- [Weber rub fundamentals](https://www.weber.com/US/en/blog/tips-techniques/bbq-rub/weber-31096.html), [KC rub](https://weberseasonings.com/products/weber-kc-bbq-rub/), [McCormick Montreal](https://www.mccormick.com/collections/grill-mates-foodservice/products/mccormick-grill-mates-montreal-steak-seasoning-29-oz), [Creole](https://www.mccormick.com/collections/zatarains/products/zatarains-creole-seasoning-8-oz), [Spice House ras el hanout](https://www.thespicehouse.com/products/ras-el-hanout), [berbere](https://www.thespicehouse.com/products/berbere).
- [USDA handling guidance](https://ask.fsis.usda.gov/article/How-do-I-handle-leftovers-safely): prompt refrigeration at 40°F or below; perishables must not remain out beyond two hours (one hour above 90°F).

## Maker behavior and limits

Ingredient parts normalize by mass to an editable 10–10,000 g ingredient charge. Ingredients labeled cooked, drained or rehydrated are weighed in that prepared state. Heating, straining and transfer change final yield; grams do not imply milliliters or bottle capacity. Dinner sizing allocates an editable gram portion per person plus reserve. Ingredient percentages are not Scoville measurements. Customized preparation methods need review. Allergen labels accompany prepared ingredients; labels must still be checked.

Recipes save locally, validate on load, retain custom proportions and batch weight, and export a weighed text recipe with culinary references and handling caveats. No upload, cloud account or active-cook changes occur. There is no fermentation, canning or shelf-life certification in this release.

## Images

Two 1448×1086 photographic-style AI texture atlases, each 4×3 square tiles, were visually reviewed for tile order and culinary context. They are illustrative surfaces, not photographs of proprietary bottled products. File paths: preview/public/assets/cards/hotSauces.jpg and rubRegions.jpg. Existing regional BBQ photo textures remain in use; new herb sauces use the green herb atlas tile.

## Next culinary acceptance

Kitchen trials of small batches, documented taste adjustments, regional contributor review and licensed actual food photographs. Fermentation and preservation need separate validated procedures before they can be supported. Software validation does not substitute for kitchen testing.
