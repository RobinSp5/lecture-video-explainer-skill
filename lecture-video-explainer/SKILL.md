---
name: lecture-video-explainer
description: Turns lecture materials (usually a PDF of slides) into a single, fully narrated explainer MP4 video for self-study and exam prep – in a selectable language (same as the slides, German, English or custom), with an AI voice via OpenRouter MCP, highly readable graphics, slide images from the PDF, code/SQL/formulas, an intro (course, topic, professor), an optional outline with time ranges, a summary, optional self-test questions, subtitles and chapters. ALWAYS use this skill when someone uploads lecture slides, a script or university materials and wants a video, video summary, explainer, narrated presentation or "something to watch instead of attending" – even if the word "video" never appears. German examples - "mach mir ein Video aus den Folien", "erklär mir die Vorlesung als Clip", "mach mir was zum Lernen für die Klausur aus diesen Folien", "Video-Zusammenfassung der Vorlesung". English examples - "lecture summary video", "turn these slides into a narrated explainer".
---

# Lecture Video Explainer

Goal: students should be able to understand a lecture **without attending it** and review it quickly **before the exam**. The video is therefore a learning tool, not a showcase: faithful to the lecture, simply explained, memorable, readable at all times.

Three principles guide every decision:

1. **Invent nothing.** Every statement, number, definition and graphic is backed by the lecture materials. Simplifying is welcome; adding facts is not. Someone writing the exam after watching must be able to trust that the content was in the lecture exactly like this.
2. **Everything readable, nothing cut off.** No half-visible text, no overflow, no tiny fonts. A single clipped sentence destroys trust in the whole video.
3. **Fluent voice, calm visuals.** The narrator makes no long pauses. Where there is a lot to see, the picture holds briefly before moving on – like a good presentation.

**The deliverable is the finished video, downloadable as one MP4 directly in Claude.** The user never runs code, scripts or commands and never has to paste an API key – everything technical happens on your side, with the tools this environment offers. No player, no extra files unless the user explicitly asks for them (subtitles as files, transcript, outline table).

Talk to the user in the language they write in. The video language is a separate choice (Phase 1, step 1).

There are two **modes**, chosen in the very first question: **narrated** (AI voice via OpenRouter, the default) and **visual-only** (no voice – everything is explained on screen, see "Visual-only mode" below). Wherever this file talks about narration, TTS or audio, that applies to the narrated mode only.

## Workflow

Work through the phases in order. Phase 1 is a mandatory stop: no money is spent (TTS) until the user has confirmed mode, language, model and length.

### Phase 0 – Read the materials

0. Look at what this environment offers, silently: the OpenRouter MCP connector (for the voice), a built-in video/animation output with MP4 export or download (e.g. in Claude Design), and/or code execution with `ffmpeg` + Chromium (for `scripts/render.py`). Phase 7 picks the output path from that. Never make the user install or run anything.
1. Extract the PDF with `scripts/extract_pdf.py`:
   ```bash
   python3 scripts/extract_pdf.py <pdf> <workdir> [--images]
   ```
   This produces `pages.json` (text, word count, image count per page), a PNG preview of every page and – with `--images` – the embedded images. If `pymupdf` is missing: `pip install pymupdf --break-system-packages`.
2. Look at the page previews (not just the text): diagrams, tables and process charts often exist only as images.
   **Scanned pages** (output "SCANNED/no text"): rerun with `--ocr` (Tesseract, language pack of the materials, e.g. `--ocr-lang deu+eng`). If Tesseract or the language pack is missing, look at the preview images and read the text yourself. Always proofread OCR text against the image before using technical terms or numbers in the script.
