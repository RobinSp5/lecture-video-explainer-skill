#!/usr/bin/env python3
"""Length suggestions, word budget and TTS cost estimate.

  estimate.py lengths --content-pages 30 --type short|comprehensive
  estimate.py budget  --minutes 5 [--dense 6] [--lang de|en|other] [--pace calm|normal|brisk|fast] [--wpm 150 --cpw 6]
  estimate.py budget  --minutes 5 --silent        # visual-only: on-screen words budget, no TTS cost
  estimate.py cost    --minutes 5 --prompt 0.5 --completion 9 [--lang de] [--buffer 0.15] [--quiz 5] [--toc]
  estimate.py quiz    --questions 5 --prompt 0.5 --completion 9 [--lang de]   # surcharge for self-test

"--minutes" is always the length of the explanation part. Self-test questions (--quiz N) and the
outline scene (--toc, ~10 s) come on top.
Prices as in OpenRouter list-models: US dollars per 1 million (tokens or characters).
"""
import argparse
import json

LANG = {
    # words per minute of a calm explainer voice, characters per word incl. spaces
    "de": {"wpm": 145, "cpw": 6.5},
    "en": {"wpm": 155, "cpw": 5.8},
    "other": {"wpm": 145, "cpw": 6.0},  # generic starting point; adjust with --wpm/--cpw
}
# words/min per chosen pace (de, en; "other" follows de) – see references/tts-models.md
PACE_WPM = {"calm": (130, 140), "normal": (145, 155), "brisk": (160, 170), "fast": (175, 185)}
DEFAULT_PACE = "brisk"
AUDIO_TOKENS_PER_S = 32  # conservative assumption for audio output tokens (Gemini TTS)
TRANSITION_S = 0.35      # transition per scene
AVG_HOLD_S = 2.5         # average hold of a dense scene
SECONDS_PER_SCENE = 13   # typical scene length, used to estimate the scene count
# Self-test: intro + per question (read question ~5 s, thinking pause ~6 s, answer ~8 s, transitions)
QUIZ_INTRO_VIDEO_S, QUIZ_INTRO_SPEECH_S = 7, 5
QUIZ_Q_VIDEO_S, QUIZ_Q_SPEECH_S = 20, 13
# Outline scene after the intro: read chapter names (~6 s) + hold to look at it (~3 s)
TOC_VIDEO_S, TOC_SPEECH_S = 10, 6


def round_half_min(sec):
    return max(1.0, round(sec / 30) * 0.5)


def lang_params(lang, wpm=None, cpw=None, pace=None):
    p = dict(LANG.get(lang, LANG["other"]))
    if pace:
        p["wpm"] = PACE_WPM[pace][1 if lang == "en" else 0]
    if wpm:
        p["wpm"] = wpm
    if cpw:
        p["cpw"] = cpw
    return p


LENGTH_OPTIONS = {
    "short": {"very_short": 4, "short (default)": 6},
    "comprehensive": {"compact": 10, "standard (default)": 14, "detailed": 18},
}


def lengths(content_pages, vtype="comprehensive"):
    return {f"{k}_min": round_half_min(content_pages * s) for k, s in LENGTH_OPTIONS[vtype].items()}


def budget(minutes, dense=None, lang="de", wpm=None, cpw=None, pace=DEFAULT_PACE):
    total = minutes * 60
    scenes = max(4, round(total / SECONDS_PER_SCENE))
    if dense is None:
        dense = round(scenes * 0.3)
    non_speech = scenes * TRANSITION_S + dense * AVG_HOLD_S
    speech_s = max(total - non_speech, total * 0.6)
    p = lang_params(lang, wpm, cpw, pace)
    words = speech_s / 60 * p["wpm"]
    return {
        "video_s": round(total),
        "scenes_approx": scenes,
        "dense_scenes_approx": dense,
        "speech_s": round(speech_s),
        "words": round(words),
        "words_tolerance": [round(words * 0.9), round(words * 1.1)],
        "chars": round(words * p["cpw"]),
    }


READ_WPS = 3.0           # on-screen reading speed for learning content (words per second)


def silent_budget(minutes):
    total = minutes * 60
    scenes = max(4, round(total / 9))          # reading scenes are shorter than narrated ones
    graphic = round(scenes * 0.5)
    reading_s = max(total - scenes * (1.5 + TRANSITION_S) - graphic * 2, total * 0.5)
    words = reading_s * READ_WPS
    return {"mode": "visual-only", "video_s": round(total), "scenes_approx": scenes,
            "on_screen_words": round(words), "words_per_scene_approx": round(words / scenes),
            "cost_usd": 0}


