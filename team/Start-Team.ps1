<#
.SYNOPSIS
  Opens the Grotesque RPG agent team: four Claude Code sessions (Opus 5.5, max effort), one per
  PowerShell window, each in its own git worktree so they never edit the same files.

.DESCRIPTION
  Roles (see team\roles\*.md):
    monster  monster designer and pixel artist       <home>\monster   branch team/monster
    world    world builder                           <home>\world     branch team/world
    fights   combat designer and battle programmer   <home>\fights    branch team/fights
    misc     integrator and everything else          <home>\main      branch main
  <home> is the folder that contains this repository's checkout.

  The first run checks for (and offers to install) Git, Claude Code, Godot 4.4.1 and the Python
  packages the art tools use, signs you in to Claude, creates the worktrees, then opens the windows.
  The sessions can message each other by name (@monster, @world, @fights, @misc).

  Permissions: sessions start in auto mode - no permission prompts; Claude Code's safety
  classifier approves routine work and blocks risky actions (force-push, wiping files, piping
  downloads into a shell...). monster, world and fights are also hard-blocked from pushing main and
  from editing VERSION or CI. -Bypass turns every check off (bypassPermissions mode).

.EXAMPLE
  .\Start-Team.ps1                       # four PowerShell windows, fresh conversations
.EXAMPLE
  .\Start-Team.ps1 -Continue             # pick up each role's previous conversation
.EXAMPLE
  .\Start-Team.ps1 -Layout Grid          # one Windows Terminal window split 2x2
.EXAMPLE
  .\Start-Team.ps1 -Only monster,fights  # just part of the team
.EXAMPLE
  .\Start-Team.ps1 -Bypass              # no safety checks at all (bypassPermissions)
.EXAMPLE
  .\Start-Team.ps1 -DryRun              # prepare everything, print the commands, open nothing
#>
[CmdletBinding()]
param(
    [ValidateSet('Windows', 'Grid', 'Tabs')] [string]$Layout = 'Windows',
    [switch]$Continue,
    [string[]]$Only,
    [ValidateSet('auto', 'acceptEdits', 'default', 'manual', 'plan', 'dontAsk', 'bypassPermissions')] [string]$PermissionMode = 'auto',
    [switch]$Bypass,
    [switch]$DryRun,
    [string]$Model = 'claude-opus-5-5',
    [string]$Effort = 'max',
    [switch]$SkipChecks
)

$Roles = @('monster', 'world', 'fights', 'misc')
$GodotVersion = '4.4.1'
$MinClaudeVersion = [version]'2.1.234'   # cross-session messaging on native Windows

$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$TeamHome = Split-Path -Parent $Repo
$ToolsDir = Join-Path $TeamHome '.tools'
$GodotExe = $null
$ScriptArgs = @{}
foreach ($key in $PSBoundParameters.Keys) { $ScriptArgs[$key] = $PSBoundParameters[$key] }

$Kickoff = @{
    monster = 'New shift. Read CLAUDE.md and docs/art.md, check the git log and merge main if it moved. Then do the first-shift task in your role file: get the Host concepts in front of Miles and ask which one he wants.'
    world   = 'New shift. Read CLAUDE.md and the docs folder, check the git log and merge main if it moved. Then do the first-shift task in your role file: pitch the world to Miles in a few lines and ask what to build first.'
    fights  = 'New shift. Read CLAUDE.md, scripts/main.gd and scripts/data.gd, run the battle autoplay and merge main if it moved. Then do the first-shift task in your role file: propose the next combat steps and ask Miles which comes first.'
    misc    = 'New shift. Read CLAUDE.md. Then do the first-shift task in your role file: check that the team setup works on this machine, fix what is broken, tell the others you are the merge point, and report to Miles.'
}

# ------------------------------------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------------------------------------

function Say([string]$Text, [string]$Color = 'Gray') { Write-Host $Text -ForegroundColor $Color }

function Step([string]$Text) {
    Write-Host ''
    Write-Host "== $Text" -ForegroundColor Cyan
}

function Has([string]$Name) { return [bool](Get-Command $Name -ErrorAction SilentlyContinue) }

function YesNo([string]$Question) {
    $answer = Read-Host "$Question [Y/n]"
    return ($answer -eq '' -or $answer -match '^\s*[yY]')
}