3. Determine from the materials: **course name, topic of this unit, lecturer/professor, language of the materials**, whether there is a **summary slide**, and which slides carry no content (title, agenda, references, "Questions?"). Anything not in the materials is not guessed – ask for it in Phase 1.
4. **Open questions in the slides:** `pages.json` lists, per page, `questions` – lines that ask the audience something ("Was meinen Sie: …?", "Welche Vorteile hat …?", "Diskussion: …", "Frage an Sie", "Why could …?"). They all get answered in the video (see "Open questions" in Phase 2). Read the slides yourself too: questions inside graphics or speech bubbles are not always caught.
5. **Lecture or exercise?** `pages.json` has `exercise_guess` (words like "Übung", "Aufgabe", "Übungsblatt", "Exercise", "Task", "Assignment", numbered tasks with a). b) c)). Confirm by reading: an exercise sheet asks the learner to *do* something. If it is an exercise (or a lecture with exercise slides), the video **solves the exercises** – see "Exercise mode" below. Also check whether a solution sheet or solution slides came with it.

Phase 0 runs silently: before the first questions (Phase 1, step 1) you ask the user **nothing else** and don't summarize the materials. The extraction only exists so the "same as the slides" option can name the detected language.

### Phase 1 – Ask the user (mandatory, before any generation)

#### Step 1 – Video type, narration and language (always the very first message)

The first message contains exactly these three questions and nothing else (as three tappable questions if such a tool is available), in the user's language, the video type always first. Example for a German-speaking user:

> **1. Was für ein Video soll es werden?**
> - **Kurze Zusammenfassung** – nur das Wichtigste: Kernbegriffe, zentrale Zusammenhänge, Klausurrelevantes; ideal zum schnellen Wiederholen
> - **Umfassende Zusammenfassung** – geht auf alle Themen der Unterlagen ein, mit Erklärungen und Beispielen; ersetzt die Vorlesung
>
> **2. Soll das Video vertont sein?**
> - **Ja, mit Sprecher (KI-Stimme)** – erklärt wie in der Vorlesung; kostet ein paar Cent
> - **Nein, nur visuell** – Erklärungen stehen als Text und Grafik im Bild, kein Ton, kostenlos
>
> **3. In welcher Sprache soll das Video sein?**
> - **Wie die Unterlagen (Deutsch)** ← detected language in parentheses
> - **Deutsch**
> - **Englisch**
> - **Andere Sprache** (free text)

The video type comes first because it decides what goes into the video and which lengths make sense:
- **Short summary:** only the core – key terms and definitions, the central relationships, everything marked exam-relevant, plus the summary slide. Examples, derivations and side topics are left out. Every chapter of the lecture may be touched in one or two sentences, but depth goes only to the core.
- **Comprehensive summary:** **every topic of the materials is covered** – each content page ends up in at least one scene (checked in Phase 6 with `scripts/coverage.py`), in the lecture's order, with the explanations and examples the lecture gives. Nothing is skipped, only condensed.
- For an exercise: short = for each task the approach in one or two sentences plus the result; comprehensive = the full solution path step by step.

Narration comes next because it changes everything that follows: with "visual-only" there is no model question, no cost, and the video is built differently.

Keep "same as the slides" even if the detected language is German or English – it is the default. For mixed-language materials, name the dominant one ("same as the slides (mostly English)").

The chosen language applies to **everything**: narration, on-screen text, intro, summary, labels like "take a look", TTS delivery instructions. It also determines which TTS models qualify and how word budget and cost are calculated – that's why it comes first.

If the video language differs from the slides' language, apply the translation rules in `references/didactics-and-script.md` (the lecture's technical terms stay visible, because the exam uses them). For "other language" in narrated mode: first check briefly whether any TTS models support it well; if not, say so openly and offer alternatives (including visual-only).

#### Step 2 – Length, model, key data, outline, quiz (one message)

Only after the answers to step 1. In visual-only mode, skip b) (model) and quote no costs; there is no step 4 (voice) then.

If the materials are an exercise, say so in one line at the top of this message ("Das ist ein Übungsblatt mit 4 Aufgaben – ich löse alle Schritt für Schritt im Video.") – no extra question; length suggestions then count tasks, not pages (≈ 45–90 s per task depending on size).

**a) Video length.** Suggest lengths that fit the video type from step 1, derived from the number of *content* pages (n) – `estimate.py lengths --content-pages n --type short|comprehensive`:

