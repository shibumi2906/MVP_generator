from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator, model_validator


def _ensure_non_empty(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("must be a non-empty string")
    return value


def _ensure_non_empty_list(values: List[str]) -> List[str]:
    if not values:
        raise ValueError("list must not be empty")
    return [_ensure_non_empty(v) for v in values]


class PRDLite(BaseModel):
    problem: str
    target_user: str
    scope_in: List[str]
    scope_out: List[str]
    user_journey: List[str]
    nfr: List[str]
    open_questions: List[str]

    _non_empty_problem = field_validator("problem")(_ensure_non_empty)
    _non_empty_target_user = field_validator("target_user")(_ensure_non_empty)
    _non_empty_scope_in = field_validator("scope_in")(_ensure_non_empty_list)
    _non_empty_scope_out = field_validator("scope_out")(_ensure_non_empty_list)
    _non_empty_user_journey = field_validator("user_journey")(_ensure_non_empty_list)
    _non_empty_nfr = field_validator("nfr")(_ensure_non_empty_list)
    _non_empty_open_questions = field_validator("open_questions")(
        _ensure_non_empty_list
    )


class Architecture(BaseModel):
    components: List[str]
    data_flow: List[str]
    risks: List[str]
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
    entities: List[str]
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
    day1: List[str]
    day2_3: List[str]
    week1: List[str]
    done_checklist: List[str]

    _non_empty_day1 = field_validator("day1")(_ensure_non_empty_list)
    _non_empty_day2_3 = field_validator("day2_3")(_ensure_non_empty_list)
    _non_empty_week1 = field_validator("week1")(_ensure_non_empty_list)
    _non_empty_done_checklist = field_validator("done_checklist")(
        _ensure_non_empty_list
    )


class SpecBundle(BaseModel):
    title: str
    summary: str
    prd_lite: PRDLite
    architecture: Architecture
    data_model: DataModel
    api_spec: APISpec
    tasks: TaskPlan
    assumptions: List[str]

    _non_empty_title = field_validator("title")(_ensure_non_empty)
    _non_empty_summary = field_validator("summary")(_ensure_non_empty)
    _non_empty_assumptions = field_validator("assumptions")(_ensure_non_empty_list)

    @model_validator(mode="after")
    def _check_all_strings_non_empty(self) -> "SpecBundle":  # type: ignore[override]
        # Deep validation is mostly handled by field validators; this hook is a safety net.
        return self


class GenerationResponse(BaseModel):
    generation_id: str
    created_at: datetime
    result: SpecBundle


class HistoryItem(BaseModel):
    generation_id: str
    created_at: datetime
    title: str


class ExportRequest(BaseModel):
    generation_id: str = Field(..., min_length=1)



