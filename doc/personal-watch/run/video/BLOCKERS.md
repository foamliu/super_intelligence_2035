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

### #5 · EP13 混音时序重叠（师兄两行台词被 Sarah 台词压没）

- **现象**：`qwen3_asr` 回读成片 v3，13 条台词中 11 条吻合；但第 6「合法吗？」、第 7「你别把我的代码写进段子里。」两句师兄台词在混音中检不出。
- **核证**：单独 ASR 源 flac `13_tts_shixiong_01_hefa.flac` →「合法吗？」、`13_tts_shixiong_02_code.flac` →「你别把我的代码写进段子里。」均正确 ⇒ 源文件无损，问题在**混音阶段**。
- **根因**：`13_tts_sarah_02_desk.flac` 实际 24.56s，但 `synth_ep13.py` 置其于 t=0、`gen_ep13_subtitles.py` 按 17.99s 窗口分配台词 ⇒ Sarah 台词 18–24.56s 溢出，与师兄台词（18.19s / 19.87s 起）重叠、把两句短台词压没（seg 18.2–22.8s ASR 仍闻「我别管他叫外骨骼」佐证）。
- **影响**：样板章成片 2/13 台词听感缺失（视觉/字幕完整）；不影响「管线已打通」结论，但违反 README §十四「台词同步偏差 < 0.3s」。
- **修复**：S3 首轮——合成前 `ffprobe` 校验每条 TTS 实际时长 vs 剧本窗口，超窗时按实际时长重排后续 CUE 起点（或缩短/重录该句）。
- **状态**：🟡 待修（入 S3 首轮）。

---

## 📋 处理原则

- 每轮唤醒先查本文件 + `PLAN.md`，有未决问题优先续做。
- 修好一项即在下方「状态」标注 ✅ 并附 commit。
