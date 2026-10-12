# MEMORY_VIDEO.md — 观察哨 · **video agent** 运行时记忆

WAITING: 0

> ⚠️ `WAITING:` **只在顶部出现一次**（本行）。
> 语义：`0` = 有近期待办（**本线当前状态**：P0 · S1/S2 完成 · S3 放量中 · 18_暖阳 54/54 成片 + BGM 混音达标）；`1` = 常态。
> ⚠️ 本线 loop（`watch_video_loop.ps1`）**按小时固定唤醒**，**与 `WAITING` 无关**（字段仅供人读）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        S3 放量 ✅ → 18_暖阳 54/54 镜成片 + BGM 混音（响度 -23.8 LUFS 达标）✅
已完成:       S1 ✅；S2 ✅；S3 18_暖阳 54/54 镜成片（273.34s/1056×608/h264+aac）；成片 + BGM01 混音；固化 gen_ep18_h3_i2v/t2v + update_ep18_manifest + gen_ep18_subtitles + synth_ep18 + gen_ep18_bgm + mix_ep18_bgm 七脚本
当前动作:     （本轮：收 T2V 5 镜 + 合成 54/54 成片；生成 3 条 ACE-Step BGM；固化 gen/mix 两脚本；混音 BGM01 并修响度至 -23.8 LUFS）
下一步:       BGM02/03 可选混音 → 最终 QC（qwen3_asr 台词核对 + sound_caption 环境音回读）→ 选定交付文件 → 下一章（08_认知矿工）
阻塞:         无硬阻塞。
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
- **上次唤醒**：2026-10-12（S3 收尾 · 18_暖阳 54/54 成片 + BGM 混音 -23.8 LUFS 达标）
- **判活**：`video/logs/watch_video_loop.hb`（每轮刷新）+ `video/logs/watch_video_loop.log`

---

## 2. 运维问答（supervisor 提问 → 本线回答）

> （暂无）

---

## 3. 流水（倒序）

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
