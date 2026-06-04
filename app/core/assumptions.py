from datetime import datetime

from app.core.schemas import (
    APISpec,
    Architecture,
    DataModel,
    PRDLite,
    SpecBundle,
    TaskPlan,
)


def build_fallback_bundle(product_idea: str, reason: str) -> SpecBundle:
    title = f"MVP for: {product_idea[:60]}"
    summary = (
        "Fallback specification generated because the LLM output was invalid or "
        "could not be parsed. This is a conservative starter pack based only on "
        "the provided product idea."
    )

    prd = PRDLite(
        problem=f"Enable a minimal viable product for: {product_idea}",
        target_user="Early adopters and internal stakeholders exploring the concept.",
        scope_in=[
            "Core user flow from first contact to main value moment",
            "Basic authentication and session handling if applicable",
            "Minimal analytics and logging",
        ],
        scope_out=[
            "Advanced growth/marketing automation",
            "Complex integrations beyond simple REST APIs",
        ],
        user_journey=[
            "User discovers the product or is invited.",
            "User understands the value proposition on a simple landing.",
            "User completes the main flow that demonstrates the core value.",
        ],
        nfr=[
            "Fast iteration speed over perfect scalability.",
            "Clear observability for debugging in early stages.",
        ],
        open_questions=[
            "What is the precise success metric for the first week?",
            "Which external systems are truly required for an MVP launch?",
        ],
    )

    architecture = Architecture(
        components=[
            "FastAPI backend for API endpoints",
            "SQLite database for persistence",
            "Streamlit frontend for rapid UI iteration",
        ],
        data_flow=[
            "User interacts with Streamlit UI.",
            "UI sends requests to FastAPI backend.",
            "Backend reads/writes to SQLite and returns structured responses.",
        ],
        risks=[
            "SQLite may not scale for heavy concurrent usage.",
            "LLM-based generation may introduce inaccuracies.",
        ],
        mermaid_diagram=(
            "flowchart TD\n"
            "  user[User] --> ui[Streamlit UI]\n"
            "  ui --> api[FastAPI Backend]\n"
            "  api --> db[(SQLite DB)]\n"
            "  api --> llm[LLM Service]\n"
        ),
    )

    data_model = DataModel(
        entities=[
            "Generation: stores input idea, generated spec bundle, timestamps.",
            "User (implicit): represented via request, not persisted.",
        ],
        mermaid_erd=(
            "erDiagram\n"
            "  GENERATION {\n"
            "    string id\n"
            "    datetime created_at\n"
            "    string title\n"
            "    text input_json\n"
            "    text output_json\n"
            "  }\n"
        ),
    )

    api_spec = APISpec(
        format="markdown",
        content=(
            "### Endpoints\n\n"
            "- `GET /health` – health check.\n"
            "- `POST /generate` – generate MVP starter pack from product idea.\n"
            "- `GET /history` – list previous generations.\n"
            "- `POST /export` – export a generation as a ZIP bundle.\n"
        ),
    )

    tasks = TaskPlan(
        day1=[
            "Clarify core value proposition and main user flow.",
            "Implement basic FastAPI skeleton and health endpoint.",
        ],
        day2_3=[
            "Wire LLM or mock service to generate structured specs.",
            "Store generations in SQLite and expose history endpoint.",
        ],
        week1=[
            "Refine prompts and validation rules based on feedback.",
            "Polish Streamlit UI and export ZIP experience.",
        ],
        done_checklist=[
            "User can enter an idea and see a structured MVP spec bundle.",
            "User can export the bundle as a ZIP.",
        ],
    )

    assumptions = [
        reason,
        "Fallback spec constructed from a generic MVP template.",
        f"Generation time: {datetime.utcnow().isoformat()}Z",
    ]

    return SpecBundle(
        title=title,
        summary=summary,
        prd_lite=prd,
        architecture=architecture,
        data_model=data_model,
        api_spec=api_spec,
        tasks=tasks,
        assumptions=assumptions,
    )



