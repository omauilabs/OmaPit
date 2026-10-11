# Sauce pour

The regular Sauce Explorer shows a live WebGL liquid-mesh animation with Pause, Replay and Hide/Show controls. No special URL parameter or video is required.

The animation uses 120 frames of Blender Mantaflow viscous liquid geometry at 24 frames per second. A rounded card collider and pool guides direct liquid toward the left and right sides. The pool begins with a small overhang so the flow can spill around the rounded ends. An initial top-edge pool gives the continual-pour view an established liquid surface. The browser renders cached geometry using a physically based wet material and soft environment lighting with restrained wet highlights.

The stream begins flush with the actual subnavigation bottom border. Its landing position, width and falling region follow the hero card’s rendered dimensions. Geometry is fitted to that layout, so its displayed proportions are art directed. A render mask protects the card face from front-edge spill; the top pool and exterior side runoff remain visible.

A reduced-motion preference starts playback paused. Hidden and offscreen views stop advancing. Pause freezes the displayed mesh; Replay starts at the first simulation frame. Later playback repeats the settled segment; this is a finite mesh cache, not an endlessly recomputed simulation or a verified seamless loop.

The simulation parameters are artistic rather than measured BBQ sauce rheology. The production build and five fluid-cache/Sites checks passed. Chrome desktop and phone views were inspected: the stream canvas and subnav border matched at 168 px and 292 px respectively, the card-face mask protected the content, and Pause, Replay and Hide/Show worked without console errors. Screenshots are saved as sauce-fluid-desktop.png and sauce-fluid-mobile.png. These implementation checks do not constitute photorealism approval or a seamless-loop acceptance. Unsupported graphics or asset failures display an unavailable state. No recipe, dinner-plan or cook data is changed.
