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
