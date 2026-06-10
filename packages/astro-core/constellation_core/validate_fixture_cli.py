"""CLI for validating chart calculation against known expected positions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .validation import validate_fixture


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a chart fixture against calculated output.")
    parser.add_argument("fixture", help="Path to validation fixture JSON")
    parser.add_argument("--house-system", default="placidus")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    results = validate_fixture(Path(args.fixture), house_system=args.house_system)

    if args.json:
        print(json.dumps([result.model_dump() for result in results], indent=2))
        return

    failures = [result for result in results if not result.passed]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.point}: {result.message}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
