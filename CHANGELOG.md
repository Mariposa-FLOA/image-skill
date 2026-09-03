# Changelog

## Unreleased

- Added `glitchy-glam-editorial-visual`, a trend-aware image Skill for fashion, beauty, product, and social visuals built around one controlled beauty fracture instead of generic full-frame glitch effects.
- Added `poster-layered-psd-export`, a local PSD writer and structural validator for poster projects with aligned RGBA layers, Unicode layer names, opacity, blend modes, merged preview, and an editability manifest.
- Added truthful raster-text and flattened-input boundaries so poster Skills do not claim semantic layers or live Photoshop text that were never created.
- Standardized the Photoshop layer-planning handoff across the poster-oriented Skills so PSD output is considered before rendering, not retrofitted from a flattened image.
- Added a portable poster-editing package builder that bundles the PSD, aligned layer PNGs, merged preview, normalized manifest, and editing notes in one handoff directory.
- Added a visual direction selector, hierarchy ratios, and local source-signal analyzer so FLOA Mariposa visuals can choose a governing composition before colour, type, and material treatment.
- Upgraded the remaining specialist visual Skills with mechanism-specific hierarchy checks for key art, screenprint, impossible space, contour, relief, mineral, collage, optics, symbolism, offset, Y2K, album covers, and page-flip presentation.
- Added `floa-mariposa-visual-system`, a brand-specific Neo-Editorial visual system for the maintainer's product FLOA Mariposa, with reusable references, copy rules, series guidance, and cross-agent chat delivery.
- Added one maintainer-authorized public example image for `floa-mariposa-visual-system`; the remaining source poster set stays outside the repository.
- Upgraded `page-flip-showcase` from a static page-turn treatment to three explicit output modes: static showcase, clickable one-page-at-a-time viewer, and locally rendered MP4 page-flip animation.
- Added detailed Chinese usage documentation covering input/output contracts, adaptive poster-derived collage backgrounds, source-image protection, identity labels, file structure, and verification.
- Added adaptive background guidance: analyse each poster's palette, composition, typography, material, and motif before choosing collage layers; keep linework subordinate when collage is stronger.
- Refreshed the chat-ready export for `page-flip-showcase`.
- Added cross-agent delivery instructions covering one-file upload, full-folder import, host capability checks, and a minimal self-test for Codex, WorkBuddy, and other agents.
- Published the current 1080 × 1440 MP4 page-flip demonstration under `examples/page-flip-showcase.mp4`.

## v1.0.4 — 2026-09-01

- Made canvas ratio inference the default across the visual Skills: inspect the source before choosing a format, and honor a ratio only when the user supplies one.
- Regenerated all 14 chat-drop files from the updated canonical Skills.

## v1.0.3 — 2026-08-31

- Added a single-file chat-drop export for every installable Skill under chat-ready/.
- Added direct chat instructions for Codex, Doubao, Image 2, and other image models.
- Added a deterministic scripts/build_chat_drop.py exporter so chat files stay synchronized with skills/.
- Updated public repository and release links after the account rename to Mariposa-FLOA.

## v1.0.2 — 2026-08-31

- Preserved seven supplied Skill outputs byte-for-byte with maintainer-confirmed assignments: six primary images and one Y2K variant.
- Displayed all 14 Skill primary examples inline, plus the separate URBAN SIGNAL variant.
- Retained the other eight existing project examples.
- Removed the community placeholder, redundant README notices, and retired historical gallery image from the current release.
- Added Codex as an AI collaborator while retaining AIGC-泷 as author and maintainer.
- Kept the beginner guides and existing license terms.

## v1.0.1 — 2026-08-31

- Replaced the README hero gallery with six selected original Skill examples.
- Kept the prior approved-example archive image available but no longer used as the README hero.
- Retained the same license, provenance, and external-Skill exclusion boundary.
- Added the author and public-sharing attribution: `AIGC-泷` / `Image Skill by @AIGC-泷`.
- Renamed the public project branding from `Our Original Visual Skills` to `Image skill`.

## v1.0.0 — 2026-08-31

- Published the first complete set of 14 original Skill directories.
- Added a named example image for every installable Skill (15 images including the historical retired visual example).
- Added beginner usage guides for Codex, WorkBuddy / Workbuddy, and other custom-Skill agents.
- Excluded external starter Skills, distilled adaptations, raw source media, and the explicitly excluded `level-17-show-time.png`.

## v1.0.0-rc2 — 2026-08-31

- Added project-generated non-person examples for the remaining original Skills.
- The release candidate now contains 14 installable original Skill directories, including `page-flip-showcase`.
- Added the static `page-flip-showcase` Skill and its deterministic demonstration image.
- Replaced the provisional Y2K example with a new composition generated from the two maintainer-supplied references.

## v1.0.0-rc1 — 2026-08-31

- Prepared the first public-release candidate for the project's original visual Skills.
- Included 13 original Skill directories with their `SKILL.md`, UI metadata, references, scripts, and assets.
- Added bilingual README, licensing split, attribution boundary, example-image terms, and provenance notes.
- Included only the four example images explicitly approved by the maintainer; excluded all unmarked images and raw source portraits.
- Withheld `page-flip-showcase` because it was newly created and not yet publicly tested.
