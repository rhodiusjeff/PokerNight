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
$SanityRoot = Join-Path $ProjectRoot "$CpRootName/state/sanity"
$ReportsRoot = Join-Path $SanityRoot 'reports'
$ReadmeTemplate = ''  # template staging retired in shape v1; README seeding is a no-op
$RuntimeVersion = 'cpb-sanity-runtime-v1'

function Show-Help {
    Write-Host 'Usage:'
    Write-Host '  control-plane-sanity.ps1 run --operation <operation> [options]'
    Write-Host '  control-plane-sanity.ps1 help'
    Write-Host ''
    Write-Host 'Options for run:'
    Write-Host '  --operation <name>    Operation under test: operational (legacy alias: steady-state), migrate, upgrade, or new-horizon.'
    Write-Host '  --repo-label <value>  Optional repo identity label written into the report.'
    Write-Host '  --smoke-spec <path>   Optional JSON file declaring project-local smoke commands.'
    Write-Host '  --report-stem <path>  Optional report path without extension.'
}

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Ensure-SanitySurface {
    New-Item -ItemType Directory -Path $ReportsRoot -Force | Out-Null
    $ReadmePath = Join-Path $SanityRoot 'README.md'
    if ($ReadmeTemplate -and (Test-Path $ReadmeTemplate -PathType Leaf) -and -not (Test-Path $ReadmePath -PathType Leaf)) {
        Copy-Item -Path $ReadmeTemplate -Destination $ReadmePath
    }
}

function Add-ControlResult {
    param(
        [System.Collections.ArrayList]$Results,
        [string]$Category,
        [string]$Status,
        [string]$Summary,
        [string]$Evidence
    )

    [void]$Results.Add([ordered]@{
        category = $Category
        status = $Status
        summary = $Summary
        evidence = $Evidence
    })
}

function Add-SmokeResult {
    param(
        [System.Collections.ArrayList]$Results,
        [string]$Id,
        [string]$Status,
        [string]$Summary,
        [string]$CommandText,
        [int]$ExitCode
    )

    [void]$Results.Add([ordered]@{
        id = $Id
        status = $Status
        summary = $Summary
        command = $CommandText
        exit_code = $ExitCode
    })
}

# LOCAL ADDITION (v3 conversion, 2026-07-21) - HARVEST TO CPB: one shared tracker validator
# is the executable authority for both Bash and PowerShell sanity.
function Test-HorizonTrackersV3 {
    param([System.Collections.ArrayList]$Results)
    $Validator = Join-Path $ProjectRoot "$CpRootName/framework/scripts/validate-horizon-trackers.py"
    $Output = @(& python3 $Validator --root $ProjectRoot 2>&1)
    $ExitCode = $LASTEXITCODE
    if ($ExitCode -eq 0) {
        Add-ControlResult -Results $Results -Category 'horizon-tracker-v3' -Status 'pass' -Summary 'Horizon tracker/archive v3 contracts, graph topology, and cross-file invariants pass through the shared validator.' -Evidence 'validate-horizon-trackers.py + horizons/*/TRACKER.json'
    }
    else {
        Add-ControlResult -Results $Results -Category 'horizon-tracker-v3' -Status 'fail' -Summary "Horizon tracker validation failures: $($Output -join '; ')" -Evidence 'validate-horizon-trackers.py + horizons/*/TRACKER.json'
    }
}

function Test-HorizonPackets {
    param([System.Collections.ArrayList]$Results)
    $Validator = Join-Path $ProjectRoot "$CpRootName/framework/scripts/validate-horizon-packets.py"
    $Output = @(& python3 $Validator --root $ProjectRoot --allow-lightweight H000 2>&1)
    $ExitCode = $LASTEXITCODE
    if ($ExitCode -eq 0) {
        Add-ControlResult -Results $Results -Category 'horizon-packets' -Status 'pass' -Summary 'Horizon packet state, folder identity, and local tag reconciliation pass (legacy H000 lightweight-tag exception active).' -Evidence 'validate-horizon-packets.py + horizons/*/HORIZON_STATE.json'
    }
    else {
        Add-ControlResult -Results $Results -Category 'horizon-packets' -Status 'fail' -Summary "Horizon packet validation failures: $($Output -join '; ')" -Evidence 'validate-horizon-packets.py + horizons/*/HORIZON_STATE.json'
    }
}

