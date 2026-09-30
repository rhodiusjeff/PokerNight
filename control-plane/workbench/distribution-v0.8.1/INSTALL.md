# Install Control Plane V0.8.1

Unzip the attachment outside the destination repository. Keep the extracted folder
for verification. Install into an existing Git repository without a control plane.
No administrator privileges, Git remote or Git identity are needed for installation.
Do not edit the destination concurrently. Review or back up existing work first.

## Linux

Prerequisites: Python 3.10+, Git, Bash, Python venv/ensurepip and access to your
configured Python package index. On Ubuntu/Debian, install python3-venv if missing.
From the extracted package directory:

```bash
bash install.sh --target /home/you/projects/existing-project --dry-run
bash install.sh --target /home/you/projects/existing-project
bash install.sh --target /home/you/projects/existing-project --verify
```

Then launch your harness from the activated environment:

```bash
cd /home/you/projects/existing-project
source .cp-venv/bin/activate
code .
```

macOS and WSL use the same commands with the appropriate target path. WSL is optional;
it is not required for Windows installation.

## Windows

Install native Windows Python 3.10+ (with venv/pip) and Git for Windows, with Git on
PATH. The launcher uses native Python and creates `.cp-venv\Scripts\python.exe`.
It does not call WSL, Bash, Docker or a Linux distribution. Windows PowerShell 5.1
or PowerShell 7 can launch it. Do not install from inside the target repository.

From PowerShell in the extracted package directory:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Target "C:\src\MyProject" -DryRun
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Target "C:\src\MyProject"
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Target "C:\src\MyProject" -Verify
```

This process-scoped policy does not change your machine's saved execution policy.
Organizational policy may still prohibit script execution; follow your administrator's
rules. The launcher tries `py -3`, `python`, then `python3`. Use
`-Python "C:\Path To Python\python.exe"` to select an interpreter explicitly.
You can also bypass the PowerShell launcher with native Python:

```powershell
py -3 .\installer\install.py --target "C:\src\MyProject"
```

After installation, open your native Windows workspace:

```powershell
Set-Location "C:\src\MyProject"
. .\.cp-venv\Scripts\Activate.ps1
code .
```

Follow local PowerShell policy for activation. You can use
`.\.cp-venv\Scripts\python.exe` directly without activation. Read WINDOWS.md before
running framework commands: native installation does not port the POSIX-only runtime
workflows. Those limitations are independent of WSL, which is not required or invoked.

## What It Changes

- Creates the framework, Copilot/Claude surfaces, discovery anchor and clean state.
- Preserves product files, existing README and unrelated .github/.claude files.
- Appends guidance to existing AGENTS.md, CLAUDE.md, Copilot instructions and .gitignore.
- Merges the observe-only Claude hook while preserving other settings and permissions.
- Saves exact originals of merged files under control-plane/state/install-backups/.
- Installs dependencies in a new `.cp-venv`; never changes global Python packages.
- Records installed hashes in control-plane/state/INSTALLATION.json.

The backup directory is ignored by the appended .gitignore rules because existing
settings may be sensitive. Do not publish those backups. Windows files inherit the
destination directory's ACLs; POSIX file modes are not an ACL-hardening mechanism.
Use a private project directory. No source-project settings
or credentials are bundled. Review the resulting instruction precedence before use.

Any other filename collision, existing control-plane/, .controlplane/, .cpb.yaml or
.cp-venv is refused before writes. Resolve collisions deliberately; there is no force
overwrite. Dry-run performs no writes or downloads and cannot guarantee a later pip
download. `--skip-venv` / `-SkipVenv` skips runtime setup for offline installation;
install control-plane/framework/requirements.txt into `.cp-venv` before running commands.

Caught installation failures restore changed files and remove files created by the
attempt; empty directories can remain. Interruptions, power loss, hostile/concurrent
filesystem changes are not transactional. Inspect a partial install and its backups
before retrying; never delete preexisting user files to bypass a refusal.

The `--verify` / `-Verify` check compares fresh installed files with the receipt; it is
not a general project-health check after intentional edits. Do not use the inherited
planning-install.py strict standalone-tree verifier against a brownfield repository.

## Integrity And Trust

Email both the ZIP and its `.zip.sha256` companion. On Linux check the ZIP with
`sha256sum -c CP-V081-0.8.1-portable.2.zip.sha256`; on macOS use `shasum -a 256 -c`.
On Windows compare `Get-FileHash .\CP-V081-0.8.1-portable.2.zip -Algorithm SHA256`
with the companion file. Inside the extracted folder, `sha256sum -c CHECKSUMS.sha256`
verifies package contents on Linux/macOS. Native PowerShell can verify them with:

```powershell
Get-Content .\CHECKSUMS.sha256 | ForEach-Object {
	$Expected, $Relative = $_ -split '  ', 2
	if ((Get-FileHash -LiteralPath $Relative -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Expected) {
		throw "Checksum mismatch: $Relative"
	}
}
```

Hashes detect corruption, not publisher identity; obtain the package and digest
through a trusted channel. No WSL is needed for either verification method on Windows.

Review installed changes and decide when to commit them yourself. Read README.md for
the current planning entry and known execution limitations. Installation does not
approve requirements, migrate existing workflow state, or start governed product work.