| Video type | Options (rule of thumb) | Example, 30 pages |
|---|---|---|
| Short summary | very short n × 4 s · **short n × 6 s** (default) | ~2 / ~3 min |
| Comprehensive summary | compact n × 10 s · **standard n × 14 s** (default) · detailed n × 18 s | ~5 / ~7 / ~9 min |

Round to half minutes. For "comprehensive", warn in one sentence if the user picks a length below n × 8 s: all topics still get covered, but very briefly. The user decides; a custom length is always allowed.

**b) TTS model incl. price for exactly this video** (narrated mode only). Procedure and cost formula are in `references/tts-models.md` – read it before asking. Short version:
- Fetch the current TTS models live via OpenRouter MCP (`list-models` with `output_modalities: "speech"`, sorted by price). Prices and models change – never answer from memory.
- Filter to models that support the **chosen video language**.
- Offer 3–4 models, cheapest good one first (preferably a Google Gemini Flash TTS variant), each with the **estimated price for the chosen length** – compute with `scripts/estimate.py`.
- If the length isn't decided yet: give prices for all three length options.
- **The choice is binding.** When the user picks an OpenRouter model, that exact model (same model ID, via OpenRouter MCP) MUST be used for every audio file of this video – see "Binding model choice" in Phase 4.

**c) Missing key data.** Only if not found in Phase 0: professor's name, course name. Offer "without name" as an option instead of guessing.

**d) Optional:** show slide images/graphics from the PDF directly (default: yes, where they explain something).

**e) Outline at the start of the video?** Yes / No. One sentence of explanation: right after the intro, a short table of contents shows every chapter with its time range ("0:18–1:30 Inner Join") and slide numbers, so learners can see the structure and jump to what they need. Costs about 10 seconds. The MP4 always has chapter marks as well, so players can jump between chapters either way.

**f) Self-test questions at the end?** Yes / No. One sentence of explanation: questions for self-quizzing with a short thinking pause followed by the answer – helps memory more than re-watching.

#### Step 3 – The look (+ number of questions)

One message with two questions about the look – and, only if self-test questions were chosen in step 2 f), a third one about their number (as tappable questions if such a tool is available; the defaults are named first):

> **Hell oder dunkel?**
> - **Hell** *(Standard)* · Dunkel
>
> **Welcher Stil?**
> - **Modern** *(Standard)* – farbige Akzente, sanfte Verläufe, Karten mit Schatten, Kapitel-Titelkarten
> - **Schlicht** – ruhig, viel Weiß bzw. Schwarz, nur eine Akzentfarbe
> - **Wie die Folien** – Farben aus den Vorlesungsfolien (z. B. Hochschul-Blau), damit es zur Vorlesung passt
> - **Passend zum Thema: …** – a concrete proposal derived from the content, e.g. "Datenbank-Look: Blau/Türkis mit dezentem Tabellenraster", "Nachhaltigkeit: Grüntöne mit Blatt-Motiv", "Finanzen: Dunkelblau/Gold mit Chart-Linien"
>
> **Wie viele Teste-dich-Fragen?** *(only if chosen)*
> - 3 · **5** · 8 · eigene Zahl – each with extra duration and cost (see below)

Write the "topic" option as one concrete suggestion for *this* lecture, not as a generic label. Skip "Wie die Folien" if `scripts/palette.py` finds no distinctive colors (plain black/white slides). How each answer is built: `references/visual-rules.md`, "Look".

**Number of questions:** options 3 / 5 / 8 / custom. For each option give the extra duration and extra cost (`estimate.py quiz --questions N --prompt … --completion …`; for the total incl. outline: `estimate.py cost … --quiz N --toc`), e.g. "5 questions · +1:45 min · +$0.02". Questions come **on top of** the chosen length of the explanation part; state the new total length once. If the materials have fewer meaningful key points than questions requested, offer fewer and say so briefly.

#### Step 4 – The voice (narrated mode only)

