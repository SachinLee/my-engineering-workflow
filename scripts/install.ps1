[CmdletBinding(SupportsShouldProcess)]
param(
  [ValidateSet("User", "Project")]
  [string]$Scope = "Project",

  [ValidateSet("Codex", "OMP", "Claude", "Pi", "Both", "All")]
  [string]$Harness = "Both",

  [string]$ProjectPath
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $PSScriptRoot)).Path
$ompExtensionsRoot = Join-Path (Split-Path -Parent $repoRoot) "omp-extensions"
$workflowReviewGateSource = Join-Path $ompExtensionsRoot "workflow-review-gate"
$agentDirOverride = if ([string]::IsNullOrWhiteSpace($env:PI_CODING_AGENT_DIR)) {
  $null
} else {
  $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath(
    $env:PI_CODING_AGENT_DIR
  )
}
$piUserRoot = if ($agentDirOverride) { $agentDirOverride } else { Join-Path $HOME ".pi\agent" }
$ompUserRoot = if ($agentDirOverride) { $agentDirOverride } else { Join-Path $HOME ".omp\agent" }
$skillNames = @(
  "run-engineering-workflow",
  "clarify-requirements",
  "plan-solution",
  "review-implementation",
  "finish-with-evidence",
  "archive-task"
)
$ompAgentNames = @(
  "workflow-planner.md",
  "workflow-implementer.md",
  "workflow-reviewer.md"
)
$claudeAgentNames = @(
  "workflow-planner.md",
  "workflow-implementer.md",
  "workflow-reviewer.md"
)
$claudeCommandNames = @(
  "engineering-workflow.md",
  "archive-task.md"
)
$piAgentNames = @(
  "workflow-planner.md",
  "workflow-implementer.md",
  "workflow-reviewer.md"
)

if ($Scope -eq "Project") {
  if (-not $ProjectPath) {
    throw "ProjectPath is required when Scope is Project."
  }
  $project = (Resolve-Path -LiteralPath $ProjectPath).Path
} else {
  $project = $null
}

function Assert-ManagedChild {
  param(
    [Parameter(Mandatory)] [string]$Root,
    [Parameter(Mandatory)] [string]$Child
  )

  $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\', '/')
  $childFull = [IO.Path]::GetFullPath($Child)
  $prefix = $rootFull + [IO.Path]::DirectorySeparatorChar
  if (-not $childFull.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to manage a path outside target root: $childFull"
  }
}

function Assert-NotReparsePoint {
  param([Parameter(Mandatory)] [string]$Path)

  if (Test-Path -LiteralPath $Path) {
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
      throw "Refusing to replace a symlink or junction: $Path"
    }
  }
}

function Sync-SkillDirectory {
  param(
    [Parameter(Mandatory)] [string]$Source,
    [Parameter(Mandatory)] [string]$TargetRoot,
    [Parameter(Mandatory)] [string]$Name
  )

  if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
    throw "Skill source directory was not found: $Source"
  }
  $target = Join-Path $TargetRoot $Name
  Assert-ManagedChild -Root $TargetRoot -Child $target
  Assert-NotReparsePoint -Path $target
  if ($PSCmdlet.ShouldProcess($target, "replace managed skill directory")) {
    New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null
    if (Test-Path -LiteralPath $target) {
      Remove-Item -LiteralPath $target -Recurse -Force
    }
    Copy-Item -LiteralPath $Source -Destination $TargetRoot -Recurse -Force
  }
}

function Copy-ManagedFile {
  param(
    [Parameter(Mandatory)] [string]$Source,
    [Parameter(Mandatory)] [string]$Target
  )


  if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
    throw "Managed source file was not found: $Source"
  }

  if ([IO.Path]::GetFullPath($Source) -eq [IO.Path]::GetFullPath($Target)) {
    Write-Host "Managed workflow file already at target: $Target"
    return
  }
  $targetRoot = Split-Path -Parent $Target
  Assert-ManagedChild -Root $targetRoot -Child $Target
  Assert-NotReparsePoint -Path $Target
  if ($PSCmdlet.ShouldProcess($Target, "install managed workflow file")) {
    New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Target -Force
  }
}

