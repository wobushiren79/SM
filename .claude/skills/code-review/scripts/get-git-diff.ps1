#!/usr/bin/env pwsh
# Get uncommitted git changes

# Check if we're in a git repository
$gitRoot = git rev-parse --show-toplevel 2>$null
if (-not $gitRoot) {
    Write-Error "Not a git repository"
    exit 1
}

# Get staged changes
$staged = git diff --cached --name-only 2>$null

# Get unstaged changes  
$unstaged = git diff --name-only 2>$null

# Get untracked files
$untracked = git ls-files --others --exclude-standard 2>$null

# Combine all changes
$allFiles = @()
if ($staged) { $allFiles += $staged }
if ($unstaged) { $allFiles += $unstaged }
if ($untracked) { $allFiles += $untracked }

# Remove duplicates and filter code files
$codeExtensions = @('.cs', '.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.go', '.rs', '.cpp', '.c', '.h', '.hpp', '.swift', '.kt', '.php', '.rb')
$uniqueFiles = $allFiles | Select-Object -Unique | Where-Object { 
    $ext = [System.IO.Path]::GetExtension($_).ToLower()
    $codeExtensions -contains $ext
}

if (-not $uniqueFiles) {
    Write-Host "No code files with uncommitted changes found." -ForegroundColor Yellow
    exit 0
}

# Output the list of changed files
$uniqueFiles | ForEach-Object { Write-Output $_ }
