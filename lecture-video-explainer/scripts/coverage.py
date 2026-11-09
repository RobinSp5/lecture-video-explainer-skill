#!/usr/bin/env python3
"""Coverage check: unanswered open questions from the slides, and content pages no scene cites.

  coverage.py script.json pages.json

Open questions (pages.json "questions", from extract_pdf.py) must be answered by a scene with
"answers_questions": [page] – for every video type. Page coverage matters for a comprehensive summary.

Compares every scene's "source" (page numbers or ranges like "12-14") with the content pages in
pages.json (from extract_pdf.py; filler pages such as title/agenda are ignored) and with
meta.skipped_pages in script.json (pages deliberately left out, each with a reason).
Exit code 1 if pages are uncovered.
"""
import json
import re
import sys


def pages_in(src):
    out = set()
    items = src if isinstance(src, list) else [src]
    for it in items:
        for a, b in re.findall(r"(\d+)\s*(?:[-–]\s*(\d+))?", str(it)):
            out.update(range(int(a), int(b or a) + 1))
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    script = json.load(open(sys.argv[1], encoding="utf-8"))
    pages = json.load(open(sys.argv[2], encoding="utf-8"))
    content = {p["page"] for p in pages["pages"] if not p.get("filler_guess")}
    cited = set()
    for sc in script.get("scenes", []):
        cited |= pages_in(sc.get("source", []))
    skipped = {int(k) for k in (script.get("meta", {}).get("skipped_pages") or {})}
    missing = sorted(content - cited - skipped)
    answered = set()
    for sc in script.get("scenes", []):
        answered |= pages_in(sc.get("answers_questions", []))
    q_pages = {p["page"]: p.get("questions", []) for p in pages["pages"] if p.get("questions")}
    unanswered = {str(pg): qs for pg, qs in sorted(q_pages.items()) if pg not in answered}
    comprehensive = script.get("meta", {}).get("video_type", "comprehensive") == "comprehensive"
    print(json.dumps({
        "open_questions_unanswered": unanswered,
        "content_pages": len(content),
        "covered": len(content & cited),
        "skipped_with_reason": sorted(skipped & content),
        "uncovered": missing,
        "coverage_pct": round(100 * len(content & (cited | skipped)) / max(1, len(content)), 1),
    }, indent=2))
    sys.exit(1 if unanswered or (missing and comprehensive) else 0)


if __name__ == "__main__":
    main()
