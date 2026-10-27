[CmdletBinding(SupportsShouldProcess)]
param(
  [ValidateSet("User", "Project")]
  [string]$Scope = "User",

  [ValidateSet("Codex", "OMP", "Claude", "Pi", "OpenCode", "Both", "All")]
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
$opencodeDirOverride = if ([string]::IsNullOrWhiteSpace($env:OPENCODE_CONFIG_DIR)) {
  $null
} else {
  $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath(
    $env:OPENCODE_CONFIG_DIR
  )
}
$opencodeUserRoot = if ($opencodeDirOverride) { $opencodeDirOverride } else { Join-Path $HOME ".config\opencode" }
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
$opencodeAgentNames = @(
  "workflow-planner.md",
  "workflow-implementer.md",
  "workflow-reviewer.md"
)
$opencodeCommandNames = @(
  "engineering-workflow.md",
  "archive-task.md"
)
$codexLegacyAgentNames = @(
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

  $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
  if ($null -ne $item) {
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
      throw "Refusing to replace a symlink or junction: $Path"
    }
  }
}

function Assert-SafeParents {
  param([Parameter(Mandatory)] [string]$Path)

  $parent = Split-Path -Parent ([IO.Path]::GetFullPath($Path))
  while ($parent) {
    Assert-NotReparsePoint -Path $parent
    $parent = Split-Path -Parent $parent
  }
}

function Assert-SafeTree {
  param([Parameter(Mandatory)] [string]$Path)

  Assert-SafeParents -Path $Path
  Assert-NotReparsePoint -Path $Path
  if (Test-Path -LiteralPath $Path -PathType Container) {
    foreach ($item in Get-ChildItem -LiteralPath $Path -Force -Recurse) {
      Assert-NotReparsePoint -Path $item.FullName
    }
  }
}

