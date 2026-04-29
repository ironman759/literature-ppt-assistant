#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SECTION_PATTERNS = [
    ("abstract", r"^\s*abstract\s*$"),
    ("introduction", r"^\s*(?:\d+\.?\s*)?introduction\s*$"),
    ("methods", r"^\s*(?:\d+\.?\s*)?(?:materials and methods|methods|methodology|experimental procedures)\s*$"),
    ("results", r"^\s*(?:\d+\.?\s*)?results\s*$"),
    ("discussion", r"^\s*(?:\d+\.?\s*)?discussion\s*$"),
    ("limitations", r"^\s*(?:\d+\.?\s*)?limitations?\s*$"),
    ("conclusion", r"^\s*(?:\d+\.?\s*)?(?:conclusions?|summary)\s*$"),
    ("references", r"^\s*(?:references|bibliography)\s*$"),
]


def load_extraction(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "pages" not in data:
        raise ValueError("Expected extract_pdf_text.py JSON with a 'pages' field")
    return data


def find_heading(line: str) -> str | None:
    clean = re.sub(r"\s+", " ", line.strip())
    for name, pattern in SECTION_PATTERNS:
        if re.match(pattern, clean, flags=re.IGNORECASE):
            return name
    return None


def add_snippet(sections: dict, section: str, page_no: int, text: str) -> None:
    if section == "references":
        return
    item = sections.setdefault(
        section,
        {"pages": [], "char_count": 0, "snippets": [], "status": "found"},
    )
    if page_no not in item["pages"]:
        item["pages"].append(page_no)
    item["char_count"] += len(text)
    if len(item["snippets"]) < 4:
        snippet = re.sub(r"\s+", " ", text).strip()
        if snippet:
            item["snippets"].append(snippet[:700])


def analyze(data: dict) -> dict:
    sections: dict[str, dict] = {}
    current = "front_matter"

    for page in data.get("pages", []):
        page_no = int(page.get("page_no", 0))
        text = str(page.get("text", ""))
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        for para in paragraphs:
            lines = [line.strip() for line in para.splitlines() if line.strip()]
            if len(lines) == 1:
                heading = find_heading(lines[0])
                if heading:
                    current = heading
                    sections.setdefault(
                        current,
                        {"pages": [], "char_count": 0, "snippets": [], "status": "found"},
                    )
                    continue
            add_snippet(sections, current, page_no, para)

    expected = ["abstract", "introduction", "methods", "results", "discussion", "limitations", "conclusion"]
    for name in expected:
        sections.setdefault(name, {"pages": [], "char_count": 0, "snippets": [], "status": "not_detected"})

    return {
        "file": data.get("file"),
        "title_guess": data.get("title_guess"),
        "page_count": data.get("page_count"),
        "sections": sections,
        "usage_note": "Use snippets as navigation evidence only; verify final claims against the PDF text before presenting.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a section-aware map from extract_pdf_text.py JSON.")
    parser.add_argument("--input", required=True, type=Path, help="Extraction JSON")
    parser.add_argument("--output", required=True, type=Path, help="Output section map JSON")
    args = parser.parse_args()

    payload = analyze(load_extraction(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
