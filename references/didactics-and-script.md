# Didactics & script

## What the video is for

Two situations, both must work:
1. **First understanding** without attending the lecture → clear thread, terms introduced properly, nothing assumed that the materials don't explain.
2. **Review before the exam** → key statements easy to spot, the lecture's structure recognizable, slide numbers for looking things up.

## Faithfulness to the materials

- Terms, definitions, models, numbers, examples and order come from the PDF. Keep the lecture's technical terms (the exam asks for exactly these), even if you then explain them in plain words.
- Simplifying means: shorter sentences, everyday language, technical term + plain translation ("redundancy – meaning the same data is stored more than once"). It does not mean: new facts, your own numbers, different definitions.
- If a slide only has bullet points, you may phrase them as sentences – but not extend the content.
- **Mnemonics and everyday comparisons** are allowed because they help memory a lot – but they must be recognizable as comparisons ("Think of it like …") and must not imply a wrong technical statement. No invented company examples, statistics or studies.
- Unclear or contradictory passages in the PDF: render them neutrally in the video and mention them to the user in the closing note.

## When video language ≠ language of the materials

The exam asks for terms as they appear in the lecture. So when translating:
- **Show the lecture's technical terms on screen in the original**, with the translation alongside: e.g. video English, slides German → "Purchase Requisition (Bestellanforderung)"; video German, slides English → "Bestellanforderung (Purchase Requisition)". In the narration, say both on first use, then use the video language.
- Don't force translations of established English terms that are also used as-is in the target language (e.g. "Data Warehouse", "Stakeholder" in German).
- Translate definitions accurately – don't simplify them until they mean something else.
- Quotes, formulas, model names, abbreviations (SAP transactions, standards) stay in the original.
- Slide images from the PDF stay as they are; the explanation next to them is in the video language.

## Memorability (what actually helps learning)

- **Advance organizer:** in the intro, say which 3–5 blocks are coming (or, if an outline scene was chosen, let the outline do this). Later, orient briefly at each chapter change ("Point two of four: …").
- **Chunking:** one idea per scene. Lists of at most 3–5 points; more → split into two scenes or group.
- **Dual coding:** speech explains, the picture shows structure (diagram, process, comparison). Don't read out the text that's on screen – show the keyword, speak the sentence.
- **Signaling:** highlight what is being talked about right now (accent color, arrow, reveal in sync with the explanation).
- **Repetition:** the summary at the end reuses the key terms exactly, ideally with the same icons/colors as in the main part.
- **Exam relevance:** if the materials give hints ("exam-relevant", "remember!", learning objectives), mark those places ("According to the slide, this is exam-relevant").
- Calm, friendly, direct tone. Default: neutral, no direct address or with "we" (in German: "du" only if the user wants it).

## Writing the narration

- Short sentences (≤ 20 words), active voice, written for the ear. No parentheses, no footnotes, no "see above".
- Spell out abbreviations on first use. For the TTS, add phonetics where needed: "ERP" → "E-R-P", "SQL" as "S-Q-L" or "sequel" depending on the lecture.
- Put formulas and number series into words and show them on screen.
- No filler ("As we all know", "Interestingly"). Every second counts with 5 minutes for 30 slides.
- Short transitions: "Now to the question of how …" instead of long bridges.

## Intro – template

Phrase it in the chosen video language. English / German:

> "This video is about [topic of the unit] from the course [course name] by Prof. [name]. We'll look at three things: [A], [B] and [C]."
>
> "In diesem Video geht es um [Thema] aus der Vorlesung [Modul] bei Prof. [Name]. Wir schauen uns drei Dinge an: [A], [B] und [C]."

If the professor's name is missing and the user doesn't want to add it, leave that part out – don't guess.

## Summary – template

> "Let's sum up: …" / "Fassen wir zusammen: …" + 3–6 key statements, one card scene each or one overview graphic. If a summary slide exists, use its points (phrased simply).

Optionally end with an overlay "To read up: slides X–Y" for the most important passages.

## Answering open questions

Lecturers often ask the audience ("Was glauben Sie, warum …?", "Welche Risiken sehen Sie?", "Diskutieren Sie kurz …"). In the lecture hall the answer comes live – in the video it must come right away, otherwise the learner is left with a gap.

- **Every** open question on the slides gets answered, in both video types – where it comes up, not at the end. Show the question as on the slide (as a heading or `.quiz-q`), then the answer (`.quiz-a` box or cards). No thinking pause, unless it is in the self-test.
- **Answer from the materials first:** often a later slide, a table or the summary contains the answer – use it and cite those pages in `source`.
- **Not answered in the materials:** give a short, well-founded answer that fits the lecture's framework, terms and examples (e.g. use the lecture's own categories or model). Mark it once on screen as "Antwortvorschlag" (in the video language). No invented numbers, studies, company cases or quotes; general, uncontroversial domain knowledge only.
- **Open/discussion questions** with no single right answer: give 2–4 solid points or both sides, as the lecture's perspective suggests, and say that other answers are possible.
- **Rhetorical questions** that the next slide answers itself: just answer them in the flow ("Warum ist das wichtig? Weil …").
- Short summary: one or two sentences per question; comprehensive: as long as the answer needs.
- In `script.json`, the answering scene gets `"answers_questions": [page]` so the coverage check can confirm nothing was left open.

