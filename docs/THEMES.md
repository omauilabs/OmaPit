# OmaPit Material Atelier

Settings → Themes → choose a preview → Apply theme. Five themes: Steakhouse, Backyard BBQ, American Football, Thanksgiving and Christmas. Omarchy restores the original palette. Choices persist on this browser independently of logo, animation and motion. Active cook and device mappings remain unchanged.

Steakhouse: walnut, oxblood and brass. Backyard BBQ: cedar, cream linen and sage checks. Football: midnight green, pebbled leather and chalk accents. Thanksgiving: parchment, copper and maple detail. Christmas: evergreen velvet, burgundy tones, gold and pine lights.

Themes change surfaces, accents, temperature colors, heading typography, materials, shadows, navigation and forms. Add future themes through preview/src/themes.js and run tests/themes.test.mjs. New text and accent colors must contrast at least 4.5:1 against base and panel surfaces. Photographic cards keep their own readable overlay colors.

Original material artwork is saved at preview/public/assets/themes/material-atlas.jpg (1536×1024 RGB), created using the built-in image-generation tool. Code is browser-verified; native Linux acceptance is separate.

## Artwork prompt
Create a single seamless-material contact sheet for premium culinary app skins, landscape 1536x1024, exactly 3 columns by 2 rows, six equal rectangles flush no gutters no text no labels. Top left dark walnut fine woodgrain and subtle oxblood leather edge antique brass grain. Top middle pale weathered cedar cream linen fine sage gingham faint woven detail. Top right extremely dark forest green turf plus fine brown pebbled football leather no logos, subdued white seam in far corner. Bottom left warm cream parchment mottling and burnished copper, realistic russet maple leaves only along bottom edge. Bottom middle very dark evergreen woven velvet with subtle burgundy undertones, realistic fine pine needles gold fairy light bokeh only along far edges. Bottom right neutral dark charcoal fine cast iron grain. These are photo-real detailed flat background textures, evenly lit, no objects in center, no UI, no food, no text, no watermarks, no thick borders. Fine tactile detail, restrained elegant materials. Each rectangle should be one cohesive background, keep center 80 percent low contrast for later overlaid UI. Full bleed.

## Validation
13 focused tests passed, including palette contrast, storage fallback, theme application roles, probe-state handling and sauce calculations. Visual checks covered all five themes in Cook, light-theme Sauce Explorer, mobile theme selection without horizontal overflow, persistence after reload and keyboard tab navigation. The final production build and Settings gallery were verified on port 4176 with no observed console errors; light preview text was checked against its own palette. No hardware scanning or benchmark upload was performed.
