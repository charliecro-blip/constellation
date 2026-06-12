"""FastAPI app for the Constellation prototype.

This exposes the calculation and report pipeline without adding accounts,
persistence, payments, or a polished frontend.
"""

from __future__ import annotations

from datetime import date, datetime, time
import json

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from .ai_enhancement import (
    EnhancementProviderError,
    EnhancementUnavailableError,
    ReportEnhancementRequest,
    enhance_report_markdown,
)
from .chart import DEFAULT_HOUSE_SYSTEM, calculate_chart
from .context import RelationshipContext
from .constellation_patterns import RelationshipPatternInput, build_constellation_pattern_summary
from .database import get_session, init_db
from .models import BirthProfile, SavedRelationship, SavedReport
from .geocoding import GeocodingStatus, PlaceSearchResponse, geocoding_status, search_places
from .patterns import Pattern, detect_relationship_patterns
from .places import PlacePreset, list_place_presets
from .relationship import calculate_relationship
from .report import ReportSynthesisPacket, generate_relationship_report
from .schemas import BirthData, Chart, RelationshipCalculation
from .web import INDEX_PATH, STATIC_DIR
from .weighting import weight_patterns


class CreateBirthProfileRequest(BaseModel):
    user_id: str | None = None
    anonymous_id: str | None = None
    display_name: str
    birth_date: date
    birth_time: time | None = None
    time_known: bool = True
    latitude: float
    longitude: float
    timezone: str
    birthplace_label: str | None = None
    geocoding_source: str | None = None


class BirthProfileResponse(CreateBirthProfileRequest):
    id: str
    created_at: datetime
    updated_at: datetime


class CreateSavedRelationshipRequest(BaseModel):
    user_id: str | None = None
    anonymous_id: str | None = None
    person_a_id: str
    person_b_id: str
    relationship_type: str
    status: str
    user_question: str | None = None
    origin_story: str | None = None
    known_themes: list[str] = Field(default_factory=list)
    house_system: str = DEFAULT_HOUSE_SYSTEM


class SavedRelationshipResponse(BaseModel):
    id: str
    user_id: str | None
    anonymous_id: str | None
    person_a_id: str
    person_b_id: str
    relationship_type: str
    status: str
    user_question: str | None
    origin_story: str | None
    known_themes: list[str]
    house_system: str
    created_at: datetime
    updated_at: datetime


class PatternTypeCountResponse(BaseModel):
    type: str
    label: str
    count: int


class PatternKnownThemeResponse(BaseModel):
    theme: str
    count: int


class PatternMotifResponse(BaseModel):
    id: str
    label: str
    count: int
    people: list[str]
    summary_label: str


class ConstellationPatternSummaryResponse(BaseModel):
    relationship_count: int
    has_enough_data: bool
    empty_state: str | None
    relationship_type_counts: list[PatternTypeCountResponse]
    known_theme_counts: list[PatternKnownThemeResponse]
    recurring_motifs: list[PatternMotifResponse]
    plain_language_summary: str


class SavedReportResponse(BaseModel):
    id: str
    relationship_id: str
    markdown: str
    synthesis_packet: ReportSynthesisPacket | None = None
    calculation_engine_version: str
    interpretation_engine_version: str
    report_template_version: str
    generated_at: datetime
    created_at: datetime


class RelationshipRequest(BaseModel):
    person_a: BirthData
    person_b: BirthData
    house_system: str = DEFAULT_HOUSE_SYSTEM
    context: RelationshipContext | None = None


class RelationshipResponse(BaseModel):
    calculation: RelationshipCalculation
    patterns: list[Pattern]


class ReportResponse(BaseModel):
    markdown: str
    synthesis_packet: ReportSynthesisPacket | None = None


