# Confirmed Defaults: Append And Canon r2 Receipt

Date: 2026-09-29
Persona: Project: Planning and Design
Invocation provenance for each operation: operator-confirmation
Actual Operator confirmation of the four listed defaults (verbatim): "Yes"
Actual Operator confirmation of the two named operations (verbatim): "run both"

The assistant offered append followed by Canon reconciliation for this capture. These
confirmations authorize only those bounded operations, not approval of every r1 assumption,
work shaping, complete proposal, admission, implementation or forge publication.

## Operation 1: Append

```text
python3 control-plane/framework/scripts/planning-capture.py append --root /Users/jmsimpson/Documents/GitHub/PokerNight --id ADHOC-7fd789738d5348cbbbd4f4cb378fbecf --expected-digest 4b6cbbe183004c1dfd26ccb300967a1d550709a511452bee40a36c01923f99c2 --source /Users/jmsimpson/Documents/GitHub/PokerNight/control-plane/ad-hoc/assets/ADHOC-7fd789738d5348cbbbd4f4cb378fbecf/requests/005-confirmed-defaults-source.md --confirmed
```

- Input source SHA-256: 677069c28c0a4c38ba1772b07b82c664fd8c82a29f1465615b8488424e9f90b8
- Input capture SHA-256: 4b6cbbe183004c1dfd26ccb300967a1d550709a511452bee40a36c01923f99c2
- Output capture SHA-256: d96c7dfa21082401fb0845ea96f9ba6d82b890fc8b37474316adfc3cd3b7838e
- Verification: helper inspection validated four sources, unchanged prior source hashes,
  retained r1 and no complete proposal. Prior capture was retained under history.
- Timing: control-plane/state/timing/IN-PLAN__20260929T172832Z__007874017962.jsonl,
  completed successfully before starting the second operation.

## Operation 2: Canon Reconciliation

```text
python3 control-plane/framework/scripts/planning-work.py --root /Users/jmsimpson/Documents/GitHub/PokerNight --context ADHOC-7fd789738d5348cbbbd4f4cb378fbecf draft --section canon --request /Users/jmsimpson/Documents/GitHub/PokerNight/control-plane/ad-hoc/assets/ADHOC-7fd789738d5348cbbbd4f4cb378fbecf/requests/006-canon-draft-r2.json --expected-digest d96c7dfa21082401fb0845ea96f9ba6d82b890fc8b37474316adfc3cd3b7838e --confirmed
```

- Request SHA-256: 9b92df3a13224d02f539ad22626a6ea70a976252dbaf25d307c1431f5c4da21e
- Input capture SHA-256: d96c7dfa21082401fb0845ea96f9ba6d82b890fc8b37474316adfc3cd3b7838e
- Output capture SHA-256: 2e8934c8b88fe938572597d7ceecd8020a7d381c3e0062958ad16449fed3ac74
- Verification: helper schema validation and inspection passed. Structured comparison
  confirmed r1 equals its original request plus section=canon, r2 equals its new request
  plus section=canon, exactly two drafts and four sources exist, and no proposal exists.
- r2 explicitly preserves retained r1 candidates and identifies all revisions/additions.
  It does not claim the exact browser matrix or mid-game setup behavior was approved.
- Timing: control-plane/state/timing/IN-PLAN__20260929T172910Z__005154013160.jsonl.
  The runtime log owns completion evidence for this operation.

Both helpers returned updated=true and admitted=false. Environment for both: repository
root, activated .cp-venv, PYTHONDONTWRITEBYTECODE=1. Sources 1-3 and r1 were preserved;
the preceding capture for each mutation was retained by the helper under history.
No operational Canon, specification, phases, execution DAG, progress, product code,
unrelated worktree content, commits or remote resources were changed.

Planning status: in-progress. Readiness: not-assessed. Next is separately authorized
work shaping; baseline/destination and remaining acceptance/setup choices still need resolution.