import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

from app.ui.components import (
    render_api_spec,
    render_architecture,
    render_assumptions,
    render_erd,
    render_prd,
    render_tasks,
)

load_dotenv()
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
st.set_page_config(page_title="MVP Generator · Product workspace", page_icon="◈", layout="wide")
st.markdown(
    """
<style>
    .stApp { background: #f5f6fa; color: #19243b; }
    .block-container { max-width: 1280px; padding-top: 2.5rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { background: #e9edf5; }
    h1, h2, h3 { letter-spacing: -.035em; }
    h1 { font-size: 3rem !important; line-height: 1.12 !important; }
    [data-testid="stForm"] { background: white; border: 1px solid #dce2ee; border-radius: 16px; padding: 1.5rem; }
    [data-testid="stMetric"] { background: white; border: 1px solid #dce2ee; border-radius: 12px; padding: 1rem; }
    .eyebrow { color: #5b5bd6; letter-spacing: .14em; font-size: .75rem; font-weight: 700; }
    .intro { color: #58657d; font-size: 1.1rem; max-width: 680px; margin-bottom: 2rem; }
    .stButton button[kind="primary"], .stFormSubmitButton button { border-radius: 10px; }
</style>
""",
    unsafe_allow_html=True,
)


def api_request(method: str, path: str, **kwargs: Any) -> requests.Response | None:
    try:
        response = requests.request(method, f"{API_BASE}{path}", timeout=65, **kwargs)
        if 200 <= response.status_code < 300:
            return response
        try:
            detail = response.json().get("detail", {})
        except ValueError:
            detail = {}
        if isinstance(detail, dict):
            st.error(detail.get("message", f"Request failed (HTTP {response.status_code})."))
            if detail.get("code"):
                st.caption(
                    f"{detail['code']} · mode: {detail.get('mode', 'unknown')} · no fallback result created"
                )
            if detail.get("issues"):
                with st.expander("Consistency check details"):
                    for issue in detail["issues"]:
                        st.write(issue)
        else:
            st.error(f"Request failed (HTTP {response.status_code}). Check the input and retry.")
    except requests.RequestException:
        st.error("The API is unavailable or the request timed out. Start the backend and retry.")
    return None


def show_provenance(data: dict) -> None:
    provenance = data.get("provenance", {})
    status = provenance.get("status", "unverified")
    if status == "demo":
        st.info(
            "Demo template · Offline example, not an AI-generated specification for your product."
        )
    elif status == "generated":
        st.success("Generated with OpenAI · Structure and document references checked.")
    else:
        st.warning(
            "Legacy result · Origin is unknown and document consistency has not been verified."
        )
    st.caption(
        f"Source: {provenance.get('source', 'unknown')} · Model: {provenance.get('model') or '—'} · Saved: {data.get('created_at', '')}"
    )


with st.sidebar:
    st.markdown("## ◈ MVP Generator")
    st.caption("PRODUCT DEVELOPMENT WORKSPACE")
    st.divider()
    try:
        health_response = requests.get(f"{API_BASE}/health", timeout=3)
        health_response.raise_for_status()
        health = health_response.json()
        mode = health.get("llm_mode", "unknown")
        st.markdown(f"**Server mode: {mode.upper()}**")
        if mode == "mock":
            st.info("Offline demo. The same generic example is used for every brief.")
        elif not health.get("generation_ready"):
            st.warning("Generation is not configured. Check the server environment.")
        else:
            st.caption("Live generation via OpenAI. Provider failures are shown explicitly.")
    except (requests.RequestException, ValueError):
        st.warning("Backend unavailable")
    st.divider()
    st.markdown("### Recent packs")
    if st.button("Refresh history", use_container_width=True):
        st.session_state.pop("history", None)
    if "history" not in st.session_state:
        history_response = api_request("GET", "/history?limit=8")
        st.session_state["history"] = (
            history_response.json() if history_response is not None else []
        )
    for item in st.session_state["history"]:
        label = f"{item.get('provenance', {}).get('status', 'unverified')} · {item['title']}"
        if st.button(label, key=item["generation_id"], use_container_width=True):
            detail_response = api_request("GET", f"/history/{item['generation_id']}")
            if detail_response is not None:
                st.session_state["last_generation"] = detail_response.json()
                st.session_state.pop("zip_bytes", None)
    if not st.session_state["history"]:
        st.caption("Your saved specifications will appear here.")
    st.divider()
    st.caption("FastAPI / SQLite / Streamlit")

