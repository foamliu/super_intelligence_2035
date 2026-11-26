# PAUSE_STATUS.md — video 线暂停记录

> 维护：运维（人工）。每次「暂停 / 恢复」各追加一段，倒序在最上面。

## ⏸ 2026-10-23 21:45（用户直令）— 已暂停

| 项 | 状态 |
|:---|:---|
| 计划任务 `WatchVideoLoop` | **Disabled**（原为 Running；已先 `Stop-ScheduledTask` 再 `Disable-ScheduledTask`） |
| loop 进程 `watch_video_loop.ps1` | **已终止**（PID 3272，20:36:53 启动；无子进程） |
| 心跳 `video/logs/watch_video_loop.hb` | 停在 **21:14:24**（原定 22:00 整点唤醒，22:00 后未再唤醒 ⇒ 已验证暂停生效） |
| 上一轮 | 21:14:24 收口（round done in 2250s），当时已睡到 22:00 |
| ComfyUI（127.0.0.1:8188） | 渲染任务**已全部停止**；服务进程与计划任务**已一并停止/禁用**（见下节） |

## ⏹ 2026-10-23 22:0x（用户追加令）— ComfyUI 渲染任务已停

| 动作 | 结果 |
|:---|:---|
| `POST /interrupt` | HTTP 200 —— 在跑的那一条（prompt `53c10ad6…`）被中断（**未落盘成片**，ComfyUI 只在完成时写文件） |
| `POST /queue {"clear": true}` | 清空 pending |
| 复核 `GET /queue` | **running=0 / pending=0** ✅ |
| GPU（RTX 4090 Laptop 16GB） | 14665 MiB / 44% → **~5.3GB / 空闲**（仅模型常驻缓存，无计算） |
| 遗留生成器进程（`gen_ep06_*.py`） | 0 个 |

### 本次中断带来的进度变化（**恢复后必须按此续投**）

- EP06 落盘盘点（以磁盘为准）：短剧仓 `OUTPUT/06_情绪/videos/` **29** 镜 ＋ ComfyUI 输出 `E:\code\ComfyUI\output\video\` 本次新出 **13** 镜（**尚未回收进短剧仓**）＝ **42/54**。
- **未渲染（需要重投）12 镜**：`41, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54`。
- 恢复第一轮顺序：① 先把 `E:\code\ComfyUI\output\video\EP06_*.mp4` 里这 13 个回收/改名进 `OUTPUT/06_情绪/videos/`（否则会被判「未出片」重复投）→ ② 用 `--skip-existing` 只补投上面 12 镜 → ③ 54 镜齐后跑字幕 + 合成。

## ⏹ 2026-10-23 22:1x（用户追加令）— ComfyUI 服务本身也已停止

| 项 | 状态 |
|:---|:---|
| 计划任务 `ComfyUI`（SYSTEM · 开机自启） | `Stop-ScheduledTask` → **`Disable-ScheduledTask`**，State = **Disabled**（重启也不会自动拉起） |
| ComfyUI 进程 | 已终止：venv launcher **PID 7148** + 其子进程 **PID 7084**（二者是同一实例，**非** BLOCKERS #9 说的「重复进程」） |
| 端口 8188 | 已关闭（`TcpTestSucceeded = False`） |
| GPU（RTX 4090 Laptop） | 5294 MiB → **~2210 MiB**（余量为 Chrome/游戏等无关进程；ComfyUI 显存已全部释放） |
| 输出文件 | `E:\code\ComfyUI\output\video\EP06_*.mp4` **13 个新片原样保留**，未删未动 |

**恢复 ComfyUI（video 线恢复前必须做）**
```powershell
Enable-ScheduledTask -TaskName 'ComfyUI' | Out-Null
Start-ScheduledTask  -TaskName 'ComfyUI'
# 等 ~40–90s 让 8188 起来并加载模型
curl.exe -s -o NUL -w "http=%{http_code}`n" http://127.0.0.1:8188/system_stats
```

**未做的事（有意保留）**
- 未动短剧仓工作区与任何已出片视频（`OUTPUT/06_情绪/videos/` 29 镜原样）。
- 未删 `E:\code\ComfyUI\output\video\` 里本次新出的 13 个 mp4（是有效产出，恢复时回收）。
- 未改 `watch_video_loop.ps1` 与 `WATCH_VIDEO_TASK.md`。

**恢复方式（两条都要做，顺序不能反）**
```powershell
# ① 先起 ComfyUI（video 线干活依赖它），等 8188 就绪
Enable-ScheduledTask -TaskName 'ComfyUI' | Out-Null
Start-ScheduledTask  -TaskName 'ComfyUI'
# ② 再起 video agent
Enable-ScheduledTask -TaskName 'WatchVideoLoop' | Out-Null
Start-ScheduledTask  -TaskName 'WatchVideoLoop'
```
（或手动前台跑一次：`powershell -NoProfile -ExecutionPolicy Bypass -File <run>\watch_video_loop.ps1`）

**暂停时的进度快照（以磁盘为准复核过）**
- **EP06《情绪》= 42/54**：短剧仓 `OUTPUT/06_情绪/videos/` **29** 镜（最新 mtime 2026-10-18）+ ComfyUI 输出 `E:\code\ComfyUI\output\video\` 新出 **13** 镜（2026-10-23 20:3x–22:00，**未回收**）。
- **未渲染 12 镜**：`41, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54`。
- 已成片七章：13_外骨骼 48/48、18_暖阳 54/54、01_晨钟 54/54、02_经验 55/55、03_种子 52/52、04_棋子 55/55、05_临界点 55/55（成片 295.51s）。
