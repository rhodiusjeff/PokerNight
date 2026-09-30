# V0.8.1 Brownfield Distribution Consult

Date: 2026-09-29. LOCAL MOD - HARVEST TO CPB.

## Consult

The Operator requested packaging this project's locally enhanced V0.8.1 control plane,
a simple Windows/Linux installer for an existing project, recovery of the original
V0.8 installer session, and an email-sized ZIP. This authorizes distribution work,
not lifecycle transitions, product implementation, Git commits/pushes or email sending.

Session 1baedc73-131b-41a5-894a-1454ef850adf in the ControlPlane repository records the
original CP-V08 distribution and its installation into PokerNight. The original
distribution remains at /Users/jmsimpson/Documents/GitHub/CP-V08, read-only in this task.
It included Copilot and Claude, an isolated Python environment, dry-run, checksums,
clean state and verification; it deliberately supported greenfield macOS/Linux only.
The installation turn recorded 293 verified files and preservation of the existing README.

The local planning-install.py helper is the appropriate V0.8.1 snapshot builder: its
positive allowlist excludes instance data, secrets/local adapters, product files and
the project-specific upgrade coordinator. It deliberately refuses existing destination
directories and uses Unix filesystem primitives. Reusing it unchanged to install into
a brownfield repo would fail. The new distribution builder reuses that helper only to
create a temporary payload, then generates portable release metadata and clean state.

The new installer is separate under control-plane/workbench/distribution-v0.8.1 so this
task does not modify the old distribution or relax the installed helper's contract.
It preserves existing README and product files, backs up and appends shared guidance,
merges Claude hooks without replacing permissions, and refuses all other filename
collisions and existing control-plane roots. A dry-run must not write or download.
Backups are ignored, since recipient settings can be sensitive. Caught failures restore
files; this is not a concurrent-write, power-loss or upgrade transaction.

Windows support means a PowerShell launcher into WSL 2, not native Windows Python.
The runtime includes Bash, POSIX filesystem operations and local Git workflows; a
native Windows runtime port exceeds this packaging task and is not silently claimed.
Linux and macOS can use the Bash launcher. Recipients must review additive instruction
precedence against their existing project rules before operating the framework.

Package status is a portable snapshot, not release certification. New operational
start/closeout remains blocked by the current installed contracts. Installation does
not admit requirements, initialize a horizon, approve existing project work or bypass
workflow gates. A successful fixture or install is not a lifecycle readiness claim.

## Stable Patterns

Reuse the maintained allowlist for payload selection; make brownfield merging a separate
explicit layer. Never copy source instance state. Keep backups exact and nonpublished,
check all collisions before writes, and distinguish installer platform support from
full runtime certification. These are harvest candidates, not universal approval-policy
changes. No source tracker/ledger/Canon/archive is edited or admitted by this work.

## Verification

Initial focused suite: nine tests passed, covering preservation, exact backups, dry-run,
collisions, existing-controller refusal, package tampering, invalid settings, unsafe paths,
caught-failure rollback and receipt verification. Bash and PowerShell syntax passed.
The first temporary ZIP contains 352 payload files. Extracted-ZIP platform checks passed
on macOS Python 3.14.7 and a Debian-based python:3.12-slim Linux Docker container. Both
performed actual venv/pip installation, verified 351 installed entries with the existing
README preserved, checked exact backups and ignored backup paths, refused reinstallation,
and ran the packaged installer suite plus installed planning-contract/planning-capture
suites successfully. Package content checksums, exclusions and Claude command coverage passed.
PowerShell argument forwarding passed with a mocked wsl.exe after fixing a test-stub
scope error. No actual Windows host is available; this cannot certify Windows/WSL E2E.

The final ZIP and companion SHA-256 are generated under the distribution's ignored dist/
directory. VERIFICATION.md inside the package records measured scope and limitations.
Generated temporary archives remain ignored under test-build/; no source framework
files or existing project work were altered. No lifecycle readiness state was advanced.

The final editor check flagged one high-severity issue in the Debian test image.
A second functional Linux run with python:3.14-alpine passed but that base showed three
high-severity issues. Rather than expand this packaging task into upstream image repair,
the disposable Dockerfile was removed from the source and distribution. No container
image is shipped or required. VERIFICATION.md retains the warnings and distinguishes
functional installation evidence from security certification. The final archive is
rebuilt without the test-container recipe; runtime/installer code remains unchanged.

## Archive Comparison

Use the ZIP in `dist/email`. The ZIP directly in `dist` is the earlier build.
The final email version removes the Docker test recipe whose base image triggered
security warnings, updates verification notes, and refreshes generated timestamps
and checksums. Installer and framework code are identical. Both archives passed
Linux/macOS installation checks. The earlier build was retained rather than overwritten.

Direct ZIP comparison confirmed only one removed entry (tests/Dockerfile) and four
changed entries: CHECKSUMS.sha256, RELEASE.json, VERIFICATION.md and the generated
payload/control-plane/state/CONTROL_PLANE_STATE.json. The latter changes only
last_updated, from 2026-09-29T17:43:34.160353+00:00 to
2026-09-29T17:46:01.795975+00:00. No archive was modified during this comparison.

## Native Windows Revision

The Operator explicitly corrected the packaging requirement: Windows must be native,
without WSL. There are two installers: native PowerShell/Windows Python, and Bash/Python
for Linux, macOS and optional WSL. Earlier statements restricting Windows to WSL are
superseded for installation by 0.8.1-portable.2; old archives are retained unchanged.

The controlling installer rejected os.name == nt and assumed bin/python. The bounded
fix removes that rejection, selects Scripts/python.exe on Windows, avoids ineffective
POSIX chmod there and rejects reparse points as well as symlinks. PowerShell now selects
native py -3/python/python3 or an explicit interpreter and forwards native paths without
WSL/Bash/path translation. Eleven local installer tests and the native-forwarding mock
passed. An initial launcher test expectation used an unresolved ../ path; normalizing
the test path fixed the assertion without changing the working launcher invocation.

The framework itself still imports fcntl in planning-capture.py/planning-execution.py
and uses POSIX descriptor APIs and Bash in relevant workflows. These are runtime
portability blockers, not solved by a native installer or Git Bash. WINDOWS.md is
packaged and installed to preserve that distinction. No complete native runtime or
actual Windows-host acceptance is claimed. This task changes packaging only, with no
source framework/runtime/prompt semantics or lifecycle state changes.

The revision-2 ZIP passed full installation through the actual PowerShell 7 launcher
on macOS and the Bash launcher in the Linux Alpine container, including real venv/pip,
preservation, backups, checksums, reinstallation refusal, eleven packaged installer
tests and the installed POSIX planning-contract/planning-capture suites. Its payload
contains 353 entries; preserving README results in 352 installed entries. Diagnostics
are clear. The new email attachment is CP-V081-0.8.1-portable.2.zip; version .1 remains
the superseded Windows-to-WSL installer, not the native deliverable.