function Test-SharedLink {
  param([string]$Path, [string]$Target)

  $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
  if ($null -eq $item -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) {
    return $false
  }
  $destination = @($item.Target)
  if ($destination.Count -ne 1 -or -not $destination[0]) { return $false }
  $resolved = $destination[0]
  if (-not [IO.Path]::IsPathRooted($resolved)) {
    $resolved = Join-Path (Split-Path -Parent $Path) $resolved
  }
  $comparison = if ($env:OS -eq 'Windows_NT') { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
  return [string]::Equals(
    [IO.Path]::GetFullPath($resolved).TrimEnd('\', '/'),
    [IO.Path]::GetFullPath($Target).TrimEnd('\', '/'),
    $comparison
  )
}

$backupRoot = Join-Path $HOME (".agents/backups/my-engineering-workflow/" + [guid]::NewGuid().ToString('N'))
$backupIndex = 0
function Backup-ManagedPath {
  param([string]$Path)

  if ($null -eq (Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue)) { return }
  $script:backupIndex++
  $destination = Join-Path $backupRoot ("{0:D3}-{1}" -f $script:backupIndex, (Split-Path -Leaf $Path))
  New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
  # Copy first so a cross-volume migration keeps the original until backup succeeds.
  Copy-Item -LiteralPath $Path -Destination $destination -Recurse -Force
  Write-Host "Backup: $Path -> $destination"
  Remove-Item -LiteralPath $Path -Recurse -Force
}

function Sync-SkillDirectory {
  param(
    [Parameter(Mandatory)] [string]$Source,
    [Parameter(Mandatory)] [string]$TargetRoot,
    [Parameter(Mandatory)] [string]$Name,
    [switch]$IncludeCompat
  )

  if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
    throw "Skill source directory was not found: $Source"
  }
  $target = Join-Path $TargetRoot $Name
  Assert-ManagedChild -Root $TargetRoot -Child $target
  Assert-SafeTree -Path $target
  $expected = @{}
  foreach ($file in Get-ChildItem -LiteralPath $Source -File -Recurse -Force) {
    $relative = $file.FullName.Substring($Source.Length).TrimStart('\', '/')
    $expected[$relative] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
  }
  if ($IncludeCompat) {
    $expected[(Join-Path 'scripts' 'openspec_compat.py')] = (Get-FileHash -LiteralPath $compatSource -Algorithm SHA256).Hash
  }
  $actual = @(Get-ChildItem -LiteralPath $target -File -Recurse -Force -ErrorAction SilentlyContinue)
  $matchesSource = (Test-Path -LiteralPath $target -PathType Container) -and $actual.Count -eq $expected.Count
  foreach ($file in $actual) {
    $relative = $file.FullName.Substring($target.Length).TrimStart('\', '/')
    if (-not $expected.ContainsKey($relative) -or $expected[$relative] -ne (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash) {
      $matchesSource = $false
      break
    }
  }
  if ($matchesSource) { return }
  if ($PSCmdlet.ShouldProcess($target, "back up existing content and publish managed directory")) {
    Backup-ManagedPath -Path $target
    New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null
    Copy-Item -LiteralPath $Source -Destination $target -Recurse -Force
    if ($IncludeCompat) {
      $scripts = Join-Path $target 'scripts'
      New-Item -ItemType Directory -Force -Path $scripts | Out-Null
      Copy-Item -LiteralPath $compatSource -Destination (Join-Path $scripts 'openspec_compat.py') -Force
    }
  }
}

function Install-SharedLink {
  param([string]$Path, [string]$Target)

  if (Test-SharedLink -Path $Path -Target $Target) { return }
  if ($PSCmdlet.ShouldProcess($Path, "link skill to $Target")) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
    $linkType = if ($env:OS -eq 'Windows_NT') { 'Junction' } else { 'SymbolicLink' }
    New-Item -ItemType $linkType -Path $Path -Target $Target | Out-Null
  }
}

function Copy-ManagedFile {
  param(
    [Parameter(Mandatory)] [string]$Source,
    [Parameter(Mandatory)] [string]$Target,
    # Adaptor files can carry user edits (for example hand-added
    # external_directory entries). Keep a backup instead of silently replacing them.
    [switch]$BackupOnOverwrite
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
  Assert-SafeParents -Path $Target
  Assert-NotReparsePoint -Path $Target
  if ($PSCmdlet.ShouldProcess($Target, "install managed workflow file")) {
    if ($BackupOnOverwrite -and (Test-Path -LiteralPath $Target -PathType Leaf)) {
      $sameBytes = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash -eq
        (Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash
      if (-not $sameBytes) {
        Backup-ManagedPath -Path $Target
      }
    }
    New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Target -Force
  }
}

function Remove-LegacyManagedFile {
  param([Parameter(Mandatory)] [string]$Path)

  $targetRoot = Split-Path -Parent $Path
  Assert-ManagedChild -Root $targetRoot -Child $Path
  Assert-SafeParents -Path $Path
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
  Assert-SafeParents -Path $Path
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

$sharedSkills = Join-Path $HOME '.agents/skills'
$compatSource = Join-Path $repoRoot 'scripts\openspec_compat.py'
$legacyRoots = @()
$claudeLinkRoots = @()
if ($Harness -in @('Codex', 'Both', 'All')) {
  $legacyRoots += Join-Path $HOME '.codex/skills'
  if ($project) { $legacyRoots += Join-Path $project '.agents/skills' }
}
if ($Harness -in @('OMP', 'Both', 'All')) {
  $legacyRoots += Join-Path $ompUserRoot 'skills'
  if ($project) { $legacyRoots += Join-Path $project '.omp/skills' }
}
if ($Harness -in @('Pi', 'All')) {
  $legacyRoots += Join-Path $piUserRoot 'skills'
  if ($project) {
    $legacyRoots += Join-Path $project '.agents/skills'
    $legacyRoots += Join-Path $project '.pi/skills'
  }
}
# OpenCode discovers ~/.agents/skills and .agents/skills natively, so its own
# skills directory becomes a legacy copy once the shared tree is published.
if ($Harness -in @('OpenCode', 'All')) {
  $legacyRoots += Join-Path $opencodeUserRoot 'skills'
  if ($project) {
    $legacyRoots += Join-Path $project '.agents/skills'
    $legacyRoots += Join-Path $project '.opencode/skills'
  }
}
if ($Harness -in @('Claude', 'All')) {
  $claudeLinkRoots += Join-Path $HOME '.claude/skills'
  if ($project) { $claudeLinkRoots += Join-Path $project '.claude/skills' }
  $legacyRoots += $claudeLinkRoots
}
$legacyRoots = @($legacyRoots | Sort-Object -Unique | Where-Object {
  [IO.Path]::GetFullPath($_) -ne [IO.Path]::GetFullPath($sharedSkills)
})

# Preflight every managed skill before any migration. Never follow unknown links.
Assert-SafeParents -Path $backupRoot
Assert-NotReparsePoint -Path $backupRoot
foreach ($name in $skillNames) {
  $source = Join-Path $repoRoot "skills\$name"
  Assert-SafeTree -Path $source
  if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md') -PathType Leaf)) {
    throw "Skill source directory was not found: $source"
  }
  $target = Join-Path $sharedSkills $name
  Assert-SafeTree -Path $target
  foreach ($root in $legacyRoots) {
    $old = Join-Path $root $name
    Assert-SafeParents -Path $old
    if (-not (Test-SharedLink -Path $old -Target $target)) {
      Assert-SafeTree -Path $old
    }
  }
}
if (-not (Test-Path -LiteralPath $compatSource -PathType Leaf)) {
  throw "Managed source file was not found: $compatSource"
}
if ($Harness -in @('OMP', 'Both', 'All') -and -not (Test-Path -LiteralPath $workflowReviewGateSource -PathType Container)) {
  throw "Skill source directory was not found: $workflowReviewGateSource"
}
$managedFiles = @()
if ($Harness -in @('OMP', 'Both', 'All')) {
  $root = if ($project) { Join-Path $project '.omp' } else { $ompUserRoot }
  foreach ($fileName in $ompAgentNames) {
    $managedFiles += @{ Source = Join-Path $repoRoot ".omp/agents/$fileName"; Target = Join-Path $root "agents/$fileName" }
  }
  $managedFiles += @{ Source = Join-Path $repoRoot 'config/omp-workflow.yml'; Target = Join-Path $root 'engineering-workflow.yml' }
  $managedFiles += @{ Source = Join-Path $repoRoot 'scripts/start-omp.py'; Target = Join-Path $root 'start-engineering-workflow.py' }
  foreach ($path in @((Join-Path $root 'start-engineering-workflow.ps1'), (Join-Path $root 'config.yml'), (Join-Path $ompUserRoot 'config.yml'))) {
    Assert-SafeParents -Path $path
    Assert-NotReparsePoint -Path $path
  }
  Assert-SafeTree -Path (Join-Path $root 'extensions/workflow-review-gate')
  Assert-SafeTree -Path $workflowReviewGateSource
}
if ($Harness -in @('Claude', 'All')) {
  $root = if ($project) { Join-Path $project '.claude' } else { Join-Path $HOME '.claude' }
  foreach ($fileName in $claudeAgentNames) {
    $managedFiles += @{ Source = Join-Path $repoRoot "agents/$fileName"; Target = Join-Path $root "agents/$fileName" }
  }
  foreach ($fileName in $claudeCommandNames) {
    $managedFiles += @{ Source = Join-Path $repoRoot "commands/$fileName"; Target = Join-Path $root "commands/$fileName" }
  }
}
if ($Harness -in @('Pi', 'All')) {
  $root = if ($project) { Join-Path $project '.pi' } else { $piUserRoot }
  foreach ($fileName in $piAgentNames) {
    $managedFiles += @{ Source = Join-Path $repoRoot ".pi/agents/$fileName"; Target = Join-Path $root "agents/$fileName" }
  }
}
if ($Harness -in @('OpenCode', 'All')) {
  $root = if ($project) { Join-Path $project '.opencode' } else { $opencodeUserRoot }
  foreach ($fileName in $opencodeAgentNames) {
    $managedFiles += @{ Source = Join-Path $repoRoot ".opencode/agents/$fileName"; Target = Join-Path $root "agents/$fileName" }
  }
  foreach ($fileName in $opencodeCommandNames) {
    $managedFiles += @{ Source = Join-Path $repoRoot "commands/$fileName"; Target = Join-Path $root "commands/$fileName" }
  }
}
foreach ($file in $managedFiles) {
  if (-not (Test-Path -LiteralPath $file.Source -PathType Leaf)) {
    throw "Managed source file was not found: $($file.Source)"
  }
  Assert-SafeParents -Path $file.Target
  Assert-NotReparsePoint -Path $file.Target
}
foreach ($name in $skillNames) {
  Sync-SkillDirectory -Source (Join-Path $repoRoot "skills\$name") -TargetRoot $sharedSkills -Name $name `
    -IncludeCompat:($name -eq 'run-engineering-workflow')
}
foreach ($root in $legacyRoots) {
  foreach ($name in $skillNames) {
    $old = Join-Path $root $name
    $target = Join-Path $sharedSkills $name
    if (Test-SharedLink -Path $old -Target $target) {
      if ($claudeLinkRoots -notcontains $root -and $PSCmdlet.ShouldProcess($old, 'remove redundant shared skill link')) {
        # Directory.Delete removes only the link, never the shared target.
        [IO.Directory]::Delete($old)
      }
    } elseif ((Test-Path -LiteralPath $old) -and $PSCmdlet.ShouldProcess($old, 'back up legacy skill directory')) {
      Backup-ManagedPath -Path $old
    }
  }
}
foreach ($root in $claudeLinkRoots) {
  foreach ($name in $skillNames) {
    Install-SharedLink -Path (Join-Path $root $name) -Target (Join-Path $sharedSkills $name)
  }
}
if ($Harness -in @("OMP", "Both", "All")) {
  $ompRoot = if ($Scope -eq "Project") {
    Join-Path $project ".omp"
  } else {
    $ompUserRoot
  }

  $ompAgents = Join-Path $ompRoot "agents"
  $ompExtensions = Join-Path $ompRoot "extensions"


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
  if ($Scope -eq 'Project') {
    Add-OmpSkillWhitelist -Path (Join-Path $ompUserRoot 'config.yml') -Names $skillNames
  }
}

if ($Harness -in @("Claude", "All")) {
  $claudeRoot = if ($Scope -eq "Project") {
    Join-Path $project ".claude"
  } else {
    Join-Path $HOME ".claude"
  }

  $claudeAgents = Join-Path $claudeRoot "agents"
  $claudeCommands = Join-Path $claudeRoot "commands"


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

  $piAgents = Join-Path $piRoot "agents"


  foreach ($fileName in $piAgentNames) {
    Copy-ManagedFile `
      -Source (Join-Path $repoRoot ".pi\agents\$fileName") `
      -Target (Join-Path $piAgents $fileName)
  }
}

if ($Harness -in @("OpenCode", "All")) {
  $opencodeRoot = if ($Scope -eq "Project") {
    Join-Path $project ".opencode"
  } else {
    $opencodeUserRoot
  }

  $opencodeAgents = Join-Path $opencodeRoot "agents"
  $opencodeCommands = Join-Path $opencodeRoot "commands"

  # These files carry user-owned external_directory entries, so an overwrite is
  # recoverable through the shared backup directory.
  foreach ($fileName in $opencodeAgentNames) {
    Copy-ManagedFile `
      -Source (Join-Path $repoRoot ".opencode\agents\$fileName") `
      -Target (Join-Path $opencodeAgents $fileName) `
      -BackupOnOverwrite
  }

  foreach ($fileName in $opencodeCommandNames) {
    Copy-ManagedFile `
      -Source (Join-Path $repoRoot "commands\$fileName") `
      -Target (Join-Path $opencodeCommands $fileName) `
      -BackupOnOverwrite
  }
}

if ($Harness -in @("Codex", "Both", "All")) {
  # Codex has no markdown runtime agents. Older Trellis-era installs left agent
  # files behind; back up only those whose content still carries the Trellis
  # signature, and never touch any other file.
  $codexAgents = Join-Path $HOME ".codex\agents"
  foreach ($fileName in $codexLegacyAgentNames) {
    $legacy = Join-Path $codexAgents $fileName
    if (-not (Test-Path -LiteralPath $legacy -PathType Leaf)) { continue }
    Assert-SafeParents -Path $legacy
    Assert-NotReparsePoint -Path $legacy
    $body = [IO.File]::ReadAllText($legacy)
    if ($body -notmatch '^---\s' -or $body -notmatch '\.trellis/tasks/') { continue }
    if ($PSCmdlet.ShouldProcess($legacy, "back up stale Codex Trellis agent definition")) {
      Backup-ManagedPath -Path $legacy
    }
  }
}

$resultVerb = if ($WhatIfPreference) { "Planned" } else { "Installed" }
Write-Host "$resultVerb $($skillNames.Count) shared workflow skills at $sharedSkills; $Harness adapters at $Scope scope."
if ($Scope -eq "Project" -and $Harness -in @("OMP", "Both", "All")) {
  $startPrefix = if ($WhatIfPreference) { "After installation, start" } else { "Start" }
  $launcher = Join-Path $project ".omp\start-engineering-workflow.py"
  Write-Host "$startPrefix OMP with: python '$launcher' --project-path '$project'"
}
if ($Scope -eq "Project" -and $Harness -in @("Pi", "All")) {
  Write-Host "Start Pi from the trusted project root with: pi"
}
if ($Scope -eq "Project" -and $Harness -in @("OpenCode", "All")) {
  Write-Host "Start OpenCode from the trusted project root with: opencode"
}
if ($Harness -in @("Codex", "Both", "All")) {
  # Codex gets the shared skills only; this adapter does not establish native runtime agents.
  Write-Host "Codex adapter installs the shared skills only: no workflow agent files are installed for Codex, which does not establish native subagent support. Verify native subagent capability for the installed Codex client version."
}
