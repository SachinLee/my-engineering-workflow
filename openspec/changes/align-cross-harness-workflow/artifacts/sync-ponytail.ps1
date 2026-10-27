param([string]$UserHome = $env:USERPROFILE)
$ErrorActionPreference = 'Stop'
$source = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..\..\ponytail\skills'))
$destination = Join-Path $UserHome '.agents\skills'
$names = @('ponytail', 'ponytail-review', 'ponytail-audit', 'ponytail-debt', 'ponytail-gain', 'ponytail-help')
# Preflight all targets before creating any directory; existing content is user-owned.
foreach ($name in $names) {
    if (!(Test-Path -LiteralPath (Join-Path $source "$name\SKILL.md"))) { throw "Missing upstream skill: $name" }
    if (Test-Path -LiteralPath (Join-Path $destination $name)) { throw "Existing skill requires explicit comparison: $name" }
}
New-Item -ItemType Directory -Path $destination -Force | Out-Null
foreach ($name in $names) {
    Copy-Item -LiteralPath (Join-Path $source $name) -Destination (Join-Path $destination $name) -Recurse
    $expected = (Get-FileHash -LiteralPath (Join-Path $source "$name\SKILL.md")).Hash
    $actual = (Get-FileHash -LiteralPath (Join-Path $destination "$name\SKILL.md")).Hash
    if ($expected -ne $actual) { throw "Hash mismatch: $name" }
    Write-Output "Installed $name (SHA256 verified)"
}
