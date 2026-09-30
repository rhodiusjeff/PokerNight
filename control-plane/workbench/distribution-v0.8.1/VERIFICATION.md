# Distribution Verification

Revision 0.8.1-portable.2, 2026-09-29. This is packaging evidence, not framework
release approval. This revision replaces the WSL-based Windows launcher with native
PowerShell/Python; the earlier revision's evidence is not native Windows evidence.

## Completed

- Eleven focused installer tests: dry-run, preservation, exact backups, collisions,
  existing-controller refusal, payload tampering, unsafe paths, invalid settings,
  failure rollback, installed-file tampering, native venv path selection and
  reparse-point refusal routing. The latter two use local platform simulations.
- Bash launcher syntax and PowerShell launcher syntax.
- PowerShell forwarding with a mocked native Python executable: Windows paths
  containing spaces, dry-run and offline-install flags remain intact. No WSL call.
- Revision 2 extracted-ZIP full installation through the actual PowerShell 7 launcher
  on macOS passed: native interpreter selection, dry-run, venv/pip setup, preservation,
  backups, installed hashes and reinstallation refusal. This is not Windows-host evidence.
- Revision 2 extracted-ZIP installation through Bash in the Linux Alpine container
  passed the same checks. Both revision-2 runs verified 353 payload entries, ran the
  eleven installer tests and passed the installed planning-contract/planning-capture
  suites on their POSIX hosts. The existing README was preserved (352 installed entries).
- Earlier revision: extracted-ZIP full installation on macOS Python 3.14.7 and Linux
  (python:3.12-slim and python:3.14-alpine disposable Docker containers).
- Those earlier platform checks verified all ZIP file hashes, the 352-entry payload,
  exclusion of source instance data, Claude command coverage, read-only dry-run,
  real venv/pip setup, installed hashes, preservation of a populated test repo,
  exact backups, ignored backup paths and second-install refusal.
- Both ran the packaged nine-test installer suite and the installed
  planning-contract.test.sh and planning-capture.test.sh suites successfully.

The new revision adds control-plane/WINDOWS.md. Exact payload counts and hashes are
recorded in RELEASE.json. The existing product README is preserved, so a brownfield
install verifies one fewer installed payload entry than the full release inventory.

## Not Certified

- No real Windows host is available for native installation acceptance. PowerShell
  tests on macOS are not Windows 5.1/NTFS/native pip evidence. WSL is optional, not
  required. A Linux test is not an actual WSL-host test.
- Native installer support is separate from Windows runtime compatibility. The
  observed POSIX dependencies in WINDOWS.md remain unported.
- No hosted-forge admission, full runtime regression, real-agent workflow, upgrade
  migration, power-loss recovery or concurrency guarantee is claimed.
- New operational execution/start/closeout remains blocked in this framework version.
- Dependencies are version-ranged in the inherited requirements, not vendored or
  hash-locked. Default setup needs your configured package index.
- Checksums detect changed bytes, not publisher identity.
- The upstream test images were flagged with high-severity vulnerabilities by the
  editor image scanner (one for slim, three for Alpine). No Docker image or Dockerfile
  is distributed or required for installation. Functional test success is not a
  security certification of those images or the recipient's Python environment.

## Repeat

From the extracted package, run `python3 -m unittest discover -s tests -v`.
Run `python3 tests/smoke.py /absolute/path/to/CP-V081-0.8.1-portable.2.zip`
for a disposable full install, including network dependency setup. On Windows, use
`py -3 tests\smoke.py C:\Downloads\CP-V081-0.8.1-portable.2.zip`; it selects native
PowerShell and the Windows venv path without WSL/Bash. Git and Python venv are required.
Use `--launcher powershell` to test the actual launcher with PowerShell 7 on macOS/Linux.
POSIX runtime suites are explicitly not run on native Windows, not counted as passing.
`pwsh -NoProfile -File tests/launcher.test.ps1` checks argument forwarding only.
Linux container testing can use an independently
maintained image with Python, Git and Bash; mount the smoke script and ZIP read-only.