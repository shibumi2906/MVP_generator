import re
from datetime import datetime, timezone
from typing import Optional, Tuple

from loguru import logger
from sqlalchemy.orm import Session

from app.core.models import GenerationRequest
from app.core.schemas import GenerationResponse
from app.core.validators import validate_or_fallback_spec_bundle
from app.services.llm_client import generate_spec
from app.services.prompt_builder import build_master_prompt
from app.storage import repository


def _detect_language_from_text(text: str) -> str:
    """
    Minimal heuristic language detector (no extra dependencies).
    Returns:
      - "ru" if Cyrillic dominates
      - otherwise "en"
    """
    if not text:
        return "en"

    cyr = len(re.findall(r"[А-Яа-яЁё]", text))
    lat = len(re.findall(r"[A-Za-z]", text))

    if cyr > 0 and cyr >= lat:
        return "ru"
    return "en"


def generate_mvp(
    db: Session,
    req: GenerationRequest,
    preferred_language: Optional[str] = None,
) -> Tuple[GenerationResponse, bool]:
    """
    Orchestrates prompt -> LLM -> validation -> save -> response.
    Returns (GenerationResponse, used_fallback).

    Language behavior:
    - If preferred_language is provided, enforce it in the prompt
    - Otherwise detect from req.product_idea
    """
    lang = preferred_language or _detect_language_from_text(req.product_idea)

    prompt = build_master_prompt(req, preferred_language=lang)
    raw = generate_spec(prompt, req)

    bundle, used_fallback = validate_or_fallback_spec_bundle(raw, product_idea=req.product_idea)

    generation_id = _generate_id()
    created_at = datetime.now(timezone.utc)

    repository.save_generation(
        db=db,
        generation_id=generation_id,
        created_at=created_at,
        title=bundle.title or "Untitled",
        input_json=req.model_dump_json(),
        output_json=bundle.model_dump_json(),
    )

    logger.info("Generated MVP spec generation_id={} fallback={} lang={}", generation_id, used_fallback, lang)

    response = GenerationResponse(generation_id=generation_id, created_at=created_at, result=bundle)
    return response, used_fallback


def _generate_id() -> str:
    import uuid
    return str(uuid.uuid4())
