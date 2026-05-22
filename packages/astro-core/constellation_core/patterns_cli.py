"""CLI for producing ranked relationship patterns from two birth fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .patterns import detect_relationship_patterns
from .relationship import calculate_relationship
from .schemas import BirthData


def load_birth_data(path: str) -> BirthData:
    return BirthData(**json.loads(Path(path).read_text()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate ranked relationship patterns.")
    parser.add_argument("--person-a", required=True)
    parser.add_argument("--person-b", required=True)
    parser.add_argument("--house-system", default="whole_sign")
    parser.add_argument("--output", required=False)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    relationship = calculate_relationship(
        load_birth_data(args.person_a),
        load_birth_data(args.person_b),
        house_system=args.house_system,
    )
    patterns = detect_relationship_patterns(relationship)
    output = json.dumps([pattern.model_dump() for pattern in patterns], indent=2)
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
