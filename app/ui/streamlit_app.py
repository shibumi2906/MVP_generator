import json
from typing import Any, Dict, Optional

import requests
import streamlit as st

from app.ui.components import (
    render_api_spec,
    render_architecture,
    render_assumptions,
    render_erd,
    render_prd,
    render_tasks,
)


API_BASE = "http://localhost:8000"


st.set_page_config(page_title="MVP Generator", layout="wide")
st.title("MVP Generator")
st.caption("From product idea to developer starter pack in one click.")


def call_generate(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        resp = requests.post(f"{API_BASE}/generate", json=payload, timeout=60)
        if resp.status_code != 200:
            st.error(f"Generate failed: {resp.status_code} - {resp.text}")
            return None
        return resp.json()
    except Exception as exc:  # pragma: no cover - UI only
        st.error(f"Error calling API: {exc}")
        return None


def call_export(generation_id: str) -> Optional[bytes]:
    try:
        resp = requests.post(
            f"{API_BASE}/export", json={"generation_id": generation_id}, timeout=60
        )
        if resp.status_code != 200:
            st.error(f"Export failed: {resp.status_code} - {resp.text}")
            return None
        return resp.content
    except Exception as exc:  # pragma: no cover - UI only
        st.error(f"Error calling export: {exc}")
        return None


with st.form("mvp_form"):
    product_idea = st.text_area(
        "Product idea",
        placeholder="Describe the product you want to build...",
        height=120,
    )
    target_users = st.text_input("Target users (optional)")
    core_user_flow = st.text_area(
        "Core user flow (optional)",
        placeholder="Main steps a user takes to reach value...",
        height=80,
    )
    constraints = st.text_area(
        "Constraints (optional)",
        placeholder="Time, budget, tech, or other constraints...",
        height=80,
    )
    output_stack = st.text_input(
        "Output stack",
        value="FastAPI + SQLite + Streamlit",
    )

    submitted = st.form_submit_button("Generate")

if "last_generation" not in st.session_state:
    st.session_state["last_generation"] = None

if submitted:
    if not product_idea or len(product_idea.strip()) < 10:
        st.error("Product idea must be at least 10 characters.")
    else:
        payload = {
            "product_idea": product_idea,
            "target_users": target_users or None,
            "core_user_flow": core_user_flow or None,
            "constraints": constraints or None,
            "output_stack": output_stack or None,
        }
        with st.spinner("Generating MVP starter pack..."):
            data = call_generate(payload)
        if data:
            st.session_state["last_generation"] = data

last = st.session_state.get("last_generation")
if last:
    result = last.get("result", {})
    st.success(f"Generation ID: {last.get('generation_id')}")
    st.markdown(f"**Title:** {result.get('title', '')}")
    st.write(result.get("summary", ""))

    tab_prd, tab_arch, tab_erd, tab_api, tab_tasks, tab_assumptions = st.tabs(
        ["PRD", "Architecture", "ERD", "API Spec", "Tasks", "Assumptions"]
    )

    with tab_prd:
        render_prd(result)
    with tab_arch:
        render_architecture(result)
    with tab_erd:
        render_erd(result)
    with tab_api:
        render_api_spec(result)
    with tab_tasks:
        render_tasks(result)
    with tab_assumptions:
        render_assumptions(result)

    st.divider()
    st.subheader("Export")
    gen_id = last.get("generation_id")
    if gen_id:
        zip_bytes = None
        if st.button("Export ZIP"):
            with st.spinner("Building ZIP bundle..."):
                zip_bytes = call_export(gen_id)
        if zip_bytes:
            st.download_button(
                label="Download bundle",
                data=zip_bytes,
                file_name=f"mvp_bundle_{gen_id}.zip",
                mime="application/zip",
            )