After the model is chosen, ask three short questions in one message (three tappable questions if such a tool is available); the defaults are pre-selected and named first:

> **Wie soll die Stimme klingen?**
> - **Weiblich** *(Standard)* · Männlich
>
> **Welcher Charakter?**
> - **Motivierend & freundlich** *(Standard)* · Ruhig & sachlich · Bestimmt & klar · Locker & entspannt
>
> **Wie schnell?**
> - Ruhig · Normal · **Zügig** *(Standard)* · Schnell

Default when the user skips or says "egal": **a good female, brisk, motivating explainer voice.** Map the answers to a concrete voice of the chosen model and to delivery instructions/speed with `references/tts-models.md` ("Voice choice"); name the voice you picked in one short line ("Stimme: Laomedeia – weiblich, motivierend, zügig"). The pace changes the word budget: pass it to `estimate.py --pace`. After the intro test (Phase 4) the user can still say "andere Stimme" or "langsamer" – then redo only the intro.

### Phase 2 – Script

Read `references/didactics-and-script.md`. Then write the script as `script.json` (schema there), scene by scene. Required structure:

1. **Intro (≈ 8–12 s):** "This video is about … from the course … by Prof. …" + an overview of what's coming in 3–5 points (advance organizer).
   **Outline (only if chosen, ≈ 10 s):** one scene directly after the intro with `<ol class="toc" data-toc>`. The scene file fills in every chapter with its time range and slides automatically from the final timing – never type times by hand, they change with every audio regeneration. Narration names the chapters in one or two sentences ("First …, then …, and at the end a summary and a self-test") and does **not** read out times. Mark the scene `data-dense` with `data-hold` ≈ 3 s so the outline can be read. When an outline is chosen, the intro's own agenda can be shorter (one sentence) so nothing is said twice.
2. **Main part:** chapters in the lecture's order. Explanations follow the lecture but may be phrased more simply.
3. **Summary (≈ 10–15 % of the length):** if the materials contain a summary, use it; otherwise build one from the key points – again only from the materials.
4. **Self-test (only if chosen):** at the very end, after the summary. Short intro ("Your turn – N questions. Pause the video if you need more time."), then two scenes per question: question (with thinking pause) and answer (with slide number). Rules for good questions: `references/didactics-and-script.md`.
5. **Closing:** one sentence, no long outro.

For an exercise, the main part is the solutions instead – see "Exercise mode".

**Open questions from the lecture are always answered.** Every question the slides put to the audience (Phase 0, step 4) gets an answer right where it comes up: show the question as on the slide, then answer it – in a comprehensive summary fully, in a short summary in one or two sentences. Rules in `references/didactics-and-script.md` ("Answering open questions"); in short: take the answer from the materials first (later slides often answer it), otherwise give a well-founded answer in line with the lecture and mark it once as "Antwortvorschlag". Mark the answering scene in `script.json` with `"answers_questions": [page]`.

**Depth by video type:** short summary → one scene per core concept, chapters may be merged, summary carries a lot of weight. Comprehensive summary → follow the lecture chapter by chapter, keep its examples, one scene per idea; make sure every content page appears in some scene's `source`.

**Chapters:** (they also feed the outline) every scene that starts a new section gets a chapter (`data-chapter`): "Intro", the lecture's chapters (named as in the materials, shortened), "Summary", "Self-test" (in the video language). Chapters are the jump marks for exam review – 4–8 meaningful ones beat 20 tiny ones.

**Subtitles:** every scene contains its narration as `<template class="caption">` – in on-screen spelling, not the phonetic TTS variant ("ERP", not "E-R-P"). The MP4's toggleable subtitle track is generated from it automatically.

Word budget: TTS narrators speak ≈ 130–175 words/min depending on language and the chosen pace. Run `estimate.py budget --lang <video language> --pace <pace>` – it already subtracts hold times (see below). If the script is off by more than 10 %, cut or extend before generating audio.

