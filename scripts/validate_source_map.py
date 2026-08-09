#!/usr/bin/env python
"""Validate Source Scout source cards and index consistency."""

from __future__ import annotations

import pathlib
import sys
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
VALID_STATUS = {"active", "watch", "stale", "deprecated"}
VALID_SURFACE_STATUS = {"active", "watch", "stale", "blocked", "deprecated", "needs_validation"}
VALID_LOGIN = {"none", "optional", "required", "unknown"}
VALID_AUTOMATION = {"manual", "semi_automated", "automated", "unknown"}
VALID_DEPTH = {"yes", "no", "partial", "unknown", True, False}
MIN_ACCESS_SURFACES = 50
REQUIRED_FIELDS = {
    "source_id",
    "name",
    "source_type",
    "status",
    "priority",
    "best_for",
    "not_good_for",
    "domain_fit",
    "access_methods",
    "query_patterns",
    "source_discovery_patterns",
    "quality_signals",
    "failure_modes",
    "maintenance",
    "history",
}
DOMAIN_FIELDS = {"ecommerce", "engineering", "consumer_feedback", "data_collection", "ai_tools"}


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def require_score(errors: list[str], value: Any, label: str, path: pathlib.Path) -> None:
    if not isinstance(value, int) or not 1 <= value <= 5:
        fail(errors, f"{path}: {label} must be integer 1-5, got {value!r}")


def validate_source(path: pathlib.Path, expected_id: str | None = None) -> list[str]:
    errors: list[str] = []
    data = load_yaml(path)
    if not isinstance(data, dict):
        return [f"{path}: top-level YAML must be a mapping"]

    missing = REQUIRED_FIELDS - set(data)
    if missing:
        fail(errors, f"{path}: missing fields: {', '.join(sorted(missing))}")

    source_id = data.get("source_id")
    if expected_id and source_id != expected_id:
        fail(errors, f"{path}: source_id {source_id!r} does not match index {expected_id!r}")

    if data.get("status") not in VALID_STATUS:
        fail(errors, f"{path}: invalid status {data.get('status')!r}")

    require_score(errors, data.get("priority"), "priority", path)

    domain_fit = data.get("domain_fit", {})
    if not isinstance(domain_fit, dict):
        fail(errors, f"{path}: domain_fit must be a mapping")
    else:
        missing_domains = DOMAIN_FIELDS - set(domain_fit)
        if missing_domains:
            fail(errors, f"{path}: missing domain_fit fields: {', '.join(sorted(missing_domains))}")
        for key, value in domain_fit.items():
            require_score(errors, value, f"domain_fit.{key}", path)

    methods = data.get("access_methods", [])
    if not isinstance(methods, list) or not methods:
        fail(errors, f"{path}: access_methods must be a non-empty list")
    else:
        for idx, method in enumerate(methods):
            if not isinstance(method, dict):
                fail(errors, f"{path}: access_methods[{idx}] must be a mapping")
                continue
            for field in ["method_id", "description", "speed", "reliability"]:
                if field not in method:
                    fail(errors, f"{path}: access_methods[{idx}] missing {field}")
            if "reliability" in method:
                require_score(errors, method["reliability"], f"access_methods[{idx}].reliability", path)

    for list_field in ["best_for", "not_good_for", "query_patterns", "source_discovery_patterns", "failure_modes"]:
        value = data.get(list_field)
        if not isinstance(value, list):
            fail(errors, f"{path}: {list_field} must be a list")

    maintenance = data.get("maintenance", {})
    if not isinstance(maintenance, dict):
        fail(errors, f"{path}: maintenance must be a mapping")
    else:
        for field in ["check_frequency", "last_checked", "known_failures"]:
            if field not in maintenance:
                fail(errors, f"{path}: maintenance missing {field}")

    return errors


