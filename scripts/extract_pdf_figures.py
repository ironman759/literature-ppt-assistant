#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz


def union_rect(rects: list[fitz.Rect]) -> fitz.Rect | None:
    if not rects:
        return None
    rect = fitz.Rect(rects[0])
    for other in rects[1:]:
        rect |= other
    return rect


def expand_clip(rect: fitz.Rect, page_rect: fitz.Rect, pad: float = 12) -> fitz.Rect:
    clip = fitz.Rect(rect)
    clip.x0 = max(page_rect.x0 + 8, clip.x0 - pad)
    clip.y0 = max(page_rect.y0 + 8, clip.y0 - pad)
    clip.x1 = min(page_rect.x1 - 8, clip.x1 + pad)
    clip.y1 = min(page_rect.y1 - 8, clip.y1 + pad)
    return clip


def image_union_clip(doc: fitz.Document, page: fitz.Page) -> fitz.Rect | None:
    rects: list[fitz.Rect] = []
    for img in page.get_images(full=True):
        xref = img[0]
        for rect in page.get_image_rects(xref):
            if rect.width >= 45 and rect.height >= 35:
                rects.append(rect)
    union = union_rect(rects)
    return expand_clip(union, page.rect) if union else None


def caption_based_clip(page: fitz.Page) -> fitz.Rect | None:
    caption_rect: fitz.Rect | None = None
    for block in page.get_text("blocks"):
        x0, y0, x1, y1, text, *_ = block
        flat = " ".join(text.split())
        if re.match(r"Figure\s+\d+", flat):
            caption_rect = fitz.Rect(x0, y0, x1, y1)
            break
    if not caption_rect:
        return None

    clip = fitz.Rect(page.rect.x0 + 30, page.rect.y0 + 30, page.rect.x1 - 30, caption_rect.y1 + 5)
    return expand_clip(clip, page.rect, pad=0)


def render_clip(page: fitz.Page, clip: fitz.Rect, out: Path) -> tuple[int, int]:
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip, alpha=False)
    pix.save(out)
    return pix.width, pix.height


def extract_figures(
    pdf_path: Path, output_dir: Path, min_width: int, min_height: int, render_fallback: bool
) -> list[dict[str, object]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    saved: list[dict[str, object]] = []
    pages_with_images: list[int] = []
    pages_with_captions: list[int] = []

    try:
        for page_index, page in enumerate(doc, start=1):
            page_images = page.get_images(full=True)
            if page_images:
                pages_with_images.append(page_index)

            has_caption = any(
                re.match(r"Figure\s+\d+", " ".join(block[4].split()))
                for block in page.get_text("blocks")
            )
            if has_caption:
                pages_with_captions.append(page_index)

            for image_index, img in enumerate(page_images, start=1):
                xref = img[0]
                base = doc.extract_image(xref)
                width = int(base.get("width", 0))
                height = int(base.get("height", 0))
                if width < min_width or height < min_height:
                    continue

                ext = base.get("ext", "png")
                out = output_dir / f"page_{page_index:02d}_img_{image_index:02d}.{ext}"
                out.write_bytes(base["image"])
                saved.append(
                    {
                        "page": page_index,
                        "image_index": image_index,
                        "path": str(out),
                        "width": width,
                        "height": height,
                    }
                )

        if render_fallback and not saved:
            candidate_pages = sorted(set(pages_with_images + pages_with_captions))
            for page_index in candidate_pages:
                page = doc[page_index - 1]
                clip = image_union_clip(doc, page) or caption_based_clip(page)
                if clip is None:
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    out = output_dir / f"page_{page_index:02d}_render.png"
                    pix.save(out)
                    width, height = pix.width, pix.height
                    mode = "page_render"
                else:
                    out = output_dir / f"page_{page_index:02d}_figure_crop.png"
                    width, height = render_clip(page, clip, out)
                    mode = "figure_crop"
                saved.append(
                    {
                        "page": page_index,
                        "image_index": 0,
                        "path": str(out),
                        "width": width,
                        "height": height,
                        "mode": mode,
                    }
                )
    finally:
        doc.close()

    manifest = output_dir / "figures_manifest.json"
    manifest.write_text(json.dumps(saved, ensure_ascii=False, indent=2), encoding="utf-8")
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract usable embedded figures from a PDF.")
    parser.add_argument("--pdf", required=True, type=Path, help="Source PDF path")
    parser.add_argument("--output-dir", required=True, type=Path, help="Output directory for extracted figures")
    parser.add_argument("--min-width", type=int, default=500, help="Minimum image width")
    parser.add_argument("--min-height", type=int, default=300, help="Minimum image height")
    parser.add_argument(
        "--render-fallback",
        action="store_true",
        help="If no usable embedded figures are found, render pages containing figures as PNGs",
    )
    args = parser.parse_args()

    saved = extract_figures(
        args.pdf, args.output_dir, args.min_width, args.min_height, args.render_fallback
    )
    print(json.dumps({"count": len(saved), "output_dir": str(args.output_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
