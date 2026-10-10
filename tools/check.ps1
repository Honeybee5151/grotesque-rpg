<#
.SYNOPSIS
  The merge checks, in one go. Checks the checkout this script lives in, from any folder.
    import            godot --headless --import
    scripts           every .gd file parses (tools/check_scripts.gd), even ones nothing runs yet
    boot              boot -> title screen, headless, for a moment
    autoplay smart    tools/smoke_test.gd -- smart
    autoplay attack   tools/smoke_test.gd -- attack
    autoplay smart troop=host,host   two enemies: the target menu and multi-enemy battles
    autoplay skills   the Skill submenu, spending MP
    export            the game.pck players get (export filters, remaps), then boot and the
                      battle run from it - catches files that work here but don't ship
    updater           tools/update_test.sh through Git Bash (only with -Updater)

.DESCRIPTION
  A check fails on a non-zero exit code, a Godot error (SCRIPT ERROR, ERROR:, Parse Error), a run
  that hangs past its time limit, or an autoplay that never prints its "=== RESULT" line. Leaks at
  exit are ignored; warnings are listed but don't fail. A parse error stops the remaining checks.
  Exits 1 if anything failed. Uses $env:GODOT (team terminals set it), else `godot` from PATH.

.EXAMPLE
  tools\check.ps1             # before "ready to merge", and on every merge
.EXAMPLE
  tools\check.ps1 -Updater    # also the updater end-to-end test (needs Git for Windows and Python)
#>
[CmdletBinding()]
param([switch]$Updater)

$Root = Split-Path -Parent $PSScriptRoot
$Godot = if ($env:GODOT) { $env:GODOT } else { 'godot' }
# One autoplay per entry: the smoke_test.gd arguments (fights owns the autoplay; they say what to run).
$Policies = @('smart', 'attack', 'smart troop=host,host', 'skills')

$ErrorPattern = '^\s*(SCRIPT ERROR|USER ERROR|ERROR):|Parse Error'
$WarningPattern = '^\s*(USER WARNING|WARNING):'
$IgnorePattern = 'ObjectDB instances leaked|resources still in use at exit'

$Failed = New-Object System.Collections.Generic.List[string]
$Stop = ''   # set when continuing makes no sense (parse errors)

function Say([string]$Text, [string]$Color = 'Gray') { Write-Host $Text -ForegroundColor $Color }

# Run a program with a time limit; collect stdout and stderr separately.
function Invoke-Native([string]$Exe, [string[]]$Arguments, [int]$TimeoutSeconds, [string]$WorkDir = '') {
    $resolved = Get-Command $Exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = if ($resolved) { $resolved.Source } else { $Exe }
    if ($WorkDir) { $psi.WorkingDirectory = $WorkDir }
    $psi.Arguments = ($Arguments | ForEach-Object { if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ } }) -join ' '
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = [Text.Encoding]::UTF8
    $psi.StandardErrorEncoding = [Text.Encoding]::UTF8
    $watch = [Diagnostics.Stopwatch]::StartNew()
    $p = [Diagnostics.Process]::Start($psi)
    $out = $p.StandardOutput.ReadToEndAsync()
    $err = $p.StandardError.ReadToEndAsync()
    $timedOut = -not $p.WaitForExit($TimeoutSeconds * 1000)
    if ($timedOut) {
        try { $p.Kill() } catch { }
        [void]$p.WaitForExit(10000)
    }
    [void][Threading.Tasks.Task]::WaitAll(@($out, $err), 10000)
    $split = { param($t) if ($t.IsCompleted) { @($t.Result -split '\r?\n' | Where-Object { $_ -ne '' }) } else { @() } }
    return [pscustomobject]@{
        Code     = if ($timedOut) { -1 } else { $p.ExitCode }
        TimedOut = $timedOut
        Limit    = $TimeoutSeconds
        Out      = & $split $out
        Err      = & $split $err
        Seconds  = [int]$watch.Elapsed.TotalSeconds
    }
}

function Get-Matches([string[]]$Lines, [string]$Pattern) {
    $found = @()
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -notmatch $Pattern -or $Lines[$i] -match $IgnorePattern) { continue }
        $text = $Lines[$i].Trim()
        if ($i + 1 -lt $Lines.Count -and $Lines[$i + 1] -match '^\s*at:') { $text += '  (' + $Lines[$i + 1].Trim() + ')' }
        $found += $text
    }
    return $found
}

function Show-Capped([string[]]$Items, [string]$Color, [int]$Max = 6) {
    $unique = @($Items | Select-Object -Unique)
    foreach ($item in ($unique | Select-Object -First $Max)) { Say "            $item" $Color }
    if ($unique.Count -gt $Max) { Say ("            ... and {0} more" -f ($unique.Count - $Max)) $Color }
}

