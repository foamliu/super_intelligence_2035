# MEMORY_VIDEO.md — 观察哨 · **video agent** 运行时记忆

WAITING: 0

> ⚠️ `WAITING:` **只在顶部出现一次**（本行）。
> 语义：`0` = 有近期待办（**本线当前状态**：S3 放量中 · 13_外骨骼 ✅ / 18_暖阳 ✅ / 01_晨钟 ✅ 三章已成片 · EP02《经验》后台跑批中）；`1` = 常态。
> ⚠️ 本线 loop（`watch_video_loop.ps1`）**按小时固定唤醒**，**与 `WAITING` 无关**（字段仅供人读）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        S3 放量 → EP02《经验》🔶 后台跑批中（33/55 落盘）；三章已成片（13/18/01）
已完成:       S1 ✅；S2 ✅；13_外骨骼 48/48 ✅（成片 95.1MB）；18_暖阳 54/54 ✅（成片 87.5MB）；01_晨钟 54/54 ✅（R2V 28 + T2V 26 · 成片 75.4MB · 漂移 0.010s）；EP02 资产（13 场景 + 2 合影）+ 生成脚本 + 字幕/合成脚本 ✅
当前动作:     EP02《经验》R2V(32)+T2V(23) 后台跑批（--skip-existing --wait，PID 12416/3168）；本轮核验 33/55 落盘（较上轮 +13）+ 全量参考图在位 + 时长/QC 全绿 + dry-run 复核字幕/合成脚本
下一步:       等 EP02 跑批收尾（55/55）→ 跑 gen_ep02_subtitles.py → synth_ep02.py（master + 硬字幕成片）→ ffprobe/signalstats QC
阻塞:         无（ComfyUI 队列 running1/pending1 = EP02 跑批正常推进；余 22 镜 = R2V 16 + T2V 6 约 2.5h）
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
- **上次唤醒**：2026-10-16（EP02《经验》跑批核验 33/55 + 时长/QC 全绿 + dry-run 复核收尾脚本 + 全量参考图在位）
- **判活**：`video/logs/watch_video_loop.hb`（每轮刷新）+ `video/logs/watch_video_loop.log`

---

## 2. 运维问答（supervisor 提问 → 本线回答）

> （暂无）

---

## 3. 流水（倒序）

- **2026-10-16 · S3 放量 · EP02《经验》跑批核验（33/55）+ 收尾脚本 dry-run ✅**：本轮核验 EP02 后台跑批健康（33/55 落盘，较上轮 +13），全量参考图在位，时长/QC 全绿，并 dry-run 复核字幕/合成脚本（不碰正在跑的 ComfyUI 队列）。
  - **git 同步**：短剧仓 up-to-date；记录仓 `pull --rebase --autostash` Fast-forward 69968183→41a5ee66（BaiZe/ZhuLong 等线，非本线），工作区净（他线 3 个未跟踪 .lnk/.docx 不碰）。
  - **自检**：ComfyUI 可达（RTX 4090 16GB · 空闲 11.2GB）· 队列 running 1 / pending 1 = EP02 跑批正常 · ffmpeg 在 · MCP comfyui-drama/web-search 可用。
  - **跑批核验**：`gen_ep02_h3_r2v.py`（PID 12416）+ `gen_ep02_h3_t2v.py`（PID 3168）两 `--wait` 进程在跑；`OUTPUT/02_经验/videos/` **33/55 镜**落盘；缺 22 镜 = R2V 16（30/31/33/34/35/36/37/39/42/43/44/45/46/47/48/49）+ T2V 6（50/51/52/53/54/55）。
  - **QC 抽检（ffprobe 全 33 镜）**：无 0 字节/无缺音轨/无零时长（ALL-OK）；时长逐镜吻合 `17k+5` 量化（22→10.125s / 28·32→4.458s / 38→3.042s / 40→5.167s）；R2V 864×480（mp 0.4）/ T2V 1056×608（mp 0.6）均 h264+aac。
  - **参考图核验**：R2V 17 张（角色定妆 5 + 场景 12）+ 合影拼版 2/2 全在位（`Test-Path` 逐张 OK）。
  - **收尾脚本 dry-run 复核**：`gen_ep02_subtitles.py --dry-run` 正常出字幕预览（SFX_ONLY={01,14,26,34,36,41,50,51} 与逐镜表「音效（后期）」8 无台词镜一致）；`synth_ep02.py --dry-run` 报 33/55 在位 / 缺 22 镜 / 预计 169.79s（部分），有缺镜即中止拼接（闸门正确）。**脚本就绪，等收尾即可直接跑**。
  - **下一步**：等 EP02 跑批收尾（55/55）→ `gen_ep02_subtitles.py` → `synth_ep02.py`（master + 硬字幕成片）→ ffprobe/signalstats QC。

- **2026-10-16 · S3 放量 · EP02《经验》跑批核验（20/55）+ 复核收尾脚本 ✅**：本轮核验 EP02 后台跑批健康（20/55 落盘，较上轮 +10），复核已预写的字幕/合成脚本，并核对全量参考图在位（不碰正在跑的 ComfyUI 队列）。
  - **git 同步**：短剧仓 up-to-date；记录仓 `pull --rebase --autostash`（git 走 stderr 报 NativeCommandError，实为 Fast-forward 后 up-to-date，工作区净，他线 3 个未跟踪 .lnk/.docx 不碰）。
  - **自检**：ComfyUI 可达（RTX 4090 16GB · 空闲 12.6GB）· 队列 running 1 / pending 1 = EP02 跑批正常 · ffmpeg 在 · MCP comfyui-drama/web-search 可用。
  - **跑批核验**：`gen_ep02_h3_r2v.py`（PID 12416）+ `gen_ep02_h3_t2v.py`（PID 3168）两 `--wait` 进程在跑；`OUTPUT/02_经验/videos/` **20/55 镜**落盘（SHOT 01–16 + 18/20/23/24）；err.log 0 字节（无报错）。
  - **规格抽检（ffprobe 全 20 镜）**：T2V 1056×608（mp 0.6）/ R2V 864×480（mp 0.4）· 均 h264 + aac（音轨随 H3 在轨）· 时长逐镜吻合 `17k+5` 量化（4.458/5.167/6.583/7.292/8.000…）· 无 0 字节/无缺音轨 ✅。
  - **参考图核验**：R2V 17 张（角色定妆 5 + 场景 12）+ 合影拼版 2/2 全在位（`Test-Path` 逐张 OK）。
  - **收尾脚本复核**：`gen_ep02_subtitles.py` 的 `SFX_ONLY={01,14,26,34,36,41,50,51}` 与 `SCENES/02_经验.md`「音效（后期）」8 无台词镜逐镜一致；`h3_dur_sec` 与任务书 §4.1 `17k+5` 量化核对无误（2.33/3.04/4.46/5.17/6.58/8.00/10.13）；`synth_ep02.py` 的 `aresample=32000…apad,atrim=0:<时长>,asetpts=N/SR/TB` 音画钉长链符合 §4.7，漂移闸门 0.15s。**脚本正确，等跑批收尾即可直接跑**。
  - **下一步**：等跑批收尾（55/55）→ 跑 `gen_ep02_subtitles.py` → `synth_ep02.py`（master + 硬字幕成片）→ ffprobe/signalstats QC。

