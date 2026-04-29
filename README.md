# Literature PPT Assistant

A Codex skill for turning academic paper PDFs into presentation-ready literature bundles:

- source PDF copy
- paper summary DOCX
- presentation PPTX with speaker notes
- source/image manifest DOCX
- rendered QA images and validation report

The skill is designed for journal clubs, lab meetings, course reports, and proposal-defense preparation.

## Use

Run the managed runtime wrapper from the skill root:

```bash
python3 scripts/literature_runtime.py \
  scripts/run_literature_bundle.py \
  --pdf "/absolute/path/to/paper.pdf" \
  --scenario lab_meeting
```

If you have a reference deck:

```bash
python3 scripts/literature_runtime.py \
  scripts/run_literature_bundle.py \
  --pdf "/absolute/path/to/paper.pdf" \
  --reference-pptx "/absolute/path/to/reference.pptx" \
  --scenario lab_meeting
```

The first pass prepares extraction artifacts. After drafting `summary.md` and `slide_spec.json`, rerun with:

```bash
python3 scripts/literature_runtime.py \
  scripts/run_literature_bundle.py \
  --pdf "/absolute/path/to/paper.pdf" \
  --summary-md "/absolute/path/to/summary.md" \
  --spec "/absolute/path/to/slide_spec.json" \
  --scenario lab_meeting
```

## Skill Files

- `SKILL.md`: Codex skill instructions.
- `scripts/literature_runtime.py`: creates and reuses a managed Python runtime.
- `scripts/run_literature_bundle.py`: prepares, builds, renders, packages, and validates the bundle.
- `references/slide_spec_schema.md`: slide spec reference for PPTX generation.

## Notes

This repository intentionally excludes local/private assets and generated cache files. External or generated images used in a deck should be recorded in the source manifest.
