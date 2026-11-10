# Lecture Video Explainer

A Claude skill that turns lecture slides into one narrated MP4 for self-study and exam prep. It reads the PDF, writes a script that sticks to the slides, builds the visuals, generates the voice via OpenRouter and returns a 1080p video with subtitles and chapters.

## Key features

- Narrated video, or visual-only without any cost
- Nothing invented: every statement and number comes from your slides
- Exercise sheets are solved step by step, with calculations run before they appear
- Toggleable subtitles and chapter marks
- Fact check and layout check before delivery

## Quick start

1. Download `lecture-video-explainer.skill` from the [latest release](../../releases/latest).
2. In Claude Desktop, add the file under Settings > Skills.
3. Connect the OpenRouter connector, with some credit on the account.
4. Upload your slides and ask: "Make me a video from these slides."

Claude asks about length, voice, language and look before anything is generated. No money is spent until you confirm.

## Requirements

- **Claude Cowork** if you use Claude. In other surfaces the connector's audio does not reach the video.
- **OpenRouter connector** for narration. Visual-only mode works without it.
- ffmpeg and Chromium for rendering. Claude runs them, you install nothing.

## Other install options

- **Claude Code:** clone the repo into `~/.claude/skills/lecture-video-explainer/`.
- **Build the .skill yourself:** `mkdir -p build/lecture-video-explainer && cp -R SKILL.md references scripts assets build/lecture-video-explainer/ && (cd build && zip -r ../lecture-video-explainer.skill lecture-video-explainer) && rm -rf build`

## FAQ

**Why does narration fail outside Cowork?** The connector returns `audio/mpeg`, which other Claude surfaces do not pass on. Use Cowork, or pick visual-only.

**Does it cost anything?** A typical narrated video costs a few cents on OpenRouter. Prices are fetched live before you confirm.

## License

MIT. See [LICENSE](LICENSE).
