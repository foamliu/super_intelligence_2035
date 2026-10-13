# PIPELINE.md — video 线 · 固化流水线 / SOP

> 维护：video agent · 首次生成 2026-10-11 · **2026-10-12 推翻旧法改 R2V**
> 目的：把「参考图（定妆照/合影 + 场景图）→ **R2V 直出视频**（**台词随 H3 一起生成 · 🚫 不用 TTS**）→ BGM/音效 → 合成 → 字幕 → 验收」固化成可复用 SOP。
> ⚠️ **2026-10-12 用户直令（最高优先）：推翻旧法** —— 「① T2I 出首帧 → ② H3 I2V」**不是 stem_fest 标准** ⇒ **作废删除重做**：
> **有角色镜 → `video_minimax_h3_r2v`（唯一入选路线）；无角色镜 → `video_minimax_h3_t2v`。** 旧 I2V 首帧路径全部停用。
> ⚠️ **2026-10-11 用户令：本线禁用 TTS**（人物对话全部由 MiniMax H3 随视频生成）；EP13 的 TTS 环节/产物一律视为 **legacy**。
> 姊妹文件：`PLAN.md`（逐章状态）· `BLOCKERS.md`（阻塞/环境）· `STEM_FEST_PLAYBOOK.md`（§3 参数/路由权威）。

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

## 1. 端到端链路（七环 · R2V 直出）

```
SCENES/<章>.md 逐镜脚本（7 列 · 参考图提示列 = 唯一权威）
   │ ① 参考图准备（★ 按「在场人数」给图 · 硬）
   ├─ 人物镜：定妆照(一人一张) / 合影(程序拼版，🚫 不经 image_edit 转)
   └─ 场景图：场景参考图（🚫 别用空场景）
   │ ② 视频片段（★ R2V 直出 · 唯一入选路线）
   ├─ 有角色镜：video_minimax_h3_r2v（ref_image_1=定妆照/合影 <Picture 1>；ref_image_2=场景图 <Picture 2>；megapixels≤0.4）
   └─ 无角色镜：video_minimax_h3_t2v（megapixels≤0.6）
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

### ① 参考图准备（按「在场人数」给图 · 硬）
- **定妆照 = 外形的唯一权威**（一人一张 `ASSETS/CHARACTERS/<角色>/<slug>_hero_v01.png`，命名全 ASCII）。
- **合影 = 程序拼版**（各定妆照裁人 → 并排拼一张宽图 → 入库 `ASSETS/CHARACTERS/_group/`），🚫 **不经 `image_edit_longcat` 转**（转过的合影身份失真）。
- **场景图**：场景参考图 `ASSETS/CHARACTERS/_scene/` 或背景图；🚫 **别用空场景**（模型会优先渲染空背景）。
- **参考图规则**：画面该出现几人，参考图就须含几张脸——1 人特写＝单人定妆照 + 场景图；2 人＝二人合影；纯场景＝场景图（走 T2V）。

### ② 视频片段（★ R2V 直出）
- **有角色镜**：`video_minimax_h3_r2v`（`ref_image_1`=定妆照/合影 `<Picture 1>`，`ref_image_2`=场景图 `<Picture 2>`；`megapixels=0.4`；`steps=10` 角色镜默认；`aspect_ratio="16:9 (Widescreen)"`；`duration` 照抄表内时长；`prompt`=`CUT 1:` + 景别 + 动作 + `Audio:` 只放 L1 台词原文）。
- **无角色镜**：`video_minimax_h3_t2v`（`megapixels≤0.6`）。
- 🚫 **不再** `image_edit_longcat` 先出首帧、再 `video_minimax_h3_i2v` 喂首帧。

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
| `gen_ep13_h3_r2v.py` | ★ **R2V 直出**（定妆照/合影 + 场景图 → H3 R2V；台词随 H3）——**角色镜头主用** |
| `gen_epXX_h3_t2v.py` | 无角色镜 T2V（`gen_ep18_h3_t2v.py` 已固化） |
| ~~`gen_ep13_h3_i2v.py`~~ / ~~`generate_ep13_t2i.py`~~ / ~~`gen_ep18_h3_i2v.py`~~ | 🚫 **legacy·停用**（I2V 首帧路径，2026-10-12 起作废） |
| ~~`gen_ep13_tts.py`~~ / ~~`gen_ep13_ai_voice.py`~~ | 🚫 **legacy·禁用**（TTS，2026-10-11 起不再使用） |
| `gen_ep13_bgm.py` | BGM（ACE-Step） |
| `generate_ep13_14_videos.py` | 已用 `Path(__file__).resolve().parent.parent` 相对定位——**路径范式** |

> 放量新章时：按 `gen_ep13_h3_r2v.py` 范式复制为 `gen_epXX_h3_r2v.py`（有角色镜）+ `gen_epXX_h3_t2v.py`（无角色镜）+ `synth_epXX.py`（**去掉 TTS 环节**），`ROOT` 统一用 `Path(__file__).resolve().parent.parent`。

---

## 4. 踩坑史（必记）

1. **路径别猜**：短剧仓已从 `E:\code\` 迁至 `D:\Users\Administrator\code\`，脚本一律 `Path(__file__).resolve().parent.parent`（LESSONS_LEARNED）。
2. **megapixels ≤ 0.6**：16GB VRAM 红线（0.92 必 OOM）。
3. 🚫 **禁用 TTS（2026-10-11 用户令）**：人物对话随 H3 生成 ⇒ 旧的「TTS 实际时长 ≠ 剧本窗口」问题**作废**（BLOCKERS #5 关闭）；时序改盯 **音画钉长**（STEM_FEST_PLAYBOOK §7）。
4. **验收式陈述**：说"生成/对齐"必须给 路径+字节+时长 / 回读证据。
