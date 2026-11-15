import io
import zipfile

from app.core.schemas import Provenance, SpecBundle


def _wrap_mermaid(diagram: str) -> str:
    return f"```mermaid\n{diagram}\n```"


def build_zip_from_bundle(bundle: SpecBundle, provenance: Provenance) -> bytes:
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        readme = (
            f"# {bundle.title}\n\n"
            f"{bundle.summary}\n\n"
            f"Mode: **{provenance.mode}** · Source: **{provenance.source}** · Status: **{provenance.status}**\n\n"
            f"Consistency checked: **{provenance.consistency_checked}** · Fallback used: **{provenance.used_fallback}**\n\n"
            "This archive contains a PRD-lite, architecture, data model, API spec, "
            "and implementation task plan for the generated MVP.\n"
        )
        zf.writestr("README.md", readme)
        zf.writestr("provenance.json", provenance.model_dump_json(indent=2))
        zf.writestr("bundle.json", bundle.model_dump_json(indent=2))

        prd_md = ["# PRD-lite", "", "## Problem", bundle.prd_lite.problem, ""]
        prd_md.append("## Target user")
        prd_md.append(bundle.prd_lite.target_user)
        prd_md.append("")
        prd_md.append("## Scope (In)")
        prd_md.extend([f"- {item}" for item in bundle.prd_lite.scope_in])
        prd_md.append("")
        prd_md.append("## Scope (Out)")
        prd_md.extend([f"- {item}" for item in bundle.prd_lite.scope_out])
        prd_md.append("")
        prd_md.append("## User journey")
        prd_md.extend([f"- {item}" for item in bundle.prd_lite.user_journey])
        prd_md.append("")
        prd_md.append("## Non-functional requirements")
        prd_md.extend([f"- {item}" for item in bundle.prd_lite.nfr])
        prd_md.append("")
        prd_md.append("## Open questions")
        prd_md.extend([f"- {item}" for item in bundle.prd_lite.open_questions])
        zf.writestr("PRD.md", "\n".join(prd_md))

        arch_md = ["# Architecture", ""]
        arch_md.append("## Components")
        arch_md.extend([f"- {c}" for c in bundle.architecture.components])
        arch_md.append("")
        arch_md.append("## Data flow")
        arch_md.extend([f"- {f}" for f in bundle.architecture.data_flow])
        arch_md.append("")
        arch_md.append("## Risks")
        arch_md.extend([f"- {r}" for r in bundle.architecture.risks])
        arch_md.append("")
        arch_md.append("## Diagram")
        arch_md.append(_wrap_mermaid(bundle.architecture.mermaid_diagram))
        zf.writestr("ARCHITECTURE.md", "\n".join(arch_md))

        erd_md = ["# Data Model", ""]
        erd_md.append("## Entities")
        erd_md.extend([f"- {e}" for e in bundle.data_model.entities])
        erd_md.append("")
        erd_md.append("## ERD")
        erd_md.append(_wrap_mermaid(bundle.data_model.mermaid_erd))
        zf.writestr("ERD.md", "\n".join(erd_md))

        api_md = ["# API Spec", ""]
        api_md.append(f"_Format: {bundle.api_spec.format}_")
        api_md.append("")
        api_md.append(bundle.api_spec.content)
        zf.writestr("API_SPEC.md", "\n".join(api_md))

        tasks_md = ["# Task Plan", ""]
        tasks_md.append("## Day 1")
        tasks_md.extend([f"- {t}" for t in bundle.tasks.day1])
        tasks_md.append("")
        tasks_md.append("## Days 2–3")
        tasks_md.extend([f"- {t}" for t in bundle.tasks.day2_3])
        tasks_md.append("")
        tasks_md.append("## Week 1")
        tasks_md.extend([f"- {t}" for t in bundle.tasks.week1])
        tasks_md.append("")
        tasks_md.append("## Done checklist")
        tasks_md.extend([f"- {t}" for t in bundle.tasks.done_checklist])
        zf.writestr("TASKS.md", "\n".join(tasks_md))

        assumptions_md = ["# Assumptions", ""]
        assumptions_md.extend([f"- {a}" for a in bundle.assumptions])
        zf.writestr("ASSUMPTIONS.md", "\n".join(assumptions_md))

    mem.seek(0)
    return mem.read()
