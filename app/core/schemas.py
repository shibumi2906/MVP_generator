from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.contracts import DocumentContract


def _ensure_non_empty(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("must be a non-empty string")
    return value


def _ensure_non_empty_list(values: list[str]) -> list[str]:
    if not values:
        raise ValueError("list must not be empty")
    return [_ensure_non_empty(v) for v in values]


class PRDLite(BaseModel):
    problem: str
    target_user: str
    scope_in: list[str]
    scope_out: list[str]
    user_journey: list[str]
    nfr: list[str]
    open_questions: list[str]

    _non_empty_problem = field_validator("problem")(_ensure_non_empty)
    _non_empty_target_user = field_validator("target_user")(_ensure_non_empty)
    _non_empty_scope_in = field_validator("scope_in")(_ensure_non_empty_list)
    _non_empty_scope_out = field_validator("scope_out")(_ensure_non_empty_list)
    _non_empty_user_journey = field_validator("user_journey")(_ensure_non_empty_list)
    _non_empty_nfr = field_validator("nfr")(_ensure_non_empty_list)
    _non_empty_open_questions = field_validator("open_questions")(_ensure_non_empty_list)


class Architecture(BaseModel):
    components: list[str]
    data_flow: list[str]
    risks: list[str]
    mermaid_diagram: str

    _non_empty_components = field_validator("components")(_ensure_non_empty_list)
    _non_empty_data_flow = field_validator("data_flow")(_ensure_non_empty_list)
    _non_empty_risks = field_validator("risks")(_ensure_non_empty_list)
    _non_empty_mermaid = field_validator("mermaid_diagram")(_ensure_non_empty)

    @field_validator("mermaid_diagram")
    @classmethod
    def _must_contain_flowchart(cls, v: str) -> str:
        if "flowchart" not in v:
            raise ValueError("mermaid_diagram must contain 'flowchart'")
        return v


class DataModel(BaseModel):
    entities: list[str]
    mermaid_erd: str

    _non_empty_entities = field_validator("entities")(_ensure_non_empty_list)
    _non_empty_mermaid_erd = field_validator("mermaid_erd")(_ensure_non_empty)

    @field_validator("mermaid_erd")
    @classmethod
    def _must_contain_erdiagram(cls, v: str) -> str:
        if "erDiagram" not in v:
            raise ValueError("mermaid_erd must contain 'erDiagram'")
        return v


class APISpec(BaseModel):
    format: str
    content: str

    _non_empty_format = field_validator("format")(_ensure_non_empty)
    _non_empty_content = field_validator("content")(_ensure_non_empty)

    @field_validator("format")
    @classmethod
    def _format_allowed(cls, v: str) -> str:
        if v not in {"yaml", "markdown"}:
            raise ValueError("format must be 'yaml' or 'markdown'")
        return v


class TaskPlan(BaseModel):
    day1: list[str]
    day2_3: list[str]
    week1: list[str]
    done_checklist: list[str]

    _non_empty_day1 = field_validator("day1")(_ensure_non_empty_list)
    _non_empty_day2_3 = field_validator("day2_3")(_ensure_non_empty_list)
    _non_empty_week1 = field_validator("week1")(_ensure_non_empty_list)
    _non_empty_done_checklist = field_validator("done_checklist")(_ensure_non_empty_list)


class SpecBundle(BaseModel):
    title: str
    summary: str
    prd_lite: PRDLite
    architecture: Architecture
    data_model: DataModel
    api_spec: APISpec
    tasks: TaskPlan
    assumptions: list[str]
    contract: DocumentContract | None = None

    _non_empty_title = field_validator("title")(_ensure_non_empty)
    _non_empty_summary = field_validator("summary")(_ensure_non_empty)
    _non_empty_assumptions = field_validator("assumptions")(_ensure_non_empty_list)

    @model_validator(mode="after")
    def check_document_views(self) -> "SpecBundle":
        if self.contract is None:
            return self
        expected_entities = [f"{e.name}: {e.description}" for e in self.contract.entities]
        if (
            self.data_model.entities != expected_entities
            or self.data_model.mermaid_erd != self.contract.render_erd()
        ):
            raise ValueError("Data model does not match the shared contract")
        if (
            self.api_spec.format != "markdown"
            or self.api_spec.content != self.contract.render_api()
        ):
            raise ValueError("API document does not match the shared contract")
        for phase in ["day1", "day2_3", "week1", "done_checklist"]:
            if getattr(self.tasks, phase) != self.contract.render_tasks(phase):
                raise ValueError(f"Task plan {phase} does not match the shared contract")
        return self


class GenerationResponse(BaseModel):
    generation_id: str
    created_at: datetime
    result: SpecBundle
    provenance: "Provenance"


class Provenance(BaseModel):
    mode: Literal["mock", "openai", "unknown"]
    source: Literal["demo_template", "openai", "legacy_unknown"]
    status: Literal["demo", "generated", "unverified"]
    model: str | None = None
    used_fallback: bool | None = False
    consistency_checked: bool = False


class GenerationDraft(BaseModel):
    """LLM output; document views are rendered from the validated contract."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    prd_lite: PRDLite
    architecture: Architecture
    contract: DocumentContract
    assumptions: list[str]

    def to_bundle(self) -> SpecBundle:
        return SpecBundle(
            title=self.title,
            summary=self.summary,
            prd_lite=self.prd_lite,
            architecture=self.architecture,
            data_model=DataModel(
                entities=[f"{e.name}: {e.description}" for e in self.contract.entities],
                mermaid_erd=self.contract.render_erd(),
            ),
            api_spec=APISpec(format="markdown", content=self.contract.render_api()),
            tasks=TaskPlan(
                **{
                    phase: self.contract.render_tasks(phase)
                    for phase in ["day1", "day2_3", "week1", "done_checklist"]
                }
            ),
            assumptions=self.assumptions,
            contract=self.contract,
        )


class HistoryItem(BaseModel):
    generation_id: str
    created_at: datetime
    title: str
    provenance: Provenance


class ExportRequest(BaseModel):
    generation_id: str = Field(..., min_length=1)
