<#
  watch_video_loop.ps1
  personal-watch · **video agent** 自动推进循环（Windows 11 本机 · 无人值守）

  干什么：每小时（对齐整点）唤醒一次 → 读 `WATCH_VIDEO_TASK.md`（全文 = prompt）→ 交给 `cline`
          （工作目录 = 短剧项目仓）→ 两个仓各做一次兜底 git 同步（fetch / pull --rebase --autostash / push）。

  与别的线为何不同：本线跑在 **Windows 本机**（不是 Linux VM），由【计划任务】在**开机后**自动拉起
          （无人登录）⇒ 本脚本把「用户环境」钉回 Administrator（镜像 `ComfyUI` 任务的 SYSTEM 做法），
          并用绝对路径调用 `cline` + 显式 `--config/--data-dir`（否则 SYSTEM 下找不到 MCP/凭据配置）。

  启动（见 register_watch_video_task.ps1）：
      powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File <本脚本>
  手动前台调试：
      powershell -NoProfile -ExecutionPolicy Bypass -File <本脚本> -Once

  停止：
      Stop-ScheduledTask -TaskName WatchVideoLoop
#>
[CmdletBinding()]
param(
    [int]$IntervalSec = 3600,          # 唤醒间隔（秒）；默认每小时（**对齐整点**）
    [int]$ClineTimeout = 3300,         # 单次 cline 上限（秒）≈ 55 min（留出 git 同步时间）
    [string]$Model = '',               # 空 ⇒ 用 cline 已配置的默认模型
    [string]$Thinking = 'medium',      # none|low|medium|high|xhigh（空 = provider 默认）
    [switch]$Once,                     # 只跑一轮后退出（调试）
    [switch]$DryRun                    # 不调用 cline（只走日志/心跳/git 同步；用于安全自检）
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

# ── 1) 路径锚点 ─────────────────────────────────────────────────────────────
$RunDir   = $PSScriptRoot
$TaskMd   = Join-Path $RunDir 'WATCH_VIDEO_TASK.md'
$MemoryMd = Join-Path $RunDir 'MEMORY_VIDEO.md'
$DailyDir = Join-Path $RunDir 'daily-memories-video'
$VideoDir = Join-Path $RunDir 'video'
$LogDir   = Join-Path $VideoDir 'logs'
$LogFile  = Join-Path $LogDir 'watch_video_loop.log'
$HbFile   = Join-Path $LogDir 'watch_video_loop.hb'
$ClineOut = Join-Path $LogDir 'watch_video_cline_last.log'

$PWRepo    = 'D:\Users\Administrator\code\super_intelligence_2035'
$DramaRepo = 'D:\Users\Administrator\code\super_intelligence_2035_short_drama'
# 本记录仓里**只允许兜底提交**这些（video 线自己的文件）
$PWAddPaths = @(
    'doc/personal-watch/run/MEMORY_VIDEO.md',
    'doc/personal-watch/run/daily-memories-video',
    'doc/personal-watch/run/video'
)

# ── 2) cline 锚点（绝对路径，SYSTEM 下也稳）────────────────────────────────
$ClineCmd  = 'C:\Users\Administrator\AppData\Roaming\npm\cline.cmd'
$ClineCfg  = 'C:\Users\Administrator\.cline'
$ClineData = 'C:\Users\Administrator\.cline\data'

# ── 3) 环境锚点：以 SYSTEM 运行时把用户环境钉回 Administrator ────────────────
$AdminHome = 'C:\Users\Administrator'
if ($env:USERPROFILE -ne $AdminHome) {
    $env:USERPROFILE  = $AdminHome
    $env:HOME         = $AdminHome
    $env:APPDATA      = Join-Path $AdminHome 'AppData\Roaming'
    $env:LOCALAPPDATA = Join-Path $AdminHome 'AppData\Local'
    $env:TEMP         = Join-Path $AdminHome 'AppData\Local\Temp'
    $env:TMP          = $env:TEMP
}
$env:PATH = (@(
    (Join-Path $AdminHome 'AppData\Roaming\npm'),   # cline
    'C:\Program Files\nodejs',                      # node
    'D:\Python310'                                  # python（MCP/脚本用）
) + $env:PATH) -join ';'
$env:PYTHONIOENCODING = 'utf-8'

New-Item -ItemType Directory -Force -Path $LogDir, $DailyDir, $VideoDir | Out-Null

function Write-Log([string]$m) {
    $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
    try { Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8 } catch {}
    Write-Host $line
}
function Touch-Hb() { try { Set-Content -LiteralPath $HbFile -Value (Get-Date -Format o) -Encoding UTF8 } catch {} }

# ── 4) 单仓兜底 git 同步（pull --rebase --autostash → 只加指定文件 → commit → push）──
function Sync-Repo {
    param(
        [string]$Repo,
        [string[]]$AddPaths = @(),
        [string]$Prefix = 'video'
    )
    if (-not (Test-Path -LiteralPath $Repo)) { Write-Log "  [git] repo missing: $Repo"; return }
    Write-Log "  [git] sync: $Repo"
    Push-Location -LiteralPath $Repo
    try {
        & git fetch origin --quiet 2>$null
        if ($LASTEXITCODE -ne 0) { Write-Log "  [git] fetch FAILED (exit $LASTEXITCODE; network?) - skip repo"; return }

        & git pull --rebase --autostash origin main --quiet 2>$null
        if ($LASTEXITCODE -ne 0) { Write-Log "  [git] pull FAILED (exit $LASTEXITCODE) - continue" }

        foreach ($p in $AddPaths) {
            if (Test-Path -LiteralPath (Join-Path $Repo $p)) { & git add -- $p 2>$null }
        }
        $staged = (& git diff --cached --name-only 2>$null)
        if ($staged) {
            & git -c core.quotepath=false commit -q -m "$Prefix auto-sync $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 2>$null
            Write-Log "  [git] committed $(@($staged).Count) file(s) (exit $LASTEXITCODE)"
        }
        $ahead = (& git rev-list --count origin/main..HEAD 2>$null)
        if ($ahead -and [int]$ahead -gt 0) {
            & git push origin main --quiet 2>$null
            Write-Log "  [git] pushed (ahead=$ahead -> 0, exit $LASTEXITCODE)"
        } else {
            Write-Log "  [git] nothing to push"
        }
    } catch {
        Write-Log "  [git] ERROR: $($_.Exception.Message)"
    } finally {
        Pop-Location
    }
}

# ── 5) 启动横幅（供秒级核验"跑的是哪种模式"）──────────────────────────────
Write-Log "===== watch_video_loop started (pid=$PID) ====="
Write-Log "  runDir     : $RunDir"
Write-Log "  task book  : $TaskMd"
Write-Log "  drama repo : $DramaRepo"
Write-Log "  cline      : $ClineCmd (config=$ClineCfg)"
Write-Log "  interval   : $IntervalSec s（对齐整点）· cline timeout = $ClineTimeout s"
Write-Log "  USERPROFILE: $env:USERPROFILE"
Touch-Hb

# ── 6) 主循环 ───────────────────────────────────────────────────────────────
while ($true) {
    $roundStart = Get-Date
    Write-Log "[loop] wake up, invoking cline ... [$($roundStart.ToString('yyyy-MM-dd HH:mm:ss'))]"
    Touch-Hb

    if (Test-Path -LiteralPath $TaskMd) {
        $prompt = Get-Content -LiteralPath $TaskMd -Raw -Encoding UTF8
        if (-not $prompt) { Write-Log "[loop] task book empty" }
        if ($prompt.Length -gt 20000) { Write-Log "[loop] WARN: task book very long ($($prompt.Length) chars)" }

        $clineArgs = @(
            '-c', $DramaRepo,
            '--auto-approve', 'true',
            '--config', $ClineCfg,
            '--data-dir', $ClineData,
            '-t', "$ClineTimeout"
        )
        if ($Model)    { $clineArgs += @('-m', $Model) }
        if ($Thinking) { $clineArgs += @('--thinking', $Thinking) }
        $clineArgs += $prompt

        if ($DryRun) {
            Write-Log "[loop] DRY-RUN: skip cline invocation"
        } else {
            try {
                & $ClineCmd @clineArgs 2>&1 | Tee-Object -FilePath $ClineOut | Out-Null
                Write-Log "[loop] cline returned (exit $LASTEXITCODE); out=$ClineOut"
            } catch {
                Write-Log "[loop] cline FAILED: $($_.Exception.Message)"
            }
        }
    } else {
        Write-Log "[loop] TASK book missing: $TaskMd"
    }

    # 兜底 git 同步（本记录仓：只加 video 线文件；短剧仓：agent 自己 commit，loop 只 pull+push）
    Sync-Repo -Repo $PWRepo    -AddPaths $PWAddPaths -Prefix 'video'
    Sync-Repo -Repo $DramaRepo -AddPaths @()         -Prefix 'video'

    Touch-Hb
    $dur = [int]((Get-Date) - $roundStart).TotalSeconds
    Write-Log "[loop] round done in ${dur}s"

    if ($Once) { Write-Log "[loop] -Once -> exit"; break }

    # 对齐整点：下一个整点（若已过/太近则顺延一小时），至少 60s
    $next = (Get-Date).Date.AddHours((Get-Date).Hour + 1)
    while (($next - (Get-Date)).TotalSeconds -lt 120) { $next = $next.AddHours(1) }
    $sleep = [int](($next - (Get-Date)).TotalSeconds)
    Write-Log "[loop] next wake = $($next.ToString('yyyy-MM-dd HH:mm')) (in $sleep s)"
    Start-Sleep -Seconds $sleep
    Touch-Hb
}

