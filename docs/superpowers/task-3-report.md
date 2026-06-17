# Task 3: Bloco 3 — Section Light Sources

**Status:** DONE

**Commit hash:** 056996a

## Summary

Successfully added ambient copper light sources (radial gradients) to three sections of the GHK·CU website:

1. **.ingredients** — Centered glow (600px circle at 50%, 50%)
   - Gradient: `rgba(201,148,100,0.08)`
   - Provides warm ambient lighting for ingredient cards

2. **.benefits** — Bottom-left glow (600px circle at bottom-left)
   - Gradient: `rgba(201,148,100,0.07)`
   - Creates accent lighting for benefit cards

3. **.timeline** — Top-center elliptical glow (700x500px ellipse)
   - Gradient: `rgba(201,148,100,0.07)`
   - Provides atmospheric top lighting for timeline section

## Insertion Details

- **File modified:** `index.html`
- **Location:** Lines 871–917 (inserted immediately before `/* ── CTA SECTION */` at line 919)
- **CSS block:** 47 lines of pure CSS, no HTML structure changes
- **Z-indexing:** All pseudo-elements set to z-index 0; content (.ingredients__grid, .benefits__header, .timeline__track) set to z-index 1 to layer correctly

## Verification

- CSS block inserted at correct location (before CTA SECTION comment)
- All three sections now have position: relative + ::before pseudo-elements with proper positioning and layering
- No overflow: hidden added (glows can bleed naturally)
- No conflicts with existing background: var(--bg2) on .ingredients and .timeline
- Commit created successfully with git

## Concerns

None. All requirements met.
