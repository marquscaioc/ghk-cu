# Sistema Atmosférico — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Elevate GHK·CU landing page to dark-luxury / biohacking aesthetic through 7 atmospheric layers applied surgically on top of the existing HTML structure.

**Architecture:** All changes are confined to `index.html` (single-file). CSS additions go inside the `<style>` tag (~line 237). JS additions go inside the `<script>` tag (~line 2101). No new files, no new dependencies. Tasks are ordered from zero-risk CSS tweaks to complex JS canvas work so each task is independently testable before the next begins.

**Tech Stack:** Vanilla HTML/CSS/JS, HTML5 Canvas, IntersectionObserver, requestAnimationFrame, ResizeObserver. Zero external libraries.

## Global Constraints

- Single-file bundle: `C:\Users\Caio\Desktop\GHK CU GLOW\index.html` — never split into separate files
- Zero external JS/CSS dependencies
- All animated effects must be disabled when `prefers-reduced-motion: reduce` matches
- Particles and parallax disabled on `window.innerWidth < 768`
- Magnetic buttons disabled on touch devices (`'ontouchstart' in window`)
- CSS color token for copper: `rgba(201,148,100,…)` — use this exact value, never approximate
- Lighthouse mobile score must not drop below 85

---

### Task 1: Bloco 7 — Elevated Spacing

**Files:**
- Modify: `index.html:238-239` (section padding)
- Modify: `index.html:390` (hero title margin)
- Modify: `index.html:404` (hero sub margin)
- Modify: `index.html:529` (ingredients header margin)
- Modify: `index.html:599` (benefits header margin)
- Modify: `index.html:714` (how steps gap)
- Modify: `index.html:770` (testimonials header margin)
- Modify: `index.html:827` (faq header margin)
- Modify: `index.html:1423` (mobile section padding override)

**Interfaces:**
- Produces: wider breathing room consumed visually by all subsequent tasks

- [ ] **Step 1: Update `.section` and `.section--sm` padding**

At line 238–239, replace:
```css
.section { padding: 120px 0; }
.section--sm { padding: 80px 0; }
```
With:
```css
.section { padding: 160px 0; }
.section--sm { padding: 110px 0; }
```

- [ ] **Step 2: Update hero title and sub margins**

At line 390, change `margin-bottom: 28px;` → `margin-bottom: 40px;`
At line 404, change `margin-bottom: 48px;` → `margin-bottom: 60px;`

- [ ] **Step 3: Update section header margins**

Line 529 `.ingredients__header`: `margin-bottom: 80px` → `margin-bottom: 88px`
Line 599 `.benefits__header`: `margin-bottom: 80px` → `margin-bottom: 100px`
Line 770 `.testimonials__header`: `margin-bottom: 64px` → `margin-bottom: 80px`
Line 827 `.faq__header`: `margin-bottom: 64px` → `margin-bottom: 80px`

- [ ] **Step 4: Update `.how__steps` gap**

At line 714, change `gap: 40px` → `gap: 52px`

- [ ] **Step 5: Update mobile section padding override**

At line 1423 (inside the `@media (max-width: 640px)` block), change:
```css
.section { padding: 80px 0; }
```
To:
```css
.section { padding: 100px 0; }
```

- [ ] **Step 6: Visual check**

Open `index.html` in browser. Scroll through the full page. Each section should feel more spacious with clear air between them. No content should overlap. No horizontal scroll.

---

### Task 2: Bloco 2 — Cinematic Reveals

**Files:**
- Modify: `index.html:1021-1031` (`.reveal` CSS block)

**Interfaces:**
- Consumes: existing `.reveal` and `.reveal-delay-*` classes already applied to elements
- Produces: slower, more expensive-feeling entry animations for all revealed elements

- [ ] **Step 1: Update reveal transition**

At lines 1021–1026, replace the entire block:
```css
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.7s ease, transform 0.7s ease;
}
.reveal.visible { opacity: 1; transform: translateY(0); }
```
With:
```css
.reveal {
  opacity: 0;
  transform: translateY(40px) scale(1.04);
  transition: opacity 1.2s cubic-bezier(0.16,1,0.3,1), transform 1.2s cubic-bezier(0.16,1,0.3,1);
}
.reveal.visible { opacity: 1; transform: translateY(0) scale(1); }
```

- [ ] **Step 2: Update stagger delays**

