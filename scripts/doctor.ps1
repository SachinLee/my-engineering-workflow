param(
  [ValidateSet("User", "Project")]
  [string]$Scope = "Project",

  [ValidateSet("Codex", "OMP", "Claude", "Both", "All")]
  [string]$Harness = "Both",

  [string]$ProjectPath
)

$ErrorActionPreference = "Stop"
$errors = [Collections.Generic.List[string]]::new()
$warnings = [Collections.Generic.List[string]]::new()
$skillNames = @(
  "run-engineering-workflow",
  "clarify-requirements",
  "plan-solution",
  "review-implementation",
  "finish-with-evidence"
)

$ompQualitySkillNames = @(
  "tdd-workflow",
  "verification-loop",
  "security-review"
 )
if ($Scope -eq "Project") {
  if (-not $ProjectPath) {
    throw "ProjectPath is required when Scope is Project."
  }
  $project = (Resolve-Path -LiteralPath $ProjectPath).Path
  if (-not (Test-Path -LiteralPath (Join-Path $project ".trellis\workflow.md"))) {
    $errors.Add("Trellis workflow was not found under $project\.trellis.")
  }
} else {
  $project = $null
}

function Test-SkillSet {
  param([string]$Root, [string]$Label)
  foreach ($name in $skillNames) {
    $path = Join-Path $Root "$name\SKILL.md"
    if (-not (Test-Path -LiteralPath $path)) {
      $errors.Add("Missing $Label skill: $name")
    }
  }
}

if ($Harness -in @("Codex", "Both", "All")) {
  $codexRoot = if ($Scope -eq "Project") {
    Join-Path $project ".agents\skills"
  } else {
    Join-Path $HOME ".codex\skills"
  }
  Test-SkillSet -Root $codexRoot -Label "Codex"
}