## Solving exercises (exercise mode)

The learner wants to understand how to get to the solution – the way the exam will ask for it.

- **Solve first, then script.** Work out every task completely before writing any scene. Check each result independently: recompute numbers, run SQL against a small database built from the task's tables, trace algorithms step by step, re-derive formulas. If two approaches give different results, find out why before going on.
- **Method from the lecture.** Use the procedure, notation and terms of the lecture the exercise belongs to (e.g. the normalization steps exactly as taught, the SAP transaction names used in class). If the exercise names a method, use that one even if another would be shorter.
- **One step per scene (or per reveal).** Show the step on screen (calculation line, SQL clause, diagram change), say in one or two sentences *why* this step comes now. Long calculations: show the formula, insert the numbers, then the result – three reveals, not one wall of digits.
- **Result clearly marked** (`.quiz-a` box or accent color) and, where sensible, with a one-line plausibility check ("Probe: 120 + 80 = 200 ✓").
- **Solution sheet available:** follow its method and result; if you find a mistake in it, say so neutrally in the video and the closing note, showing both.
- **No solution sheet:** label the solutions once as "Lösungsvorschlag" (own solution). State any assumption for an ambiguous task in one line on screen.
- **Open tasks** (essays, discussions, "Diskutieren Sie …"): give a model answer structured as the lecture structures the topic (e.g. its criteria or framework), clearly as one possible answer, with the lecture slides it draws on.
- **Can't be solved from what's given** (missing data, a file you don't have): say so in the video and the closing note; never guess numbers.
- Chapters: one per task ("Aufgabe 1", "Aufgabe 2a"); the outline then doubles as a list of tasks with time ranges.

## Self-test questions

Goal: practice active recall – the way the exam demands it. Rules:

- **Only from the materials.** Every question and every answer has a slide number. No transfer questions with invented scenarios; application questions only if the lecture itself has an example/exercise for it.
- **Selection:** first content with exam hints (`exam_hint_pages`, learning objectives, "remember"), then the key terms of the summary. Spread across chapters, not everything from one section.
- **Mix question types:** definition ("What is meant by …?"), distinction ("How do … and … differ?"), process/order ("Which steps …, in what order?"), purpose/reason ("What is … for?"), for code/formulas: "What does this query return?" / "What does K_v stand for?".
- **Open questions** rather than multiple choice – that trains recall instead of recognition. Exception: the user wants MC, or the materials say the exam is MC.
- Short questions (≤ 15 words on screen), unambiguous, no trick questions, no double negatives.
- **Answer:** as short as a good exam answer (1–3 bullet points), in the lecture's terms, spoken in 1–2 sentences + "Read up: slide X".
- Order of questions = order of chapters in the video.

## Script schema (`script.json`)

```json
{
  "meta": {
    "course": "Enterprise Resource Planning",
    "topic": "Procurement process in SAP S/4HANA",
    "lecturer": "Prof. Dr. Example",
    "video_language": "de",
    "materials_language": "de",
    "target_duration_s": 300,
    "tts_model": "google/gemini-3.8-flash-lite-tts",
    "voice": "Laomedeia",
    "voice_answers": {"gender": "female", "character": "motivating", "pace": "brisk"},
    "materials_kind": "lecture",
    "video_type": "comprehensive",
    "skipped_pages": {"1": "title", "2": "agenda", "31": "references"},
    "look": {"mode": "light", "style": "modern"},
    "tts_instructions": "Speak in German. Warm, motivating tutor who enjoys explaining. Sound encouraging and positive, smile in the voice, stress key terms. Brisk, energetic pace, no long pauses between sentences.",
    "quiz_questions": 5,
    "outline": true
  },
  "scenes": [
    {
      "id": "s01",
      "type": "intro",
      "chapter": "Intro",
      "source": [1, 2],
      "narration": "In diesem Video geht es um …",
      "audio_text": "In diesem Video geht es um … (optional: phonetically adjusted version for the TTS)",
      "screen": {
        "layout": "title",
        "title": "Beschaffungsprozess",
        "subtitle": "ERP · Prof. Dr. Example",
        "elements": ["Bestellanforderung", "Bestellung", "Wareneingang", "Rechnungsprüfung"]
      },
      "dense": false,
      "answers_questions": [],
      "estimated_duration_s": 10
    }
  ]
}
```

- `type`: `intro` | `outline` | `task` | `solution_step` | `result` | `chapter` | `content` | `graphic` | `slide_image` | `code` | `formula` | `table` | `summary` | `quiz_intro` | `quiz_question` | `quiz_answer` | `outro`
- `chapter`: only set on scenes that start a section (becomes `data-chapter`); otherwise `null`.
- `narration` → subtitle track (on-screen spelling); `audio_text` → TTS only.
- `dense: true` → the scene gets a hold time (see SKILL.md, Phase 5).
- Quiz questions additionally get `"think_s": 6`.
- `source` is mandatory for every scene except pure transitions.