function Test-RegistersAndInstanceState {
    param([System.Collections.ArrayList]$Results)
    $Validator = Join-Path $ProjectRoot "$CpRootName/framework/scripts/validate-registers-and-state.py"
    $Output = @(& python3 $Validator --root $ProjectRoot 2>&1)
    $ExitCode = $LASTEXITCODE
    if ($ExitCode -eq 0) {
        Add-ControlResult -Results $Results -Category 'registers-and-instance-state' -Status 'pass' -Summary 'Register catalog contracts and instance state pass.' -Evidence 'validate-registers-and-state.py + state/*.json'
    }
    else {
        Add-ControlResult -Results $Results -Category 'registers-and-instance-state' -Status 'fail' -Summary "Register or instance-state validation failures: $($Output -join '; ')" -Evidence 'validate-registers-and-state.py + state/*.json'
    }
}

# LOCAL ADDITION (2026-07-29) - HARVEST TO CPB: CI profile contract gate.
function Test-CiProfileCatalog {
    param([System.Collections.ArrayList]$Results)
    $Catalog = Join-Path $ProjectRoot "$CpRootName/canon/standards/CI_PROFILE_CATALOG.json"
    $Validator = Join-Path $ProjectRoot "$CpRootName/framework/scripts/validate-ci-profile.py"
    if (-not (Test-Path $Catalog -PathType Leaf)) {
        Add-ControlResult -Results $Results -Category 'ci-profile-catalog' -Status 'skip' -Summary 'No project CI profile catalog is installed.' -Evidence 'canon/standards/CI_PROFILE_CATALOG.json'
        return
    }
    $Output = @(& python3 $Validator $Catalog 2>&1)
    $ExitCode = $LASTEXITCODE
    if ($ExitCode -eq 0) {
        Add-ControlResult -Results $Results -Category 'ci-profile-catalog' -Status 'pass' -Summary 'Project CI profile catalog satisfies the deterministic contract.' -Evidence 'validate-ci-profile.py + canon/standards/CI_PROFILE_CATALOG.json'
    }
    else {
        Add-ControlResult -Results $Results -Category 'ci-profile-catalog' -Status 'fail' -Summary "CI profile validation failures: $($Output -join '; ')" -Evidence 'validate-ci-profile.py + canon/standards/CI_PROFILE_CATALOG.json'
    }
}

function Test-CiCustomizations {
    param([System.Collections.ArrayList]$Results)
    $Validator = Join-Path $ProjectRoot "$CpRootName/framework/scripts/validate-ci-customizations.py"
    $Output = @(& python3 $Validator --root $ProjectRoot 2>&1)
    $ExitCode = $LASTEXITCODE
    if ($ExitCode -eq 0) {
        Add-ControlResult -Results $Results -Category 'ci-customizations' -Status 'pass' -Summary 'CI persona, prompt help/bindings, timing vocabulary, approval boundaries, and Claude adapters are coherent.' -Evidence 'validate-ci-customizations.py'
    }
    else {
        Add-ControlResult -Results $Results -Category 'ci-customizations' -Status 'fail' -Summary "CI customization failures: $($Output -join '; ')" -Evidence 'validate-ci-customizations.py'
    }
}

