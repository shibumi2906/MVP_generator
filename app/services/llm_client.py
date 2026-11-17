import json
from dataclasses import dataclass
from typing import Any

from loguru import logger
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

from app.core.assumptions import build_demo_draft
from app.core.errors import GenerationError
from app.core.models import GenerationRequest
from app.core.schemas import Provenance
from app.core.timeouts import GENERATION_TIMEOUT_SECONDS, TOKEN_COUNT_TIMEOUT_SECONDS
from app.services import token_budget
from app.utils.config import get_settings


@dataclass(frozen=True)
class LLMResult:
    data: Any
    provenance: Provenance


def generate_spec(prompt: str, req: GenerationRequest) -> LLMResult:
    settings = get_settings()
    if settings.llm_mode == "mock":
        return LLMResult(
            build_demo_draft(req.product_idea).model_dump(),
            Provenance(
                mode="mock",
                source="demo_template",
                status="demo",
            ),
        )
    if settings.llm_mode != "openai":
        raise GenerationError(
            "invalid_mode",
            "LLM_MODE must be mock or openai.",
            mode=settings.llm_mode,
            status_code=503,
        )
    if not settings.openai_api_key:
        raise GenerationError(
            "missing_api_key", "OpenAI mode requires OPENAI_API_KEY on the server.", status_code=503
        )
    try:
        with OpenAI(
            api_key=settings.openai_api_key, timeout=GENERATION_TIMEOUT_SECONDS, max_retries=0
        ) as client:
            text_format = {"format": {"type": "json_object"}}
            reasoning_options = (
                {"reasoning": {"effort": "low"}}
                if settings.openai_model.startswith(("gpt-5", "gpt-6"))
                else {}
            )
            counted = client.responses.input_tokens.count(
                model=settings.openai_model,
                input=prompt,
                text=text_format,
                timeout=TOKEN_COUNT_TIMEOUT_SECONDS,
                **reasoning_options,
            )
            day, reserved, output_limit = token_budget.reserve(counted.input_tokens)
            response = client.responses.create(
                model=settings.openai_model,
                input=prompt,
                text=text_format,
                max_output_tokens=output_limit,
                **reasoning_options,
            )
            if response.usage is not None:
                token_budget.settle(day, reserved, response.usage.total_tokens)
        if response.status != "completed" or not response.output_text:
            raise GenerationError(
                "incomplete_response",
                "OpenAI did not return a complete specification. Please retry.",
            )
        raw = json.loads(response.output_text)
    except GenerationError:
        raise
    except APITimeoutError as exc:
        raise GenerationError(
            "provider_timeout", "OpenAI timed out. Please retry.", status_code=504
        ) from exc
    except RateLimitError as exc:
        raise GenerationError(
            "provider_rate_limit",
            "OpenAI rate or quota limit reached. Check your account and retry.",
            status_code=503,
        ) from exc
    except APIConnectionError as exc:
        raise GenerationError(
            "provider_unavailable", "Could not connect to OpenAI. Please retry.", status_code=503
        ) from exc
    except APIStatusError as exc:
        logger.bind(channel="llm").warning("OpenAI request failed status={}", exc.status_code)
        raise GenerationError(
            "provider_error",
            "OpenAI rejected the generation request. Check the server configuration.",
        ) from exc
    except (ValueError, TypeError) as exc:
        raise GenerationError(
            "invalid_provider_response", "OpenAI returned an invalid JSON response. Please retry."
        ) from exc
    except Exception as exc:
        logger.bind(channel="llm").error("OpenAI client failed type={}", type(exc).__name__)
        raise GenerationError(
            "provider_error",
            "OpenAI generation failed. Please retry or check the server configuration.",
        ) from exc
    return LLMResult(
        raw,
        Provenance(mode="openai", source="openai", status="generated", model=settings.openai_model),
    )
