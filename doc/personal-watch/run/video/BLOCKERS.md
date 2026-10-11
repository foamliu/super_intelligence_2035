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
- **状态**：⏳ 待修（下一轮 S2 首步）。

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

- **现象**：`EP13_外骨骼_成片_v1.mp4` 107.7s / 47.3MB；`EP13_外骨骼_成片_v2.mp4` 91.1s / 58.1MB（均 1920×1080 · 24fps · h264+aac）。README Step4 的「字幕/调色/验收」仍 ❌。
- **说明**：两版时长差 ~16.6s，需在 S2 核清（疑与 concat 镜头取舍 / `-shortest` 有关）；成片尚未加中英字幕。
- **优先级**：S2 样板章收尾时处理。

---

## 📋 处理原则

- 每轮唤醒先查本文件 + `PLAN.md`，有未决问题优先续做。
- 修好一项即在下方「状态」标注 ✅ 并附 commit。
