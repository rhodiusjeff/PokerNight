[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Target,
    [string]$Python,
    [switch]$DryRun,
    [switch]$SkipVenv,
    [switch]$Verify
)
$ErrorActionPreference = 'Stop'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required on PATH. Install Git for Windows before running this installer.'
}
$Candidates = @('py', 'python', 'python3')
if ($Python) { $Candidates = @($Python) }
$PythonCommand = $null
$PythonArgs = @()
foreach ($Candidate in $Candidates) {
    if (-not (Get-Command $Candidate -ErrorAction SilentlyContinue)) { continue }
    $Prefix = @()
    if ([System.IO.Path]::GetFileNameWithoutExtension($Candidate) -eq 'py') { $Prefix = @('-3') }
    & $Candidate @Prefix -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'
    if ($LASTEXITCODE -eq 0) {
        $PythonCommand = $Candidate
        $PythonArgs = $Prefix
        break
    }
}
if (-not $PythonCommand) { throw 'Python 3.10+ is required. Install native Windows Python, or pass -Python with its executable path.' }
$Installer = Join-Path $PSScriptRoot 'installer/install.py'
$InstallArgs = @($Installer, '--target', $Target)
if ($DryRun) { $InstallArgs += '--dry-run' }
if ($SkipVenv) { $InstallArgs += '--skip-venv' }
if ($Verify) { $InstallArgs += '--verify' }
& $PythonCommand @PythonArgs @InstallArgs
exit $LASTEXITCODE