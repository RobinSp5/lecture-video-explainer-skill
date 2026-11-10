#!/usr/bin/env python3
"""Read a lecture PDF: text per page, page previews, embedded images, crops, OCR.

Usage:
  extract_pdf.py <pdf> <outdir>                       # pages.json + preview PNGs
  extract_pdf.py <pdf> <outdir> --images              # also extract embedded images
  extract_pdf.py <pdf> <outdir> --crop 12 10,20,90,85 # crop of page 12 (percent: x0,y0,x1,y1)
  extract_pdf.py <pdf> <outdir> --crop 12 full        # whole page 12 at high resolution
  extract_pdf.py <pdf> <outdir> --ocr [--ocr-lang deu+eng]  # text recognition for scanned pages

Scanned pages (almost no text, but an image) are flagged "needs_ocr". With --ocr, Tesseract
is used if installed; otherwise look at the preview images and read the text yourself.

Output:
  <outdir>/pages.json          metadata + text per page
  <outdir>/preview/p012.png    preview of every page (for looking at, not for the video)
  <outdir>/images/p012_1.png   embedded images (with --images, above a minimum size)
  <outdir>/crops/p012_crop.png crops in video quality (--crop)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    import pymupdf as fitz  # PyMuPDF >= 1.24
except ImportError:
    try:
        import fitz
    except ImportError:
        sys.exit("PyMuPDF missing: pip install pymupdf --break-system-packages")

FILLER_PATTERNS = re.compile(
    r"^\s*(agenda|inhalt|inhaltsverzeichnis|gliederung|literatur|quellen|references|"
    r"fragen\??|vielen dank|danke|thank you|questions\??|outline)\b",
    re.IGNORECASE | re.MULTILINE,
)
EXERCISE_PATTERNS = re.compile(
    r"(übungsblatt|übung\b|\baufgabe\s*\d|\baufgaben\b|tutorium|hausaufgabe|exercise|\btask\s*\d|assignment|problem set|"
    r"lösungsvorschlag|musterlösung|solution sheet|berechnen sie|bestimmen sie|erstellen sie|skizzieren sie|"
    r"calculate|determine|write a query|formulieren sie)", re.IGNORECASE)
SOLUTION_PATTERNS = re.compile(r"(lösung|musterlösung|lösungsvorschlag|solution)", re.IGNORECASE)
QUESTION_LINE = re.compile(r"\?\s*$")
NOT_A_QUESTION = re.compile(r"^\s*(fragen|questions|noch fragen|any questions)\s*\??\s*$", re.IGNORECASE)
DISCUSSION = re.compile(r"^\s*(diskussion|diskutieren sie|frage an sie|think about|discuss|reflexion|was meinen sie)", re.IGNORECASE)


def find_questions(text):
    """Questions on a slide; lines wrapped across the slide are joined back together."""
    out, buf, title_seen = [], [], False
    for line in (l.strip() for l in text.splitlines()):
        if not line:
            buf = []
            continue
        if not title_seen:            # the slide title never belongs to a question below it
            title_seen = True
            if not QUESTION_LINE.search(line):
                continue
        if NOT_A_QUESTION.match(line):
            buf = []
            continue
        if QUESTION_LINE.search(line):
            full = " ".join(buf[-2:] + [line]) if buf else line
            if len(full) >= 12:
                out.append(full[:200])
            buf = []
        elif DISCUSSION.match(line):
            out.append(line[:200])
            buf = []
        else:
            buf = [] if re.search(r"[.!:;]$", line) or line.startswith(("•", "-", "–")) else buf + [line]
    return out


SUMMARY_PATTERNS = re.compile(
    r"(zusammenfassung|fazit|summary|key takeaways|wrap[- ]?up|das wichtigste)", re.IGNORECASE
)
EXAM_PATTERNS = re.compile(
    r"(klausur|prüfung|merke|wichtig!|lernziel|\bexams?\b|key point|important!|learning objective|must know)",
    re.IGNORECASE)


def page_info(doc, i):
    page = doc[i]
    text = page.get_text("text").strip()
    words = len(re.findall(r"\w+", text))
    first_line = next((l.strip() for l in text.splitlines() if l.strip()), "")
    imgs = page.get_images(full=True)
    drawings = len(page.get_drawings())
    return {
        "page": i + 1,
        "title_guess": first_line[:120],
        "words": words,
        "embedded_images": len(imgs),
        "vector_drawings": drawings,
        "likely_graphic": len(imgs) > 0 or drawings > 25,
        "filler_guess": bool(FILLER_PATTERNS.search(first_line))
                        or (words < 8 and not SUMMARY_PATTERNS.search(first_line)),
        "summary_guess": bool(SUMMARY_PATTERNS.search(first_line)),
        "exam_hint": bool(EXAM_PATTERNS.search(text)),
        "exercise_hint": bool(EXERCISE_PATTERNS.search(text)),
        "solution_hint": bool(SOLUTION_PATTERNS.search(first_line)),
        "needs_ocr": words < 8 and len(imgs) > 0,
        "questions": find_questions(text),
        "text": text,
    }


def tesseract_langs():
    if not shutil.which("tesseract"):
        return None
    out = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True)
    return {l.strip() for l in out.stdout.splitlines()[1:] if l.strip()}


def run_ocr(doc, pages, want_lang, dpi=300):
    langs = tesseract_langs()
    if langs is None:
        print("OCR: Tesseract not installed (apt install tesseract-ocr tesseract-ocr-deu). "
              "Instead, look at the preview images of the flagged pages and read the text yourself.")
        return
    use = [l for l in want_lang.split("+") if l in langs]
    missing = [l for l in want_lang.split("+") if l not in langs]
    if missing:
        print(f"OCR: language pack(s) missing: {', '.join(missing)} (apt install tesseract-ocr-<code>). "
              f"Recognition without them is unreliable for umlauts/technical terms – proofread the result.")
    if not use:
        use = ["eng"] if "eng" in langs else sorted(langs - {"osd"})[:1]
    targets = [p for p in pages if p["needs_ocr"]]
    with tempfile.TemporaryDirectory() as tmp:
        for p in targets:
            img = os.path.join(tmp, f"p{p['page']}.png")
            doc[p["page"] - 1].get_pixmap(dpi=dpi).save(img)
            r = subprocess.run(["tesseract", img, "-", "-l", "+".join(use), "--psm", "3"],
                               capture_output=True, text=True)
            p["ocr_text"] = r.stdout.strip()
            p["ocr_lang"] = "+".join(use)
            if p["ocr_text"]:
                p["text"] = p["ocr_text"]
                p["words"] = len(re.findall(r"\w+", p["text"]))
                first = next((l.strip() for l in p["text"].splitlines() if l.strip()), "")
                p["title_guess"] = first[:120]
                p["questions"] = find_questions(p["text"])
                p["filler_guess"] = bool(FILLER_PATTERNS.search(first)) or (
                    p["words"] < 8 and not SUMMARY_PATTERNS.search(first))
    print(f"OCR: recognized {len(targets)} page(s) with {'+'.join(use)}")


def render_previews(doc, outdir, dpi):
    d = os.path.join(outdir, "preview")
    os.makedirs(d, exist_ok=True)
    for i, page in enumerate(doc):
        page.get_pixmap(dpi=dpi).save(os.path.join(d, f"p{i+1:03d}.png"))


def extract_images(doc, outdir, min_px):
    d = os.path.join(outdir, "images")
    os.makedirs(d, exist_ok=True)
    out = []
    seen = set()
    for i, page in enumerate(doc):
        for n, img in enumerate(page.get_images(full=True), 1):
            xref = img[0]
            if xref in seen:
                continue  # logos etc. repeat on every slide
            seen.add(xref)
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.width < min_px or pix.height < min_px:
                    continue
                if pix.n - pix.alpha >= 4:  # CMYK -> RGB
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                path = os.path.join(d, f"p{i+1:03d}_{n}.png")
                pix.save(path)
                out.append({"page": i + 1, "file": path, "width": pix.width, "height": pix.height})
            except Exception as e:  # skip broken images
                print(f"Skipped image xref {xref} on page {i+1}: {e}", file=sys.stderr)
    return out


def crop(doc, outdir, page_no, box, dpi):
    d = os.path.join(outdir, "crops")
    os.makedirs(d, exist_ok=True)
    page = doc[page_no - 1]
    r = page.rect
    if box == "full":
        clip = r
        suffix = "full"
    else:
        x0, y0, x1, y1 = [float(v) / 100 for v in box.split(",")]
        clip = fitz.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height,
                         r.x0 + x1 * r.width, r.y0 + y1 * r.height)
        suffix = "crop_" + box.replace(",", "-").replace(".", "_")
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    path = os.path.join(d, f"p{page_no:03d}_{suffix}.png")
    pix.save(path)
    print(json.dumps({"file": path, "width": pix.width, "height": pix.height}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("outdir")
    ap.add_argument("--images", action="store_true", help="extract embedded images")
    ap.add_argument("--min-px", type=int, default=200, help="minimum edge length for images")
    ap.add_argument("--preview-dpi", type=int, default=80)
    ap.add_argument("--crop", nargs=2, metavar=("SEITE", "BOX"))
    ap.add_argument("--crop-dpi", type=int, default=250)
    ap.add_argument("--ocr", action="store_true", help="recognize scanned pages with Tesseract")
    ap.add_argument("--ocr-lang", default="deu+eng")
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    doc = fitz.open(a.pdf)

    if a.crop:
        crop(doc, a.outdir, int(a.crop[0]), a.crop[1], a.crop_dpi)
        return

    pages = [page_info(doc, i) for i in range(len(doc))]
    if a.ocr:
        run_ocr(doc, pages, a.ocr_lang)
    content = [p for p in pages if not p["filler_guess"]]
    meta = doc.metadata or {}
    result = {
        "file": os.path.abspath(a.pdf),
        "pdf_title": meta.get("title") or "",
        "pdf_author": meta.get("author") or "",
        "page_count": len(pages),
        "content_pages": len(content),
        "total_words": sum(p["words"] for p in pages),
        "summary_pages": [p["page"] for p in pages if p["summary_guess"]],
        "exam_hint_pages": [p["page"] for p in pages if p["exam_hint"]],
        "exercise_pages": [p["page"] for p in pages if p["exercise_hint"]],
        "question_pages": [p["page"] for p in pages if p["questions"]],
        "solution_pages": [p["page"] for p in pages if p["solution_hint"]],
        "exercise_guess": sum(p["exercise_hint"] for p in pages) >= max(1, len(pages) // 3),
        "graphic_pages": [p["page"] for p in pages if p["likely_graphic"]],
        "needs_ocr_pages": [p["page"] for p in pages if p["needs_ocr"] and not p.get("ocr_text")],
        "pages": pages,
    }
    render_previews(doc, a.outdir, a.preview_dpi)
    if a.images:
        result["images"] = extract_images(doc, a.outdir, a.min_px)

    with open(os.path.join(a.outdir, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Pages: {result['page_count']} (content ~{result['content_pages']}), "
          f"words: {result['total_words']}")
    print(f"Summary probably on: {result['summary_pages'] or '-'}")
    print(f"Graphic pages: {result['graphic_pages'] or '-'}")
    print(f"Exam hints on: {result['exam_hint_pages'] or '-'}")
    print(f"Open questions to answer on pages: {result['question_pages'] or '-'}")
    print(f"Exercise: {'LIKELY' if result['exercise_guess'] else 'no'} (task pages: {result['exercise_pages'] or '-'}, "
          f"solution pages: {result['solution_pages'] or '-'})")
    if result["needs_ocr_pages"]:
        print(f"SCANNED/no text: {result['needs_ocr_pages']} -> use --ocr or read the preview images")
    if a.images:
        print(f"Images extracted: {len(result['images'])}")
    print(f"-> {os.path.join(a.outdir, 'pages.json')}")


if __name__ == "__main__":
    main()
