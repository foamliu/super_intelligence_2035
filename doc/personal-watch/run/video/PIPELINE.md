# PIPELINE.md — video 线 · 固化流水线 / SOP

> 维护：video agent · 首次生成 2026-10-11（S2 样板章 `13_外骨骼` 端到端打通后固化）
> 目的：把「分镜帧 → I2V 视频 → TTS 旁白 → BGM/音效 → 合成 → 字幕 → 验收」七环固化成可复用 SOP。
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
3. **TTS 固定 speaker + seed**：同一角色跨集固定 `speaker` 与 `seed`，否则音色漂移。
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
   │ ③ 旁白 TTS
   └─ qwen3_tts（固定 speaker+seed）
   │ ④ BGM / 音效
   ├─ ace_step_t2audio(BGM)    ├─ stable_audio_3_sfx / woosh_sfx(音效)
   │ ⑤ 合成
   └─ ffmpeg：concat 视频轨 + amix(BGM@0.22 + TTS)（范式：scripts/synth_ep13.py）
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

### ③ 旁白 TTS
- `qwen3_tts`：`speaker`（Sarah→Vivian；师兄→Dylan）；`instruct` 写音色/表演指令；**同角色固定 `seed`**；`audio_format=flac`。

### ④ BGM / 音效
- BGM：`ace_step_t2audio`（`tags`=氛围总谱，`lyrics`=结构脚本，`duration` 对齐成片时长）。
- 音效：`stable_audio_3_sfx`（`steps=8, cfg=1.0`）或 `woosh_sfx`（`steps=0, cfg=-1` 用官方建议值）。

### ⑤ 合成（synth_ep13.py 范式）
```bash
# 1) 拼接视频轨
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c:v libx264 -crf 18 -preset fast -an video_track.mp4
# 2) 混音：BGM@volume=0.22 + 各 TTS(adelay=start_ms|start_ms) → amix=inputs=N:duration=longest:normalize=0
# 3) 合成
ffmpeg -y -i video_track.mp4 -i bgm.mp3 -i tts1.flac ... -filter_complex "..." -map 0:v -map "[outa]" -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```
> ⚠️ **混音时序对齐**：每条 TTS 先 `ffprobe` 实际时长，再定下一条 CUE 起点；**勿**假设台词窗口=剧本时间（见 BLOCKERS #5 教训）。

### ⑥ 字幕（gen_ep13_subtitles.py 范式）
- 中英双语 `.srt`（时间轴取自 TTS 实际时长 + 下一 CUE 起点）。
- 烧录：`ffmpeg -vf "subtitles=xx.srt:fontsdir='C\:/Windows/Fonts':force_style='FontName=Microsoft YaHei,FontSize=21,...'" -c:a copy`（libass + 微软雅黑，无 tofu）。

### ⑦ 验收（六项门禁）
| 门禁 | 手段 | 通过标准 |
|:--|:--|:--|
| 时长/分辨率 | `ffprobe` | 1920×1080 / 24fps / h264+aac；时长与脚本一致 |
| 旁白 | `qwen3_asr` | 逐字比对字幕原文，缺失台词须定位 |
| 混音 | `sound_caption` | BGM/氛围在轨，无静音段 |
| 字幕 | 抽帧 + libass 日志 | 字形在位、零 "Glyph not found" |
| 台词同步 | 对照 ASR 时间窗 | 偏差 < 0.3s（README §十四） |

---

## 3. 脚本索引（短剧仓 `scripts/`）

| 脚本 | 作用 |
|:--|:--|
| `synth_ep13.py` | 样板章合成（concat + amix 混音）——**范式** |
| `gen_ep13_subtitles.py` | 中英双语 .srt + libass 烧录——**范式** |
| `gen_ep13_tts.py` / `gen_ep13_bgm.py` / `gen_ep13_h3_i2v.py` | TTS / BGM / I2V 生成 |
| `generate_ep13_14_videos.py` | 已用 `Path(__file__).resolve().parent.parent` 相对定位——**路径范式** |

> 放量新章时：按上述范式复制为 `gen_epXX_*.py` + `synth_epXX.py`，`ROOT` 统一用 `Path(__file__).resolve().parent.parent`。

---

## 4. 踩坑史（必记）

1. **路径别猜**：短剧仓已从 `E:\code\` 迁至 `D:\Users\Administrator\code\`，脚本一律 `Path(__file__).resolve().parent.parent`（LESSONS_LEARNED）。
2. **megapixels ≤ 0.6**：16GB VRAM 红线（0.92 必 OOM）。
3. **混音时序对齐**：TTS 实际时长 ≠ 剧本窗口 → 台词重叠压没（BLOCKERS #5）。
4. **验收式陈述**：说"生成/对齐"必须给 路径+字节+时长 / 回读证据。
