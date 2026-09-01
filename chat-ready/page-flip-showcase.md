---
name: page-flip-showcase
description: Create a refined static, interactive, or rendered page-flip / flipbook showcase from one or more user-supplied images. Use this skill whenever the user asks to turn photos, product images, portraits, artwork, screenshots, or a sequence of images into a book-like page-turning display, a clickable one-page-at-a-time viewer, an editorial flipbook, an album page reveal, or a real page-flip video/MP4. Choose the output mode from the user's wording and never claim that a still image or interactive viewer is already a rendered animation.
---

# Page-Flip Image Showcase

## Mission

Turn supplied images into a memorable editorial flipbook scene: the images remain the content, while the book, paper, fold, shadow, and page-turn action provide the visual structure. The result should feel like a designed showcase of the user's work, not a generic scrapbook mockup or a stack of unrelated thumbnails.

Treat the supplied images as protected source material. Add a physical presentation system around them; do not casually redraw, duplicate, beautify, or replace the people, products, artwork, or screenshots inside them.

## Output modes

Choose the mode from the requested behavior:

- **Interactive viewer:** use when the user says “可以翻页”“一篇一篇翻”“点击翻页”“电子画册” or asks to browse pages manually. Deliver a local HTML viewer that shows one page at a time, supports previous/next controls, keyboard arrows, and touch swipe, and does not auto-advance.
- **Page-flip video:** use when the user says “做成视频”“MP4”“自动一页一页播放” or asks for a rendered animation. Deliver a local MP4 rendered from a deterministic HyperFrames composition with a real 3D page turn between each image.
- **Static showcase:** use when the user asks for a展示图、主视觉、海报 or only a visual direction. Deliver one polished still and explicitly label it as a still.

For a static showcase, unless the user specifies otherwise, make:

- one static portrait showcase, preferably 3:4;
- 1–6 supplied images, kept in upload order;
- a clean warm-white or lightly tinted paper field with restrained table/background context;
- an open book or editorial spread with one page visibly lifted mid-turn;
- no invented title, logo, date, author name, or fake publication information;
- a clean PNG/JPG preview. The image is a still key visual, not a GIF or video.

For interactive or video modes, more than six images are acceptable because each page is shown separately. For a static showcase, keep more than six images readable by proposing a smaller selection or a multi-frame series; do not shrink every image into illegible postage stamps just to fit them all.

## Intake

Before rendering, identify the minimum available facts:

1. Which images are included and what order they should follow.
2. Whether the user wants a static showcase, a true page-turn animation, or both.
3. Preferred ratio, reading direction, background mood, and whether any image must remain uncropped.
4. The visual role of each image: cover, left page, right page, turning page, or detail insert.

When the user has not specified these, use the default output above, preserve upload order, and place the active page-turn on the right side. Ask for the images only when none are available; do not invent source images.

## Workflow

### 1. Inspect the source set

Look for orientation, aspect ratio, faces, hands, products, important edges, built-in text, and the visual center of each image. Decide where a crop can safely happen. If a face, product mark, artwork detail, or screenshot control is near an edge, use a larger page margin or a contained page instead of cutting it off.

### 2. Choose the page structure

Read `references/layout-archetypes.md` when choosing among the main page structures; use one archetype only.

- **One image:** use it as the hero page, with a single turning sheet or cover edge to explain the page-flip idea. Never create fake alternate copies of the image.
- **Two or three images:** use an open spread plus one lifted page. Keep at least one image large enough to read at thumbnail size.
- **Four to six images:** use a restrained sequence across a spread and one or two page layers. Keep the visual hierarchy clear; not every page needs equal size.
- **Mixed aspect ratios:** place each image inside a believable printed area with margins or a controlled crop. Never stretch a portrait into landscape or vice versa.
- **A requested reading direction:** follow it. Otherwise, use the upload order and make the page movement obvious from right to left, as in a physical book being turned.

Choose one governing composition: open book, lifted single sheet, accordion-like sequence, or close editorial page detail. Do not combine all four into one cluttered scene.

### 3. Build the physical illusion

Make the page-turn readable through geometry rather than decoration:

