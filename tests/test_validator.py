from app.core.assumptions import build_fallback_bundle
from app.core.schemas import SpecBundle
from app.core.validators import validate_or_fallback_spec_bundle


def _good_bundle_dict() -> dict:
    bundle = build_fallback_bundle(
        product_idea="Test product idea for validator.",
        reason="Test reason.",
    )
    return bundle.model_dump()


def test_validator_accepts_good_bundle():
    raw = _good_bundle_dict()
    bundle, used_fallback = validate_or_fallback_spec_bundle(
        raw, product_idea="Test product idea for validator."
    )
    assert isinstance(bundle, SpecBundle)
    assert used_fallback is False


def test_validator_rejects_bad_bundle_and_uses_fallback():
    raw = {"title": "", "summary": "", "assumptions": []}
    bundle, used_fallback = validate_or_fallback_spec_bundle(
        raw, product_idea="Broken idea"
    )
    assert isinstance(bundle, SpecBundle)
    assert used_fallback is True
    assert "LLM output invalid; fallback used." in bundle.assumptions



