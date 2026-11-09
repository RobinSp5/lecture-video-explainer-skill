# TTS model selection via OpenRouter MCP

## 1. Fetch models live

```
list-models  { "output_modalities": "speech", "sort": "pricing-low-to-high", "limit": 40 }
```

Never answer from memory: models, prices and voices change constantly, and some models have an `expiration_date`. Only mention models expiring within the next 30 days if you say so.

## 2. Filter to the chosen video language

The video language was asked first (SKILL.md, Phase 1, step 1). A model only qualifies if it speaks exactly that language cleanly:

- **Gemini TTS family** (`google/gemini-*-tts*`): multilingual (German, English and many more), voices are language-independent. Instructable via `instructions` (pace, tone). Preferred default – cheap and good.
- **Models with language-prefixed voices** (e.g. `de-DE-…` for Microsoft MAI-Voice, `…-de` for Deepgram Aura-2): only if `supported_voices` contains a voice for the target language.
- **Check the description**: if it says "English-only" or the target language is missing from its language list (e.g. Kokoro, Orpheus, CSM), exclude it.
- When in doubt, call `get-model` or test with one sentence.
- `:free` variants only as a note ("free, but may have limits/expiry") – never as the default.

## 3. Estimate cost

Figures for German (English: 155 words/min, 5.8 chars/word; other languages: `estimate.py --lang other`, adjust with `--wpm`/`--cpw` if needed – e.g. languages with a different script have far fewer characters per word):

- Speaking rate ≈ 145 words/min, ≈ 6.5 characters per word incl. spaces → ≈ 940 characters per spoken minute.
- Spoken minutes = video length − hold times (≈ 8–12 % of the video length).

Two pricing models appear in `list-models`:

| Pricing | Meaning | Formula |
|---|---|---|
| `prompt` > 0 **and** `completion` > 0 (e.g. Gemini TTS) | text tokens in, audio tokens out | chars/4 × prompt + seconds × 32 audio tokens/s × completion |
| only `prompt` > 0, `completion` = 0 | billed by input text | chars × prompt (treat the price as "per million characters" – the conservative assumption) |

Prices are "$ per million" → divide by 1,000,000. `scripts/estimate.py cost` does this for you:

```bash
python3 scripts/estimate.py cost --minutes 5 --prompt 0.5 --completion 9 --lang de   # Gemini Flash TTS
python3 scripts/estimate.py cost --minutes 5 --prompt 15  --completion 0 --lang en   # character-based
python3 scripts/estimate.py cost --minutes 5 --prompt 0.5 --completion 9 --quiz 5    # incl. 5 self-test questions
```

Always add a 15 % buffer for redoing single scenes and the test sentence. State prices rounded to the cent in US dollars (OpenRouter bills in USD), formatted for the user's locale; below one cent as "< $0.01".

The estimate is an estimate: after the test scene in Phase 4, get the real cost with `get-generation` and extrapolate. If the extrapolation is > 50 % above the quoted estimate, ask the user before continuing.

## 4. Presenting the options

Short and comparable, in the user's language. Example for a German-speaking user (always compute the values live; this only shows the format):

> Für dein ~5-min-Video auf Deutsch (≈ 4.300 Zeichen Sprechtext):
> 1. **Gemini Flash Lite TTS** – ca. 0,05 $ · schnell, gute Qualität *(empfohlen)*
> 2. **Gemini Flash TTS** – ca. 0,08 $ · natürlichere Betonung
> 3. **MAI-Voice Flash (de-DE)** – ca. 0,07 $ · sehr natürlich, feste deutsche Stimmen
> 4. **ElevenLabs Flash v2.5** – ca. 0,18 $ · Premium-Klang

Per option: name, price for *this* video, half a sentence of character. No tables of raw per-million prices – the user can't do anything with those.

## 5. The choice is binding

Once the user has picked a model, it is used for the whole video – exact model ID and voice, for every scene, retry and later change. The voice comes through the OpenRouter MCP connector (the API script only if the user explicitly asks); the model never changes. No silent fallbacks to another model, variant or TTS tool. If it fails, stop and ask (details: SKILL.md, Phase 4, "Binding model choice"). Write the chosen model ID, voice and delivery instructions into `script.json` (`meta.tts_model`, `meta.voice`, `meta.tts_instructions`) right after the user's answer, and use those values for every call.

## 6. Technical requirements per model

- `voice` is required by some providers (e.g. Mistral Voxtral) – always pass one from `supported_voices`.
- `response_format`: Gemini TTS and HeyGen only accept `pcm` (16-bit, 24 kHz, mono → convert to WAV/MP3); most other models return `mp3`.
- `instructions` is only honored by instructable models (Gemini TTS, OpenAI TTS); elsewhere put the style into the voice choice.
- Long inputs: generate per scene anyway – that also keeps each request far below any model's input limit.

## 7. Voice choice (Phase 1, step 4)

**Default: female · motivating & friendly · brisk.** One voice for the whole video; no dialogue format unless the user wants it.

### Gemini TTS voices (all speak German and English)

Google describes each prebuilt voice with one word; use that to match the answers (female/male as the voices are commonly perceived – the intro test confirms it):

| | Motivating & friendly | Calm & factual | Firm & clear | Relaxed |
|---|---|---|---|---|
| **Female** | **Laomedeia** (upbeat) – default; Zephyr (bright), Autonoe (bright) | Erinome (clear), Vindemiatrix (gentle), Achernar (soft) | Kore (firm), Pulcherrima (forward) | Aoede (breezy), Callirrhoe (easy-going), Sulafat (warm) |
| **Male** | Puck (upbeat), Sadachbia (lively), Achird (friendly) | Charon (informative), Rasalgethi (informative), Iapetus (clear) | Orus (firm), Alnilam (firm), Sadaltager (knowledgeable) | Umbriel (easy-going), Zubenelgenubi (casual), Schedar (even) |

Use the first name in the cell unless the user asked for another. The name must be in `supported_voices` of the chosen model (check with `get-model`); if not, take the next one in the cell.

### Other models

Voice names rarely say gender or character. Read `supported_voices` and the model description (`get-model`); prefix-coded voices (e.g. `de-DE-…`) often include the name of a female/male speaker. If it stays unclear, pick the most likely one and let the intro test (Phase 4) decide; say which voice you picked.

### Delivery instructions (Gemini TTS and other instructable models)

Always start with "Speak in [video language].", then add character and pace:

| Character | Instruction text |
|---|---|
| Motivating & friendly (default) | "Warm, motivating tutor who enjoys explaining. Sound encouraging and positive, smile in the voice, stress key terms." |
| Calm & factual | "Calm, factual lecturer. Even tone, clear articulation, no dramatics." |
| Firm & clear | "Confident, clear and determined. Short, crisp emphasis on key terms, no hesitation." |
| Relaxed | "Relaxed and friendly, like explaining to a fellow student, but still precise." |

| Pace | Instruction | `speed` (models that support it) | words/min for the budget (de / en) |
|---|---|---|---|
| Calm | "Unhurried pace with short natural pauses." | 0.9 | 130 / 140 |
| Normal | "Natural, even pace." | 1.0 | 145 / 155 |
| **Brisk (default)** | "Brisk, energetic pace, no long pauses between sentences." | 1.1 | 160 / 170 |
| Fast | "Fast but clearly articulated pace, minimal pauses." | 1.2 | 175 / 185 |

Pass the pace to `estimate.py` (`--pace calm|normal|brisk|fast`) so the word budget and the cost estimate match.
