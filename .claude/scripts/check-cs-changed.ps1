<#
.SYNOPSIS
  Hook helper: PostToolUse on Write/Edit. When a C# file under Assets/
  has just been modified, runs check-watched.ps1 and reports which
  agents/skills' watched_files were affected.

.DESCRIPTION
  Reads PostToolUse stdin JSON, extracts the modified file path. If it's
  a C# file under Assets/, invokes check-watched.ps1 -Json against the
  working tree, then emits a systemMessage naming the affected Agents/Skills
  so the next turn can update them in sync. Stays silent when nothing matches.
#>
$stdin = [Console]::In.ReadToEnd()
if (-not $stdin) { exit 0 }

try {
    $obj = $stdin | ConvertFrom-Json
    $filePath = $obj.tool_input.file_path
    if (-not $filePath) { $filePath = $obj.tool_response.filePath }
    if (-not $filePath) { exit 0 }

    $normalized = $filePath -replace '\\', '/'
    if ($normalized -notmatch '(^|/)Assets/.*\.cs$') { exit 0 }

    # 取【项目相对】路径(从 Assets/ 起)，用于把结果收敛到“刚改的这个文件”，
    # 避免把整个工作树里其它未提交改动命中的 agent/skill 一并刷出来(告警疲劳)。
    # 用 IndexOf/Substring 而非 -replace '$1'：后者在 Windows PowerShell 5.1 按非
    # UTF-8 读取本文件时反向引用会失效导致结果为空，IndexOf 写法与编码无关更稳。
    $assetsIdx = $normalized.IndexOf('Assets/')
    $editedRel = if ($assetsIdx -ge 0) { $normalized.Substring($assetsIdx) } else { $normalized }

    $watchScript = Join-Path $PSScriptRoot 'check-watched.ps1'
    if (-not (Test-Path $watchScript)) { exit 0 }

    $json = & $watchScript -Json 2>$null
    if (-not $json) { exit 0 }

    $result = $json | ConvertFrom-Json
    # 仅保留 watched_files 命中了【本次编辑文件】的条目
    $agents = @($result.affected_agents | Where-Object { @($_.matched) -contains $editedRel })
    $skills = @($result.affected_skills | Where-Object { @($_.matched) -contains $editedRel })
    if ($agents.Count -eq 0 -and $skills.Count -eq 0) { exit 0 }

    $parts = @()
    if ($agents.Count -gt 0) {
        $parts += "Agents: " + (($agents | ForEach-Object { $_.name }) -join ', ')
    }
    if ($skills.Count -gt 0) {
        $parts += "Skills: " + (($skills | ForEach-Object { $_.name }) -join ', ')
    }
    $msg = "C# change hits watched_files of these Agents/Skills - consider syncing them: " + ($parts -join ' | ')
    $out = @{ systemMessage = $msg } | ConvertTo-Json -Compress
    Write-Output $out
} catch {
    # Silently ignore parse / invocation errors.
}
exit 0
