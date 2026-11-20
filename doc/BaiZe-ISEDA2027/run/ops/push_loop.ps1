$ErrorActionPreference = 'Continue'
Set-Location 'D:\Users\Administrator\code\super_intelligence_2035'
$env:http_proxy  = 'http://172.19.92.25:13128'
$env:https_proxy = $env:http_proxy
$log = 'D:\Users\Administrator\code\super_intelligence_2035\doc\Baize-ISEDA2027\run\ops\logs\push_loop.log'
function L($m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m; Add-Content -Path $log -Value $l -Encoding utf8 }

for ($i = 1; $i -le 12; $i++) {
    L "=== try $i ==="
    & git fetch origin main --quiet 2>$null
    if ($LASTEXITCODE -ne 0) { L "fetch failed"; Start-Sleep -Seconds 3; continue }

    $tree = (& git merge-tree --write-tree HEAD origin/main 2>&1) | Select-Object -First 1
    if ($LASTEXITCODE -ne 0) { L "merge-tree CONFLICT: $tree"; break }
    L "tree=$tree"

    $msg = "Merge origin/main via merge-tree (worktree blob fill pending)"
    $commit = (& git commit-tree $tree -p HEAD -p origin/main -m $msg) | Select-Object -First 1
    if (-not $commit) { L "commit-tree failed"; break }
    & git update-ref refs/heads/main $commit
    L "main -> $commit"

    & git push origin main --quiet 2>$null
    if ($LASTEXITCODE -eq 0) { L "PUSH OK at try $i"; break }
    L "push rejected, retry"
    Start-Sleep -Seconds 2
}
L "loop end"
