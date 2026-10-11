# MEMORY_VIDEO.md — 观察哨 · **video agent** 运行时记忆

WAITING: 0

> ⚠️ `WAITING:` **只在顶部出现一次**（本行）。
> 语义：`0` = 有近期待办（**本线当前状态**：P0 已开工 · S1 完成 · S2 待做）；`1` = 常态。
> ⚠️ 本线 loop（`watch_video_loop.ps1`）**按小时固定唤醒**，**与 `WAITING` 无关**（字段仅供人读）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        S2 样板章 13_外骨骼 收尾（进行中 · 修路径✅ 补字幕✅ 烧录✅；验收+PIPELINE 待下轮）
已完成:       S1 全部 ✅；S2 第 1 步：① 修 9 个 EP13 脚本旧路径(E:/code→__file__) ✅ ② 生成中英双语字幕(13 条) ✅ ③ libass+微软雅黑烧录硬字幕成片 v3(91.13s/1080p/无缺字) ✅ ④ 抽帧+libass 日志验收 ✅
当前动作:     （本轮 S2 收尾：写 MEMORY/PLAN/BLOCKERS/daily + 两仓 commit+push）
下一步:       S2 收尾剩余：① 六项门禁验收(ffprobe 已核 91.13s/1080p/24fps/aac；qwen3_asr 核对旁白 + sound_caption 回读混音待做) ② 固化 PIPELINE.md → 之后进 S3 放量
阻塞:         无硬阻塞（ComfyUI/MCP/ffmpeg 全绿）。BLOCKERS #1(路径)✅ #4(字幕)✅ 已修；#2(MCP project_root=stem_fest 需传绝对路径) #3(15章缺规格) 仍在；legacy 脚本引用缺失工作流 LTX-2.3（不影响当前线）
ERROR_COUNT:  0
```

---

## 1. 状态头

- **线**：video（**基于 ComfyUI 制作视频**）
- **使命**：把《超级智能2035》短剧项目做成**视频成片**（首个任务 = P0）
- **任务书**：`WATCH_VIDEO_TASK.md`（只读 · = 每轮 prompt）
- **loop**：`watch_video_loop.ps1`（**Windows 11 本机** · 每小时**对齐整点**唤醒；计划任务名 `WatchVideoLoop`）
- **主战场仓**：`D:\Users\Administrator\code\super_intelligence_2035_short_drama`（独立 git 仓）
- **本线记录仓**：`D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\`
  - 记忆 = 本文件 · 日流水 = `daily-memories-video/` · 记录产物 = `video/`（`PLAN.md` / `PIPELINE.md` / `BLOCKERS.md` / `logs/`）
- **ComfyUI**：`http://127.0.0.1:8188`（根 `E:\code\ComfyUI`；开机由计划任务 `ComfyUI` 以 SYSTEM 自动启动）
- **MCP**：`comfyui-drama` · `web-search`（`E:\code\stem_fest\mcp_server\`）
- **上次唤醒**：2026-10-11（S2 · 修 EP13 旧路径 + 补中英字幕 + 烧录硬字幕成片 v3，见 §3 流水）
- **判活**：`video/logs/watch_video_loop.hb`（每轮刷新）+ `video/logs/watch_video_loop.log`

---

## 2. 运维问答（supervisor 提问 → 本线回答）

> （暂无）

---

## 3. 流水（倒序）

- **2026-10-11 · S2 样板章 13_外骨骼 收尾（第 1 步：修路径 + 补字幕）✅**：按任务书 S2 推进，完成「修旧路径 → 补字幕 → 烧录 → 字幕验收」四环。
  - **修路径（BLOCKERS #1 ✅）**：9 个 EP13 脚本硬编码 `E:/code/...` 改为 `ROOT = Path(__file__).resolve().parent.parent`（`gen_ep13_{ai_voice,bgm,h3_i2v,ltx_i2v,tts}.py`、`gen_shixiong_portraits.py`、`_regen_ep13_h3_720p.py`、`recover_ep13_ltx169.py`、`regen_ep13_ltx_169.py`），全量 `py_compile` 通过。
  - **补字幕**：新建 `scripts/gen_ep13_subtitles.py`，时间轴取自 TTS 音频时长、中文原文取自 `gen_ep13_tts.py`，生成 13 条中英双语 `OUTPUT/13_外骨骼/EP13_外骨骼_字幕.srt`。
  - **烧录（BLOCKERS #4 字幕部分 ✅）**：libass + 微软雅黑（`fontsdir=C:\Windows\Fonts`，`-c:a copy` 保原音轨）→ `EP13_外骨骼_成片_v3_字幕.mp4`（91.13s / 1920×1080 / 24fps / h264 4822kbps + aac 48kHz 单声道，时长与 v2 一致）。
  - **字幕验收**：抽帧 t=3.5/19/24 确认字幕在位；libass verbose 日志 `fontselect: (Microsoft YaHei,400,0) -> MicrosoftYaHei` 且**零** "Glyph not found" ⇒ 中文字形无 tofu、渲染正确，临时帧/探针已清理。
  - **遗留**：legacy `gen_ep13_ltx_i2v.py` / `regen_ep13_ltx_169.py` 引用缺失工作流 `workflows/Image to Video (LTX-2.3).json`（已入 BLOCKERS，不阻塞当前线）。
  - **下一步**：六项门禁验收（`qwen3_asr` 核对旁白 + `sound_caption` 回读混音）+ 固化 `PIPELINE.md`。
- **2026-10-11 · S1 首跑（环境 & 盘点）✅**：执行任务书 §1 S1 全项并产出记录。
  - **自检全绿**：ComfyUI `http://127.0.0.1:8188` v0.33.0 · RTX 4090 Laptop 16GB（空闲 14.7GB）· 队列空；MCP `comfyui-drama` 冒烟通过（`z_image_turbo_t2i` 512×512 · 21.2s · `s1_smoke_00001_.png` 207.9KB）；ffmpeg 2025-10-12 build 在。
  - **盘点结论**（短剧仓）：42 章逐镜脚本**全**在 `SCENES/`（2203 镜 / ≈3h03m）；`ASSETS/SHOT_SPECS/` 仅 **27 章**有 T2I/I2V 规格（缺 15 章）；**`OUTPUT/13_外骨骼/` 是唯一有素材的章**（16 帧 · 12 镜视频 · 16 TTS + 4 BGM · 成片 v1 107.7s / v2 91.1s，均 1080p）；`ASSETS/CHARACTERS/` 56 角色目录；`workflows/` 19 json。
  - **发现 4 项问题**（入 `BLOCKERS.md`）：#1 短剧仓已从 `E:\code\` 迁至 `D:\Users\Administrator\code\`，EP13 脚本硬编码旧路径失效；#2 MCP `project_root` = `E:\code\stem_fest`（产出需传绝对路径）；#3 15 章缺规格；#4 EP13 成片 v1/v2 时长差 + 缺字幕。
  - **产出**：`run/video/PLAN.md`（42 章状态表）+ `run/video/BLOCKERS.md`。
- **2026-10-11 · 立线（supervisor）**：新建 **video** 线脚手架 —— 任务书 `WATCH_VIDEO_TASK.md` · loop `watch_video_loop.ps1` · 计划任务注册脚本 `register_watch_video_task.ps1` · 本记忆 · `video/` 与 `daily-memories-video/` 目录。**待首轮唤醒执行 S1（环境 & 盘点）**。
  - 运行环境：`hx-c1000`（Win11）· **开机自启、无人登录**（计划任务，SYSTEM）· ComfyUI 开机 +30s 自启 · loop 每小时对齐整点唤醒。
