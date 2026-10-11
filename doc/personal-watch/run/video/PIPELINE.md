# PIPELINE.md — video 线 · 固化流水线 / SOP

> 维护：video agent · 首次生成 2026-10-11（S2 样板章 `13_外骨骼` 端到端打通后固化）
> 目的：把「分镜帧 → I2V 视频（**台词随 H3 一起生成 · 🚫 不用 TTS**）→ BGM/音效 → 合成 → 字幕 → 验收」固化成可复用 SOP。
> ⚠️ **2026-10-11 用户令：本线禁用 TTS**（人物对话全部由 MiniMax H3 随视频生成）——本文件已按此改写；EP13 的 TTS 环节/产物一律视为 **legacy**。
> 姊妹文件：`PLAN.md`（逐章状态）· `BLOCKERS.md`（阻塞/环境）。

---

## 0. 环境与铁律（先读）

| 项 | 值 |
|:--|:--|
| ComfyUI | `http://127.0.0.1:8188`（本机 · RTX 4090 Laptop 16GB） |
| MCP | `comfyui-drama`（工具已封装 19 个工作流，**用工具跑，勿手拼 API**） |
| ffmpeg/ffprobe | 合成 / 探测 / 验收 |
| Python | `py -3.10` |

铁律（违反会翻车）：

1. **绝对路径**：MCP `project_root` = `E:\code\stem_fest`；目标短剧仓一律传**绝对路径**
   `D:\Users\Administrator\code\super_intelligence_2035_short_drama\OUTPUT\...`。
2. **VRAM megapixels ≤ 0.6**：`video_minimax_h3_i2v/r2v/t2v` 的 `megapixels` 必须 ≤ 0.6（≈1056×608）；0.92/720p 必 OOM。要 1080p 走 `video_upscale_seedvr2`。
3. 🚫 **禁用 TTS（2026-10-11 用户令）**：**人物对话全部由 MiniMax H3 随视频一起生成**（写进 prompt 的 `Audio:`）；⛔ `qwen3_tts` / 任何 TTS **不得**用于台词与旁白；合成时**不再叠人声**（人声已在视频轨内）。
4. **体积红线**：单文件 ≥5MB 不入 git（视频/音频/大图）；靠 `manifest.json` 间接入库。
5. **长任务异步**：视频单条 5–15min，用 `wait=False` + `comfyui_get_result`；一轮排 3–6 条，别堵死队列。

---

## 1. 端到端链路（七环）

```
SCENES/<章>.md 逐镜脚本
   │ ① 分镜帧（T2I）
   ├─ 人物镜：image_edit_longcat(定妆照)      ├─ 非人物：z_image_turbo_t2i
   │ ② 视频片段（I2V）
   └─ video_minimax_h3_i2v（首帧图 + 运动描述；megapixels≤0.6）
   │ ③ 台词（🚫 **不用 TTS** —— 随 ② 一起由 H3 生成，写进 prompt 的 `Audio:`）
   │ ④ BGM / 音效
   ├─ ace_step_t2audio(BGM)    ├─ stable_audio_3_sfx / woosh_sfx(音效)
   │ ⑤ 合成
   └─ ffmpeg：concat 视频轨 + amix(BGM@0.22)（**人声已在视频轨内**；范式 synth_ep13.py 去掉 TTS 输入）
   │ ⑥ 字幕
   └─ 中英双语 .srt → libass+微软雅黑烧录硬字幕（范式：scripts/gen_ep13_subtitles.py）
   │ ⑦ 验收
   └─ ffprobe 时长/分辨率 + qwen3_asr 核对旁白 + sound_caption 回读混音
```

---

## 2. 各环节参数（样板章实测值）

### ① 分镜帧
- 非人物：`z_image_turbo_t2i`（`width=1280, height=720, steps=8, cfg=1.0, batch_size=1`）。
- 人物（角色一致性）：`image_edit_longcat`（`image`=定妆照 `ASSETS/CHARACTERS/<角色>/...png`，`prompt`=新场景描述，`steps=50, cfg=4.5`）。

### ② 视频片段
- `video_minimax_h3_i2v`：`prompt` 含 `SHOT 段 + 镜头运动 + Audio 环境音`；`image`=首帧图；`duration`≈5s；`aspect_ratio="16:9 (Widescreen)"`；`megapixels=0.6`；`steps=20`。
- 多角色锁定：`video_minimax_h3_r2v`（`megapixels=0.4`，`<Picture 1>`/`<Picture 2>` 引用）。

