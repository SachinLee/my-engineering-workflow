param(
  [ValidateSet("User", "Project")]
  [string]$Scope = "Project",

  [ValidateSet("Codex", "OMP", "Claude", "Pi", "Both", "All")]
  [string]$Harness = "Both",

  [string]$ProjectPath
)

$ErrorActionPreference = "Stop"
$doctor = Join-Path $PSScriptRoot "doctor.py"
if (-not (Test-Path -LiteralPath $doctor -PathType Leaf)) {
  throw "Python doctor was not found: $doctor"
}

$arguments = @($doctor, "--scope", $Scope, "--harness", $Harness)
if ($ProjectPath) {
  $arguments += @("--project-path", $ProjectPath)
}

if (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3 @arguments
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  & python @arguments
} else {
  throw "Python 3.9 or later was not found on PATH. Install Python, then run this command again."
}

exit $LASTEXITCODE
