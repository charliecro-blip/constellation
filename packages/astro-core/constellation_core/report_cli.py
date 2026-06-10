"""CLI for generating a first-pass Relationship Field Map markdown report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .context import RelationshipContext
from .report import generate_report_from_birth_data
from .schemas import BirthData


def load_birth_data(path: str) -> BirthData:
    return BirthData(**json.loads(Path(path).read_text()))


def load_context(path: str | None) -> RelationshipContext | None:
    if path is None:
        return None
    return RelationshipContext(**json.loads(Path(path).read_text()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a markdown Relationship Field Map.")
    parser.add_argument("--person-a", required=True)
    parser.add_argument("--person-b", required=True)
    parser.add_argument("--context", required=False, help="Optional relationship context JSON")
    parser.add_argument("--house-system", default="placidus")
    parser.add_argument("--output", required=False)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = generate_report_from_birth_data(
        load_birth_data(args.person_a),
        load_birth_data(args.person_b),
        house_system=args.house_system,
        context=load_context(args.context),
    )
    markdown = report.to_markdown()
    if args.output:
        Path(args.output).write_text(markdown)
    else:
        print(markdown)


if __name__ == "__main__":
    main()
