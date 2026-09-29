#!/usr/bin/env python3
"""Inspect planning merge candidates in isolated clones; never publish or admit work."""

import argparse
import base64
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile


module_spec = importlib.util.spec_from_file_location("planning_contract", pathlib.Path(__file__).with_name("planning-contract.py"))
contract = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(contract)
capture_spec = importlib.util.spec_from_file_location("planning_capture", pathlib.Path(__file__).with_name("planning-capture.py"))
capture = importlib.util.module_from_spec(capture_spec)
capture_spec.loader.exec_module(capture)


class GitPlanningError(ValueError):
    pass


def git(root, *arguments, check=True):
    environment = {name: value for name, value in os.environ.items() if not name.startswith("GIT_")}
    environment.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
                       GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0",
                       GIT_EDITOR="true", GIT_SEQUENCE_EDITOR="true")
    result = subprocess.run(
        ["git", "-c", "core.hooksPath=" + os.devnull, "-c", "core.fsmonitor=false",
         "-c", "commit.gpgSign=false", "-c", "rerere.enabled=false", "-C", str(root), *arguments],
        capture_output=True, env=environment, timeout=60,
    )
    if check and result.returncode:
        raise GitPlanningError(result.stderr.decode("utf-8", "replace").strip() or "Git operation failed")
    return result


def repository_root(root):
    return pathlib.Path(git(root, "rev-parse", "--show-toplevel").stdout.decode().strip()).resolve()


def resolve_commit(root, reference):
    return git(root, "rev-parse", "--verify", "--end-of-options", reference + "^{commit}").stdout.decode().strip()