Every scene gets a `source` entry (page numbers). It is your check against invented content and is shown small in the video ("Slide 12–14") so learners can look it up in the PDF directly.

Show the user a **short** outline (scene titles + duration) before narration. Don't dump the whole script unless they want to see it.

### Phase 3 – Build the visuals

Read `references/visual-rules.md` – its rules are the core of this skill. Key points:

- Stage 1920×1080, safe area 96 px left/right, 64 px top/bottom. No text outside.
- Body text ≥ 34 px, headings ≥ 60 px, source note ≥ 22 px. If it doesn't fit: split the content into two scenes, **never** shrink the font below the minimum.
- The screen shows keywords and graphics, not the spoken text.
- Build your own graphics (diagrams, processes, comparisons) freely – but only with elements, terms and numbers from the materials.
- Slide images from the PDF: as a crop at sufficient resolution (`extract_pdf.py --crop`); never screenshot whole text slides if the text ends up too small.
- **Code, SQL, formulas, tables** have dedicated layouts (syntax highlighting, line-by-line highlighting in sync with the explanation, MathML formulas, data tables). Code is never wrapped and never shrunk – too long means split. Details in `references/visual-rules.md`.

**Look:** set `data-mode` (light/dark) and `data-style` (simple/modern/slides/topic) on `<html>` as chosen in Phase 1, step 3 – the template then switches all colors, backgrounds, cards and headings. For "slides", run `scripts/palette.py <pdf> --mode <light|dark>` and paste its CSS variables into `:root` (or the dark block); for "topic", pick an accent pair that fits the subject and add one decorative background motif (rules in `references/visual-rules.md`). Never hard-code colors in scenes – use the tokens, so the layout check can verify contrast.

**Make it visually rich, not just text on a background:** every content scene shows structure – a diagram, process chain, comparison, card grid, table, code or slide crop – rather than a heading plus bullets. Use chapter title cards (`.chapter-card` with the chapter number) at chapter starts, highlight what is being said (`data-focus`), and build graphics step by step. Bullet-only scenes are the exception (at most one in four scenes).

**Preview before spending money:** before narration (Phase 4), render snapshots of the intro, one chapter card and one content scene (`render.py --snapshots`) and show them to the user together with the short scene outline (Phase 2): "So sieht's aus – passt das?" Adjust the look on feedback; this costs nothing yet. In visual-only mode, show the preview the same way before rendering the MP4.

Build the scenes in a copy of `assets/video-template.html` (e.g. `work/video.html`): one `<section>` per scene, with timing, holds, outline, subtitles and a built-in layout check. Its attributes are documented at the top of the file. This file is only the source for the MP4 – never deliver it, publish it or present it as a player.

### Phase 4 – Narration (narrated mode only)

**Binding model choice.** The OpenRouter model the user chose in Phase 1 MUST be used – exactly that model ID and voice, for the test scene, every scene, every retry and every later change:
- Never substitute another model, a cheaper or "equivalent" variant, a `:free` variant, or a non-OpenRouter TTS – not even for a single scene and not to save time or money.
- The voice always comes from that model through the OpenRouter MCP connector (the API script only if the user explicitly asks for it) – never from another TTS.
- If the chosen model fails (error, unavailable, expired, language or voice unsupported, quality or cost far off the estimate): stop, tell the user what happened, and let them decide (retry, different voice, different model, visual-only). Only a model the user explicitly picks may replace it.
- Log model ID, generation ID and cost (via `get-generation`) for every file in `costs.json`. If a generation ran on a different model, treat it as a failure as above.
- The same applies when the user names a model directly ("use Gemini Flash TTS"): resolve it to the exact OpenRouter model ID, confirm it once in one sentence, then use only that.

