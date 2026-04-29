#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


REQUIRED_DIRS = ["1.原文献", "2.文献总结", "3.文献ppt", "4.来源清单"]


def count_pptx_slides(path: Path) -> int:
    with zipfile.ZipFile(path) as zf:
        return len([name for name in zf.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml")])


def count_pptx_notes(path: Path) -> int:
    with zipfile.ZipFile(path) as zf:
        return len([name for name in zf.namelist() if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")])


def validate(bundle: Path, qa_dir: Path | None = None) -> dict:
    checks = []
    for dirname in REQUIRED_DIRS:
        path = bundle / dirname
        checks.append({"check": f"directory:{dirname}", "ok": path.is_dir(), "path": str(path)})

    pdfs = list((bundle / "1.原文献").glob("*.pdf"))
    summaries = list((bundle / "2.文献总结").glob("*.docx"))
    pptxs = list((bundle / "3.文献ppt").glob("*.pptx"))
    manifests = list((bundle / "4.来源清单").glob("*.docx"))
    checks.extend(
        [
            {"check": "source_pdf_present", "ok": bool(pdfs), "count": len(pdfs)},
            {"check": "summary_docx_present", "ok": bool(summaries), "count": len(summaries)},
            {"check": "pptx_present", "ok": bool(pptxs), "count": len(pptxs)},
            {"check": "manifest_docx_present", "ok": bool(manifests), "count": len(manifests)},
        ]
    )

    slide_count = None
    notes_count = None
    if pptxs:
        slide_count = count_pptx_slides(pptxs[0])
        notes_count = count_pptx_notes(pptxs[0])
        checks.append({"check": "pptx_has_slides", "ok": slide_count > 0, "count": slide_count})
        checks.append({"check": "speaker_notes_present", "ok": notes_count >= max(slide_count - 1, 0), "notes": notes_count, "slides": slide_count})

    if qa_dir:
        images = sorted(qa_dir.glob("slide-*.jpg"))
        checks.append({"check": "qa_images_present", "ok": bool(images), "count": len(images), "path": str(qa_dir)})
        if slide_count is not None:
            checks.append({"check": "qa_image_count_matches_pptx", "ok": len(images) == slide_count, "images": len(images), "slides": slide_count})

    ok = all(item["ok"] for item in checks)
    return {"ok": ok, "bundle_dir": str(bundle), "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the standard literature presentation bundle.")
    parser.add_argument("--bundle-dir", required=True, type=Path)
    parser.add_argument("--qa-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = validate(args.bundle_dir, args.qa_dir)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
