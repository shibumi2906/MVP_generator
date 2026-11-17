from typing import Any

import streamlit as st

from app.ui.i18n import tr


def render_prd(result: dict[str, Any]) -> None:
    prd = result.get("prd_lite", {})
    st.subheader(tr("Problem"))
    st.write(prd.get("problem", ""))
    st.subheader(tr("Target user"))
    st.write(prd.get("target_user", ""))

    def _render_list(title: str, items: list[str] | None) -> None:
        st.markdown(f"### {title}")
        if items:
            for item in items:
                st.markdown(f"- {item}")

    _render_list(tr("Scope in"), prd.get("scope_in") or [])
    _render_list(tr("Scope out"), prd.get("scope_out") or [])
    _render_list(tr("User journey"), prd.get("user_journey") or [])
    _render_list(tr("Non-functional requirements"), prd.get("nfr") or [])
    _render_list(tr("Open questions"), prd.get("open_questions") or [])


def render_architecture(result: dict[str, Any]) -> None:
    arch = result.get("architecture", {})
    st.subheader(tr("Components"))
    for c in arch.get("components", []) or []:
        st.markdown(f"- {c}")
    st.subheader(tr("Data flow"))
    for f in arch.get("data_flow", []) or []:
        st.markdown(f"- {f}")
    st.subheader(tr("Risks"))
    for r in arch.get("risks", []) or []:
        st.markdown(f"- {r}")
    st.subheader(tr("Mermaid diagram"))
    st.code(arch.get("mermaid_diagram", ""), language="mermaid")


def render_erd(result: dict[str, Any]) -> None:
    dm = result.get("data_model", {})
    contract = result.get("contract") or {}
    if contract:
        for entity in contract["entities"]:
            st.subheader(entity["name"])
            st.caption(entity["description"])
            st.dataframe(
                [
                    {
                        tr("Field"): f["name"],
                        tr("Type"): f["type"],
                        tr("Primary key"): f["primary_key"],
                        tr("References"): f.get("references") or "—",
                    }
                    for f in entity["fields"]
                ],
                hide_index=True,
                use_container_width=True,
            )
    else:
        for entity in dm.get("entities", []):
            st.markdown(f"- {entity}")
    with st.expander(tr("Mermaid ERD source")):
        st.code(dm.get("mermaid_erd", ""), language="mermaid")


def render_api_spec(result: dict[str, Any]) -> None:
    api = result.get("api_spec", {})
    if api.get("format") == "markdown":
        st.markdown(api.get("content", ""))
    else:
        st.code(api.get("content", ""), language="yaml")


def render_tasks(result: dict[str, Any]) -> None:
    tasks = result.get("tasks", {})

    def _render_list(title: str, items: list[str] | None) -> None:
        st.markdown(f"### {title}")
        if items:
            for item in items:
                st.markdown(f"- {item}")

    _render_list(tr("Day 1"), tasks.get("day1") or [])
    _render_list(tr("Days 2–3"), tasks.get("day2_3") or [])
    _render_list(tr("Week 1"), tasks.get("week1") or [])
    _render_list(tr("Done checklist"), tasks.get("done_checklist") or [])


def render_assumptions(result: dict[str, Any]) -> None:
    st.subheader(tr("Assumptions"))
    for a in result.get("assumptions", []) or []:
        st.markdown(f"- {a}")