def validate_access_surfaces(known_sources: set[str]) -> list[str]:
    errors: list[str] = []
    path = ROOT / "access" / "access-surfaces.yaml"
    if not path.exists():
        return [f"{path}: missing access surface catalog"]
    data = load_yaml(path)
    surfaces = data.get("access_surfaces", []) if isinstance(data, dict) else []
    if not isinstance(surfaces, list):
        return [f"{path}: access_surfaces must be a list"]
    if len(surfaces) < MIN_ACCESS_SURFACES:
        fail(errors, f"{path}: expected at least {MIN_ACCESS_SURFACES} access surfaces, got {len(surfaces)}")

    ids: set[str] = set()
    for idx, surface in enumerate(surfaces):
        label = f"{path}: access_surfaces[{idx}]"
        if not isinstance(surface, dict):
            fail(errors, f"{label} must be a mapping")
            continue
        for field in [
            "surface_id",
            "parent_source",
            "name",
            "access_type",
            "status",
            "priority",
            "login_required",
            "automation_level",
            "best_for",
            "not_good_for",
            "entry_points",
            "query_templates",
            "retrieval_depth",
            "validation",
            "fallback_surfaces",
            "history",
        ]:
            if field not in surface:
                fail(errors, f"{label} missing {field}")

        surface_id = surface.get("surface_id")
        if surface_id in ids:
            fail(errors, f"{label}: duplicate surface_id {surface_id}")
        if surface_id:
            ids.add(surface_id)

        parent = surface.get("parent_source")
        if parent not in known_sources:
            fail(errors, f"{label}: parent_source {parent!r} is not an indexed source")

        if surface.get("status") not in VALID_SURFACE_STATUS:
            fail(errors, f"{label}: invalid status {surface.get('status')!r}")
        if surface.get("login_required") not in VALID_LOGIN:
            fail(errors, f"{label}: invalid login_required {surface.get('login_required')!r}")
        if surface.get("automation_level") not in VALID_AUTOMATION:
            fail(errors, f"{label}: invalid automation_level {surface.get('automation_level')!r}")
        require_score(errors, surface.get("priority"), "priority", path)

        for list_field in ["best_for", "not_good_for", "entry_points", "query_templates", "fallback_surfaces", "history"]:
            if not isinstance(surface.get(list_field), list):
                fail(errors, f"{label}: {list_field} must be a list")

        depth = surface.get("retrieval_depth", {})
        if not isinstance(depth, dict):
            fail(errors, f"{label}: retrieval_depth must be a mapping")
        else:
            for field in ["title", "snippet", "body", "comments", "metadata"]:
                if depth.get(field) not in VALID_DEPTH:
                    fail(errors, f"{label}: retrieval_depth.{field} invalid: {depth.get(field)!r}")

        validation = surface.get("validation", {})
        if not isinstance(validation, dict):
            fail(errors, f"{label}: validation must be a mapping")
        else:
            for field in ["last_checked", "method", "success_criteria", "failure_signals"]:
                if field not in validation:
                    fail(errors, f"{label}: validation missing {field}")
            for list_field in ["success_criteria", "failure_signals"]:
                if list_field in validation and not isinstance(validation[list_field], list):
                    fail(errors, f"{label}: validation.{list_field} must be a list")

    for surface in surfaces:
        if not isinstance(surface, dict):
            continue
        for fallback in surface.get("fallback_surfaces", []):
            if fallback not in ids:
                fail(errors, f"{path}: {surface.get('surface_id')} fallback {fallback!r} is not a known surface_id")

    return errors


def main() -> int:
    errors: list[str] = []
    index_path = ROOT / "sources" / "source-index.yaml"
    index = load_yaml(index_path)
    if not isinstance(index, dict) or "sources" not in index:
        print(f"{index_path}: invalid source index")
        return 1

    seen_ids: set[str] = set()
    indexed_paths: set[pathlib.Path] = set()
    for item in index["sources"]:
        source_id = item.get("source_id")
        rel_file = item.get("file")
        if source_id in seen_ids:
            fail(errors, f"{index_path}: duplicate source_id {source_id}")
        seen_ids.add(source_id)
        path = ROOT / rel_file
        indexed_paths.add(path.resolve())
        if not path.exists():
            fail(errors, f"{index_path}: missing source file {rel_file}")
            continue
        errors.extend(validate_source(path, expected_id=source_id))

    for path in sorted((ROOT / "sources").glob("*.yaml")):
        if path.name == "source-index.yaml":
            continue
        if path.resolve() not in indexed_paths:
            fail(errors, f"{path}: source card exists but is not indexed")

    routing_path = ROOT / "routing" / "problem-type-routing.yaml"
    if routing_path.exists():
        routing = load_yaml(routing_path)
        known_sources = seen_ids
        for problem_type, spec in routing.get("problem_types", {}).items():
            for field in ["default_sources", "escalation_sources"]:
                for source_id in spec.get(field, []):
                    if source_id not in known_sources:
                        fail(errors, f"{routing_path}: {problem_type}.{field} references unknown source {source_id}")

    errors.extend(validate_access_surfaces(seen_ids))

    if errors:
        print("Source Map validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    access_path = ROOT / "access" / "access-surfaces.yaml"
    surface_count = 0
    if access_path.exists():
        access_data = load_yaml(access_path)
        surface_count = len(access_data.get("access_surfaces", []))
    print(f"Source Map valid: {len(seen_ids)} indexed sources, {surface_count} access surfaces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
