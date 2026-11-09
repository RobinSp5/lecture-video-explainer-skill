#!/usr/bin/env python3
"""Render the scene file (assets/video-template.html, filled in) into the MP4 – the only deliverable.

  render.py video.html --mp4 out/video.mp4            # the MP4 (1080p, 30 fps) with audio,
                                                     # toggleable subtitle track and chapter marks
  render.py video.html --check                        # layout check before rendering, exit 1 on problems
  render.py video.html --snapshots work/shots         # mid + final state of every scene as PNG (for your own review)
  render.py video.html --export work/extras           # optional extras only if the user asks: subtitles.srt/.vtt,
                                                     # chapters.txt, outline.md, transcript.md

Long videos take a few minutes. Run in the background and poll the log, e.g.:
  nohup python3 render.py video.html --mp4 out/video.mp4 > render.log 2>&1 &
  tail -n 3 render.log        # repeat until it prints "MP4: …"

Requirements: playwright (python) + chromium, ffmpeg/ffprobe.
  pip install playwright --break-system-packages && playwright install chromium
Audio durations are measured with ffprobe and injected into the scene file so that timing
and soundtrack match exactly. Frames are only re-captured when something on screen changes.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright


def ffprobe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def audio_sources(html_path):
    import re
    html = Path(html_path).read_text(encoding="utf-8")
    return re.findall(r'<section[^>]*data-audio="([^"]+)"', html)


def open_scenes(p, html, mode):
    srcs = audio_sources(html)
    base = Path(html).resolve().parent
    durations = {}
    for s in srcs:
        d = ffprobe_duration(str(base / s))
        if d is None:
            print(f"WARNING: audio not readable: {s}", file=sys.stderr)
        else:
            durations[s] = d
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    page.add_init_script(f"window.PRESET_DURATIONS = {json.dumps(durations)};")
    page.goto(Path(html).resolve().as_uri() + f"?{mode}=1")
    page.wait_for_function("window.__ready === true", timeout=30000)
    page.evaluate("document.fonts.ready")
    return browser, page, base


def run_check(html):
    with sync_playwright() as p:
        browser, page, _ = open_scenes(p, html, "check")
        page.wait_for_function("window.__layoutReport !== undefined", timeout=60000)
        report = page.evaluate("window.__layoutReport")
        browser.close()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


def run_snapshots(html, outdir):
    os.makedirs(outdir, exist_ok=True)
    with sync_playwright() as p:
        browser, page, _ = open_scenes(p, html, "render")
        n = page.evaluate("window.__timeline.length")
        for i in range(n):
            for where in ("mid", "end"):
                page.evaluate(f"window.seekScene({i}, '{where}')")
                page.wait_for_timeout(50)
                page.screenshot(path=os.path.join(outdir, f"s{i+1:02d}_{where}.png"))
        browser.close()
    print(f"{n} scenes -> {outdir}")


ISO639_2 = {"de": "ger", "en": "eng", "fr": "fre", "es": "spa", "it": "ita", "nl": "dut", "pt": "por",
            "pl": "pol", "tr": "tur", "ru": "rus", "zh": "chi", "ja": "jpn", "ko": "kor", "ar": "ara"}


def ts(sec, sep=","):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def mmss(sec):
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60}:{sec % 60:02d}"


def collect(page):
    return {k: page.evaluate(f"window.__{k}") for k in ("timeline", "captions", "chapters", "duration", "meta")}


def write_exports(data, outdir):
    os.makedirs(outdir, exist_ok=True)
    caps, chaps, tl, meta = data["captions"], data["chapters"], data["timeline"], data["meta"]
    silent = bool(meta.get("silent"))
    for stale in ("subtitles.srt", "subtitles.vtt"):
        if silent and os.path.exists(os.path.join(outdir, stale)):
            os.remove(os.path.join(outdir, stale))
    with open(os.path.join(outdir, "subtitles.srt") if not silent else os.devnull, "w", encoding="utf-8") as f:
        for k, c in enumerate(caps, 1):
            f.write(f"{k}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n\n")
    with open(os.path.join(outdir, "subtitles.vtt") if not silent else os.devnull, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for c in caps:
            f.write(f"{ts(c['start'], '.')} --> {ts(c['end'], '.')}\n{c['text']}\n\n")
    with open(os.path.join(outdir, "chapters.txt"), "w", encoding="utf-8") as f:
        for c in chaps:
            f.write(f"{mmss(c['start'])} {c['title']}\n")
    # Outline: chapter with time range and slides (always delivered, also when the video has no outline scene)
    sw = meta["slideWord"]
    t_time, t_chap = {"de": ("Zeit", "Kapitel")}.get((meta["lang"] or "")[:2], ("Time", "Chapter"))
    out = [f"# {meta['title']}", "", f"| {t_time} | {t_chap} | {sw} |", "|---|---|---|"]
    for c in chaps:
        out.append(f"| {mmss(c['start'])}–{mmss(c['end'])} | {c['title']} | {c.get('slides') or '–'} |")
    with open(os.path.join(outdir, "outline.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    # Transcript as a study sheet: grouped by chapter, with slide numbers
    lines = [f"# {meta['title']}", ""]
    starts = {c["scene"]: c for c in chaps}
    for e in tl:
        if e["index"] in starts:
            c = starts[e["index"]]
            lines += ["", f"## {c['title']} ({mmss(c['start'])})", ""]
        if e["caption"]:
            src = f" *({meta['slideWord']} {e['source']})*" if e["source"] else ""
            lines.append(f"{e['caption']}{src}")
            lines.append("")
    with open(os.path.join(outdir, "transcript.md"), "w", encoding="utf-8") as f:
        import re as _re
        f.write(_re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n")
    with open(os.path.join(outdir, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Export: {0 if silent else len(caps)} subtitles, {len(chaps)} chapters"
          f"{' (visual-only: no subtitles)' if silent else ''} -> {outdir}")


def ffmetadata(chapters, total, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(";FFMETADATA1\n")
        for c in chapters:
            title = c["title"].replace("=", "\\=").replace(";", "\\;").replace("#", "\\#")
            f.write(f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(c['start']*1000)}\n"
                    f"END={int(min(c['end'], total)*1000)}\ntitle={title}\n")


def build_audio(timeline, base, total, out_wav):
    items = [(e["audio"], e["audioStart"]) for e in timeline if e.get("audio")]
    if not items:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                        "anullsrc=r=48000:cl=stereo", "-t", f"{total:.3f}", out_wav], check=True)
        return
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for src, _ in items:
        cmd += ["-i", str(base / src)]
    parts = []
    for k, (_, start) in enumerate(items):
        ms = int(round(start * 1000))
        parts.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[a{k}]")
    mix = "".join(f"[a{k}]" for k in range(len(items)))
    parts.append(f"{mix}amix=inputs={len(items)}:normalize=0:dropout_transition=0,"
                 f"apad,atrim=0:{total:.3f}[out]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[out]", out_wav]
    subprocess.run(cmd, check=True)


def run_mp4(html, out, fps, export_dir=None):
    with sync_playwright() as p:
        browser, page, base = open_scenes(p, html, "render")
        data = collect(page)
        timeline, total = data["timeline"], data["duration"]
        frames = int(total * fps) + 1
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "audio.wav")
            build_audio(timeline, base, total, wav)
            exp = export_dir or tmp
            write_exports(data, exp)
            meta = os.path.join(tmp, "chapters.txt")
            ffmetadata(data["chapters"], total, meta)
            lang = ISO639_2.get((data["meta"]["lang"] or "de")[:2], "und")
            silent = bool(data["meta"].get("silent"))
            cmd = ["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(fps), "-i", "-", "-i", wav]
            if silent:   # visual-only: no subtitle track, chapters from input 2
                cmd += ["-i", meta, "-map", "0:v", "-map", "1:a", "-map_metadata", "2", "-map_chapters", "2"]
            else:
                cmd += ["-i", os.path.join(exp, "subtitles.srt"), "-i", meta,
                        "-map", "0:v", "-map", "1:a", "-map", "2:s", "-map_metadata", "3", "-map_chapters", "3",
                        "-c:s", "mov_text", "-metadata:s:s:0", f"language={lang}"]
            cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-metadata:s:a:0", f"language={lang}",
                    "-shortest", "-movflags", "+faststart", out]
            ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            last_sig, last_img, shots = None, None, 0
            for f in range(frames):
                sig = page.evaluate(f"window.seek({f / fps})")
                if sig != last_sig or last_img is None:
                    last_img = page.screenshot(type="jpeg", quality=92)
                    last_sig = sig
                    shots += 1
                ff.stdin.write(last_img)
                if f % (fps * 10) == 0:
                    print(f"  {f / fps:6.1f} s / {total:.1f} s", flush=True)
            print(f"  {frames} frames, {shots} captured", flush=True)
            ff.stdin.close()
            ff.wait()
        browser.close()
    print(f"MP4: {out} ({total:.1f} s, {fps} fps)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--snapshots")
    ap.add_argument("--export")
    ap.add_argument("--mp4")
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()
    code = 0
    if a.check:
        code = run_check(a.html)
    if a.snapshots:
        run_snapshots(a.html, a.snapshots)
    if a.export and not a.mp4:
        with sync_playwright() as p:
            browser, page, _ = open_scenes(p, a.html, "render")
            write_exports(collect(page), a.export)
            browser.close()
    if a.mp4:
        run_mp4(a.html, a.mp4, a.fps, a.export)
    sys.exit(code)


if __name__ == "__main__":
    main()