At lines 1027–1031, replace:
```css
.reveal-delay-1 { transition-delay: 0.1s; }
.reveal-delay-2 { transition-delay: 0.2s; }
.reveal-delay-3 { transition-delay: 0.3s; }
.reveal-delay-4 { transition-delay: 0.4s; }
.reveal-delay-5 { transition-delay: 0.5s; }
```
With:
```css
.reveal-delay-1 { transition-delay: 0.15s; }
.reveal-delay-2 { transition-delay: 0.30s; }
.reveal-delay-3 { transition-delay: 0.45s; }
.reveal-delay-4 { transition-delay: 0.60s; }
.reveal-delay-5 { transition-delay: 0.75s; }
```

- [ ] **Step 3: Visual check**

Reload page. Scroll down slowly. Each `.reveal` element should glide up and expand from a very slight shrunk state. The motion should feel cinematic — slow start, smooth landing. Staggered children (e.g., benefits cards) should cascade with 150ms gaps between each card.

---

### Task 3: Bloco 3 — Section Light Sources

**Files:**
- Modify: `index.html` CSS — add `::before` light glows to `.ingredients`, `.benefits`, `.timeline` sections

**Interfaces:**
- Consumes: existing section layout; `.hero::before`, `.hero::after`, `.cta-section::before` already exist — do NOT touch them
- Produces: ambient copper radial glow anchored to each section's corner/center

- [ ] **Step 1: Add light sources CSS**

Find the comment `/* ── CTA SECTION ────` (line ~871) and insert the following block immediately before it:

```css
    /* ── SECTION LIGHT SOURCES ──────────────────────────────── */
    .ingredients { position: relative; }
    .ingredients::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 600px;
      height: 600px;
      background: radial-gradient(circle, rgba(201,148,100,0.08) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
    }
    .ingredients__grid { position: relative; z-index: 1; }
    .ingredients__header { position: relative; z-index: 1; }

    .benefits { position: relative; }
    .benefits::before {
      content: '';
      position: absolute;
      bottom: 0;
      left: -100px;
      width: 600px;
      height: 600px;
      background: radial-gradient(circle, rgba(201,148,100,0.07) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
    }
    .benefits__header { position: relative; z-index: 1; }
    .benefits__grid { position: relative; z-index: 1; }

    .timeline { position: relative; }
    .timeline::before {
      content: '';
      position: absolute;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 700px;
      height: 500px;
      background: radial-gradient(ellipse at top, rgba(201,148,100,0.07) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
    }
    .timeline__header { position: relative; z-index: 1; }
    .timeline__track { position: relative; z-index: 1; }
```

- [ ] **Step 2: Visual check**

Reload page. Scroll through ingredients, benefits, and timeline sections. Each should have a subtle warm copper glow emanating from its light source position. Glow must NOT interfere with text readability. No layout shifts.

---

### Task 4: Bloco 1 — Grain Texture Overlay

**Files:**
- Modify: `index.html` CSS — add `body::after` rule after existing `body` styles

**Interfaces:**
- Produces: 4% opacity SVG noise texture overlaid on entire page at fixed position

- [ ] **Step 1: Add grain CSS**

Find the comment `/* ── SCROLLBAR ─────` (or the line `html { scroll-behavior: smooth; }`) near the top of the `<style>` block (around line 206). Insert the following right after the `body { ... }` closing brace:

```css
    body::after {
      content: '';
      position: fixed;
      inset: 0;
      z-index: 9999;
      pointer-events: none;
      opacity: 0.04;
      mix-blend-mode: overlay;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
      background-repeat: repeat;
      background-size: 300px 300px;
    }
```

- [ ] **Step 2: Visual check**

Reload page. The background should feel textured, like film grain or expensive printed paper. Toggle `body::after { display: none }` in DevTools — the page should look slightly flatter without it. Text must remain fully legible. No impact on interaction.

- [ ] **Step 3: Verify z-index doesn't block interaction**

Click buttons, open FAQ items, tap mobile nav. Everything must remain fully interactive. If anything is blocked, add `pointer-events: none` is already set — verify it's present.

---

### Task 5: Bloco 6 — Magnetic CTA Buttons

**Files:**
- Modify: `index.html` JS `<script>` block — append magnetic button code before `</script>`

**Interfaces:**
- Consumes: `.btn-primary` elements
- Produces: cursor-following displacement on hover (desktop only)

- [ ] **Step 1: Add magnetic button JS**

Inside the `<script>` block at line 2101, append the following before the closing `</script>` tag (after the existing mousemove parallax code at line 2168):

