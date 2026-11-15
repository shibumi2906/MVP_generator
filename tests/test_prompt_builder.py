from app.core.models import GenerationRequest
from app.services.prompt_builder import build_master_prompt


def test_prompt_contains_output_only_json():
    req = GenerationRequest(product_idea="A simple test idea for MVP.")
    prompt = build_master_prompt(req)
    assert "Output ONLY JSON" in prompt
