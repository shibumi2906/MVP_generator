"""Explicit offline example. Never used to recover a failed provider call."""

from app.core.schemas import GenerationDraft


def build_demo_draft(product_idea: str) -> GenerationDraft:
    return GenerationDraft.model_validate(
        {
            "title": "Idea to first release · Demo",
            "summary": "A generic item tracker demonstrating the starter pack format. This is an offline template, not an AI-generated design for your product.",
            "prd_lite": {
                "problem": f"Explore an MVP for: {product_idea}",
                "target_user": "A small team testing its first product workflow.",
                "scope_in": ["Create items with a title and status", "Browse saved items"],
                "scope_out": ["Authentication", "Billing and external integrations"],
                "user_journey": [
                    "Open the workspace",
                    "Create an item",
                    "Review the saved item list",
                ],
                "nfr": [
                    "Validate incoming titles and status values",
                    "Persist items across application restarts",
                ],
                "open_questions": [
                    "What domain entity should replace the generic Item?",
                    "Which metric demonstrates user value?",
                ],
            },
            "architecture": {
                "components": [
                    "Streamlit workspace",
                    "FastAPI resource API",
                    "SQLite item storage",
                ],
                "data_flow": [
                    "UI sends an Item creation request",
                    "API validates and stores Item",
                    "UI retrieves saved items",
                ],
                "risks": ["This generic demo needs domain-specific design before implementation"],
                "mermaid_diagram": "flowchart LR\n  UI[Streamlit] --> API[FastAPI]\n  API --> DB[(SQLite)]",
            },
            "contract": {
                "entities": [
                    {
                        "name": "Item",
                        "description": "A generic unit of user work",
                        "fields": [
                            {"name": "id", "type": "string", "primary_key": True},
                            {"name": "title", "type": "string"},
                            {"name": "status", "type": "string"},
                        ],
                    }
                ],
                "endpoints": [
                    {
                        "method": "POST",
                        "path": "/items",
                        "summary": "Create an item",
                        "entity": "Item",
                        "request_fields": ["title", "status"],
                        "response_fields": ["id", "title", "status"],
                    },
                    {
                        "method": "GET",
                        "path": "/items",
                        "summary": "List items",
                        "entity": "Item",
                        "request_fields": [],
                        "response_fields": ["id", "title", "status"],
                    },
                ],
                "tasks": [
                    {
                        "phase": "day1",
                        "title": "Create Item storage and validate fields",
                        "entities": ["Item"],
                        "endpoints": [],
                    },
                    {
                        "phase": "day2_3",
                        "title": "Implement item creation and listing",
                        "entities": ["Item"],
                        "endpoints": ["POST /items", "GET /items"],
                    },
                    {
                        "phase": "week1",
                        "title": "Connect the workspace and verify persistence",
                        "entities": ["Item"],
                        "endpoints": ["POST /items", "GET /items"],
                    },
                    {
                        "phase": "done_checklist",
                        "title": "A created item appears in the saved list after restart",
                        "entities": ["Item"],
                        "endpoints": ["POST /items", "GET /items"],
                    },
                ],
            },
            "assumptions": [
                "Explicit mock mode: a deterministic demo template was requested.",
                "The generic Item is illustrative; the brief has not been designed by an LLM.",
                "The demo uses FastAPI, SQLite and Streamlit regardless of the requested stack.",
            ],
        }
    )
