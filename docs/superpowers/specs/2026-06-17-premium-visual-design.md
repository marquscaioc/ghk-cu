# GHK·CU — Premium Visual Elevation: Sistema Atmosférico

**Data:** 2026-06-17  
**Abordagem escolhida:** Cirúrgica — mesma estrutura HTML, elevação visual por camadas  
**Estética alvo:** Dark luxury / Biohacking (La Mer meets Biohacking Lab)

---

## Contexto

O site GHK·CU existe como single-page HTML/CSS/JS em `index.html`. A estrutura de seções e conteúdo está validada. O objetivo desta spec é elevar o visual para nível premium sem alterar layout ou conteúdo — apenas aprimorando atmosfera, espaçamento e interatividade.

---

## Bloco 1 — Grain Texture

**O quê:** Pseudo-elemento `body::after` fixo, cobrindo 100vw × 100vh, com SVG noise filter gerado via `<feTurbulence>`.

**Especificação:**
- `position: fixed; inset: 0; z-index: 9999; pointer-events: none`
- Opacidade: `0.04` (4%) — invisível ao olhar direto, sentido como profundidade
- `mix-blend-mode: overlay`
- SVG inline como `background-image: url("data:image/svg+xml,...")`
- Parâmetros do noise: `baseFrequency="0.65"`, `numOctaves="3"`, `type="fractalNoise"`

**Critério de sucesso:** Ao alternar `display: none` no DevTools, o fundo perde textura perceptível — mas com ele ativo, nenhum texto fica ilegível.

---

## Bloco 2 — Reveal Cinematográfico

**O quê:** Upgrade das animações `.reveal` existentes para transições mais lentas e elegantes.

**Especificação:**
- Duração: `0.7s` → `1.2s`
- Easing: `cubic-bezier(0.16, 1, 0.3, 1)` (desaceleração exponencial — "expensive feel")
- Transform inicial: `translateY(40px) scale(1.04)` → `translateY(0) scale(1.00)`
- Stagger entre `.reveal-delay-*`: aumentar de `0.1s` por step para `0.15s`
- Opacidade: mantém `0 → 1`, sem alteração

**Critério de sucesso:** Cada seção revela seus filhos como uma cortina abrindo, não como elementos piscando na tela.

---

## Bloco 3 — Fontes de Luz por Seção

**O quê:** Cada seção principal recebe um radial-gradient posicionado como fonte de luz ambiente.

**Mapeamento:**
| Seção | Posição do glow | Cor | Opacidade |
|---|---|---|---|
| Hero | top-right | `rgba(201,148,100,0.10)` | — |
| Ingredientes | center (emana do frasco) | `rgba(201,148,100,0.08)` | — |
| Benefits | bottom-left | `rgba(201,148,100,0.07)` | — |
| Timeline | top-center | `rgba(201,148,100,0.07)` | — |
| CTA | center radial full | `rgba(201,148,100,0.09)` | — |

**Implementação:** `::before` pseudo-elemento em cada seção, `position: absolute; pointer-events: none; z-index: 0`. Conteúdo interno recebe `position: relative; z-index: 1` onde necessário.

**Critério de sucesso:** A página parece iluminada por uma fonte real, não uniformemente escura.

---

## Bloco 4 — Partículas Flutuantes no Hero

**O quê:** `<canvas>` posicionado atrás do conteúdo do hero com partículas cobre flutuando.

**Especificação:**
- 35 partículas, tamanho 1–3px, cor `rgba(201,148,100, 0.2–0.6)`
- Movimento: drift vertical para cima (~0.3px/frame) + drift lateral senoidal suave
- Loop: quando partícula sai pelo topo, reaparece no fundo com x aleatório
- Performance: `requestAnimationFrame`, canvas redimensiona com `ResizeObserver`
- **Desativado em:** `prefers-reduced-motion: reduce` + `window.innerWidth < 768`
- `position: absolute; inset: 0; z-index: 0; pointer-events: none`

**Critério de sucesso:** Em desktop, o hero parece "respirar". Em mobile ou com reduced motion, zero impacto.

---

## Bloco 5 — Parallax no Scroll do Hero

**O quê:** Conteúdo do hero e frasco se movem a velocidades diferentes ao rolar.

**Especificação:**
- `.hero__content`: `transform: translateY(scrollY * 0.25)`
- `.hero__visual`: `transform: translateY(scrollY * 0.12)`
- Listener em `scroll` com `requestAnimationFrame` throttle para não travar
- Desativado em `prefers-reduced-motion` e `window.innerWidth < 768`
- Resetar transforms quando hero sai do viewport (performance)

**Critério de sucesso:** Rolar os primeiros 200px cria separação visual perceptível entre texto e frasco — sensação de profundidade Z sem biblioteca externa.

---

## Bloco 6 — Botões Magnéticos

**O quê:** Botões `.btn-primary` seguem o cursor levemente no hover.

**Especificação:**
- Raio de influência: `80px` do centro do botão
- Deslocamento máximo: `10px` em X e Y
- Cálculo: `(cursorPos - btnCenter) / radius * maxDisplacement`
- Aplicado como `transform: translate(dx, dy)` com `transition: transform 0.15s ease`
- No `mouseleave`: suavemente retorna ao centro (`transform: translate(0, 0)`)
- Desativado em touch devices (`'ontouchstart' in window`)

**Critério de sucesso:** Hover no botão primário parece responsivo e vivo sem ser distrativo.

---

## Bloco 7 — Espaçamento Elevado

**O quê:** Aumento sistemático de padding e margens para criar grandiosidade.

**Especificação:**
| Token | Antes | Depois |
|---|---|---|
| `.section` padding | `120px 0` | `160px 0` |
| `.section--sm` padding | `80px 0` | `110px 0` |
| `.benefits__header` margin-bottom | `80px` | `100px` |
| `.ingredients__header` margin-bottom | `64px` | `88px` |
| `.testimonials__header` margin-bottom | `64px` | `80px` |
| `.faq__header` margin-bottom | `64px` | `80px` |
| `.how__steps` gap | `40px` | `52px` |
| `.hero__title` margin-bottom | `28px` | `40px` |
| `.hero__sub` margin-bottom | `48px` | `60px` |

**Mobile (max-width: 640px):** `.section` fica em `100px 0` em vez de `80px 0`.

**Critério de sucesso:** Cada seção tem respiro suficiente para que o conteúdo "flutue" — não pareça comprimido.

---

## Ordem de Implementação

1. Bloco 7 (espaçamento) — impacto imediato, zero risco
2. Bloco 2 (reveals) — melhora perceptível em toda a página
3. Bloco 3 (fontes de luz) — atmosfera por CSS puro
4. Bloco 1 (grain) — camada final de textura
5. Bloco 6 (botões magnéticos) — JS leve, isolado
6. Bloco 4 (partículas) — canvas, mais complexo
7. Bloco 5 (parallax) — scroll JS, testar performance

---

## Restrições

- Zero dependências externas (sem GSAP, Three.js, etc.) — tudo em CSS/JS vanilla
- Bundle final deve permanecer single-file `index.html`
- Performance: Lighthouse score mobile não deve cair abaixo de 85
- Acessibilidade: todos os efeitos respeitam `prefers-reduced-motion`
