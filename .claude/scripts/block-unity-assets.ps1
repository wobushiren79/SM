<#
.SYNOPSIS
  Hook helper: PreToolUse on Write/Edit. Blocks direct edits to Unity
  serialized resource files, enforcing the CLAUDE.md rule that such files
  must be modified through Unity MCP (mcpforunityserver).

.DESCRIPTION
  Reads PreToolUse stdin JSON, inspects tool_input.file_path. If the target
  is a Unity serialized asset (.prefab/.unity/.mat/.anim/.controller/.asset/.meta),
  exits with code 2 to block the tool call and returns the reason on stderr.
  C# scripts and all other files pass through untouched.
#>
$stdin = [Console]::In.ReadToEnd()
if (-not $stdin) { exit 0 }

try {
    $obj = $stdin | ConvertFrom-Json
    $filePath = $obj.tool_input.file_path
    if (-not $filePath) { exit 0 }

    $normalized = $filePath -replace '\\', '/'
    if ($normalized -match '\.(prefab|unity|mat|anim|controller|asset|meta)$') {
        $ext = $Matches[1]
        $reason = "BLOCKED: Direct Write/Edit on Unity serialized asset (.$ext) is forbidden. " +
                  "Per CLAUDE.md, .prefab/.unity/.mat/.anim/.controller/.asset/.meta must be modified " +
                  "through Unity MCP (mcpforunityserver) via manage_scene / manage_gameobject / manage_asset."
        [Console]::Error.WriteLine($reason)
        exit 2
    }
} catch {
    # Parse errors: do not block.
}
exit 0