**Required parameters** (otherwise the API rejects the call with HTTP 400):
- `voice`: always set one from `get-model` → `supported_voices` (some providers have no default voice).
- `response_format`: **Gemini TTS and HeyGen accept only `"pcm"`** (raw 16-bit, 24 kHz, mono); most others default to `mp3`. If an error says "only supports response_format …", switch the format – same model.
- PCM is not playable as-is: convert to WAV (`tts_openrouter.py --pcm-to-wav in.pcm out.wav`, no ffmpeg needed) or MP3 (`ffmpeg -f s16le -ar 24000 -ac 1 -i in.pcm out.mp3`). The scene file and renderer take `.wav` and `.mp3`.

**Getting the audio – via the OpenRouter MCP connector.**

Generate the voice with the connector's `generate-speech`, one call per scene, with the chosen model and the required parameters above. Then use the audio **in whatever form this environment hands it over**: a file in the tool result or in `/mnt/user-data/tool_results/` or the outputs folder, an asset/attachment the environment stores for the video, or an audio block your video output can take directly. Look in all of these before concluding anything.

1. **Intro scene first** (one call): confirm the audio is usable for the video in this environment before generating the rest – that keeps the cost of a mistake to one short clip.
2. **Usable → generate all scenes** the same way, one file per scene, and go on.
3. **Not usable here** – the tool only answers with something like `Audio content (audio/mpeg) is not currently supported` and no audio exists anywhere: don't repeat calls (each is billed). Tell the user in one or two plain sentences, quoting the tool's message, that this environment doesn't pass the connector's audio through, and offer:
   - running the same request where it works for them (e.g. Claude Design, or the app/surface where they downloaded a voiced video before), or
   - the video right now in visual-only mode.
   Don't ask them to run scripts or paste an API key. Only if they explicitly ask for a workaround with their own key: `scripts/tts_openrouter.py` (same model, same voice, via the OpenRouter API) can produce the files.
4. Never deliver a narrated video with silent placeholder audio unless the user explicitly chooses that.

**Narration quality:**

1. Check the test scene: correct language and pronunciation in the chosen video language, technical terms, pace. Compare its cost (`get-generation`) with the estimate; if it deviates a lot, tell the user before generating the rest.
2. Generate audio **per scene** (one file per scene → precise sync; on errors only one scene is redone).
3. Delivery instructions (for instructable models like Gemini TTS via `instructions`; also stored in `meta.tts_instructions`), built from the voice answers in Phase 1, step 4 (templates in `references/tts-models.md`), always naming the video language. Default: *"Speak in [language]. Warm, motivating female tutor who enjoys explaining. Brisk, energetic pace, no long pauses between sentences, stress technical terms clearly, sound encouraging."* For models with a `speed` parameter, pass the pace as `speed` too. When translating, have original-language technical terms pronounced correctly in their own language.
4. Technical terms/abbreviations that get mispronounced: spell them out or write them phonetically in the script (only in `audio_text`, not on screen).
5. Use the real duration of every audio file (`manifest.json` or `ffprobe`; the renderer measures it automatically) for timing. Scene length comes from audio + hold time, not from the estimate.

### Phase 5 – Timing & pauses

- **Between sentences:** no artificial pauses.
- **Between normal scenes:** 0.3–0.5 s transition.
- **Hold after dense scenes** (graphic, table, slide image, ≥ 5 elements): the picture stays after the narration ends so it can be looked at. Hold time = 1.5 s + 0.25 s per unspoken on-screen word, max 5 s (set via `data-hold`). A subtle progress bar shows that it will continue shortly.
- For very complex graphics, prefer building the graphic step by step while speaking over waiting long at the end.
- **Self-test questions:** thinking pause after the question is read (`data-think`, default 6 s; 4 s for simple term questions, up to 10 s for process/comparison questions). The video shows "Think about it …" (in the video language) with a countdown – this pause is intended and the only longer silence in the video.

### Phase 6 – Quality check (mandatory before delivery)

