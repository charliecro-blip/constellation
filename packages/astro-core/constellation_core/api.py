"""FastAPI app for the Constellation prototype.

This exposes the calculation and report pipeline without adding accounts,
persistence, payments, or a polished frontend.
"""

from __future__ import annotations

from datetime import date, datetime, time
import json

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session, delete, select

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
from .models import BirthProfile, ReportFeedback, SavedRelationship, SavedRelationshipMotif, SavedReport
from .geocoding import GeocodingStatus, PlaceSearchResponse, geocoding_status, search_places
from .motifs import list_relationship_motifs, replace_relationship_motifs
from .patterns import Pattern, detect_relationship_patterns
from .places import PlacePreset, list_place_presets
from .relationship import calculate_relationship
from .report import build_report_diagnostics, build_report_synthesis_packet, generate_relationship_report
from .schemas import BirthData, Chart, DynamicDetail, RelationshipCalculation, ReportDiagnostics, ReportSynthesisPacket
from .theme_index import ThemePresence
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


class UpdateSavedRelationshipRequest(BaseModel):
    person_a: CreateBirthProfileRequest
    person_b: CreateBirthProfileRequest
    relationship_type: str
    status: str
    user_question: str | None = None
    origin_story: str | None = None
    known_themes: list[str] = Field(default_factory=list)
    house_system: str = DEFAULT_HOUSE_SYSTEM


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


class RelationshipMotifResponse(BaseModel):
    id: str
    relationship_id: str
    person_a_id: str
    person_b_id: str
    motif_key: str
    category: str
    title: str
    layer: str
    priority: int
    adjusted_priority: int | None = None
    confidence: str | None = None
    evidence_text: str | None = None
    lead_eligible: bool
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
    category: str | None = None
    category_label: str | None = None
    description: str | None = None
    evidence: list[str] = Field(default_factory=list)
    relationship_ids: list[str] = Field(default_factory=list)


class MotifCategoryCountResponse(BaseModel):
    category: str
    label: str
    description: str | None = None
    count: int


class RelationshipSpecificMotifResponse(BaseModel):
    title: str
    category: str
    category_label: str
    description: str
    evidence: str | None = None


class RelationshipMotifGroupResponse(BaseModel):
    relationship_id: str
    label: str
    motifs: list[RelationshipSpecificMotifResponse]


class ConstellationPatternSummaryResponse(BaseModel):
    relationship_count: int
    has_enough_data: bool
    empty_state: str | None
    relationship_type_counts: list[PatternTypeCountResponse]
    known_theme_counts: list[PatternKnownThemeResponse]
    recurring_motifs: list[PatternMotifResponse]
    top_motif_categories: list[MotifCategoryCountResponse] = Field(default_factory=list)
    relationship_motifs: list[RelationshipMotifGroupResponse] = Field(default_factory=list)
    plain_language_summary: str




class ReportFeedbackRequest(BaseModel):
    relationship_id: str | None = None
    report_id: str | None = None
    saved_report_id: str | None = None
    usefulness_rating: int | None = Field(default=None, ge=1, le=5)
    rating: int | None = Field(default=None, ge=1, le=5)
    accuracy_rating: int | None = Field(default=None, ge=1, le=5)
    clarity_rating: int | None = Field(default=None, ge=1, le=5)
    felt_seen_rating: int | None = Field(default=None, ge=1, le=5)
    too_long: bool | None = None
    too_intense: bool | None = None
    too_technical: bool | None = None
    freeform_comment: str | None = None
    what_landed: str | None = None
    what_felt_off: str | None = None
    central_theme_feedback: str | None = None
    tester_label: str | None = None
    report_version_metadata: dict[str, object] | None = None

    @field_validator(
        "freeform_comment",
        "what_landed",
        "what_felt_off",
        "central_theme_feedback",
        "tester_label",
    )
    @classmethod
    def blank_strings_as_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ReportFeedbackResponse(BaseModel):
    feedback_id: str
    relationship_id: str | None
    saved_report_id: str | None
    created_at: datetime
    usefulness_rating: int | None = None
    accuracy_rating: int | None = None
    clarity_rating: int | None = None
    felt_seen_rating: int | None = None
    too_long: bool | None = None
    too_intense: bool | None = None
    too_technical: bool | None = None
    freeform_comment: str | None = None
    what_landed: str | None = None
    what_felt_off: str | None = None
    central_theme_feedback: str | None = None
    tester_label: str | None = None
    report_version_metadata: dict[str, object] | None = None


class RelationshipFeedbackSummaryResponse(BaseModel):
    relationship_id: str
    response_count: int
    average_clarity: float | None = None
    average_accuracy: float | None = None
    average_felt_seen: float | None = None
    most_recent: str | None = None
    feedback: list[ReportFeedbackResponse]

