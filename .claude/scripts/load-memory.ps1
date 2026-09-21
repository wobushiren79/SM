# SessionStart Hook: inject the project memory index into the session context.
# Purpose: every teammate who clones this repo gets the .claude/memory/ files via git,
#          but Claude Code only auto-loads memory from the user home dir, NOT the repo.
#          This hook prints the repo memory index to stdout so the harness injects it
#          into the session context for everyone, deterministically.
# NOTE: keep this script ASCII-only. Windows PowerShell 5.1 reads BOM-less .ps1 as the
#       system ANSI codepage (GBK on zh-CN), which would corrupt non-ASCII source.
#       Chinese memory content flows in from MEMORY.md, read explicitly as UTF-8.

# Force UTF-8 stdout so Chinese memory content is not mojibake'd.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Resolve project root dynamically: this script lives in .claude/scripts/, two levels up.
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$memoryIndex = Join-Path $projectRoot ".claude/memory/MEMORY.md"

if (Test-Path $memoryIndex) {
    $content = Get-Content $memoryIndex -Raw -Encoding UTF8
    Write-Output "# Project collaboration memory index (from .claude/memory/MEMORY.md, shared via git)"
    Write-Output ""
    Write-Output "These are shared project memories. When a task relates to one of them,"
    Write-Output "use the Read tool to open .claude/memory/<file> for the full content first."
    Write-Output ""
    Write-Output $content
}
