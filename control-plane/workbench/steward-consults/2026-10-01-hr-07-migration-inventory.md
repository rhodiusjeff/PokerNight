# HR-07 Migration Inventory And Plans

## Request And Authority

Operator request, verbatim:

> IMplement HR-07

Implemented under Project: Control Plane Steward in the already selected
`cp-v0-8-1-planning-admission` upgrade packet. This is explicit HR-07 implementation
authorization, not inferred HR-06 acceptance. Existing HR-06 review/acceptance records,
the required Windows/GLab final gate and instance lifecycle pointers remain unchanged.
LOCAL MOD - HARVEST TO CPB applies to the migration helper, test, schemas and policy.

## Delivered Slice

- Five strict Draft 2020-12 schemas: inventory, plan/request, confirmation, manifest
  and receipt; typed future journal events and migration ownership markers live in
  the manifest definitions. They grant no transaction authority.
- `planning-migration.py`: explicit `inspect` and confirmed new-run `plan`, strict
  JSON/CLI parsing, fixed in-process profile registry and installed contract pins.
- File/directory accounting with raw hashes, mode/length, root-map digest, references,
  exclusions, identity recognition, mixed/unknown/operational blockers and custody checks.
- Exact source-choice coverage, target preconditions, identity/path maps, dependency
  ordering/cycle reporting and explicit unavailable conversion/application results.
- New-run recording confined to the selected packet's `migrations/ID/` pair plus
  inventory; existing runs refuse, partial recordings remain preserved, no target writer.
- Installed policy and entry documentation describe actual command effects and limits.

No staged conversion, snapshot writer, apply/rollback, live operational migration,
ordinary-reader marker integration, agent skill or successor-slice work was implemented.
All source/target test data was in disposable directories. No actual repository data
was inventoried through the migration command or migrated.

## Focused Verification

Final focused command:

```sh
source .cp-venv/bin/activate
bash control-plane/framework/scripts/planning-migration.test.sh
```

37 tests passed in 1.051 seconds on macOS. These cover current pairs/empty and selected
bindings, legacy bindings/source-only and populated captures, recognized journals,
operational/unknown shapes, malformed/duplicate-key JSON, source refs/custody, mixed and
duplicate identities, exclusions, unsafe roots/paths, symlinks/special files, case and
target collisions, dependency cycles, exact coverage, no-op, stale root/source/target/
contract subjects, confirmation and home refusals, partial recording, existing-run
preservation, unavailable CLI operations and cross-schema typed artifact validation.

The case-insensitive filesystem collision test uses a mocked directory enumeration
when the host cannot create two differently cased siblings; that is not a native
case-sensitive-filesystem claim. No hosted forge or Windows/GLab test ran.

Earlier focused runs are development evidence, not extra distinct tests. One 32-test
run had four failures because the current-format test fixture lacked required minted
identity allocation metadata; the fixture was corrected without relaxing the runtime.
A subsequent 37-test run exposed JSON Schema's unavailable optional date-time checker.
A Pylance runtime probe confirmed `FormatChecker().conforms('not-a-date', 'date-time')`
returned true in the selected venv. The helper now registers an explicit standard-library
timestamp checker; the same 37-test suite passes. The receipt confirmation guard was
independently distinguished by that probe and required no relaxation.

Pylance reported no Python syntax errors. Final editor diagnostics and diff/JSONL checks
are recorded at the completion checkpoint; no independent code review was performed.

## Disposition

HR-07 is locally implemented and focused-test verified, awaiting independent review
and Operator acceptance. Initial/current plans state `application: unsupported-hr07`.
Schema-defined future artifacts are not evidence that their owning operations exist.
Runtime reuses POSIX planning helpers; required Windows/GLab validation remains unverified.

Preserved unrelated worktree changes to `.cpb.yaml`, `.gitignore`, deletion of `CLAUDE.md`
and two brand-document deletions. No commit, push, branch operation, forge action, live
migration, lifecycle transition or HR-08 implementation occurred.

## HR-07 Code Review