function Quote([string]$Text) { return "'" + ($Text -replace "'", "''") + "'" }

function Update-SessionPath {
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($machine -or $user) { $env:Path = "$machine;$user" }
    $local = Join-Path $env:USERPROFILE '.local\bin'
    if ((Test-Path $local) -and ($env:Path -notlike "*$local*")) { $env:Path = "$local;$env:Path" }
}

# Run a native command without Windows PowerShell 5.1 turning its stderr into terminating errors.
function Invoke-Native([string]$Exe, [string[]]$Arguments) {
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $out = & $Exe @Arguments 2>&1 | ForEach-Object { "$_" }
    } finally {
        $ErrorActionPreference = $old
    }
    return [pscustomobject]@{ Code = $LASTEXITCODE; Output = @($out) }
}

function Invoke-Git([string[]]$Arguments) {
    $r = Invoke-Native 'git' (@('-C', $Repo) + $Arguments)
    if ($r.Code -ne 0) {
        throw ("git " + ($Arguments -join ' ') + " failed:`n" + ($r.Output -join "`n"))
    }
    return $r.Output
}

# ------------------------------------------------------------------------------------------------
# prerequisites
# ------------------------------------------------------------------------------------------------

function Ensure-Git {
    if (Has 'git') { return }
    Say 'Git is not installed. The team needs it.' Yellow
    if ((Has 'winget') -and (YesNo 'Install Git for Windows with winget now?')) {
        winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
        Update-SessionPath
    }
    if (-not (Has 'git')) {
        throw 'Git is still missing. Install it from https://git-scm.com/downloads/win and run this again.'
    }
}

function Ensure-Claude {
    Update-SessionPath
    if (-not (Has 'claude')) {
        Say 'Claude Code is not installed.' Yellow
        if (-not (YesNo 'Install it now with the official installer (irm https://claude.ai/install.ps1 | iex)?')) {
            throw 'Claude Code is required. See https://code.claude.com/docs/en/setup'
        }
        Invoke-RestMethod -Uri 'https://claude.ai/install.ps1' | Invoke-Expression
        Update-SessionPath
        if (-not (Has 'claude')) {
            throw 'Claude Code installed, but it is not on PATH yet. Open a new PowerShell window and run this again.'
        }
    }
    $v = (Invoke-Native 'claude' @('--version')).Output -join ' '
    Say "Claude Code: $v" DarkGray
    if ($v -match '(\d+)\.(\d+)\.(\d+)') {
        $ver = [version]("{0}.{1}.{2}" -f $Matches[1], $Matches[2], $Matches[3])
        if ($ver -lt $MinClaudeVersion) {
            Say "Claude Code $ver is older than $MinClaudeVersion (needed for the agents to message each other). Updating..." Yellow
            & claude update
        }
    }
    if ((Invoke-Native 'claude' @('auth', 'status')).Code -ne 0) {
        Say 'Sign in to Claude: a browser window opens.' Yellow
        & claude auth login
        if ((Invoke-Native 'claude' @('auth', 'status')).Code -ne 0) { throw 'Not signed in to Claude Code.' }
    }
}

function Find-Godot {
    $exe = Join-Path (Join-Path $ToolsDir "godot-$GodotVersion") "Godot_v$GodotVersion-stable_win64_console.exe"
    if (Test-Path $exe) { return $exe }
    if ($env:GODOT -and (Test-Path $env:GODOT)) { return $env:GODOT }
    return $null
}

function Ensure-Godot {
    $found = Find-Godot
    if ($found) { return $found }
    $dir = Join-Path $ToolsDir "godot-$GodotVersion"
    Say "Godot $GodotVersion is not set up for the team yet (about 60 MB)." Yellow
    if (-not (YesNo "Download Godot $GodotVersion into $dir ?")) {
        Say 'Skipping Godot: the agents will not be able to run the game or its tests.' Yellow
        return $null
    }
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $zip = Join-Path $dir 'godot.zip'
    $url = "https://github.com/godotengine/godot/releases/download/$GodotVersion-stable/Godot_v$GodotVersion-stable_win64.exe.zip"
    $oldProgress = $ProgressPreference
    $ProgressPreference = 'SilentlyContinue'
    try {
        Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $zip
    } finally {
        $ProgressPreference = $oldProgress
    }
    Expand-Archive -Path $zip -DestinationPath $dir -Force
    Remove-Item $zip -Force
    $found = Find-Godot
    if (-not $found) { throw "The Godot download did not contain the console executable in $dir" }
    return $found
}

