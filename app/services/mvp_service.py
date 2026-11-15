from datetime import UTC, datetime

from loguru import logger
from sqlalchemy.orm import Session

from app.core.models import GenerationRequest
from app.core.schemas import GenerationResponse
from app.core.validators import validate_spec_bundle
from app.services.llm_client import generate_spec
from app.services.prompt_builder import build_master_prompt
from app.storage import repository


def generate_mvp(db: Session, req: GenerationRequest) -> GenerationResponse:
    """
    Orchestrates prompt -> LLM -> validation -> save -> response.
    Provider and validation failures propagate; only validated results are saved.
    """
    prompt = build_master_prompt(req)
    llm_result = generate_spec(prompt, req)
    bundle = validate_spec_bundle(llm_result.data, mode=llm_result.provenance.mode)
    provenance = llm_result.provenance.model_copy(update={"consistency_checked": True})

    generation_id = _generate_id()
    created_at = datetime.now(UTC)
    response = GenerationResponse(
        generation_id=generation_id,
        created_at=created_at,
        result=bundle,
        provenance=provenance,
    )

    repository.save_generation(
        db=db,
        generation_id=generation_id,
        created_at=created_at,
        title=bundle.title or "Untitled",
        input_json=req.model_dump_json(),
        output_json=response.model_dump_json(),
    )

    logger.info(
        "Generated MVP spec generation_id={} source={}",
        generation_id,
        provenance.source,
    )

    return response


def _generate_id() -> str:
    # uuid4 without importing uuid to keep this function compact
    import uuid

    return str(uuid.uuid4())
