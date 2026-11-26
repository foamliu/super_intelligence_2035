# _deprecated_2026-10-13.md — 「T2I 首帧 → I2V」旧法产物作废留档

> 依据运维指令区 2026-10-12「推翻旧法：现有成果删除重做，一律回归 stem_fest 标准 R2V」（用户直令 · 最高优先）。
> 本文件只作**删除前的清单 + 字节留档**（`OUTPUT/` 不入 git，删除/重命名不可恢复，故先留档）。

## 1. 已作废/重命名目录

| 原路径（短剧仓） | 处置 | 说明 |
|:--|:--|:--|
| `OUTPUT/13_外骨骼/` | 重命名为 `OUTPUT/_deprecated_t2i_2026-10-13/` | 14 张 T2I 首帧 + 10 条 legacy I2V 视频（旧「去 TTS」重写 + TTS 时代混合产物） |
| `OUTPUT/18_暖阳/` | 已被删（本轮 git status 见 `D OUTPUT/18_暖阳/videos/manifest.json` 未提交删除） | 帧/videos/audio/成片全量作废 |
| `OUTPUT/08_认知矿工/` | 已不存在（仅残留 `ep08_*.log`） | 仅 frames，一并作废 |

## 2. OUTPUT/13_外骨骼 完整清单（重命名前 · 29 文件 / 40,534,556 B ≈ 38.7 MiB）

### frames/（14 张 T2I 首帧 · 23,668,290 B）
- 13_bar_01_aftermath.png — 1,550,753
- 13_lab_01_2017_night.png — 1,783,971
- 13_office_01_exoskeleton_ui.png — 1,719,624
- 13_prop_01_notebook_label.png — 1,611,646
- 13_prop_02_wechat_hao.png — 1,279,256
- 13_sarah_01_desk_explaining.png — 1,932,451
- 13_sarah_02_subway_observing.png — 2,169,935
- 13_sarah_03_bar_aftermath.png — 1,458,922
- 13_shixiong_01_coffee.png — 2,041,280
- 13_subway_01_rush_hour.png — 1,946,883
- 13_ui_01_exoskeleton_clean.png — 1,409,361
- 13_ui_02_double_annotation_xiaozhou.png — 1,698,681
- 13_virtual_audience_01_imaginary_face.png — 1,566,410
- 13_virtual_audience_02_render_vs_real.png — 1,495,530
- manifest.json — 2,803
- _batch.err.log / _batch.out.log — 0 / 3,609

### videos/（10 条 legacy H3 I2V 视频 · 16,863,441 B）
- EP13_SHOT-01_H3_00002_.mp4 — 3,514,532
- EP13_SHOT-02_H3_00001_.mp4 — 2,619,917
- EP13_SHOT-03_H3_00002_.mp4 — 536,264
- EP13_SHOT-04_H3_00001_.mp4 — 2,565,705
- EP13_SHOT-05_H3_00001_.mp4 — 1,334,293
- EP13_SHOT-06_H3_00002_.mp4 — 1,408,307
- EP13_SHOT-07_H3_00001_.mp4 — 1,220,149
- EP13_SHOT-08_H3_00001_.mp4 — 978,524
- EP13_SHOT-09_H3_00001_.mp4 — 1,170,520
- EP13_SHOT-10_H3_00001_.mp4 — 1,515,230
- _gen.err.log / _gen.out.log — 0 / 0

## 3. 保留不动（按指令②）

- `SCENES/13_外骨骼.md`（48 镜逐镜表 · 权威）
- `ASSETS/SHOT_SPECS/13_外骨骼_*.md`（SHOT_SPECS / T2I_Prompts / I2V_Prompts）
- `ASSETS/CHARACTERS/08_莎拉·赵/` · `ASSETS/CHARACTERS/师兄/` · `ASSETS/CHARACTERS/01_林薇/`
- `scripts/`（脚本保留，但 `gen_ep13_h3_i2v.py` 等 I2V 首帧路径**停用**，改 `gen_ep13_h3_r2v.py`）

## 4. 后续

- 13_外骨骼 48 镜按 **R2V 全流程**重做（`gen_ep13_h3_r2v.py`）。
- `_deprecated_t2i_2026-10-13/` 待 R2V 样板打通确认无误后，报运维再清空（不擅自物理删除）。
