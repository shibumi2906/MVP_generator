from typing import Any, Tuple

from loguru import logger
from pydantic import ValidationError

from app.core.assumptions import build_fallback_bundle
from app.core.schemas import SpecBundle


def validate_or_fallback_spec_bundle(
    raw: Any, product_idea: str
) -> Tuple[SpecBundle, bool]:
    """
    Try to validate raw data into SpecBundle.
    Returns (bundle, used_fallback).
    """
    try:
        bundle = SpecBundle.model_validate(raw)
        return bundle, False
    except ValidationError as exc:
        logger.warning(
            "SpecBundle validation failed, using fallback: {}", exc,
        )
        reason = "LLM output invalid; fallback used."
        fallback = build_fallback_bundle(product_idea=product_idea, reason=reason)
        return fallback, True