function Test-HorizonLifecycleCustomizations {
    param([System.Collections.ArrayList]$Results)
    $Validator = Join-Path $ProjectRoot "$CpRootName/framework/scripts/validate-horizon-lifecycle.py"
    $Output = @(& python3 $Validator --root $ProjectRoot 2>&1)
    $ExitCode = $LASTEXITCODE
    if ($ExitCode -eq 0) {
        Add-ControlResult -Results $Results -Category 'horizon-lifecycle-v1' -Status 'pass' -Summary 'Horizon shaping/admission prompts, schemas, timing, manuals, adapters, and branch policy are coherent.' -Evidence 'validate-horizon-lifecycle.py'
    }
    else {
        Add-ControlResult -Results $Results -Category 'horizon-lifecycle-v1' -Status 'fail' -Summary "Horizon lifecycle failures: $($Output -join '; ')" -Evidence 'validate-horizon-lifecycle.py'
    }
}

# LOCAL MOD (2026-07-21) - HARVEST TO CPB: dual-harness parity for the completion-evidence gate.
function Test-CompletionEvidence {
    param([System.Collections.ArrayList]$Results)
    $Problems = @()
    foreach ($Tj in (Get-ChildItem -Path (Join-Path $ProjectRoot "$CpRootName/horizons") -Filter 'TRACKER.json' -Recurse -ErrorAction SilentlyContinue)) {
        $Pkt = $Tj.Directory
        $Led = Join-Path $Pkt.FullName 'ledgers/REVIEW_UNIT_LEDGER.json'
        if (-not (Test-Path $Led)) { continue }
        try { $Ledger = Get-Content -Path $Led -Raw | ConvertFrom-Json } catch { $Problems += "$Led : unparseable"; continue }
        $Rows = @{}; foreach ($R in @($Ledger.entries)) { $Rows[$R.review_unit_id] = $R }
        $Nodes = @()
        try { $Nodes += @((Get-Content -Path $Tj.FullName -Raw | ConvertFrom-Json).nodes) } catch { $Problems += "$($Tj.FullName): unparseable" }
        $Arch = Join-Path $Pkt.FullName 'TRACKER_ARCHIVE.json'
        if (Test-Path $Arch) { try { $Nodes += @((Get-Content -Path $Arch -Raw | ConvertFrom-Json).rolled_nodes) } catch { $Problems += "$Arch : unparseable" } }
        foreach ($N in $Nodes) {
            if ($N.status -ne 'done') { continue }
            $Ru = $N.review_unit
            if (-not $Ru -and $N.section -eq 'historical-legacy') { continue }
            if (-not $Ru) { $Problems += "$($Pkt.Name): $($N.id) is done with no review_unit declared"; continue }
            if ($Ru -like '*:*') { $Boundary, $Uid = $Ru -split ':', 2 } else { $Boundary = 'self'; $Uid = $Ru }
            if (-not $Rows.ContainsKey($Uid)) { $Problems += "$($Pkt.Name): $($N.id) review_unit '$Ru' has no ledger entry"; continue }
            $Row = $Rows[$Uid]
            if ($Row.boundary_type -ne $Boundary) { $Problems += "$($Pkt.Name): $($N.id) declares boundary '$Boundary' but ledger says '$($Row.boundary_type)'" }
            $Members = @(([string]$Row.phase_ids) -split ',' | ForEach-Object { $_.Trim().Trim('`') })
            if ($Members -notcontains $N.id) { $Problems += "$($Pkt.Name): $($N.id) not listed in ledger unit $Uid phase_ids" }
            if ($Boundary -eq 'none-by-policy') {
                if ($Row.status -ne 'Waived') { $Problems += "$($Pkt.Name): $($N.id) none-by-policy but ledger status '$($Row.status)' != Waived" }
            } elseif ($Row.status -eq 'Superseded') {
            } elseif ($Row.status -ne 'Merged') {
                $Problems += "$($Pkt.Name): $($N.id) is done but ledger unit $Uid status is '$($Row.status)' (expected Merged)"
            } elseif (-not $Row.merge_commit_sha) {
                $Problems += "$($Pkt.Name): $($N.id) ledger unit $Uid is Merged with no merge_commit_sha"
            }
        }
        $Known = @($Nodes | ForEach-Object { $_.id })
        foreach ($Uid in $Rows.Keys) {
            foreach ($M in @(([string]$Rows[$Uid].phase_ids) -split ',' | ForEach-Object { $_.Trim().Trim('`') })) {
                if ($M -and ($Known -notcontains $M)) { $Problems += "$($Pkt.Name): ledger unit $Uid lists unknown phase '$M'" }
            }
        }
    }
    if ($Problems.Count -eq 0) {
        Add-ControlResult -Results $Results -Category 'completion-evidence' -Status 'pass' -Summary 'Every done node resolves through its review_unit to merged-review (or waived) ledger evidence; all ledger members resolve to real nodes.' -Evidence 'TRACKER.json + TRACKER_ARCHIVE.json vs REVIEW_UNIT_LEDGER.json'
    } else {
        Add-ControlResult -Results $Results -Category 'completion-evidence' -Status 'fail' -Summary "Completion-evidence failures: $($Problems -join '; ')" -Evidence 'TRACKER.json + TRACKER_ARCHIVE.json vs REVIEW_UNIT_LEDGER.json'
    }
}

