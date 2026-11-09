# Visual rules: readability first

The video is often watched on a phone, on a train, or at 1.5× speed. What isn't readable there doesn't exist. These rules are hard – beauty comes second.

## Stage & safe area

- Fixed stage **1920 × 1080 px**, scaled to the screen with CSS `transform: scale()`. Never lay out with `vw`/`vh` or media queries – otherwise every screen size looks different and the layout check means nothing.
- **Safe area:** 96 px left/right, 64 px top/bottom. All text and every content image lies fully inside it. Only background/decoration may extend beyond.
- Progress bar and source note sit at the bottom inside the safe area and never overlap content (reserved strip ~56 px; content ends at y = 960).

## Typography

| Element | Minimum | Recommended |
|---|---|---|
| Scene heading | 60 px | 64–80 px |
| Body text / bullets | 34 px | 38–44 px |
| Labels in graphics | 28 px | 30–34 px |
| Source note "Slide 12–14" | 22 px | 24 px |

- Line height 1.25–1.4. At most ~45 characters per line for body text, max 6 lines of text per scene, max ~40 on-screen words per scene.
- Sans-serif, highly legible font with fallbacks (e.g. `Inter, "Segoe UI", Roboto, Arial, sans-serif`). No thin weights (< 400) for content.
- **Never auto-shrink** (no fit-text below the minimum). If it doesn't fit → cut content or split the scene.
- Set `<html lang="…">` to the video language (important for hyphenation) and translate all fixed on-screen labels via `data-hold-label`, `data-think-label`, `data-slide-word` (e.g. "take a look", "Think about it …", "Slide").
- Long German compound words ("Bestellanforderungsfreigabe"): `hyphens: auto` with `lang="de"` keeps them from running off the edge; still verify with the check.

## Look (chosen in Phase 1, step 3)

Set on `<html>`: `data-mode="light|dark"` and `data-style="simple|modern|slides|topic"`. All colors are CSS tokens (`--bg`, `--surface`, `--ink`, `--muted`, `--accent`, `--accent2`, `--accent-soft`, `--glow`, `--glow2`, …); scenes never hard-code colors.

| Style | What it looks like | What you do |
|---|---|---|
| **modern** (default) | soft color glows in the background, gradient accent bar under headings, cards with shadow and colored top edge, gradient bullet dots, chapter title cards with a large gradient number | nothing beyond using the layouts |
| **simple** | flat background, one accent color, no shadows or gradients | nothing |
| **slides** | like modern, but with the slides' colors and a thin brand stripe at the top | run `scripts/palette.py <pdf> --mode <mode>`, paste the CSS variables into `:root` (light) or the dark block |
| **topic** | like modern, with an accent pair and one decorative motif that fit the subject | choose the colors and the motif (below) |

Dark mode switches every token (background, cards, text, accents, table headers); check snapshots in the chosen mode, not just in light.

**Topic looks:** pick two accent colors that match the subject (databases: blue/teal; sustainability: green/lime; finance: navy/gold; marketing: magenta/orange; law: burgundy/slate; IT security: dark blue/cyan) and one abstract background motif as inline SVG in `<div class="motif" data-deko>` per scene or on chapter cards: a grid, network nodes, chart lines, leaves, waves, circuit lines. The motif is pure decoration: opacity ≤ 0.07 (class `.motif`), behind the content, never icons or symbols that could be read as information, never logos.

**Contrast:** text contrast at least 4.5:1, headings ≥ 60 px at least 3:1 (WCAG). The layout check measures it against the first opaque background behind each text and reports violations – fix by using `--ink`/`--muted`, not by lightening the background. No text directly on busy images; if necessary, put text on a solid surface.

**Color use:** base colors + `--accent` for "what is being talked about right now", `--accent2` for secondary emphasis/gradients, `--warn` for "attention/exam-relevant", `--ok` for results/answers. Never use color as the only distinguishing feature. Use the same colors/icons for the same concepts throughout the video (helps recognition in the summary).

## Visual richness

- Every content scene shows structure, not just text: diagram, process chain, comparison columns, card grid, table, code, formula or slide crop. Heading + bullets only for at most one in four scenes.
- Chapter starts get a title card (`.chapter-card`: big chapter number + title, 2–4 s) – it gives rhythm and makes chapters visible when skimming.
- Reveal step by step in sync with the narration; highlight the current element (`data-focus`).
- Simple icons are welcome when they help recognition (inline SVG, monochrome in `--accent`), e.g. a database cylinder next to "Datenbank" – one icon style for the whole video.

## Layout types (provided by the scene file)

- `title` – intro: large title, subtitle, optional agenda.
- `chapter-card` – chapter start: big chapter number + title (`.chapter-card`).
- `outline` – table of contents after the intro (see below).
- `bullets` – 3–5 points revealed in sync with the narration.
- `two-column` – comparison A vs. B, term + explanation.
- `process` – process as a chain (max 5–6 steps per row, otherwise two rows or split).
- `graphic` – self-built SVG diagram.
- `slide-image` – image/crop from the PDF + max 2 keywords alongside.
- `summary` – card grid with the key statements.
- `code` – source code/SQL from the lecture (see below).
- `formula` – formula large and centered, optionally with a symbol table below.
- `table` – data table, comparison table, SQL result.
- `quiz-question` / `quiz-answer` – self-test scenes.

## Custom graphics

- As **inline SVG** with a `viewBox` so they scale crisply. All text in the SVG ≥ 28 px (relative to the 1920 stage).
- Only elements, terms, relationships and numbers from the materials. If you rebuild a diagram from a slide: same elements and relationships, arranged more clearly if you like.
- Don't drop axes, units or labels that are in the original.