- **2026-10-16 · S3 放量 · EP02《经验》跑批核验 + 预写字幕/合成脚本 ✅**：本轮核验 EP02 后台跑批健康（10/55 落盘）并预写 EP02 收尾脚本（不碰正在跑的 ComfyUI 队列）。
  - **git 同步**：短剧仓 up-to-date；记录仓 `pull --rebase --autostash` Fast-forward 77137bf6→fedae090（ZhuLong 线等，非本线）。
  - **自检**：ComfyUI 可达（RTX 4090 16GB · 空闲 13.1GB）· 队列 running 1 / pending 1 = EP02 跑批正常 · ffmpeg 在 · MCP `comfyui-drama`/`web-search` 可用。
  - **跑批核验**：后台两个 `--wait` 进程（`gen_ep02_h3_r2v.py` PID 12416 + `gen_ep02_h3_t2v.py` PID 3168）在跑；`OUTPUT/02_经验/videos/` **10/55 镜**落盘（SHOT 01–09 + 14）；资产全在位（场景 13/13 + 合影拼版 2/2）。
  - **预写脚本（本轮产出）**：`scripts/gen_ep02_subtitles.py`（复用两生成脚本 SHOTS · SFX_ONLY 8 无台词镜 = 01/14/26/34/36/41/50/51 · dry-run 148 条 / 291.25s）+ `scripts/synth_ep02.py`（音画钉长 + scale=1280:720 归一 + libass 硬字幕 · dry-run 10/55 在位/缺 45）。py_compile 通过。
  - **下一步**：等跑批收尾（55/55）→ 跑 `gen_ep02_subtitles.py` → `synth_ep02.py`（master + 硬字幕成片）→ ffprobe/signalstats QC。

- **2026-10-16 · S3 放量 · EP01《晨钟》成片合成 ✅（54/54 → master + 硬字幕成片 75.4MB）**：本轮核验 EP01 后台跑批已全部完成（54/54 落盘、ComfyUI 队列清零），随即生成字幕、拼接、烧录硬字幕成片。
  - **git 同步**：短剧仓 up-to-date；记录仓 `pull --rebase --autostash` Fast-forward 5f443f2d→f047b463（BaiZe/ZhuLong/news/research 等线，非本线）；工作区净（他线在途文件不碰）。
  - **自检**：ComfyUI 可达（RTX 4090 16GB · 空闲 14.7GB）· **队列已空（running 0 / pending 0）** = 后台跑批已收尾；ffmpeg 在 · MCP comfyui-drama 可用。
  - **出片核验**：`OUTPUT/01_晨钟/videos/` **54/54 镜**（R2V 28 + T2V 26）全部落盘，缺镜清零（上轮缺 9 镜 = R2V 36/37/44/48/50/53 + T2V 51/52/54 已补齐）。
  - **字幕**：`gen_ep01_subtitles.py` 出 `EP01_晨钟_字幕.srt`（70 条 · 235.79s；SFX_ONLY 26 无台词镜 + CAPTION 镜 54 收尾字幕），与 `SCENES/01_晨钟.md` 逐镜表「台词/音效」列逐镜核对一致。
  - **合成**：`synth_ep01.py` 拼接 54 镜 → `EP01_晨钟_master.mp4`（74.4MB）→ libass 硬字幕 `EP01_晨钟_成片.mp4`（**75,435,064 B = 71.9MB**）。
  - **QC（ffprobe + signalstats 实测）**：成片 **1280×720 @ 24fps h264 + aac**；视频 5659 帧 = 235.792s / 音轨 235.802s；**音画漂移 0.010s < 0.15s 闸门 ✅**；字幕带 signalstats（crop y640–720 @ t14.5s）YMIN=20 / YMAX=206 双峰在位（黑描边 + 白字）✅。图像接口「Unsupported Image」不可读 ⇒ 复用程序化 signalstats 核验（同 18_暖阳 口径）。
  - **遗留（可选）**：SeedVR2 超分 1920×1080；BGM 跨镜混音（ace_step_t2audio）—— 与 13/18 同口径，暂缓。
  - **下一步**：选下一章 EP02《经验》（55 镜，规格 ✅，待补参考图/合影 + R2V/T2V 生成脚本）。

- **2026-10-15 · S3 放量 · EP01《晨钟》出片核验 45/54 ✅（R2V 22/28 + T2V 23/26 · 后台跑批健康）+ spot QC 10 新镜全绿**：本轮核验 EP01 后台跑批进度并抽检新落盘镜头规格。
  - **git 同步**：两仓 `git status -sb` 均 `main...origin/main`（无 ahead/behind）；记录仓 pull 时 git 走 stderr 被 PS 报 NativeCommandError（瞬态噪音），复检确认已在同步态；工作区净（他线在途文件不碰）。
  - **自检**：ComfyUI 可达（RTX 4090 16GB · 空闲 9.3GB）· 队列 running 1 / pending 1 · ffmpeg 在 · MCP comfyui-drama 可用。
  - **出片核验**：`OUTPUT/01_晨钟/videos/` **45/54 镜**落盘（较上轮 +10：R2V 28/31/32/34/35 + T2V 43/45/46/47/49）；缺 9 镜 = R2V 6（36/37/44/48/50/53）+ T2V 3（51/52/54）。
  - **dry-run 复核**：R2V「✅ 所有参考图在位」28 镜；T2V 26 镜 —— 剩余 9 镜参考图/脚本无阻塞。
  - **spot QC（ffprobe 实测 10 新镜）**：R2V 28/31/32/34/35 = 864×480 24fps（73/73/158/107/226 帧 = 3.042/3.042/6.583/4.458/9.417s ✅）；T2V 43/45/46/47/49 = 1056×608 24fps（124/124/73/124/124 帧 = 5.167/5.167/3.042/5.167/5.167s ✅）—— 分辨率/帧率/`17k+5` 量化全部吻合。
  - **合成链路就绪复核**：`synth_ep01.py`（54 镜 concat 音画钉长 + scale=1280:720 归一 + 漂移闸门 <0.15s + libass 硬字幕）+ `gen_ep01_subtitles.py`（SFX_ONLY 26 无台词镜 + CAPTION 镜 54）读源码确认完整，全 54/54 后可立即跑。
  - **进程**：R2V pid 1488 / T2V pid 20976 均 ALIVE（StartTime 18:05:47）；最新出片 22:00:26（镜 49）—— 跑批持续健康推进。
  - **下一步**：每小时核出片进度（缺 9 镜）→ 全 54/54 后跑 `gen_ep01_subtitles.py` → `synth_ep01.py` → 合成 + QC。

