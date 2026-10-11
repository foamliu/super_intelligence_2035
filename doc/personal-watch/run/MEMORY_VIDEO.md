# MEMORY_VIDEO.md — 观察哨 · **video agent** 运行时记忆

WAITING: 0

> ⚠️ `WAITING:` **只在顶部出现一次**（本行）。
> 语义：`0` = 有近期待办（**本线当前状态**：P0 已开工 · S1 完成 · S2 待做）；`1` = 常态。
> ⚠️ 本线 loop（`watch_video_loop.ps1`）**按小时固定唤醒**，**与 `WAITING` 无关**（字段仅供人读）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        S3 放量 ✅ → 18_暖阳 续跑：13 张基础图 + 53 条台词已固化（ep18_dialogue.py · 🚫 禁用 TTS）；下一步 H3 I2V
已完成:       S1 ✅；S2 ✅（样板章端到端）；S3 首轮 ✅（18_暖阳 13 张基础图）；S3 续跑 ✅（53 条台词固化 ep18_dialogue.py + TTS 作废·按用户令禁用 TTS）
当前动作:     （本轮 S3 续跑：误按旧口径跑 TTS → 落档发现用户令禁用 TTS → 中止 TTS + 固化台词源 ep18_dialogue.py + 回写 PLAN/MEMORY/日流水 + commit+push）
下一步:       18_暖阳 续跑：video_minimax_h3_i2v 分镜视频（**台词随 H3 一起出 · 🚫 不用 TTS**）→ 字幕/音效BGM → 合成（★ 音画钉长）；BLOCKERS #5 已作废
阻塞:         无硬阻塞（ComfyUI/MCP/ffmpeg 全绿）。BLOCKERS #1✅ #4(字幕)✅ #5✅(已作废) 已修；#2(MCP project_root=stem_fest 需传绝对路径·已照做) #3(15章缺规格) 待处理
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
- **上次唤醒**：2026-10-11（S3 续跑 · 18_暖阳 53 条台词固化 ep18_dialogue.py；用户令禁用 TTS → TTS 作废）
- **判活**：`video/logs/watch_video_loop.hb`（每轮刷新）+ `video/logs/watch_video_loop.log`

---

## 2. 运维问答（supervisor 提问 → 本线回答）

> （暂无）

---

## 3. 流水（倒序）

- **2026-10-11 · 纪律变更（用户令 · supervisor 落档）· 🚫 禁用 TTS ✅**：用户下令「**不要使用 TTS；视频中的人物对话全部由 MiniMax H3 随视频一起生成**」。已落文档：任务书 **运维指令区 ⑦ + §3 铁律 + §1 链路 + §4.5**；`video/PIPELINE.md` 按新口径改写（③ 环节＝随 H3 生成、⑤ 合成去掉 TTS 输入、⑥ 字幕时间轴改用镜头时长）；`STEM_FEST_PLAYBOOK.md` §5/§10 同步；`BLOCKERS.md` **#5 作废关闭**（根因消失）；`PLAN.md` 表头「旁白TTS」→「台词(H3)」＋状态列标注 EP13 音轨 legacy。
  - **⇒ 影响**：**EP13 的 TTS 产物与 `synth_ep13` 的 TTS 混音 = legacy**（不再使用、不再混入成片）；**后续各章一律不生成、不混任何 TTS**，台词写进 H3 `prompt` 的 `Audio:`。
  - **⇒ 新链路**：分镜帧 → **H3 I2V（台词同期生成）** → BGM/音效 → 合成（**音画钉长**）→ 字幕 → 验收（`qwen3_asr` 逐字核对**含多余语音**）。

