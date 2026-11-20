$R = 'D:\Users\Administrator\code\super_intelligence_2035'
$log = "$R\doc\Baize-ISEDA2027\run\ops\logs\fill_blobs2.log"
function L($m) { Add-Content -Path $log -Value ("[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m) -Encoding utf8 }

L '=== per-object fill start ==='
for ($pass = 1; $pass -le 4; $pass++) {
    $files = git -C $R diff --name-only HEAD 2>$null
    if (-not $files) { L ("pass {0}: clean" -f $pass); break }
    $oids = @(); $map = @{}
    foreach ($f in $files) {
        $l = git -C $R ls-tree HEAD -- $f 2>$null
        if ($l) { $o = ($l -split '\s+')[2]; $oids += $o; $map[$o] = $f }
    }
    $oids = $oids | Select-Object -Unique
    L ("pass {0}: files={1} oids={2}" -f $pass, $files.Count, $oids.Count)
    $miss = 0
    foreach ($o in $oids) {
        if (Test-Path "$R\.git\index.lock") { Remove-Item -Force "$R\.git\index.lock" -ErrorAction SilentlyContinue }
        $p = Start-Process -FilePath 'cmd' -ArgumentList '/c',("git -C `"$R`" cat-file blob $o > NUL 2>NUL") -PassThru -WindowStyle Hidden
        if (-not $p.WaitForExit(120000)) {
            try { $p.Kill() } catch {}
            Get-Process git, ssh -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
            $miss++
            L "  TIMEOUT $($map[$o])"
        } elseif ($p.ExitCode -ne 0) {
            $miss++
            L "  MISS $($map[$o])"
        }
        if (Test-Path "$R\.git\index.lock") { Remove-Item -Force "$R\.git\index.lock" -ErrorAction SilentlyContinue }
    }
    L "pass $pass done: missing=$miss"
    if ($miss -eq 0) { break }
    Start-Sleep -Seconds 3
}
$dirty = (git -C $R diff --name-only HEAD 2>$null | Measure-Object -Line).Lines
L "=== fill done: dirty=$dirty ==="