- **2026-10-15 · S3 放量 · EP01《晨钟》出片核验 35/54 ✅（R2V 17/28 + T2V 18/26 · 后台跑批健康）+ spot QC 8 镜全绿**：本轮核验 EP01 后台跑批进度并抽检新落盘镜头规格。
  - **git 同步**：记录仓 `pull --rebase --autostash` Fast-forward 8991af4f→c4556667（BaiZe 线 outbox.md 等，非本线）；短剧仓 up-to-date；工作区净。
  - **自检**：ComfyUI 可达（RTX 4090 16GB · 空闲 6.5GB）· 队列 running 1 / pending 1 · ffmpeg 在 · MCP comfyui-drama 可用。
  - **出片核验**：`OUTPUT/01_晨钟/videos/` **35/54 镜**落盘（R2V 17 = 02/04/05/06/07/08/09/10/11/12/16/17/18/20/21/25/27；T2V 18 = 01/03/13/14/15/19/22/23/24/26/29/30/33/38/39/40/41/42）；缺 19 镜 = R2V 11（28/31/32/34/35/36/37/44/48/50/53）+ T2V 8（43/45/46/47/49/51/52/54）。
  - **dry-run 复核**：R2V「✅ 所有参考图在位」28 镜；T2V 26 镜 —— 剩余 19 镜参考图/脚本无阻塞。
  - **spot QC（ffprobe 实测 8 镜）**：R2V 16/20/25/27 = 864×480 24fps（73/107/56/73 帧 = 3.042/4.458/2.333/3.042s ✅）；T2V 30/33/39/42 = 1056×608 24fps（107/56/124/73 帧 = 4.458/2.333/5.167/3.042s ✅）—— 分辨率/帧率/`17k+5` 量化全部吻合。
  - **进程**：R2V pid 1488 / T2V pid 20976 均 ALIVE（= .pid 一致；日志 0 字节为块缓冲 · 已知）。
  - **下一步**：每小时核出片进度（缺 19 镜）→ 全 54/54 后跑 `gen_ep01_subtitles.py` → `synth_ep01.py` → QC。


- **2026-10-15 · S3 放量 · EP01《晨钟》出片核验 21/54 ✅（R2V 10/28 + T2V 11/26 · 后台跑批健康）+ R2V 整改闭环盘点**：本轮核验 EP01 后台跑批进度，并盘点 2026-10-12「推翻旧法·R2V 重做」整改的落地情况。
  - **git 同步**：短剧仓 up-to-date；记录仓 `pull --rebase --autostash` 先撞「cannot lock ref」（并发 git 进程所致 · 瞬态），复拉后 HEAD 从 b0b880a4 推进到 c2e3b10c（仍 behind 1 → origin/main 82bee819）；工作区已净（BaiZe 线改动已并入上游，非本线），3 条旧 stash 非本线、不碰。
  - **自检**：ComfyUI 可达（RTX 4090 16GB · 空闲 6.6GB）· 队列 running 1 / pending 1 · ffmpeg 在 · MCP comfyui-drama 可用。
  - **出片核验**：`OUTPUT/01_晨钟/videos/` **21/54 镜**落盘（R2V 10 = 02/04/05/06/07/08/09/10/11/12；T2V 11 = 01/03/13/14/15/19/22/23/24/26/29）；两进程 ALIVE（R2V pid 1488 / T2V pid 20976 = .pid 文件一致）。
  - **spot QC（ffprobe 实测）**：镜12 R2V = h264 864×480 24fps 107帧 4.458s ✅；镜29 T2V = h264 1056×608 24fps 107帧 4.458s ✅；镜11 R2V = 864×480 73帧 3.042s ✅ —— 分辨率/帧率/`17k+5` 时长量化全部吻合。
  - **★ R2V 整改闭环核验（运维指令 ①③④ 已落地）**：`PIPELINE.md` §1 已改「参考图 → R2V 直出」+ §2/§3 参数路由 + legacy I2V/TTS 停用 ✅；`STEM_FEST_PLAYBOOK.md` §3 路由行已更正「有角色→R2V（唯一）；无角色→T2V」✅；`OUTPUT/_deprecated_t2i_2026-10-13/`（frames/videos）在位 ✅；13/18 成片落盘（`EP13_外骨骼_成片.mp4` 95.1MB / `EP18_暖阳_成片.mp4` 87.5MB）✅。
  - **下一步**：每小时核 EP01 出片进度（R2V 缺 18 镜 / T2V 缺 15 镜）→ 全 54/54 落盘后跑 `gen_ep01_subtitles.py`（SRT）→ `synth_ep01.py`（concat 音画钉长 + scale=1280:720 归一 + libass 硬字幕）→ QC。

- **2026-10-15 · S3 放量 · EP01《晨钟》出片核验 + 预写合成/字幕脚本 ✅（12/54 落盘）**：本轮核验 EP01 后台跑批进度并预写合成脚本（跑批期间不占 ComfyUI）。
  - **git 同步**：短剧仓 up-to-date；记录仓 `pull --rebase` 拉到新提交（zhulong 线 `fff139b7` 等，非本线）。
  - **自检**：ComfyUI 可达（RTX 4090 16GB · 空闲 8.8GB）· 队列 running 1 / pending 1 · ffmpeg 在 · 两仓无冲突。
  - **出片核验**：`OUTPUT/01_晨钟/videos/` **12/54 镜**落盘（01–08/13/14/15/19）；后台跑批两进程 ALIVE（R2V pid 1488 / T2V pid 20976），日志 0 字节为块缓冲（已知，改看文件计数）。
  - **★ 预写脚本（提前就绪）**：新建 `scripts/gen_ep01_subtitles.py`（台词取 H3 prompt `Audio:` 中文原文 · `SFX_ONLY` 显式排除 26 无台词镜 · `CAPTION` 单独烧录镜 54 收尾字幕「她没有开场白。只是坐在那里，等。」）+ `scripts/synth_ep01.py`（54 镜 concat 音画钉长 + scale=1280:720 归一 + libass 硬字幕）。均 `py_compile` + `--dry-run` 验证通过（字幕 70 条 · 全片 235.79s · 合成缺 42 镜正常拦截）。
  - **下一步**：全 54/54 落盘后跑 `gen_ep01_subtitles.py`（生成 SRT）→ `synth_ep01.py`（拼 master + 烧字幕）→ ffprobe/signalstats QC。


