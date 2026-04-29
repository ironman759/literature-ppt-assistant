#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REQUIREMENTS = SKILL_DIR / "requirements.txt"
CACHE_ROOT = Path.home() / ".cache" / "codex-skill-runtimes" / "literature-ppt-assistant"
VENV_DIR = CACHE_ROOT / ".venv"
PYTHON = VENV_DIR / "bin" / "python3"

MODULES = {
    "fitz": "PyMuPDF",
    "pptx": "python-pptx",
    "docx": "python-docx",
    "yaml": "PyYAML",
}


def missing_modules(python: Path | None = None) -> list[str]:
    code = (
        "import importlib.util, json; "
        f"mods={list(MODULES)!r}; "
        "print(json.dumps([m for m in mods if importlib.util.find_spec(m) is None]))"
    )
    exe = str(python or sys.executable)
    proc = subprocess.run([exe, "-c", code], capture_output=True, text=True)
    if proc.returncode != 0:
        return list(MODULES)
    import json

    return json.loads(proc.stdout)


def ensure_runtime() -> Path:
    if PYTHON.exists() and not missing_modules(PYTHON):
        return PYTHON

    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    if not PYTHON.exists():
        venv.EnvBuilder(with_pip=True, clear=False).create(VENV_DIR)

    subprocess.run(
        [str(PYTHON), "-m", "pip", "install", "--upgrade", "pip"],
        check=True,
    )
    subprocess.run(
        [str(PYTHON), "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        check=True,
    )
    remaining = missing_modules(PYTHON)
    if remaining:
        names = ", ".join(f"{m} ({MODULES[m]})" for m in remaining)
        raise SystemExit(f"Runtime setup failed; missing modules: {names}")
    return PYTHON


def run_with_runtime(script: Path, args: list[str]) -> int:
    python = ensure_runtime()
    env = os.environ.copy()
    env["LITERATURE_PPT_RUNTIME"] = str(python)
    return subprocess.call([str(python), str(script), *args], env=env)


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Runtime python: {ensure_runtime()}")
        return 0
    script = Path(sys.argv[1])
    if not script.exists():
        raise SystemExit(f"Script not found: {script}")
    return run_with_runtime(script, sys.argv[2:])


if __name__ == "__main__":
    raise SystemExit(main())
