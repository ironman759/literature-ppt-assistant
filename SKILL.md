---
name: literature-ppt-assistant
description: Use when Codex is given an academic paper PDF, reference PPT, or local paper path and the user wants a literature summary, group-meeting deck, journal-club slides, course report, proposal-defense material, PPT outline, speaker notes, or a complete presentation bundle.
---

# Literature PPT Assistant

Turn a paper PDF into a presentation-ready literature bundle. Stay faithful to the source, expose uncertainty, and optimize for oral delivery rather than generic summarization.

## Tool Boundary

- `pdf`: base layer for reading, extracting, OCR/repair, and page-level inspection.
- `literature-ppt-assistant`: orchestration layer for paper analysis, outline, slide spec, notes, bundle structure, source manifest, and delivery QA.
- `pptx` / `docx`: file execution layers for final Office artifacts.
- Local scripts: deterministic execution layer for extraction, PPTX generation, manifest conversion, rendering, and validation.
- MCP/web tools: use only when the user allows external search or when a DOI/page/repo must be fetched; do not browse by default for a local PDF.

## Default Output

Unless the user asks for only one artifact, create a paper folder under:

`/Users/wuyue/Desktop/文献阅读总结汇报`

The bundle must contain:

1. `1.原文献` - copied source PDF
2. `2.文献总结` - summary `.docx`
3. `3.文献ppt` - presentation `.pptx`
4. `4.来源清单` - source/image manifest `.docx`

For research-workspace tasks with lasting value, also route or copy final artifacts into the relevant project area, normally `30 Projects/<项目名>/exports/` or `10 Research/`, then use the workspace closeout flow when appropriate.

## Workflow

1. Identify the PDF. If absent, ask for it.
2. If a reference PPT exists, keep it available for style profiling.
3. Prepare deterministic artifacts with the managed runtime:

```bash
python3 /Users/wuyue/.codex/skills/literature-ppt-assistant/scripts/literature_runtime.py \
  /Users/wuyue/.codex/skills/literature-ppt-assistant/scripts/run_literature_bundle.py \
  --pdf "/absolute/path/to/paper.pdf" \
  --scenario lab_meeting
```

This creates a work folder containing:

- `paper_extract.json`
- `paper_sections.json`
- `figures/`
- `design_tokens.json`
- `asset_sources.json`
- optional `reference_style_profile.json`
- `run_state.json`

4. Use those artifacts to draft:

- `summary.md`
- `slide_spec.json`

5. Build and validate the final bundle:

```bash
python3 /Users/wuyue/.codex/skills/literature-ppt-assistant/scripts/literature_runtime.py \
  /Users/wuyue/.codex/skills/literature-ppt-assistant/scripts/run_literature_bundle.py \
  --pdf "/absolute/path/to/paper.pdf" \
  --summary-md "/absolute/path/to/summary.md" \
  --spec "/absolute/path/to/slide_spec.json" \
  --scenario lab_meeting
```

Use `--reference-pptx "/absolute/path/to/reference.pptx"` when a sample deck is provided. Use `--title` when the extracted title is noisy.

## Scenario Defaults

- `lab_meeting`: emphasize motivation, gap, method novelty, evidence strength, limitations, and relevance to the lab.
- `course_report`: emphasize background, problem definition, method logic, result interpretation, and teaching clarity.
- `proposal_defense`: emphasize pain point, prior-work gap, methodological borrowing, extension plan, and likely challenges.

If the scenario is not stated, assume `lab_meeting` and say so briefly.

## Language Rules

- Chat responses follow the user's language by default.
- PPT text and speaker notes follow the paper's main language by default.
- If the user wants a Chinese talk from an English paper, use Chinese slide text with original English terms preserved where useful.
- Speaker notes should be in the same language as the PPT unless the user requests otherwise.
- The written summary keeps the user's preferred language unless explicitly changed.

## Analysis Rules