- **2026-10-11 · S3 续跑 · 18_暖阳 台词固化（53 条）+ TTS 作废 ✅**：S3 续跑 18_暖阳 第二棒。
  - **固化**：`scripts/ep18_dialogue.py`（5 角色 · 53 条台词/旁白原文 + 表演指令，唯一对话来源）；py_compile 通过。
  - **中止 TTS**：本轮误按旧口径跑 TTS（`gen_ep18_tts.py` 已产出 41/53 条 FLAC），落档发现**用户令禁用 TTS**（人物对话全部由 H3 随视频生成）⇒ 已 kill 进程、删除 `gen_ep18_tts.py`/`verify_ep18_tts.py` 及 `OUTPUT/18_暖阳/audio/` TTS 产物；台词转由 `ep18_dialogue.py` 供给 H3 `Audio:`。
  - **口径**：台词随 H3 生成（写进 prompt 的 `Audio:`）；⛔ 禁用 `qwen3_tts` 及任何 TTS（PIPELINE 铁律 3）。
  - **下一步**：`gen_ep18_h3_i2v.py` 分镜视频（台词写进 H3 prompt 的 `Audio:`，随 H3 一起出）→ 字幕/音效BGM → 合成（★ 音画钉长）。
- **2026-10-11 · S3 首轮 · 18_暖阳 基础图产出 ✅**：进 S3 放量，首选 18_暖阳 开工。
  - **产出 13 张基础图**（`OUTPUT/18_暖阳/frames/`，`manifest.json` 间接入库）：老周定妆 02_半侧面沉思 / 03_落泪（image_edit，输入 01 正面定妆，seed 43/44，1312×736）+ 出租屋 2 + 车内 4（image_edit）+ 小晴头像 1 + 城市夜景 2 + 道具 2（zimage_t2i，1024×1024 / 1280×720）。
  - **老周定妆扩展**：`02_半侧面沉思.png` / `03_落泪.png` 落库 `ASSETS/CHARACTERS/07_老周/`（与 01 正面定妆并列，跨第 18/39 集复用）。
  - **固化**：新建 `scripts/generate_ep18_t2i.py`（13 规格硬编码 + image_edit/zimage 自动路由 + `--dry-run`/`--shot`，py_compile + dry-run 验证通过）+ `OUTPUT/18_暖阳/frames/manifest.json`。
  - **路由口径**：人物镜头 → `image_edit_longcat`（megapixels=0.92）；非人物 → `z_image_turbo_t2i`；绝对路径落盘短剧仓。
  - **下一步**：18_暖阳 TTS → I2V → 字幕/音效 → 合成。
- **2026-10-11 · S2 样板章 13_外骨骼 完成（第 2 步：六项验收 + 固化 PIPELINE）✅**：按任务书 §2 收尾，S2 全部闭环。
  - **六项门禁验收**：① ffprobe 91.125s/1920×1080/24fps/h264 + aac 48kHz 单声道（91.114s）✅；② qwen3_asr 全片回读旁白：13 条中 11 条逐字吻合（L1–4 精确、L5 部分、L8–10 精确、L11–12 精确、L13 尾句截断）✅；③ sound_caption 回读混音：seg_a(0–27s) 检出连续 hum/drone + speech、seg_b(68–91s) 检出低频 hum/机械底噪 + 叙事语音（经 ASR 确认在轨）✅；④ 字幕（上轮 libass 零缺字）✅；⑤ 视频轨/烧录 ✅。
  - **发现缺陷（入 BLOCKERS #5）**：qwen3_asr 检不出第 6「合法吗？」、第 7「你别把我的代码写进段子里。」两句师兄台词；单独 ASR 源 flac 均正确；定位根因 = `13_tts_sarah_02_desk.flac` 实际 24.56s > 脚本分配 17.99s，Sarah 台词 18–24.56s 溢出、与师兄台词(18.19/19.87s)重叠压没（seg 18.2–22.8s ASR 仍听得到「我别管他叫外骨骼」佐证）。不阻塞 S2 结论，S3 首轮修时序。
  - **固化 PIPELINE.md**：把「分镜帧→I2V→TTS→BGM/音效→合成→字幕→验收」七环 + 命令/参数 + 5 条铁律（绝对路径 / megapixels≤0.6 / TTS固定speaker+seed / 体积红线 / 混音时序对齐）写入 `run/video/PIPELINE.md`。
  - **本轮短剧仓无代码改动**（仅验收 + 清理临时 `_verify/` 探针）；记录仓 commit `video:` 前缀。
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
