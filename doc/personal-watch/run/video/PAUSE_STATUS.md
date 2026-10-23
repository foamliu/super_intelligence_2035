# PAUSE_STATUS.md — video 线暂停记录

> 维护：运维（人工）。每次「暂停 / 恢复」各追加一段，倒序在最上面。

## ⏸ 2026-10-23 21:45（用户直令）— 已暂停

| 项 | 状态 |
|:---|:---|
| 计划任务 `WatchVideoLoop` | **Disabled**（原为 Running；已先 `Stop-ScheduledTask` 再 `Disable-ScheduledTask`） |
| loop 进程 `watch_video_loop.ps1` | **已终止**（PID 3272，20:36:53 启动；无子进程） |
| 心跳 `video/logs/watch_video_loop.hb` | 停在 **21:14:24**（原定 22:00 整点唤醒，22:00 后未再唤醒 ⇒ 已验证暂停生效） |
| 上一轮 | 21:14:24 收口（round done in 2250s），当时已睡到 22:00 |
| ComfyUI（127.0.0.1:8188） | **未停**，仍在渲染：running 1 / pending 12（EP06 剩余镜头继续出片，不再有新的投递） |

**未做的事（有意保留）**
- 未动短剧仓工作区与任何已出片视频（`OUTPUT/06_情绪/videos/` 原样）。
- 未清理 ComfyUI 队列（如需一并暂停渲染，见下方「恢复/追加操作」）。
- 未改 `watch_video_loop.ps1` 与 `WATCH_VIDEO_TASK.md`。

**恢复方式（人工，一条即可）**
```powershell
Enable-ScheduledTask -TaskName 'WatchVideoLoop' | Out-Null
Start-ScheduledTask  -TaskName 'WatchVideoLoop'
```
（或手动前台跑一次：`powershell -NoProfile -ExecutionPolicy Bypass -File <run>\watch_video_loop.ps1`）

**追加操作（可选）**
- 只要停渲染、不删结果：`POST http://127.0.0.1:8188/interrupt`（停当前）＋ `POST /queue` with `{"clear":true}`（清 pending）。
- 停 ComfyUI 服务本身：计划任务 `ComfyUI`（SYSTEM 自启）→ `Stop-ScheduledTask -TaskName 'ComfyUI'`。

**暂停时的进度快照（取自 MEMORY_VIDEO.md）**
- EP06《情绪》54 镜：本轮唤醒时 29/54 落盘，补投 25 镜；至暂停时队列剩 **running 1 / pending 12**（即约 **41/54** 镜已出，剩 ~13 镜在渲染）。
- 已成片七章：13_外骨骼 48/48、18_暖阳 54/54、01_晨钟 54/54、02_经验 55/55、03_种子 52/52、04_棋子 55/55、05_临界点 55/55（成片 295.51s）。
