param(
    [Parameter(Position = 0, Mandatory = $false)]
    [string]$Command,

    [Parameter(Mandatory = $false, ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$ErrorActionPreference = 'Stop'

# LOCAL MOD (shape v1, 2026-07-19) - HARVEST TO CPB: anchor-based root resolution
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir
while ($ProjectRoot -and -not (Test-Path (Join-Path $ProjectRoot '.cpb.yaml') -PathType Leaf)) {
    $ProjectRoot = Split-Path -Parent $ProjectRoot
}
if (-not $ProjectRoot) { throw "Error: .cpb.yaml anchor not found above $ScriptDir" }
$CpRootLine = Select-String -Path (Join-Path $ProjectRoot '.cpb.yaml') -Pattern '^cp_root:\s*(.+)$' | Select-Object -First 1
$CpRootName = if ($CpRootLine) { $CpRootLine.Matches[0].Groups[1].Value.Trim() } else { 'control-plane' }
function Get-TimingRootForPhase {
    param([string]$PhaseId)
    if ($PhaseId -like 'OPS-*' -or $PhaseId -like 'LC-*' -or $PhaseId -like 'IN-*') {
        return (Join-Path $ProjectRoot "$CpRootName/state/timing")
    }
    $Resolver = Join-Path $ProjectRoot "$CpRootName/framework/scripts/resolve-horizon.py"
    $Relative = @(& python3 $Resolver $PhaseId --root $ProjectRoot --require-executable --field timing 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Error: $($Relative -join '; ')" }
    return (Join-Path $ProjectRoot ($Relative -join ''))
}
$TimingRoot = Join-Path $ProjectRoot "$CpRootName/state/timing"  # default; re-derived per phase-id after arg parse
$ActiveRoot = Join-Path $TimingRoot 'current'
$ReadmeTemplate = ''  # template staging retired in shape v1; README seeding is a no-op

function Show-Help {
    Write-Host 'Usage:'
    Write-Host '  timing-log.ps1 <command> [options]'
    Write-Host ''
    Write-Host 'Commands:'
    Write-Host '  open    Open or resume the active timing session for a governed execution window.'
    Write-Host '  emit    Append an event to the active timing session.'
    Write-Host '  close   Append a terminal event and close the active timing session.'
    Write-Host '  reset   Record a reset on the current session, then open a new one.'
    Write-Host '  status  Print the active log file for a governed execution window.'
    Write-Host '  help    Show this help text.'
    Write-Host ''
    Write-Host 'Common options:'
    Write-Host '  --phase-id <id>        Required governed identifier such as CP-001, IN-REFINE, or LC-MIGRATE.'
    Write-Host '  --source <value>       Event source. Defaults to runtime.'
    Write-Host '  --persona <name>       Optional persona label.'
    Write-Host '  --outcome <value>      Optional outcome such as success, blocked, deferred, or override.'
    Write-Host '  --duration-ms <value>  Optional duration for terminal events.'
    Write-Host '  --metadata <json>      Optional JSON object payload.'
    Write-Host '  --copilot-session-id <id>'
    Write-Host '                         Optional upstream Copilot session identifier recorded in metadata.'
    Write-Host '                         When omitted, open auto-resolves it from the newest live transcript'
    Write-Host '                         for this repo''s VS Code window, folder-mode or workspace-mode'
    Write-Host '                         (override root with CPB_VSCODE_USER_DIR; staleness window'
    Write-Host '                         CPB_RESOLVER_MAX_AGE_SECONDS, default 1800).'
    Write-Host '  --no-resolve           Disable auto-resolution of the Copilot session id (open only).'
    Write-Host ''
    Write-Host 'Session marker:'
    Write-Host '  Every open (new or resume) generates a unique session marker, records it in event'
    Write-Host '  metadata as session_marker, and echoes CPB-SESSION-MARKER: <token> to stderr so the'
    Write-Host '  harness transcript captures it; timing-harvest.sh reconciles the join later.'
    Write-Host ''
    Write-Host 'Examples:'
    Write-Host '  timing-log.ps1 open --phase-id CP-001'
    Write-Host '  timing-log.ps1 open --phase-id IN-REFINE --copilot-session-id vscode-chat-12345'
    Write-Host '  timing-log.ps1 emit --phase-id CP-001 --action refinement-turn --metadata ''{"code_change":true}'''
    Write-Host '  timing-log.ps1 emit --phase-id CP-001 --action review-requested --metadata ''{"review_url":"https://example.invalid/reviews/123"}'''
    Write-Host '  timing-log.ps1 close --phase-id CP-001 --action phase-session-completed --outcome success'
    Write-Host '  timing-log.ps1 reset --phase-id CP-001 --metadata ''{"reason":"replan"}'''
    Write-Host '  timing-log.ps1 status --phase-id CP-001'
    Write-Host ''
    Write-Host 'Notes:'
    Write-Host '  - The acquired project runtime writes JSONL files under control-plane/state/timing/.'
    Write-Host '  - Each governed execution window owns one log file. open resumes the current file unless reset is requested.'
    Write-Host '  - Prefer major governance events such as review publication, review-driven refinement, approval decisions, contract verification, and merge capture over transcript-level detail.'
    Write-Host '  - Missing or broken timing state is a control-plane misconfiguration and returns a non-zero exit status.'
}

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Ensure-TimingSurface {
    New-Item -ItemType Directory -Path $ActiveRoot -Force | Out-Null
    $ReadmePath = Join-Path $TimingRoot 'README.md'
    if ($ReadmeTemplate -and (Test-Path $ReadmeTemplate -PathType Leaf) -and -not (Test-Path $ReadmePath -PathType Leaf)) {
        Copy-Item -Path $ReadmeTemplate -Destination $ReadmePath
    }
}

function Get-SafePhaseId {
    param([string]$PhaseId)
    return (($PhaseId -replace '/', '_') -replace ' ', '_')
}

function Get-CurrentPointerPath {
    param([string]$PhaseId)
    return (Join-Path $ActiveRoot ("$(Get-SafePhaseId -PhaseId $PhaseId).current"))
}

function Get-ActiveLogPath {
    param([string]$PhaseId)
    $PointerPath = Get-CurrentPointerPath -PhaseId $PhaseId
    if (-not (Test-Path $PointerPath -PathType Leaf)) {
        return $null
    }
    return (Get-Content -Path $PointerPath -Raw).Trim()
}

function Get-SessionIdFromLogPath {
    param([string]$LogPath)
    $BaseName = [System.IO.Path]::GetFileNameWithoutExtension($LogPath)
    return ($BaseName -replace '^[^_]+__', '')
}

function New-SessionId {
    $Stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $Suffix = -join ((48..57) + (97..102) | Get-Random -Count 8 | ForEach-Object { [char]$_ })
    return "$Stamp`__$Suffix"
}

function Write-TimingEvent {
    param(
        [string]$LogFile,
        [string]$SessionId,
        [string]$PhaseId,
        [string]$Action,
        [string]$Source,
        [string]$Persona,
        [string]$Outcome,
        [string]$DurationMs,
        [string]$MetadataJson
    )

    $Record = [ordered]@{
        timestamp  = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        session_id = $SessionId
        phase_id   = $PhaseId
        action     = $Action
        source     = $Source
    }

    if (-not [string]::IsNullOrWhiteSpace($Persona)) {
        $Record.persona = $Persona
    }

    if (-not [string]::IsNullOrWhiteSpace($Outcome)) {
        $Record.outcome = $Outcome
    }

    if (-not [string]::IsNullOrWhiteSpace($DurationMs)) {
        $Record.duration_ms = [int]$DurationMs
    }

    if (-not [string]::IsNullOrWhiteSpace($MetadataJson)) {
        $Record.metadata = $MetadataJson | ConvertFrom-Json
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $LogFile) -Force | Out-Null
    Add-Content -Path $LogFile -Value ($Record | ConvertTo-Json -Compress -Depth 8)
}

function Merge-MetadataField {
    param(
        [string]$MetadataJson,
        [string]$Key,
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $MetadataJson
    }

    if ([string]::IsNullOrWhiteSpace($MetadataJson)) {
        return (@{ $Key = $Value } | ConvertTo-Json -Compress)
    }

    if (-not $MetadataJson.TrimStart().StartsWith('{')) {
        Fail "--metadata must be a JSON object when merging $Key"
    }

    $ParsedMetadata = $MetadataJson | ConvertFrom-Json
    if ($ParsedMetadata.PSObject.Properties.Name -contains $Key) {
        Fail "--metadata already includes $Key"
    }

    $ParsedMetadata | Add-Member -NotePropertyName $Key -NotePropertyValue $Value
    return ($ParsedMetadata | ConvertTo-Json -Compress -Depth 8)
}

function Merge-MetadataJson {
    param(
        [string]$MetadataJson,
        [string]$CopilotSessionId
    )
    return (Merge-MetadataField -MetadataJson $MetadataJson -Key 'copilot_session_id' -Value $CopilotSessionId)
}

function New-SessionMarker {
    $Stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $Suffix = [guid]::NewGuid().ToString('N').Substring(0, 12)
    return "cpbm-$Stamp-$Suffix"
}

function Get-VSCodeUserDir {
    if (-not [string]::IsNullOrWhiteSpace($env:CPB_VSCODE_USER_DIR)) {
        return $env:CPB_VSCODE_USER_DIR
    }
    $Candidates = @()
    if (-not [string]::IsNullOrWhiteSpace($env:APPDATA)) {
        $Candidates += (Join-Path $env:APPDATA 'Code/User')
    }
    if (-not [string]::IsNullOrWhiteSpace($env:HOME)) {
        $Candidates += (Join-Path $env:HOME 'Library/Application Support/Code/User')
        $Candidates += (Join-Path $env:HOME '.config/Code/User')
    }
    foreach ($Candidate in $Candidates) {
        if (Test-Path $Candidate -PathType Container) { return $Candidate }
    }
    return $null
}

function ConvertTo-LocalPathFromUri {
    param([string]$Uri)
    try {
        return ([System.Uri]::new($Uri)).LocalPath
    }
    catch {
        return $null
    }
}

function Test-PathsEqual {
    param([string]$PathA, [string]$PathB)
    if ([string]::IsNullOrWhiteSpace($PathA) -or [string]::IsNullOrWhiteSpace($PathB)) { return $false }
    $NormA = [System.IO.Path]::GetFullPath($PathA).TrimEnd('\', '/')
    $NormB = [System.IO.Path]::GetFullPath($PathB).TrimEnd('\', '/')
    $Comparison = if ($IsWindows -or $env:OS -eq 'Windows_NT') { [System.StringComparison]::OrdinalIgnoreCase } else { [System.StringComparison]::Ordinal }
    return $NormA.Equals($NormB, $Comparison)
}

function Test-WorkspaceJsonMatchesProject {
    # workspace.json holds exactly one of:
    #   {"folder":    "file:///abs/path"}                  - single-folder window
    #   {"workspace": "file:///abs/path/x.code-workspace"} - multi-root window
    param([string]$WorkspaceJsonPath)

    try {
        $Entry = Get-Content -Path $WorkspaceJsonPath -Raw | ConvertFrom-Json
    }
    catch {
        return $false
    }

    if ($Entry.PSObject.Properties.Name -contains 'folder') {
        return (Test-PathsEqual -PathA (ConvertTo-LocalPathFromUri -Uri $Entry.folder) -PathB $ProjectRoot)
    }

    if (-not ($Entry.PSObject.Properties.Name -contains 'workspace')) {
        return $false
    }

    $WorkspaceFile = ConvertTo-LocalPathFromUri -Uri $Entry.workspace
    if ([string]::IsNullOrWhiteSpace($WorkspaceFile) -or -not (Test-Path $WorkspaceFile -PathType Leaf)) {
        return $false
    }

    # .code-workspace allows JSONC; strip line comments before parsing.
    $Raw = (Get-Content -Path $WorkspaceFile) -replace '^\s*//.*$', '' -join "`n"
    try {
        $Workspace = $Raw | ConvertFrom-Json
    }
    catch {
        return $false
    }

    $WorkspaceDir = Split-Path -Parent $WorkspaceFile
    foreach ($Folder in @($Workspace.folders)) {
        if ($null -eq $Folder) { continue }
        $FolderPath = $null
        if ($Folder.PSObject.Properties.Name -contains 'path') {
            $FolderPath = $Folder.path
            if (-not [System.IO.Path]::IsPathRooted($FolderPath)) {
                $FolderPath = Join-Path $WorkspaceDir $FolderPath
            }
        }
        elseif ($Folder.PSObject.Properties.Name -contains 'uri') {
            $FolderPath = ConvertTo-LocalPathFromUri -Uri $Folder.uri
        }
        if (Test-PathsEqual -PathA $FolderPath -PathB $ProjectRoot) { return $true }
    }
    return $false
}

function Resolve-CopilotSessionId {
    # Best-effort inline resolution: the live Copilot session's transcript file
    # is the newest transcript across every VS Code window hosting this repo -
    # single-folder or multi-root. "Active" is inferred from write time, never
    # asked of VS Code. Wrong only under concurrent sessions on the same repo;
    # the session-marker harvest reconciles that case. Never fails the caller.
    $UserDir = Get-VSCodeUserDir
    if ([string]::IsNullOrWhiteSpace($UserDir)) { return $null }
    $StorageRoot = Join-Path $UserDir 'workspaceStorage'
    if (-not (Test-Path $StorageRoot -PathType Container)) { return $null }

    $MaxAgeSeconds = 1800
    if (-not [string]::IsNullOrWhiteSpace($env:CPB_RESOLVER_MAX_AGE_SECONDS)) {
        $MaxAgeSeconds = [int]$env:CPB_RESOLVER_MAX_AGE_SECONDS
    }

    $Newest = $null
    foreach ($WorkspaceJson in (Get-ChildItem -Path $StorageRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object { Join-Path $_.FullName 'workspace.json' })) {
        if (-not (Test-Path $WorkspaceJson -PathType Leaf)) { continue }
        if (-not (Test-WorkspaceJsonMatchesProject -WorkspaceJsonPath $WorkspaceJson)) { continue }
        $TranscriptsDir = Join-Path (Split-Path -Parent $WorkspaceJson) 'GitHub.copilot-chat/transcripts'
        if (-not (Test-Path $TranscriptsDir -PathType Container)) { continue }
        foreach ($Transcript in (Get-ChildItem -Path $TranscriptsDir -Filter '*.jsonl' -File -ErrorAction SilentlyContinue)) {
            if ($null -eq $Newest -or $Transcript.LastWriteTimeUtc -gt $Newest.LastWriteTimeUtc) {
                $Newest = $Transcript
            }
        }
    }

    if ($null -eq $Newest) { return $null }
    $AgeSeconds = ((Get-Date).ToUniversalTime() - $Newest.LastWriteTimeUtc).TotalSeconds
    if ($AgeSeconds -gt $MaxAgeSeconds) { return $null }
    return [System.IO.Path]::GetFileNameWithoutExtension($Newest.Name)
}

function Open-PhaseSession {
    param(
        [string]$PhaseId,
        [string]$Source,
        [string]$Persona,
        [string]$Outcome,
        [string]$MetadataJson,
        [switch]$Reset
    )

    Ensure-TimingSurface
    $PointerPath = Get-CurrentPointerPath -PhaseId $PhaseId
    $ActiveLogPath = Get-ActiveLogPath -PhaseId $PhaseId

    if (-not [string]::IsNullOrWhiteSpace($ActiveLogPath)) {
        if (-not (Test-Path $ActiveLogPath -PathType Leaf)) {
            Fail "Active timing session pointer exists for $PhaseId but the log file is missing: $ActiveLogPath"
        }

        if ($Reset) {
            Write-TimingEvent -LogFile $ActiveLogPath -SessionId (Get-SessionIdFromLogPath -LogPath $ActiveLogPath) -PhaseId $PhaseId -Action 'phase-session-reset' -Source $Source -Persona $Persona -Outcome $Outcome -DurationMs '' -MetadataJson $MetadataJson
            Remove-Item -Force $PointerPath
        }
        else {
            Write-TimingEvent -LogFile $ActiveLogPath -SessionId (Get-SessionIdFromLogPath -LogPath $ActiveLogPath) -PhaseId $PhaseId -Action 'phase-session-resumed' -Source $Source -Persona $Persona -Outcome $Outcome -DurationMs '' -MetadataJson $MetadataJson
            return $ActiveLogPath
        }
    }

    $SessionId = New-SessionId
    $LogFile = Join-Path $TimingRoot "$PhaseId`__$SessionId.jsonl"
    Write-TimingEvent -LogFile $LogFile -SessionId $SessionId -PhaseId $PhaseId -Action 'phase-session-opened' -Source $Source -Persona $Persona -Outcome $Outcome -DurationMs '' -MetadataJson $MetadataJson
    Set-Content -Path $PointerPath -Value $LogFile
    return $LogFile
}

function Emit-PhaseEvent {
    param(
        [string]$PhaseId,
        [string]$Action,
        [string]$Source,
        [string]$Persona,
        [string]$Outcome,
        [string]$DurationMs,
        [string]$MetadataJson,
        [string]$LogFile
    )

    Ensure-TimingSurface

    if ([string]::IsNullOrWhiteSpace($LogFile)) {
        $LogFile = Get-ActiveLogPath -PhaseId $PhaseId
    }

    if ([string]::IsNullOrWhiteSpace($LogFile)) {
        Fail "No active timing session for $PhaseId; run open first"
    }

    if (-not (Test-Path $LogFile -PathType Leaf)) {
        Fail "Timing log file is missing for ${PhaseId}: $LogFile"
    }

    Write-TimingEvent -LogFile $LogFile -SessionId (Get-SessionIdFromLogPath -LogPath $LogFile) -PhaseId $PhaseId -Action $Action -Source $Source -Persona $Persona -Outcome $Outcome -DurationMs $DurationMs -MetadataJson $MetadataJson
    return $LogFile
}

function Close-PhaseSession {
    param(
        [string]$PhaseId,
        [string]$Action,
        [string]$Source,
        [string]$Persona,
        [string]$Outcome,
        [string]$DurationMs,
        [string]$MetadataJson
    )

    $LogFile = Emit-PhaseEvent -PhaseId $PhaseId -Action $Action -Source $Source -Persona $Persona -Outcome $Outcome -DurationMs $DurationMs -MetadataJson $MetadataJson -LogFile ''
    Remove-Item -Force (Get-CurrentPointerPath -PhaseId $PhaseId)
    return $LogFile
}

function Get-OptionValue {
    param(
        [string[]]$Values,
        [ref]$Index
    )

    if (($Index.Value + 1) -ge $Values.Count) {
        Fail "Missing value for $($Values[$Index.Value])"
    }

    $Index.Value += 1
    return $Values[$Index.Value]
}

if ([string]::IsNullOrWhiteSpace($Command) -or $Command -in @('help', '--help', '-h')) {
    Show-Help
    exit 0
}

$PhaseId = ''
$Action = ''
$Source = 'runtime'
$Persona = ''
$Outcome = ''
$DurationMs = ''
$MetadataJson = ''
$CopilotSessionId = ''
$ModelId = ''
$Harness = ''
$InvocationSource = ''
$LogFile = ''
$DoReset = $false
$NoResolve = $false

for ($Index = 0; $Index -lt $Arguments.Count; $Index++) {
    switch ($Arguments[$Index]) {
        '--phase-id' { $PhaseId = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--action' { $Action = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--source' { $Source = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--persona' { $Persona = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--outcome' { $Outcome = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--duration-ms' { $DurationMs = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--metadata' { $MetadataJson = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--copilot-session-id' { $CopilotSessionId = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--model-id' { $ModelId = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--harness' { $Harness = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--invocation-source' {
            $InvocationSource = Get-OptionValue -Values $Arguments -Index ([ref]$Index)
            if ($InvocationSource -notin @('operator-command','operator-confirmation')) {
                Fail "--invocation-source must be operator-command or operator-confirmation (got: $InvocationSource)"
            }
        }
        '--log-file' { $LogFile = Get-OptionValue -Values $Arguments -Index ([ref]$Index) }
        '--reset' { $DoReset = $true }
        '--no-resolve' { $NoResolve = $true }
        '--help' { Show-Help; exit 0 }
        '-h' { Show-Help; exit 0 }
        default { Fail "Unknown option: $($Arguments[$Index])" }
    }
}

    $MetadataJson = Merge-MetadataJson -MetadataJson $MetadataJson -CopilotSessionId $CopilotSessionId
    $MetadataJson = Merge-MetadataField -MetadataJson $MetadataJson -Key 'model_id' -Value $ModelId
    $MetadataJson = Merge-MetadataField -MetadataJson $MetadataJson -Key 'harness' -Value $Harness
    $MetadataJson = Merge-MetadataField -MetadataJson $MetadataJson -Key 'invocation_source' -Value $InvocationSource

if (-not [string]::IsNullOrWhiteSpace($PhaseId)) {
    $TimingRoot = Get-TimingRootForPhase -PhaseId $PhaseId
    $ActiveRoot = Join-Path $TimingRoot 'current'
}

switch ($Command) {
    'open' {
        if ([string]::IsNullOrWhiteSpace($PhaseId)) { Fail 'open requires --phase-id' }

        $SessionIdSource = ''
        if (-not [string]::IsNullOrWhiteSpace($CopilotSessionId)) {
            $SessionIdSource = 'operator'
        }
        elseif (-not $NoResolve) {
            $ResolvedId = Resolve-CopilotSessionId
            if (-not [string]::IsNullOrWhiteSpace($ResolvedId)) {
                $MetadataJson = Merge-MetadataField -MetadataJson $MetadataJson -Key 'copilot_session_id' -Value $ResolvedId
                $SessionIdSource = 'resolver'
            }
            else {
                $SessionIdSource = 'unresolved'
            }
        }
        if (-not [string]::IsNullOrWhiteSpace($SessionIdSource)) {
            $MetadataJson = Merge-MetadataField -MetadataJson $MetadataJson -Key 'copilot_session_id_source' -Value $SessionIdSource
        }

        $SessionMarker = New-SessionMarker
        $MetadataJson = Merge-MetadataField -MetadataJson $MetadataJson -Key 'session_marker' -Value $SessionMarker
        # Echoed so the harness transcript captures it (deterministic join);
        # stderr keeps stdout as the log-file-path contract.
        [Console]::Error.WriteLine("CPB-SESSION-MARKER: $SessionMarker")

        Open-PhaseSession -PhaseId $PhaseId -Source $Source -Persona $Persona -Outcome $Outcome -MetadataJson $MetadataJson -Reset:$DoReset
        break
    }
    'emit' {
        if ([string]::IsNullOrWhiteSpace($PhaseId)) { Fail 'emit requires --phase-id' }
        if ([string]::IsNullOrWhiteSpace($Action)) { Fail 'emit requires --action' }
        Emit-PhaseEvent -PhaseId $PhaseId -Action $Action -Source $Source -Persona $Persona -Outcome $Outcome -DurationMs $DurationMs -MetadataJson $MetadataJson -LogFile $LogFile
        break
    }
    'close' {
        if ([string]::IsNullOrWhiteSpace($PhaseId)) { Fail 'close requires --phase-id' }
        if ([string]::IsNullOrWhiteSpace($Action)) { $Action = 'phase-session-completed' }
        Close-PhaseSession -PhaseId $PhaseId -Action $Action -Source $Source -Persona $Persona -Outcome $Outcome -DurationMs $DurationMs -MetadataJson $MetadataJson
        break
    }
    'reset' {
        if ([string]::IsNullOrWhiteSpace($PhaseId)) { Fail 'reset requires --phase-id' }
        Open-PhaseSession -PhaseId $PhaseId -Source $Source -Persona $Persona -Outcome $Outcome -MetadataJson $MetadataJson -Reset
        break
    }
    'status' {
        if ([string]::IsNullOrWhiteSpace($PhaseId)) { Fail 'status requires --phase-id' }
        $ActiveLogPath = Get-ActiveLogPath -PhaseId $PhaseId
        if ([string]::IsNullOrWhiteSpace($ActiveLogPath)) { Fail "No active timing session for $PhaseId" }
        if (-not (Test-Path $ActiveLogPath -PathType Leaf)) { Fail "Timing log file is missing for ${PhaseId}: $ActiveLogPath" }
        $ActiveLogPath
        break
    }
    default {
        Show-Help
        Fail "Unknown command: $Command"
    }
}