function Test-RequiredPaths {
    param([string[]]$Paths)
    $Missing = @()
    foreach ($Path in $Paths) {
        if (-not (Test-Path $Path -PathType Leaf)) {
            $Missing += $Path.Substring($ProjectRoot.Length + 1)
        }
    }
    return $Missing
}

function Get-LifecycleMode {
    $LifecyclePath = Join-Path $ProjectRoot 'control-plane/state/CONTROL_PLANE_STATE.json'
    if (-not (Test-Path $LifecyclePath -PathType Leaf)) {
        return 'missing'
    }
    try {
        $StateObj = Get-Content -Path $LifecyclePath -Raw | ConvertFrom-Json
        if ($StateObj.state) { return [string]$StateObj.state }
        return 'missing'
    } catch { return 'unreadable' }
}

function Invoke-SmokeCommands {
    param(
        [string]$SmokeSpecPath,
        [System.Collections.ArrayList]$SmokeResults,
        [System.Collections.ArrayList]$ResidualBlockers
    )

    if ([string]::IsNullOrWhiteSpace($SmokeSpecPath) -or -not (Test-Path $SmokeSpecPath -PathType Leaf)) {
        Add-SmokeResult -Results $SmokeResults -Id 'no-smoke-spec' -Status 'skip' -Summary 'No project-local smoke spec was declared for this run.' -CommandText '' -ExitCode 0
        return $false
    }

    $SmokeData = Get-Content -Path $SmokeSpecPath -Raw | ConvertFrom-Json
    if ($null -eq $SmokeData.commands -or $SmokeData.commands.Count -eq 0) {
        Add-SmokeResult -Results $SmokeResults -Id 'empty-smoke-spec' -Status 'skip' -Summary 'Smoke spec exists but declares no commands.' -CommandText $SmokeSpecPath -ExitCode 0
        return $false
    }

    $SmokeFailure = $false
    foreach ($Item in $SmokeData.commands) {
        $ExpectedExit = if ($null -eq $Item.expected_exit) { 0 } else { [int]$Item.expected_exit }
        $CommandText = [string]$Item.command
        $ActualExit = 0
        try {
            Push-Location $ProjectRoot
            pwsh -NoProfile -Command $CommandText *> $null
            $ActualExit = 0
        }
        catch {
            $ActualExit = 1
        }
        finally {
            Pop-Location
        }

        if ($ActualExit -eq $ExpectedExit) {
            Add-SmokeResult -Results $SmokeResults -Id ([string]$Item.id) -Status 'pass' -Summary ([string]$Item.description) -CommandText $CommandText -ExitCode $ActualExit
        }
        else {
            Add-SmokeResult -Results $SmokeResults -Id ([string]$Item.id) -Status 'fail' -Summary "Expected exit $ExpectedExit but got $ActualExit" -CommandText $CommandText -ExitCode $ActualExit
            [void]$ResidualBlockers.Add("smoke:$($Item.id): Expected exit $ExpectedExit but got $ActualExit")
            $SmokeFailure = $true
        }
    }

    return $SmokeFailure
}