- **2026-10-15 · S3 放量 · EP01《晨钟》视频生成启动 ✅（54 镜 · R2V 28 + T2V 26）**：本轮把下一章 EP01 晨钟 的视频生成跑起来。
  - **盘点发现**：上一轮（17:11–17:25）已就绪 EP01 三脚本（`gen_ep01_scenes.py` / `gen_ep01_h3_r2v.py` / `gen_ep01_h3_t2v.py`，均未提交）+ 16 张参考图（`ASSETS/CHARACTERS/_scene/01_*.png`，4 角色 + 12 场景）；`OUTPUT/01_晨钟/` 尚 0 文件。
  - **自检**：ComfyUI 可达（RTX 4090 16GB）· 队列空 · 两仓 pull 均 up-to-date。
  - **dry-run 核验**：R2V 28 镜（`--dry-run` 报「✅ 所有参考图在位」）+ T2V 26 镜 = 54 镜，与 `SCENES/01_晨钟.md` 逐镜表一致。
  - **★ 启动后台跑批**：`Start-Process py -3.10 scripts/gen_ep01_h3_r2v.py --skip-existing --wait`（pid 1488）+ `gen_ep01_h3_t2v.py`（pid 20976），stdout/stderr 落 `_gen_ep01_{r2v,t2v}.log/.err.log`，pid 落 `.pid`；核验 ComfyUI 队列 running 1 / pending 2（提交成功、正在出片）。
  - **已知**：① 首镜 02 有 1 次重复提交（前一次 30s 超时被中断的 smoke test 已提交同 seed 1002 同镜，产物同 seed 相同、下载覆盖，无功能影响）；② `py` 重定向 stdout 到文件走块缓冲 ⇒ 日志暂 0 字节，监控改看 `OUTPUT/01_晨钟/videos/` 文件计数。
  - **下一步**：每小时核 EP01 出片进度（`OUTPUT/01_晨钟/videos/EP01_SHOT-*.mp4` 计数）→ 全 54/54 后写 `synth_ep01.py` + `gen_ep01_subtitles.py`（复用 EP13/EP18 范式）→ 合成 + QC。


- **2026-10-15 · S3 收尾 · 18_暖阳 R2V 端到端成片 ✅（54/54 镜 master + 硬字幕成片）**：本轮完成 EP18 暖阳「样板第三例」端到端收口与 QC。
  - **资产核清**：`OUTPUT/18_暖阳/videos` R2V 32 + T2V 22 = **54/54 镜在位**；`EP18_暖阳_字幕.srt`（6,510B · 96 条）已生成。
  - **★ 脚本收口**：`gen_ep18_subtitles.py` 台词取 H3 prompt `Audio:` 中文原文（🚫 无 TTS），`SFX_ONLY` 显式排除 13 个无台词镜（01/03/10/22/27/29/33/34/36/41/47/49/53）；`synth_ep18.py` 每镜视频链前加 `scale=1280:720:flags=lanczos,setsar=1`（R2V mp=0.4=864×480 vs T2V mp=0.6=1056×608 尺寸不一致），沿用音画钉长（`h3_dur_sec` + `atrim/asetpts` 钉帧）。
  - **成片合成**：`EP18_暖阳_master.mp4`（85,442,249B）+ libass 硬字幕 → `EP18_暖阳_成片.mp4`（87,541,683B）。
  - **QC（ffprobe + signalstats 实测）**：master/成片均 **1280×720 @ 24fps h264 + aac**，视频 273.333s / 音轨 273.342s，**音画漂移 0.009s < 0.15s 闸门 ✅**；抽帧 6s/270s（`_chk_06.png`/`_chk_270.png`）非空白（整帧 YAVG 122.4/25.3 · YMAX 235）；底部字幕带核验（帧 06 字幕带 YMIN=0 黑描边 + YMAX=220 白字在位；帧 270 片尾系统 UI 文字中下部高亮 YMAX 254/255）。
  - **★ QC 程序化核验替代目视**：图像接口返回「Unsupported Image」不可读 ⇒ 改用 ffmpeg `signalstats,metadata=print:file=...` 量化核验（整帧 YAVG/YMIN/YMAX + 底部字幕区 crop 亮度），避免人工目视。
  - **遗留（可选）**：SeedVR2 ×1.5 → 1920×1080 超分；BGM 跨镜混音（ace_step_t2audio）。
  - **下一步**：下一章放量。

- **2026-10-13 · S3 收尾 · 13_外骨骼 R2V 端到端成片 ✅（48/48 镜 master + 硬字幕成片）**：本轮完成 EP13 外骨骼「样板第二例」端到端收口与 QC。
  - **T2V 批次收齐**：`gen_ep13_h3_t2v.py` 19/19 无角色镜全部落盘；`OUTPUT/13_外骨骼/videos` R2V 29 + T2V 19 = **48/48 镜在位**。
  - **★ concat 分辨率归一修复**：`scripts/synth_ep13.py::build_concat_cmd` 每镜视频链前加 `scale=1280:720:flags=lanczos,setsar=1`（R2V mp=0.4=864×480 vs T2V mp=0.6=1056×608 尺寸/宽高比 1.8 vs 1.737 不一致，直接 concat 报错）。
  - **成片合成**：`gen_ep13_subtitles.py` 出 `EP13_外骨骼_字幕.srt`（11,610B）→ `synth_ep13.py` 拼接 `EP13_外骨骼_master.mp4`（89,320,786B）+ libass 硬字幕 → `EP13_外骨骼_成片.mp4`（95,126,651B）。
  - **六项 QC（ffprobe 实测）**：master/成片均 **1280×720 @ 24fps h264 + aac**，视频 262.875s / 音轨 262.886s，**音画漂移 0.011s < 0.15s 闸门 ✅**；抽帧 63s/259s（`_chk_63.png`/`_chk_259.png`，1024×576）非空白（均值亮度 186.5/88.8，动态范围 0–255）。
  - **遗留（可选后续）**：SeedVR2 ×1.5 → 1920×1080 超分；BGM 跨镜混音（ace_step_t2audio）。
  - **下一步**：18_暖阳 重做 / 下一章放量。


