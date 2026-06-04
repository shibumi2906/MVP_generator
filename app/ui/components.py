from typing import Any, Dict

import streamlit as st


def render_prd(result: Dict[str, Any]) -> None:
    prd = result.get("prd_lite", {})
    st.subheader("Problem")
    st.write(prd.get("problem", ""))
    st.subheader("Target user")
    st.write(prd.get("target_user", ""))

    def _render_list(title: str, items: list[str] | None) -> None:
        st.markdown(f"### {title}")
        if items:
            for item in items:
                st.markdown(f"- {item}")

    _render_list("Scope in", prd.get("scope_in") or [])
    _render_list("Scope out", prd.get("scope_out") or [])
    _render_list("User journey", prd.get("user_journey") or [])
    _render_list("Non-functional requirements", prd.get("nfr") or [])
    _render_list("Open questions", prd.get("open_questions") or [])


def render_architecture(result: Dict[str, Any]) -> None:
    arch = result.get("architecture", {})
    st.subheader("Components")
    for c in arch.get("components", []) or []:
        st.markdown(f"- {c}")
    st.subheader("Data flow")
    for f in arch.get("data_flow", []) or []:
        st.markdown(f"- {f}")
    st.subheader("Risks")
    for r in arch.get("risks", []) or []:
        st.markdown(f"- {r}")
    st.subheader("Mermaid diagram")
    st.code(arch.get("mermaid_diagram", ""), language="mermaid")


def render_erd(result: Dict[str, Any]) -> None:
    dm = result.get("data_model", {})
    st.subheader("Entities")
    for e in dm.get("entities", []) or []:
        st.markdown(f"- {e}")
    st.subheader("Mermaid ERD")
    st.code(dm.get("mermaid_erd", ""), language="mermaid")


def render_api_spec(result: Dict[str, Any]) -> None:
    api = result.get("api_spec", {})
    st.subheader("Format")
    st.write(api.get("format", ""))
    st.subheader("Content")
    st.code(api.get("content", ""), language="yaml")


def render_tasks(result: Dict[str, Any]) -> None:
    tasks = result.get("tasks", {})

    def _render_list(title: str, items: list[str] | None) -> None:
        st.markdown(f"### {title}")
        if items:
            for item in items:
                st.markdown(f"- {item}")

    _render_list("Day 1", tasks.get("day1") or [])
    _render_list("Days 2–3", tasks.get("day2_3") or [])
    _render_list("Week 1", tasks.get("week1") or [])
    _render_list("Done checklist", tasks.get("done_checklist") or [])


def render_assumptions(result: Dict[str, Any]) -> None:
    st.subheader("Assumptions")
    for a in result.get("assumptions", []) or []:
        st.markdown(f"- {a}")



