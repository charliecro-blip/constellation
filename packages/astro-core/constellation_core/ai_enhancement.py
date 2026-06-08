"""Optional AI prose enhancement for deterministic relationship reports."""

from __future__ import annotations

from typing import Any
import os

from pydantic import BaseModel, Field


DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MODEL_ENV = "OPENAI_MODEL"
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
PROVIDER_ERROR_MESSAGE = (
    "AI enhancement provider error. Check OpenAI API key, billing, model access, "
    "or provider availability."
)

AI_ENHANCEMENT_SYSTEM_PROMPT = """You are writing an astrology relationship report from a structured deterministic astrology report.

Rules:
- Do not invent placements, aspects, houses, signs, timing, asteroids, or biographical facts.
- Only interpret patterns that appear in the provided report.
- Keep the same main section headings.
- Preserve the two people's names.
- Do not add compatibility scores.
- Do not say "meant to be."
- Do not make deterministic predictions.
- Do not mention AI, model, prompts, API, technical metadata, or backend details.
- Do not add medical, legal, financial, or crisis advice.
- Do not use raw orb numbers.
- Do not use generic astrology glossary language.
- Avoid generic AI phrases and vague connective language, including: "navigate the complexities", "fosters", "invites both", "highlights", "suggests", and "journey".
- Use direct relational language that names what each person tends to feel, provoke, protect, resist, or reveal.
- Name the central relationship story in the first Overview paragraph.
- Do not over-soften difficult dynamics; describe friction, avoidance, intensity, control, disappointment, or mismatch plainly when the source report supports it.
- Do not overstate certainty.
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
    markdown: str, context: ReportEnhancementContext | None = None
) -> str:
    context_lines = _context_lines(context)
    context_block = (
        "\n".join(context_lines) if context_lines else "- No additional context supplied."
    )
    return f"""Rewrite the deterministic Markdown report below into a warmer, cohesive astrology relationship reading while following every rule in the system instructions.

Available user context:
{context_block}

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
                    "content": build_enhancement_user_prompt(request.markdown, request.context),
                },
            ],
            temperature=0.55,
        )
    except Exception as exc:
        raise EnhancementProviderError(PROVIDER_ERROR_MESSAGE) from exc
    return _extract_markdown(response)
