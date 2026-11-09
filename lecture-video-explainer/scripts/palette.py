#!/usr/bin/env python3
"""Extract the slides' brand/accent colors for the "slides" look and make them readable.

  palette.py <pdf> [--pages 1-5] [--mode light|dark]

Renders a few pages small, ignores white/black/grey and photo noise, and returns the dominant
saturated colors. It then suggests --accent and --accent2 for the video, adjusted (darker for light
mode, lighter for dark mode) until text in that color reaches 4.5:1 contrast on the video background.
Output: JSON with the raw colors and ready-to-paste CSS variables.
"""
import argparse
import colorsys
import json
import sys

try:
    import pymupdf as fitz
except ImportError:
    import fitz
from PIL import Image

BG = {"light": (246, 246, 243), "dark": (15, 18, 24)}


def lum(c):
    def f(x):
        x /= 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def hexc(c):
    return "#%02X%02X%02X" % tuple(int(round(v)) for v in c)


def adjust(c, mode, target=4.5):
    """Darken (light mode) or lighten (dark mode) in HLS until contrast >= target."""
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
    bg = BG[mode]
    for _ in range(60):
        rgb = tuple(v * 255 for v in colorsys.hls_to_rgb(h, l, s))
        if contrast(rgb, bg) >= target:
            return rgb
        l = max(0.0, l - 0.02) if mode == "light" else min(1.0, l + 0.02)
    return tuple(v * 255 for v in colorsys.hls_to_rgb(h, l, s))


def mix(c, bg, t):
    return tuple(c[i] * (1 - t) + bg[i] * t for i in range(3))


def parse_pages(spec, n):
    if not spec:
        return list(range(min(n, 6)))
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a) - 1, int(b or a)))
    return [p for p in out if 0 <= p < n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--pages")
    ap.add_argument("--mode", choices=["light", "dark"], default="light")
    a = ap.parse_args()

    doc = fitz.open(a.pdf)
    counts = {}
    for i in parse_pages(a.pages, len(doc)):
        pix = doc[i].get_pixmap(dpi=40)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        q = img.quantize(colors=24, method=Image.Quantize.MEDIANCUT).convert("RGB")
        for n, c in q.getcolors(1 << 16) or []:
            h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
            if s < 0.30 or l < 0.12 or l > 0.92:      # skip white, black, greys
                continue
            key = (round(h * 24) % 24)                 # group by hue
            prev = counts.get(key)
            if not prev or n > prev[0]:
                counts[key] = (n + (prev[0] if prev else 0), c)
            else:
                counts[key] = (prev[0] + n, prev[1])
    ranked = sorted(counts.values(), key=lambda x: -x[0])
    if not ranked:
        print(json.dumps({"colors": [], "note": "no distinctive colors found – use the modern look instead"}))
        return
    raw = [hexc(c) for _, c in ranked[:5]]
    acc = adjust(ranked[0][1], a.mode)
    acc2 = adjust(ranked[1][1], a.mode) if len(ranked) > 1 else acc
    print(json.dumps({
        "mode": a.mode,
        "colors": raw,
        "css": {"--accent": hexc(acc), "--accent2": hexc(acc2),
                "--accent-soft": hexc(mix(acc, BG[a.mode], 0.85)),
                "--glow": "rgba(%d,%d,%d,%.2f)" % (*[int(v) for v in acc], 0.16 if a.mode == "light" else 0.22),
                "--glow2": "rgba(%d,%d,%d,%.2f)" % (*[int(v) for v in acc2], 0.12 if a.mode == "light" else 0.16)},
        "contrast_on_bg": [round(contrast(acc, BG[a.mode]), 2), round(contrast(acc2, BG[a.mode]), 2)],
    }, indent=2))


if __name__ == "__main__":
    main()