if ([string]::IsNullOrWhiteSpace($Command) -or $Command -in @('help', '--help', '-h')) {
    Show-Help
    exit 0
}

$Operation = ''
$RepoLabel = ''
$SmokeSpec = ''
$ReportStem = ''

for ($Index = 0; $Index -lt $Arguments.Count; $Index++) {
    switch ($Arguments[$Index]) {
        '--operation' { $Index += 1; $Operation = $Arguments[$Index] }
        '--repo-label' { $Index += 1; $RepoLabel = $Arguments[$Index] }
        '--smoke-spec' { $Index += 1; $SmokeSpec = $Arguments[$Index] }
        '--report-stem' { $Index += 1; $ReportStem = $Arguments[$Index] }
        '--help' { Show-Help; exit 0 }
        '-h' { Show-Help; exit 0 }
        default { Fail "Unknown option: $($Arguments[$Index])" }
    }
}

if ($Command -ne 'run') {
    Fail "Unknown command: $Command"
}

if ([string]::IsNullOrWhiteSpace($Operation)) {
    Fail 'run requires --operation'
}

Ensure-SanitySurface

if ([string]::IsNullOrWhiteSpace($RepoLabel)) {
    $RepoLabel = Split-Path -Leaf $ProjectRoot
}

if ([string]::IsNullOrWhiteSpace($ReportStem)) {
    $Stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $SafeOperation = (($Operation -replace '/', '_') -replace ' ', '_')
    $ReportStem = Join-Path $ReportsRoot "$Stamp`__$SafeOperation"
}

$ControlResults = [System.Collections.ArrayList]::new()
$SmokeResults = [System.Collections.ArrayList]::new()
$ResidualBlockers = [System.Collections.ArrayList]::new()
$ControlFailure = $false

$RequiredPaths = @(
    (Join-Path $ProjectRoot 'control-plane/README.md'),
    (Join-Path $ProjectRoot 'control-plane/canon/context/CONTEXT_HANDOFF.md'),
    (Join-Path $ProjectRoot 'control-plane/framework/docs/control-system-user-guide.md'),
    (Join-Path $ProjectRoot 'control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json'),
    (Join-Path $ProjectRoot 'control-plane/canon/context/PROJECT_ARCHITECTURE_OVERVIEW.md'),
    (Join-Path $ProjectRoot 'control-plane/framework/governance/codegen-handoff.spec.md'),
    (Join-Path $ProjectRoot 'control-plane/state/CONTROL_PLANE_STATE.json'),
    (Join-Path $ProjectRoot 'cp-ops-work/OPS_WORK_STATE.json'),
    (Join-Path $ProjectRoot 'cp-ops-work/TRACKER.json'),
    (Join-Path $ProjectRoot 'control-plane/canon/context/ACCEPTANCE_TEST_MATRIX.json'),
    (Join-Path $ProjectRoot 'control-plane/framework/governance/review/contract-verify.spec.md'),
    (Join-Path $ProjectRoot 'control-plane/framework/governance/timing/timing-log.spec.md')
)

