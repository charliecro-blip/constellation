"""FastAPI app for the Constellation calculation and report prototype."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .context import RelationshipContext
from .patterns import Pattern, detect_relationship_patterns
from .relationship import calculate_relationship
from .report import generate_relationship_report
from .schemas import BirthData, Chart, RelationshipCalculation
from .weighting import weight_patterns

app = FastAPI(
    title="Constellation API",
    version="0.1.0",
    description="Calculation-first API for relational astrology maps.",
)


class RelationshipRequest(BaseModel):
    person_a: BirthData
    person_b: BirthData
    house_system: str = "whole_sign"
    context: RelationshipContext | None = None


class RelationshipResponse(BaseModel):
    calculation: RelationshipCalculation
    patterns: list[Pattern]


class ReportResponse(BaseModel):
    markdown: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chart", response_model=Chart)
def chart_endpoint(birth: BirthData) -> Chart:
    from .chart import calculate_chart

    return calculate_chart(birth)


@app.post("/relationship", response_model=RelationshipResponse)
def relationship_endpoint(request: RelationshipRequest) -> RelationshipResponse:
    calculation = calculate_relationship(
        request.person_a,
        request.person_b,
        house_system=request.house_system,
    )
    raw_patterns = detect_relationship_patterns(calculation)
    patterns = weight_patterns(raw_patterns, request.context)
    return RelationshipResponse(calculation=calculation, patterns=patterns)


@app.post("/report", response_model=ReportResponse)
def report_endpoint(request: RelationshipRequest) -> ReportResponse:
    calculation = calculate_relationship(
        request.person_a,
        request.person_b,
        house_system=request.house_system,
    )
    report = generate_relationship_report(calculation, context=request.context)
    return ReportResponse(markdown=report.to_markdown())
