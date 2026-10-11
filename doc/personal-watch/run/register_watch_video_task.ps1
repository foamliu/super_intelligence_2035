<#
  register_watch_video_task.ps1
  personal-watch · **video** 线 —— 注册/更新 Windows 计划任务 `WatchVideoLoop`

  作用：让 `watch_video_loop.ps1` 在**无人登录**的情况下**开机自动启动**（镜像既有 `ComfyUI` 任务：
        BootTrigger + 延迟 + SYSTEM + Highest），之后由 loop 自己每小时唤醒。

  用法（**需管理员 PowerShell**）：
      # 默认：开机 +45s 启动（晚于 ComfyUI 的 +30s），以 SYSTEM 运行
      powershell -ExecutionPolicy Bypass -File .\register_watch_video_task.ps1
      # 额外每天 10:00 也触发一次（机器若已在运行）
      powershell -ExecutionPolicy Bypass -File .\register_watch_video_task.ps1 -AtHour 10
      # 以当前用户（S4U，无需密码、无人登录也能跑）运行 —— 若 SYSTEM 下环境有问题可用它
      powershell -ExecutionPolicy Bypass -File .\register_watch_video_task.ps1 -AsSystem:$false
      # 卸载
      powershell -ExecutionPolicy Bypass -File .\register_watch_video_task.ps1 -Unregister

  核验：
      Get-ScheduledTask -TaskName WatchVideoLoop | Format-List
      Start-ScheduledTask   -TaskName WatchVideoLoop     # 立即试跑一次
      Get-Content 'D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\video\logs\watch_video_loop.log' -Tail 20
#>
[CmdletBinding()]
param(
    [string]$TaskName   = 'WatchVideoLoop',
    [int]$BootDelaySec  = 45,
    [int]$AtHour        = -1,          # >=0 ⇒ 额外加一个「每天 AtHour:00」触发
    [bool]$AsSystem     = $true,       # $true ⇒ SYSTEM（镜像 ComfyUI）；$false ⇒ 当前用户 S4U
    [switch]$Unregister
)

$ErrorActionPreference = 'Stop'

# ── 0) 管理员自检 ──────────────────────────────────────────────────
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { throw '必须以**管理员**身份运行（注册计划任务需要提权）。' }

$RunDir = $PSScriptRoot
$Loop   = Join-Path $RunDir 'watch_video_loop.ps1'
$TaskMd = Join-Path $RunDir 'WATCH_VIDEO_TASK.md'

if ($Unregister) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "[ok] 已卸载计划任务: $TaskName" -ForegroundColor Green
    } else {
        Write-Host "[i] 计划任务不存在: $TaskName"
    }
    return
}

# ── 1) 前置自检 ────────────────────────────────────────────────────
foreach ($f in @($Loop, $TaskMd)) {
    if (-not (Test-Path -LiteralPath $f)) { throw "缺少文件: $f" }
}
Write-Host "[i] loop   : $Loop"
Write-Host "[i] taskMd : $TaskMd"

# ── 2) 动作：用 Windows PowerShell（无窗口、绕执行策略、跑完不退出前不回收）──
$arg = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}"' -f $Loop
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg -WorkingDirectory $RunDir

# ── 3) 触发器：开机（+延迟）；可选每天 AtHour 点 ─────────────────────
$triggers = @()
$boot = New-ScheduledTaskTrigger -AtStartup
try { $boot.Delay = [string]('PT{0}S' -f $BootDelaySec) } catch { Write-Warning "无法设置开机延迟：$($_.Exception.Message)" }
$triggers += $boot
if ($AtHour -ge 0) {
    $daily = New-ScheduledTaskTrigger -Daily -At ([datetime]::Today.AddHours($AtHour))
    $triggers += $daily
    Write-Host "[i] 额外触发器：每天 $($AtHour):00"
}

# ── 4) 身份：SYSTEM（镜像 ComfyUI）或 当前用户 S4U ──────────────────
if ($AsSystem) {
    $principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
    Write-Host "[i] 运行身份：SYSTEM（无人登录可跑；loop 内已把环境钉回 Administrator）"
} else {
    $principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:COMPUTERNAME, $env:USERNAME) -LogonType S4U -RunLevel Highest
    $who = "{0}\{1}" -f $env:COMPUTERNAME, $env:USERNAME
    Write-Host "[i] 运行身份：$who（S4U，无需密码）"
}

# ── 5) 设置：不因电池停、错过则补跑、单实例、不限时长、失败重启 3 次 ────
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# ── 6) 注册（-Force 覆盖同名）───────────────────────────────────────
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers `
    -Principal $principal -Settings $settings -Force | Out-Null

$t = Get-ScheduledTask -TaskName $TaskName
Write-Host ""
Write-Host "[ok] 已注册计划任务 '$TaskName'（State=$($t.State)）" -ForegroundColor Green
Write-Host "     立即试跑 : Start-ScheduledTask -TaskName $TaskName"
Write-Host "     看日志   : Get-Content '$(Join-Path $RunDir 'video\logs\watch_video_loop.log')' -Tail 20 -Wait"
Write-Host "     停止     : Stop-ScheduledTask -TaskName $TaskName"
Write-Host "     卸载     : powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Unregister"