- Do not stop at the abstract. Use `paper_sections.json` to cover methods, results, discussion, limitations, and conclusion when present.
- Ground important claims with page numbers or section snippets when possible.
- Mark uncertain content as `文中未明确说明` or `根据当前提取内容无法确认`.
- Do not invent datasets, metrics, author claims, clinical meaning, or experimental conclusions.
- If extraction is noisy, inspect the PDF with `pdf` tooling or page renders before making claims.

## Slide Planning

Do not force a fixed deck length. Choose slide count by paper complexity:

- short/simple paper: 8-10 slides
- standard experimental paper: 10-16 slides
- dense methods/results or review-heavy report: 14-20 slides

Prioritize this narrative: background -> gap -> objective -> design/method -> results -> limitations -> implications.

Use assertion-style titles where helpful. Every slide in `slide_spec.json` should include `slide_purpose` and `notes`.

For the full slide spec schema and layout fields, read [references/slide_spec_schema.md](references/slide_spec_schema.md).

## Reference PPT Handling

When the user gives a reference PPT:

1. Run the quick workflow with `--reference-pptx`.
2. Read `reference_style_profile.json`.
3. Match slide count, text density, title rhythm, note depth, and dominant visual style when scientifically appropriate.
4. Do not blindly copy the reference if it would weaken the paper's logic.

## Image and Source Manifest

Image priority:

1. figures extracted from the source PDF
2. user-provided reference images
3. web-sourced scientific illustrations only when the user allows external search
4. generated explanatory bitmap only when no suitable source exists and generation is useful

All images used in the PPT must be represented in `asset_sources.json`, then converted to `4.来源清单/asset_sources.docx` by the runner.

Manifest items should include:

- `source_type`
- `title`
- `url`
- `license_or_note`
- `local_path`
- `used_for_slide`

## Done Check

Treat the task as done only when:

- the four bundle folders exist
- original PDF, summary `.docx`, PPTX, and source manifest `.docx` are present
- PPTX renders to QA images unless the user accepts a render failure
- slide count and QA image count match
- speaker notes exist for content slides
- source or generated images are traceable
- summary and slides remain faithful to the paper

The runner writes `validation_report.json` when the bundle is built. Inspect it before claiming completion.

## Fallback / Failure Handling

- If dependencies are missing, run through `scripts/literature_runtime.py`; it creates a managed runtime under `~/.cache/codex-skill-runtimes/literature-ppt-assistant/`.
- If `extract_pdf_text.py` fails, use the `pdf` skill for OCR/repair or page rendering, then retry.
- If figure extraction produces unreadable crops, use page renders or skip the figure rather than inserting noise.
- If LibreOffice rendering fails but the PPTX is otherwise generated, report that QA rendering failed and include the failure state.
- If a generated title is bad, rebuild with `--title`.

## Research Workspace Closeout

For high-value research outputs:

- keep the desktop bundle for immediate use
- copy or register the final artifacts under `30 Projects/<项目名>/exports/` or `10 Research/`
- record useful lessons with the workspace closeout path when the task produced reusable workflow knowledge

## Bundled Scripts

- `scripts/literature_runtime.py`: installs/uses the managed Python runtime.
- `scripts/run_literature_bundle.py`: prepares, builds, renders, packages, and validates the bundle.
- `scripts/extract_pdf_text.py`: extracts title guess, pages, abstract snippet, and text.
- `scripts/analyze_paper_sections.py`: maps extracted text into section-aware snippets.
- `scripts/extract_pdf_figures.py`: extracts or renders figure candidates.
- `scripts/profile_reference_ppt.py`: profiles a reference deck.
- `scripts/build_presentation_from_spec.py`: builds the PPTX from slide spec JSON.
- `scripts/write_summary_docx.py`: converts summary text to Word.
- `scripts/write_sources_docx.py`: converts source manifest JSON to Word.
- `scripts/render_pptx_for_qa.py`: renders PPTX to PDF/JPEG QA images.
- `scripts/validate_literature_bundle.py`: validates final bundle structure and QA counts.
- `scripts/create_literature_bundle.py`: copies final artifacts into the desktop bundle.
