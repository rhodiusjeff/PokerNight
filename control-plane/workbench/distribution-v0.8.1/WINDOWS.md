# Native Windows Installation And Runtime Boundaries

Revision 0.8.1-portable.2 installs directly with Windows Python and PowerShell.
WSL, Bash and Docker are not called or required by the Windows installer.
Linux, macOS and optional WSL installations continue to use install.sh.

## Installer

Use native Python 3.10+ and Git for Windows. From the extracted package directory:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Target "C:\src\MyProject"
```

The installer creates `.cp-venv\Scripts\python.exe`, downloads the framework's Python
requirements, installs the canonical Copilot/Claude files and writes a hash receipt.
Dry-run, collision checks, shared-file backups and verification remain available.
It rejects symlinks and Windows reparse points, including junctions, along destination
paths. Use a normal local directory rather than a junction or cloud placeholder tree.
Windows ACLs are inherited, not replaced with ineffective Unix mode bits.

Activate with `. .\.cp-venv\Scripts\Activate.ps1` in the project, or invoke
`.\.cp-venv\Scripts\python.exe` directly. Native VS Code requires no WSL extension.
Legacy examples using `python3` may need the explicit native venv interpreter.

## Runtime Is Not Yet Fully Windows-Native

This is an installer change, not a completed runtime portability release. The
following observed dependencies remain in the inherited framework:

- planning-capture.py imports `fcntl` for writer locks and uses `os.O_NOFOLLOW`.
  Capture mutations and workflows importing this module cannot run under native
  Windows Python until that locking/filesystem implementation is ported.
- planning-execution.py imports `fcntl` and uses POSIX directory descriptors,
  `os.O_DIRECTORY`, `os.O_NOFOLLOW` and `dir_fd`. Installing its dependencies does
  not make those APIs available on Windows.
- Current planning-context.py uses the shared identity helper, not the retired legacy
  tag minters. Removal of those scripts does not certify the remaining runtime on Windows.
- Claude bindings and hooks are no longer packaged; other harness bindings are deferred.
  Existing destination-owned harness settings remain untouched.
- The inherited planning-install.py developer lift and planning-validation.py POSIX
  suite runner are not the native installer or a Windows acceptance test.

Git Bash is not WSL, but it also does not provide `fcntl` to native Windows Python.
Do not report a successful file installation as a working native `/plan-work` workflow.
These runtime blockers need a separate implementation/verification pass before claiming
end-to-end native Windows control-plane operation. No workflow gate is relaxed here.

## Verification Limit

The native launcher and platform-specific installer paths are covered by local tests.
This build host is macOS; no real Windows host was available to validate Windows 5.1,
NTFS behavior, native pip setup or full Windows installation. The cross-platform ZIP
smoke test can be run on Windows with `py -3 tests\smoke.py C:\Downloads\PACKAGE.zip`;
it chooses native PowerShell and tests file installation, not POSIX runtime compatibility.