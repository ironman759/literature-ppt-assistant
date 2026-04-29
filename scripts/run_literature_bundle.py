#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = Path("/Users/wuyue/Desktop/文献阅读总结汇报")


def run(args: list[str], *, allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode and not allow_fail:
        raise SystemExit(
            "Command failed:\n"
            + " ".join(args)
            + "\n\nSTDOUT:\n"
            + proc.stdout
            + "\nSTDERR:\n"
            + proc.stderr
        )
    return proc


def safe_name(text: str) -> str:
    import re

    text = re.sub(r"[/:*?\"<>|]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:120] if text else "未命名文献"


def load_title(extract_json: Path, fallback: str | None) -> str:
    if fallback:
        return fallback
    data = json.loads(extract_json.read_text(encoding="utf-8"))
    return str(data.get("title_guess") or "未命名文献")


def write_minimal_manifest(path: Path, pdf: Path, figures_dir: Path | None) -> None:
    items = [
        {
            "source_type": "source_pdf",
            "title": pdf.stem,
            "url": "",
            "license_or_note": "Original user-provided paper PDF.",
            "local_path": str(pdf),
            "used_for_slide": "whole deck reference",
        }
    ]
    if figures_dir and figures_dir.exists():
        for image in sorted(figures_dir.glob("*.png"))[:30]:
            items.append(
                {
                    "source_type": "paper_figure",
                    "title": image.stem,
                    "url": "",
                    "license_or_note": "Figure crop/render extracted from the source PDF.",
                    "local_path": str(image),
                    "used_for_slide": "",
                }
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def prepare(args: argparse.Namespace) -> dict:
    work_dir = args.work_dir or (args.root_dir / "_work" / safe_name(args.pdf.stem))
    work_dir.mkdir(parents=True, exist_ok=True)

    extract_json = work_dir / "paper_extract.json"
    sections_json = work_dir / "paper_sections.json"
    figures_dir = work_dir / "figures"
    tokens_json = work_dir / "design_tokens.json"
    manifest_json = args.manifest_json or (work_dir / "asset_sources.json")

    extract = run([sys.executable, str(SCRIPT_DIR / "extract_pdf_text.py"), str(args.pdf), "--max-chars", str(args.max_chars)])
    extract_json.write_text(extract.stdout, encoding="utf-8")

    run([sys.executable, str(SCRIPT_DIR / "analyze_paper_sections.py"), "--input", str(extract_json), "--output", str(sections_json)])
    run([sys.executable, str(SCRIPT_DIR / "generate_design_tokens.py"), "--scenario", args.scenario, "--output", str(tokens_json)])
    run([sys.executable, str(SCRIPT_DIR / "extract_pdf_figures.py"), "--pdf", str(args.pdf), "--output-dir", str(figures_dir), "--render-fallback"], allow_fail=True)

    reference_profile = None
    if args.reference_pptx:
        reference_profile = work_dir / "reference_style_profile.json"
        run([sys.executable, str(SCRIPT_DIR / "profile_reference_ppt.py"), "--pptx", str(args.reference_pptx), "--output", str(reference_profile)])

    if not manifest_json.exists():
        write_minimal_manifest(manifest_json, args.pdf, figures_dir)

    state = {
        "work_dir": str(work_dir),
        "pdf": str(args.pdf),
        "extract_json": str(extract_json),
        "sections_json": str(sections_json),
        "figures_dir": str(figures_dir),
        "design_tokens_json": str(tokens_json),
        "manifest_json": str(manifest_json),
        "reference_profile_json": str(reference_profile) if reference_profile else "",
        "next_step": "Use these artifacts to draft summary.md and slide_spec.json, then rerun with --summary-md and --spec.",
    }
    (work_dir / "run_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def build(args: argparse.Namespace, state: dict) -> dict:
    if not args.summary_md or not args.spec:
        return state

    work_dir = Path(state["work_dir"])
    title = load_title(Path(state["extract_json"]), args.title)
    out_dir = work_dir / "outputs"
    summary_docx = out_dir / "summary.docx"
    pptx = out_dir / "presentation.pptx"
    manifest_docx = out_dir / "asset_sources.docx"
    qa_dir = out_dir / "qa_renders"

    run([sys.executable, str(SCRIPT_DIR / "write_summary_docx.py"), "--input", str(args.summary_md), "--output", str(summary_docx), "--title", title])
    run([sys.executable, str(SCRIPT_DIR / "build_presentation_from_spec.py"), "--spec", str(args.spec), "--output", str(pptx)])
    run([sys.executable, str(SCRIPT_DIR / "write_sources_docx.py"), "--input", state["manifest_json"], "--output", str(manifest_docx), "--title", "来源清单"])
    run([sys.executable, str(SCRIPT_DIR / "render_pptx_for_qa.py"), "--pptx", str(pptx), "--output-dir", str(qa_dir)], allow_fail=args.allow_qa_fail)

    bundle_proc = run(
        [
            sys.executable,
            str(SCRIPT_DIR / "create_literature_bundle.py"),
            "--pdf",
            str(args.pdf),
            "--summary",
            str(summary_docx),
            "--pptx",
            str(pptx),
            "--manifest",
            str(manifest_docx),
            "--title",
            title,
            "--root-dir",
            str(args.root_dir),
        ]
    )
    bundle_dir = Path(bundle_proc.stdout.strip().splitlines()[-1])
    bundle_qa = bundle_dir / "qa_renders"
    if qa_dir.exists():
        if bundle_qa.exists():
            shutil.rmtree(bundle_qa)
        shutil.copytree(qa_dir, bundle_qa)

    validation_json = bundle_dir / "validation_report.json"
    validation = run(
        [
            sys.executable,
            str(SCRIPT_DIR / "validate_literature_bundle.py"),
            "--bundle-dir",
            str(bundle_dir),
            "--qa-dir",
            str(bundle_qa),
            "--output",
            str(validation_json),
        ],
        allow_fail=True,
    )

    state.update(
        {
            "summary_docx": str(summary_docx),
            "pptx": str(pptx),
            "manifest_docx": str(manifest_docx),
            "qa_dir": str(qa_dir),
            "bundle_dir": str(bundle_dir),
            "validation_json": str(validation_json),
            "validation_stdout": validation.stdout,
            "validation_returncode": validation.returncode,
        }
    )
    (work_dir / "run_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and build a literature presentation bundle.")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--summary-md", type=Path, help="Agent-authored summary markdown/plain text")
    parser.add_argument("--spec", type=Path, help="Agent-authored slide spec JSON")
    parser.add_argument("--manifest-json", type=Path, help="Optional asset/source manifest JSON")
    parser.add_argument("--reference-pptx", type=Path, help="Optional reference deck to profile")
    parser.add_argument("--scenario", choices=["lab_meeting", "course_report", "proposal_defense"], default="lab_meeting")
    parser.add_argument("--title", help="Override bundle title")
    parser.add_argument("--root-dir", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--max-chars", type=int, default=50000)
    parser.add_argument("--allow-qa-fail", action="store_true", help="Continue if LibreOffice/pdftoppm QA rendering fails")
    args = parser.parse_args()

    state = prepare(args)
    state = build(args, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