### ③ 台词（🚫 **不用 TTS** · 随 ② 一起由 H3 生成）
- **人物对话全部写进 H3 的 `prompt`** ⇒ `Audio:` 段只放 **L1 台词原文**（一人一镜一句/多句；环境声用 `（后期）` 标记、拼 prompt 前用 `strip_late_audio()` 剔除）。
- ⛔ **禁用** `qwen3_tts` 及任何 TTS。台词**净字数必须匹配镜头时长**（`need ≈ 字数÷语速 + 0.8s`；太短会被 H3 补话/乱音，见 stem_fest 镜 7 教训）。
- ⚠️ `gen_ep13_tts.py` / `gen_ep13_ai_voice.py` 与 EP13 的 `*_tts_*.flac` 产物 = **legacy**（不再使用、不再混入成片）。

### ④ BGM / 音效
- BGM：`ace_step_t2audio`（`tags`=氛围总谱，`lyrics`=结构脚本，`duration` 对齐成片时长）。
- 音效：`stable_audio_3_sfx`（`steps=8, cfg=1.0`）或 `woosh_sfx`（`steps=0, cfg=-1` 用官方建议值）。

### ⑤ 合成（synth_ep13.py 范式）
```bash
# 1) 拼接视频轨（★ 音频必须钉长到「帧数÷24」，见 STEM_FEST_PLAYBOOK §7）
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c:v libx264 -crf 18 -preset fast -an video_track.mp4
# 2) 混音：以「拼接后的原音轨」为底（已含 H3 台词）→ 只叠 BGM / 音效层，🚫 不加任何 TTS
#    BGM@volume=0.22 + sidechaincompress(用成片音轨当侧链) + alimiter(守 -1dBFS) → aac
# 3) 合成
ffmpeg -y -i video_track.mp4 -i bgm.mp3 -i sfx.mp3 -filter_complex "<钉长后的原音轨> + BGM + 音效 → amix → alimiter" -map 0:v -map "[outa]" -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```
> ⚠️ 人声不再由音轨提供 ⇒ **旧「TTS 混音时序」问题（BLOCKERS #5）作废**；余下的时序纪律只有 **拼接时给每镜音轨钉长** 与 **逐镜测内容偏移**（STEM_FEST_PLAYBOOK §7）。

### ⑥ 字幕（gen_ep13_subtitles.py 范式）
- 中英双语 `.srt`（时间轴取自**逐镜表镜头时长 / 音频钉长口径**；**不再依赖 TTS 时长**）。
- 烧录：`ffmpeg -vf "subtitles=xx.srt:fontsdir='C\:/Windows/Fonts':force_style='FontName=Microsoft YaHei,FontSize=21,...'" -c:a copy`（libass + 微软雅黑，无 tofu）。

### ⑦ 验收（六项门禁）
| 门禁 | 手段 | 通过标准 |
|:--|:--|:--|
| 时长/分辨率 | `ffprobe` | 1920×1080 / 24fps / h264+aac；时长与脚本一致 |
| 台词（H3 同期） | `qwen3_asr` | 逐字比对各镜台词原文；**多余语音**（H3 补话）也要定位 |
| 混音 | `sound_caption` | BGM/氛围在轨，无静音段 |
| 字幕 | 抽帧 + libass 日志 | 字形在位、零 "Glyph not found" |
| 台词同步 | 对照 ASR 时间窗 | 偏差 < 0.3s（README §十四） |

---

## 3. 脚本索引（短剧仓 `scripts/`）

| 脚本 | 作用 |
|:--|:--|
| `synth_ep13.py` | 样板章合成（concat + amix 混音）——**范式** |
| `gen_ep13_subtitles.py` | 中英双语 .srt + libass 烧录——**范式** |
| `gen_ep13_bgm.py` / `gen_ep13_h3_i2v.py` | BGM / I2V 生成（**台词随 H3 一起出**） |
| ~~`gen_ep13_tts.py`~~ / ~~`gen_ep13_ai_voice.py`~~ | 🚫 **legacy·禁用**（TTS，2026-10-11 起不再使用） |
| `generate_ep13_14_videos.py` | 已用 `Path(__file__).resolve().parent.parent` 相对定位——**路径范式** |

> 放量新章时：按上述范式复制为 `gen_epXX_*.py` + `synth_epXX.py`（**去掉 TTS 环节**），`ROOT` 统一用 `Path(__file__).resolve().parent.parent`。

---

## 4. 踩坑史（必记）

1. **路径别猜**：短剧仓已从 `E:\code\` 迁至 `D:\Users\Administrator\code\`，脚本一律 `Path(__file__).resolve().parent.parent`（LESSONS_LEARNED）。
2. **megapixels ≤ 0.6**：16GB VRAM 红线（0.92 必 OOM）。
3. 🚫 **禁用 TTS（2026-10-11 用户令）**：人物对话随 H3 生成 ⇒ 旧的「TTS 实际时长 ≠ 剧本窗口」问题**作废**（BLOCKERS #5 关闭）；时序改盯 **音画钉长**（STEM_FEST_PLAYBOOK §7）。
4. **验收式陈述**：说"生成/对齐"必须给 路径+字节+时长 / 回读证据。