- consistent camera angle and vanishing direction across every page;
- visible but modest paper thickness at the curled edge;
- one believable fold or lifted corner, with a coherent underside;
- contact shadows where paper meets paper and where the book meets the surface;
- a restrained cast shadow that supports the page movement;
- image surfaces that stay flat and printed, unless the user explicitly requests a tactile or embossed treatment.

The page-turn is the hero action. Keep the rest of the scene quiet so the viewer can understand which page was, is, and will be visible.

### 4. Render and refine

Use the image-generation tool with the supplied images as references when a crafted visual mockup is requested. Describe the layout, source protection, page mechanics, camera, lighting, and negative constraints explicitly. If exact pixel fidelity matters—especially for logos, UI, or dense text—prefer a composited page treatment or a contained image area over asking a model to redraw those pixels. For repeatable source-heavy showcases, use `scripts/build_flipbook_showcase.py` and inspect the rendered result rather than rebuilding the same geometry by hand.

Run one focused correction pass only when needed:

- correct a warped page or impossible fold;
- restore a cropped face/product/detail;
- remove a duplicated or hallucinated subject;
- simplify a background that competes with the images.

Change the page structure or crop before adding more props, texture, or effects.

## Visual taste

Aim for the feeling of a small art book, contact-sheet folio, or premium editorial portfolio: generous breathing room, tactile but clean paper, a clear sequence, and a page action that can be understood in one glance. The supplied images should do the emotional or informational work; the book is the framing device.

Prefer:

- one dominant page-turn gesture;
- off-white, soft grey, muted ink, or a restrained colour derived from the source set;
- realistic but not theatrical light;
- varied page scale with one clear hero image;
- empty space that makes the sequence feel intentional.

Avoid:

- random piles of pages, multiple simultaneous curls, or impossible accordion geometry;
- floating screenshots, phone frames, polaroid stickers, tape, clips, UI chrome, or fake gallery labels unless requested;
- generic beige scrapbook styling, heavy vintage grain, dust, scratches, glitter, or artificial paper noise;
- duplicated people, cloned products, altered faces, invented hands, or a new subject that was not in the source set;
- stretching, mirroring, or aggressively cropping the supplied images;
- fake words on page headers or a title baked into the artwork without user-supplied copy.

## Boundaries

- Do not proceed as if the images were supplied when they are missing.
- Do not silently change image order, reading direction, ratio, or the number of requested pages.
- Do not remove watermarks, signatures, private information, or copyright marks unless the user explicitly requests an allowed edit and the source ownership is clear.
- Do not expose private metadata or infer identities from the pictures.
- Do not use a still preview to represent a finished animation. If the user requests actual motion, state that the current output is a key visual and hand off to an appropriate video/motion workflow or create the motion only when that capability is available.
- Do not make a paid or external generation call without the user's approval when the workflow requires one.

## Review gate

Before returning the result, check:

1. The supplied images are recognizable and remain in the intended order.
2. The viewer can tell which page is turning within one second.
3. Perspective, page thickness, shadows, and lighting agree with one another.
4. At least one image remains legible at a small preview size.
5. No face, product, artwork, or important text was needlessly cropped or regenerated.
6. The scene is a flipbook showcase, not a generic collage or a fake animation frame.

If any check fails, revise the layout, page scale, or crop first. Stop after the focused correction pass and report any remaining limitation honestly.

## References

- `references/layout-archetypes.md` — choose and reset the page composition.

## Scripts

- `scripts/build_flipbook_showcase.py` — create a clean static flipbook preview while preserving supplied image pixels and aspect ratios.

## Delivery

Return the image with:

- status: `test` until the user approves it, or `accepted` after explicit confirmation;
- used Skill: `page-flip-showcase`;
- a one-sentence visual thesis naming the page-turn structure;
- a concise Chinese note about source-image fidelity and any limitation;
- the absolute delivery path only after acceptance.

For accepted visual finals in this workspace, archive them under:

`./accepted-outputs/08-page-flip-showcase/`

Never overwrite an existing final; append `-v2`, `-v3`, or a later version. Test images belong in a dated test folder and are not automatically accepted finals.

## Optional motion branch

When the user explicitly asks for a playable page-turn animation, first preserve this visual design as the key frame. Then create a separate motion plan with page-open, lift, bend, shadow travel, settle, and hold beats. Keep the still-image skill's source-protection rules, but do not promise a rendered GIF/video unless a video or motion tool actually produces it.