```js
    // Magnetic buttons (desktop only)
    if (!('ontouchstart' in window) && window.matchMedia('(prefers-reduced-motion: no-preference)').matches) {
      const magneticBtns = document.querySelectorAll('.btn-primary');
      const RADIUS = 80;
      const MAX_DISPLACEMENT = 10;
      magneticBtns.forEach(btn => {
        btn.addEventListener('mousemove', e => {
          const rect = btn.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;
          const dx = e.clientX - cx;
          const dy = e.clientY - cy;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < RADIUS) {
            const ratio = (RADIUS - dist) / RADIUS;
            const tx = (dx / RADIUS) * MAX_DISPLACEMENT * ratio;
            const ty = (dy / RADIUS) * MAX_DISPLACEMENT * ratio;
            btn.style.transform = `translate(${tx}px, ${ty}px)`;
            btn.style.transition = 'transform 0.15s ease';
          }
        });
        btn.addEventListener('mouseleave', () => {
          btn.style.transform = 'translate(0, 0)';
          btn.style.transition = 'transform 0.4s ease';
        });
      });
    }
```

- [ ] **Step 2: Visual check**

Hover slowly over a `.btn-primary` button. The button should follow the cursor with a gentle 10px max displacement. Moving cursor away should smoothly return the button to center. On mobile (narrow viewport) the effect should not activate.

---

### Task 6: Bloco 4 — Hero Particle System

**Files:**
- Modify: `index.html` HTML — add `<canvas>` inside `.hero` (line ~1475)
- Modify: `index.html` CSS — add canvas positioning rule
- Modify: `index.html` JS — append particle system code

**Interfaces:**
- Consumes: `.hero` div as parent container
- Produces: 35 floating copper particles on a canvas behind hero content; canvas updates via rAF loop

- [ ] **Step 1: Add canvas element to hero HTML**

At line 1475, inside the `.hero` div but before `.hero__content`, insert:

```html
        <canvas id="heroParticles" aria-hidden="true"></canvas>
```

The hero block at line 1475 becomes:
```html
      <div class="hero">
        <canvas id="heroParticles" aria-hidden="true"></canvas>
        <div class="hero__content">
```

- [ ] **Step 2: Add canvas CSS**

Inside the `<style>` block, after `.hero::after { ... }` closing brace (around line 368), add:

```css
    #heroParticles {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 0;
    }
```

- [ ] **Step 3: Add particle system JS**

Append the following inside the `<script>` block before `</script>`:

```js
    // Hero particle system (desktop + reduced-motion check)
    (function() {
      const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (prefersReduced || window.innerWidth < 768) return;

      const canvas = document.getElementById('heroParticles');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const PARTICLE_COUNT = 35;
      let particles = [];
      let animId;

      function resize() {
        const hero = canvas.parentElement;
        canvas.width = hero.offsetWidth;
        canvas.height = hero.offsetHeight;
      }

      function randomParticle(forceY) {
        return {
          x: Math.random() * canvas.width,
          y: forceY !== undefined ? forceY : Math.random() * canvas.height,
          r: 1 + Math.random() * 2,
          alpha: 0.2 + Math.random() * 0.4,
          speedY: 0.2 + Math.random() * 0.3,
          phase: Math.random() * Math.PI * 2,
          freq: 0.003 + Math.random() * 0.004
        };
      }

      function initParticles() {
        particles = Array.from({ length: PARTICLE_COUNT }, () => randomParticle());
      }

      let frame = 0;
      function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        frame++;
        particles.forEach(p => {
          p.y -= p.speedY;
          p.x += Math.sin(p.phase + frame * p.freq) * 0.4;
          if (p.y < -p.r * 2) {
            const fresh = randomParticle(canvas.height + p.r);
            Object.assign(p, fresh);
          }
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(201,148,100,${p.alpha})`;
          ctx.fill();
        });
        animId = requestAnimationFrame(draw);
      }

      const ro = new ResizeObserver(() => { resize(); });
      ro.observe(canvas.parentElement);
      resize();
      initParticles();
      draw();

      // Stop animation when hero leaves viewport for performance
      const heroObs = new IntersectionObserver(([entry]) => {
        if (entry.isIntersecting) {
          if (!animId) { draw(); }
        } else {
          cancelAnimationFrame(animId);
          animId = null;
        }
      }, { threshold: 0 });
      heroObs.observe(canvas.parentElement);
    })();
