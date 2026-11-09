#!/usr/bin/env python3
"""Generate one audio file per scene through the OpenRouter TTS API (POST /api/v1/audio/speech).

Use this when the OpenRouter MCP tool `generate-speech` runs but its audio never arrives as a file
(the client reports e.g. 'Audio content (audio/mpeg) is not currently supported'). It calls the SAME
model with the SAME voice – only the route differs. Python 3 standard library only, so it also runs
on the user's own computer.

  export OPENROUTER_API_KEY=sk-or-...           # never write the key into files
  python3 tts_openrouter.py script.json audio/                  # all scenes
  python3 tts_openrouter.py script.json audio/ --only s07 s09 --suffix _v2   # redo single scenes
  python3 tts_openrouter.py script.json audio/ --dry-run        # show what would be generated
  python3 tts_openrouter.py --check                             # is openrouter.ai reachable from here?
  python3 tts_openrouter.py --pcm-to-wav in.pcm out.wav [--rate 24000]

Reads model, voice and instructions from script.json (meta.tts_model, meta.voice, meta.tts_instructions);
command-line flags override them. Text per scene: "audio_text" if present, else "narration".
Writes audio/<scene id><suffix>.wav (PCM models such as Gemini TTS) or .mp3, plus audio/manifest.json
with file, duration and generation id per scene (costs: get-generation with that id).
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import wave

API = os.environ.get("OPENROUTER_TTS_URL", "https://openrouter.ai/api/v1/audio/speech")   # override only for testing
PCM_ONLY = re.compile(r"^(google/gemini-.*tts|heygen/)", re.I)   # known to accept only pcm


def check():
    try:
        urllib.request.urlopen("https://openrouter.ai/api/v1/models?output_modalities=speech", timeout=10)
        print("reachable")
        return 0
    except Exception as e:
        print(f"NOT reachable from this environment: {e}")
        return 1


def pcm_to_wav(pcm_bytes, path, rate=24000, channels=1, width=2):
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(width)
        w.setframerate(rate)
        w.writeframes(pcm_bytes)
    return len(pcm_bytes) / (rate * channels * width)


def mp3_duration(path):
    import shutil
    import subprocess
    if not shutil.which("ffprobe"):
        return None
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def speak(key, model, text, voice, fmt, instructions=None, speed=None):
    body = {"model": model, "input": text, "response_format": fmt}
    if voice:
        body["voice"] = voice
    if instructions:
        body["instructions"] = instructions
    if speed:
        body["speed"] = speed
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "X-Title": "lecture-video-explainer"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read(), r.headers.get("Content-Type", ""), r.headers.get("X-Generation-Id")


def rate_from(ctype, default=24000):
    m = re.search(r"rate=(\d+)", ctype or "")
    return int(m.group(1)) if m else default


def channels_from(ctype, default=1):
    m = re.search(r"channels=(\d+)", ctype or "")
    return int(m.group(1)) if m else default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", nargs="?")
    ap.add_argument("outdir", nargs="?")
    ap.add_argument("--model"); ap.add_argument("--voice"); ap.add_argument("--instructions")
    ap.add_argument("--speed", type=float)
    ap.add_argument("--format", choices=["mp3", "pcm"], help="default: pcm for Gemini/HeyGen, else mp3")
    ap.add_argument("--only", nargs="*", help="scene ids to (re)generate")
    ap.add_argument("--suffix", default="", help="file name suffix for new versions, e.g. _v2")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--pcm-to-wav", nargs=2, metavar=("IN", "OUT"))
    ap.add_argument("--rate", type=int, default=24000)
    a = ap.parse_args()

    if a.check:
        sys.exit(check())
    if a.pcm_to_wav:
        d = pcm_to_wav(open(a.pcm_to_wav[0], "rb").read(), a.pcm_to_wav[1], a.rate)
        print(f"{a.pcm_to_wav[1]}: {d:.2f} s")
        return
    if not (a.script and a.outdir):
        ap.error("script.json and output folder are required")

    data = json.load(open(a.script, encoding="utf-8"))
    meta = data.get("meta", {})
    model = a.model or meta.get("tts_model")
    voice = a.voice or meta.get("voice")
    instructions = a.instructions or meta.get("tts_instructions")
    if not model:
        sys.exit("No model: set meta.tts_model in script.json or pass --model (use exactly the model the user chose).")
    fmt = a.format or ("pcm" if PCM_ONLY.match(model) else "mp3")
    scenes = [s for s in data.get("scenes", []) if (s.get("audio_text") or s.get("narration"))]
    if a.only:
        scenes = [s for s in scenes if s["id"] in a.only]
    os.makedirs(a.outdir, exist_ok=True)
    print(f"model={model} voice={voice or '(default)'} format={fmt} scenes={len(scenes)}")
    if a.dry_run:
        for s in scenes:
            print(f"  {s['id']}: {len(s.get('audio_text') or s['narration'])} chars")
        return

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("OPENROUTER_API_KEY is not set (export it in the shell; never write it into a file).")

    man_path = os.path.join(a.outdir, "manifest.json")
    manifest = json.load(open(man_path, encoding="utf-8")) if os.path.exists(man_path) else {}
    failed = []
    for s in scenes:
        text = s.get("audio_text") or s["narration"]
        for attempt in range(3):
            try:
                audio, ctype, gen_id = speak(key, model, text, voice, fmt, instructions, a.speed)
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="replace")
                # format mismatch: the error names the only accepted format -> switch once, same model
                try:
                    msg = json.loads(msg)["error"]["message"]
                except Exception:
                    pass
                m = re.search(r"only supports response_format\W+(\w+)", msg)
                if m and m.group(1) != fmt and attempt == 0:
                    fmt = m.group(1)
                    print(f"  {s['id']}: model needs response_format={fmt}, retrying")
                    continue
                if e.code in (429, 500, 502, 503) and attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue
                print(f"  {s['id']}: FAILED HTTP {e.code}: {msg[:300]}")
                audio = None
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(3)
                    continue
                print(f"  {s['id']}: FAILED {e}")
                audio = None
                break
        if audio is None:
            failed.append(s["id"])
            continue
        if fmt == "pcm" or "pcm" in ctype:
            path = os.path.join(a.outdir, f"{s['id']}{a.suffix}.wav")
            dur = pcm_to_wav(audio, path, rate_from(ctype), channels_from(ctype))
        else:
            path = os.path.join(a.outdir, f"{s['id']}{a.suffix}.mp3")
            open(path, "wb").write(audio)
            dur = mp3_duration(path)
        manifest[s["id"]] = {"file": os.path.basename(path), "duration_s": round(dur, 3) if dur else None,
                             "generation_id": gen_id, "model": model, "voice": voice}
        json.dump(manifest, open(man_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"  {s['id']}: {os.path.basename(path)} {dur:.1f} s" if dur else f"  {s['id']}: {os.path.basename(path)}")

    if failed:
        print(f"FAILED scenes: {' '.join(failed)} – stop and tell the user; do not switch models on your own.")
        sys.exit(1)
    print(f"done -> {man_path}")


if __name__ == "__main__":
    main()
