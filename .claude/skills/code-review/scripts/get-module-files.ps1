#!/usr/bin/env pwsh
# Find files in a specific module
param(
    [Parameter(Mandatory=$true)]
    [string]$ModuleName
)

# Common module path patterns
$searchPaths = @(
    "*/$ModuleName/*",
    "*/$ModuleName*",
    "$ModuleName/*",
    "$ModuleName*",
    "src/*/$ModuleName/*",
    "src/$ModuleName/*",
    "Assets/*/$ModuleName/*",
    "Assets/$ModuleName/*",
    "Scripts/*/$ModuleName/*",
    "Scripts/$ModuleName/*"
)

$foundFiles = @()

foreach ($pattern in $searchPaths) {
    $files = Get-ChildItem -Path . -Recurse -File -Filter "*.cs" -ErrorAction SilentlyContinue | 
        Where-Object { $_.FullName -like "*$ModuleName*" } |
        Select-Object -ExpandProperty FullName
    
    if ($files) {
        $foundFiles += $files
    }
}

# Remove duplicates and return relative paths
$uniqueFiles = $foundFiles | Select-Object -Unique | ForEach-Object { 
    $_.Substring((Get-Location).Path.Length + 1)
}

if (-not $uniqueFiles) {
    Write-Error "No files found for module: $ModuleName"
    exit 1
}

$uniqueFiles | ForEach-Object { Write-Output $_ }
