<#
.SYNOPSIS
  Cross-references git changes with agent/skill watched_files to flag which
  agents and skills need updating when their associated classes change.

.DESCRIPTION
  Reads watched_files from frontmatter of every .claude/agents/*.md and
  .claude/skills/*/SKILL.md, then compares against files changed in the
  working tree (git diff --name-only). Supports both exact file paths and
  directory prefixes (paths ending in /).

.PARAMETER BaseRef
  Git ref to diff against. Defaults to HEAD (unstaged + staged changes).
  Use "main" or "origin/main" to check against the main branch.

.PARAMETER StagedOnly
  Only check staged changes (git diff --cached).

.PARAMETER Json
  Output results as JSON instead of human-readable text.

.PARAMETER FailOnMatch
  Exit with non-zero code when any watched file has changed (for CI hooks).

.EXAMPLE
  .claude/scripts/check-watched.ps1
  # Checks working-tree changes against HEAD

.EXAMPLE
  .claude/scripts/check-watched.ps1 -BaseRef origin/main
  # Checks all changes on this branch vs origin/main

.EXAMPLE
  .claude/scripts/check-watched.ps1 -StagedOnly
  # Only checks staged changes (pre-commit hook)
#>

param(
    [string]$BaseRef = "HEAD",
    [switch]$StagedOnly,
    [switch]$Json,
    [switch]$FailOnMatch
)

$ErrorActionPreference = "Continue"
$claudeDir = Split-Path $PSScriptRoot -Parent
$agentsDir = Join-Path $claudeDir "agents"
$skillsDir = Join-Path $claudeDir "skills"

# ------------------------------------------------------------------
# 1. Collect changed files from git
# ------------------------------------------------------------------
$changedArgs = @("diff", "--name-only")
if ($StagedOnly) {
    $changedArgs += "--cached"
}
if ($BaseRef -ne "HEAD") {
    $changedArgs += $BaseRef
}

# -c core.fsmonitor=false 避免某些环境下 "bad fsmonitor version" 报错污染输出
$changedFiles = git -c core.autocrlf=false -c core.fsmonitor=false @changedArgs 2>$null
if (-not $changedFiles) { $changedFiles = @() }
$changedFiles = @($changedFiles | Where-Object { $_ -ne "" })

if (-not $changedFiles) {
    if ($Json) {
        Write-Output '{"changed_files":[],"affected_agents":[],"affected_skills":[]}'
    } else {
        Write-Output "No changed files detected."
    }
    exit 0
}

# Normalize paths (forward slashes, no trailing slash)
function Normalize-Path($p) {
    return ($p -replace '\\', '/').TrimEnd('/')
}

# git diff 返回的是【仓库根】相对路径；当项目位于仓库子目录时(本项目根=仓库根，
# 项目在 "Demon Lord Roguelike/" 子目录)，需去掉该前缀，才能与各 agent/skill
# 里【项目相对】的 watched_files 对齐，否则精确比对永远不命中。
$gitPrefix = git -c core.autocrlf=false -c core.fsmonitor=false rev-parse --show-prefix 2>$null
$gitPrefix = if ($gitPrefix) { Normalize-Path ([string]$gitPrefix) } else { "" }

$changedSet = [System.Collections.Generic.HashSet[string]]::new(
    [string[]]($changedFiles | ForEach-Object {
        $n = Normalize-Path $_
        if ($gitPrefix -and $n.StartsWith($gitPrefix + '/')) {
            $n = $n.Substring($gitPrefix.Length + 1)
        }
        $n
    })
)

# ------------------------------------------------------------------
# 2. Parse watched_files from a markdown file's YAML frontmatter
# ------------------------------------------------------------------
function Get-WatchedFiles($filePath) {
    $content = Get-Content $filePath -Raw -Encoding UTF8
    if (-not $content) { return @() }

    # Extract YAML frontmatter between --- delimiters.
    # (?s) 开启 Singleline，使 . 能匹配换行，否则多行 frontmatter 永远提取失败；
    # \r?\n 兼容 CRLF/LF 两种行尾。
    if ($content -match '(?s)^\s*---\r?\n(.*?)\r?\n---') {
        $yaml = $Matches[1]
        # Find watched_files line (不加 (?s)：逐行匹配列表项，避免 . 贪婪跨行吞掉后续键)
        if ($yaml -match 'watched_files:\s*\r?\n((?:[ \t]*-[ \t]*\S.*\r?\n?)*)') {
            $block = $Matches[1]
            $paths = @()
            foreach ($line in ($block -split "`n")) {
                $trimmed = $line.Trim()
                if ($trimmed -match '^-\s*(.+)$') {
                    $path = $Matches[1].Trim()
                    if ($path) {
                        # 仅统一斜杠，【保留末尾 /】：目录前缀项靠末尾 / 区分，
                        # 若用 Normalize-Path(会 TrimEnd '/') 会让目录匹配永远失效。
                        $paths += ($path -replace '\\', '/')
                    }
                }
            }
            return $paths
        }
    }
    return @()
}

