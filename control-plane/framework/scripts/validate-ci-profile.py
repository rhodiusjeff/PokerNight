#!/usr/bin/env python3
"""Validate a cpb-ci-profile-catalog-v1 document without external dependencies."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CHECK_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
ROLLOUT_STAGES = {"design", "observe", "required-pr", "queue-ready"}
PROVIDERS = {"github", "gitlab"}


def load_json(path: pathlib.Path, problems: list[str]) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        problems.append(f"{path}: unparseable JSON: {exc}")
        return None


def require_keys(value: Any, keys: set[str], location: str, problems: list[str]) -> bool:
    if not isinstance(value, dict):
        problems.append(f"{location}: expected object")
        return False
    missing = keys - set(value)
    if missing:
        problems.append(f"{location}: missing keys {sorted(missing)}")
    return not missing


def validate_budget(value: Any, location: str, problems: list[str]) -> None:
    required = {"wall_minutes", "runner_minutes", "max_concurrency", "retry_limit"}
    if not require_keys(value, required, location, problems):
        return
    allowed = required
    extras = set(value) - allowed
    if extras:
        problems.append(f"{location}: unexpected keys {sorted(extras)}")
    for field in ("wall_minutes", "runner_minutes"):
        if not isinstance(value[field], (int, float)) or isinstance(value[field], bool) or value[field] <= 0:
            problems.append(f"{location}.{field}: expected positive number")
    if not isinstance(value["max_concurrency"], int) or value["max_concurrency"] < 1:
        problems.append(f"{location}.max_concurrency: expected integer >= 1")
    if not isinstance(value["retry_limit"], int) or not 0 <= value["retry_limit"] <= 2:
        problems.append(f"{location}.retry_limit: expected integer 0..2")


def validate_runner(value: Any, location: str, problems: list[str]) -> None:
    if not require_keys(value, {"labels"}, location, problems):
        return
    extras = set(value) - {"labels", "container"}
    if extras:
        problems.append(f"{location}: unexpected keys {sorted(extras)}")
    labels = value.get("labels")
    if not isinstance(labels, list) or not labels or not all(isinstance(item, str) and item for item in labels):
        problems.append(f"{location}.labels: expected non-empty string array")
    if value.get("container") is not None and not isinstance(value.get("container"), str):
        problems.append(f"{location}.container: expected string or null")


def validate_checks(values: Any, location: str, problems: list[str]) -> list[str]:
    if not isinstance(values, list):
        problems.append(f"{location}: expected array")
        return []
    ids: list[str] = []
    for index, check in enumerate(values):
        item_location = f"{location}[{index}]"
        required = {"id", "command", "timeout_minutes"}
        if not require_keys(check, required, item_location, problems):
            continue
        extras = set(check) - (required | {"requires_secrets"})
        if extras:
            problems.append(f"{item_location}: unexpected keys {sorted(extras)}")
        check_id = check.get("id")
        if not isinstance(check_id, str) or not ID_RE.fullmatch(check_id):
            problems.append(f"{item_location}.id: invalid kebab-case identifier")
        else:
            ids.append(check_id)
        if not isinstance(check.get("command"), str) or not check["command"].strip():
            problems.append(f"{item_location}.command: expected non-empty string")
        if not isinstance(check.get("timeout_minutes"), int) or check["timeout_minutes"] < 1:
            problems.append(f"{item_location}.timeout_minutes: expected integer >= 1")
        if "requires_secrets" in check and not isinstance(check["requires_secrets"], bool):
            problems.append(f"{item_location}.requires_secrets: expected boolean")
    return ids


def validate_profile(profile: Any, index: int, problems: list[str]) -> tuple[str | None, list[str]]:
    location = f"profiles[{index}]"
    required = {
        "id", "description", "enabled", "selectors", "runner", "blocking_checks",
        "post_merge_checks", "manual_checks", "caches", "broadening_rules", "budget",
        "evidence_owner",
    }
    if not require_keys(profile, required, location, problems):
        return None, []
    extras = set(profile) - required
    if extras:
        problems.append(f"{location}: unexpected keys {sorted(extras)}")
    profile_id = profile.get("id")
    if not isinstance(profile_id, str) or not ID_RE.fullmatch(profile_id):
        problems.append(f"{location}.id: invalid kebab-case identifier")
        profile_id = None
    if not isinstance(profile.get("description"), str) or not profile["description"].strip():
        problems.append(f"{location}.description: expected non-empty string")
    if not isinstance(profile.get("enabled"), bool):
        problems.append(f"{location}.enabled: expected boolean")
    selectors = profile.get("selectors")
    if require_keys(selectors, {"paths", "impact_classes"}, f"{location}.selectors", problems):
        if set(selectors) != {"paths", "impact_classes"}:
            problems.append(f"{location}.selectors: unexpected keys {sorted(set(selectors) - {'paths', 'impact_classes'})}")
        paths = selectors.get("paths")
        impacts = selectors.get("impact_classes")
        if not isinstance(paths, list) or not all(isinstance(item, str) and item for item in paths):
            problems.append(f"{location}.selectors.paths: expected string array")
        if not isinstance(impacts, list) or not all(isinstance(item, str) and item for item in impacts):
            problems.append(f"{location}.selectors.impact_classes: expected string array")
        if isinstance(paths, list) and isinstance(impacts, list) and not paths and not impacts:
            problems.append(f"{location}.selectors: paths and impact_classes cannot both be empty")
    validate_runner(profile.get("runner"), f"{location}.runner", problems)
    all_check_ids: list[str] = []
    for field in ("blocking_checks", "post_merge_checks", "manual_checks"):
        all_check_ids.extend(validate_checks(profile.get(field), f"{location}.{field}", problems))
    if len(all_check_ids) != len(set(all_check_ids)):
        problems.append(f"{location}: duplicate check ids across tiers")
    caches = profile.get("caches")
    if not isinstance(caches, list):
        problems.append(f"{location}.caches: expected array")
    else:
        cache_ids: list[str] = []
        for cache_index, cache in enumerate(caches):
            cache_location = f"{location}.caches[{cache_index}]"
            required_cache = {"id", "key_inputs", "paths"}
            if not require_keys(cache, required_cache, cache_location, problems):
                continue
            if set(cache) != required_cache:
                problems.append(f"{cache_location}: unexpected keys {sorted(set(cache) - required_cache)}")
            cache_id = cache.get("id")
            if not isinstance(cache_id, str) or not ID_RE.fullmatch(cache_id):
                problems.append(f"{cache_location}.id: invalid kebab-case identifier")
            else:
                cache_ids.append(cache_id)
            for field in ("key_inputs", "paths"):
                data = cache.get(field)
                if not isinstance(data, list) or not data or not all(isinstance(item, str) and item for item in data):
                    problems.append(f"{cache_location}.{field}: expected non-empty string array")
        if len(cache_ids) != len(set(cache_ids)):
            problems.append(f"{location}: duplicate cache ids")
    rules = profile.get("broadening_rules")
    if not isinstance(rules, list) or not all(isinstance(item, str) and item for item in rules):
        problems.append(f"{location}.broadening_rules: expected string array")
    validate_budget(profile.get("budget"), f"{location}.budget", problems)
    if not isinstance(profile.get("evidence_owner"), str) or not profile["evidence_owner"].strip():
        problems.append(f"{location}.evidence_owner: expected non-empty string")
    return profile_id, all_check_ids


def validate_document(document: Any, source: str = "document") -> list[str]:
    problems: list[str] = []
    required = {
        "schema", "version", "provider", "protected_target", "stable_check", "rollout_stage",
        "default_runner", "global_budget", "profiles", "unknown_impact",
    }
    if not require_keys(document, required, source, problems):
        return problems
    extras = set(document) - required
    if extras:
        problems.append(f"{source}: unexpected keys {sorted(extras)}")
    if document.get("schema") != "cpb-ci-profile-catalog-v1":
        problems.append(f"{source}.schema: expected cpb-ci-profile-catalog-v1")
    if not isinstance(document.get("version"), str) or not document["version"].strip():
        problems.append(f"{source}.version: expected non-empty string")
    if document.get("provider") not in PROVIDERS:
        problems.append(f"{source}.provider: expected github or gitlab")
    if not isinstance(document.get("protected_target"), str) or not document["protected_target"].strip():
        problems.append(f"{source}.protected_target: expected non-empty string")
    if not isinstance(document.get("stable_check"), str) or not CHECK_RE.fullmatch(document["stable_check"]):
        problems.append(f"{source}.stable_check: invalid check name")
    if document.get("rollout_stage") not in ROLLOUT_STAGES:
        problems.append(f"{source}.rollout_stage: invalid stage")
    if document.get("unknown_impact") not in {"broaden", "block"}:
        problems.append(f"{source}.unknown_impact: expected broaden or block")
    validate_runner(document.get("default_runner"), f"{source}.default_runner", problems)
    validate_budget(document.get("global_budget"), f"{source}.global_budget", problems)
    profiles = document.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        problems.append(f"{source}.profiles: expected non-empty array")
        return problems
    profile_ids: list[str] = []
    all_check_ids: list[str] = []
    always_present = False
    for index, profile in enumerate(profiles):
        profile_id, checks = validate_profile(profile, index, problems)
        if profile_id:
            profile_ids.append(profile_id)
        all_check_ids.extend(checks)
        selectors = profile.get("selectors", {}) if isinstance(profile, dict) else {}
        if "always" in selectors.get("impact_classes", []) or "**" in selectors.get("paths", []):
            always_present = True
    if len(profile_ids) != len(set(profile_ids)):
        problems.append(f"{source}: duplicate profile ids")
    if not always_present:
        problems.append(f"{source}: no always-run profile selector")
    if document.get("stable_check") in all_check_ids:
        problems.append(f"{source}: stable aggregate check must not be a component check id")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=pathlib.Path)
    args = parser.parse_args()
    problems: list[str] = []
    document = load_json(args.catalog, problems)
    if document is not None:
        problems.extend(validate_document(document, str(args.catalog)))
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())