def existing_operation(root):
    for name in ("rebase-merge", "rebase-apply", "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "sequencer"):
        location = pathlib.Path(git(root, "rev-parse", "--git-path", name).stdout.decode().strip())
        if not location.is_absolute():
            location = root / location
        if location.exists():
            return name
    return None


def dirty_paths(root):
    raw = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout
    return [item.decode("utf-8", "surrogateescape") for item in raw.split(b"\0") if item]


def blob_json(sandbox, revision, filename):
    path = pathlib.PurePosixPath(filename)
    if path.is_absolute() or ".." in path.parts or not path.parts or str(path) != filename:
        raise GitPlanningError("admission paths must be canonical repository-relative paths")
    entry = git(sandbox, "ls-tree", "-z", revision, "--", filename).stdout
    if not entry.startswith(b"100644 blob "):
        raise GitPlanningError(f"admission artifact is not a regular JSON file: {filename}")
    content = git(sandbox, "show", f"{revision}:{filename}").stdout
    with tempfile.NamedTemporaryFile(dir=sandbox.parent, suffix=".json") as temporary:
        temporary.write(content)
        temporary.flush()
        return contract.load_json(temporary.name)


def validate_candidate(sandbox, target, proposal, tree, paths, inventory):
    allowed = {paths[name] for name in ("specification", "proposal", "reviews", "decision")}
    unexpected = [filename for filename in inventory[1::2] if filename not in allowed]
    if unexpected:
        return {"status": "unexpected-changes", "unexpected_paths": unexpected,
                "next_action": "Isolate the admission changes; do not carry parent implementation into the proposal."}
    try:
        base = blob_json(sandbox, target, paths["specification"])
        declaration = blob_json(sandbox, proposal, paths["proposal"])
        reviews = blob_json(sandbox, proposal, paths["reviews"])
        decision = blob_json(sandbox, proposal, paths["decision"])
        execution = blob_json(sandbox, target, paths["execution"])
        result = contract.validate_admission(base, declaration, reviews, decision, execution)
        candidate = blob_json(sandbox, tree, paths["specification"])
        contract.validate_specification(candidate)
        if result["already_applied_revision"] is not None:
            contract.require(contract.digest(candidate) == contract.digest(base),
                             "already-applied proposal alters the current specification")
            return {"status": "already-applied", "revision": result["already_applied_revision"],
                    "next_action": "Report the existing admission; do not publish a duplicate."}
        contract.require(contract.digest(candidate) == contract.digest(result["result"]),
                         "actual merged candidate differs from the declared result")
        for name, value in (("proposal", declaration), ("reviews", reviews), ("decision", decision)):
            contract.require(contract.digest(blob_json(sandbox, tree, paths[name])) == contract.digest(value),
                             f"merge altered the reviewed {name} artifact")
        return {"status": "candidate-valid", "revision": candidate["revision"],
                "content_digest": candidate["content_digest"],
                "warnings": [finding["id"] for finding in result["warnings"]],
                "next_action": "Local candidate checks passed; hosted enforcement and actual admission remain separate."}
    except (GitPlanningError, contract.ContractError, OSError, ValueError) as error:
        message = str(error)
        return {"status": "stale-base" if "proposal base is stale" in message else "invalid-candidate",
                "reason": message, "next_action": "Reconcile the proposal and refresh affected review/decision evidence."}


def inspect_candidate(root, proposal_ref, target_ref, paths=None):
    root = repository_root(root)
    operation = existing_operation(root)
    observed = {"schema": "cp-planning-git-v1", "repository": str(root), "proposal_ref": proposal_ref,
                "target_ref": target_ref, "dirty_work": dirty_paths(root), "live_admission": False,
                "target_freshness": "locally-observed-ref; not a remote freshness attestation"}
    if operation:
        return {**observed, "status": "operation-in-progress", "operation": operation,
                "next_action": "Do not continue or abort an operation owned by someone else."}
    proposal = resolve_commit(root, proposal_ref)
    target = resolve_commit(root, target_ref)
    observed.update(proposal_commit=proposal, target_commit=target)
    common = git(root, "merge-base", target, proposal, check=False)
    if common.returncode:
        return {**observed, "status": "unrelated-history", "next_action": "Select and reconcile the correct planning base."}
    observed["merge_base"] = common.stdout.decode().strip()
    with tempfile.TemporaryDirectory(prefix="cp-planning-merge-") as temporary:
        sandbox = pathlib.Path(temporary) / "repo.git"
        git(pathlib.Path(temporary), "clone", "--quiet", "--mirror", "--local", "--no-hardlinks", str(root), str(sandbox))
        merged = git(sandbox, "merge-tree", "--write-tree", "--name-only", "-z", target, proposal, check=False)
        if merged.returncode not in (0, 1):
            raise GitPlanningError(merged.stderr.decode("utf-8", "replace").strip() or "merge-tree failed")
        tokens = merged.stdout.split(b"\0")
        tree = tokens[0].decode().strip()
        conflicts = []
        for token in tokens[1:]:
            if not token:
                break
            conflicts.append(token.decode("utf-8", "surrogateescape"))
        changed = git(sandbox, "diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", "-z", target, tree).stdout
        inventory = [token.decode("utf-8", "surrogateescape") for token in changed.split(b"\0") if token]
        status = "text-conflict" if merged.returncode else "merge-clean"
        validation = validate_candidate(sandbox, target, proposal, tree, paths, inventory) if paths and status == "merge-clean" else {}
    if resolve_commit(root, target_ref) != target or resolve_commit(root, proposal_ref) != proposal:
        return {**observed, "status": "refs-moved", "next_action": "Refresh the exact candidate before continuing."}
    return {**observed, "status": status, "conflicted_paths": conflicts, "candidate_tree": tree,
            "candidate_retained": False, "candidate_diff": inventory,
            "next_action": "Offer the exact rebase or deferral; do not choose a resolution." if conflicts else
            "Validate the semantic base and complete candidate; a clean Git merge is not admission.", **validation}


def rebase_offer(root, proposal_ref, target_ref):
    inspection = inspect_candidate(root, proposal_ref, target_ref)
    if inspection["status"] not in ("merge-clean", "text-conflict"):
        return inspection
    subject = {name: inspection[name] for name in ("repository", "proposal_ref", "target_ref",
                                                  "proposal_commit", "target_commit", "merge_base")}
    subject["operation"] = "isolated-rebase-committed-work-only"
    identity = contract.digest(subject)
    return {**inspection, "offer_id": identity, "offer": subject,
            "proposed_worktree": str(session_directory(pathlib.Path(subject["repository"]), identity) / "worktree"),
            "next_action": "Approve Rebase authorizes only this isolated rebase; defer performs no writes."}


def session_directory(root, identity):
    if not re.fullmatch(r"[0-9a-f]{64}", identity or ""):
        raise GitPlanningError("a valid --offer-id is required")
    directory = root / "control-plane/state/planning-local/rebases" / identity
    contract.require(directory.resolve().is_relative_to(root), "recovery session escapes repository")
    return directory


def write_session(directory, session):
    destination = directory / "session.json"
    with tempfile.NamedTemporaryFile(mode="wb", dir=directory, prefix=".session-", delete=False) as output:
        temporary = pathlib.Path(output.name)
        output.write(json.dumps(session, indent=2, ensure_ascii=True).encode())
        output.flush()
        os.fsync(output.fileno())
    try:
        os.replace(temporary, destination)
        capture.sync_directory(directory)
    finally:
        temporary.unlink(missing_ok=True)


def load_session(root, identity):
    directory = session_directory(root, identity)
    session = contract.load_json(directory / "session.json")
    contract.require(session.get("schema") == "cp-planning-rebase-v1" and session.get("id") == identity,
                     "invalid recovery session")
    contract.require(session["offer"]["repository"] == str(root) and contract.digest(session["offer"]) == identity,
                     "recovery offer binding changed")
    sandbox = directory / "worktree"
    contract.require(not sandbox.is_symlink() and sandbox.resolve().is_relative_to(directory.resolve()),
                     "recovery worktree escapes session")
    return directory, sandbox, session


def resolution_digest(sandbox):
    return contract.digest(resolution_snapshot(sandbox))


def refs_match(root, session):
    try:
        return all(resolve_commit(root, session["offer"][name + "_ref"]) == session["offer"][name + "_commit"]
                   for name in ("proposal", "target"))
    except GitPlanningError:
        return False


def inferred_recovery_state(sandbox, session):
    operation = existing_operation(sandbox)
    if operation:
        verify_owned_rebase(sandbox, session)
        return "conflicted"
    if session["status"] in ("rebase-starting", "conflicted"):
        head = resolve_commit(sandbox, "HEAD")
        if head == session["offer"]["proposal_commit"]:
            return "prepared" if session["status"] == "rebase-starting" else "operation-ended"
        if not git(sandbox, "merge-base", "--is-ancestor", session["offer"]["target_commit"], head, check=False).returncode:
            return "needs-revalidation"
        return "inconsistent-recovery"
    return session["status"]


def verify_owned_rebase(sandbox, session):
    operation = existing_operation(sandbox)
    contract.require(operation in ("rebase-merge", "rebase-apply"), "no owned rebase is in progress")
    directory = sandbox / ".git" / operation
    contract.require((directory / "orig-head").read_text().strip() == session["offer"]["proposal_commit"],
                     "rebase original head is not owned by this session")
    contract.require((directory / "onto").read_text().strip() == session["offer"]["target_commit"],
                     "rebase target is not owned by this session")


def recovery_status(root, identity):
    directory, sandbox, session = load_session(root, identity)
    if not (sandbox / ".git").is_dir():
        return {"status": "setup-incomplete", "offer_id": identity, "live_admission": False,
                "next_action": "Resume the same setup; do not discard partial work."}
    operation = existing_operation(sandbox)
    conflicts = [name.decode("utf-8", "surrogateescape") for name in
                 git(sandbox, "diff", "--name-only", "--diff-filter=U", "-z").stdout.split(b"\0") if name]
    refs_current = refs_match(root, session)
    return {"status": inferred_recovery_state(sandbox, session), "offer_id": identity, "worktree": str(sandbox),
            "operation": operation, "conflicted_paths": conflicts, "refs_current": refs_current,
            "resolution_digest": resolution_digest(sandbox), "live_admission": False,
            "next_action": "Source/target refs moved or are unavailable; preserve recovery, refresh the offer, or explicitly abort this owned operation."
            if not refs_current else "Resolve only with explicit authority; stage resolved files, inspect the new digest, then confirm continue."
            if operation else "Reconcile and revalidate proposal/base/result and affected reviews; do not reuse stale approval."}


def run_rebase(directory, sandbox, session):
    session["status"] = "rebase-starting"
    write_session(directory, session)
    result = git(sandbox, "rebase", "--no-autostash", "--onto", session["offer"]["target_commit"],
                 session["offer"]["merge_base"], check=False)
    if result.returncode and existing_operation(sandbox) not in ("rebase-merge", "rebase-apply"):
        session["status"] = "rebase-error"
        write_session(directory, session)
        raise GitPlanningError(result.stderr.decode("utf-8", "replace"))
    session["status"] = "conflicted" if result.returncode else "needs-revalidation"
    write_session(directory, session)


def start_rebase(root, proposal_ref, target_ref, identity, confirmed):
    contract.require(confirmed, "rebase requires explicit confirmation of the current offer")
    root = repository_root(root)
    offered = rebase_offer(root, proposal_ref, target_ref)
    contract.require(offered.get("offer_id") == identity, "rebase offer changed; present a fresh offer")
    directory = session_directory(root, identity)
    with capture.local_writer(root):
        if (directory / "session.json").exists():
            directory, sandbox, session = load_session(root, identity)
            if (sandbox / ".git").is_dir():
                session["status"] = inferred_recovery_state(sandbox, session)
                write_session(directory, session)
            if session["status"] != "prepared":
                return recovery_status(root, identity)
        else:
            capture.ensure_directory(root, directory)
            session = {"schema": "cp-planning-rebase-v1", "id": identity, "offer": offered["offer"], "status": "prepared"}
            write_session(directory, session)
            sandbox = directory / "worktree"
        if not sandbox.exists():
            git(directory, "clone", "--quiet", "--no-checkout", "--local", "--no-hardlinks", str(root), str(sandbox))
        contract.require((sandbox / ".git").is_dir(), "partial recovery clone needs explicit repair; no files were removed")
        contract.require(existing_operation(sandbox) is None, "setup contains an unexpected Git operation")
        git(sandbox, "config", "user.name", "Control Plane local recovery")
        git(sandbox, "config", "user.email", "local-recovery@example.invalid")
        if not git(sandbox, "show-ref", "--verify", "--quiet", "refs/heads/cp-recovery", check=False).returncode:
            contract.require(resolve_commit(sandbox, "refs/heads/cp-recovery") == offered["proposal_commit"],
                             "prepared recovery branch changed")
            contract.require(git(sandbox, "symbolic-ref", "HEAD").stdout.strip() == b"refs/heads/cp-recovery",
                             "recovery worktree is on a different branch")
        else:
            git(sandbox, "checkout", "--quiet", "-b", "cp-recovery", offered["proposal_commit"])
        contract.require(refs_match(root, session), "source or target moved during setup; refresh the offer")
        run_rebase(directory, sandbox, session)
    return recovery_status(root, identity)


def resolution_snapshot(sandbox):
    files = {}
    names = (git(sandbox, "ls-files", "--modified", "--others", "-z").stdout +
             git(sandbox, "diff", "--cached", "--name-only", "-z").stdout).split(b"\0")
    for encoded in names:
        if not encoded:
            continue
        relative = encoded.decode("utf-8", "surrogateescape")
        source = sandbox / relative
        if source.is_symlink():
            files[relative] = {"symlink": os.readlink(source)}
        elif source.is_dir():
            raise GitPlanningError("untracked directory requires explicit preservation before recovery: " + relative)
        elif source.exists():
            contract.require(source.resolve().is_relative_to(sandbox.resolve()), "resolution path escapes recovery worktree")
            files[relative] = {"bytes_base64": base64.b64encode(source.read_bytes()).decode()}
        else:
            files[relative] = {"deleted": True}
    return {"head": resolve_commit(sandbox, "HEAD"), "files": files,
            "index_base64": base64.b64encode((sandbox / ".git/index").read_bytes()).decode(),
            "staged_diff_base64": base64.b64encode(git(sandbox, "diff", "--cached", "--no-ext-diff", "--binary", "HEAD").stdout).decode(),
            "worktree_diff_base64": base64.b64encode(git(sandbox, "diff", "--no-ext-diff", "--binary").stdout).decode()}


def preserve_resolution(directory, sandbox, digest):
    snapshot = resolution_snapshot(sandbox)
    contract.require(contract.digest(snapshot) == digest, "resolution changed before preservation; inspect and confirm again")
    snapshot["resolution_digest"] = digest
    destination = directory / f"resolution-{digest}.json"
    content = json.dumps(snapshot, sort_keys=True, ensure_ascii=True).encode()
    try:
        capture.publish_new_bytes(destination, content)
    except FileExistsError:
        contract.require(destination.read_bytes() == content, "resolution snapshot differs from retained evidence")
        capture.sync_directory(directory)


def finish_rebase(root, identity, action, expected_resolution, confirmed):
    contract.require(confirmed, f"{action} requires explicit scoped confirmation")
    root = repository_root(root)
    with capture.local_writer(root):
        directory, sandbox, session = load_session(root, identity)
        verify_owned_rebase(sandbox, session)
        current = resolution_digest(sandbox)
        contract.require(current == expected_resolution, "resolution changed; inspect and confirm the current subject")
        if action == "continue":
            contract.require(recovery_status(root, identity)["refs_current"], "source or target moved; preserve recovery and refresh the offer")
            contract.require(not git(sandbox, "diff", "--name-only", "--diff-filter=U").stdout, "unresolved conflict paths remain")
            contract.require(not git(sandbox, "diff", "--name-only").stdout, "stage the explicitly approved resolution before continuing")
        preserve_resolution(directory, sandbox, current)
        result = git(sandbox, "rebase", "--" + action, check=False)
        if result.returncode and existing_operation(sandbox) not in ("rebase-merge", "rebase-apply"):
            raise GitPlanningError(result.stderr.decode("utf-8", "replace"))
        session["status"] = "aborted" if action == "abort" else ("conflicted" if result.returncode else "needs-revalidation")
        if action == "abort":
            contract.require(resolve_commit(sandbox, "HEAD") == session["offer"]["proposal_commit"], "abort did not restore the original proposal")
        write_session(directory, session)
    return recovery_status(root, identity)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--action", choices=("inspect", "offer", "start", "status", "continue", "abort", "defer"), default="inspect")
    parser.add_argument("--proposal-ref")
    parser.add_argument("--target-ref")
    parser.add_argument("--offer-id")
    parser.add_argument("--resolution-digest")
    parser.add_argument("--confirmed", action="store_true")
    for name in ("specification", "proposal", "reviews", "decision", "execution"):
        parser.add_argument(f"--{name}-path")
    args = parser.parse_args()
    try:
        paths = {name: getattr(args, name + "_path") for name in ("specification", "proposal", "reviews", "decision", "execution")}
        if any(paths.values()) and not all(paths.values()):
            raise GitPlanningError("candidate validation requires all five artifact paths")
        if args.action in ("inspect", "offer", "start") and not (args.proposal_ref and args.target_ref):
            raise GitPlanningError("proposal and target refs are required")
        if args.action == "inspect":
            result = inspect_candidate(args.root, args.proposal_ref, args.target_ref, paths if all(paths.values()) else None)
        elif args.action == "offer":
            result = rebase_offer(args.root, args.proposal_ref, args.target_ref)
        elif args.action == "start":
            result = start_rebase(args.root, args.proposal_ref, args.target_ref, args.offer_id, args.confirmed)
        elif args.action == "status":
            result = recovery_status(repository_root(args.root), args.offer_id)
        elif args.action in ("continue", "abort"):
            result = finish_rebase(args.root, args.offer_id, args.action, args.resolution_digest, args.confirmed)
        else:
            result = {"status": "deferred", "live_admission": False, "next_action": "No rebase or state mutation performed."}
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0 if result["status"] in ("merge-clean", "candidate-valid", "already-applied", "needs-revalidation", "aborted", "deferred") else 2
    except (GitPlanningError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "error", "message": str(error), "live_admission": False}))
        return 1


if __name__ == "__main__":
    sys.exit(main())