function Remove-LegacyManagedFile {
  param([Parameter(Mandatory)] [string]$Path)

  $targetRoot = Split-Path -Parent $Path
  Assert-ManagedChild -Root $targetRoot -Child $Path
  Assert-NotReparsePoint -Path $Path
  if ((Test-Path -LiteralPath $Path -PathType Leaf) -and
      $PSCmdlet.ShouldProcess($Path, "remove legacy managed workflow file")) {
    Remove-Item -LiteralPath $Path -Force
  }
}

function Add-OmpSkillWhitelist {
  param(
    [Parameter(Mandatory)] [string]$Path,
    [Parameter(Mandatory)] [string[]]$Names
  )

  # Plain `omp` filters discovered skills through skills.includeSkills in its own
  # config.yml. A non-empty list that lacks a skill hides it even when installed.
  # No file, or no includeSkills list, means no filtering: leave it alone.
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    Write-Host "OMP config not found, so skills stay unfiltered: $Path"
    return
  }
  Assert-NotReparsePoint -Path $Path

  $raw = [IO.File]::ReadAllText($Path)
  $eol = if ($raw -match "\r\n") { "`r`n" } else { "`n" }
  $lines = @($raw -split "\r?\n")

  $keyIndex = -1
  for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^skills:\s*(?:#.*)?$') { $keyIndex = $i; break }
  }
  if ($keyIndex -lt 0) {
    Write-Host "OMP config has no skills block, so skills stay unfiltered: $Path"
    return
  }

  $listIndent = $null
  $listIndex = -1
  for ($i = $keyIndex + 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\S') { break }
    if ($lines[$i] -match '^(\s+)includeSkills:\s*(?:#.*)?$') {
      $listIndent = $matches[1]
      $listIndex = $i
      break
    }
  }
  if ($listIndex -lt 0) {
    Write-Host "OMP config has no includeSkills list, so skills stay unfiltered: $Path"
    return
  }

  $existing = New-Object System.Collections.Generic.List[string]
  $entryIndent = $null
  $lastEntry = $listIndex
  for ($i = $listIndex + 1; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ($line -match '^\s*$' -or $line -match '^\s*#') { continue }
    if ($line -notmatch '^(\s*)-\s+(.+?)\s*$') { break }
    if ($null -eq $entryIndent) { $entryIndent = $matches[1] }
    $lastEntry = $i
    [void]$existing.Add(($matches[2] -replace '^["\x27]|["\x27]$', ''))
  }

  $missing = @($Names | Where-Object { $existing -notcontains $_ })
  if ($missing.Count -eq 0) {
    Write-Host "OMP skill whitelist already lists every workflow skill."
    return
  }
  if ($null -eq $entryIndent) { $entryIndent = $listIndent + '  ' }

  if ($PSCmdlet.ShouldProcess($Path, "add $($missing.Count) skill(s) to OMP includeSkills")) {
    $newLines = @($missing | ForEach-Object { "$entryIndent- $_" })
    $lines = @($lines[0..$lastEntry]) + $newLines + @($lines[($lastEntry + 1)..($lines.Count - 1)])
    [IO.File]::WriteAllText($Path, ($lines -join $eol))
  }
  Write-Host "Added to OMP skill whitelist: $($missing -join ', ')"
}