function Check-Python {
    $py = $null
    foreach ($candidate in @('py', 'python')) {
        if (-not (Has $candidate)) { continue }
        if ((Invoke-Native $candidate @('-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)')).Code -eq 0) {
            $py = $candidate
            break
        }
    }
    if (-not $py) {
        Say 'Python 3 not found. The monster artist needs it for its art tools: winget install Python.Python.3.12' Yellow
        return
    }
    if ((Invoke-Native $py @('-c', 'import numpy, PIL')).Code -ne 0) {
        if (YesNo "The art tools need numpy and pillow. Install them for '$py' (pip --user)?") {
            & $py -m pip install --user --quiet numpy pillow
        }
    }
}

function Ensure-GitIdentity {
    if (-not ((Invoke-Native 'git' @('-C', $Repo, 'config', '--get', 'user.name')).Output -join '')) {
        $name = Read-Host 'Your name for git commits'
        if ($name) { & git config --global user.name $name }
    }
    if (-not ((Invoke-Native 'git' @('-C', $Repo, 'config', '--get', 'user.email')).Output -join '')) {
        $mail = Read-Host 'Your email for git commits (the one on your GitHub account)'
        if ($mail) { & git config --global user.email $mail }
    }
}

# ------------------------------------------------------------------------------------------------
# self-update
# ------------------------------------------------------------------------------------------------

# "-Only monster,fights" arrives as one string through powershell -File; accept both forms.
function Resolve-Only([string[]]$Names) {
    $out = @()
    foreach ($n in $Names) {
        foreach ($part in ($n -split '[,\s]+')) {
            if (-not $part) { continue }
            if ($Roles -notcontains $part) { throw "Unknown role '$part'. Roles: $($Roles -join ', ')" }
            $out += $part
        }
    }
    return $out
}

function Get-ForwardArgs {
    $list = @()
    foreach ($key in $ScriptArgs.Keys) {
        $value = $ScriptArgs[$key]
        if ($value -is [System.Management.Automation.SwitchParameter]) {
            if ($value.IsPresent) { $list += "-$key" }
        } elseif ($value -is [array]) {
            $list += "-$key"
            $list += ($value -join ',')
        } else {
            $list += "-$key"
            $list += "$value"
        }
    }
    return $list
}

# Bring the main checkout up to date; if that changed this launcher, run the new one instead.
function Update-Main {
    if ((Invoke-Native 'git' @('-C', $Repo, 'fetch', 'origin', '--prune')).Code -ne 0) {
        Say 'Could not reach GitHub; using what is already on this machine.' DarkGray
        return
    }
    $branch = (Invoke-Git @('rev-parse', '--abbrev-ref', 'HEAD')) -join ''
    $dirty = (Invoke-Git @('status', '--porcelain', '--untracked-files=no')) -join ''
    if ($branch -ne 'main' -or $dirty -or -not (Test-Ref 'refs/remotes/origin/main')) { return }
    $before = (Get-FileHash -LiteralPath $PSCommandPath).Hash
    if ((Invoke-Native 'git' @('-C', $Repo, 'merge', '--ff-only', 'origin/main')).Code -ne 0) {
        Say 'main has commits that are not on GitHub yet; leaving it as it is.' DarkGray
        return
    }
    if ((Get-FileHash -LiteralPath $PSCommandPath).Hash -ne $before -and -not $env:GROTESQUE_LAUNCHER_REEXEC) {
        Say 'The launcher was updated; restarting it.' DarkGray
        $env:GROTESQUE_LAUNCHER_REEXEC = '1'
        $hostExe = (Get-Process -Id $PID).Path
        & $hostExe -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath @(Get-ForwardArgs)
        exit $LASTEXITCODE
    }
}

# ------------------------------------------------------------------------------------------------
# checkouts
# ------------------------------------------------------------------------------------------------

function Get-RoleDir([string]$Role) {
    if ($Role -eq 'misc') { return $Repo }
    return (Join-Path $TeamHome $Role)
}

