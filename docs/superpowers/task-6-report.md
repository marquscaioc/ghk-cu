# Task 6 Report — Bloco 4: Hero Particle System

## Status: DONE

## Commit Hash
`e5cc7b407b15f91e4a2bc49a38a084faa90a7894`

## Changes Applied

### Change 1 — HTML (line 1546)
Inserted `<canvas id="heroParticles" aria-hidden="true"></canvas>` as the first child of `.hero`, before `.hero__content`.

### Change 2 — CSS (after line 382)
Added `#heroParticles` rule with `position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0;` immediately after the `.hero::after` closing brace.

### Change 3 — JS (before closing `</script>`)
Appended the self-invoking particle system function that:
- Skips on `prefers-reduced-motion: reduce` or viewport width < 768px
- Renders 35 copper-toned (`rgba(201,148,100,…)`) floating particles on the canvas
- Uses `ResizeObserver` to keep canvas dimensions in sync with the hero element
- Uses `IntersectionObserver` to pause `requestAnimationFrame` when the hero is off-screen (performance)
- Particles drift upward with sinusoidal horizontal sway and respawn at the bottom when they exit the top
