$R = 'D:\Users\Administrator\code\super_intelligence_2035'
$log = "$R\doc\Baize-ISEDA2027\run\ops\logs\offline_fix.log"
function L($m) { Add-Content -Path $log -Value ("[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m) -Encoding utf8 }

L '=== offline worktree fix ==='
$files = git -C $R diff --name-only HEAD 2>$null
L ("dirty files: " + ($files | Measure-Object).Count)

$restored = 0; $skipped = 0
foreach ($f in $files) {
    $l = git -C $R ls-tree HEAD -- $f 2>$null
    if (-not $l) { continue }
    $o = ($l -split '\s+')[2]
    & git -C $R cat-file -e $o 2>$null
    if ($LASTEXITCODE -eq 0) {
        & git -C $R checkout -- $f 2>$null
        if ($LASTEXITCODE -eq 0) { $restored++ } else { $skipped++; & git -C $R update-index --assume-unchanged -- $f 2>$null }
    } else {
        $skipped++
        & git -C $R update-index --assume-unchanged -- $f 2>$null
    }
}
L ("restored=$restored skipped(assume-unchanged)=$skipped")
$st = (git -C $R status --porcelain 2>$null | Measure-Object -Line).Lines
L ("status lines after fix: $st")
