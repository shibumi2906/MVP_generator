from typing import Any

from pydantic import ValidationError

from app.core.errors import GenerationError
from app.core.schemas import GenerationDraft, SpecBundle


def validate_spec_bundle(raw: Any, *, mode: str) -> SpecBundle:
    try:
        return GenerationDraft.model_validate(raw).to_bundle()
    except ValidationError as exc:
        issues = [
            f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}"
            for e in exc.errors(include_input=False, include_url=False)
        ]
        raise GenerationError(
            "invalid_specification",
            "The generated documents failed structure or consistency checks. Please retry or refine the brief.",
            mode=mode,
            issues=issues,
        ) from exc