# ------------------------------------------------------------------
# 3. Check if any changed file matches the watched paths
# ------------------------------------------------------------------
function Test-WatchedChanged($watchedPaths) {
    foreach ($watched in $watchedPaths) {
        $isDir = $watched.EndsWith('/')
        foreach ($changed in $changedSet) {
            if ($isDir) {
                if ($changed.StartsWith($watched)) {
                    return $true
                }
            } else {
                if ($changed -eq $watched) {
                    return $true
                }
            }
        }
    }
    return $false
}

# ------------------------------------------------------------------
# 4. Collect matching changed files per entry
# ------------------------------------------------------------------
function Get-MatchingFiles($watchedPaths) {
    # 不用 $matches：它是 PowerShell 内置自动变量(被 -match 复用)，自定义赋值有副作用
    $matched = @()
    foreach ($watched in $watchedPaths) {
        $isDir = $watched.EndsWith('/')
        foreach ($changed in $changedSet) {
            if ($isDir) {
                if ($changed.StartsWith($watched)) {
                    $matched += $changed
                }
            } else {
                if ($changed -eq $watched) {
                    $matched += $changed
                }
            }
        }
    }
    return ($matched | Select-Object -Unique)
}

# ------------------------------------------------------------------
# 5. Scan all agent and skill files
# ------------------------------------------------------------------
$affectedAgents = @()
$affectedSkills = @()

# Scan agents
if (Test-Path $agentsDir) {
    Get-ChildItem $agentsDir -Filter "*.md" | ForEach-Object {
        $watched = Get-WatchedFiles $_.FullName
        if ($watched.Count -gt 0 -and (Test-WatchedChanged $watched)) {
            $affectedAgents += [PSCustomObject]@{
                name   = $_.BaseName
                file   = $_.FullName
                matched = (Get-MatchingFiles $watched)
            }
        }
    }
}

# Scan skills
if (Test-Path $skillsDir) {
    Get-ChildItem $skillsDir -Directory | ForEach-Object {
        $skillFile = Join-Path $_.FullName "SKILL.md"
        if (Test-Path $skillFile) {
            $watched = Get-WatchedFiles $skillFile
            if ($watched.Count -gt 0 -and (Test-WatchedChanged $watched)) {
                $affectedSkills += [PSCustomObject]@{
                    name   = $_.Name
                    file   = $skillFile
                    matched = (Get-MatchingFiles $watched)
                }
            }
        }
    }
}

# ------------------------------------------------------------------
# 6. Output
# ------------------------------------------------------------------
if ($Json) {
    $result = @{
        changed_files    = @($changedSet)
        affected_agents  = @($affectedAgents | ForEach-Object { @{ name = $_.name; matched = @($_.matched) } })
        affected_skills  = @($affectedSkills | ForEach-Object { @{ name = $_.name; matched = @($_.matched) } })
    }
    $result | ConvertTo-Json -Depth 3 -Compress
} else {
    Write-Output "============================================"
    Write-Output " Agent/Skill Change Detection"
    Write-Output "============================================"
    Write-Output "Changed files: $($changedSet.Count)"

    if ($affectedAgents.Count -eq 0 -and $affectedSkills.Count -eq 0) {
        Write-Output ""
        Write-Output "No agents or skills need updating."
    } else {
        if ($affectedAgents.Count -gt 0) {
            Write-Output ""
            Write-Output "--- AGENTS needing update ($($affectedAgents.Count)) ---"
            foreach ($agent in $affectedAgents) {
                Write-Output ""
                Write-Output "  [$($agent.name)] $($agent.file)"
                foreach ($m in $agent.matched) {
                    Write-Output "    -> $m"
                }
            }
        }

        if ($affectedSkills.Count -gt 0) {
            Write-Output ""
            Write-Output "--- SKILLS needing update ($($affectedSkills.Count)) ---"
            foreach ($skill in $affectedSkills) {
                Write-Output ""
                Write-Output "  [$($skill.name)] $($skill.file)"
                foreach ($m in $skill.matched) {
                    Write-Output "    -> $m"
                }
            }
        }
    }
}

if ($FailOnMatch -and ($affectedAgents.Count -gt 0 -or $affectedSkills.Count -gt 0)) {
    exit 1
}
exit 0