# Judge one run and print its line. $Need: a regex some stdout line must match. $Show: the stdout
# line to print next to "ok".
function Report([string]$Name, $Run, [string]$Need = '', [string]$Show = '') {
    $all = @($Run.Out) + @($Run.Err)
    $problems = @()
    if ($Run.TimedOut) { $problems += "still running after $($Run.Limit)s - stopped it" }
    elseif ($Run.Code -ne 0) { $problems += "exit code $($Run.Code)" }
    if ($Need -and -not ($Run.Out | Where-Object { $_ -match $Need })) { $problems += "no line matching '$Need'" }
    $problems += Get-Matches $Run.Err $ErrorPattern
    $problems += Get-Matches $Run.Out ($ErrorPattern + '|^\s*(FAILED|BROKEN)\b')
    $warnings = @(Get-Matches $all $WarningPattern)
    if (($problems | Where-Object { $_ -match 'Parse Error' })) { $script:Stop = "parse errors in $Name" }

    $label = ("{0,-30} {1,3}s" -f $Name, $Run.Seconds)
    $extra = ''
    if ($Show) { $extra = $Run.Out | Where-Object { $_ -match $Show } | Select-Object -Last 1 }
    if ($problems.Count -eq 0) {
        Say "  ok      $label  $extra" Green
    } else {
        Say "  FAILED  $label  $extra" Red
        Show-Capped $problems Red
        $tail = @($Run.Out | Where-Object { $_ -notmatch '^Godot Engine v' } | Select-Object -Last 8)
        if ($tail.Count -gt 0) { Say '            last lines of output:' DarkGray }
        foreach ($l in $tail) { Say "              $l" DarkGray }
        $script:Failed.Add($Name)
    }
    Show-Capped $warnings Yellow
}

function Skip([string]$Name) {
    Say ("  -       {0,-30}       skipped: {1}" -f $Name, $Stop) DarkGray
    $script:Failed.Add($Name)
}

function Find-Bash {
    if ($env:OS -ne 'Windows_NT') { return 'bash' }
    # Git for Windows' bash; System32\bash.exe is WSL, which can't run the Windows Godot.
    $exec = & git --exec-path   # <git>/mingw64/libexec/git-core
    if ($exec) {
        $bash = Join-Path (Split-Path (Split-Path (Split-Path $exec))) 'bin\bash.exe'
        if (Test-Path $bash) { return $bash }
    }
    return $null
}

Say "Checking $Root" Cyan
Report 'import' (Invoke-Native $Godot @('--headless', '--path', $Root, '--import') 600)
$run = Invoke-Native $Godot @('--headless', '--path', $Root, '--script', 'res://tools/check_scripts.gd') 120
Report 'scripts' $run '^=== SCRIPTS:' '^=== SCRIPTS:'
if ($Stop) { Skip 'boot' } else {
    Report 'boot' (Invoke-Native $Godot @('--headless', '--path', $Root, '--quit-after', '120') 60)
}
foreach ($p in $Policies) {
    if ($Stop) { Skip "autoplay $p"; continue }
    $run = Invoke-Native $Godot (@('--headless', '--path', $Root, '--script', 'res://tools/smoke_test.gd', '--') + ($p -split ' ')) 120
    Report "autoplay $p" $run '^=== RESULT:' '^=== RESULT:'
}
# The exported game: only resources (plus release.cfg) ship, minus tools/; run it from the pack in an
# empty folder so nothing from the project folder can stand in for a missing file.
if ($Stop) { Skip 'export' } else {
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ('grotesque-check-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
    New-Item -ItemType Directory -Path $tmp | Out-Null
    try {
        $pck = Join-Path $tmp 'game.pck'
        Report 'export' (Invoke-Native $Godot @('--headless', '--path', $Root, '--export-pack', 'Windows Desktop', $pck) 300)
        if (Test-Path $pck) {
            Report 'export: boot' (Invoke-Native $Godot @('--headless', '--main-pack', $pck, '--quit-after', '120') 60 $tmp)
            Report 'export: battle' (Invoke-Native $Godot @('--headless', '--main-pack', $pck, 'res://main.tscn', '--quit-after', '300') 60 $tmp)
        }
    } finally {
        Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    }
}
if (-not $Updater) {
    Say ('  -       {0,-30}       (add -Updater when anything near the updater changed)' -f 'updater') DarkGray
} elseif ($Stop) {
    Skip 'updater'
} else {
    $bash = Find-Bash
    if (-not $bash) {
        Say ('  FAILED  {0,-30}       Git Bash not found (install Git for Windows)' -f 'updater') Red
        $Failed.Add('updater')
    } else {
        $script = (Join-Path $Root 'tools/update_test.sh') -replace '\\', '/'
        Report 'updater' (Invoke-Native $bash @($script) 300) '^== updater: all checks passed' '^== updater:'
    }
}

Write-Host ''
if ($Failed.Count -gt 0) {
    Say ("FAILED: " + ($Failed -join ', ')) Red
    exit 1
}
Say 'All checks passed.' Green
exit 0
