param(
    [Parameter(Position = 0, Mandatory = $false)]
    [string]$Command = 'help',

    [Parameter(Mandatory = $false, ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$ErrorActionPreference = 'Stop'

# LOCAL ADDITION (2026-07-21) - HARVEST TO CPB: PowerShell parity for the forge-agnostic
# atomic horizon ID mint. Every native Git exit code is inspected explicitly.

function Show-Help {
    @'
Usage:
    horizon-mint.ps1 mint [--remote <name>] [--target-ref <ref>] [--max-attempts <count>]
  horizon-mint.ps1 abandon <HNNN> --reason <text> [--remote <name>]
  horizon-mint.ps1 help

Commands:
  mint       Reserve the next production horizon ID with an annotated horizon/HNNN tag.
  abandon    Record an abandoned reservation with horizon/HNNN-abandoned. The original
             reservation remains immutable and the ID is never reused.
  help       Show this help text.

Rules:
  - Production IDs are H000-H899. H900-H999 are reserved for protection probes.
  - The script fetches horizon tags before allocation and retries boundedly on a real race.
  - Every push names exactly one ref. `git push --tags` and forced remote updates are forbidden.
  - Tag messages contain immutable mint facts only; slug, owner, and environment belong in the
    horizon packet.

Output:
  On success, stdout contains only the reserved or abandoned horizon ID. Diagnostics go to
  stderr, so callers may safely capture the result.

Examples:
  horizon-mint.ps1 mint
    horizon-mint.ps1 mint --remote upstream --target-ref refs/remotes/upstream/integration --max-attempts 5
  horizon-mint.ps1 abandon H004 --reason "Planning cycle cancelled before packet declaration"
'@ | Write-Output
}

function Fail {
    param([string]$Message)
    [Console]::Error.WriteLine("Error: $Message")
    exit 1
}

function Require-Value {
    param([string]$Option, [string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value) -or $Value.StartsWith('--')) {
        Fail "$Option requires a value"
    }
}

function Invoke-GitCapture {
    param([string[]]$GitArgs)
    $Output = @(& git @GitArgs 2>$null)
    [pscustomobject]@{ ExitCode = $LASTEXITCODE; Output = ($Output -join "`n").Trim() }
}

function Get-RepoRoot {
    $Result = Invoke-GitCapture @('rev-parse', '--show-toplevel')
    if ($Result.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($Result.Output)) {
        Fail 'run this command inside a Git working tree'
    }
    return $Result.Output
}

function Get-GitIdentity {
    param([string]$Root)
    $Name = Invoke-GitCapture @('-C', $Root, 'config', 'user.name')
    $Email = Invoke-GitCapture @('-C', $Root, 'config', 'user.email')
    if ($Name.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($Name.Output)) {
        Fail 'git user.name is not configured'
    }
    if ($Email.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($Email.Output)) {
        Fail 'git user.email is not configured'
    }
    return "$($Name.Output) <$($Email.Output)>"
}

function Assert-Remote {
    param([string]$Root, [string]$Remote)
    $Result = Invoke-GitCapture @('-C', $Root, 'remote', 'get-url', $Remote)
    if ($Result.ExitCode -ne 0) { Fail "Git remote '$Remote' does not exist" }
}

function Fetch-HorizonTags {
    param([string]$Root, [string]$Remote)
    & git -C $Root fetch --quiet --no-tags $Remote 'refs/tags/horizon/*:refs/tags/horizon/*'
    if ($LASTEXITCODE -ne 0) { Fail "cannot fetch horizon tags from remote '$Remote'" }
}

function Get-NextHorizonId {
    param([string]$Root, [string]$Remote)
    $Result = Invoke-GitCapture @('-C', $Root, 'ls-remote', '--tags', '--refs', $Remote, 'refs/tags/horizon/H???')
    if ($Result.ExitCode -ne 0) { Fail "cannot enumerate horizon tags on remote '$Remote'" }
    $Max = -1
    foreach ($Line in @($Result.Output -split "`n")) {
        if ($Line -match 'refs/tags/horizon/H([0-9]{3})$') {
            $Value = [int]$Matches[1]
            if ($Value -le 899 -and $Value -gt $Max) { $Max = $Value }
        }
    }
    if ($Max -ge 899) { Fail 'production horizon ID space H000-H899 is exhausted' }
    return ('H{0:D3}' -f ($Max + 1))
}

function Test-RemoteRef {
    param([string]$Root, [string]$Remote, [string]$Ref)
    & git -C $Root ls-remote --exit-code --refs $Remote $Ref *> $null
    return $LASTEXITCODE -eq 0
}

function Remove-LocalProposal {
    param([string]$Root, [string]$Tag)
    & git -C $Root tag --delete $Tag *> $null
}

function New-MintMessage {
    param([string]$Horizon, [string]$Identity, [string]$MintedAt)
    return @"
cpb-horizon-mint-v1
horizon: $Horizon
minter: $Identity
minted-at: $MintedAt
reserved-ref: refs/tags/horizon/$Horizon
"@.TrimEnd()
}

function New-AbandonmentMessage {
    param([string]$Horizon, [string]$Identity, [string]$AbandonedAt, [string]$Reason)
    return @"
cpb-horizon-abandonment-v1
horizon: $Horizon
recorded-by: $Identity
abandoned-at: $AbandonedAt
reserved-ref: refs/tags/horizon/$Horizon
reason: $Reason
"@.TrimEnd()
}

function Invoke-Mint {
    param([string]$Remote, [int]$MaxAttempts, [string]$TargetRef)
    $Root = Get-RepoRoot
    Assert-Remote $Root $Remote
    $Identity = Get-GitIdentity $Root
    $Target = Invoke-GitCapture @('-C', $Root, 'rev-parse', $TargetRef)
    if ($Target.ExitCode -ne 0) { Fail "target ref '$TargetRef' does not resolve" }

    for ($Attempt = 1; $Attempt -le $MaxAttempts; $Attempt++) {
        Fetch-HorizonTags $Root $Remote
        $Horizon = Get-NextHorizonId $Root $Remote
        $Tag = "horizon/$Horizon"
        $Ref = "refs/tags/$Tag"
        $MintedAt = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        $Message = New-MintMessage $Horizon $Identity $MintedAt

        & git -C $Root tag -a $Tag -m $Message $Target.Output
        if ($LASTEXITCODE -ne 0) { Fail "cannot create local annotated proposal $Tag" }

        & git -C $Root push --quiet $Remote "${Ref}:${Ref}"
        if ($LASTEXITCODE -eq 0) {
            Write-Output $Horizon
            return
        }

        if (Test-RemoteRef $Root $Remote $Ref) {
            [Console]::Error.WriteLine("Collision: $Tag was reserved by another operator; retrying ($Attempt/$MaxAttempts).")
            Remove-LocalProposal $Root $Tag
            continue
        }

        Remove-LocalProposal $Root $Tag
        Fail "push of $Tag failed and the ref does not exist remotely; refusing to report success"
    }

    Fail "unable to reserve a horizon ID after $MaxAttempts attempts"
}

function Invoke-Abandon {
    param([string]$Horizon, [string]$Reason, [string]$Remote)
    if ($Horizon -notmatch '^H[0-8][0-9]{2}$') { Fail 'abandon requires a production horizon ID H000-H899' }
    if ([string]::IsNullOrWhiteSpace($Reason)) { Fail '--reason must not be empty' }
    if ($Reason.Contains("`n") -or $Reason.Contains("`r")) { Fail '--reason must be a single line' }

    $Root = Get-RepoRoot
    Assert-Remote $Root $Remote
    $Identity = Get-GitIdentity $Root
    $OriginalTag = "horizon/$Horizon"
    $OriginalRef = "refs/tags/$OriginalTag"
    $AbandonedTag = "$OriginalTag-abandoned"
    $AbandonedRef = "refs/tags/$AbandonedTag"

    if (-not (Test-RemoteRef $Root $Remote $OriginalRef)) { Fail "$OriginalTag does not exist on remote '$Remote'" }
    if (Test-RemoteRef $Root $Remote $AbandonedRef) { Fail "$AbandonedTag already exists on remote '$Remote'" }

    & git -C $Root fetch --quiet --no-tags $Remote "${OriginalRef}:${OriginalRef}"
    if ($LASTEXITCODE -ne 0) { Fail "cannot fetch $OriginalTag from remote '$Remote'" }
    $Target = Invoke-GitCapture @('-C', $Root, 'rev-parse', "${OriginalRef}^{}")
    if ($Target.ExitCode -ne 0) { Fail "cannot resolve target for $OriginalTag" }

    $AbandonedAt = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    $Message = New-AbandonmentMessage $Horizon $Identity $AbandonedAt $Reason
    & git -C $Root tag -a $AbandonedTag -m $Message $Target.Output
    if ($LASTEXITCODE -ne 0) { Fail "cannot create local abandonment record $AbandonedTag" }

    & git -C $Root push --quiet $Remote "${AbandonedRef}:${AbandonedRef}"
    if ($LASTEXITCODE -ne 0) {
        Remove-LocalProposal $Root $AbandonedTag
        Fail "push of $AbandonedTag failed; refusing to report success"
    }

    Write-Output $Horizon
}

$Remote = 'origin'
$MaxAttempts = 10
$TargetRef = 'HEAD'
$Remaining = @($Arguments | Where-Object { $null -ne $_ })

switch ($Command) {
    { $_ -in @('help', '--help', '-h') } {
        if ($Remaining.Count -ne 0) { Fail 'help does not accept arguments' }
        Show-Help
        break
    }
    'mint' {
        for ($Index = 0; $Index -lt $Remaining.Count; $Index++) {
            switch ($Remaining[$Index]) {
                '--remote' {
                    if ($Index + 1 -ge $Remaining.Count) { Fail '--remote requires a value' }
                    $Index++; Require-Value '--remote' $Remaining[$Index]; $Remote = $Remaining[$Index]
                }
                '--max-attempts' {
                    if ($Index + 1 -ge $Remaining.Count) { Fail '--max-attempts requires a value' }
                    $Index++; Require-Value '--max-attempts' $Remaining[$Index]
                    if ($Remaining[$Index] -notmatch '^[1-9][0-9]*$') { Fail '--max-attempts must be a positive integer' }
                    $MaxAttempts = [int]$Remaining[$Index]
                }
                '--target-ref' {
                    if ($Index + 1 -ge $Remaining.Count) { Fail '--target-ref requires a value' }
                    $Index++; Require-Value '--target-ref' $Remaining[$Index]; $TargetRef = $Remaining[$Index]
                }
                { $_ -in @('--help', '-h') } { Show-Help; exit 0 }
                default { Fail "unknown mint option: $($Remaining[$Index])" }
            }
        }
        Invoke-Mint $Remote $MaxAttempts $TargetRef
        break
    }
    'abandon' {
        if ($Remaining.Count -eq 0) { Fail 'abandon requires HNNN' }
        $Horizon = $Remaining[0]
        $Reason = ''
        for ($Index = 1; $Index -lt $Remaining.Count; $Index++) {
            switch ($Remaining[$Index]) {
                '--reason' {
                    if ($Index + 1 -ge $Remaining.Count) { Fail '--reason requires a value' }
                    $Index++; Require-Value '--reason' $Remaining[$Index]; $Reason = $Remaining[$Index]
                }
                '--remote' {
                    if ($Index + 1 -ge $Remaining.Count) { Fail '--remote requires a value' }
                    $Index++; Require-Value '--remote' $Remaining[$Index]; $Remote = $Remaining[$Index]
                }
                { $_ -in @('--help', '-h') } { Show-Help; exit 0 }
                default { Fail "unknown abandon option: $($Remaining[$Index])" }
            }
        }
        if ([string]::IsNullOrWhiteSpace($Reason)) { Fail 'abandon requires --reason <text>' }
        Invoke-Abandon $Horizon $Reason $Remote
        break
    }
    default { Fail "unknown command: $Command (use 'help')" }
}