import json

from app.core.schemas import GenerationResponse, Provenance
from app.storage.models import Generation


def read_saved_generation(row: Generation) -> GenerationResponse:
    data = json.loads(row.output_json)
    if "result" in data and "provenance" in data:
        return GenerationResponse.model_validate(data)
    # Older rows have no reliable indication of whether OpenAI actually succeeded.
    return GenerationResponse(
        generation_id=row.id,
        created_at=row.created_at,
        result=data,
        provenance=Provenance(
            mode="unknown", source="legacy_unknown", status="unverified", used_fallback=None
        ),
    )
