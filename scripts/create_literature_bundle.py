#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


DEFAULT_ROOT = Path("/Users/wuyue/Desktop/文献阅读总结汇报")


def safe_name(text: str) -> str:
    text = re.sub(r"[/:*?\"<>|]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:120] if text else "未命名文献"


def copy_into(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    shutil.copy2(src, dst)
    return dst


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a literature reading bundle on the desktop.")
    parser.add_argument("--pdf", required=True, type=Path, help="Path to the source PDF")
    parser.add_argument("--summary", required=True, type=Path, help="Path to the summary document")
    parser.add_argument("--pptx", required=True, type=Path, help="Path to the generated PPTX")
    parser.add_argument("--manifest", type=Path, help="Optional asset/source manifest document")
    parser.add_argument("--title", required=True, help="Paper title for naming the bundle folder")
    parser.add_argument("--root-dir", type=Path, default=DEFAULT_ROOT, help="Root output directory")
    args = parser.parse_args()

    bundle_dir = args.root_dir / safe_name(args.title)
    original_dir = bundle_dir / "1.原文献"
    summary_dir = bundle_dir / "2.文献总结"
    ppt_dir = bundle_dir / "3.文献ppt"
    source_dir = bundle_dir / "4.来源清单"

    copy_into(args.pdf, original_dir)
    copy_into(args.summary, summary_dir)
    copy_into(args.pptx, ppt_dir)
    if args.manifest and args.manifest.exists():
        copy_into(args.manifest, source_dir)

    print(bundle_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
