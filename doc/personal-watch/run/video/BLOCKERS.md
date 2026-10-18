# BLOCKERS.md — video 线 · 阻塞与环境问题

> 维护：video agent（每轮唤醒更新）· 首次生成 2026-10-11（S1 首跑）

## 🔴 硬阻塞（当前无）

ComfyUI / MCP `comfyui-drama` / ffmpeg 均可用（S1 自检全绿）。**本轮无硬阻塞。**

---

## 🟡 问题清单（待处理 / 环境）

### #1 · 短剧仓历史路径失效（E:/code → D:/Users/Administrator/code）

- **现象**：`E:\code\super_intelligence_2035_short_drama` **已不存在**；项目现位于 `D:\Users\Administrator\code\super_intelligence_2035_short_drama`。
- **影响**：`scripts/` 下所有 EP13 生成脚本硬编码旧路径，直接运行会 `FileNotFoundError`：
  - `synth_ep13.py`（`ROOT = Path("E:/code/...")`）
  - `gen_ep13_h3_i2v.py` / `gen_ep13_ltx_i2v.py` / `gen_ep13_tts.py` / `gen_shixiong_portraits.py`（`WF`/`OUT` 硬编码）
  - `recover_ep13_ltx169.py` / `regen_ep13_ltx_169.py` / `_regen_ep13_h3_720p.py`
- **修复**：统一改为 `Path(__file__).resolve().parent.parent`（参照 `generate_ep13_14_videos.py` 已用此法）。
- **优先级**：S2 开工前必做（否则样板章收尾/放量无法复用脚本）。
- **状态**：✅ 已修（2026-10-11 S2 · 9 个 EP13 脚本改 `Path(__file__).resolve().parent.parent`，全量 py_compile 通过）。

### #2 · MCP `comfyui-drama` 的 project_root 非短剧仓

- **现象**：`comfyui_status` 返回 `project_root: E:\code\stem_fest`（MCP 服务器自身所在项目）。
- **影响**：调用工具时 `output_dir` 传**相对路径**会落到 `E:\code\stem_fest\OUTPUT\...`，而非短剧仓。
- **规避**：目标短剧仓时一律传**绝对路径** `D:\Users\Administrator\code\super_intelligence_2035_short_drama\OUTPUT\...`。
- **状态**：已规避（S1 冒烟即用绝对路径思路验证；下轮起所有产出传绝对路径）。

### #3 · 15 章缺 T2I/I2V Prompt 规格

- **缺口章**：15/16/17/20/26/27/28/29/30/31/32/35/38/40/41（共 15 章，`ASSETS/SHOT_SPECS/` 无对应规格）。
- **说明**：`SCENES/` 逐镜脚本 42 章齐全；但缺规格的章无法直接进 T2I/I2V 批量生成，需先补规格（可由 `SCENES/<章>.md` 逐镜表转换）。
- **影响**：S3 放量到这些章时会被卡。
- **优先级**：低（先完成有规格的 27 章 + 13 样板，再回头补规格）。

### #4 · EP13 成片 v1 vs v2 时长不一致 + 字幕缺失

- **现象**：`EP13_外骨骼_成片_v1.mp4` 107.7s / 47.3MB；`EP13_外骨骼_成片_v2.mp4` 91.1s / 58.1MB（均 1920×1080 · 24fps · h264+aac）。字幕此前缺失。
- **说明**：字幕 ✅ 已补（2026-10-11 S2）：新建 `scripts/gen_ep13_subtitles.py`，libass+微软雅黑烧录硬字幕 → `EP13_外骨骼_成片_v3_字幕.mp4`（91.125s / 1080p / 24fps / h264+aac，`-c:a copy` 保原音轨）。
- **状态**：✅ 字幕已解决。v1/v2 时长差（~16.6s）根因指向混音/镜头拼接时序差异（v3 基于 v2 的 91.13s），已降级为非阻塞项，留待 S4 全片对齐时统一核对。

---

### #5 · EP13 混音时序重叠（师兄两行台词被 Sarah 台词压没）—— 🟠 **已作废（2026-10-11）**

- **现象**：`qwen3_asr` 回读成片 v3，13 条台词中 11 条吻合；但第 6「合法吗？」、第 7「你别把我的代码写进段子里。」两句师兄台词在混音中检不出。
- **核证**：单独 ASR 源 flac `13_tts_shixiong_01_hefa.flac` →「合法吗？」、`13_tts_shixiong_02_code.flac` →「你别把我的代码写进段子里。」均正确 ⇒ 源文件无损，问题在**混音阶段**。
- **根因**：`13_tts_sarah_02_desk.flac` 实际 24.56s，但 `synth_ep13.py` 置其于 t=0、`gen_ep13_subtitles.py` 按 17.99s 窗口分配台词 ⇒ Sarah 台词 18–24.56s 溢出，与师兄台词（18.19s / 19.87s 起）重叠、把两句短台词压没（seg 18.2–22.8s ASR 仍闻「我别管他叫外骨骼」佐证）。
- **影响**：样板章成片 2/13 台词听感缺失（视觉/字幕完整）；不影响「管线已打通」结论，但违反 README §十四「台词同步偏差 < 0.3s」。
- **修复**：~~S3 首轮——合成前 `ffprobe` 校验每条 TTS 实际时长 vs 剧本窗口，超窗时按实际时长重排后续 CUE 起点~~ ⇒ **不再需要**。
- **状态**：🟠 **作废/关闭（2026-10-11 用户令：禁用 TTS）** —— 人物对话改由 **MiniMax H3 随视频一起生成**（写进 prompt 的 `Audio:`），成片音轨**不再叠加 TTS 人声** ⇒ 本问题（TTS 音轨互相重叠压没）**根因消失**。遗留的 EP13 `v3` 成片与 `*_tts_*.flac` 视为 **legacy**，不必再修；时序纪律转为 **音画钉长 + 逐镜内容偏移**（`STEM_FEST_PLAYBOOK.md` §7）。

