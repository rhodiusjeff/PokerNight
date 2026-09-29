# Existing Horizon Data Scrub

Date: 2026-09-29. Operator request: "I want to scrub the H000 horizon from the repo.
Then we will set up for a manual validation run. REport back when all exising horizons
are scrubbed". Per the existing explicit repository test-reset permission, this is
physical removal of current horizon data, not semantic inception scrub, abandonment,
closeout, admission, upgrade completion or product execution.

## Inventory And Preservation

Only one current horizon packet existed: control-plane/horizons/H000-poker-night.
Its 40 tracked files included captures, proposals, admission approvals/bundle, the
tracker/archive, 11 phase prompts, review/side-track ledgers and packet timing/current.
All 11 phases were not-started; archive rolled_nodes and review-unit entries were empty.
The side-track table was empty: active-side-track count 0, oldest-active-age not applicable.
No closeout or published review evidence contradicted those progress states. The tracker's
old proposed-laydown prose remained historical; it did not indicate completed execution.

Verified all 67 payload SHA-256 values in the external inception pack at
/Users/jmsimpson/Documents/poker-night-inception-pack. Four original source documents
were also compared byte-for-byte with the current repository copies. The recovered fifth
source remains preserved and hash-verified, not a claim of new product interpretation.

Preserved the entire current horizon tree before deletion in:
control-plane/state/validation-runs/cp-v0.8.1-upgrade/horizons-before-scrub-20260929T154946Z.tar.gz.
Compared all 40 archived file byte strings and paths against the live tree successfully.
Archive SHA-256: 25d42147477e2de6dd32437f32da89261b333456261e51e64be8d07eb23d7f9e.

## Result

Removed all 40 H000 files and their empty packet directories. The control-plane/horizons
root is empty. Direct resolver checks return no active or archived candidates for
CP-101 through CP-111. No control-plane/state/planning-local/binding.json existed and
none was created. H000's packet-local CP-101 timing pointer was removed with the packet.

Added an explanatory note to CONTROL_PLANE_STATE.json and updated its date, preserving
the upgrading mode, selected upgrade packet/coordinator and previous notes. No lifecycle
state transition occurred. Manual-validation baseline/context setup has NOT started.

## Preserved Boundaries

The repaired framework, uncommitted retirement fixes, source-pack originals outside the
repo, upgrade records, retained test fixtures/archives, historical workbench references,
instance timing history and archive/ history are preserved. Historical links to removed
paths are historical references, not active horizon ownership; no broad prose scrub was
performed. No new horizon or repository-level specification/execution baseline was created.

Git branches, remote-tracking refs, remote branches/tags and branch-tracking configuration
were not deleted. They are history/remote resources, not active horizon packets in this
worktree. No Git-history purge, commit or push was requested or performed. Switching to an
older branch/commit can still show its historical H000 tree; this cleanup is uncommitted
on the current upgrade branch until separately authorized publication.

The agreed cleanup condition is met: zero current horizon packets and no active horizon
binding in this checkout. This does not itself establish E2E readiness or full upgrade
completion. Instance remains upgrading; release readiness not-assessed. Next step is
separately authorized manual-validation setup, not automatic execution of the prior plan.

## Inception Pack Used For Horizon Testing

Operator asked which inception pack was used. Checked the retained SOURCE_ONLY_TRIAL.md
in the selected upgrade packet. The horizon-planning corpus was the external lifted pack
at /Users/jmsimpson/Documents/poker-night-inception-pack, specifically its sources/ directory:

- 2026-09-23-operator-domain-and-surface-discussion.md
- 2026-09-24-poker-night-inception.md
- 2026-09-25-league-rules-chunking-session.md
- 2026-09-25-operator-league-rules-capture.md
- 2026-09-28-operator-decisions-recovered.md

The agent read MANIFEST.md and reported reading all five source files in full. reference/
and framework-notes/, plus old H000 derived Canon, trackers and phase plans, were excluded
as product inputs. The 67-file preservation pack is larger than the five-file test corpus.
The source extraction report covers 24 bounded topics, not exhaustive adoption of every
clause. Admission/controller mechanics separately used small synthetic fixtures rather
than a completed admission of the entire Poker Night corpus. The external pack survives
the H000 scrub; its 67 payload hashes and four directly copied source files were verified
before deletion. This answer creates no new horizon or manual test fixture.