from textwrap import dedent

from app.core.models import GenerationRequest


def build_master_prompt(req: GenerationRequest, preferred_language: str = "en") -> str:
    """
    Master prompt for Spec -> MVP Generator.

    NOTE:
    We enforce language based on the language of req.product_idea itself.
    preferred_language is kept for backward compatibility, but the model MUST follow
    the language of product_idea, not this parameter.
    """
    base = dedent(
        f"""
        You are an assistant that generates a complete MVP developer starter pack.

        CRITICAL LANGUAGE RULE:
        - Detect the language of the Product idea text below.
        - Write ALL textual VALUES strictly in that same language.
        - Do NOT mix languages.
        - JSON KEYS must remain exactly as specified (English keys). Only VALUES change language.

        Product idea:
        {req.product_idea}

        Target users:
        {req.target_users or "Not specified; infer reasonable early adopters."}

        Core user flow:
        {req.core_user_flow or "Not specified; infer a simple end-to-end flow."}

        Constraints:
        {req.constraints or "Not specified; assume typical MVP constraints (timeboxed, small team)."}

        Desired implementation stack:
        {req.output_stack or "FastAPI + SQLite + Streamlit"}

        Use these fields when possible. If anything is missing, clearly state your
        assumptions in the 'assumptions' field.

        Output ONLY JSON. Do NOT use markdown, code fences, comments, or prose.

        The JSON MUST have exactly this structure (keys and nesting):

        {{
          "title": string,
          "summary": string,
          "prd_lite": {{
            "problem": string,
            "target_user": string,
            "scope_in": [string],
            "scope_out": [string],
            "user_journey": [string],
            "nfr": [string],
            "open_questions": [string]
          }},
          "architecture": {{
            "components": [string],
            "data_flow": [string],
            "risks": [string],
            "mermaid_diagram": string
          }},
          "data_model": {{
            "entities": [string],
            "mermaid_erd": string
          }},
          "api_spec": {{
            "format": "yaml" or "markdown",
            "content": string
          }},
          "tasks": {{
            "day1": [string],
            "day2_3": [string],
            "week1": [string],
            "done_checklist": [string]
          }},
          "assumptions": [string]
        }}

        Requirements:
        - All strings must be non-empty.
        - All lists must be non-empty.
        - 'mermaid_diagram' MUST be a mermaid flowchart definition and MUST contain the word "flowchart".
        - 'mermaid_erd' MUST be a mermaid ER diagram definition and MUST contain the word "erDiagram".
        - Use simple, implementation-oriented language suitable for engineers.
        - Include any guesses or missing information under 'assumptions'.
        """
    ).strip()
    return base


