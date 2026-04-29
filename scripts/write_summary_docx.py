#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document
from docx.shared import Pt


def write_docx(md_text: str, output: Path, title: str | None = None) -> None:
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    if title:
        doc.add_heading(title, level=0)

    lines = md_text.splitlines()
    current_list = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            current_list = False
            continue

        if stripped.startswith("# "):
            doc.add_heading(stripped[2:].strip(), level=1)
            current_list = False
            continue
        if stripped.startswith("## "):
            doc.add_heading(stripped[3:].strip(), level=2)
            current_list = False
            continue
        if stripped.startswith("### "):
            doc.add_heading(stripped[4:].strip(), level=3)
            current_list = False
            continue
        if stripped.startswith("- "):
            doc.add_paragraph(stripped[2:].strip(), style="List Bullet")
            current_list = True
            continue
        if stripped[:2].isdigit() and stripped[1:3] == ". ":
            doc.add_paragraph(stripped[3:].strip(), style="List Number")
            current_list = True
            continue

        p = doc.add_paragraph()
        p.add_run(stripped)
        current_list = False

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert markdown-like summary text into a Word document.")
    parser.add_argument("--input", required=True, type=Path, help="Input markdown/plain text file")
    parser.add_argument("--output", required=True, type=Path, help="Output .docx file")
    parser.add_argument("--title", help="Optional document title")
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8")
    write_docx(text, args.output, args.title)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