Test-HorizonPackets -Results $ControlResults
Test-HorizonTrackersV3 -Results $ControlResults
Test-RegistersAndInstanceState -Results $ControlResults
Test-CiProfileCatalog -Results $ControlResults
Test-CiCustomizations -Results $ControlResults
Test-HorizonLifecycleCustomizations -Results $ControlResults
Test-CompletionEvidence -Results $ControlResults
$MissingDocs = Test-RequiredPaths -Paths $RequiredPaths
if ($MissingDocs.Count -eq 0) {
    Add-ControlResult -Results $ControlResults -Category 'required-governance-surfaces' -Status 'pass' -Summary 'Required governance docs are present.' -Evidence 'control-plane core set'
}
else {
    Add-ControlResult -Results $ControlResults -Category 'required-governance-surfaces' -Status 'fail' -Summary "Missing required governance docs: $($MissingDocs -join ', ')" -Evidence 'control-plane core set'
    [void]$ResidualBlockers.Add("required-governance-surfaces: Missing required governance docs: $($MissingDocs -join ', ')")
    $ControlFailure = $true
}

if ((Test-Path (Join-Path $ProjectRoot '.github/prompts') -PathType Container) -and (Test-Path (Join-Path $ProjectRoot '.github/agents') -PathType Container)) {
    Add-ControlResult -Results $ControlResults -Category 'active-github-surface' -Status 'pass' -Summary 'Active .github prompt and agent surfaces are present.' -Evidence '.github/agents + .github/prompts'
}
else {
    Add-ControlResult -Results $ControlResults -Category 'active-github-surface' -Status 'fail' -Summary 'Active .github surface is missing prompts or agents.' -Evidence '.github runtime surface'
    [void]$ResidualBlockers.Add('active-github-surface: Active .github surface is missing prompts or agents.')
    $ControlFailure = $true
}

$Mode = Get-LifecycleMode
switch ($Operation) {
    'operational' {
        if ($Mode -eq 'missing' -or $Mode -eq 'steady-state' -or $Mode -eq 'operational') {
            Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'pass' -Summary 'Lifecycle state is compatible with operational execution.' -Evidence 'lifecycle/CONTROL_PLANE_STATE.json'
        }
        else {
            Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'fail' -Summary "Expected operational instance state but found: $Mode" -Evidence 'lifecycle/CONTROL_PLANE_STATE.json'
            [void]$ResidualBlockers.Add("lifecycle-packet-and-mode: Expected operational instance state but found: $Mode")
            $ControlFailure = $true
        }
    }
    'steady-state' {
        if ($Mode -eq 'missing' -or $Mode -eq 'steady-state' -or $Mode -eq 'operational') {
            Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'pass' -Summary 'Lifecycle state is compatible with steady-state execution.' -Evidence 'lifecycle/CONTROL_PLANE_STATE.json'
        }
        else {
            Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'fail' -Summary "Expected steady-state lifecycle mode but found: $Mode" -Evidence 'lifecycle/CONTROL_PLANE_STATE.json'
            [void]$ResidualBlockers.Add("lifecycle-packet-and-mode: Expected steady-state lifecycle mode but found: $Mode")
            $ControlFailure = $true
        }
    }
    'migrate' {
        if ((Test-Path (Join-Path $ProjectRoot 'control-plane/archive/migration-closeout-2026-06/MIGRATION_STATUS.md') -PathType Leaf) -and $Mode -eq 'migration') {
            Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'pass' -Summary 'Migration packet and lifecycle mode are aligned.' -Evidence 'migration/MIGRATION_STATUS.md + lifecycle/CONTROL_PLANE_STATE.json'
        }
        else {
            Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'fail' -Summary 'Migration operation requires control-plane/archive/migration-closeout-2026-06/MIGRATION_STATUS.md and Mode: migration.' -Evidence 'migration packet alignment'
            [void]$ResidualBlockers.Add('lifecycle-packet-and-mode: Migration operation requires control-plane/archive/migration-closeout-2026-06/MIGRATION_STATUS.md and Mode: migration.')
            $ControlFailure = $true
        }
    }
    'upgrade' {
        if ((Test-Path (Join-Path $ProjectRoot 'control-plane/archive/upgrade-0.4.x/UPGRADE_STATUS.md') -PathType Leaf) -and ($Mode -eq 'upgrading' -or $Mode -eq 'upgrade')) {
            Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'pass' -Summary 'Upgrade packet and lifecycle mode are aligned.' -Evidence 'upgrade/UPGRADE_STATUS.md + lifecycle/CONTROL_PLANE_STATE.json'
        }
        else {
            Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'fail' -Summary 'Upgrade operation requires control-plane/archive/upgrade-0.4.x/UPGRADE_STATUS.md and Mode: upgrade.' -Evidence 'upgrade packet alignment'
            [void]$ResidualBlockers.Add('lifecycle-packet-and-mode: Upgrade operation requires control-plane/archive/upgrade-0.4.x/UPGRADE_STATUS.md and Mode: upgrade.')
            $ControlFailure = $true
        }
    }
    'new-horizon' {
        if ((Test-Path (Join-Path $ProjectRoot 'control-plane/horizons/README.md') -PathType Leaf) -and $Mode -eq 'operational') {
            Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'pass' -Summary 'Horizon packet root and operational instance state are aligned.' -Evidence 'horizons/README.md + state/CONTROL_PLANE_STATE.json'
        }
        else {
            Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'fail' -Summary 'New-horizon operation requires the horizons packet root and operational instance state.' -Evidence 'horizon packet alignment'
            [void]$ResidualBlockers.Add('lifecycle-packet-and-mode: New-horizon operation requires the horizons packet root and operational instance state.')
            $ControlFailure = $true
        }
    }
    default {
        Add-ControlResult -Results $ControlResults -Category 'lifecycle-packet-and-mode' -Status 'fail' -Summary "Unknown operation: $Operation" -Evidence 'runtime invocation'
        [void]$ResidualBlockers.Add("lifecycle-packet-and-mode: Unknown operation: $Operation")
        $ControlFailure = $true
    }
}

