# Control Plane V0.8.1

A portable snapshot of the locally enhanced V0.8.1 control plane. Includes canonical
Copilot agents, prompts, skills, governance, scripts and templates. Other harness
bindings are deferred and are not packaged. No PokerNight Canon, captures, horizons, trackers, archives, workbench,
credentials, product assets, or execution history is installed.

For installation, read INSTALL.md in the extracted distribution. Linux uses
install.sh; Windows uses install.ps1 with native Windows Python, without WSL.
macOS and WSL use the Linux/Bash launcher. Revision 0.8.1-portable.2 replaces the
previous Windows-to-WSL launcher. See WINDOWS.md for separate runtime limitations.

## After Installation

Activate `.cp-venv` before framework commands and before launching VS Code.
On Windows, activate `.cp-venv\Scripts\Activate.ps1` and use native VS Code. Inspect
the additive guidance in AGENTS.md and .github/copilot-instructions.md
for conflicts with your project's existing policies before asking an agent to work.
Existing instructions are preserved, but conflicting policies need an operator decision.

Select **Project: Planning and Design**, **Project: Codegen**, or
**Control Plane: Lifecycle Facilitator**. Start with `/plan-work --help` or `/horizon --help`.
On supported POSIX runtimes, capture intent with `/plan-work --capture ad-hoc`.
The current capture helper is not Windows-native; read WINDOWS.md first on Windows.
A new horizon requires an explicit
`/horizon --create` invocation and the actual remote/target prerequisites.

Treat the existing codebase and project documentation as evidence to assess, not as
automatically approved Canon. Installation never admits current work, creates a
horizon, changes branches, commits, pushes, or grants execution permission.
The source project's active upgrade state is not inherited.

## Important Limits

This packages current capability, not a claim that V0.8.1 is a complete production
release. New-format planning and origin-selected gh/glab admission are present.
New operational execution/start/closeout integration is still blocked by the installed
contracts. Legacy execution paths retain their separate gates. Installing this
snapshot does not remove those blocks or certify hosted-forge behavior.

This is a first installation into an existing Git project, not an upgrade or
migration of an existing control plane. Existing control-plane roots and conflicting
framework filenames cause refusal. Product files and README are preserved.

Installation requires Python 3.10+, Git, venv and pip. The Linux/macOS/WSL launcher
also requires Bash; the native Windows installer does not. Default installation downloads
the framework requirements into `.cp-venv`; `--skip-venv` performs offline file
installation only. Copilot subscriptions, gh/glab, PowerShell
for optional runtime suites, diagram tools, MCP providers and credentials are
separate prerequisites for the workflows that use them.

Some inherited framework helpers use `fcntl`, POSIX descriptor APIs and Bash.
Native installation success is not evidence that these workflows work on Windows.
WINDOWS.md lists the observed blockers; this packaging update does not port them.

Framework docs retain labeled historical procedures. Current canonical prompts and
the V0.8.1 section of control-plane/framework/docs/control-system-user-guide.md
govern current workflows; historical examples are not your project's policy.