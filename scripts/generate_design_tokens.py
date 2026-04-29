#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


THEMES = {
    "academic_teal": {
        "palette": {
            "background": [248, 245, 239],
            "primary": [26, 77, 90],
            "secondary": [181, 137, 78],
            "text": [33, 37, 41],
            "muted": [92, 100, 107],
            "surface": [255, 255, 255],
            "line": [226, 236, 234],
            "band": [239, 232, 219],
            "accent": [180, 45, 45],
        },
        "typography": {
            "title_font": "Georgia",
            "body_font": "Georgia",
            "label_font": "Georgia",
        },
        "shape": {"border_width": 1.0},
    },
    "clinical_blue": {
        "palette": {
            "background": [244, 247, 250],
            "primary": [24, 63, 95],
            "secondary": [106, 154, 178],
            "text": [29, 37, 43],
            "muted": [97, 108, 117],
            "surface": [255, 255, 255],
            "line": [218, 227, 233],
            "band": [226, 237, 242],
            "accent": [176, 63, 54],
        },
        "typography": {
            "title_font": "Cambria",
            "body_font": "Aptos",
            "label_font": "Aptos",
        },
        "shape": {"border_width": 1.1},
    },
    "forest_research": {
        "palette": {
            "background": [246, 246, 241],
            "primary": [48, 84, 62],
            "secondary": [144, 162, 99],
            "text": [37, 43, 38],
            "muted": [102, 111, 101],
            "surface": [255, 255, 252],
            "line": [222, 228, 216],
            "band": [233, 237, 223],
            "accent": [160, 74, 57],
        },
        "typography": {
            "title_font": "Palatino Linotype",
            "body_font": "Aptos",
            "label_font": "Aptos",
        },
        "shape": {"border_width": 1.0},
    },
}


SCENARIO_THEME = {
    "lab_meeting": "academic_teal",
    "course_report": "clinical_blue",
    "proposal_defense": "forest_research",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate default design tokens for literature PPT decks.")
    parser.add_argument("--theme", choices=sorted(THEMES), help="Explicit theme id")
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIO_THEME),
        help="Scenario-based theme selection when --theme is not given",
    )
    parser.add_argument("--output", type=Path, help="Optional output JSON path")
    args = parser.parse_args()

    theme_id = args.theme or SCENARIO_THEME.get(args.scenario or "lab_meeting", "academic_teal")
    payload = {
        "theme_id": theme_id,
        "design_tokens": THEMES[theme_id],
    }

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
