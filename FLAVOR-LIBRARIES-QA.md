# Flavor library software verification

October 5, 2026. Browser preview verification, not a native Linux or kitchen acceptance report.

- 16 focused tests passed across BBQ sauce allocation, rub weights and the new hot-sauce catalog/maker.
- Catalog totals: 24 distinct hot sauces, 30 BBQ/grilling sauces and 30 rubs. Existing BBQ and rub IDs retained.
- Hot-sauce search for Ecuador returned Ají Criollo. Selecting it synchronized the story, recipe and source.
- A 400 g ingredient charge produced 112 g chili, 60 g cilantro, 112 g water, 48 g onion, 40 g lime, 24 g garlic and 4 g salt; total 400 g.
- Adding cooked carrot renormalized every ingredient. Reset restored the selected starting proportions.
- A blank batch displayed validation and disabled Save. Invalid quantities and unknown ingredient keys are rejected by calculation and saved-record tests.
- Saved My Ají Criollo, 400 g, and verified its proportions and weight after reload. This useful example remains in the local browser; no cook or hardware state changed.
- Twelve guests × 5 g × 10% reserve produced 66 g and the Use this batch size action updated the maker.
- Export preview contained the actual weighed Harissa recipe, preparation, culinary reference and refrigeration/provenance caveats. The in-app browser did not expose a download event; the existing preview/copy fallback remains usable. A native file-save result is not claimed.
- BBQ search selected Chermoula from 30 styles. Green herb texture matched the sidebar and hero; sauce color changed accordingly. Dynamic family options include Herb, Soy, Peanut, Fruit and Spiced.
- Rub search for Japan selected Shichimi Togarashi Style from 30 blends. The multicolor sesame/chili/nori photograph-style texture and Japanese source matched. Flavor family filtering is available.
- Combined heat and flavor filters correctly reduced Mild + Garlic to one style. Show 8 more expanded the list from 8 to 16 cards. A single search match spans the available card width. The final 317 px mobile card is covered by a 329 px square atlas tile, preserving its photo proportions without blank edges.
- Desktop and 390×844 mobile layouts visually inspected. Mobile did not overflow horizontally. The narrow-screen ingredient table remained readable and controls stayed within the page.
- Sauce and spice atlases visually reviewed as illustrative AI textures; both are 1448×1086 with 4×3 square tiles. Copied into public and preview build assets.

Production build completed successfully, with the existing public-asset resolution and large Three.js chunk warnings.

No live thermometer scan, hardware test, community submission or external publishing occurred. Culinary proportions remain untested. No shelf-stability, exact Scoville, fermentation or native-Linux acceptance claim.