## Slide images from the PDF

- Prefer **crops** over whole slides: `extract_pdf.py <pdf> <out> --crop PAGE x0,y0,x1,y1` (coordinates in percent of the page) renders the region at high resolution.
- After scaling into the scene, the smallest text in the image must be ≥ ~24 px tall on the stage. If smaller: crop tighter, rebuild the graphic yourself, or leave it out.
- `object-fit: contain`, never `cover` (cuts content). No stretching.
- Don't include university logos/decorative images, except subtly in the intro if the user wants.
- Photos of people from slides only if they matter for the content.

## Code & SQL

- `<pre class="code" data-lang="sql">` – highlighting for sql, python, java, js is automatic; otherwise `plain`. Copy code **exactly as on the slide** (including identifiers); don't "fix" obvious typos on the slide – leave them.
- Font 36 px (minimum 28 px), monospace. **No wrapping, no shrinking, no scrolling.** Rule of thumb at 36 px: max ~75 characters per line, max ~14 lines. Longer code → split into two scenes or show the relevant excerpt with "…" for omitted parts, plus the slide number.
- Highlight the lines being discussed in sync with the explanation: `data-focus-lines="1@0.1-0.35; 2-3@0.35-0.7"` (lines@fraction of narration time). The other lines are dimmed but stay readable.
- The narration doesn't read code character by character; it explains what happens ("Here we join both tables on the customer number").
- If the slide shows the result of a query: as `table.data` alongside or in the next scene.

## Formulas

- As **MathML** (`<math display="block">…</math>` inside `<div class="formula">`) – runs in every current browser and when rendering, with no external library. Fractions `<mfrac>`, subscripts `<msub>`, sums `<munderover><mo>∑</mo>…`.
- Formula size 84 px (`.formula`) or 60 px (`.formula.small`); subscripts must not drop below 28 px – the check measures this.
- Symbols exactly as in the lecture (same letters, same subscripts). Below the formula, a small "symbol → meaning" table if more than two quantities appear.
- Derivations step by step: each transformation as its own `data-at` element, not all at once.
- In the audio text, the formula in words ("D-B equals U minus K v"); on screen, the real formula.

## Tables

- `<table class="data">`, 36 px (minimum 28 px), numbers right-aligned (`td.num`). Max ~6 columns × 8 rows; trim larger tables to the relevant rows/columns (with a note "excerpt, full table on slide X") or split.
- Highlight the row/column being discussed with `data-focus` on `<tr>`/`<td>`.

## Visual-only mode

- The explanation the narrator would give goes into `<p class="explain">` (36 px, accent bar on the left) – one per scene, 1–3 short sentences, placed below or beside the graphic/keywords, never over it.
- Reveal the explanation together with the part of the graphic it refers to (`data-at`), so the eye follows the order of the explanation.
- Up to ~60 on-screen words per scene (instead of ~40); everything else in this file applies unchanged.

## Outline scene

- `<ol class="toc" data-toc></ol>` under a heading in the video language ("Gliederung", "Outline"). The scene file fills it after timing is known: time range, chapter title, slides.
- Up to 6 chapters → one column; 7–12 → two columns in a slightly more compact style. More than 12 chapters means the chapters are too fine – merge them rather than shrinking the outline.
- Chapter titles should be short (≤ ~35 characters) so they fit on one or two lines; long German compounds get hyphenated automatically.
- Nothing else on this scene. The layout check covers it like any other scene – check its snapshot, since the content only exists after timing.

## Self-test scenes

- **Question scene** (`data-think`, `data-hold` = thinking time): kicker "Self-test · Question 2 of 5" (in the video language), the question large below it (`.quiz-q`, 60 px). Nothing else – no hints that give away the answer.
- **Answer scene:** question small and grey at the top, answer in the green box (`.quiz-a`), source at the bottom ("Slide 12"). For process questions, use the `process` layout for the answer.
- Chapter "Self-test" on the intro scene of the quiz so learners can jump straight to it.

## Subtitles

- Generated automatically from each scene's `<template class="caption">`: max ~84 characters per subtitle, sentence boundaries preferred, never split right after abbreviations like "Prof.".
- In the MP4 they are a toggleable subtitle track (not burned in) – so they never cover content and need no room in the safe area.
- Subtitle text = on-screen spelling. Phonetic aids for the TTS belong only in the audio text.

## Animation

- Animations serve understanding: reveals in sync with the explanation, highlighting, arrows. No effects for their own sake, no fast camera moves.
- Reveal via opacity/short shift (≤ 40 px) **inside** the safe area. Nothing flies in from outside the frame – that's exactly how half-visible text happens.
- Final state of every scene: all elements fully visible, calm, nothing moving while the hold runs.
- Scene changes: short crossfade (300–400 ms). Never let text from two scenes overlap readably during a transition – fade the old scene out first.
- Respect `prefers-reduced-motion` (fades only).

## Layout check (automatic)

`render.py --check` checks every scene in two states (mid-animation, final state) and reports:
- elements with `scrollWidth > clientWidth` or `scrollHeight > clientHeight` (overflow / clipped),
- text or image elements whose box leaves the safe area,
- computed font size below the minimum for the element type,
- overlapping text elements,
- slide images scaled down so far that their text is likely unreadable,
- scenes without subtitle or source, and a first scene without a chapter.

Fix every finding. Exceptions only for elements marked `data-deko` that deliberately extend beyond the edge.