Operator request, verbatim:

> Review HR-07

Reviewed the uncommitted HR-07 helper, schemas, focused tests and installed contract
against the HR-07 slice. This is a same-session code review by the implementing
assistant, not an independent reviewer or acceptance decision. No implementation
or test file was changed. Review timestamp: 2026-10-01T16:25:32Z.

### HR07-R1: Publication Can Escape The Confirmed Run Home

Priority: P1. [Publication calls](../../framework/scripts/planning-migration.py#L465).

The run path is checked before publication, but later writes resolve the pathname
again. Replacing the newly created run directory with a symlink after `mkdir` and
before the first `publish_new_bytes` redirects all three writes outside the approved
home. The reused publisher follows directory symlinks; its exclusive final-file
creation does not protect the parent directory.

Reproduced in a disposable fixture by wrapping the first publication call: rename
the empty run directory to a retained sibling, put a symlink to the selected target
at its old path, then call the original publisher. Result: `status: planned`, with
`fixture-inventory.json`, `fixture-plan.json` and `fixture-capture.md` all created
inside the selected target. This violates HR-07's no-selected-target-writer boundary.
The probe injected a deterministic concurrent-filesystem change; it did not require
or perform any change to a real repository target.

Required repair: publish through verified, anchored directory handles with no-follow
semantics throughout the write path, or an equivalent race-resistant confined writer.
Rechecking a pathname once before writing is insufficient. Add interruption/race
fixtures for swapped run directories and ancestors, proving no target writes and
an accurate blocked/partial result.

### HR07-R2: Late Encoding Failure Reports No Changes After Publication

Priority: P2. [Capture encoding and exception handling](../../framework/scripts/planning-migration.py#L466)
and [CLI outcome](../../framework/scripts/planning-migration.py#L509).

Request validation accepts a JSON actor containing an unpaired surrogate, for example
the escaped value `\ud800`. Inventory and plan files are published first; encoding
the capture then raises `UnicodeEncodeError`. The local partial-recording handler
catches only `OSError`, so the outer `ValueError` handler returns exit 2 with
`status: blocked` and `changed: false` despite the existing two files. The run ID
cannot be retried because the incomplete directory now exists.

Reproduced through `main` with a transient request file in a disposable fixture.
Observed exit 2, blocked/no-change result, and both `fixture-inventory.json` and
`fixture-plan.json` present, with no capture. The current partial-write test injects
only `OSError` and misses this path.

Required repair: validate/encode all prospective output bytes before creating the
run, and ensure failures after any publication are reported as partial with retained
evidence. Test malformed Unicode and failures after each publication boundary.

### HR07-R3: Explicit Excluded Roots Bypass Content Exclusions

Priority: P2. [Root validation](../../framework/scripts/planning-migration.py#L103)
and [child-only exclusions](../../framework/scripts/planning-migration.py#L253).

Exclusion checks apply only to children visited by `walk`. Selecting `.git` itself,
or a descendant of an excluded credential/environment directory, passes `root_path`
and loses the excluded ancestor when constructing relative entry names. Those bytes
are then opened and hashed instead of being excluded or refused.

Reproduced with a disposable `.git/config` containing synthetic data, selecting
`.git` as the source root: inspection observed `config` and returned no exclusions.
The same route applies to directly selected `.ssh`/environment subtrees. This does
not print raw contents, but violates the explicit promise not to read Git internals
or excluded credential/environment contents.

Required repair: enforce the exclusion boundary on selected roots and their relevant
ancestors before traversal, for both source and target; add direct-root and nested-root
exclusion tests, verifying the excluded files are never opened.

### Review Verification And Disposition

The existing 37 tests passed again in 1.035 seconds. Three additional disposable
probes reproduced the findings above; they are not three passing regression tests.
No framework fixes, live migration, forge operations, commits, pushes, lifecycle
changes or successor implementation occurred. Unrelated worktree changes remain intact.

Exact reviewed helper SHA-256:

```text
99bab28d2c3bb4d44678e4b79173d02f29cbaec5c093c7c7eee88684a79cc865
```

Exact reviewed test SHA-256:

```text
d7c7bc449596d68282e29a88becc03f702a374846f21d9d117b4905ed9fd59b5
```

The five schema subjects are pinned in progress checkpoint 48. HR07-R1, HR07-R2 and
HR07-R3 remain open. HR-07 acceptance is blocked pending repairs and re-review;
independent review remains outstanding. Windows/GLab and HR-06 acceptance remain
separate unmet gates. No HR-08 or real migration authority is granted.

## Review Finding Repairs

Operator request, verbatim:

> Fix findings

Under that request, HR07-R1, HR07-R2 and HR07-R3 are locally fixed. This section
supersedes their open implementation disposition above, while preserving the original
review subjects, reproductions and limitations. No independent re-review or Operator
acceptance is claimed. Verification timestamp: 2026-10-01T16:32:05Z.

### Changes

- HR07-R1: replaced pathname publication with directory-descriptor-relative creation
  and writes. Every ancestor is opened with `O_DIRECTORY | O_NOFOLLOW`; artifact
  files use exclusive no-follow creation relative to the retained run descriptor.
  Directory device/inode identities are verified before and after publication.
  Swaps refuse or report partial without following the replacement into the target.
  Unsupported filesystem primitives refuse before creating anything; no unsafe fallback.
- HR07-R2: encode inventory, plan and capture before any directory creation. All
  ordinary exceptions after owned directory creation/publication report partial with
  retained artifacts. The surrogate-actor reproduction now returns blocked/unchanged
  with no new run home; a post-publication ValueError returns exit 4, partial and
  `changed: true`. Failure during initial directory fsync is also correctly partial.
- HR07-R3: reject selected roots with excluded directory names anywhere in their
  ancestry before either source or target scan. Direct and nested selections under
  Git, SSH/cloud credential, environment and dependency directories cannot bypass this.

The new writer owns only plan-recording files/directories. No staging, selected-target
writer, apply, rollback or resumptive migration operation was added. Incomplete files
and renamed original run homes are retained for explicit reconciliation. Descriptor
anchoring prevents symlink redirection; it is not a distributed lock against arbitrary
external edits or a claim of multi-file atomicity.

### Verification

`bash control-plane/framework/scripts/planning-migration.test.sh` passed 47 tests in
1.219 seconds with `.cp-venv` active on macOS. Ten new test methods and updated existing
failure tests cover the reported issues. Intermediate same-slice suites passed 39,
40 and 46 tests; these are not additional distinct tests.

Specific regression evidence:

- Swap the run after mkdir but before opening it: partial; selected target untouched.
- Swap run, migration home or packet during publication: partial; first artifact remains
  in the original retained directory; selected target remains empty in each fixture.
- Fail before and after each of three file publications: six cases retain the expected
  number of files and report partial. Initial directory fsync failure also retains its
  directory and reports partial.
- Surrogate actor: exact CLI exit 2/no-change result with the entire fixture unchanged.
- Non-I/O failure after two files: exact CLI exit 4, partial and changed result.
- Seven excluded names, each direct/nested and source/target: 28 cases refuse before
  `scan` can be called.
- Missing anchored-writer capability: refusal with no filesystem effects.

Pylance syntax and editor diagnostics are clear. Final diff/progress checks accompany
checkpoint 49. The existing 37-test baseline and review probes remain historical evidence;
no unrelated suite or hosted/platform test is represented as rerun.

Repaired helper SHA-256:

```text
0687702f13d6c0e680f674410d5cae991182a06bc7b832a1054ce58f0494e5a3
```

Repaired test SHA-256:

```text
5ced19e31737a60d4951a2be346c2e24c97b5ebbe811cc7041075391076ca636
```

Next boundary: independent re-review of these repairs, then Operator acceptance.
Windows/GLab remains required and unverified. Preserved all unrelated edits/deletions;
no commit, push, live data migration, forge action, lifecycle transition or HR-08 work.