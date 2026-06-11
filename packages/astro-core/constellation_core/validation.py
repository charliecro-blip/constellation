"""Fixture validation helpers for Constellation."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from .chart import DEFAULT_HOUSE_SYSTEM, calculate_chart
from .schemas import BirthData, Chart


class ExpectedPoint(BaseModel):
    sign: str | None = None
    degree: float | None = None
    longitude: float | None = None
    tolerance: float = 1.0


class ValidationFixture(BaseModel):
    birth: BirthData
    expected: dict[str, ExpectedPoint]
    source: str | None = None


class ValidationResult(BaseModel):
    point: str
    passed: bool
    expected: ExpectedPoint
    actual_sign: str | None = None
    actual_degree: float | None = None
    actual_longitude: float | None = None
    message: str


def _degree_delta(a: float, b: float) -> float:
    diff = abs(a - b) % 30.0
    return min(diff, 30.0 - diff)


def validate_chart_against_fixture(chart: Chart, fixture: ValidationFixture) -> list[ValidationResult]:
    results: list[ValidationResult] = []

    for point, expected in fixture.expected.items():
        key = point.lower()
        actual_sign = None
        actual_degree = None
        actual_longitude = None

        if key in chart.placements:
            actual = chart.placements[key]
            actual_sign = actual.sign
            actual_degree = actual.degree
            actual_longitude = actual.longitude
        elif key in chart.angles:
            actual_angle = chart.angles[key]
            actual_sign = actual_angle.sign
            actual_degree = actual_angle.degree
            actual_longitude = actual_angle.longitude
        else:
            results.append(ValidationResult(
                point=point,
                passed=False,
                expected=expected,
                message=f"Point {point} not found in chart output.",
            ))
            continue

        passed = True
        messages: list[str] = []
        if expected.sign is not None and actual_sign != expected.sign:
            passed = False
            messages.append(f"expected sign {expected.sign}, got {actual_sign}")
        if expected.degree is not None and actual_degree is not None:
            delta = _degree_delta(actual_degree, expected.degree)
            if delta > expected.tolerance:
                passed = False
                messages.append(
                    f"expected degree {expected.degree}, got {actual_degree}, delta {delta:.3f}"
                )
        if expected.longitude is not None and actual_longitude is not None:
            long_delta = abs(actual_longitude - expected.longitude) % 360.0
            long_delta = min(long_delta, 360.0 - long_delta)
            if long_delta > expected.tolerance:
                passed = False
                messages.append(
                    f"expected longitude {expected.longitude}, got {actual_longitude}, delta {long_delta:.3f}"
                )

        results.append(ValidationResult(
            point=point,
            passed=passed,
            expected=expected,
            actual_sign=actual_sign,
            actual_degree=actual_degree,
            actual_longitude=actual_longitude,
            message="; ".join(messages) if messages else "ok",
        ))

    return results


def load_validation_fixture(path: str | Path) -> ValidationFixture:
    return ValidationFixture(**json.loads(Path(path).read_text()))


def validate_fixture(path: str | Path, house_system: str = DEFAULT_HOUSE_SYSTEM) -> list[ValidationResult]:
    fixture = load_validation_fixture(path)
    chart = calculate_chart(fixture.birth, house_system=house_system)
    return validate_chart_against_fixture(chart, fixture)
