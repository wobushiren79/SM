<#
.SYNOPSIS
  Hook helper: PreToolUse on Write/Edit. Blocks direct edits to auto-generated
  C# files, identified SOLELY by an in-file marker comment the code generator
  emits. No path-based heuristic.

.DESCRIPTION
  Reads PreToolUse stdin JSON, inspects tool_input.file_path.

  Detection:
  - Any '*Partial.cs'  -> allow (always hand-written, even if the bean is generated).
  - Not a '.cs' file   -> allow.
  - The target file on disk contains the token 'AUTO-GENERATED-DO-NOT-EDIT' near
    its top -> block. The generator (ExcelEditorWindow.CreateEntity +
    ScriptsTemplates/Excel_LanguageEntity.txt) stamps this into every generated
    *Bean.cs header. Path-independent and flexible: anything the generator marks
    is protected, regardless of location; anything without the marker (incl.
    hand-maintained beans under Assets/Scripts/Bean/** such as CreatureBean.cs and
    the MVCEditorWindow-scaffolded UserDataBean) is editable.
  - Everything else -> allow.

  The marker token is pure ASCII so it matches regardless of how Windows
  PowerShell 5.1 decodes the (UTF-8, possibly Chinese) file.

  NOTE: protection relies on the file actually carrying the marker. Excel-generated
  beans gain it on the next "generate entity" run; until regenerated they are NOT
  blocked here.
#>
$stdin = [Console]::In.ReadToEnd()
if (-not $stdin) { exit 0 }

try {
    $obj = $stdin | ConvertFrom-Json
    $filePath = $obj.tool_input.file_path
    if (-not $filePath) { exit 0 }

    $normalized = $filePath -replace '\\', '/'

    # '*Partial.cs' are always hand-written extensions -> allow.
    if ($normalized -match 'Partial\.cs$') { exit 0 }
    # Only .cs files are candidates.
    if ($normalized -notmatch '\.cs$') { exit 0 }
    # Must already exist on disk to inspect its header.
    if (-not (Test-Path -LiteralPath $filePath)) { exit 0 }

    $hasMarker = $false
    try {
        $head = Get-Content -LiteralPath $filePath -TotalCount 20 -ErrorAction Stop
        if ($head -match 'AUTO-GENERATED-DO-NOT-EDIT') { $hasMarker = $true }
    } catch { }

    if ($hasMarker) {
        $name = Split-Path $normalized -Leaf
        $partialPath = $normalized -replace 'Bean\.cs$', 'BeanPartial.cs'
        $partialName = Split-Path $partialPath -Leaf
        $reason = "BLOCKED: '$name' carries the AUTO-GENERATED-DO-NOT-EDIT marker and is auto-generated. " +
                  "Per CLAUDE.md, generated files must NOT be edited directly. " +
                  "Put extension methods, helper properties, or parsing logic in the sibling Partial (e.g. '$partialName') instead."
        [Console]::Error.WriteLine($reason)
        exit 2
    }
} catch {
    # Parse errors: do not block.
}
exit 0
