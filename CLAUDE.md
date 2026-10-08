# Skyline

A single interactive illustration. Open `index.html` in a browser — no build, no deps, no server
needed. Clicking certain windows in the artwork plays a short animation inside that window.

## Files

| File | What it is |
|---|---|
| `index.html` | Everything: markup, CSS animations, inline SVG overlay, ~15 lines of JS |
| `skyline.png` | The illustration. **1672 × 941**. Never edited — all animation is overlaid |
| `animation/dance.png` | Sprite sheet, 4070 × 976, 4 frames in one row (cell width **1017.5**) |
| `animation/plantgrowth.png` | Raw generated plant-growth sheet, 6 frames, unevenly spaced. Source only |
| `animation/plant.png` | Built from it by `animation/build_plant_sheet.py`: 1680 × 419, 6 cells of **280**, every pot centred at cell (140, 414), recoloured to the painted plants' tones |
| `animation/curtainclose.png` | Raw generated curtain sheet, 5 frames, uneven widths. Source only |
| `animation/curtain.png` | Built by `animation/build_curtain_sheet.py`: 1800 × 396, 5 cells of **360**, each cropped to its rod (rod top y 6, hem y 392), red keying specks removed |

## The one rule that makes everything work

Every coordinate in the SVG is in **`skyline.png`'s native pixel space**. One full-size
`<svg viewBox="0 0 1672 941">` is stretched over the `<img>`, and `.stage` is locked to the
image's exact aspect ratio, so the two always occupy the identical box. That is why hotspots stay
glued to their windows at any viewport size — there is no JS repositioning and there must not be.

If you add anything, write its geometry in image pixels. Don't introduce percentages or
viewport units inside the SVG.

## Layout: every interactive window is always on screen (except phones)

All hotspots lie inside the **safe box x 173–1592, y 24–930** (centre 882.5, 477). `.stage` is
sized and placed in pure CSS: `--k` (screen px per image px) covers the viewport unless that would
crop the safe box, in which case it shrinks just enough to fit it; `left`/`top` centre the safe
box, clamped so the picture never leaves an edge it can still cover. Leftover strips show
`body::before`, a blurred copy of `skyline.png` stretched to the viewport, and the stage's edges
are feathered (30 image px) into it. Phones (`max-width: 767px`) keep plain centred cover and may
crop windows — deliberately.

**Adding a window outside the safe box?** Widen the box: update 1419/906 (its size) and
882.5/477 (its centre) in `.stage`, and this note. Check with a script that tests every `.hit`'s
`getBoundingClientRect()` against the viewport at several window sizes.

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

Right building, bottom window (plant)
  glass quad     1440,677 → 1576,671 → 1576,818 → 1440,820   (single pane)
  painted plant  leaves x 1503–1534 y 782–804 · pot x 1507–1529 y 805–820, centre 1518

Left building, top row, right window (plant)
  glass          x 299–349 · upper pane y 487–534 · lower pane y 538–583
  painted plant  x 300–321, y 561–583, pot mostly hidden behind the sill

Back-right building, wide-column lit windows (curtains)
  3rd row        glass x 1165–1189, y 751–786, mid-rail y 768–769
  5th row        glass x 1165–1189, y 879–914, mid-rail y 896–897

Back-right building, narrow lit windows (blinds)
  A  right column, 2nd row   glass x 1234–1247 · panes y 688–704, 707–723
  B  3rd column, 3rd row     glass x 1068–1082 · panes y 752–767, 770–786 (blinds painted at top)
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
3. `.dot` — hint in the glass's top-right corner marking the window as clickable: a `<g>` of
   `.dot-halo` (r ≈ 2.6× core, ripples out and fades on a 2.6s loop) + `.dot-core` (breathes).
   Blur is in bounding-box units so it scales with `r`. The `<g>` fades out while `.playing`
4. `.hit` — transparent click target, last so it's on top; `pointer-events: all`

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
- **Plants** — `plant.png` sprite, `step-end` through 1→6, sway 5↔6, back to 1 over 3.2s. The
  pot is pre-registered in every cell, so no per-frame nudges (unlike the dancer). Placement is
  `translate(anchor − (140, 414)·s) scale(s)`: bottom window anchor (1518, 820) s .168, top-left
  window anchor (308, 591) s .125. Frame 1 is recoloured opaque to the colour the painted plant
  shows through the glass (≈ `#241a30` at .58 over the lit wall), so it covers the painted plant
  rather than doubling it.
  While playing, `plant-patch-rb.png` / `plant-patch-lt.png` (also made by the build script: the
  window background with the painted plant filled in from its surroundings) sit under the sprite,
  so the painted plant never shows behind the growing one. At rest the artwork is untouched.
- **Curtains** — `curtain.png` sprite on both back-right windows: open → closed → peek → closed →
  open over 3.2s, `step-end`. Cell 0..360 is stretched to x 1163–1191 (just past the glass so the
  edges tuck behind the frame), rod at the glass top, hem at the sill: `scale(.0778 .0959)`.
  Open curtains aren't in the painting, so `.curtain-fade` fades the sprite in and out at the ends.
  The fabric colour was left as generated; it already matches the painted curtains (~#a97376).
- **Back-building blinds** — windows A and B reuse `.blind` / `blindsShut` (data-dur 2600) with
  `#slatsSmall`, the same three slat colours at pitch 2.2 to suit the distant building. No
  rotation: that building is drawn flat-on, not in perspective.
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