$TrackerCount = @(Get-ChildItem -Path (Join-Path $ProjectRoot "$CpRootName/horizons") -Filter 'TRACKER.json' -Recurse -File -ErrorAction SilentlyContinue).Count
if ($TrackerCount -gt 0 -and (Test-Path (Join-Path $ProjectRoot 'control-plane/canon/context/ACCEPTANCE_TEST_MATRIX.json') -PathType Leaf) -and (Test-Path (Join-Path $ProjectRoot 'control-plane/framework/governance/review/contract-verify.spec.md') -PathType Leaf) -and (Test-Path (Join-Path $ProjectRoot 'control-plane/framework/governance/closeout/prompt-closeout-report.template.md') -PathType Leaf)) {
    Add-ControlResult -Results $ControlResults -Category 'tracker-acceptance-closeout-contract' -Status 'pass' -Summary 'Tracker, acceptance, contract-verify, and closeout surfaces are present.' -Evidence 'tracker + acceptance + contract verify + closeout template'
}
else {
    Add-ControlResult -Results $ControlResults -Category 'tracker-acceptance-closeout-contract' -Status 'fail' -Summary 'Tracker, acceptance, contract verify, or closeout template surface is missing.' -Evidence 'tracker/acceptance/closeout contract'
    [void]$ResidualBlockers.Add('tracker-acceptance-closeout-contract: Tracker, acceptance, contract verify, or closeout template surface is missing.')
    $ControlFailure = $true
}

