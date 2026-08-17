[CmdletBinding(SupportsShouldProcess)]
param(
  [ValidateSet("User", "Project")]
  [string]$Scope = "Project",

  [ValidateSet("Codex", "OMP", "Claude", "Both", "All")]
  [string]$Harness = "Both",

  [string]$ProjectPath
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $PSScriptRoot)).Path
$skillNames = @(
  "run-engineering-workflow",
  "clarify-requirements",
  "plan-solution",
  "review-implementation",
  "finish-with-evidence"
)
$ompAgentNames = @(
  "workflow-planner.md",
  "workflow-reviewer.md"
)
$claudeAgentNames = @(
  "workflow-planner.md",
  "workflow-reviewer.md"
)
$claudeCommandNames = @(
  "engineering-workflow.md"
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
}

if ($Harness -in @("OMP", "Both", "All")) {
  $ompRoot = if ($Scope -eq "Project") {
    Join-Path $project ".omp"
  } else {
    Join-Path $HOME ".omp\agent"
  }
  $ompSkills = Join-Path $ompRoot "skills"
  $ompAgents = Join-Path $ompRoot "agents"

  foreach ($name in $skillNames) {
    Sync-SkillDirectory `
      -Source (Join-Path $repoRoot "skills\$name") `
      -TargetRoot $ompSkills `
      -Name $name
  }

  foreach ($fileName in $ompAgentNames) {
    Copy-ManagedFile `
      -Source (Join-Path $repoRoot ".omp\agents\$fileName") `
      -Target (Join-Path $ompAgents $fileName)
  }

  Copy-ManagedFile `
    -Source (Join-Path $repoRoot "config\omp-workflow.yml") `
    -Target (Join-Path $ompRoot "engineering-workflow.yml")
  Copy-ManagedFile `
    -Source (Join-Path $repoRoot "scripts\start-omp.py") `
    -Target (Join-Path $ompRoot "start-engineering-workflow.py")
  Remove-LegacyManagedFile `
    -Path (Join-Path $ompRoot "start-engineering-workflow.ps1")
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

$resultVerb = if ($WhatIfPreference) { "Planned" } else { "Installed" }
Write-Host "$resultVerb $($skillNames.Count) workflow skills for $Harness at $Scope scope."
if ($Scope -eq "Project" -and $Harness -in @("OMP", "Both", "All")) {
  $startPrefix = if ($WhatIfPreference) { "After installation, start" } else { "Start" }
  $launcher = Join-Path $project ".omp\start-engineering-workflow.py"
  Write-Host "$startPrefix OMP with: python '$launcher' --project-path '$project'"
}
