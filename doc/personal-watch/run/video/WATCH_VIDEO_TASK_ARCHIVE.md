# WATCH_VIDEO_TASK_ARCHIVE.md — 观察哨 · video agent 任务书 · 已闭合历史运维指令归档

> 本文件归档 `WATCH_VIDEO_TASK.md` 中**已闭合**（工作已完成 / 被后续指令覆盖）的历史运维指令，
> 从主任务书移出以控制体积（目标 ≤32KB · 红线 40KB）。**仅作历史留档，不再作为当前指令执行**。
> 当前唯一生效指令 = `WATCH_VIDEO_TASK.md` 顶部的「2026-10-12 推翻旧法·R2V 重做」块。

---

### 🆕 运维指令 · 2026-10-12（🎯 **流水线改判：角色镜头弃「先出首帧→I2V」，直接用定妆照 + H3 R2V**）· 用户直令 · ⭐ 最高优先 · 覆盖 `PIPELINE.md §1/§2`

> **用户原话（2026-10-12）**：「**告诉 video 不要用先制作首帧、然后生成视频的方式。直接用任务定妆照作为参考，用 MiniMax H3 r2v 模型生成视频。**」
> **改判（即日生效）**：**取消「① 分镜帧(T2I) → ② I2V(首帧图)」这条主链路** ⇒ **改为「定妆照(参考图) → H3 R2V 直出视频」**。

**① 角色/人物镜头（新主链路）**：
- 🚫 **不再**用 `image_edit_longcat` 先出首帧、再用 `video_minimax_h3_i2v` 喂首帧。
- ✅ **直接**用 **`ASSETS/CHARACTERS/<角色>/<定妆照>.png`**（如 `13_Mira Carter/主定妆照.png`）作 **参考图** → **`video_minimax_h3_r2v`**（MCP `comfyui-drama`）。
- **参数**：`ref_image_1` = 主角定妆照（prompt 用 `<Picture 1>` 引用）；**多角色**再加 `ref_image_2`（`<Picture 2>`）；`megapixels≤0.4`（双参考图 · 16GB 红线）· `aspect_ratio="16:9 (Widescreen)"` · `duration≈5s` · `steps=20`。
- **prompt 写法**：`<Picture 1>` 指代角色 + `CUT 1/CUT 2` 分段 + 镜头运动 + **`Audio:` 台词（🚫 仍不用 TTS，随 H3 出）**。
- ⚠️ **无定妆照的角色**（只有 `定妆规格.md` 未生成图）⇒ 先补齐定妆照，或**临时回退** `image_edit_longcat` 出参考图；**如实记**。

**② 非人物镜头（场景/UI/道具）**：**首选 R2V**（用背景/关键帧参考图）；**无参考图**时可 `video_minimax_h3_t2v`；**总之不再默认「先 T2I 首帧 → I2V」**。

**③ 即日切换 & 回溯**：
- **`13_外骨骼`（本轮在跑）**：**人物镜改 R2V 重做**；**已生成的 T2I 首帧弃用**（可留作 R2V 提示/对色，**不计入成片链路**）。
- 后续所有章一律按新链路。

**④ 交付与记录**：
- 更新 **`run/video/PIPELINE.md`**（§1 七环链路 ①→② 改为「参考图→R2V 直出」；§2 参数表同步；**注明 R2V 为角色镜头主用**）。
- 更新 **`run/video/PLAN.md`**（§3 表「帧」列语义改注为「参考图/R2V」）+ `run/MEMORY_VIDEO.md` + `run/daily-memories-video/<date>.md`。
- 固化脚本 **`gen_epXX_h3_r2v.py`**（照 `gen_ep18_h3_i2v.py` 范式，改调 R2V + 传定妆照路径）。

**⑤ 纪律**：🚫 无 TTS · `megapixels≤0.6`（R2V 双图建议 ≤0.4）· ≥5MB 不入 git · 「已产出」须落盘核验（路径+字节+`ffprobe`）· 验收六项门禁照旧（`qwen3_asr` 核台词 / `sound_caption` 回读）。

### 🆕 运维指令 · 2026-10-12（🎬 下一章改判：**「暖阳之后做外骨骼」= `13_外骨骼`**）· 用户直令 · ⭐ 最高优先

> **用户原话（2026-10-12）**：「video：**暖阳之后做外骨骼**。」
> **口径**：**覆盖** `PLAN.md §3/§4` 里原定的「下一章 = `08_认知矿工`」⇒ **下一章改做 `13_外骨骼`**（48 镜）。

**① 顺序（硬）**：
1. **先收尾 `18_暖阳`**：按 `PLAN.md §4.1` 完成 **最终 QC**（`qwen3_asr` 台词核对 + `sound_caption` 环境音回读）→ **选定交付文件**（`EP18_暖阳_成片_BGM01.mp4` 等）；BGM02/03 可选。
2. **再做 `13_外骨骼`**（下一章）：**排在 `08_认知矿工` 之前**。