class SavedReportResponse(BaseModel):
    id: str
    relationship_id: str
    markdown: str
    dynamic_details: list[DynamicDetail] = Field(default_factory=list)
    theme_index: list[ThemePresence] = Field(default_factory=list)
    synthesis_packet: ReportSynthesisPacket | None = None
    diagnostics: ReportDiagnostics | None = None
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
    dynamic_details: list[DynamicDetail] = Field(default_factory=list)
    theme_index: list[ThemePresence] = Field(default_factory=list)
    synthesis_packet: ReportSynthesisPacket | None = None
    diagnostics: ReportDiagnostics | None = None


class ReportEnhancementResponse(BaseModel):
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


@app.post("/report", response_model=ReportResponse, response_model_exclude_none=True)
def report_endpoint(
    request: RelationshipRequest,
    include_diagnostics: bool = Query(False),
) -> ReportResponse:
    calculation = calculate_relationship(
        request.person_a,
        request.person_b,
        house_system=request.house_system,
    )
    report = generate_relationship_report(calculation, context=request.context)
    synthesis_packet = build_report_synthesis_packet(calculation, context=request.context)
    diagnostics = (
        build_report_diagnostics(calculation, context=request.context, synthesis_packet=synthesis_packet)
        if include_diagnostics
        else None
    )
    return ReportResponse(markdown=report.to_markdown(), dynamic_details=report.dynamic_details, theme_index=report.theme_index, synthesis_packet=synthesis_packet, diagnostics=diagnostics)


