---
name: premium-frontend-ui
description: 'A comprehensive guide for GitHub Copilot to craft immersive, high-performance web experiences with advanced motion, typography, and architectural craftsmanship.'
---

# Immersive Frontend UI Craftsmanship

As an AI engineering assistant, your role when building premium frontend experiences goes beyond outputting functional HTML and CSS. You must architect **immersive digital environments**. This skill provides the blueprint for generating highly intentional, award-level web applications that prioritize aesthetic quality, deep interactivity, and flawless performance.

When a user requests a high-end landing page, an interactive portfolio, or a specialized component that requires top-tier visual polish, apply the following rigorous standards to every line of code you generate.

---

## 1. Establishing the Creative Foundation

Before generating layout code, ensure you understand the core emotional resonance the UI should deliver. Do not default to generic, unopinionated code. 

Commit to a strong visual identity in your CSS and component structure:
- **Editorial Brutalism**: High-contrast monochromatic palettes, oversized typography, sharp rectangular edges, and raw grid structures.
- **Organic Fluidity**: Soft gradients, deeply rounded corners, glassmorphism overlays, and bouncy spring-based physics.
- **Cyber / Technical**: Dark mode dominance, glowing neon accents, monospaced typography, and rapid, staggered reveal animations.
- **Cinematic Pacing**: Full-viewport imagery, slow cross-fades, profound use of negative space, and scroll-dependent storytelling.

---

## 2. Structural Requirements for Immersive UI

When scaffolding a page or generating core components, include the following architectural layers to transform a standard page into an experience.

### 2.1 The Entry Sequence (Preloading & Initialization)
A blank screen is unacceptable. The user's first interaction must set expectations.
- **Implementation**: Generate a lightweight preloader component that handles asset resolution (fonts, initial images, 3D models).
- **Animation**: Output code that transitions the preloader away fluidly—such as a split-door reveal, a scale-up zoom, or a staggered text sweep.

### 2.2 The Hero Architecture
The top fold must command attention immediately.
- **Visuals**: Output code that implements full-bleed containers (`100vh`/`100dvh`).
- **Typography Engine**: Ensure headlines are broken down syntactically (e.g., span wrapping by word or character) to allow for cascading entrance animations.
- **Depth**: Utilize subtle floating elements or background clipping paths to create a sense of scale and depth behind the primary copy.

### 2.3 Fluid & Contextual Navigation
- **Implementation**: Do not generate standard static navbars. Output sticky headers that react toscroll direction (hide on scroll down, reveal on scroll up).
- **Interactivity**: Include hover states that reveal rich content (e.g., mega-menus that display image previews of the hovered link).

---

## 3. The Motion Design System

Animation is not an afterthought; it is the connective tissue of a premium site. Always implement the following motion principles:

