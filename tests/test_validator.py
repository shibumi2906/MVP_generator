import pytest
from pydantic import ValidationError

from app.core.assumptions import build_demo_draft
from app.core.errors import GenerationError
from app.core.schemas import SpecBundle
from app.core.validators import validate_spec_bundle


def draft():
    return build_demo_draft("A product idea for the validator").model_dump()


def test_valid_contract_renders_consistent_documents():
    raw = draft()
    raw["contract"]["entities"][0]["fields"].append({"name": "priority", "type": "integer"})
    raw["contract"]["endpoints"][0]["request_fields"].append("priority")
    bundle = validate_spec_bundle(raw, mode="openai")
    assert "integer priority" in bundle.data_model.mermaid_erd
    assert "priority: integer" in bundle.api_spec.content
    assert "POST /items" in " ".join(bundle.tasks.day2_3)


@pytest.mark.parametrize(
    "mutation, message",
    [
        (lambda c: c["endpoints"][0].update(entity="Ghost"), "unknown entity"),
        (lambda c: c["endpoints"][0]["request_fields"].append("ghost"), "unknown field"),
        (lambda c: c["endpoints"][0]["response_fields"].append("ghost"), "unknown field"),
        (
            lambda c: c["entities"][0]["fields"][1].update(references="Ghost.id"),
            "unknown reference",
        ),
        (
            lambda c: c["entities"][0]["fields"][1].update(references="Item.title"),
            "primary key type",
        ),
        (lambda c: c["entities"].append(c["entities"][0]), "names must be unique"),
        (
            lambda c: c["entities"][0]["fields"].append(c["entities"][0]["fields"][0]),
            "field names must be unique",
        ),
        (lambda c: c["endpoints"].append(c["endpoints"][0]), "pairs must be unique"),
        (
            lambda c: c["entities"][0]["fields"][0].update(primary_key=False),
            "primary key is required",
        ),
        (lambda c: c["tasks"][0]["entities"].append("Ghost"), "unknown entity"),
        (lambda c: c["tasks"][0]["endpoints"].append("DELETE /ghost"), "unknown endpoint"),
        (lambda c: [t.update(endpoints=[]) for t in c["tasks"]], "without implementation tasks"),
        (lambda c: c["tasks"].pop(0), "Tasks must cover"),
        (lambda c: c["endpoints"][0]["request_fields"].append("title"), "duplicate API fields"),
    ],
)
def test_inconsistent_contract_is_rejected(mutation, message):
    raw = draft()
    mutation(raw["contract"])
    with pytest.raises(GenerationError) as error:
        validate_spec_bundle(raw, mode="openai")
    assert error.value.code == "invalid_specification"
    assert message in " ".join(error.value.issues)
    assert error.value.detail()["used_fallback"] is False


@pytest.mark.parametrize("raw", [{}, None, [], {"title": ""}])
def test_invalid_output_has_no_fallback(raw):
    with pytest.raises(GenerationError):
        validate_spec_bundle(raw, mode="openai")


def test_task_endpoint_must_belong_to_task_entity():
    raw = draft()
    raw["contract"]["entities"].append(
        {
            "name": "User",
            "description": "A user",
            "fields": [{"name": "id", "type": "string", "primary_key": True}],
        }
    )
    raw["contract"]["tasks"][1]["entities"] = ["User"]
    with pytest.raises(GenerationError, match="consistency") as error:
        validate_spec_bundle(raw, mode="openai")
    assert "endpoint entity must be listed" in " ".join(error.value.issues)


def test_valid_foreign_key_is_rendered():
    raw = draft()
    raw["contract"]["entities"].append(
        {
            "name": "User",
            "description": "A user",
            "fields": [{"name": "id", "type": "string", "primary_key": True}],
        }
    )
    raw["contract"]["entities"][0]["fields"].append(
        {"name": "user_id", "type": "string", "references": "User.id"}
    )
    raw["contract"]["tasks"][0]["entities"].append("User")
    result = validate_spec_bundle(raw, mode="openai")
    assert "string user_id FK" in result.data_model.mermaid_erd
    assert 'User ||--o{ Item : "user_id"' in result.data_model.mermaid_erd


@pytest.mark.parametrize(
    "section, field, value",
    [
        ("data_model", "mermaid_erd", "erDiagram\n  Ghost {\n string id\n }"),
        ("data_model", "entities", ["Ghost: does not exist"]),
        ("api_spec", "content", "POST /ghost"),
        ("tasks", "day1", ["Implement an unrelated entity"]),
    ],
)
def test_saved_document_drift_is_rejected(section, field, value):
    bundle = validate_spec_bundle(draft(), mode="openai").model_dump()
    bundle[section][field] = value
    with pytest.raises(ValidationError, match="does not match"):
        SpecBundle.model_validate(bundle)


def test_entity_only_in_done_checklist_has_no_implementation_coverage():
    raw = draft()
    raw["contract"]["entities"].append(
        {
            "name": "User",
            "description": "A user",
            "fields": [{"name": "id", "type": "string", "primary_key": True}],
        }
    )
    raw["contract"]["tasks"][-1]["entities"].append("User")
    with pytest.raises(GenerationError) as error:
        validate_spec_bundle(raw, mode="openai")
    assert "Entities without implementation tasks: User" in str(error.value.issues)


def test_unknown_path_parameter_is_rejected():
    raw = draft()
    raw["contract"]["endpoints"][0]["path"] = "/items/{ghost}"
    with pytest.raises(GenerationError) as error:
        validate_spec_bundle(raw, mode="openai")
    assert "unknown path field ghost" in str(error.value.issues)