@app.post("/report/enhance", response_model=ReportEnhancementResponse)
def enhance_report_endpoint(request: ReportEnhancementRequest) -> ReportEnhancementResponse:
    try:
        enhanced_markdown = enhance_report_markdown(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except EnhancementUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except EnhancementProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ReportEnhancementResponse(markdown=enhanced_markdown)


def _feedback_response(feedback: ReportFeedback) -> ReportFeedbackResponse:
    metadata = json.loads(feedback.report_version_metadata_json) if feedback.report_version_metadata_json else None
    return ReportFeedbackResponse(
        feedback_id=feedback.id,
        relationship_id=feedback.relationship_id,
        saved_report_id=feedback.saved_report_id,
        created_at=feedback.created_at,
        usefulness_rating=feedback.usefulness_rating,
        accuracy_rating=feedback.accuracy_rating,
        clarity_rating=feedback.clarity_rating,
        felt_seen_rating=feedback.felt_seen_rating,
        too_long=feedback.too_long,
        too_intense=feedback.too_intense,
        too_technical=feedback.too_technical,
        freeform_comment=feedback.freeform_comment,
        what_landed=feedback.what_landed,
        what_felt_off=feedback.what_felt_off,
        central_theme_feedback=feedback.central_theme_feedback,
        tester_label=feedback.tester_label,
        report_version_metadata=metadata,
    )


def _average_rating(values: list[int | None]) -> float | None:
    numeric = [value for value in values if value is not None]
    if not numeric:
        return None
    return round(sum(numeric) / len(numeric), 2)


@app.post("/report-feedback", response_model=ReportFeedbackResponse)
def create_report_feedback(
    request: ReportFeedbackRequest, session: Session = Depends(get_session)
) -> ReportFeedbackResponse:
    saved_report_id = request.saved_report_id or request.report_id
    if request.relationship_id and session.get(SavedRelationship, request.relationship_id) is None:
        raise HTTPException(status_code=404, detail="Saved relationship not found")
    saved_report = session.get(SavedReport, saved_report_id) if saved_report_id else None
    if saved_report_id and saved_report is None:
        raise HTTPException(status_code=404, detail="Saved report not found")
    if saved_report and request.relationship_id and saved_report.relationship_id != request.relationship_id:
        raise HTTPException(status_code=422, detail="Saved report does not belong to relationship")
    relationship_id = request.relationship_id or (saved_report.relationship_id if saved_report else None)
    feedback = ReportFeedback(
        relationship_id=relationship_id,
        saved_report_id=saved_report_id,
        usefulness_rating=request.usefulness_rating or request.rating,
        accuracy_rating=request.accuracy_rating,
        clarity_rating=request.clarity_rating,
        felt_seen_rating=request.felt_seen_rating,
        too_long=request.too_long,
        too_intense=request.too_intense,
        too_technical=request.too_technical,
        freeform_comment=request.freeform_comment,
        what_landed=request.what_landed,
        what_felt_off=request.what_felt_off,
        central_theme_feedback=request.central_theme_feedback,
        tester_label=request.tester_label,
        report_version_metadata_json=json.dumps(request.report_version_metadata)
        if request.report_version_metadata
        else None,
    )
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return _feedback_response(feedback)


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



def _update_birth_profile(profile: BirthProfile, request: CreateBirthProfileRequest) -> None:
    for key, value in request.model_dump().items():
        setattr(profile, key, value)
    profile.updated_at = datetime.utcnow()


@app.patch("/saved-relationships/{relationship_id}", response_model=SavedRelationshipResponse)
def update_saved_relationship(
    relationship_id: str,
    request: UpdateSavedRelationshipRequest,
    session: Session = Depends(get_session),
) -> SavedRelationshipResponse:
    relationship = session.get(SavedRelationship, relationship_id)
    if relationship is None:
        raise HTTPException(status_code=404, detail="Saved relationship not found")
    person_a = session.get(BirthProfile, relationship.person_a_id)
    person_b = session.get(BirthProfile, relationship.person_b_id)
    if person_a is None or person_b is None:
        raise HTTPException(status_code=404, detail="Birth profile not found")

    _update_birth_profile(person_a, request.person_a)
    _update_birth_profile(person_b, request.person_b)
    relationship.relationship_type = request.relationship_type
    relationship.status = request.status
    relationship.user_question = request.user_question
    relationship.origin_story = request.origin_story
    relationship.known_themes_json = json.dumps(request.known_themes)
    relationship.house_system = request.house_system
    relationship.updated_at = datetime.utcnow()
    session.add(person_a)
    session.add(person_b)
    session.add(relationship)
    session.commit()
    session.refresh(relationship)
    return _relationship_response(relationship)


@app.delete("/saved-relationships/{relationship_id}")
def delete_saved_relationship(
    relationship_id: str,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    relationship = session.get(SavedRelationship, relationship_id)
    if relationship is None:
        raise HTTPException(status_code=404, detail="Saved relationship not found")
    session.exec(delete(ReportFeedback).where(ReportFeedback.relationship_id == relationship_id))
    session.exec(delete(SavedRelationshipMotif).where(SavedRelationshipMotif.relationship_id == relationship_id))
    session.exec(delete(SavedReport).where(SavedReport.relationship_id == relationship_id))
    session.delete(relationship)
    session.commit()
    return {"status": "deleted", "id": relationship_id}


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
        stored_motifs = list_relationship_motifs(session, relationship.id)
        inputs.append(
            RelationshipPatternInput(
                relationship_id=relationship.id,
                relationship_type=relationship.relationship_type,
                person_name=person_b.display_name if person_b else "",
                known_themes=json.loads(relationship.known_themes_json),
                report_markdown=latest_report.markdown if latest_report else None,
                structured_motifs=[
                    {
                        "key": motif.motif_key,
                        "category": motif.category,
                        "title": motif.title,
                        "relationship_id": motif.relationship_id,
                        "evidence_text": motif.evidence_text,
                    }
                    for motif in stored_motifs
                ],
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


@app.get("/saved-relationships/{relationship_id}/feedback", response_model=RelationshipFeedbackSummaryResponse)
def get_saved_relationship_feedback(
    relationship_id: str, session: Session = Depends(get_session)
) -> RelationshipFeedbackSummaryResponse:
    if session.get(SavedRelationship, relationship_id) is None:
        raise HTTPException(status_code=404, detail="Saved relationship not found")
    feedback = list(
        session.exec(
            select(ReportFeedback)
            .where(ReportFeedback.relationship_id == relationship_id)
            .order_by(ReportFeedback.created_at.desc())
        )
    )
    most_recent = None
    if feedback:
        latest = feedback[0]
        most_recent = latest.freeform_comment or latest.what_felt_off or latest.what_landed
    return RelationshipFeedbackSummaryResponse(
        relationship_id=relationship_id,
        response_count=len(feedback),
        average_clarity=_average_rating([item.clarity_rating for item in feedback]),
        average_accuracy=_average_rating([item.accuracy_rating for item in feedback]),
        average_felt_seen=_average_rating([item.felt_seen_rating for item in feedback]),
        most_recent=most_recent,
        feedback=[_feedback_response(item) for item in feedback],
    )


@app.get("/saved-relationships/{relationship_id}/motifs", response_model=list[RelationshipMotifResponse])
def get_saved_relationship_motifs(
    relationship_id: str, session: Session = Depends(get_session)
) -> list[SavedRelationshipMotif]:
    if session.get(SavedRelationship, relationship_id) is None:
        raise HTTPException(status_code=404, detail="Saved relationship not found")
    return list_relationship_motifs(session, relationship_id)


@app.post("/saved-relationships/{relationship_id}/report", response_model=SavedReportResponse, response_model_exclude_none=True)
def generate_saved_relationship_report(
    relationship_id: str,
    include_diagnostics: bool = Query(False),
    session: Session = Depends(get_session),
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
    synthesis_packet = build_report_synthesis_packet(calc, context=context)
    saved = SavedReport(relationship_id=relationship.id, markdown=report.to_markdown())
    session.add(saved)
    replace_relationship_motifs(session, relationship, synthesis_packet)
    session.commit()
    session.refresh(saved)
    diagnostics = (
        build_report_diagnostics(calc, context=context, synthesis_packet=synthesis_packet)
        if include_diagnostics
        else None
    )
    return SavedReportResponse(
        id=saved.id,
        relationship_id=saved.relationship_id,
        markdown=saved.markdown,
        dynamic_details=report.dynamic_details,
        theme_index=report.theme_index,
        synthesis_packet=synthesis_packet,
        diagnostics=diagnostics,
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