1. **Layout check:** `scripts/render.py work/video.html --check` visits every scene mid-animation *and* in its final state and reports elements that are clipped, overflowing, outside the safe area, too small, or overlapping. Fix every finding; don't ignore it.
2. **Visual check:** look at screenshots of the scenes (`render.py --snapshots`). Especially: are slide images readable? Is text on images high-contrast?
3. **Fact check:** read every scene against its source pages. Any statements, numbers or examples not in the materials? Remove them or mark them as a mnemonic (see the didactics reference).
4. **Length:** explanation part within ±10 % of the chosen length (outline and quiz come on top).
5. **Subtitles, chapters & outline:** the check reports scenes without subtitles or source. For your own review (not for the user) run `render.py work/video.html --export work/extras` and skim `chapters.txt`/`subtitles.srt`: meaningful chapters? Subtitles not breaking in the middle of a technical term? If there is an outline scene, look at its snapshot: all chapters visible, times plausible?
6. **Coverage:** `python3 scripts/coverage.py work/script.json work/pages.json` lists open questions from the slides that no scene answers (`answers_questions`) – always fix those, for both video types – and content pages that no scene cites in `source`. Every listed page must be covered by a scene or consciously skipped because it has no content of its own (title, agenda, references, duplicate) – add those to the script's `meta.skipped_pages` with a reason. For a short summary the page report is informational only; the question report is not.

### Phase 7 – Delivery: one MP4 to download

Pick the first path that works in this environment; the user just downloads the MP4 either way.

1. **The environment's own video output** (e.g. Claude Design's video/animation output with MP4 export or download): build the video there from the same scenes, timing and audio, and point the user to its download/export. Use this only if it can carry the narration audio from Phase 4; if it can't take external audio, use path 2.
2. **Rendered by you with `scripts/render.py`** (needs code execution with `ffmpeg` + Chromium on your side – invisible to the user). It takes a few minutes for a 5-minute video, so run it in the background and poll until it prints `MP4: …`:
   ```bash
   nohup python3 scripts/render.py work/video.html --mp4 /mnt/user-data/outputs/<Course>_<Topic>.mp4 > work/render.log 2>&1 &
   tail -n 3 work/render.log
   ```
   Then check duration (`ffprobe`) and one or two frames, and hand over only the MP4 (`present_files`). Name it after course and topic (e.g. `Datenbanken_SQL-Joins.mp4`). It is 1080p/30 fps with narration, a toggleable subtitle track (narrated mode) and chapter marks.
3. **Neither possible:** say so in one sentence and offer the visual-only video in the environment's own output, if it has one.

Close with a short note (in their language, 2–3 sentences): length, actual TTS cost, and whether content was deliberately left out (e.g. with "Compact").

If the user later asks for extras: `render.py work/video.html --export <dir>` produces `subtitles.srt`/`.vtt`, `chapters.txt`, `outline.md` and `transcript.md`.

## Exercise mode

When the materials are an exercise (Phase 0, step 5), the video solves it. Read "Solving exercises" in `references/didactics-and-script.md`. In short:

