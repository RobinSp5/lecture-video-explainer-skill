<div align="center">

# 🎓 Lecture Video Explainer

**Turn lecture slides into a fully narrated explainer video — ready for exam prep.**

A Claude skill that reads your PDF, writes a faithful script, builds readable visuals, adds an AI voice via OpenRouter, and hands you one MP4.

</div>

---

## ✨ What you get

Drop in a PDF of lecture slides, say *"make me a video from these slides"*, and receive a single **1080p / 30 fps MP4** with:

- 🎙️ **AI narration** in your chosen language (or a silent, text-driven "visual-only" version)
- 🖼️ **Readable graphics** — diagrams, slide crops, code, SQL, formulas, tables
- 🧭 **Intro, outline with time ranges, summary** and optional **self-test questions**
- 💬 **Toggleable subtitles** and **chapter marks** for quick exam review
- ✅ **Exercise sheets solved** step by step, with results verified before they go in the video

## 🔑 Requirements

> [!IMPORTANT]
> **You need an [OpenRouter](https://openrouter.ai) MCP connection.** The voice is generated through the connector's `generate-speech` tool.
>
> **If you use Claude, use Claude Cowork.** In other Claude surfaces the connector's audio does not reliably reach the video (typically: *"Audio content (audio/mpeg) is not currently supported"*), so the narration breaks.

| | |
|---|---|
| **OpenRouter MCP** | Connected, with credit on your account (a few cents per video) |
| **Claude Cowork** | Recommended environment when using Claude |
| **Rendering** | Code execution with `ffmpeg` and Chromium (handled by Claude, nothing for you to install) |

No OpenRouter? Visual-only mode needs no voice and costs nothing.

## 🚀 Install

1. Download or build `lecture-video-explainer.skill` (see below).
2. In **Claude Cowork**, add it as a skill and connect the **OpenRouter** connector.
3. Upload your slides and ask for a video.

<details>
<summary>Build the <code>.skill</code> file yourself</summary>

```bash
cd lecture-video-explainer && zip -r ../lecture-video-explainer.skill . -x "*.DS_Store"
```

For Claude Code, copy the `lecture-video-explainer/` folder to `~/.claude/skills/` instead.

</details>

## 💬 Usage

Just talk to Claude:

> *"Make me a video from these slides."*
> *"Turn this lecture into a narrated explainer for the exam."*
> *"Mach mir ein Video aus den Folien."*

Claude then asks a few short questions **before spending anything**:

1. **Video type** — short summary or comprehensive
2. **Narration** — AI voice or visual-only
3. **Language** — same as the slides, or any other
4. **Length, TTS model and exact price**, outline, self-test questions
5. **Look** — light/dark, and a style (modern, minimal, slide colors, or topic-themed)
6. **Voice** — gender, character, pace

## ⚙️ How it works

```
PDF ──▶ Read ──▶ Ask ──▶ Script ──▶ Visuals ──▶ Narration ──▶ Timing ──▶ QA ──▶ MP4
```

Three rules drive every decision:

1. **Invent nothing.** Everything on screen and in the voice comes from your materials.
2. **Everything readable.** Minimum font sizes, safe areas, and an automatic layout check catch clipped or overflowing text.
3. **Fluent voice, calm visuals.** No long pauses; dense graphics get a short hold so you can read them.

Before delivery, a **fact check, layout check and coverage check** make sure every slide topic and every open question from the lecture is handled.

## 📁 Repository layout

```
lecture-video-explainer/
├── SKILL.md                 # the skill's workflow
├── references/              # didactics, visual rules, TTS model selection
├── scripts/                 # PDF extraction, cost estimate, coverage, palette, renderer, TTS fallback
└── assets/video-template.html
```

## 📝 Notes

- The chosen OpenRouter TTS model is **binding**: it is used for every scene, never silently swapped.
- Changes after delivery are surgical — only the affected scenes get new audio.
- Prices and models are fetched live from OpenRouter, never from memory.
