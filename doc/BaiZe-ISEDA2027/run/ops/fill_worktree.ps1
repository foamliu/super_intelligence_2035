$R = 'D:\Users\Administrator\code\super_intelligence_2035'
$log = "$R\doc\Baize-ISEDA2027\run\ops\logs\fill_worktree.log"
function L($m) { Add-Content -Path $log -Value ("[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m) -Encoding utf8 }

L '=== fill-worktree start ==='
for ($i = 1; $i -le 40; $i++) {
    $dirty = (git -C $R diff --name-only HEAD 2>$null | Measure-Object -Line).Lines
    if ($dirty -eq 0) { L "clean at try $i"; break }
    L "try $i (dirty=$dirty)"
    $p = Start-Process -FilePath 'git' -ArgumentList '-C', $R, 'reset', '--hard', 'HEAD' -PassThru -WindowStyle Hidden -RedirectStandardOutput "$env:TEMP\rst.out" -RedirectStandardError "$env:TEMP\rst.err"
    if (-not $p.WaitForExit(25000)) {
        try { $p.Kill() } catch {}
        Get-Process git, ssh -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        $lock = "$R\.git\index.lock"
        if (-not (Get-Process git -ErrorAction SilentlyContinue) -and (Test-Path $lock)) { Remove-Item -Force $lock; L '  removed stale index.lock' }
        L "  timeout -> killed, retry"
    } else {
        L "  reset rc=$($p.ExitCode)"
        $err = Get-Content "$env:TEMP\rst.err" -Raw -ErrorAction SilentlyContinue
        if ($err) { L ("  err: " + ($err -split "`n" | Select-Object -First 1)) }
        Start-Sleep -Seconds 1
    }
}
$dirty = (git -C $R diff --name-only HEAD 2>$null | Measure-Object -Line).Lines
L "=== done: dirty=$dirty ==="
