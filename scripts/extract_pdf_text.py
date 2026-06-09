#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import fitz
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency: PyMuPDF. Install it with `pip install pymupdf`."
    ) from exc


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def guess_title(lines: list[str]) -> str:
    title_zone: list[str] = []
    for line in lines[:25]:
        lowered = line.lower()
        if lowered == "abstract":
            break
        title_zone.append(line)

    for line in title_zone:
        if 8 <= len(line) <= 220:
            return line

    candidates: list[str] = []
    for line in lines[:25]:
        lowered = line.lower()
        if len(line) < 8:
            continue
        if lowered in {"abstract", "introduction", "keywords"}:
            continue
        candidates.append(line)
    return max(candidates, key=len) if candidates else (lines[0] if lines else "未识别标题")


def clean_metadata_title(title: str | None) -> str:
    if not title:
        return ""
    title = re.sub(r"\s+", " ", title).strip()
    lowered = title.lower()
    noisy = ["untitled", "springer", "article", "nature microbiology"]
    if not title or lowered in noisy:
        return ""
    if len(title) < 8:
        return ""
    return title


def extract_abstract(text: str, max_chars: int = 1800) -> str:
    lower_text = text.lower()
    match = re.search(r"\babstract\b", lower_text)
    if not match:
        return text[:max_chars].strip()

    start = match.end()
    snippet = text[start : start + max_chars]
    end_markers = ["introduction", "1.", "keywords", "index terms"]
    end_positions = [
        pos for marker in end_markers if (pos := snippet.lower().find(marker)) != -1
    ]
    end = min(end_positions) if end_positions else len(snippet)
    return snippet[:end].strip()


def extract_pdf(path: Path, max_chars: int) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    doc = fitz.open(path)
    pages: list[dict[str, object]] = []
    all_text: list[str] = []
    lines: list[str] = []
    metadata_title = clean_metadata_title(doc.metadata.get("title") if doc.metadata else "")

    try:
        for page_index, page in enumerate(doc, start=1):
            text = normalize_text(page.get_text("text"))
            pages.append(
                {
                    "page_no": page_index,
                    "char_count": len(text),
                    "text": text,
                }
            )
            if text:
                all_text.append(text)
                lines.extend([line.strip() for line in text.splitlines() if line.strip()])
    finally:
        doc.close()

    combined = "\n\n".join(all_text)
    excerpt = combined[:max_chars]

    return {
        "file": str(path),
        "page_count": len(pages),
        "title_guess": metadata_title or guess_title(lines),
        "abstract_snippet": extract_abstract(combined),
        "text_excerpt": excerpt,
        "pages": pages,
        "extraction_path": "pymupdf",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract text from an academic PDF.")
    parser.add_argument("pdf", type=Path, help="Absolute or relative path to the PDF file")
    parser.add_argument("--max-chars", type=int, default=25000, help="Max chars in text_excerpt")
    args = parser.parse_args()

    result = extract_pdf(args.pdf, args.max_chars)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