st.markdown('<div class="eyebrow">FROM IDEA TO IMPLEMENTATION</div>', unsafe_allow_html=True)
st.title("Give your next idea a clear starting point.")
st.markdown(
    '<p class="intro">Turn a product brief into a practical starter pack: requirements, architecture, a shared data contract and a plan for the first release.</p>',
    unsafe_allow_html=True,
)

left, right = st.columns([1.65, 1], gap="large")
with left:
    with st.form("mvp_form"):
        st.subheader("01 / Define the brief")
        product_idea = st.text_area(
            "Product idea",
            placeholder="A booking workspace for independent tutors to manage students and lessons…",
            height=125,
        )
        target_users = st.text_input(
            "Who is it for?", placeholder="Independent tutors and small teaching teams"
        )
        with st.expander("Add workflow, constraints and stack"):
            core_user_flow = st.text_area(
                "Core user flow",
                placeholder="Create a student → schedule a lesson → review the week",
            )
            constraints = st.text_area(
                "Constraints", placeholder="One developer, one week, no paid integrations"
            )
            output_stack = st.text_input(
                "Implementation stack", value="FastAPI + SQLite + Streamlit"
            )
        submitted = st.form_submit_button(
            "Build starter pack →", type="primary", use_container_width=True
        )
with right:
    st.subheader("A useful first draft")
    st.markdown("**01 · Product clarity**  \nProblem, audience, scope and open questions.")
    st.markdown(
        "**02 · Connected documents**  \nERD and API fields share one validated contract. Tasks reference the same entities and endpoints."
    )
    st.markdown(
        "**03 · Ready to take with you**  \nSaved history and a ZIP of Markdown documents, diagrams and provenance."
    )
    st.caption(
        "Review generated plans before implementation. Checks validate references and coverage; product decisions still need your judgment."
    )

if submitted:
    # Clear the previous result so a failed request cannot look like a fresh success.
    st.session_state.pop("last_generation", None)
    st.session_state.pop("zip_bytes", None)
    if len(product_idea.strip()) < 10:
        st.error("Describe your product in at least 10 characters.")
    else:
        with st.spinner("Building and checking your starter pack…"):
            response = api_request(
                "POST",
                "/generate",
                json={
                    "product_idea": product_idea,
                    "target_users": target_users or None,
                    "core_user_flow": core_user_flow or None,
                    "constraints": constraints or None,
                    "output_stack": output_stack or None,
                },
            )
        if response is not None:
            st.session_state["last_generation"] = response.json()
            st.session_state.pop("history", None)
            st.rerun()

last = st.session_state.get("last_generation")
if last:
    st.divider()
    st.subheader("02 / Your starter pack")
    show_provenance(last)
    result = last["result"]
    st.markdown(f"### {result['title']}")
    st.write(result["summary"])
    contract = result.get("contract") or {}
    metrics = st.columns(3)
    metrics[0].metric("Entities", len(contract.get("entities", [])))
    metrics[1].metric("API endpoints", len(contract.get("endpoints", [])))
    metrics[2].metric(
        "Implementation tasks",
        len([t for t in contract.get("tasks", []) if t["phase"] != "done_checklist"]),
    )
    tabs = st.tabs(
        ["Product brief", "Architecture", "Data model", "API", "Delivery plan", "Assumptions"]
    )
    for tab, renderer in zip(
        tabs,
        [
            render_prd,
            render_architecture,
            render_erd,
            render_api_spec,
            render_tasks,
            render_assumptions,
        ],
        strict=True,
    ):
        with tab:
            renderer(result)
    st.divider()
    export_col, info_col = st.columns([1, 2])
    with export_col:
        if st.button("Prepare ZIP download", use_container_width=True):
            exported = api_request("POST", "/export", json={"generation_id": last["generation_id"]})
            if exported is not None:
                st.session_state["zip_bytes"] = exported.content
        if st.session_state.get("zip_bytes"):
            st.download_button(
                "Download starter pack ↓",
                data=st.session_state["zip_bytes"],
                file_name=f"mvp_bundle_{last['generation_id']}.zip",
                mime="application/zip",
                use_container_width=True,
            )
    with info_col:
        st.caption(
            "Markdown documents, Mermaid sources, the shared contract and generation provenance."
        )
        st.caption(f"Generation ID: {last['generation_id']}")
else:
    st.divider()
    st.caption("YOUR WORKSPACE IS READY · Add a product brief to create the first starter pack.")
