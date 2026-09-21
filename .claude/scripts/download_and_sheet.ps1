param(
    [string]$UserId,
    [string]$ObjectId,
    [string]$AnimId,
    [string]$OutName,
    [int]$FrameCount = 16,
    [int]$Cols = 4,
    [int]$Rows = 4
)

$base     = "https://backblaze.pixellab.ai/file/pixellab-characters/objects"
# 动态推导项目根目录：脚本位于 .claude/scripts/，向上两级即项目根
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$outDir   = Join-Path $projectRoot "Assets\Out\$OutName"
$tmpDir   = "$outDir\_tmp_frames"

New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null

for ($i = 0; $i -lt $FrameCount; $i++) {
    $url  = "$base/$UserId/$ObjectId/animations/$AnimId/unknown/$i.png"
    $dest = "$tmpDir\$i.png"
    Invoke-WebRequest $url -OutFile $dest
    Write-Host "Frame $i OK"
}

Add-Type -AssemblyName System.Drawing

$frames = @()
for ($i = 0; $i -lt $FrameCount; $i++) {
    $frames += [System.Drawing.Image]::FromFile("$tmpDir\$i.png")
}

$fw = $frames[0].Width
$fh = $frames[0].Height
Write-Host "Frame size: ${fw}x${fh}"

$sheet = New-Object System.Drawing.Bitmap ($fw * $Cols), ($fh * $Rows)
$g = [System.Drawing.Graphics]::FromImage($sheet)

for ($i = 0; $i -lt $FrameCount; $i++) {
    $x = ($i % $Cols) * $fw
    $y = [math]::Floor($i / $Cols) * $fh
    $g.DrawImage($frames[$i], $x, $y, $fw, $fh)
}

$g.Dispose()
$sheetPath = "$outDir\${OutName}_4x4.png"
$sheet.Save($sheetPath, [System.Drawing.Imaging.ImageFormat]::Png)
$sheet.Dispose()
foreach ($f in $frames) { $f.Dispose() }

Remove-Item -Recurse -Force $tmpDir
Write-Host "Spritesheet saved: $sheetPath ($($fw*$Cols)x$($fh*$Rows)px, $FrameCount frames)"