def quiz(questions, lang="de", wpm=None, cpw=None, pace=DEFAULT_PACE):
    if not questions:
        return {"questions": 0, "video_s": 0, "speech_s": 0, "words": 0, "chars": 0}
    p = lang_params(lang, wpm, cpw, pace)
    video = QUIZ_INTRO_VIDEO_S + questions * QUIZ_Q_VIDEO_S
    speech = QUIZ_INTRO_SPEECH_S + questions * QUIZ_Q_SPEECH_S
    words = speech / 60 * p["wpm"]
    return {"questions": questions, "video_s": video, "speech_s": speech,
            "words": round(words), "chars": round(words * p["cpw"])}


def price(chars, speech_s, prompt, completion):
    if completion and completion > 0:
        # text tokens in (~4 chars/token), audio tokens out
        return chars / 4 * prompt / 1e6 + speech_s * AUDIO_TOKENS_PER_S * completion / 1e6
    return chars * prompt / 1e6


def cost(minutes, prompt, completion, lang="de", buffer=0.15, dense=None, wpm=None, cpw=None, questions=0, toc=False, pace=DEFAULT_PACE):
    b = budget(minutes, dense, lang, wpm, cpw, pace)
    q = quiz(questions, lang, wpm, cpw, pace)
    p = lang_params(lang, wpm, cpw, pace)
    toc_video, toc_speech = (TOC_VIDEO_S, TOC_SPEECH_S) if toc else (0, 0)
    toc_chars = round(toc_speech / 60 * p["wpm"] * p["cpw"])
    chars = b["chars"] + q["chars"] + toc_chars
    speech = b["speech_s"] + q["speech_s"] + toc_speech
    c = price(chars, speech, prompt, completion)
    return {
        "billing": "token-based (text in, audio out)" if completion else "character-based (conservative assumption)",
        "video_total_s": b["video_s"] + q["video_s"] + toc_video,
        "of_which_quiz_s": q["video_s"],
        "of_which_outline_s": toc_video,
        "chars": chars,
        "speech_s": speech,
        "cost_usd": round(c, 4),
        "cost_with_buffer_usd": round(c * (1 + buffer), 4),
        "of_which_quiz_usd": round(price(q["chars"], q["speech_s"], prompt, completion), 4),
    }


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lengths")
    p.add_argument("--content-pages", type=int, required=True)
    p.add_argument("--type", choices=list(LENGTH_OPTIONS), default="comprehensive")
    p = sub.add_parser("budget")
    p.add_argument("--minutes", type=float, required=True)
    p.add_argument("--dense", type=int)
    p.add_argument("--lang", default="de", choices=LANG)
    p.add_argument("--wpm", type=float); p.add_argument("--cpw", type=float)
    p.add_argument("--pace", choices=list(PACE_WPM), default=DEFAULT_PACE)
    p.add_argument("--silent", action="store_true", help="visual-only mode (no narration)")
    p = sub.add_parser("quiz")
    p.add_argument("--questions", type=int, required=True)
    p.add_argument("--prompt", type=float); p.add_argument("--completion", type=float, default=0)
    p.add_argument("--lang", default="de", choices=LANG)
    p.add_argument("--wpm", type=float); p.add_argument("--cpw", type=float)
    p.add_argument("--pace", choices=list(PACE_WPM), default=DEFAULT_PACE)
    p = sub.add_parser("cost")
    p.add_argument("--minutes", type=float, required=True)
    p.add_argument("--prompt", type=float, required=True)
    p.add_argument("--completion", type=float, default=0)
    p.add_argument("--dense", type=int)
    p.add_argument("--quiz", type=int, default=0, help="number of self-test questions")
    p.add_argument("--toc", action="store_true", help="include the outline scene after the intro")
    p.add_argument("--lang", default="de", choices=LANG)
    p.add_argument("--buffer", type=float, default=0.15)
    p.add_argument("--wpm", type=float); p.add_argument("--cpw", type=float)
    p.add_argument("--pace", choices=list(PACE_WPM), default=DEFAULT_PACE)
    a = ap.parse_args()

    if a.cmd == "lengths":
        out = lengths(a.content_pages, a.type)
    elif a.cmd == "budget":
        out = silent_budget(a.minutes) if a.silent else budget(a.minutes, a.dense, a.lang, a.wpm, a.cpw, a.pace)
    elif a.cmd == "quiz":
        out = quiz(a.questions, a.lang, a.wpm, a.cpw, a.pace)
        if a.prompt is not None:
            out["cost_usd"] = round(price(out["chars"], out["speech_s"], a.prompt, a.completion), 4)
    else:
        out = cost(a.minutes, a.prompt, a.completion, a.lang, a.buffer, a.dense, a.wpm, a.cpw, a.quiz, a.toc, a.pace)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
