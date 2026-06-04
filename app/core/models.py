from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    product_idea: str = Field(..., min_length=10)
    target_users: str | None = None
    core_user_flow: str | None = None
    constraints: str | None = None
    output_stack: str | None = Field(
        default="FastAPI + SQLite + Streamlit",
        description="Preferred implementation stack",
    )



