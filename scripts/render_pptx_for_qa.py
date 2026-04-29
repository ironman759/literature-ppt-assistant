#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PPTX_SKILL_DIR = Path("/Users/wuyue/.codex/skills/pptx/scripts")
SOFFICE_WRAPPER = PPTX_SKILL_DIR / "office" / "soffice.py"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a PPTX into PDF and slide images for visual QA.")
    parser.add_argument("--pptx", required=True, type=Path, help="Input PPTX file")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for PDF and rendered images")
    parser.add_argument("--dpi", type=int, default=150, help="Image render DPI")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = args.output_dir / f"{args.pptx.stem}.pdf"
    slide_prefix = args.output_dir / "slide"

    subprocess.run(
        [
            "python3",
            str(SOFFICE_WRAPPER),
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(args.output_dir),
            str(args.pptx),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "pdftoppm",
            "-jpeg",
            "-r",
            str(args.dpi),
            str(pdf_path),
            str(slide_prefix),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    images = sorted(args.output_dir.glob("slide-*.jpg"))
    print(pdf_path)
    for image in images:
        print(image)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
