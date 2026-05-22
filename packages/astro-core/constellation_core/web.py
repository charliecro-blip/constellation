"""Static web asset helpers for the Constellation prototype."""

from __future__ import annotations

from pathlib import Path

STATIC_DIR = Path(__file__).with_name("static")
INDEX_PATH = STATIC_DIR / "index.html"
