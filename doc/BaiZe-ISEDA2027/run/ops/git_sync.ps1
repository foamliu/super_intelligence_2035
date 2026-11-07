<#
  git_sync.ps1 — 本仓 git 同步/自愈脚本（2026-11-07 运维）

  三个根因（详见 run/ops/GIT_SYNC_README.md）：
    1) 仓库是 blob:none 部分克隆 -> 每次 merge 拉 blob 慢、易超时
    2) 同一工作树被 robot loop / cline agent / 运维三方并发使用 -> index.lock 争用
    3) pack 碎片化 + 被打断 fetch 留下的 tmp_pack_* 垃圾

  用法：
    powershell -NoProfile -ExecutionPolicy Bypass -File git_sync.ps1              # 日常同步
    powershell -NoProfile -ExecutionPolicy Bypass -File git_sync.ps1 -Status      # 只体检
    powershell -NoProfile -ExecutionPolicy Bypass -File git_sync.ps1 -Maintenance # 维护（清垃圾+预取小blob+repack）
#>
[CmdletBinding()]
param(
    [switch]$Status,
    [switch]$Maintenance,
    [int]$Retry = 5,
    [string]$Repo = 'D:\Users\Administrator\code\super_intelligence_2035'
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

$GitDir = Join-Path $Repo '.git'
$LogDir = Join-Path $Repo 'doc\BaiZe-ISEDA2027\run\ops\logs'
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Force -Path $LogDir | Out-Null }
$LogFile = Join-Path $LogDir ("git_sync_{0}.log" -f (Get-Date -Format 'yyyyMMdd'))

function Write-Log([string]$msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $msg
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding utf8
}

$env:http_proxy  = 'http://172.19.92.25:13128'
$env:https_proxy = $env:http_proxy
$env:GIT_TERMINAL_PROMPT = '0'

function Test-GitBusy { return [bool](Get-Process git, git-remote-https, ssh -ErrorAction SilentlyContinue) }

# 只有"确定没有 git 进程"时才删锁/半途 rebase
function Clear-StaleState {
    if (Test-GitBusy) { Write-Log '  [clean] git 进程在跑，跳过清锁'; return $false }
    $cleared = $false
    foreach ($p in @("$GitDir\index.lock", "$GitDir\HEAD.lock", "$GitDir\shallow.lock")) {
        if (Test-Path $p) { Remove-Item -Force $p; Write-Log "  [clean] 删 $(Split-Path $p -Leaf)"; $cleared = $true }
    }
    foreach ($d in @("$GitDir\rebase-merge", "$GitDir\rebase-apply")) {
        if (Test-Path $d) { Remove-Item -Recurse -Force $d; Write-Log "  [clean] 删 $(Split-Path $d -Leaf)"; $cleared = $true }
    }
    $tmp = Get-ChildItem "$GitDir\objects\pack" -Filter 'tmp_pack_*' -ErrorAction SilentlyContinue
    if ($tmp) { $tmp | Remove-Item -Force; Write-Log "  [clean] 删 tmp_pack_* x$($tmp.Count)"; $cleared = $true }
    return $cleared
}


function Invoke-Git([string[]]$GitArgs, [string]$What) {
    $cmdline = 'git ' + ($GitArgs -join ' ') + ' 2>&1'
    for ($i = 1; $i -le $Retry; $i++) {
        $out = (& cmd /c $cmdline) -join "`n"
        $rc = $LASTEXITCODE
        if ($rc -eq 0) { Write-Log "  [$What] ok"; return $true }
        $msg = ($out -split "`n" | Where-Object { $_ -match 'fatal|error|Unable|rejected|失败|拒绝' } | Select-Object -First 2) -join ' | '
        if (-not $msg) { $msg = ($out -split "`n" | Where-Object { $_.Trim() } | Select-Object -First 2) -join ' | ' }
        Write-Log "  [$What] 第 $i 次失败 (rc=$rc) $msg"
        if ($out -match 'Unable to write index|index\.lock') { Clear-StaleState | Out-Null }
        if ($out -match 'rejected|fetch first') { & cmd /c 'git fetch origin main 2>&1' | Out-Null }
        if ($i -lt $Retry) { Start-Sleep -Seconds ([Math]::Min(2 * $i, 8)) }
    }
    return $false
}

