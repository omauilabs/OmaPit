# Software and visual asset licensing

LICENSE covers original OmaPit software, documentation, and owner-authorized original visual assets distributed with this repository. Third-party dependencies retain their own licenses, including backend/adapters/CHEFIQ-LICENSE.txt.

## Owner-authorized visual bundle

On October 5, 2026, the project owner confirmed ownership of the AI imagery and authorized inclusion of the complete visual bundle in the public open-source repository. This supersedes the earlier local-only media exclusion.

- Culinary card atlases, sauce textures, guide illustrations, cut photographs, and wordmarks in `preview/public/assets`: AI-generated project artwork.
- `preview/public/assets/themes/material-atlas.jpg`: generated with the built-in image-generation tool, 1536×1024 RGB; no third-party team logos.
- `preview/public/assets/cards/hotSauces.jpg` and `rubRegions.jpg`: generated culinary atlases, 1448×1086 RGB; no copied vendor photography or logos.
- `preview/public/assets/cuts/*.glb`: animal meshes exported through the owner's paid Meshy workflow. Face/region data are project-generated annotations.
- `preview/public/favicon.svg` and `preview/public/assets/icons/apple-touch-icon.png`: hand-written SVG flame icon using the app's amber and background colors, plus a 180 px PNG rendered from it; original OmaPit artwork.
- Remaining runtime visual/animation assets in `preview/public/assets` and `assets/grill.png`: project visual bundle included under the owner's authorization.

Generated culinary illustrations do not depict tested recipes or actual commercial products. Anatomical regions and educational diagrams retain the validation limits documented elsewhere. This license does not grant rights to third-party trademarks or manufacturer media not included in the bundle. Original user attachments, private generation archives, journals, and local sensor reports are not distributed.

## Bundled fonts

The browser preview bundles DM Sans and JetBrains Mono through the `@fontsource/dm-sans` and `@fontsource/jetbrains-mono` npm packages, both under the SIL Open Font License 1.1 (OFL-1.1). The licence text ships in each package. The fonts are served with the app; OmaPit makes no requests to font services.