$RuntimeHelpers = @(
    (Join-Path $ProjectRoot "$CpRootName/framework/scripts/timing-log.sh"),
    (Join-Path $ProjectRoot "$CpRootName/framework/scripts/timing-log.ps1"),
    (Join-Path $ProjectRoot "$CpRootName/framework/scripts/control-plane-sanity.sh"),
    (Join-Path $ProjectRoot "$CpRootName/framework/scripts/control-plane-sanity.ps1"),
    (Join-Path $ProjectRoot "$CpRootName/framework/scripts/validate-ci-profile.py"),
    (Join-Path $ProjectRoot "$CpRootName/framework/scripts/validate-ci-customizations.py"),
    (Join-Path $ProjectRoot "$CpRootName/framework/scripts/verify-forge-readiness.py"),
    (Join-Path $ProjectRoot "$CpRootName/framework/scripts/ci-repo-inventory.py"),
    (Join-Path $ProjectRoot "$CpRootName/framework/scripts/horizon-branch.py"),
    (Join-Path $ProjectRoot "$CpRootName/framework/scripts/validate-horizon-lifecycle.py")
)
$MissingHelpers = Test-RequiredPaths -Paths $RuntimeHelpers
if ($MissingHelpers.Count -eq 0) {
    Add-ControlResult -Results $ControlResults -Category 'runtime-helpers-installed' -Status 'pass' -Summary 'Timing, sanity, and CI runtime helpers are installed.' -Evidence 'control-plane/framework/scripts/'
}
else {
    Add-ControlResult -Results $ControlResults -Category 'runtime-helpers-installed' -Status 'fail' -Summary "Missing runtime helpers: $($MissingHelpers -join ', ')" -Evidence 'control-plane/framework/scripts/'
    [void]$ResidualBlockers.Add("runtime-helpers-installed: Missing runtime helpers: $($MissingHelpers -join ', ')")
    $ControlFailure = $true
}

$SmokeFailure = Invoke-SmokeCommands -SmokeSpecPath $SmokeSpec -SmokeResults $SmokeResults -ResidualBlockers $ResidualBlockers

foreach ($Item in $ControlResults) {
    if ($Item.status -eq 'fail') {
        $ControlFailure = $true
        $Blocker = "$($Item.category): $($Item.summary)"
        if ($ResidualBlockers -notcontains $Blocker) {
            [void]$ResidualBlockers.Add($Blocker)
        }
    }
}

$OverallDisposition = if ($ControlFailure -and $SmokeFailure) { 'mixed' } elseif ($ControlFailure) { 'control-plane-failed' } elseif ($SmokeFailure) { 'smoke-failed' } else { 'pass' }
$Timestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')

$Report = [ordered]@{
    runtime_version = $RuntimeVersion
    timestamp = $Timestamp
    operation = $Operation
    repo_identity = [ordered]@{
        label = $RepoLabel
        path = $ProjectRoot
    }
    control_plane_results = $ControlResults
    smoke_results = $SmokeResults
    overall_disposition = $OverallDisposition
    residual_blockers = $ResidualBlockers
}

$JsonPath = "$ReportStem.json"
$MarkdownPath = "$ReportStem.md"
$Report | ConvertTo-Json -Depth 8 -Compress | Set-Content -Path $JsonPath

$MarkdownLines = @(
    '# Control-Plane Sanity Report',
    '',
    "- Operation: $Operation",
    "- Repo label: $RepoLabel",
    "- Runtime version: $RuntimeVersion",
    "- Timestamp: $Timestamp",
    "- Overall disposition: $OverallDisposition",
    '',
    '## Control-Plane Results'
)

foreach ($Item in $ControlResults) {
    $MarkdownLines += "- $($Item | ConvertTo-Json -Compress -Depth 6)"
}

$MarkdownLines += ''
$MarkdownLines += '## Smoke Results'
foreach ($Item in $SmokeResults) {
    $MarkdownLines += "- $($Item | ConvertTo-Json -Compress -Depth 6)"
}

$MarkdownLines += ''
$MarkdownLines += '## Residual Blockers'
if ($ResidualBlockers.Count -eq 0) {
    $MarkdownLines += '- none'
}
else {
    foreach ($Item in $ResidualBlockers) {
        $MarkdownLines += "- $Item"
    }
}

$MarkdownLines | Set-Content -Path $MarkdownPath
Write-Output $JsonPath
if ($OverallDisposition -ne 'pass') { exit 1 }