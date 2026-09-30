$ErrorActionPreference = 'Stop'
$global:PythonTestCalls = [System.Collections.Generic.List[object]]::new()
function global:TestNativePython {
    $global:PythonTestCalls.Add(@($args))
    $global:LASTEXITCODE = 0
}
$Launcher = (Resolve-Path (Join-Path $PSScriptRoot '../install.ps1')).Path
& $Launcher -Target 'C:\Projects\Existing Project' -Python TestNativePython -DryRun -SkipVenv
if ($global:PythonTestCalls.Count -ne 2) { throw 'Expected version check and native installer invocation' }
$Actual = $global:PythonTestCalls[1]
$Expected = @((Join-Path (Split-Path $Launcher) 'installer/install.py'), '--target', 'C:\Projects\Existing Project', '--dry-run', '--skip-venv')
if (($Actual | ConvertTo-Json -Compress) -ne ($Expected | ConvertTo-Json -Compress)) {
    throw "Incorrect native Python forwarding: $($Actual | ConvertTo-Json -Compress)"
}
Write-Output 'PASS: PowerShell calls native Python with Windows paths and flags intact; no WSL or Bash (mock, not Windows E2E).'