function Test-Ref([string]$Ref) {
    return ((Invoke-Native 'git' @('-C', $Repo, 'show-ref', '--verify', '--quiet', $Ref)).Code -eq 0)
}

function Ensure-Worktrees([string[]]$Wanted) {
    foreach ($role in $Wanted) {
        if ($role -eq 'misc') { continue }
        $dir = Get-RoleDir $role
        if (Test-Path (Join-Path $dir '.git')) { continue }
        if (Test-Path $dir) {
            throw "$dir exists but is not a git checkout. Move it out of the way and run this again."
        }
        $b = "team/$role"
        if (Test-Ref "refs/heads/$b") {
            Invoke-Git @('worktree', 'add', $dir, $b) | Out-Null
        } elseif (Test-Ref "refs/remotes/origin/$b") {
            Invoke-Git @('worktree', 'add', '--track', '-b', $b, $dir, "origin/$b") | Out-Null
        } else {
            Invoke-Git @('worktree', 'add', '-b', $b, $dir, 'main') | Out-Null
        }
        Say "  $role -> $dir ($b)" DarkGray
    }
}

# Every checkout carries its own .claude/settings.json (it is in the repo), and Claude Code merges
# permission lists across files, so an outdated copy keeps outdated rules. Bring each checkout's copy
# in line with main's, unless that checkout has its own uncommitted edits to the file.
function Sync-TeamSettings([string[]]$Wanted) {
    $ref = 'origin/main'
    if (-not (Test-Ref 'refs/remotes/origin/main')) { $ref = 'main' }
    $r = Invoke-Native 'git' @('-C', $Repo, 'show', "${ref}:.claude/settings.json")
    if ($r.Code -ne 0) { return }
    $want = (($r.Output -join "`n").TrimEnd()) + "`n"
    foreach ($role in $Wanted) {
        $dir = Get-RoleDir $role
        if (-not (Test-Path (Join-Path $dir '.git'))) { continue }
        $file = Join-Path (Join-Path $dir '.claude') 'settings.json'
        $have = ''
        if (Test-Path $file) { $have = ([IO.File]::ReadAllText($file)) -replace "`r`n", "`n" }
        if ($have.TrimEnd() -eq $want.TrimEnd()) { continue }
        $local = Invoke-Native 'git' @('-C', $dir, 'status', '--porcelain', '--', '.claude/settings.json')
        if (($local.Output -join '').Trim()) {
            Say ("  {0}: has its own edits to .claude/settings.json; leaving them" -f $role) DarkGray
            continue
        }
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $file) | Out-Null
        [IO.File]::WriteAllText($file, $want)
        $c = Invoke-Native 'git' @('-C', $dir, 'commit', '-q', '-m', 'Sync team permissions from main', '--', '.claude/settings.json')
        if ($c.Code -eq 0) {
            Say ("  {0}: permission rules synced from main" -f $role) DarkGray
        } else {
            Say ("  {0}: permission rules updated (commit them when convenient)" -f $role) DarkGray
        }
    }
}

# ------------------------------------------------------------------------------------------------
# launching
# ------------------------------------------------------------------------------------------------

function Get-RoleCommand([string]$Role) {
    $dir = Get-RoleDir $Role
    $roleFile = Join-Path $Repo "team\roles\$Role.md"
    $bin = Join-Path $Repo 'team\bin'
    $lines = @(
        "`$Host.UI.RawUI.WindowTitle = 'Grotesque: $Role'",
        "Set-Location -LiteralPath $(Quote $dir)",
        "`$env:Path = $(Quote $bin) + ';' + `$env:Path"
    )
    if ($GodotExe) { $lines += "`$env:GODOT = $(Quote $GodotExe)" }
    $base = "claude --model $Model --effort $Effort --name $Role --permission-mode $PermissionMode --append-system-prompt-file $(Quote $roleFile)"
    if ($Role -ne 'misc') {
        # monster/world/fights: hard-blocked from pushing main and editing VERSION or CI
        $base += " --settings $(Quote (Join-Path $Repo 'team\settings\creative.json'))"
    }
    $fresh = "$base $(Quote $Kickoff[$Role])"
    if ($Continue) {
        # fall back to a fresh session only if there was nothing to continue (it exits right away)
        $lines += "`$started = Get-Date"
        $lines += "$base --continue"
        $lines += "if (`$LASTEXITCODE -ne 0 -and ((Get-Date) - `$started).TotalSeconds -lt 15) { $fresh }"
    } else {
        $lines += $fresh
    }
    return ($lines -join "`n")
}

