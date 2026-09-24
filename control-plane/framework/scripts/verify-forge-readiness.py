#!/usr/bin/env python3
"""Create a time-bounded forge-readiness attestation from normalized or live facts.

Fixture mode is provider-neutral. Live mode currently implements read-only GitHub collection via
the gh CLI. GitLab live collection is intentionally unimplemented in v1 and reports unverified.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import fnmatch
import hashlib
import json
import pathlib
import subprocess
import sys
from typing import Any


ADAPTER_VERSION = "cpb-forge-adapter-v1"
CAPABILITY_IDS = (
    "protected-target",
    "pull-requests-required",
    "force-push-blocked",
    "required-stable-check",
    "pr-workflow",
    "merge-group-workflow",
    "merge-queue-enabled",
    "bypass-constrained",
)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(value: dt.datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text())


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gh_json(endpoint: str) -> tuple[Any | None, str | None]:
    process = subprocess.run(
        ["gh", "api", endpoint], capture_output=True, text=True, check=False
    )
    if process.returncode != 0:
        message = process.stderr.strip().splitlines()[-1] if process.stderr.strip() else "gh api failed"
        return None, message
    try:
        return json.loads(process.stdout), None
    except json.JSONDecodeError as exc:
        return None, f"unparseable gh response: {exc}"


def ruleset_applies(ruleset: dict[str, Any], target: str) -> bool:
    conditions = ruleset.get("conditions")
    if not conditions:
        return True
    ref_name = conditions.get("ref_name", {})
    include = ref_name.get("include", [])
    exclude = ref_name.get("exclude", [])
    ref = f"refs/heads/{target}"
    included = not include or any(fnmatch.fnmatch(ref, pattern) for pattern in include)
    excluded = any(fnmatch.fnmatch(ref, pattern) for pattern in exclude)
    return included and not excluded


def collect_workflow_triggers(repository: str, target: str, stable_check: str, limits: list[str]) -> tuple[bool | None, bool | None]:
    items, error = gh_json(f"repos/{repository}/contents/.github/workflows?ref={target}")
    if error:
        limits.append(f"workflow content unavailable: {error}")
        return None, None
    if not isinstance(items, list):
        return False, False
    pull_request = False
    merge_group = False
    for item in items:
        if not isinstance(item, dict) or item.get("type") != "file":
            continue
        content_doc, content_error = gh_json(f"repos/{repository}/contents/.github/workflows/{item.get('name')}?ref={target}")
        if content_error or not isinstance(content_doc, dict):
            limits.append(f"workflow {item.get('name')} content unavailable")
            continue
        encoded = content_doc.get("content")
        if not isinstance(encoded, str):
            continue
        try:
            text = base64.b64decode(encoded).decode("utf-8", errors="replace")
        except Exception:
            limits.append(f"workflow {item.get('name')} could not be decoded")
            continue
        if stable_check not in text:
            continue
        pull_request = pull_request or "pull_request:" in text
        merge_group = merge_group or "merge_group:" in text
    return pull_request, merge_group


def collect_github_facts(repository: str, target: str, stable_check: str) -> dict[str, Any]:
    limits: list[str] = []
    protection, protection_error = gh_json(f"repos/{repository}/branches/{target}/protection")
    if protection_error:
        limits.append(f"branch protection unavailable: {protection_error}")
        protection = None
    summaries, rulesets_error = gh_json(f"repos/{repository}/rulesets")
    detailed_rulesets: list[dict[str, Any]] = []
    if rulesets_error:
        limits.append(f"rulesets unavailable: {rulesets_error}")
    elif isinstance(summaries, list):
        for summary in summaries:
            if not isinstance(summary, dict) or summary.get("enforcement") != "active":
                continue
            detail, detail_error = gh_json(f"repos/{repository}/rulesets/{summary.get('id')}")
            if detail_error:
                limits.append(f"ruleset {summary.get('id')} details unavailable")
            elif isinstance(detail, dict) and detail.get("target") == "branch" and ruleset_applies(detail, target):
                detailed_rulesets.append(detail)

    protection_present = isinstance(protection, dict)
    rules = [rule for ruleset in detailed_rulesets for rule in ruleset.get("rules", []) if isinstance(rule, dict)]
    protected_target: bool | None = protection_present or bool(detailed_rulesets)
    pull_requests_required: bool | None = None
    force_push_blocked: bool | None = None
    bypass_constrained: bool | None = None
    required_checks: list[str] | None = None
    merge_queue_enabled: bool | None = None

    if protection_present:
        pull_requests_required = bool(protection.get("required_pull_request_reviews"))
        allow_force = protection.get("allow_force_pushes", {})
        force_push_blocked = not bool(allow_force.get("enabled"))
        enforce_admins = protection.get("enforce_admins", {})
        bypass_constrained = bool(enforce_admins.get("enabled"))
        status = protection.get("required_status_checks")
        if isinstance(status, dict):
            contexts = list(status.get("contexts") or [])
            contexts.extend(
                check.get("context") for check in status.get("checks", [])
                if isinstance(check, dict) and check.get("context")
            )
            required_checks = sorted(set(contexts))
        else:
            required_checks = []

    if detailed_rulesets:
        pull_requests_required = pull_requests_required or any(rule.get("type") == "pull_request" for rule in rules)
        force_push_blocked = force_push_blocked or any(rule.get("type") == "non_fast_forward" for rule in rules)
        merge_queue_enabled = any(rule.get("type") == "merge_queue" for rule in rules)
        required_from_rulesets: list[str] = []
        for rule in rules:
            if rule.get("type") != "required_status_checks":
                continue
            parameters = rule.get("parameters", {})
            for check in parameters.get("required_status_checks", []):
                if isinstance(check, dict) and check.get("context"):
                    required_from_rulesets.append(check["context"])
        required_checks = sorted(set((required_checks or []) + required_from_rulesets))
        bypass_constrained = bypass_constrained or all(not ruleset.get("bypass_actors") for ruleset in detailed_rulesets)
    elif rulesets_error:
        merge_queue_enabled = None
    else:
        merge_queue_enabled = False

    pr_workflow, merge_group_workflow = collect_workflow_triggers(repository, target, stable_check, limits)
    return {
        "schema": "cpb-forge-facts-v1",
        "provider": "github",
        "repository": repository,
        "target_branch": target,
        "collected_at": iso(utc_now()),
        "adapter_version": ADAPTER_VERSION,
        "capabilities": {
            "protected_target": protected_target,
            "pull_requests_required": pull_requests_required,
            "force_push_blocked": force_push_blocked,
            "required_checks": required_checks,
            "pr_workflow": pr_workflow,
            "merge_group_workflow": merge_group_workflow,
            "merge_queue_enabled": merge_queue_enabled,
            "bypass_constrained": bypass_constrained,
        },
        "visibility_limits": limits,
    }


def fact(id_: str, status: str, summary: str, evidence: str = "") -> dict[str, str]:
    return {"id": id_, "status": status, "summary": summary, "evidence": evidence}


def bool_fact(id_: str, value: bool | None, positive: str, negative: str) -> dict[str, str]:
    if value is None:
        return fact(id_, "unverified", f"{positive} could not be verified.")
    return fact(id_, "pass" if value else "fail", positive if value else negative)


def build_attestation(facts: dict[str, Any], profile_path: pathlib.Path, ttl_hours: int) -> dict[str, Any]:
    profile = load_json(profile_path)
    capabilities = facts.get("capabilities", {})
    queue_required = profile.get("rollout_stage") == "queue-ready"
    stable_check = profile.get("stable_check")
    required_checks = capabilities.get("required_checks")
    results = [
        bool_fact("protected-target", capabilities.get("protected_target"), "Protected target is configured.", "Protected target is not configured."),
        bool_fact("pull-requests-required", capabilities.get("pull_requests_required"), "Pull requests or merge requests are required.", "Pull requests or merge requests are not required."),
        bool_fact("force-push-blocked", capabilities.get("force_push_blocked"), "Force pushes are blocked.", "Force pushes are not blocked."),
    ]
    if required_checks is None:
        results.append(fact("required-stable-check", "unverified", f"Required check {stable_check!r} could not be verified."))
    elif stable_check in required_checks:
        results.append(fact("required-stable-check", "pass", f"Stable check {stable_check!r} is required.", ", ".join(required_checks)))
    else:
        results.append(fact("required-stable-check", "fail", f"Stable check {stable_check!r} is not required.", ", ".join(required_checks)))
    results.append(bool_fact("pr-workflow", capabilities.get("pr_workflow"), "A pull-request pipeline trigger is present.", "No pull-request pipeline trigger is present."))
    if queue_required:
        results.append(bool_fact("merge-group-workflow", capabilities.get("merge_group_workflow"), "A merge-group/train pipeline trigger is present.", "No merge-group/train pipeline trigger is present."))
        results.append(bool_fact("merge-queue-enabled", capabilities.get("merge_queue_enabled"), "Merge queue/train is enabled.", "Merge queue/train is not enabled."))
    else:
        results.append(fact("merge-group-workflow", "not-required", "Merge-group/train workflow is not required at this rollout stage."))
        results.append(fact("merge-queue-enabled", "not-required", "Merge queue/train is not required at this rollout stage."))
    results.append(bool_fact("bypass-constrained", capabilities.get("bypass_constrained"), "Bypass actors are constrained.", "Bypass actors are not constrained."))

    statuses = {item["status"] for item in results}
    overall = "fail" if "fail" in statuses else "unverified" if "unverified" in statuses else "pass"
    checked = utc_now()
    return {
        "schema": "cpb-forge-readiness-attestation-v1",
        "provider": facts.get("provider"),
        "repository": facts.get("repository"),
        "target_branch": facts.get("target_branch"),
        "checked_at": iso(checked),
        "expires_at": iso(checked + dt.timedelta(hours=ttl_hours)),
        "adapter_version": facts.get("adapter_version", ADAPTER_VERSION),
        "requirements_digest": digest(profile_path),
        "overall": overall,
        "facts": results,
        "visibility_limits": list(facts.get("visibility_limits") or []),
    }


def validate_facts(facts: Any) -> list[str]:
    problems: list[str] = []
    if not isinstance(facts, dict) or facts.get("schema") != "cpb-forge-facts-v1":
        return ["facts: schema must be cpb-forge-facts-v1"]
    required = {"provider", "repository", "target_branch", "collected_at", "adapter_version", "capabilities", "visibility_limits"}
    missing = required - set(facts)
    if missing:
        problems.append(f"facts: missing keys {sorted(missing)}")
    capabilities = facts.get("capabilities")
    capability_keys = {
        "protected_target", "pull_requests_required", "force_push_blocked", "required_checks",
        "pr_workflow", "merge_group_workflow", "merge_queue_enabled", "bypass_constrained",
    }
    if not isinstance(capabilities, dict):
        problems.append("facts.capabilities: expected object")
    else:
        missing_capabilities = capability_keys - set(capabilities)
        if missing_capabilities:
            problems.append(f"facts.capabilities: missing keys {sorted(missing_capabilities)}")
        for key in capability_keys - {"required_checks"}:
            if key in capabilities and capabilities[key] not in {True, False, None}:
                problems.append(f"facts.capabilities.{key}: expected boolean or null")
        checks = capabilities.get("required_checks")
        if checks is not None and (not isinstance(checks, list) or not all(isinstance(item, str) for item in checks)):
            problems.append("facts.capabilities.required_checks: expected string array or null")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=pathlib.Path, required=True)
    parser.add_argument("--facts", type=pathlib.Path)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--provider", choices=("github", "gitlab"))
    parser.add_argument("--repository")
    parser.add_argument("--target")
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--ttl-hours", type=int, default=24)
    args = parser.parse_args()

    if args.ttl_hours < 1:
        print("--ttl-hours must be >= 1", file=sys.stderr)
        return 2
    profile_validator = pathlib.Path(__file__).with_name("validate-ci-profile.py")
    profile_check = subprocess.run(
        [sys.executable, str(profile_validator), str(args.profile)],
        capture_output=True,
        text=True,
        check=False,
    )
    if profile_check.returncode != 0:
        detail = profile_check.stdout.strip() or profile_check.stderr.strip() or "profile validation failed"
        print(detail, file=sys.stderr)
        return 2
    if bool(args.facts) == bool(args.live):
        print("provide exactly one of --facts or --live", file=sys.stderr)
        return 2
    if args.live:
        if not args.provider or not args.repository or not args.target:
            print("--live requires --provider, --repository, and --target", file=sys.stderr)
            return 2
        if args.provider == "github":
            profile = load_json(args.profile)
            facts = collect_github_facts(args.repository, args.target, profile["stable_check"])
        else:
            now = utc_now()
            facts = {
                "schema": "cpb-forge-facts-v1",
                "provider": "gitlab",
                "repository": args.repository,
                "target_branch": args.target,
                "collected_at": iso(now),
                "adapter_version": ADAPTER_VERSION,
                "capabilities": {key: None for key in (
                    "protected_target", "pull_requests_required", "force_push_blocked",
                    "required_checks", "pr_workflow", "merge_group_workflow",
                    "merge_queue_enabled", "bypass_constrained",
                )},
                "visibility_limits": ["Live GitLab collection is not implemented in v1."],
            }
    else:
        facts = load_json(args.facts)
    problems = validate_facts(facts)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    attestation = build_attestation(facts, args.profile, args.ttl_hours)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(attestation, indent=2) + "\n")
    print(f"{attestation['overall']}: {args.output}")
    return 0 if attestation["overall"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())