if ($Harness -in @("Codex", "Both", "All")) {
  $codexSkills = if ($Scope -eq "Project") {
    Join-Path $project ".agents\skills"
  } else {
    Join-Path $HOME ".codex\skills"
  }

  foreach ($name in $skillNames) {
    Sync-SkillDirectory `
      -Source (Join-Path $repoRoot "skills\$name") `
      -TargetRoot $codexSkills `
      -Name $name
  }

  Copy-ManagedFile `
    -Source (Join-Path $repoRoot "scripts\openspec_compat.py") `
    -Target (Join-Path $codexSkills "run-engineering-workflow\scripts\openspec_compat.py")
}
if ($Harness -in @("OMP", "Both", "All")) {
  $ompRoot = if ($Scope -eq "Project") {
    Join-Path $project ".omp"
  } else {
    $ompUserRoot
  }
  $ompSkills = Join-Path $ompRoot "skills"
  $ompAgents = Join-Path $ompRoot "agents"
  $ompExtensions = Join-Path $ompRoot "extensions"

  foreach ($name in $skillNames) {
    Sync-SkillDirectory `
      -Source (Join-Path $repoRoot "skills\$name") `
      -TargetRoot $ompSkills `
      -Name $name
  }

  Copy-ManagedFile `
    -Source (Join-Path $repoRoot "scripts\openspec_compat.py") `
    -Target (Join-Path $ompSkills "run-engineering-workflow\scripts\openspec_compat.py")

  foreach ($fileName in $ompAgentNames) {
    Copy-ManagedFile `
      -Source (Join-Path $repoRoot ".omp\agents\$fileName") `
      -Target (Join-Path $ompAgents $fileName)
  }

  Sync-SkillDirectory `
    -Source $workflowReviewGateSource `
    -TargetRoot $ompExtensions `
    -Name "workflow-review-gate"

  Copy-ManagedFile `
    -Source (Join-Path $repoRoot "config\omp-workflow.yml") `
    -Target (Join-Path $ompRoot "engineering-workflow.yml")
  Copy-ManagedFile `
    -Source (Join-Path $repoRoot "scripts\start-omp.py") `
    -Target (Join-Path $ompRoot "start-engineering-workflow.py")
  Remove-LegacyManagedFile `
    -Path (Join-Path $ompRoot "start-engineering-workflow.ps1")
  Add-OmpSkillWhitelist `
    -Path (Join-Path $ompRoot "config.yml") `
    -Names $skillNames
}

if ($Harness -in @("Claude", "All")) {
  $claudeRoot = if ($Scope -eq "Project") {
    Join-Path $project ".claude"
  } else {
    Join-Path $HOME ".claude"
  }
  $claudeSkills = Join-Path $claudeRoot "skills"
  $claudeAgents = Join-Path $claudeRoot "agents"
  $claudeCommands = Join-Path $claudeRoot "commands"

  foreach ($name in $skillNames) {
    Sync-SkillDirectory `
      -Source (Join-Path $repoRoot "skills\$name") `
      -TargetRoot $claudeSkills `
      -Name $name
  }

  Copy-ManagedFile `
    -Source (Join-Path $repoRoot "scripts\openspec_compat.py") `
    -Target (Join-Path $claudeSkills "run-engineering-workflow\scripts\openspec_compat.py")

  foreach ($fileName in $claudeAgentNames) {
    Copy-ManagedFile `
      -Source (Join-Path $repoRoot "agents\$fileName") `
      -Target (Join-Path $claudeAgents $fileName)
  }

  foreach ($fileName in $claudeCommandNames) {
    Copy-ManagedFile `
      -Source (Join-Path $repoRoot "commands\$fileName") `
      -Target (Join-Path $claudeCommands $fileName)
  }
}

if ($Harness -in @("Pi", "All")) {
  $piRoot = if ($Scope -eq "Project") {
    Join-Path $project ".pi"
  } else {
    $piUserRoot
  }
  $piSkills = if ($Scope -eq "Project") {
    Join-Path $project ".agents\skills"
  } else {
    Join-Path $piRoot "skills"
  }
  $piAgents = Join-Path $piRoot "agents"

  foreach ($name in $skillNames) {
    Sync-SkillDirectory `
      -Source (Join-Path $repoRoot "skills\$name") `
      -TargetRoot $piSkills `
      -Name $name
  }

  Copy-ManagedFile `
    -Source (Join-Path $repoRoot "scripts\openspec_compat.py") `
    -Target (Join-Path $piSkills "run-engineering-workflow\scripts\openspec_compat.py")

  foreach ($fileName in $piAgentNames) {
    Copy-ManagedFile `
      -Source (Join-Path $repoRoot ".pi\agents\$fileName") `
      -Target (Join-Path $piAgents $fileName)
  }
}

$resultVerb = if ($WhatIfPreference) { "Planned" } else { "Installed" }
Write-Host "$resultVerb $($skillNames.Count) workflow skills for $Harness at $Scope scope."
if ($Scope -eq "Project" -and $Harness -in @("OMP", "Both", "All")) {
  $startPrefix = if ($WhatIfPreference) { "After installation, start" } else { "Start" }
  $launcher = Join-Path $project ".omp\start-engineering-workflow.py"
  Write-Host "$startPrefix OMP with: python '$launcher' --project-path '$project'"
}
if ($Scope -eq "Project" -and $Harness -in @("Pi", "All")) {
  Write-Host "Start Pi from the trusted project root with: pi"
}
