# Interactive and Video Contract

## Interactive viewer

Use a single visible page surface and keep the next/previous image underneath it. On a next action, rotate the current page around its left edge; on a previous action, rotate it around its right edge. After the finite transition completes, update the active index and reset the sheet without a visible jump.

Required behavior:

- show one page at a time;
- preserve upload order and expose `current / total`;
- support previous/next buttons, `ArrowLeft`, `ArrowRight`, spacebar, and touch swipe;
- ignore new navigation while a turn is running;
- disable the correct boundary control on the first and last pages;
- keep image pixels local and contained so faces, products, logos, and dense text are not needlessly cropped;
- do not auto-advance unless the user explicitly asks for an autoplay viewer.

## Page-flip video

Use a local HyperFrames composition with one root timeline and local image assets. Set an explicit canvas size and duration. Give every page the same stable box, a clear z-order, `transform-style: preserve-3d`, a vertical transform origin, and `backface-visibility: hidden`. Animate the current page with a finite `rotationY` turn; the next page remains underneath and becomes visible as the current page turns away.

A good first timing is approximately 0.45 seconds for the opening, 1.10 seconds of hold per page, 0.78 seconds per turn, and 1.60 seconds of final hold. Adjust only when the image count or reading needs require it. The final frame must remain on the last page, not black.

## Adaptive collage background

Treat each page's poster as the source of the background direction. Record a small per-page theme packet before authoring: dominant palette, contrast requirement, one material or structural cue, and one abstract collage translation. A phone poster may yield a circular dial, a night street poster may yield a receipt-like vertical strip, an architectural poster may yield an arch, and a black-and-white portrait may yield a graphic frame. These are source-derived abstractions; do not paste a second copy of the poster behind itself.

Use one background layer whose palette and collage pieces can transition between page themes, or split the video into small validated scenes when the treatments are materially different. Keep the page safe zone stable and let the surrounding field, up to two cropped source fragments, cutouts, outlines, and rule marks change with the active image. Avoid a fixed template whose only change is hue. Keep the layer order legible: field, source-derived fragment, cut-paper shape, line system, then page.

For identity labels and line treatment, use only copy the user supplied. A fixed top-left label and bottom-right label can anchor the sequence. Let collage carry the visual weight; retain only a short identity underline and, if needed, one or two crop/registration marks. Do not default to complete frames, long axes, or full-width baselines, and do not leave placeholder labels such as `PAGE FLIP` when the user has provided a real name.

Before delivery:

1. Run `npx hyperframes check` and clear resource, runtime, motion, and contrast errors. Mark only intentionally off-canvas page motion with the framework's explicit overflow attribute.
2. Render the MP4 locally with HyperFrames/FFmpeg after the user has asked for the video.
3. Verify the file with `ffprobe`: it must exist, be non-empty, have the requested canvas ratio, a plausible duration, and the expected frame rate.
4. Extract at least one midpoint during a turn and inspect it. It must show a page visibly rotated with the next page exposed, not a hard cut or blank frame.
5. Report whether the result is silent; never imply that page-turn sound or music exists unless it was actually added and verified.
