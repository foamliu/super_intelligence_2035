$R = 'D:\Users\Administrator\code\super_intelligence_2035'
$log = "$R\doc\Baize-ISEDA2027\run\ops\logs\resolve_index.log"
function L($m) { Add-Content -Path $log -Value ("[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m) -Encoding utf8 }

L '=== resolve index ==='
$u = (git -C $R ls-files -u | Measure-Object -Line).Lines
L "unmerged entries: $u"

# 1) 索引对齐到 HEAD 树（只读 tree，不拉 blob）
& git -C $R read-tree HEAD 2>&1 | Out-Null
L "read-tree rc=$LASTEXITCODE"

$u2 = (git -C $R ls-files -u | Measure-Object -Line).Lines
L "unmerged entries after read-tree: $u2"

# 2) 分类：能取到 blob 的直接 checkout；取不到的标记 assume-unchanged
$dirty = git -C $R diff --name-only HEAD 2>$null
L ("dirty files: " + ($dirty | Measure-Object).Count)
$present = New-Object System.Collections.Generic.List[string]
$missing = New-Object System.Collections.Generic.List[string]
foreach ($f in $dirty) {
    $l = git -C $R ls-tree HEAD -- $f 2>$null
    if (-not $l) { continue }
    $o = ($l -split '\s+')[2]
    & git -C $R cat-file -e $o 2>$null
    if ($LASTEXITCODE -eq 0) { $present.Add($f) } else { $missing.Add($f) }
}
L ("present=$($present.Count) missing=$($missing.Count)")

$p1 = "$env:TEMP\present.txt"; $p2 = "$env:TEMP\missing.txt"
$present | Set-Content $p1 -Encoding utf8
$missing | Set-Content $p2 -Encoding utf8

if ($present.Count -gt 0) {
    & git -C $R checkout --pathspec-from-file=$p1 2>&1 | Out-Null
    L "checkout rc=$LASTEXITCODE"
}
if ($missing.Count -gt 0) {
    & git -C $R update-index --assume-unchanged --pathspec-from-file=$p2 2>&1 | Out-Null
    L "assume-unchanged rc=$LASTEXITCODE"
}
$st = (git -C $R status --porcelain 2>$null | Measure-Object -Line).Lines
L "status lines: $st"