function Get-Encoded([string]$Role) {
    return [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes((Get-RoleCommand $Role)))
}

function Open-Windows([string[]]$Wanted) {
    foreach ($role in $Wanted) {
        Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoExit', '-EncodedCommand', (Get-Encoded $role)) -WorkingDirectory (Get-RoleDir $role)
        Start-Sleep -Milliseconds 1500
    }
}

function Get-TerminalArgs([string[]]$Wanted, [string]$Mode) {
    $parts = @()
    for ($i = 0; $i -lt $Wanted.Count; $i++) {
        $role = $Wanted[$i]
        $pane = "--title $role -d `"$(Get-RoleDir $role)`" powershell.exe -NoExit -EncodedCommand $(Get-Encoded $role)"
        if ($Mode -eq 'Tabs' -or $i -eq 0) {
            $parts += "new-tab $pane"
        } elseif ($i -eq 1) {
            $parts += "split-pane -V $pane"
        } elseif ($i -eq 2) {
            $parts += 'move-focus left'
            $parts += "split-pane -H $pane"
        } else {
            $parts += 'move-focus right'
            $parts += "split-pane -H $pane"
        }
    }
    return ('-w grotesque ' + ($parts -join ' ; '))
}

# ------------------------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------------------------

function Main {
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    } catch { }

    $wanted = $Roles
    if ($Only) {
        $picked = Resolve-Only $Only
        $wanted = @($Roles | Where-Object { $picked -contains $_ })
    }
    if ($Bypass) { $script:PermissionMode = 'bypassPermissions' }

    Say 'Grotesque RPG: starting the team' Magenta
    Say "Repository: $Repo" DarkGray

    Step 'Updating'
    if (Has 'git') { Update-Main }

    if ($SkipChecks) {
        Update-SessionPath
        $script:GodotExe = Find-Godot
    } else {
        Step 'Checking tools'
        Ensure-Git
        Ensure-Claude
        $script:GodotExe = Ensure-Godot
        Check-Python
        Ensure-GitIdentity
    }

    Step 'Preparing checkouts'
    Ensure-Worktrees $wanted
    Sync-TeamSettings $wanted
    $starter = Join-Path $TeamHome 'Start-Team.cmd'
    if (-not (Test-Path $starter)) {
        $leaf = Split-Path -Leaf $Repo
        $body = "@echo off`r`npowershell -NoProfile -ExecutionPolicy Bypass -File `"%~dp0$leaf\team\Start-Team.ps1`" %*`r`nif errorlevel 1 pause`r`n"
        [IO.File]::WriteAllText($starter, $body)
        Say "  next time, double-click $starter" DarkGray
    }

    Step "Opening $($wanted.Count) sessions ($Model, effort $Effort, permissions: $PermissionMode)"
    if ($PermissionMode -eq 'bypassPermissions') {
        Say 'Bypass mode: no permission checks and no safety classifier. The first window asks you to accept that once.' Yellow
    }
    $mode = $Layout
    if ($mode -ne 'Windows' -and -not (Has 'wt')) {
        Say 'Windows Terminal (wt) not found: opening separate PowerShell windows instead.' DarkGray
        $mode = 'Windows'
    }
    if ($DryRun) {
        foreach ($role in $wanted) {
            Say "--- $role" Cyan
            Say (Get-RoleCommand $role) DarkGray
        }
        return
    } elseif ($mode -eq 'Windows') {
        Open-Windows $wanted
    } else {
        Start-Process -FilePath 'wt.exe' -ArgumentList (Get-TerminalArgs $wanted $mode)
    }

    Write-Host ''
    foreach ($role in $wanted) { Say ("  {0,-8} {1}" -f $role, (Get-RoleDir $role)) }
    Write-Host ''
    Say 'First launch in a folder: Claude asks whether you trust it - press Enter in each window.' Yellow
    Say 'Talk to any window directly. They message each other as @monster, @world, @fights and @misc.'
    Say 'Next time: run this again, or add -Continue to pick up where each role left off.'
}

if ($MyInvocation.InvocationName -ne '.') {
    try {
        Main
    } catch {
        Write-Host ''
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
}