```

- [ ] **Step 4: Visual check**

Reload desktop browser. Hero should display 35 small copper dots gently floating upward with slight sinusoidal drift. Particles should feel like specks of copper dust. They must appear behind the text and vial image. On mobile (< 768px), no particles should appear.

---

### Task 7: Bloco 5 — Hero Scroll Parallax

**Files:**
- Modify: `index.html` JS `<script>` block — replace existing mousemove handler + add scroll parallax

**Interfaces:**
- Consumes: `.hero__content` and `.hero__visual` DOM elements
- Produces: content scrolls at 0.25x speed, visual at 0.12x speed; combined with existing mousemove effect on visual

**Note:** The existing mousemove parallax at line 2160–2168 sets `hero.style.transform = translate(x, y)`. The scroll parallax would overwrite this. Solution: store mousemove values in JS variables and combine both in a single transform applied on each rAF frame.

- [ ] **Step 1: Replace existing mousemove parallax and add scroll parallax**

Find the block at lines 2160–2168:
```js
    // Smooth hero parallax on mousemove (subtle)
    const hero = document.querySelector('.hero__visual');
    if (hero) {
      document.addEventListener('mousemove', e => {
        const x = (e.clientX / window.innerWidth - 0.5) * 8;
        const y = (e.clientY / window.innerHeight - 0.5) * 8;
        hero.style.transform = `translate(${x}px, ${y}px)`;
      });
    }
```

Replace it with:
```js
    // Hero parallax: mousemove + scroll combined (desktop only)
    (function() {
      const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const heroVisual = document.querySelector('.hero__visual');
      const heroContent = document.querySelector('.hero__content');
      const heroSection = document.querySelector('.hero');
      if (!heroVisual || !heroContent || prefersReduced) return;

      let mouseX = 0, mouseY = 0, rafPending = false;

      function applyVisual() {
        if (window.innerWidth < 768) {
          heroVisual.style.transform = '';
          heroContent.style.transform = '';
          rafPending = false;
          return;
        }
        const scrollY = window.scrollY;
        const heroH = heroSection ? heroSection.offsetHeight : window.innerHeight;
        const scrollRatio = Math.min(scrollY / heroH, 1);
        const scrollOffsetVisual = scrollRatio * heroH * 0.12;
        const scrollOffsetContent = scrollRatio * heroH * 0.25;
        heroVisual.style.transform = `translate(${mouseX}px, ${mouseY + scrollOffsetVisual}px)`;
        heroContent.style.transform = `translateY(${scrollOffsetContent}px)`;
        rafPending = false;
      }

      function scheduleUpdate() {
        if (!rafPending) {
          rafPending = true;
          requestAnimationFrame(applyVisual);
        }
      }

      document.addEventListener('mousemove', e => {
        mouseX = (e.clientX / window.innerWidth - 0.5) * 8;
        mouseY = (e.clientY / window.innerHeight - 0.5) * 8;
        scheduleUpdate();
      });

      window.addEventListener('scroll', scheduleUpdate, { passive: true });

      // Reset when hero leaves viewport
      const heroObs = new IntersectionObserver(([entry]) => {
        if (!entry.isIntersecting) {
          heroVisual.style.transform = '';
          heroContent.style.transform = '';
        }
      }, { threshold: 0 });
      heroObs.observe(heroSection || heroVisual);
    })();
```

- [ ] **Step 2: Visual check**

Reload desktop. Hover cursor over hero — vial should shift subtly following the mouse (same as before). Scroll down slowly — text content should drift upward faster than the vial, creating a parallax depth effect. At mobile widths, no parallax should occur. Scroll back to top should reset positions.

---

## Self-Review

### Spec coverage check

| Spec block | Task | Status |
|---|---|---|
| Bloco 1 — Grain texture | Task 4 | Covered |
| Bloco 2 — Cinematic reveals | Task 2 | Covered |
| Bloco 3 — Light sources per section | Task 3 | Covered (hero/CTA already existed) |
| Bloco 4 — Canvas particles | Task 6 | Covered |
| Bloco 5 — Parallax scroll | Task 7 | Covered |
| Bloco 6 — Magnetic buttons | Task 5 | Covered |
| Bloco 7 — Elevated spacing | Task 1 | Covered |

### Potential conflicts identified

1. **Task 3 hero light sources:** Hero already has `::before` and `::after` — plan correctly avoids touching them.
2. **Task 7 mousemove conflict:** Plan explicitly replaces the old handler with a combined version — no double-assignment.
3. **Task 6 canvas z-index:** Canvas uses `z-index: 0`, hero content uses `z-index: 1` — particles correctly appear behind content.
4. **Task 4 grain z-index 9999:** `pointer-events: none` is set — verified in Step 3 of Task 4.
5. **Task 5 magnetic buttons:** `.btn-primary` in sticky buy bar also gets the effect — acceptable; the bar is fixed and the displacement won't cause layout issues.

### No placeholders found — all steps have concrete code.