### 3.1 Scroll-Driven Narratives
Generate code utilizing modern scroll libraries (like GSAP's ScrollTrigger) to tie animations to user progress.
- **Pinned Containers**: Create sections that lock into the viewport while secondary content flows past or reveals itself.
- **Horizontal Journeys**: Translate vertical scroll data into horizontal movement for specific galleries or showcases.
- **Parallax Mapping**: Assign subtle, varying scroll-speeds to background elements, midground text, and foreground imagery.

### 3.2 High-Fidelity Micro-Interactions
The cursor is the user's avatar. Build interactions around it.
- **Magnetic Components**: Write logic that calculates the distance between the mouse pointer and a button, pulling the button towards the cursor dynamically.
- **Custom Tracking Elements**: Generate custom cursor components that follow the mouse with calculated interpolation (lerp) for a smooth drag effect.
- **Dimensional Hover States**: Use CSS Transforms (`scale`, `rotateX`, `translate3d`) to give interactive elements weight and tactile feedback.

---

## 4. Typography & Visual Texture

The aesthetics of your generated code must reflect premium craftsmanship.

- **Type Hierarchy**: Enforce massive contrast in scale. Headlines should utilize extreme sizing (`clamp()` functions spanning up to `12vw`), while body copy remains incredibly crisp (`16px-18px` minimum). 
- **Font Selection**: Always recommend or implement highly specified variable fonts or premium typefaces over system defaults.
- **Atmospheric Filters**: Implement CSS/SVG noise overlays (`mix-blend-mode: overlay`, opacity `0.02 - 0.05`) to remove digital sterility and add photographic grain.
- **Lighting & Glass**: Utilize `backdrop-filter: blur(x)` combined with ultra-thin, semi-transparent borders to create modern, frosted-glass depth.

---

## 5. The Performance Imperative

A beautiful site that stutters is a failure. Enforce strict performance guardrails in all generated code:

- **Hardware Acceleration**: Only animate properties that do not trigger layout recalculations: `transform` and `opacity`. Code that animates `width`, `height`, `top`, or `margin` should be fiercely avoided.
- **Render Optimization**: Apply `will-change: transform` intelligently on complex moving elements, but remove it post-animation to conserve memory.
- **Responsive Degradation**: Wrap custom cursor logic and heavy hover animations in `@media (hover: hover) and (pointer: fine)` to ensure pristine performance on touch devices.
- **Accessibility**: Wrap heavy continuous animations in `@media (prefers-reduced-motion: no-preference)`. Never sacrifice user accessibility for aesthetic flair.

---

## 6. Implementation Ecosystem

When the user asks you to implement these patterns, leverage industry-standard libraries tailored to their framework:

### For React / Next.js Targets
- Structure the application to support **Framer Motion** for layout transitions and spring physics.
- Recommend **Lenis** (`@studio-freight/lenis`) for smooth scrolling context.
- Implement **React Three Fiber** (`@react-three/fiber`) if webGL or 3D interactions are requested.

### For Vanilla / HTML / Astro Targets
- Rely heavily on **GSAP** (GreenSock Animation Platform) for timeline sequencing.
- Utilize vanilla **Lenis** via CDN for scroll hijacking and smoothing.
- Use **SplitType** for safe, accessible typography chunking.

---

## 7. Indicators of Premium Craftsmanship

Use these signals as acceptance criteria — a component is not "premium" until the relevant indicators hold.

### Visual & Structural Indicators

| Indicator | Target / Signal |
| --- | --- |
| Type contrast ratio (headline size / body size) | ≥ 4× scale difference |
| Layout whitespace rhythm | Consistent 8-pt baseline grid, no orphaned gaps |
| Cinematic viewport coverage | Hero ≥ `90vh` / `90dvh` with content above the fold |
| Motion presence | ≥ 1 staggered entrance + 1 contextual micro-interaction |
| Color depth | Foreground/background ΔE perceptible; AA contrast everywhere |
| Edge quality | No raw 0-radius rectangles unless brutalism is the chosen identity |

### Performance Indicators

| Indicator | Target |
| --- | --- |
| Animations triggering layout | 0 (only `transform`/`opacity`) |
| Main-thread long tasks on load | < 50ms p95 |
| `prefers-reduced-motion` branch | Implemented and reviewed |
| Touch-device degradation | No hover-only affordances; `hover: hover` gated |
| Image weight (hero, LCP) | AVIF/WebP, sized to viewport, ≤ 200KB on mobile |

### Accessibility Indicators (do not regress for aesthetics)

| Indicator | Target |
| --- | --- |
| WCAG 2.2 AA contrast | Minimum 4.5:1 body, 3:1 large text |
| Focus visibility | Visible focus ring on every interactive element |
| Keyboard reachability | All reveal-on-scroll content reachable via Tab |
| Motion auto-disable | `prefers-reduced-motion: reduce` disables parallax + magnetic cursors |

## 8. Guidelines & Rules

1. **Composition over configuration**: build from small primitives (frame, layer, reveal, magnetic) rather than one mega-component with dozens of props.
2. **Identity first**: commit to one creative direction (editorial brutalism, organic fluidity, cyber, cinematic) — mixing dilutes premium feel.
3. **No layout-thrash animations**: the moment you reach for `width`/`height`/`top`/`margin` transitions, stop and use `transform`.
4. **Progressive enhancement**: the page must read and navigate without JS; reveal animations and cursor effects layer on top.
5. **Tokenized aesthetics**: colors, spacing, radii, durations, and easings must live in CSS custom properties — never as raw literals in components.
6. **Reduced-motion parity**: the no-motion experience must still communicate the same content hierarchy.
7. **Performance budget before polish**: a frame that drops below 55fps is a regression regardless of beauty.
8. **Lighthouse-cI gate**: treat LCP > 2.5s, INP > 200ms, or CLS > 0.1 as a blocking defect.

## 9. Project Structure (recommended)

```
src/
├── styles/
│   ├── tokens.css          # color, space, type, motion tokens
│   ├── motion.css          # keyframes, easings, reveal utilities
│   └── base.css            # reset, fluid typography, print
├── components/
│   ├── primitives/         # Frame, Reveal, Magnetic, Parallax
│   ├── layout/             # Hero, Section, Marquee
│   └── ui/                 # buttons, nav, cards
└── motion/
    └── variants.ts         # shared Framer Motion variants
```

## Summary of Action

Whenever you receive a prompt to "Build a premium landing page," "Create an Awwwards-style component," or "Design an immersive UI," you must automatically:
1. Wrap the output in a robust, scroll-smoothed architecture.
2. Provide CSS that guarantees perfect performance using composited layers.
3. Integrate sweeping, staggered component entrances.
4. Elevate the typography using fluid scales.
5. Create an intentional, memorable aesthetic footprint.
6. Record the relevant indicators from §7 in your handoff so progress is measurable.
