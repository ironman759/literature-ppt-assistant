# Slide Spec Schema

Use this file when generating `slide_spec.json` for `build_presentation_from_spec.py`.

## Deck Fields

```json
{
  "deck_title": "Paper title",
  "subtitle": "Scenario or short framing",
  "citation": "Author, journal, year",
  "design_tokens": {},
  "slides": []
}
```

`design_tokens` may use:

```json
{
  "palette": {
    "background": [248, 245, 239],
    "primary": [26, 77, 90],
    "secondary": [181, 137, 78],
    "text": [33, 37, 41],
    "muted": [92, 100, 107],
    "surface": [255, 255, 255],
    "line": [226, 236, 234],
    "band": [239, 232, 219],
    "accent": [180, 45, 45]
  },
  "typography": {
    "title_font": "Georgia",
    "body_font": "Georgia",
    "label_font": "Georgia"
  },
  "shape": {
    "border_width": 1.0
  }
}
```

## Slide Fields

Each slide should include:

```json
{
  "section": "Background",
  "title": "Internal planning title",
  "assertion_title": "Conclusion-style slide title",
  "subtitle": "Optional short context",
  "slide_purpose": "Set up the gap",
  "layout": "standard",
  "bullets": ["Concise point 1", "Concise point 2"],
  "notes": "Presentation-ready speaker notes.",
  "image_path": "/absolute/path/to/image.png",
  "image_caption": "Figure 1, source PDF page 4",
  "takeaway": "Optional bottom-line message",
  "design_tokens": {}
}
```

`title` can stay neutral for planning. Prefer `assertion_title` on rendered slides when the slide makes a claim.

## Supported Layouts

- `standard`: bullets with optional image panel.
- `section_intro`: chapter-opening or transition page.
- `workflow`: 3-4 step method/process/pipeline page.
- `result_summary`: foreground 2-3 headline findings or metrics.
- `comparison`: two methods, conditions, or interpretations side by side.
- `limitation_implication`: separate risks from take-home meaning.
- `figure_focus`: give one source figure primary visual space.
- `sampling_design`: sample groups, branches, or experimental design.

## Layout-Specific Fields

Use these fields exactly. The builder validates them before rendering.

### `standard`

Required:

```json
{
  "layout": "standard",
  "bullets": ["Point 1", "Point 2"]
}
```

Optional:

```json
{
  "image_path": "/absolute/path/to/image.png",
  "image_caption": "Short caption"
}
```

### `comparison`

Required:

```json
{
  "layout": "comparison",
  "left_column": {
    "title": "Column title",
    "bullets": ["Point 1", "Point 2"]
  },
  "right_column": {
    "title": "Column title",
    "bullets": ["Point 1", "Point 2"]
  }
}
```

Do not use `items` for comparison columns. If older specs contain `items`, the builder will convert them to `bullets`, but new specs should use `bullets`.

### `workflow`

Required:

```json
{
  "layout": "workflow",
  "workflow_steps": ["Step 1", "Step 2", "Step 3"]
}
```

`bullets` may be used as a fallback, but `workflow_steps` is clearer.

### `result_summary`

Required:

```json
{
  "layout": "result_summary",
  "result_highlights": [
    {"value": "119,510", "label": "putatively lytic phages"}
  ],
  "bullets": ["Interpretive point"]
}
```

If `result_highlights` is absent, the builder tries to infer highlights from `bullets`, but explicit highlights are preferred.

### `figure_focus`

Required:

```json
{
  "layout": "figure_focus",
  "image_path": "/absolute/path/to/readable_figure.png",
  "figure_callout": "What to notice",
  "bullets": ["Interpretive point"]
}
```

Use `image_caption` only for short source notes. If the slide also has a `takeaway`, the builder suppresses bottom captions to avoid overlap; keep full source details in `asset_sources.json`.

### `limitation_implication`

Required:

```json
{
  "layout": "limitation_implication",
  "limitations": ["Risk or uncertainty"],
  "implications": ["Meaning or opportunity"]
}
```

### `section_intro`

Recommended:

```json
{
  "layout": "section_intro",
  "assertion_title": "Section message",
  "bullets": ["What this section covers"]
}
```

### `sampling_design`

Required when used:

```json
{
  "layout": "sampling_design",
  "panel_headings": {"left": "Left panel", "right": "Right panel"},
  "left_image_path": "/absolute/path/to/left.png",
  "right_image_path": "/absolute/path/to/right.png"
}
```

## Speaker Notes

Notes are for oral delivery. They should sound like what a prepared presenter would say aloud: clear transitions, moderate density, accurate terms, no copied abstract prose.

Use phrases such as:

- "Here the authors show..."
- "The key point is..."
- "What matters for us is..."
- "这一页的重点是..."
- "作者在这里想说明的是..."

## Quality Guardrails

- Keep slide bullets short and presentation-ready.
- Put detailed explanation in notes, not on the slide.
- Preserve source uncertainty.
- Do not insert unreadable figures.
- Use bold/red emphasis sparingly for important numbers, method names, or conclusion terms.
- Every rendered content slide must have `slide_purpose` and `notes`.
- Run spec validation before building the deck; empty cards usually mean a layout-specific field name is wrong.
- After rendering, spot-check QA images for text overflow, unintended whitespace, page-number wrapping, and figure/takeaway overlap.
