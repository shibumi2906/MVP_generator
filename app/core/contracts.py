"""The shared source of truth for ERD, API documentation and implementation tasks."""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class EntityField(ContractModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    type: Literal["string", "text", "integer", "number", "boolean", "datetime"]
    primary_key: bool = False
    references: str | None = None


class Entity(ContractModel):
    name: str = Field(pattern=r"^[A-Z][A-Za-z0-9]*$")
    description: str = Field(min_length=1)
    fields: list[EntityField] = Field(min_length=1)


class Endpoint(ContractModel):
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str = Field(pattern=r"^/[a-zA-Z0-9_/{}/-]*$")
    summary: str = Field(min_length=1)
    entity: str
    request_fields: list[str]
    response_fields: list[str]

    @property
    def key(self) -> str:
        return f"{self.method} {self.path}"


class ImplementationTask(ContractModel):
    phase: Literal["day1", "day2_3", "week1", "done_checklist"]
    title: str = Field(min_length=1)
    entities: list[str] = Field(min_length=1)
    endpoints: list[str]


class DocumentContract(ContractModel):
    entities: list[Entity] = Field(min_length=1)
    endpoints: list[Endpoint] = Field(min_length=1)
    tasks: list[ImplementationTask] = Field(min_length=1)

    @model_validator(mode="after")
    def check_references(self) -> "DocumentContract":
        errors: list[str] = []
        entities = {e.name: e for e in self.entities}
        endpoints = {e.key: e for e in self.endpoints}
        if len(entities) != len(self.entities):
            errors.append("Entity names must be unique")
        if len(endpoints) != len(self.endpoints):
            errors.append("Endpoint method/path pairs must be unique")
        fields = {e.name: {f.name: f for f in e.fields} for e in self.entities}
        for entity in self.entities:
            if len(fields[entity.name]) != len(entity.fields):
                errors.append(f"{entity.name}: field names must be unique")
            if not any(f.primary_key for f in entity.fields):
                errors.append(f"{entity.name}: a primary key is required")
            for field in entity.fields:
                if field.references:
                    target_entity, _, target_field = field.references.partition(".")
                    target = fields.get(target_entity, {}).get(target_field)
                    if target is None:
                        errors.append(
                            f"{entity.name}.{field.name}: unknown reference {field.references}"
                        )
                    elif not target.primary_key or target.type != field.type:
                        errors.append(
                            f"{entity.name}.{field.name}: reference must match a primary key type"
                        )
        for endpoint in self.endpoints:
            if endpoint.entity not in entities:
                errors.append(f"{endpoint.key}: unknown entity {endpoint.entity}")
                continue
            for name in endpoint.request_fields + endpoint.response_fields:
                if name not in fields[endpoint.entity]:
                    errors.append(f"{endpoint.key}: unknown field {endpoint.entity}.{name}")
            if len(set(endpoint.request_fields)) != len(endpoint.request_fields) or len(
                set(endpoint.response_fields)
            ) != len(endpoint.response_fields):
                errors.append(f"{endpoint.key}: duplicate API fields")
            parameters = re.findall(r"\{([^{}]+)\}", endpoint.path)
            if endpoint.path.count("{") != len(parameters) or endpoint.path.count("}") != len(
                parameters
            ):
                errors.append(f"{endpoint.key}: malformed path parameters")
            for parameter in parameters:
                if parameter not in fields[endpoint.entity]:
                    errors.append(f"{endpoint.key}: unknown path field {parameter}")
        covered_entities: set[str] = set()
        covered_endpoints: set[str] = set()
        phases = set()
        for task in self.tasks:
            phases.add(task.phase)
            for name in task.entities:
                if name not in entities:
                    errors.append(f"Task '{task.title}': unknown entity {name}")
            for key in task.endpoints:
                if key not in endpoints:
                    errors.append(f"Task '{task.title}': unknown endpoint {key}")
                elif endpoints[key].entity not in task.entities:
                    errors.append(
                        f"Task '{task.title}': endpoint entity must be listed in task entities"
                    )
            if task.phase != "done_checklist":
                covered_entities.update(task.entities)
                covered_endpoints.update(task.endpoints)
        if missing := set(entities) - covered_entities:
            errors.append(f"Entities without implementation tasks: {', '.join(sorted(missing))}")
        if missing := set(endpoints) - covered_endpoints:
            errors.append(f"Endpoints without implementation tasks: {', '.join(sorted(missing))}")
        if phases != {"day1", "day2_3", "week1", "done_checklist"}:
            errors.append("Tasks must cover day1, day2_3, week1 and done_checklist")
        if errors:
            raise ValueError("; ".join(errors))
        return self

    def render_erd(self) -> str:
        lines = ["erDiagram"]
        for entity in self.entities:
            lines.append(f"  {entity.name} {{")
            for field in entity.fields:
                keys = [
                    key
                    for key, enabled in [("PK", field.primary_key), ("FK", field.references)]
                    if enabled
                ]
                suffix = f" {','.join(keys)}" if keys else ""
                lines.append(f"    {field.type} {field.name}{suffix}")
            lines.append("  }")
        for entity in self.entities:
            for field in entity.fields:
                if field.references:
                    target = field.references.split(".")[0]
                    lines.append(f'  {target} ||--o{{ {entity.name} : "{field.name}"')
        return "\n".join(lines)

    def render_api(self) -> str:
        lines = ["## Resource endpoints", "", "Fields refer to the shared ERD entities.", ""]
        for endpoint in self.endpoints:
            entity = next(e for e in self.entities if e.name == endpoint.entity)
            fields = {f.name: f for f in entity.fields}
            lines.extend(
                [
                    f"### `{endpoint.key}`",
                    "",
                    endpoint.summary,
                    "",
                    f"Entity: `{endpoint.entity}`",
                    "",
                ]
            )
            for label, names in [
                ("Request fields", endpoint.request_fields),
                ("Response fields", endpoint.response_fields),
            ]:
                description = (
                    ", ".join(f"`{name}: {fields[name].type}`" for name in names) or "None"
                )
                lines.extend([f"**{label}:** {description}", ""])
        return "\n".join(lines)

    def render_tasks(self, phase: str) -> list[str]:
        return [
            f"{t.title} [entities: {', '.join(t.entities)}; endpoints: {', '.join(t.endpoints) or 'none'}]"
            for t in self.tasks
            if t.phase == phase
        ]