- **2026-10-13 · S3 续跑 · 任务书体积归档（⑥ 自滚归档）+ R2V 29/29 核验 + T2V 批量进行中**：本轮做不依赖 ComfyUI 队列的「记录/整改」活（T2V 批量串行在跑 · 队列 running=1 · PID 3424）。
  - **⑥ 体积归档**：`WATCH_VIDEO_TASK.md` 实测 42301B 越 40KB 红线 ⇒ Python 行级脚本把三块**已闭合**历史运维指令（2026-10-12 流水线改判 / 2026-10-12 下一章改判 / 2026-10-11 立线）**逐字归档**到 `run/video/WATCH_VIDEO_TASK_ARCHIVE.md`（80 行 · 8986B），任务书瘦身至 **33686B**（<40KB 红线），顶部留指针、唯一生效指令 = 2026-10-12「推翻旧法·R2V 重做」块。
  - **R2V 批次收尾核验**：`OUTPUT/13_外骨骼/videos/` R2V **29/29 全部落盘**（last 镜 47 @13:24）；spot-check 镜 47 = h264 864×480 24fps + aac 5.167s（吻合 `17k+5`）；T2V 镜 22 = h264 1056×608 24fps + aac 5.167s（mp=0.6 口径）。
  - **T2V 批次进行中**：`gen_ep13_h3_t2v.py --wait --skip-existing`（PID 3424 · 14:03 起）串行 19 无角色镜，**已出 10/19**（01/02/04/05/08/12/14/20/22），剩 9 镜（25/28/30/31/37/40/43/44/46/48）。
  - **下一步**：收 T2V → `gen_ep13_subtitles.py` 出 SRT → `synth_ep13.py` 拼接（音画钉长）→ BGM（ace_step_t2audio 跨镜整体铺）→ 硬字幕 → 六项验收。

- **2026-10-13 · S3 续跑 · 重写 synth_ep13.py（去 TTS · 48 镜音画钉长）+ R2V 24/29 核验**：队列忙（R2V 批量在跑 · 约镜 39），本轮做不依赖队列的「脚本整改」活。
  - **重写 `scripts/synth_ep13.py`**：旧版混 TTS（`TTS_CUES`/`13_tts_*.flac`）+ 引用旧 `_720p_`/`_sarah_desk_` 文件名，违反 2026-10-11「禁用 TTS」用户令 ⇒ 整体重写为「R2V 29 + T2V 19 = 48 镜」concat（`from gen_ep13_h3_r2v/t2v import SHOTS` 合并 `ALL`），沿用 EP18 已固化 **音画钉长**铁律（`h3_dur_sec` 按 `17k+5` 帧量化；每段音频 `aresample...atrim=0:<dur>...asetpts=N/SR/TB` 钉到「帧数÷24」；漂移闸门 <0.15s；🚫 `-shortest`），libass 字幕烧录。py_compile exit=0 + `--dry-run` 通过（24/48 镜在位、预计 134.63s、缺镜清单=19 T2V + 5 R2V 剩）。
  - **R2V 批次进度**：`OUTPUT/13_外骨骼/videos/` 已落 24/29 镜（新增 23/24/26/27/29/32/33/34/35/36/38），约镜 39 在跑；PID 10556 存活（串行 --wait）；剩 39/41/42/45/47 五镜。
  - **下一步**：收 R2V 剩余 5 镜 → 队列空闲后跑 `gen_ep13_h3_t2v.py` 19 无角色镜 → 重写 `gen_ep13_subtitles.py`（去 TTS 时序 · 48 镜台词）→ BGM/SFX → `synth_ep13.py` 合成 → 六项验收。


- **2026-10-13 · S3 续跑 · 固化 gen_ep13_h3_t2v.py（19 无角色镜 · T2V 路线）**：补齐 13_外骨骼 无角色镜的 H3 T2V 生成脚本，等 R2V 批次收尾后即可跑（队列空闲后提交，§4.8）。
  - **脚本**：`scripts/gen_ep13_h3_t2v.py`（照 `gen_ep18_h3_t2v.py` T2V 注入 + `gen_ep13_h3_r2v.py` 4 键下载/CLI 范式）；19 镜硬编码（01/02/04/05/08/12/14/20/22/25/28/30/31/37/40/43/44/46/48），台词随 H3 生成（写进 `Audio:`），无台词镜只写正向音景；`mp=0.6 / steps=10 / 16:9`（steps 按 2026-10-12「别默认堆 20」回落，本批均静态/界面/道具镜）；seed=1300+镜号。
  - **校验**：py_compile exit=0 + `--dry-run` 列出 19 镜（R2V 29 + T2V 19 = 48 全集，01–48 无缺无重）。
  - **R2V 进度**：已落 13/29（03/06/07/09/10/11/13/15/16/17/18/19/21），约镜 23 在跑（PID 10556 串行 --wait）。
  - **下一步**：收 R2V 剩余 16 镜 → 跑 T2V 19 镜 → BGM/SFX → `synth_ep13.py` → 字幕 → 六项验收。

- **2026-10-13 · S3 续跑 · 13_外骨骼 R2V 批量启动（03/06/07 验收 ✅ + 26 镜后台跑）**：验证 3 个手动复制产物 + 定位 SaveVideo 登记键 + 修复自动下载 + 启动批量。
  - **验收（03/06/07）**：ffprobe 三镜均 **h264 864×480 24fps + aac**（mp=0.4 16:9），时长精确吻合 §4.1 `17k+5`：03=5.167s/124 帧、06=5.167s/124 帧、07=6.583s/158 帧 ⇒ 三镜规格达标。
  - **定位 & 修复**：`/history` 确认 Minimax H3 的 `SaveVideo`（node 92）把 `.mp4` 登记在 **`images` 键**（type=output / subfolder=video），非 `videos` 键 ⇒ `gen_ep13_h3_r2v.py::_save_outputs` 改为遍历 images/gifs/videos/audio 四键 + `_download_view` 按 type/subfolder/filename 下载。
  - **启动批量**：`gen_ep13_h3_r2v.py --wait --skip-existing --timeout 3600` 后台 Start-Process（PID 10556），串行提交+等待+自动下载剩余 26 镜（09/10/11/13/15/16/17/18/19/21/23/24/26/27/29/32/33/34/35/36/38/39/41/42/45/47）；首镜 09 已入队列 running。
  - **下一步**：收 26 镜 → 另写 `gen_ep13_h3_t2v.py`（19 无角色镜）→ BGM/SFX → `synth_ep13.py` → 字幕 → 六项验收。