### #6 · 18_暖阳 13 张基础图缺失（OUTPUT/ 空）—— 🟠 已定位+再生中（2026-10-12）

- **现象**：MEMORY/PLAN 声称「S3 首轮已产出 13 张基础图」，但 `OUTPUT/18_暖阳/` **为空**（`frames/` 空目录，0 张 PNG）。`OUTPUT/` 整体 .gitignore ⇒ 二进制产出从未 commit，换机/清理后丢失。
- **核证**：`ASSETS/CHARACTERS/07_老周/` 仍有 3 张定妆（01 正面/02 半侧面/03 落泪）在盘；`OUTPUT/18_暖阳/frames/` 空。⇒ 前轮「13 张基础图」是**未留路径+字节证据的验收式陈述**，落盘证据未存活。
- **根因（脚本 bug）**：`generate_ep18_t2i.py` 的 `_detect_comfyui_base()` 先查不存在的 `E:/ComfyUI`；ComfyUI 实际根 = `E:\code\ComfyUI` ⇒ 旧脚本产出从未落到本仓。
- **修复**：`_detect_comfyui_base()` 改为优先 `E:/code/ComfyUI`（本机实际根）。
- **再生**：后台跑 `generate_ep18_t2i.py`（13 帧 = image_edit×8 + zimage×5，ComfyUI 队列已确认提交 client_id `ep18_*`）；截至 2026-10-12 已核验首帧 `18_laozhou_02_profile_thinking.png` = 2041498B，其余进行中。
- **核验（2026-10-12）**：13/13 帧全部落盘（字节 1.40–2.27 MB），`_gen.log` 显示「完成: 13/13」。
- **教训**：产出必须「路径+字节」核验后再写『已完成』；`.gitignore` 下的二进制不能当跨机持久化依据。
- **状态**：✅ 已闭环（2026-10-12 · 13/13 帧核验落盘；后续 H3 I2V 已启动）。

### #8 · ComfyUI 重启会清空队列与历史（在途跑批丢失）—— 🟠 已补投（2026-10-18）

- **现象**：2026-10-18 21:28:34 ComfyUI `main.py --port 8188` 重启（PID 10048/10064），`/history` 清空（0 条）、队列 0/0 ⇒ 上一轮排队的 **40 pending 镜**（EP06《情绪》在途批次）全部丢失。
- **根因**：ComfyUI 队列与 `/history` 是**内存态**，进程重启即清空（未启用持久化存储）；本机计划任务 `ComfyUI` 开机自启 + 可能偶发崩溃重启。
- **影响**：在途跑批的镜头需**重新补投**（`--skip-existing` 已落盘的跳过，只补缺失镜）；已落盘到 `OUTPUT/` 的 13 镜不受影响。
- **处置**：核验落盘 13/54 镜在盘 + 参考图/工作流在位 → 补投 `gen_ep06_h3_r2v.py --skip-existing` + `gen_ep06_h3_t2v.py --skip-existing`（41 镜）→ 队列恢复 running 1/pending 40。
- **教训**：① 每轮唤醒先查 `/history` + `/queue` 与落盘数是否一致（`recover_*.py` 报「已回收 X/54」若骤降即为重启迹象）；② 跑批用 `--skip-existing` 幂等可续跑，重启后可一键补投；③ 长跑批中断是常态，判活靠「落盘 mp4 数」而非「队列数」。
- **状态**：🟠 已补投恢复（本轮）；长期建议（可选）→ 报告运维评估 ComfyUI 队列/历史持久化。

### #7 · 13_外骨骼 R2V 缺 14 张场景参考图（补资产）—— ✅ 已闭环（2026-10-13）

- **现象**：`scripts/gen_ep13_h3_r2v.py --dry-run` 报 29 镜缺 `ref2` 场景图：`ASSETS/CHARACTERS/_scene/13_*.png`（backstage/openmic/interview/testcar/annualparty/cafe/office/lab/subway/street/phone/screen_ui/virtual_audience/theatre_door，共 14 张）全缺。
- **影响**：R2V 工作流 `ref_image_1/ref_image_2` 双参考图是硬输入，缺场景图 ⇒ 29 个有角色镜**无法开跑**（R2V 线卡在资产层，非 ComfyUI/脚本）。
- **根因**：本集此前走「T2I 首帧 → I2V」旧法，从未备过 R2V 用的**独立场景参考图**；场景背景只在 `ASSETS/BACKGROUNDS/` 有 `.md` 规格、无 PNG。
- **修复**：`z_image_turbo_t2i` 批量生成 14 张场景图（**无角色场景**，不需要角色一致性，正合 T2I 用途；16:9 1280×720），落盘 `ASSETS/CHARACTERS/_scene/13_*.png`，再复跑 `--dry-run` 到「✅ 所有参考图在位」。
- **优先级**：P0（13_外骨骼重做的唯一硬阻塞）。
- **核验（2026-10-13）**：`scripts/gen_ep13_scenes.py` 批量生成 14/14 落盘 `ASSETS/CHARACTERS/_scene/`（每张 1280×720 · 1.25–2.0 MB）；`gen_ep13_h3_r2v.py --dry-run` 报「✅ 所有参考图在位」并列出 29 镜计划。
- **状态**：✅ 已闭环（2026-10-13 · 场景图补齐 · R2V 29 镜就绪）。


---

## 📋 处理原则

- 每轮唤醒先查本文件 + `PLAN.md`，有未决问题优先续做。
- 修好一项即在下方「状态」标注 ✅ 并附 commit。