Push-Location -LiteralPath $Repo
try {
    if ($Status) {
        Write-Log '===== STATUS ====='
        Write-Log ("  promisor=" + (& git config --get remote.origin.promisor) + "  filter=" + (& git config --get remote.origin.partialclonefilter))
        Write-Log ("  autocrlf=" + (& git config --get core.autocrlf) + "  pull.rebase=" + (& git config --get pull.rebase) + "  gc.auto=" + (& git config --get gc.auto))
        Write-Log ("  local : " + (& git log -1 --format='%h %s' 2>$null))
        Write-Log ("  origin: " + (& git log -1 --format='%h %s' origin/main 2>$null))
        Write-Log ("  ahead/behind: " + (& git rev-list --left-right --count HEAD...origin/main 2>$null))
        $packs = (Get-ChildItem "$GitDir\objects\pack" -Filter '*.pack' -ErrorAction SilentlyContinue).Count
        $tmp   = (Get-ChildItem "$GitDir\objects\pack" -Filter 'tmp_pack_*' -ErrorAction SilentlyContinue).Count
        $locks = (Get-ChildItem $GitDir -Filter '*.lock' -ErrorAction SilentlyContinue).Count
        Write-Log ("  packs=$packs tmp_packs=$tmp locks=$locks gitBusy=" + (Test-GitBusy))
        exit 0
    }

    if ($Maintenance) {
        Write-Log '===== MAINTENANCE ====='
        Clear-StaleState | Out-Null
        Write-Log '  [1/4] 预取小 blob（blob:limit=200k，一次性，可能较久）...'
        if (Invoke-Git @('fetch','--refetch','--filter=blob:limit=200k','origin') 'refetch') {
            & git config remote.origin.partialclonefilter 'blob:limit=200k' | Out-Null
            Write-Log '  [1/4] 已切为 blob:limit=200k'
        } else {
            Write-Log '  [1/4] refetch 失败，保留 blob:none（只是慢，不影响正确性）'
        }
        Write-Log '  [2/4] gc --prune=now ...'
        Invoke-Git @('gc','--prune=now','--quiet') 'gc' | Out-Null
        Write-Log '  [3/4] repack -a -d ...'
        Invoke-Git @('repack','-a','-d','-q') 'repack' | Out-Null
        & git config gc.auto '0' | Out-Null
        Write-Log '  [4/4] 完成，当前对象库：'
        & git count-objects -vH 2>&1 | ForEach-Object { Write-Log "    $_" }
        exit 0
    }

    Write-Log '===== SYNC ====='
    Clear-StaleState | Out-Null
    if (-not (Invoke-Git @('fetch','origin','main') 'fetch')) { Write-Log 'fetch 失败（网络/代理？）'; exit 1 }

    $ab = ((& git rev-list --left-right --count HEAD...origin/main 2>$null) -split "\s+") | Where-Object { $_ -ne '' }
    Write-Log ("  ahead=" + $ab[0] + " behind=" + $ab[1])
    if ([int]$ab[1] -gt 0) { Invoke-Git @('merge','--no-edit','origin/main') 'merge' | Out-Null }

    $ab = ((& git rev-list --left-right --count HEAD...origin/main 2>$null) -split "\s+") | Where-Object { $_ -ne '' }
    if ([int]$ab[0] -gt 0) { if (-not (Invoke-Git @('push','origin','main') 'push')) { Write-Log 'push 失败'; exit 1 } }
    Write-Log ("  结果: " + (& git rev-list --left-right --count HEAD...origin/main))
    exit 0
}
finally { Pop-Location }