- **2026-10-13 · S3 续跑 · 13_外骨骼 R2V 场景参考图补齐（BLOCKERS #7 ✅）**：补上「T2I 首帧→I2V」旧法从未备过的 14 张独立场景参考图，R2V 29 镜的 `ref2` 硬输入齐活。
  - **固化脚本**：新建 `scripts/gen_ep13_scenes.py`（14 张无角色场景 · 16:9 1280×720 · `Z-Image-Turbo 文生图.json` · 负面词以 "Do NOT include: ..." 追加进正向，因该工作流负面被 ConditioningZeroOut 置零 · 按 class_type 通用注入 CLIPTextEncode/EmptySD3LatentImage/KSampler · `--dry-run/--key/--wait`）。
  - **文件名权威**：`out` 文件名与 `gen_ep13_h3_r2v.py` 的 `REFS`/`REF_SLUG` 注册表逐字一致（`13_theatre_backstage.png` 等 14 张，非早期 `13_backstage.png` 式臆测名）。
  - **核验**：14/14 落盘 `ASSETS/CHARACTERS/_scene/`（每张 1280×720 · 1.25–2.0 MB）；`gen_ep13_h3_r2v.py --dry-run` 报「✅ 所有参考图在位」并列出 29 镜计划。
  - **下一步**：R2V 29 镜批量 + 另写 `gen_ep13_h3_t2v.py`（19 无角色镜）→ BGM/SFX → synth → 字幕 → 六项验收。

- **2026-10-13 · S3 续跑 · 13_外骨骼 R2V 迁移（推翻「T2I→I2V」旧法 · 去 TTS）✅**：按 operator 2026-10-12 令，弃用「T2I 首帧 → H3 I2V」，改用 stem_fest R2V 标准重做 13_外骨骼。
  - **弃用旧输出**：`OUTPUT/13_外骨骼`（旧 T2I→I2V 成片）改名 `OUTPUT/_deprecated_t2i_2026-10-13`（29 文件 / 38.7 MiB，待 R2V 验证后再物理删除）；留档 `_deprecated_2026-10-13.md`。
  - **整改文档**：`PIPELINE.md` 改 R2V-first（§1 链 / §2 参数 / §3 脚本索引，I2V/T2I/TTS 标 legacy）；`STEM_FEST_PLAYBOOK.md` §3 路由改「有角色→R2V 唯一 / 无角色→T2V」，新增「参考图按在场人数给脸」硬规则。
  - **固化脚本**：新建 `scripts/gen_ep13_h3_r2v.py`（29 有角色镜 · 台词随 H3 · mp=0.4/steps=10/16:9 · ref1=定妆照/合影+ref2=场景图 · `--dry-run/--shot/--limit/--skip-existing`，py_compile + dry-run 通过）；新建 `scripts/make_group_composite.py`（合影程序拼版，🚫 不经 image_edit）。
  - **补资产（合影）**：`ASSETS/CHARACTERS/_group/sarah_shixiong_hero_v01.png` + `sarah_linwei_hero_v01.png`（1920×1080，PIL 居中裁 4:5 拼版）。
  - **验证**：3 张定妆照（莎拉 2848×1600 / 师兄 1920×1920 / 林薇 1672×941）在位；`--dry-run` 报缺 14 张场景参考图（→ BLOCKERS #7）。
  - **下一步**：补 14 张 `_scene/` 场景图（z_image_turbo_t2i）→ R2V 29 镜 + T2V 19 镜 → BGM/SFX → synth → 字幕 → 六项验收。

- **2026-10-12 · S3 续跑 · 13_外骨骼重做启动（去 TTS）+ 18_暖阳最终 QC 已执行 ✅**：按 operator 令「暖阳之后做外骨骼」，重写 EP13 T2I 脚本。
  - **18_暖阳最终 QC（已执行）**：`qwen3_asr` 回读 `EP18_暖阳_成片.mp4` 返回中文台词 transcript；`sound_caption` 回读 `EP18_暖阳_成片_BGM01.mp4` 返回环境音描述（H3 随片人声 + BGM 混音在轨）。逐字比对结论待下轮持久化。
  - **13_外骨骼 T2I 重做（去 TTS）**：重写 `scripts/generate_ep13_t2i.py`（替代 legacy）——**14 帧新口径**：4 人物帧 `image_edit`（莎拉×3 工位/地铁/吧台 + 师兄×1 咖啡，输入各自主定妆照，megapixels=0.92）+ 10 非人物帧 `zimage`（场景×4 + 虚拟观众×2 + 道具×2 + UI×2）。**无 TTS**，台词由 H3 随片。
  - **验证**：`py_compile` exit=0 + `--dry-run` 列出 14 帧 + 主定妆照（莎拉/师兄）/工作流存在核验通过。
  - **后台**：批量 `generate_ep13_t2i.py`（Start-Process，RedirectOutput `OUTPUT/13_外骨骼/frames/_batch.*.log`），首帧 `13_sarah_01_desk_explaining.png` 已落盘（1.93MB）。
  - **下一步**：收 14 帧 → 核验 manifest → I2V（H3 随片配音）→ 字幕/音效BGM → 合成 → 六项验收。

- **2026-10-12 · S3 收尾 · 18_暖阳 54/54 成片 + BGM 混音（响度 -23.8 LUFS）✅**：本轮收 T2V + 合成成片 + 混 BGM。
  - **成片（验收式陈述）**：`EP18_暖阳_成片.mp4` = **54/54 镜 · 273.34s · 1056×608 · h264+aac**，主音画漂移 **0.009s**；manifest `verified_count=54`。T2V 5 镜（15/20/27/28/54）全收 + SHOT-54 生成。
  - **BGM 素材**：`OUTPUT/18_暖阳/audio/` 3 条 ACE-Step 纯器乐（01 大提琴 60s seed4801 / 02 数据流 45s seed4802 / 03 尾声 45s seed4803）。
  - **固化两脚本**：`scripts/gen_ep18_bgm.py` + `scripts/mix_ep18_bgm.py`（从 stem_fest `_mix_bgm.py` 移植：`-c:v copy` + BGM acrossfade 循环 + 侧链闪避 + alimiter -1 dBFS）。
  - **响度修正（关键）**：成片 H3 音轨实测 **-13.4 LUFS / 真峰 0.1 dBFS / LRA 16.2 LU**（非 README §4.4 的 -50 dB 环境声）。按 README 音频规格（配乐 -25~-30 LUFS / 母带 -23 LUFS -1 dBTP）修 mix：新增 `--film-dip` -9.6（主干→-23）+ `--level` -12（BGM→-28）。
  - **混音产物**：`EP18_暖阳_成片_BGM01.mp4` 65.1MB，**-23.8 LUFS / LRA 7.9 / 峰值 -9.1 dBFS**（≈ -23 ✓，峰值 ≤ -1 ✓）。
  - **下一步**：BGM02/03 可选混音 → 最终 QC（qwen3_asr + sound_caption）→ 选定交付文件 → 08_认知矿工。


