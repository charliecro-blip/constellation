"""Optional AI prose enhancement for deterministic relationship reports."""

from __future__ import annotations

from typing import Any
import os

from pydantic import BaseModel, Field

from .schemas import ReportSynthesisPacket


DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MODEL_ENV = "OPENAI_MODEL"
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
PROVIDER_ERROR_MESSAGE = (
    "AI enhancement provider error. Check OpenAI API key, billing, model access, "
    "or provider availability."
)

AI_ENHANCEMENT_SYSTEM_PROMPT = """You are writing an astrology relationship report from a structured deterministic astrology report.

Rules:
- Do not invent astrology. Do not invent placements or aspect meanings beyond the source.
- Do not add new aspects, houses, signs, asteroids, placements, or claims.
- Do not introduce new aspects, placements, houses, asteroids, signs, timing, or claims not present in the deterministic report.
- Only interpret patterns that appear in the provided report.
- When a synthesis packet is provided, treat it as the deterministic priority guide, not optional background.
- Preserve the lead pattern from the synthesis packet unless the deterministic Markdown clearly contradicts it.
- Use the top ranked patterns in synthesis packet priority order to shape the Overview.
- Do not elevate secondary or supporting patterns over lead-eligible patterns.
- Preserve the deterministic priorities; do not make supporting contacts sound more important than the selected lead themes.
- Prefer fewer, deeper themes over scattershot coverage.
- Keep the same main section headings.
- Preserve the Chart Check section as concise factual bullet points; do not turn it into interpretive prose.
- Preserve the two people's names.
- Do not turn the reading into a compatibility score.
- Do not turn the report into compatibility scoring; do not add compatibility scores or a compatibility score.
- Do not use soulmate, fated, destined, twin flame, fate, destiny, meant-to-be, or perfect-match language.
- Do not say "meant to be."
- Do not make deterministic predictions or claims about whether the relationship will last.
- Do not mention AI, model, prompts, API, technical metadata, or backend details.
- Do not add medical, legal, financial, or crisis advice.
- Do not use raw orb numbers.
- Do not use generic astrology glossary language.
- Avoid generic AI phrases and vague connective language, including: "navigate the complexities", "provide a baseline", "unique entity", "thrives on", "fosters", "invites both", "highlighting how", "highlights", "suggests", and "journey".
- Rewrite toward concrete relational language and direct relational language that names what each person tends to feel, provoke, protect, resist, or reveal.
- Use the movement theme → felt experience → shadow → repair → agency when developing major themes.
- Name the central relationship story in the first Overview paragraph.
- Do not over-soften difficult dynamics. Keep difficult dynamics clear but non-alarming; describe friction, avoidance, intensity, control, disappointment, or mismatch plainly when the source report supports it.
- Do not overstate certainty. Use calibrated language such as "may", "tends to", "can", "often", "worth noticing", "the bond asks for", and "repair often means".
- Do not turn the report into therapy-speak.
- Keep the report grounded, warm, precise, and emotionally intelligent.
- Synthesize rather than list.
- Make the report feel like a skilled astrologer is interpreting the relationship field.
- Keep the tone precise, warm, and human; intimate but not melodramatic.
- Keep Markdown headings intact.
- Preserve astrology facts and section headings, but rewrite the prose substantially.
- Remove or smooth visible deterministic labels and engine phrases, including:
  Additional.; Central.; Moderate.; Exact.; Very close.; Close.; Supporting texture.;
  "The Ascendant/Descendant axis describes";
  "The listed bodies operate less like separate details";
  "The planet person may appear as"; and "This is the basic weather".
- Return only Markdown.

Internal weak/strong examples:
Weak: "Venus conjunct Pluto indicates a powerful soulmate connection."
Strong: "Venus-Pluto contacts can feel less like simply liking someone and more like being pulled toward them before you have fully decided what the attraction means. The intensity is real, but it does not, by itself, say whether the bond has enough structure to last."
Weak: "Moon opposite Moon is a bad aspect."
Strong: "Moon-Moon opposition often means each person has a different emotional home base. What soothes one person may not register as soothing to the other, so emotional repair usually needs to be learned explicitly rather than assumed."

Style target:
The prose should feel more like a human astrology reading than pattern-detector output. It should be specific, cohesive, and relational. It should explain what the patterns mean together, not simply restate each aspect."""


