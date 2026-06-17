# Task 7 Report — Bloco 5: Hero Scroll Parallax

## Status: DONE

## Commit Hash
`2f14656`

## Summary

- **Old code removed:** The single-target `mousemove`-only block (`const hero = document.querySelector('.hero__visual')...`) at lines 2231–2239 has been fully removed.
- **New IIFE in place:** Replaced with the combined mousemove + scroll parallax IIFE starting at line 2231, ending at line 2281 (before the magnetic buttons block).
- **New targets:** `.hero__visual` (image column) and `.hero__content` (text column) are both animated.
- **Guards active:** `prefers-reduced-motion` check and mobile breakpoint guard (`window.innerWidth < 768`) are both present inside the IIFE.
- **rAF throttle:** A single `scheduleUpdate()` / `requestAnimationFrame` path handles both `mousemove` and `scroll` events.
- **Viewport reset:** `IntersectionObserver` clears transforms when the hero section leaves the viewport.