- **2026-10-12 · S3 续跑 · 18_暖阳 I2V 49/49 全收 + 固化字幕/合成两脚本 ✅（T2V 后台续跑中）**：本轮收尾 I2V + 备好字幕/合成脚本。
  - **核验（验收式陈述）**：`update_ep18_manifest.py` ffprobe 扫 49 镜 mp4 → manifest **31→49 verified**（h264 1056×608 24fps + aac，时长精确吻合 §4.1 `17k+5`：3.042/4.458/5.167/6.583s）。I2V 批次（后台 `--skip-existing`）已全收。
  - **新增字幕脚本**：`gen_ep18_subtitles.py`（从各镜 H3 prompt 的 `Audio:` 提取中文台词→字幕，无台词镜（英文音景）自动跳过；py_compile + dry-run 通过）→ 生成 `EP18_暖阳_字幕.srt`（**96 条 · 6514B** · 全片 273.33s）。
  - **新增合成脚本**：`synth_ep18.py`（54 镜 concat，**★音画钉长**：每段音频 `aresample=32000,aformat=stereo,apad,atrim=0:<镜时长>,asetpts=N/SR/TB` + 闸门 |音轨−画面|<0.15s + 🚫 禁 `-shortest`；dry-run 正确识别缺 5 T2V 镜）。
  - **git**：records 仓 `pull --rebase` 同步 11 commits（他线）；短剧仓 up-to-date。
  - **后台**：T2V 批次 `gen_ep18_h3_t2v.py --skip-existing`（PID 4588，steps=20）续跑 5 镜，ComfyUI 队列 running=1。
  - **下一步**：收 T2V 5 镜 → `synth_ep18.py` 合成 → BGM/音效 → 成片（★ 音画钉长 + 逐镜内容偏移验收）。

- **2026-10-12 · S3 续跑 · 18_暖阳 I2V 批次收 31/54 镜成片 ✅（后台批次续跑中）**：核验 31 镜 mp4 → manifest 19→31 → 固化脚本 commit+push。
  - **核验（验收式陈述）**：`update_ep18_manifest.py --dry-run` + ffprobe 逐镜核验 **31/54 镜 mp4**（h264 1056×608 24fps + aac，时长吻合 §4.1 `17k+5`：3.042/4.458/5.167/6.583s）。新增 12 镜（07/17/29/31/32/39/41/42/45/46/47/48）。
  - **manifest**：`OUTPUT/18_暖阳/videos/manifest.json` 19→**31 verified**（`verified_count:31` + notes「剩余 23 镜：I2V 18 + T2V 5」）。
  - **固化脚本**：`gen_ep18_h3_i2v.py`（扩至全 49 I2V 镜含 16 UI 镜）、`gen_ep18_h3_t2v.py`（5 T2V 镜 15/20/27/28/54，steps=20，新增）、`update_ep18_manifest.py`（扫 mp4→ffprobe→回写 verified，新增）；三脚本 py_compile exit=0。
  - **短剧仓 commit**：`2a9e851`（4 files, +988/−29）→ push ✅（`main...origin/main` 同步）。
  - **背景**：上一轮遗留后台批次 `gen_ep18_h3_i2v.py --skip-existing`（PID 9136）未提交即被中断，本轮不干扰批次、改为核验+固化+commit。
  - **下一步**：收尾 I2V 批次（剩余 18 镜）→ `gen_ep18_h3_t2v.py` 5 镜 → 字幕/音效BGM → 合成（★ 音画钉长）。

- **2026-10-12 · S3 续跑 · 18_暖阳 手机UI系列 16 帧全生成 ✅（含补 23 消费记录）**：本轮补全 UI 帧缺口并核验。
  - **补 23**：`scripts/gen_ep18_ui_frames.py` SPECS 新增 SHOT-23（消费记录 `18_ui_23_orders.png`，seed=1923）；py_compile exit=0 + `--shot 23 --dry-run` 通过；后台 `Start-Process` 出 1 张（1331KB）。
  - **核验 16/16**：`OUTPUT/18_暖阳/frames/18_ui_*.png` 共 16 张，PIL 逐张核 1280×720、无零字节（1.16–1.59MB）。
  - **UI 帧清单**（16 镜）：03 注册 / 09 头像 / 12 波形 / 16 聊天 / 21 推荐 / 23 消费记录 / 29 延迟 / 30 延迟2 / 34 论坛首页 / 35 发帖 / 38 淡出 / 40 聊天问答 / 43 输入 / 44 聊天回复 / 51 干预 / 53 购物车。
  - **manifest**：`OUTPUT/18_暖阳/videos/manifest.json` notes 更新为「UI 16 帧已全生成」，verified_count 仍 19。
  - **下一步**：扩 `gen_ep18_h3_i2v.py` 用 16 张 UI 帧出 I2V（手机屏幕动态）+ 数据流 T2V（15/20/27/28/54）+ 其余镜 → 逐批 H3 → 字幕/音效BGM → 合成。


