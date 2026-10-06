# Skyline

A single interactive illustration. Open `index.html` in a browser — no build, no deps, no server
needed. Clicking certain windows in the artwork plays a short animation inside that window.

## Files

| File | What it is |
|---|---|
| `index.html` | Everything: markup, CSS animations, inline SVG overlay, ~15 lines of JS |
| `skyline.png` | The illustration. **1672 × 941**. Never edited — all animation is overlaid |
| `animation/dance.png` | Sprite sheet, 4070 × 976, 4 frames in one row (cell width **1017.5**) |

## The one rule that makes everything work

Every coordinate in the SVG is in **`skyline.png`'s native pixel space**. One full-size
`<svg viewBox="0 0 1672 941">` is stretched over the `<img>`, and `.stage` is locked to the
image's exact aspect ratio, so the two always occupy the identical box. That is why hotspots stay
glued to their windows at any viewport size — there is no JS repositioning and there must not be.

If you add anything, write its geometry in image pixels. Don't introduce percentages or
viewport units inside the SVG.

## Measured window geometry

Measured off the PNG, not eyeballed. The right building is drawn in perspective, so its windows
are tilted quads, not rectangles.

```
Right building, top window (cat)
  glass quad     1439,68  → 1576,41  → 1576,247 → 1439,268
  mullion band   y 165–176 (left edge) … 143–152 (right edge)
  sill line      (1439,268) → (1576,247)

Right building, middle window (blinds)
  glass quad     1439,377 → 1576,361 → 1576,562 → 1439,572
  mullion band   y 472–480 (left) … 459–468 (right)
  top edge tilt  -6.3°  ← blind slats are rotated to match

Left building, middle row, centre window (dancer)
  glass          x 187–233, y 656–750
  mullion        y 703–705   (upper pane 656–703, lower pane 706–750)
  painted plant  x 187–209, y 719–750
```

**How to measure a new window:** scan rows/columns of `skyline.png` for the luminance step
between the dark frame (`lum < 70`) and the lit glass. Do *not* read coordinates off a grid
overlay by eye — doing that put the right building's glass edge at x=1562 when it is actually
**1576**, and the blinds came out 14px short of the frame.

## Art-style constants (sampled from the illustration)

Flat vector shapes, no outlines, no gradients except where the original has them.

```
silhouettes (plant, lamp, cat, dancer)  #241a30 at opacity .68–.72
window glow                             #f5b16e bright · #dd8e61 mid
blind slat body                         #84545f      highlight line #eb9a68   pitch 10.4px
hover glow                              #ffc078 bloom (blur 7) · #ffd8a4 core
frame / mullion navy                    #1e192e
```

Anything new must look like it was always in the picture: soft silhouettes in the same key as the
plants and lamps, nothing with an outline, nothing that reads as clip art.

## Animation conventions

Each clickable window is a `<g class="win" data-dur="2800">` containing, in order:

1. `.glow-bloom` + `.glow-core` — hover lighting, painted on the **panes only** (two subpaths,
   skipping the mullion) so the frame stays dark
2. `.anim` — the animation, wrapped in a `clip-path` of the glass so it can't spill onto the frame
3. `.hit` — transparent click target, last so it's on top; `pointer-events: all`

JS adds `.playing` on click and removes it after `data-dur` ms. **`data-dur` must match the CSS
`animation-duration`** or the animation gets cut off or the window can't be re-clicked.

### Per-window notes

- **Blinds** — the window already has blinds painted in the upper sash. The overlay starts at
  `scaleY(.03)` (invisible), drops to cover, then retracts to `.03` and fades out, so the *painted*
  blinds are the rest state. Slats are one `<rect>` filled with a `<pattern>`, rotated -6.3° to
  match the painted top edge, overdrawn past the bottom and trimmed by the clip.
- **Dancer** — the sprite sheet's four poses are **not registered to each other**; hip centres sit
  at cell-x `559, 505, 492.5, 467.5`. Played raw he slides sideways across the window. The
  keyframes nudge each step (`-54, -1017.5, -2022.5, -3015`) to land every pose on the same hips.
  Stepping is `step-end` at 200ms (5fps). He's clipped to both panes *minus* the mid-rail, so the
  sash cuts his raised arm and the sill hides his waist — that's what puts him behind the glass.
- **Cat** — hand-drawn paths. Jump arc is translate + squash with `transform-box: fill-box`.

## Verifying changes

Serve the folder (`python3 -m http.server`) and drive it in Chrome. Live playback is unreliable to
screenshot — a background tab throttles rAF and the animation jumps to finished. Freeze a frame
instead:

```js
document.querySelectorAll('.win').forEach(w => w.classList.add('playing'));
document.getAnimations().forEach(a => { a.pause(); a.currentTime = 820; });
```

Then screenshot. Stepping `currentTime` through the timeline is the only dependable way to check
pose, placement and clipping.

Placement of new artwork is fastest to iterate *outside* the browser: composite the shape over
`skyline.png` in Python/PIL at the intended scale and offset, crop the window, upscale 6–8×, and
look at it. Several size candidates per run beats one round trip through Chrome each time.

## Gotcha

Keep this project out of `~/Desktop`. macOS TCC protects that folder, and when the grant lapses
every shell and file tool here starts returning `EPERM: operation not permitted` for every path,
including reads. It was moved to `~/skyline` for exactly this reason.