if ($Harness -in @("OMP", "Both", "All")) {
  $ompCommand = Get-Command omp -ErrorAction SilentlyContinue
  if (-not $ompCommand) {
    $errors.Add("omp was not found on PATH.")
  }

  $ompRoot = if ($Scope -eq "Project") {
    Join-Path $project ".omp"
  } else {
    Join-Path $HOME ".omp\agent"
  }
  Test-SkillSet -Root (Join-Path $ompRoot "skills") -Label "OMP"

  $requiredAgents = @("workflow-planner", "workflow-reviewer")
  if ($Scope -eq "Project") {
    $requiredAgents += @("trellis-implement", "trellis-check")
  }
  foreach ($agent in $requiredAgents) {
    if (-not (Test-Path -LiteralPath (Join-Path $ompRoot "agents\$agent.md"))) {
      $errors.Add("Missing OMP agent: $agent")
    }
  }
  foreach ($agent in @("workflow-planner", "workflow-reviewer")) {
    $agentPath = Join-Path $ompRoot "agents\$agent.md"
    if (Test-Path -LiteralPath $agentPath -PathType Leaf) {
      $agentBody = Get-Content -Raw -LiteralPath $agentPath
      if ($agentBody -notmatch "Active task:") {
        $errors.Add("OMP agent is missing the Active task handoff contract: $agent")
      }
      if ($agent -eq "workflow-planner" -and -not ($agentBody -match "Assigned slice:" -and $agentBody -match "Phase:" -and $agentBody -match "Read:" -and $agentBody -match "Must preserve:")) {
        $errors.Add("OMP planner is missing bounded handoff fields: $agent")
      }
      if ($agent -eq "workflow-planner" -and $agentBody -notmatch "PLANNING_STATUS: INVALID") {
        $errors.Add("OMP planner is missing invalid-dispatch behavior: $agent")
      }
      if ($agent -eq "workflow-reviewer" -and -not ($agentBody -match "Assigned slice:" -and $agentBody -match "Phase:" -and $agentBody -match "Read:" -and $agentBody -match "Must preserve:" -and $agentBody -match "Review scope:" -and $agentBody -match "Evidence:")) {
        $errors.Add("OMP reviewer is missing bounded handoff fields: $agent")
      }
      if ($agent -eq "workflow-reviewer" -and $agentBody -notmatch "REVIEW_STATUS: INVALID") {
        $errors.Add("OMP reviewer is missing invalid-dispatch behavior: $agent")
      }
      if ($agent -eq "workflow-reviewer" -and $agentBody -match "tools:.*(?:write|edit)") {
        $errors.Add("OMP reviewer must remain read-only: $agent")
      }
    }
  }

  $overlay = Join-Path $ompRoot "engineering-workflow.yml"
  $launcher = Join-Path $ompRoot "start-engineering-workflow.py"
  if (-not (Test-Path -LiteralPath $launcher -PathType Leaf)) {
    $errors.Add("Missing OMP Python launcher: $launcher")
  }
  if (-not (Test-Path -LiteralPath $overlay)) {
    $errors.Add("Missing OMP workflow overlay: $overlay")
  } else {
    $body = Get-Content -Raw -LiteralPath $overlay
    foreach ($required in @("includeSkills", "workflow-planner", 'trellis-implement: "@task"', 'trellis-check: "@advisor"', "workflow-reviewer")) {
      if ($body -notmatch [regex]::Escape($required)) {
        $errors.Add("OMP overlay is missing required setting: $required")
      }
    }

    foreach ($skill in $ompQualitySkillNames) {
      if ($body -notmatch [regex]::Escape("- $skill")) {
        $errors.Add("OMP overlay is missing quality skill baseline: $skill")
      }
    }
    if ($body -notmatch "Context mode:") {
      $warnings.Add("OMP overlay does not declare its pointer-based task context strategy.")
    }
    if ($ompCommand) {
      $previousConfigFiles = $env:PI_CONFIG_FILES
      try {
        $env:PI_CONFIG_FILES = if ($previousConfigFiles) {
          "$previousConfigFiles$([IO.Path]::PathSeparator)$overlay"
        } else {
          $overlay
        }
        $rawConfig = & omp config list --json | Out-String
        if ($LASTEXITCODE -ne 0) {
          $errors.Add("OMP could not load the workflow overlay.")
        } else {
          try {
            $effective = $rawConfig | ConvertFrom-Json -AsHashtable
            $included = $effective["skills.includeSkills"].value
            foreach ($skill in $skillNames) {
              if ($skill -notin $included) {
                $errors.Add("Effective OMP skill whitelist is missing: $skill")
              }
            }
            foreach ($skill in $ompQualitySkillNames) {
              if ($skill -notin $included) {
                $errors.Add("Effective OMP skill whitelist is missing quality baseline: $skill")
              }
            }

            $agentModels = $effective["task.agentModelOverrides"].value
            foreach ($entry in @(
              @{ Name = "workflow-planner"; Role = "@plan" },
              @{ Name = "trellis-implement"; Role = "@task" },
              @{ Name = "trellis-check"; Role = "@advisor" },
              @{ Name = "workflow-reviewer"; Role = "@advisor" }
            )) {
              if ($agentModels[$entry.Name] -ne $entry.Role) {
                $errors.Add("Effective OMP role mismatch: $($entry.Name) should use $($entry.Role).")
              }
            }

            $modelRoles = $effective["modelRoles"].value
            foreach ($role in @("default", "plan", "task", "advisor", "slow")) {
              if (-not $modelRoles[$role]) {
                $errors.Add("OMP modelRoles does not define: $role")
              }
            }
            if ($modelRoles["task"] -eq $modelRoles["advisor"]) {
              $warnings.Add("OMP @task and @advisor resolve to the same model; review has a fresh context but not cross-model independence.")
            }
          } catch {
            $errors.Add("Could not parse effective OMP configuration: $($_.Exception.Message)")
          }
        }
      } finally {
        $env:PI_CONFIG_FILES = $previousConfigFiles
      }
    }
  }

  if ($Scope -eq "Project") {
    foreach ($upstream in @("trellis-before-dev", "tdd-workflow", "verification-loop")) {
      $roots = @(
        (Join-Path $project ".omp\skills"),
        (Join-Path $project ".agents\skills"),
        (Join-Path $HOME ".omp\agent\skills"),
        (Join-Path $HOME ".codex\skills")
      )
      $found = $roots | Where-Object { Test-Path -LiteralPath (Join-Path $_ "$upstream\SKILL.md") }
      if (-not $found) {
        $warnings.Add("Recommended upstream skill was not found: $upstream")
      }
    }
  }
}

if ($Harness -in @("Claude", "All")) {
  $claudeCommand = Get-Command claude -ErrorAction SilentlyContinue
  if (-not $claudeCommand) {
    $errors.Add("claude was not found on PATH.")
  } else {
    & claude --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
      $errors.Add("claude --version failed.")
    }
  }

  $claudeRoot = if ($Scope -eq "Project") {
    Join-Path $project ".claude"
  } else {
    Join-Path $HOME ".claude"
  }
  Test-SkillSet -Root (Join-Path $claudeRoot "skills") -Label "Claude"

  foreach ($agent in @("workflow-planner", "workflow-reviewer")) {
    if (-not (Test-Path -LiteralPath (Join-Path $claudeRoot "agents\$agent.md"))) {
      $errors.Add("Missing Claude agent: $agent")
    }
  }

  $commandPath = Join-Path $claudeRoot "commands\engineering-workflow.md"
  if (-not (Test-Path -LiteralPath $commandPath)) {
    $errors.Add("Missing Claude command: engineering-workflow")
  }

  if ($Scope -eq "Project") {
    foreach ($agent in @("trellis-implement", "trellis-check")) {
      if (-not (Test-Path -LiteralPath (Join-Path $claudeRoot "agents\$agent.md"))) {
        $errors.Add("Missing Trellis Claude agent: $agent. Run trellis init --claude or trellis update.")
      }
    }
  }
}

foreach ($warning in $warnings) {
  Write-Warning $warning
}
foreach ($errorMessage in $errors) {
  Write-Error $errorMessage
}

if ($errors.Count -gt 0) {
  exit 1
}

Write-Host "Workflow installation is healthy."
