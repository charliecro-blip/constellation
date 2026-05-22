"""Command-line relationship calculation tool."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .relationship import calculate_relationship
from .schemas import BirthData


def load_birth_data(path: str) -> BirthData:
    payload = json.loads(Path(path).read_text())
    return BirthData(**payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate relationship JSON for two birth data files.")
    parser.add_argument("--person-a", required=True, help="Path to Person A birth JSON")
    parser.add_argument("--person-b", required=True, help="Path to Person B birth JSON")
    parser.add_argument("--house-system", default="whole_sign")
    parser.add_argument("--output", required=False, help="Optional path for output JSON")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    person_a = load_birth_data(args.person_a)
    person_b = load_birth_data(args.person_b)
    relationship = calculate_relationship(person_a, person_b, house_system=args.house_system)
    output = json.dumps(relationship.model_dump(), indent=2)
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
