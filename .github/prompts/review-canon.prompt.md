---
description: "Review one exact committed canon synchronization candidate against protected canon and visible admitted horizons without mutating authority."
name: "Review Canon"
argument-hint: "HNNN:synchronization-id --scope candidate, or --help"
agent: "Project: Planning and Design"
adapter-persona-state: "memory-only"
---
INVOCATION CONTRACT: execute this prompt only from an explicit operator invocation of
`/review-canon <HNNN>:<synchronization-id> --scope candidate` or explicit confirmation after an
agent names that exact command. Candidate publication, `/review-code`, closeout, reminders, hooks,
and controllers may recommend the command but may not invoke it. Before any tool use, adopt the
`canon-review-read-only` mode defined by `Project: Planning and Design`; stop if that mode is not
available.

If the argument contains `--help` or `-h`, output concise help only:

- purpose and the only supported candidate scope;
- exact command grammar and refusal conditions;
- protected-profile readiness, derived trust inputs, and output-root requirements;
- all four verdicts and their non-approval meaning;
- the installed deterministic-fixture limitation and uninstalled capabilities; and
- 3 to 5 realistic command examples.

Do not inspect candidates, run tools, write output, or open timing when help is requested.

## Command Grammar

Accept exactly:

```text
/review-canon <HNNN>:<synchronization-id> --scope candidate
```

Split the candidate token at its first colon. Require one `HNNN` horizon ID, one non-empty
synchronization ID with no second colon, exactly one `--scope`, and the literal scope `candidate`.
Reject omitted, malformed, inferred, duplicate, phase, horizon, promotion, or unknown scopes and
all additional flags. Do not infer a candidate from the current phase, branch, worktree, or recent
conversation.

## Exact Inputs

Read the fixed profile only from
`control-plane/framework/templates/canon-review-and-escalation-v1/profiles/CANON_REVIEW_PROFILE.json`
as authenticated by the machine runtime against protected integration. If it is absent or invalid,
report `profile-not-installed` and stop. Do not synthesize, repair, select, or accept a substitute
profile. When installed, show the profile-derived inventory before execution:

- repository root from `.cpb.yaml`;
- profile digest/ref, repository identity, candidate token/ref, protected canon ref, discovery
  manifest, included/excluded/unknown horizons, Package A/B catalogs, validator/interpreter/
  requirements digests, deterministic provider ref/tree digest, authority namespace/policy/history
  identities, limits, and allowed output parents;
- scope `candidate`, output mode, and a pre-created output root explicitly named or confirmed by
  the operator beneath one profile-authorized parent, with pre-created `requests` and `responses`.

Do not guess, abbreviate, fetch, repair, or silently omit an input. Require all refs to be locally
available commits. Require the index and worktree to be clean for every routed input path and
require current bytes to match `git show <exact-ref>:<path>`. The output root must not overlap an
input root and must be the only writable location. If any input or output boundary is unavailable,
ambiguous, dirty, uncommitted, or unverifiable, stop before Package A and provider execution and
report `invalid-input` or the runtime's canonical tool-error envelope.

## Required Workflow

1. Adopt `canon-review-read-only` mode and validate the exact command grammar before all other tool
   use.
2. Resolve and display the profile-derived inventory above. Ask only for the pre-created output
  root when it is not already named; this does not extend the slash-command grammar.
3. Invoke `control-plane/framework/scripts/review-canon.py` with the fixed profile path, candidate,
  scope, output mode, and output root. Never pass or override refs, roots, catalogs, validator,
  provider, authority, limits, or discovery membership. Unknown request digests fail closed.
4. Preserve the runtime's stage order: Package A validation first, deterministic Package B
   narrowing second, bounded fixture-provider review third, then normalized CHR emission.
5. Treat exit status `0` as a valid `clear-within-declared-visibility` report, `1` as a valid
   non-clear report, and `2` as invalid invocation or tool failure. Never relabel a nonzero result
   as success.
6. Report the exact output paths, candidate/report/frontier digests, provider-call count,
   limitations, and one runtime verdict. Relinquish `canon-review-read-only` mode when the command
   returns.

## Guardrails

- Write only the runtime's explicit CHR output family beneath the operator-confirmed output root.
- Adopt the bound persona and `canon-review-read-only` mode in session memory only. A harness adapter
  must not create, refresh, or update `.claude/.persona-state` or
  `.claude/state/active-persona.json`; prior absence or bytes must remain exact after return.
- Do not edit canon, candidate sources, horizon packets, trackers, OPS or horizon state, schemas,
  fixtures, prompts, refs, branches, index state, forge state, acknowledgments, dispositions, or
  promotion artifacts.
- Do not fetch, checkout, switch, create, update, or delete Git refs.
- Do not invoke a live LLM/model provider, model subprocess, network socket, credential, cloud
  service, live forge adapter, webhook, workflow, listener, poller, or CI job.
- Do not apply an escalation decision, synchronization disposition, promotion eligibility result,
  canon postimage, publication, merge, or promotion receipt.
- A `clear-within-declared-visibility` report is read-only evidence, not approval, global
  completeness, disposition, promotion eligibility, or promotion.
- Do not auto-run from `/review-code`, candidate publication, closeout, a reminder, hook, or
  controller. A lawful reminder names the exact command and states `review_status: not-invoked`.

## Installed And Uninstalled Behavior

Installed Package B framework behavior is candidate-only protected-profile review through Package
A, Package B's deterministic runtime, `deterministic-fixture-v1`, and explicit CHR output writes.
No project-owned protected review profile is seeded by this portable installer; invocation
fails closed until a separately governed profile/trial installs it. Live LLM
providers, live escalation/forge adapters, Package C promotion, promotion CI/merge-queue setup, and
automatic invocation are not installed.

## Timing Behavior

Do not open a timing session or emit invented `/review-canon-*` actions. The current timing
specification has no candidate-review session identifier or action vocabulary. The CHR
`generated_at` and provenance fields remain report evidence; observational trial timing is
external until a separately authorized timing contract is installed.

## Examples

```text
/review-canon H001:SYNC-001 --scope candidate
/review-canon H002:CSYNC-014 --scope candidate
/review-canon H104:canon-sync-api-auth-v2 --scope candidate
/review-canon --help
```