# How to use these Skills

This is the beginner-facing entry point. Different agent products may use different menu labels, but the shared model is simple: load a Skill directory containing `SKILL.md`, then ask the agent for a task in natural language.

## Write a clear request

Include four things:

1. **Goal** — what should be made.
2. **Platform and ratio (optional)** — specify `Xiaohongshu 3:4` or `Douyin 9:16` only when there is a real publishing target; otherwise let the AI inspect the source composition and choose the best canvas.
3. **Keep / avoid rules** — identity, product text, source relationships, and exclusions.
4. **Delivery state** — `test` first, or `accepted` after approval.

```text
Use <skill-name>.
Goal: <what I want made>.
Platform / ratio (optional): <platform + native ratio; if omitted, infer it from the source>.
Keep: <identity, object, text, or relationship>.
Avoid: <unwanted elements>.
Return a test image first; do not archive automatically.
```

## Codex

```bash
git clone https://github.com/Mariposa-FLOA/image-skill.git
mkdir -p ~/.codex/skills
cp -R image-skill/skills/graphic-composition-poster ~/.codex/skills/
```

Copy the complete Skill directory, including any `references/`, `scripts/`, or `assets/`. Restart Codex, then invoke it by its exact name:

```text
Use $graphic-composition-poster to make a native 3:4 Xiaohongshu poster from this photo.
Keep the subject recognizable and return a test image first.
```

## WorkBuddy / Workbuddy and other agents

WorkBuddy menus vary by client version and enterprise configuration. Use the product's **Skills / custom capability / agent instructions** area and choose one of these compatible paths:

1. **Import a folder or upload a package:** select `skills/<skill-name>/`, keeping `SKILL.md` and all companion files.
2. **Paste Markdown:** paste the complete `SKILL.md`; upload companion references or scripts if the host supports attachments.
3. **Import from Git URL:** if the host supports it, use `https://github.com/Mariposa-FLOA/image-skill` and confirm that it discovered the child directories under `skills/`.

Then call it by name:

```text
Use graphic-composition-poster for a native 9:16 Douyin image.
Build the wordless composition first, preserve my supplied text exactly, and return a test.
```

If the host accepts only Markdown, missing companion files may make some references or scripts unavailable. Do not treat a pasted excerpt as a complete installation.

### Image 2 and other image models

These Skills are model-agnostic Markdown workflows; they do not lock you to one image provider. Load a Skill in Codex, Doubao, WorkBuddy, or another agent, then have that agent call Image 2, Seedream, or another image-generation model (for example, “Use this Skill and ask Image 2 to generate the image”). If a model uses different controls, adapt only the invocation format and keep the Skill's composition, subject-protection, and negative constraints intact.

For a one-off chat, download one .md file from chat-ready/, upload it with any reference image, and say “Treat the attachment as the visual task specification and follow it directly.” See docs/CHAT-DROP.md for the Doubao example and the full handoff sentence.

## Choosing a Skill

Use `floa-mariposa-visual-system` for brand-specific FLOA Mariposa posters, campaign series, product visuals, and Neo-Editorial visual direction.

Use `poster-layered-psd-export` when a poster must continue into Photoshop as a verified layered PSD; pair it with the upstream poster Skill that creates the actual layer assets.

Use `cinematic-key-art-poster` for film narrative key art, `graphic-composition-poster` for crop/grid/type composition, `impossible-space-editorial-poster` for spatial contradiction, `music-album-cover-art` for record identity and layered masters, `optical-refraction-visual` for believable transparent media, `symbolic-narrative-poster` for one visual metaphor, and `y2k-street-cutout-poster` for Y2K street collage. Use the matching Skill for screenprint, contour, paper relief, mineral relief, mixed media, offset print, or page-turn presentation.

Choose one governing Skill per image. State a platform ratio only when needed; otherwise let the Skill infer a source-preserving canvas. Do not ask conflicting Skills to take over at once.

## Images, type, and delivery

- Label uploaded images as binding source, reference, or inspiration.
- Protect product, packaging, screenshot, and supplied type exactly when required.
- For dense copy, solve the wordless visual first and add live type locally or in SVG.
- Write the platform and native ratio when you have a publishing target; otherwise leave the ratio open for source-aware inference.
- Treat `test` as a review draft. Only explicit approval should move work to `accepted` archival output.

## Boundary

This repository publishes only our original Skills. External starter Skills, distilled adaptations, private input files, and unapproved example images are excluded. Inspect the source and license of any third-party Skill before installing or executing it.
