import json
import time
from typing import Any, Dict, Optional

from loguru import logger

from app.core.assumptions import build_fallback_bundle
from app.core.models import GenerationRequest
from app.utils.config import get_settings

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore


def _mock_spec(req: GenerationRequest, reason: str) -> Dict[str, Any]:
    """Deterministic SpecBundle JSON for offline/demo usage."""
    bundle = build_fallback_bundle(
        product_idea=req.product_idea,
        reason=reason,
    )
    return json.loads(bundle.model_dump_json())


def _normalize_mode(mode: Optional[str]) -> str:
    m = (mode or "").strip().lower()
    if m in {"", "default"}:
        return "auto"
    return m


def generate_spec(prompt: str, req: GenerationRequest) -> Dict[str, Any]:
    """
    Single LLM call entrypoint.
    Returns dict that MUST be a JSON object matching SpecBundle keys.
    """
    settings = get_settings()
    start = time.perf_counter()

    mode = _normalize_mode(getattr(settings, "llm_mode", None))
    key_present = bool(getattr(settings, "openai_api_key", None))
    sdk_present = OpenAI is not None
    model = getattr(settings, "openai_model", "unknown")

    llm_log = logger.bind(channel="llm")
    llm_log.info(
        "LLM init mode={} key_present={} openai_sdk={} model={} prompt_len={}",
        mode,
        key_present,
        sdk_present,
        model,
        len(prompt),
    )

    # AUTO mode: use OpenAI if possible, else mock
    if mode == "auto":
        mode = "openai" if (key_present and sdk_present) else "mock"

    # MOCK mode
    if mode == "mock":
        reason = (
            "LLM used MOCK spec. "
            f"(mode={getattr(settings, 'llm_mode', None)!r}, key_present={key_present}, openai_sdk={sdk_present})"
        )
        data = _mock_spec(req, reason=reason)
        duration_ms = (time.perf_counter() - start) * 1000
        llm_log.info("LLM MOCK done duration_ms={:.2f}", duration_ms)
        return data

    # OPENAI mode: do NOT silently fallback
    if mode != "openai":
        raise RuntimeError(
            f"Unknown LLM_MODE={getattr(settings, 'llm_mode', None)!r}. Use 'openai', 'mock', or 'auto'."
        )

    if not sdk_present:
        raise RuntimeError("OpenAI SDK is not installed or failed to import. Install: pip install -U openai")

    if not key_present:
        raise RuntimeError("OPENAI_API_KEY is missing. Set it in .env and restart backend.")

    client = OpenAI(api_key=settings.openai_api_key)

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Return ONLY a valid JSON object. No markdown. No code fences.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = resp.choices[0].message.content or "{}"
        raw = json.loads(content)
        success = True

    except Exception as exc:
        llm_log.exception("LLM OPENAI call failed")
        raw = _mock_spec(req, reason=f"OpenAI call failed: {exc}")
        success = False

    duration_ms = (time.perf_counter() - start) * 1000
    llm_log.info("LLM OPENAI done duration_ms={:.2f} success={}", duration_ms, success)
    return raw