**② `13_外骨骼` 关键前提（必读）**：
- 素材**齐全**：`SCENES/13_外骨骼.md`（48 镜）+ `ASSETS/SHOT_SPECS/13_外骨骼_{SHOT_SPECS,T2I_Prompts,I2V_Prompts}.md`（规格不缺）。
- ⚠️ **旧原型音轨 = legacy TTS**（`gen_ep13_tts.py` / `gen_ep13_ai_voice.py` 时期产物）—— **违反 2026-10-11「禁用 TTS」用户令** ⇒ **🚫 不得沿用该音轨**；**必须按新口径重做**：**台词/人声全部由 MiniMax H3 随视频生成**（写进 prompt 的 `Audio:`），合成时**不再叠 TTS**。
- ⚠️ **旧 EP13 脚本硬编码旧路径 `E:\code\…`**（`PLAN.md §5`）⇒ 复用前先修路径为现行 `D:\Users\Administrator\code\super_intelligence_2035_short_drama\…`（照 `synth_ep18.py` 的 `ROOT = Path(__file__).resolve().parent.parent` 范式）。
- ⚠️ **核实现存产物**：当前新仓 `OUTPUT/` 仅见 `08_认知矿工`（仅 frames）与 `18_暖阳`，**未见 `13_外骨骼` 产物** —— 请**自行核实**（含 `manifest.json` / 旧路径残留），**以实际落盘为准**，并如实记「13 现有产物 = 什么 / 缺什么」。

**③ 做法（照 EP18 已固化范式）**：T2I 帧（人物用 `image_edit_longcat` + 定妆照；非人物用 `z_image_turbo_t2i`）→ **H3 I2V 片段（含 Audio 台词）** → BGM/音效 → 字幕 → 合成 → **六项验收**（文件存在 + 字节 > 0 + `ffprobe` 时长/分辨率 + `qwen3_asr`/`sound_caption` 抽检）。一次 1 章、`wait=False` 异步。

**④ 交付与记录**：更新 `run/video/PLAN.md`（§3 表 13 行改为「**S3 重做中（新口径·去 TTS）**」、§4 下一步改判为 `13_外骨骼`）· `run/MEMORY_VIDEO.md` · `run/daily-memories-video/<date>.md`；成片入短剧仓 `OUTPUT/13_外骨骼/`。

**⑤ 纪律**：🚫 无 TTS；≥5MB 不入 git；「已产出」须落盘核验（路径 + 字节）；每轮有看得见的进展。

---

### 🆕 运维指令 · 2026-10-11（🎬 **立线：`video` = 基于 ComfyUI 制作视频**；首个任务 = 完成《超级智能2035》视频制作）· 用户直令 · ⭐ 最高优先

> **用户原话（2026-10-11）**：「在 personal watch 目录下建个新的 agent 任务书和 loop … **这个新的任务叫 `video`，使命是基于 ComfyUI 制作视频**。第一项任务是：**完成超级智能2035 视频的制作** `D:\Users\Administrator\code\super_intelligence_2035_short_drama`。」

**① 使命（本线唯一目的）**：**用本机 ComfyUI 把《超级智能2035》短剧项目做成「可发布的视频成片」**。
- 主战场 = **短剧项目仓** `D:\Users\Administrator\code\super_intelligence_2035_short_drama`（42 章 · 逐镜分镜脚本已全部完成，**2203 镜 / 约 3h03m**）。
- 工具 = **本机 ComfyUI**（`http://127.0.0.1:8188`）+ **MCP `comfyui-drama`**（见 §0）。

**② 首个任务（P0）= 完成《超级智能2035》视频制作**
- **定义「完成」**：**每一章**都要产出**成片视频文件**（`OUTPUT/<章>/videos/` 或项目约定的成片路径），由「分镜帧 → I2V 视频片段（**台词由 H3 随视频一起生成 · 不用 TTS**）→ BGM/音效 → 合成（含字幕）」这条链路构成；最终按章汇总为可播放的 mp4。
- **不要一上来摊全 42 章** —— 先做「**1 章端到端样板**」（建议从**素材最全的章**开始，如 `OUTPUT/13_外骨骼/` 已有产物），把**流水线跑通并固化脚本**，再**按章滚动放量**。
- **每轮唤醒都要有「看得见的进展」**：要么新增/修复脚本，要么新增成片产物，要么在 `run/video/PLAN.md` 推进状态。🚫 **不得空转**。

**③ 交付物与记录**
- **本线记录**（入 `super_intelligence_2035` 仓）：`run/video/PLAN.md`（总计划 + 逐章状态表）· `run/video/PIPELINE.md`（固化的流水线/SOP）· `run/video/BLOCKERS.md`（阻塞与环境问题）· `run/MEMORY_VIDEO.md` · `run/daily-memories-video/<date>.md`。
- **成片与素材**（入短剧仓）：按项目既有约定（`OUTPUT/`、`ASSETS/`、`scripts/`）；**大文件（视频/音频/模型）不入 git**（遵项目 `.gitignore` + 本线体积纪律，见 §5）。

**④ 验收（硬）**：每个「已生成」的产物都要**亲眼核验存在**：文件存在 + **字节数 > 0** + 用 `ffprobe/ffmpeg` 读**时长/分辨率**（视频）或 `sound_caption` / `qwen3_asr` 回读（音频）。🚫 **不许把「提交成功」当「产出成功」**。

**⑤ 优先级**：本批 = **P0**；本线暂**无其他批次**，全部精力投入「完成成片」。

**⑥ 经验并入（2026-10-11）**：已并入 `stem_fest`（同机·同工具·已全片交付）实战经验 ⇒ **§4** + `run/video/STEM_FEST_PLAYBOOK.md`。**先读 §4 再动手**。

**⑦ 纪律 · 2026-10-11（用户令）**：🚫 **禁用 TTS** —— **视频里的人物对话全部由 MiniMax H3 随视频一起生成**（写进 prompt 的 `Audio:`）。`qwen3_tts`/任何 TTS **不得**用于台词与旁白；合成时**不再叠人声**。口径已并入 §3 铁律、§1 链路、**§4.5**。