- **Structure:** intro (course, topic, which exercise sheet) → outline if chosen → one chapter per task ("Aufgabe 1", "Aufgabe 2a" …) → summary of the key solution ideas → self-test if chosen.
- **Per task:** show the task (crop from the PDF or retyped, with its number) → one sentence on what is asked and which concept from the lecture it needs → the solution step by step, every step on screen and explained → the result clearly highlighted (box/accent color) → for longer tasks, one sentence on the typical mistake to avoid, if the materials name one.
- **Correctness first:** solve every task completely yourself before writing the script. Verify everything that can be verified – calculations, SQL queries, formulas, algorithms, conversions – by actually computing/running it in your environment where possible (e.g. SQL on a small SQLite database with the task's data). A wrong solution in an exam-prep video is the worst possible outcome.
- **Sources:** if a solution sheet or solution slides exist, follow them (method and result) and cite them. Otherwise solve with the methods of the lecture this exercise belongs to; mark the solution on screen once as "Lösungsvorschlag" (own solution) in the intro of the solutions. Where a task is ambiguous, state the assumption on screen in one line.
- **Nothing invented:** use exactly the task's data. Don't add tasks, change numbers or skip sub-tasks; if a task cannot be solved from what is given (missing data, depends on a file you don't have), say so in the video and in the closing note instead of guessing.
- Before the solution of each task, a 2–3 s still with "Erst selbst probieren? Jetzt pausieren." is optional – only if the user asks for it.

## Visual-only mode

Chosen in Phase 1, step 1. No voice, no TTS, no OpenRouter calls, no cost. Everything that the narrator would say has to be understandable from the screen. Differences from the narrated mode:

- **Script:** instead of narration, each scene gets a short **explanation text** shown on screen (1–3 short sentences, ≤ 35 words) next to or below the graphic/keywords. Same rules as narration: faithful to the materials, simple, technical terms kept. The scene's `<template class="caption">` contains this explanation text too (used for the transcript if the user asks for one).
- **Layout:** the explanation sits in a fixed, calm text area (e.g. a card at the bottom or a side column), never on top of graphics. All visual rules still apply; on-screen text limits rise to ~60 words per scene, body text stays ≥ 34 px. Too much → split the scene.
- **Timing:** reading time instead of audio. Set `<html data-silent>` in the scene file; scenes without `data-dur` get their duration automatically from the visible words (≈ 3 words/s + 1.5 s, +2 s if the scene has a graphic, code, table or image; at least 4 s). Set `data-dur` by hand where a scene needs more time. Reveals (`data-at`) still work as fractions of the scene duration – build graphics step by step so the eye knows where to look.
- **Length:** the length options from Phase 1 still apply; budget on-screen words with `estimate.py budget --minutes N --silent`.
- **Subtitles:** none (the text is already on screen). The MP4 gets a silent audio track, chapter marks and no subtitle track.
- **Outline and self-test** work the same way; self-test questions keep their thinking countdown.
- Mention in the closing note that the video is silent, so pausing or slowing down in any video player works well with it.

## Changes after delivery

Implement change requests ("scene 7 again, slower", "the example on slide 12 is missing", "question 3 is too easy") surgically, don't redo the whole video:

1. Identify the affected scene(s) and change only those in `script.json` and the scene file.
2. **Regenerate only their audio** – with the same chosen model through the connector (binding, see Phase 4), under a new file name (`s07_v2.wav`) so nothing stale gets mixed in; keep the old version until the new one works.
3. "Slower/faster": use the `speed` parameter on models that support it, otherwise adjust the delivery instructions. Never speed up the whole video instead.
4. Timing, subtitles, chapters and the outline's time ranges adapt automatically (reveals are defined as fractions of the narration time).
5. Rerun the layout check, produce a new MP4 the same way as before (Phase 7), and tell the user the cost of the change.

Log the cost of every generation in `costs.json` (scene, model, cost from `get-generation`) so the total is correct at the end.

## References

- `references/tts-models.md` – model selection, language filter, cost formulas, how to present options.
- `references/didactics-and-script.md` – explanation style, memorability, translation rules, self-test questions, script schema, mnemonic rule.
- `references/visual-rules.md` – readability, safe area, font sizes, slide images, code/formulas/tables, quiz scenes, subtitles, animation.
- `scripts/extract_pdf.py` – PDF text, page previews, embedded images, crops, OCR for scans.
- `scripts/palette.py` – extracts the slides' brand colors for the "slides" look, adjusted to readable contrast for light or dark.
- `scripts/coverage.py` – checks that every open question from the slides is answered and that a comprehensive summary covers every content page.
- `scripts/estimate.py` – length suggestions, word budget, cost estimate per model, quiz surcharge.
- `scripts/render.py` – MP4 rendering (only re-captures frames that change), layout check, snapshots, optional extras export.
- `scripts/tts_openrouter.py` – only on explicit request: audio per scene via the OpenRouter API with the user's own key (same model); also converts PCM→WAV.
- `assets/video-template.html` – internal scene file the MP4 is rendered from: audio sync, hold times, subtitle track, chapters, auto-filled outline, code/formula/table layouts, quiz scenes and layout check. The example scenes show each layout once.
- `evals/` – test cases for the skill.