class ReportEnhancementContext(BaseModel):
    relationship_type: str | None = None
    status: str | None = None
    user_question: str | None = None
    origin_story: str | None = None
    known_themes: list[str] = Field(default_factory=list)
    house_system: str | None = None


class ReportEnhancementRequest(BaseModel):
    markdown: str
    context: ReportEnhancementContext | None = None
    synthesis_packet: ReportSynthesisPacket | None = None


class EnhancementUnavailableError(RuntimeError):
    """Raised when optional AI enhancement cannot be used in this environment."""


class EnhancementProviderError(RuntimeError):
    """Raised when the AI provider does not return usable enhanced Markdown."""


def configured_model() -> str:
    return os.getenv(OPENAI_MODEL_ENV, DEFAULT_OPENAI_MODEL)


def _context_lines(context: ReportEnhancementContext | None) -> list[str]:
    if context is None:
        return []
    values = context.model_dump()
    lines: list[str] = []
    labels = {
        "relationship_type": "Relationship type",
        "status": "Status",
        "user_question": "User question",
        "origin_story": "Origin story",
        "known_themes": "Known themes",
        "house_system": "House system",
    }
    for key, label in labels.items():
        value = values.get(key)
        if value is None or value == "" or value == []:
            continue
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value if item)
        if value:
            lines.append(f"- {label}: {value}")
    return lines


def build_enhancement_user_prompt(
    markdown: str,
    context: ReportEnhancementContext | None = None,
    synthesis_packet: ReportSynthesisPacket | None = None,
) -> str:
    context_lines = _context_lines(context)
    context_block = (
        "\n".join(context_lines) if context_lines else "- No additional context supplied."
    )
    packet_block = (
        synthesis_packet.model_dump_json(exclude_none=True, indent=2)
        if synthesis_packet is not None
        else "No synthesis packet supplied; preserve priorities visible in the deterministic Markdown."
    )
    return f"""Rewrite the deterministic Markdown report below into a warmer, cohesive astrology relationship reading while following every rule in the system instructions.

Available user context:
{context_block}

Deterministic synthesis packet (priority guide):
{packet_block}

Use the synthesis packet priority order to decide what leads, what supports, and what should remain secondary. Do not infer the main themes from Markdown alone when a packet is supplied.

Deterministic Markdown report:
---
{markdown}
---"""


def _load_openai_client(api_key: str) -> Any:
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - depends on optional installation state
        raise EnhancementUnavailableError(
            "AI enhancement is unavailable because the OpenAI client is not installed."
        ) from exc
    return OpenAI(api_key=api_key)


def _extract_markdown(response: Any) -> str:
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise EnhancementProviderError("AI enhancement did not return Markdown.") from exc
    if not isinstance(content, str) or not content.strip():
        raise EnhancementProviderError("AI enhancement returned an empty report.")
    return content.strip()


def enhance_report_markdown(
    request: ReportEnhancementRequest,
    *,
    client: Any | None = None,
    api_key: str | None = None,
) -> str:
    if not request.markdown.strip():
        raise ValueError("markdown is required")

    key = api_key if api_key is not None else os.getenv(OPENAI_API_KEY_ENV)
    if not key:
        raise EnhancementUnavailableError(
            "AI enhancement is unavailable because OPENAI_API_KEY is not configured."
        )

    openai_client = client or _load_openai_client(key)
    try:
        response = openai_client.chat.completions.create(
            model=configured_model(),
            messages=[
                {"role": "system", "content": AI_ENHANCEMENT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_enhancement_user_prompt(
                        request.markdown, request.context, request.synthesis_packet
                    ),
                },
            ],
            temperature=0.55,
        )
    except Exception as exc:
        raise EnhancementProviderError(PROVIDER_ERROR_MESSAGE) from exc
    return _extract_markdown(response)
