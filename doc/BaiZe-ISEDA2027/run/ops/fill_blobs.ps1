$R = 'D:\Users\Administrator\code\super_intelligence_2035'
$log = "$R\doc\Baize-ISEDA2027\run\ops\logs\fill_blobs.log"
function L($m) { Add-Content -Path $log -Value ("[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m) -Encoding utf8 }

$files = git -C $R diff --name-only HEAD 2>$null
$oids = @()
foreach ($f in $files) {
    $l = git -C $R ls-tree HEAD -- $f 2>$null
    if ($l) { $oids += ($l -split '\s+')[2] }
}
$oids = $oids | Select-Object -Unique
L "start: files=$($files.Count) oids=$($oids.Count)"

$i = 0; $bad = 0
foreach ($o in $oids) {
    $i++
    & git -C $R cat-file -e $o 2>$null
    if ($LASTEXITCODE -ne 0) {
        # 重试一次
        Start-Sleep -Seconds 1
        & git -C $R cat-file -e $o 2>$null
        if ($LASTEXITCODE -ne 0) { $bad++; L "MISS $o" }
    }
    if ($i % 10 -eq 0) { L "progress $i/$($oids.Count) bad=$bad" }
}
L "blob fill done: total=$($oids.Count) bad=$bad"

# 全部到位后更新工作树
& git -C $R reset --hard HEAD 2>&1 | Out-Null
$left = (git -C $R diff --name-only HEAD 2>$null | Measure-Object -Line).Lines
L "after reset: dirty=$left"