- **2026-10-12 · S3 续跑 · 18_暖阳 I2V 二批 8 镜全收 ✅（14/54 镜成片）**：收 8 镜异步 → 14/14 ffprobe 核验 → manifest 8→verified → 回写 commit。
  - **收 8 镜（验收式陈述）**：`comfyui_get_result` 取回 SHOT-10/11/19/24/26/33/36/37（8 个 prompt_id 全 `success`，ComfyUI 队列已清零 0 running/0 pending），ffprobe 核验全部 h264 1056×608 24fps + aac，时长精确吻合 §4.1 `17k+5`（10→5.167 / 11→6.583 / 19→5.167 / 24→5.167 / 26→4.458 / 33→3.042 / 36→4.458 / 37→4.458）。字节 288KB–818KB。
  - **累计 14/54 镜成片**（01/02/04/05/08/10/11/14/19/24/26/33/36/37）；`manifest.json` 更新为 14 verified（`verified_count:14` + notes 列剩余资产缺口）。
  - **盘点剩余 40 镜资产缺口**：车间主任无定妆照（`ASSETS/CHARACTERS/` 无此角色，镜 06 需新建或 T2I 泛化中年男）；手机 UI 系列 16 镜需 UI 帧；数据流 T2V（15/20/27/28/54 无参考图，直接 `t2v`）；出租屋书桌/门口/卧室（18/22/25）；老周手部特写（13）。前妻 VO-only 闪回（45 用老周定妆照）。
  - **下一步**：补资产 → 扩 `gen_ep18_h3_i2v.py` / 新增 t2v 脚本 → 逐批 H3 出片 → 字幕/音效BGM → 合成（★ 音画钉长）。

- **2026-10-12 · S3 续跑 · 18_暖阳 I2V 首批收 + 二批 8 镜排队 ✅**：收 5 镜异步 → 6/6 ffprobe 核验 → 固化脚本扩至 14 镜 → 二批 8 镜异步排队。
  - **收 5 镜（验收式陈述）**：`comfyui_get_result` 取回 SHOT-02/04/05/08/14（5 个 prompt_id 全 `success`），ffprobe 核验 6/6 全部 h264 1056×608 24fps + aac，时长与 §4.1 `17k+5` 精确吻合（01→4.458 / 02→5.167 / 04→4.458 / 05→3.042 / 08→4.458 / 14→6.583）。字节 246KB–1.26MB。
  - **扩固化脚本**：`scripts/gen_ep18_h3_i2v.py` SHOTS 扩至 14 镜（二批 8 镜 = 10/11/19/24/26/33/36/37，复用现成帧，单人/无台词，seed=1800+镜号）。py_compile exit=0 + dry-run 14/14 通过。
  - **二批 8 镜异步排队**（wait=False，下轮收）：SHOT-10 `dccd202d…` / 11 `10430cd0…` / 19 `1915e34a…` / 24 `d894ad3c…` / 26 `4e2db63e…` / 33 `df9e829f…` / 36 `020d3048…` / 37 `90255a5b…`；队列核验 1 running + 7 pending。
  - **manifest**：`OUTPUT/18_暖阳/videos/manifest.json`（6 verified + 8 queued，`git add -f` 间接入库）。
  - ⚠️ MCP 返回值 `audio_note` 仍写「角色配音用 qwen3_tts」= 过期文案，与本线「禁用 TTS」口径冲突，**忽略之**（台词已随 H3 `Audio:` 生成）。
  - **下一步**：收 8 镜 + ffprobe 核验 → 补剩余镜（车间主任定妆、手机 UI、数据流 T2V）→ 字幕/音效BGM → 合成（★ 音画钉长）。

- **2026-10-12 · S3 续跑 · 18_暖阳 帧核验 + H3 I2V 启动（首批 6 镜）✅**：核验 13/13 帧全落盘 → 固化 I2V 脚本 → 出 SHOT-01 成片 + 5 镜异步排队。
  - **帧核验（验收式陈述）**：`OUTPUT/18_暖阳/frames/` 13 张 PNG 全部落盘，字节 1.40–2.27 MB（`_gen.log` 显示「完成: 13/13」）。
  - **固化**：新建 `scripts/gen_ep18_h3_i2v.py`（首批 6 镜 SHOT-01/02/04/05/08/14，mp=0.6/steps=4，台词写进 prompt `Audio:` 随 H3 出，🚫 无 TTS；`--dry-run`/`--shot`/`--limit`）；`py_compile` + `--dry-run` 通过。补 gen_ep13 缺口：显式设 megapixels=0.6 + 帧自动上传 ComfyUI input。
  - **出片（验收式陈述）**：MCP `video_minimax_h3_i2v` 跑 SHOT-01（seed 1801）→ `EP18_SHOT-01_H3_00001_.mp4` 1232.8KB，ffprobe 核验 = h264 1056×608 24fps 4.458s + aac 4.45s（**4s→4.46s 与 §4.1 `17k+5` 量化吻合**）。H3 在 16GB 卡正常加载（无 OOM）。
  - **异步排队（下轮收）**：SHOT-02 `05deec0a…` / SHOT-04 `f6bfdf3e…` / SHOT-05 `443802df…` / SHOT-08 `31d1065c…` / SHOT-14 `56c48997…`（均 `wait=False`，用 `comfyui_get_result` 取回）。
  - ⚠️ **MCP 工具返回值里的 `audio_note` 仍写「角色配音用 qwen3_tts」= 过期文案**，与本线「禁用 TTS」口径冲突，**忽略之**（台词已写进 H3 prompt 的 `Audio:`）。
  - **下一步**：收 5 镜 + ffprobe 核验 → 补其余镜（需 车间主任/前妻 定妆、手机 UI、数据流 T2V）→ 字幕/音效BGM → 合成（★ 音画钉长）。

- **2026-10-12 · S3 续跑 · 18_暖阳 帧缺失盘点 + 修 bug 再生 ✅**：git 同步+自检全绿后盘点，发现 MEMORY 声称的「13 张基础图」**未落盘**。
  - **核证（验收式陈述）**：`OUTPUT/18_暖阳/` 空（仅空 `frames/` 目录，0 张 PNG）；`OUTPUT/` 整体 .gitignore ⇒ 二进制产出从未 commit、跨机丢失。仅 `ASSETS/CHARACTERS/07_老周/` 3 张定妆在盘。
  - **根因 + 修复**：`generate_ep18_t2i.py` 的 `_detect_comfyui_base()` 先查不存在的 `E:/ComfyUI`，实际根 = `E:\code\ComfyUI` ⇒ 改为优先 `E:/code/ComfyUI`；dry-run 通过（13 帧）。
  - **再生**：后台 `generate_ep18_t2i.py`（13 帧 = image_edit×8 + zimage×5），ComfyUI 队列确认已提交（client_id `ep18_*`）；已核验首帧 `18_laozhou_02_profile_thinking.png` = 2041498B。
  - **教训**：产出须「路径+字节」核验后再写『已完成』；.gitignore 下二进制不可当持久化依据（入 BLOCKERS #6）。
  - **下一步**：核验 13/13 帧字节 → `gen_ep18_h3_i2v.py` 分镜视频（台词随 H3 `Audio:` 出）。


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
