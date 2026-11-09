# Lecture Video Explainer

A Claude skill that converts lecture slides into one narrated MP4 for self-study and exam preparation.

Give it a PDF. It reads the slides, writes a script that stays faithful to them, builds the visuals, generates the voice through OpenRouter, and returns a 1080p video with subtitles and chapters.

## Requirements

You need an **OpenRouter MCP connection**. The voice is generated with the connector's `generate-speech` tool.

If you use Claude, use **Claude Cowork**. In other Claude surfaces the audio from the connector does not reach the video (the tool answers with `Audio content (audio/mpeg) is not currently supported`), so narration fails.

| Requirement | Detail |
| --- | --- |
| OpenRouter MCP | Connected, with credit on the account. A typical video costs a few cents. |
| Claude Cowork | The supported environment when using Claude. |
| ffmpeg and Chromium | Used for rendering. Claude runs them, you install nothing. |

Without OpenRouter you can still use visual-only mode: no voice, no cost.

## Install

1. Download `lecture-video-explainer.skill` from the [latest release](../../releases/latest).
2. In Claude, open Settings, go to the skills section and upload the `.skill` file.
3. Connect the OpenRouter connector.
4. Upload your slides.

To build the file from this repository instead:

```bash
zip -r lecture-video-explainer.skill lecture-video-explainer -x "*.DS_Store"
```

For Claude Code, copy the `lecture-video-explainer/` folder to `~/.claude/skills/` instead.

## Usage

Ask in plain words:

```text
Make me a video from these slides.
Turn this lecture into a narrated explainer for the exam.
Mach mir ein Video aus den Folien.
```

Before anything is generated, Claude asks what it needs to know:

- Short or comprehensive summary
- AI voice or visual-only
- Video language (same as the slides, or another)
- Length, TTS model, and the exact price for that length
- Optional outline and self-test questions
- Look: light or dark, and a style (modern, minimal, slide colors, or themed to the topic)
- Voice: gender, character, pace

No money is spent until you confirm.

## Output

One MP4, 1080p at 30 fps, containing:

- Narration, or on-screen explanations in visual-only mode
- Diagrams, slide crops, code, SQL, formulas and tables
- Intro, optional outline with time ranges, summary, optional self-test
- A toggleable subtitle track and chapter marks

If the PDF is an exercise sheet, the video solves each task step by step. Calculations and queries are run before they go into the script.

## How it works

```text
PDF > read > ask > script > visuals > narration > timing > checks > MP4
```

The skill follows three rules:

- **Nothing invented.** Every statement, number and graphic comes from your materials.
- **Everything readable.** Minimum font sizes, a safe area, and an automatic layout check for clipped or overlapping text.
- **Steady voice, calm visuals.** No long pauses. Dense graphics stay on screen long enough to read.

Before delivery it runs a layout check, a fact check against the source pages, and a coverage check that every content slide and every open question from the lecture is handled.

## Repository

```text
lecture-video-explainer/
  SKILL.md            workflow
  references/         didactics, visual rules, TTS model selection
  scripts/            PDF extraction, cost estimate, coverage, palette, renderer, TTS fallback
  assets/             video template
```

## Behavior worth knowing

- The TTS model you choose is used for every scene. It is never swapped silently.
- Prices and models are fetched live from OpenRouter.
- Changes after delivery regenerate only the affected scenes.
