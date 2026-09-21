param(
    [string]$FramesDir,
    [string]$Output
)

Add-Type -AssemblyName System.Drawing

# 动态推导项目根目录：脚本位于 .claude/scripts/，向上两级即项目根
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$outDir = Join-Path $projectRoot "Assets\Out"

# 参数缺省时回退到项目内默认路径
$framesDir = if ($FramesDir) { $FramesDir } else { Join-Path $outDir "meteorite_frames" }
$output = if ($Output) { $Output } else { Join-Path $outDir "meteorite_fall_4x4.png" }
$cols = 4
$rows = 4
$frameCount = 16

$frames = @()
for ($i = 0; $i -lt $frameCount; $i++) {
    $path = Join-Path $framesDir "$i.png"
    $frames += [System.Drawing.Image]::FromFile($path)
}

$fw = $frames[0].Width
$fh = $frames[0].Height
Write-Host "Frame size: ${fw}x${fh}"

$sheet = New-Object System.Drawing.Bitmap ($fw * $cols), ($fh * $rows)
$g = [System.Drawing.Graphics]::FromImage($sheet)

for ($i = 0; $i -lt $frameCount; $i++) {
    $x = ($i % $cols) * $fw
    $y = [math]::Floor($i / $cols) * $fh
    $g.DrawImage($frames[$i], $x, $y, $fw, $fh)
}

$g.Dispose()
$sheet.Save($output, [System.Drawing.Imaging.ImageFormat]::Png)
$sheet.Dispose()
foreach ($f in $frames) { $f.Dispose() }

Write-Host "Saved: $output ($($fw*$cols)x$($fh*$rows)px, $frameCount frames)"