app = FastAPI(
    title="Constellation API",
    version="0.1.0",
    description="Calculation-first API for relational astrology maps.",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(INDEX_PATH)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/geocoding/status", response_model=GeocodingStatus)
def geocoding_status_endpoint() -> GeocodingStatus:
    return geocoding_status()


@app.get("/places", response_model=list[PlacePreset])
def places_endpoint() -> list[PlacePreset]:
    return list_place_presets()


@app.get("/places/search", response_model=PlaceSearchResponse)
def place_search_endpoint(q: str) -> PlaceSearchResponse:
    return search_places(q)


@app.post("/chart", response_model=Chart)
def chart_endpoint(birth: BirthData, house_system: str = DEFAULT_HOUSE_SYSTEM) -> Chart:
    return calculate_chart(birth, house_system=house_system)


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
    return ReportResponse(markdown=report.to_markdown(), synthesis_packet=report.synthesis_packet)


@app.post("/report/enhance", response_model=ReportResponse, response_model_exclude_none=True)
def enhance_report_endpoint(request: ReportEnhancementRequest) -> ReportResponse:
    try:
        enhanced_markdown = enhance_report_markdown(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except EnhancementUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except EnhancementProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ReportResponse(markdown=enhanced_markdown)


@app.post("/birth-profiles", response_model=BirthProfileResponse)
def create_birth_profile(
    request: CreateBirthProfileRequest, session: Session = Depends(get_session)
) -> BirthProfile:
    profile = BirthProfile.model_validate(request.model_dump())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@app.get("/birth-profiles", response_model=list[BirthProfileResponse])
def list_birth_profiles(session: Session = Depends(get_session)) -> list[BirthProfile]:
    return list(session.exec(select(BirthProfile).order_by(BirthProfile.created_at.desc())))


@app.get("/birth-profiles/{birth_profile_id}", response_model=BirthProfileResponse)
def get_birth_profile(
    birth_profile_id: str, session: Session = Depends(get_session)
) -> BirthProfile:
    profile = session.get(BirthProfile, birth_profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Birth profile not found")
    return profile


def _relationship_response(relationship: SavedRelationship) -> SavedRelationshipResponse:
    return SavedRelationshipResponse(
        id=relationship.id,
        user_id=relationship.user_id,
        anonymous_id=relationship.anonymous_id,
        person_a_id=relationship.person_a_id,
        person_b_id=relationship.person_b_id,
        relationship_type=relationship.relationship_type,
        status=relationship.status,
        user_question=relationship.user_question,
        origin_story=relationship.origin_story,
        known_themes=json.loads(relationship.known_themes_json),
        house_system=relationship.house_system,
        created_at=relationship.created_at,
        updated_at=relationship.updated_at,
    )


@app.post("/saved-relationships", response_model=SavedRelationshipResponse)
def create_saved_relationship(
    request: CreateSavedRelationshipRequest, session: Session = Depends(get_session)
) -> SavedRelationshipResponse:
    if (
        session.get(BirthProfile, request.person_a_id) is None
        or session.get(BirthProfile, request.person_b_id) is None
    ):
        raise HTTPException(status_code=404, detail="Birth profile not found")
    relationship = SavedRelationship(
        user_id=request.user_id,
        anonymous_id=request.anonymous_id,
        person_a_id=request.person_a_id,
        person_b_id=request.person_b_id,
        relationship_type=request.relationship_type,
        status=request.status,
        user_question=request.user_question,
        origin_story=request.origin_story,
        known_themes_json=json.dumps(request.known_themes),
        house_system=request.house_system,
    )
    session.add(relationship)
    session.commit()
    session.refresh(relationship)
    return _relationship_response(relationship)


@app.get("/constellation-patterns", response_model=ConstellationPatternSummaryResponse)
def constellation_patterns_endpoint(
    session: Session = Depends(get_session),
) -> dict[str, object]:
    relationships = list(
        session.exec(select(SavedRelationship).order_by(SavedRelationship.created_at.desc()))
    )
    inputs: list[RelationshipPatternInput] = []
    for relationship in relationships:
        person_b = session.get(BirthProfile, relationship.person_b_id)
        latest_report = session.exec(
            select(SavedReport)
            .where(SavedReport.relationship_id == relationship.id)
            .order_by(SavedReport.created_at.desc())
        ).first()
        inputs.append(
            RelationshipPatternInput(
                relationship_type=relationship.relationship_type,
                person_name=person_b.display_name if person_b else "",
                known_themes=json.loads(relationship.known_themes_json),
                report_markdown=latest_report.markdown if latest_report else None,
            )
        )
    return build_constellation_pattern_summary(inputs)


@app.get("/saved-relationships", response_model=list[SavedRelationshipResponse])
def list_saved_relationships(
    session: Session = Depends(get_session),
) -> list[SavedRelationshipResponse]:
    relationships = list(
        session.exec(select(SavedRelationship).order_by(SavedRelationship.created_at.desc()))
    )
    return [_relationship_response(item) for item in relationships]


@app.get("/saved-relationships/{relationship_id}", response_model=SavedRelationshipResponse)
def get_saved_relationship(
    relationship_id: str, session: Session = Depends(get_session)
) -> SavedRelationshipResponse:
    relationship = session.get(SavedRelationship, relationship_id)
    if relationship is None:
        raise HTTPException(status_code=404, detail="Saved relationship not found")
    return _relationship_response(relationship)


@app.post("/saved-relationships/{relationship_id}/report", response_model=SavedReportResponse)
def generate_saved_relationship_report(
    relationship_id: str, session: Session = Depends(get_session)
) -> SavedReportResponse:
    relationship = session.get(SavedRelationship, relationship_id)
    if relationship is None:
        raise HTTPException(status_code=404, detail="Saved relationship not found")

    person_a = session.get(BirthProfile, relationship.person_a_id)
    person_b = session.get(BirthProfile, relationship.person_b_id)
    if person_a is None or person_b is None:
        raise HTTPException(status_code=404, detail="Birth profile not found")

    context = RelationshipContext(
        relationship_type=relationship.relationship_type,
        status=relationship.status,
        user_question=relationship.user_question,
        origin_story=relationship.origin_story,
        known_themes=json.loads(relationship.known_themes_json),
        house_system=relationship.house_system,
    )

    calc = calculate_relationship(
        BirthData(
            name=person_a.display_name,
            date=person_a.birth_date.isoformat(),
            time=person_a.birth_time.isoformat() if person_a.birth_time else None,
            time_known=person_a.time_known,
            latitude=person_a.latitude,
            longitude=person_a.longitude,
            timezone=person_a.timezone,
            birthplace_label=person_a.birthplace_label,
        ),
        BirthData(
            name=person_b.display_name,
            date=person_b.birth_date.isoformat(),
            time=person_b.birth_time.isoformat() if person_b.birth_time else None,
            time_known=person_b.time_known,
            latitude=person_b.latitude,
            longitude=person_b.longitude,
            timezone=person_b.timezone,
            birthplace_label=person_b.birthplace_label,
        ),
        house_system=relationship.house_system,
    )
    report = generate_relationship_report(calc, context=context)
    saved = SavedReport(relationship_id=relationship.id, markdown=report.to_markdown())
    session.add(saved)
    session.commit()
    session.refresh(saved)
    return SavedReportResponse(
        id=saved.id,
        relationship_id=saved.relationship_id,
        markdown=saved.markdown,
        synthesis_packet=report.synthesis_packet,
        calculation_engine_version=saved.calculation_engine_version,
        interpretation_engine_version=saved.interpretation_engine_version,
        report_template_version=saved.report_template_version,
        generated_at=saved.generated_at,
        created_at=saved.created_at,
    )


@app.get("/saved-relationships/{relationship_id}/reports", response_model=list[SavedReportResponse])
def list_saved_relationship_reports(
    relationship_id: str, session: Session = Depends(get_session)
) -> list[SavedReport]:
    if session.get(SavedRelationship, relationship_id) is None:
        raise HTTPException(status_code=404, detail="Saved relationship not found")
    return list(
        session.exec(
            select(SavedReport)
            .where(SavedReport.relationship_id == relationship_id)
            .order_by(SavedReport.created_at.desc())
        )
    )
