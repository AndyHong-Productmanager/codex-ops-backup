#!/usr/bin/env python3
"""Compatibility entry point for the relocated GitHub CI fallback helper."""

from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    canonical_helper = (
        Path(__file__).resolve().parents[2] / "github" / "scripts" / "inspect_pr_checks.py"
    )
    runpy.run_path(str(canonical_helper), run_name="__main__")
