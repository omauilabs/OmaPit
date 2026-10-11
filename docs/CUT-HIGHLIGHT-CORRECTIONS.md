# Cut highlight correction

The previous correction used unconstrained, brightness-weighted flood fills and interpolated vertex labels. It was not visually validated across every panel on both sides. Decorative ridges could steal regions, and triangles crossing several vertex labels produced wedges and gaps.

The current viewer loads exclusive triangle masks for beef, pork, lamb, goat, buck and doe. Offline authoring uses model-specific engraved-panel traces as fixed interior anchors, then a bounded mesh-topology refinement around adjacent seams. Heads, tails, horns/antlers and hooves are excluded. Boundary triangles use majority ownership; unassigned three-way junctions prevent ambiguity without punching gaps all along a seam. Disconnected patches use their traced panel membership rather than leaving arbitrary holes. The doe has its own recalibrated traces.

Rendering and ray picking use the same triangle ID. Vertices shared across different regions are split while preserving normals, UVs, index winding and material groups. This avoids overlapping/interpolated masks without adding an offset overlay mesh. Regression tests check this behavior and verify each mask against the exact GLB topology and digest.

These are sculpture-panel boundaries, not internal muscle dissections or butcher-validated carcass maps. The goat sculpture has one shared rack/loin panel; both selections intentionally highlight it. Poultry masks remain pending model import and are not part of this correction.

The preview contains the updated viewer and masks. Browser audit images are saved in cut-alignment-audit.

Validation: production build passed, 11 geometry/catalog tests and 4 packaging tests passed. All six masks passed offline head/hoof exclusion and exclusive-ID checks. Final browser verification completed after the majority-boundary cleanup: all 40 region selections were captured and visually reviewed from both sides (80 screenshots). Direct clicking on the cow rib surface selected Ribeye. Final screenshots use the final- prefix in cut-alignment-audit; cut-highlight-correction.png shows the current viewer. Sculpted seams remain approximate, with occasional fine irregularities inherited from the generated meshes; this is not a claim of butcher-validated anatomy.
