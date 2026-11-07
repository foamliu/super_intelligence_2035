# MEMORY_VIDEO.md — 观察哨 · **robot 线**（原 video 线转型）运行时记忆

WAITING: 0

> ⚠️ `WAITING:` 只在顶部出现一次。语义：`0` = 有近期待办（等用户 5 条回复）；`1` = 常态。本线 loop 按小时唤醒，与 `WAITING` 无关（字段仅供人读）。
> 纪律：正文/快照/流水里绝不再出现以 `WAITING:` 开头的行。

> 🔄 **本线已转型（2026-11-07 11:10 用户令）**：停做短视频 → **基于华为手机的 AI 机器人**，调用大模型/智能体辅导初中生功课。
> 权威指令 = `WATCH_VIDEO_TASK.md` 顶部「2026-11-07 11:10」块；工作目录 = `run/robot/`；旧视频制作**全部终止并冻结**（`video/`、`OUTPUT/` 不删不动）。
> 旧视频时代记忆已归档 → `MEMORY_VIDEO_ARCHIVE.md`（88KB，只读存档，不再推进）。

---

## 📊 进度快照（每次唤醒必须更新）

```
PHASE:        L0 设备通路（PC mock 已跑通）→ 等用户 5 条回复做真机化
已完成:       P0 结论✅（adb/hdc 未装、手机未连）；路线= R3 手机+PC 协同✅；最小 demo 真跑通✅（题图→OCR→分步引导→TTS 出声）
第2轮复验:    P0 结论复验✅；链路复跑通✅；发现 OCR 最弱一环⚠️（llava 读纯算式对/中文+算式混易错）
当前动作:     第 2 轮：真实命令复验 P0+demo；定位 OCR 弱环；诚实回写 P0/ROADMAP/host 文档；commit+push(robot:)
下一步:       收用户 5 条回复 → 复验 hdc/adb → 真机拍照/出声（L0 真机化）；修复 qwen3-vl:32b 404（ollama pull 20GB）；补 100 题库跑 L1
阻塞:         ⏳ 手机未连本机 + 型号/系统版本未知（需用户回复）；qwen3-vl:32b /api/chat 报 404（OCR 最弱一环的根因）
ERROR_COUNT:  0
```

---

## 1. 状态头

- **线**：robot（原 video；**基于华为手机的 AI 家教机器人**）
- **使命**：手机成为「看得见、听得懂、说得出」的家教入口——拍题 → 识别 → 分步引导（**不代写**）→ 语音讲解 → 错题本/学情画像
- **任务书**：`WATCH_VIDEO_TASK.md`（只读 · = 每轮 prompt）
- **loop**：`watch_video_loop.ps1`（Win11 本机 `hx-c1000` · 每小时对齐整点唤醒；计划任务 `WatchVideoLoop`）
- **工作目录**：`run/robot/`（`P0_设备通路.md` / `ROADMAP.md` / `app/` 手机端 / `host/` PC agent / `eval/` 题库 / `proto/` mock）
- **记录仓**：`D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\`
- **ComfyUI**：**已冻结（Disabled），不碰视频流水线**
- **上次唤醒**：2026-11-07（第 1 轮 · P0 + 路线 + 最小 demo）

## 2. 分层目标与状态（L0-L4）

| 层 | 目标 | 判据 | 状态 |
|:--|:--|:--|:--|
| L0 设备通路 | 手机与开发机连通 | 装包/截屏/拍照/出声各一条命令真实产物 | 🟡 PC mock 通，真机待连 |
| L1 单题闭环 | 拍题→OCR→结构化→LLM 分步引导→TTS | 20 题 ≥15 识别正确，引导不含答案 | 🟡 1 题 demo 通 |
| L2 智能体 | 工具调用/多轮追问 | 5 工具可调、3 轮一致 | ⬜ |
| L3 学情 | 错题本+画像+家长摘要 | 本地可导出 HTML | ⬜ |
| L4 形态 | 桌面实体机器人 | 待用户确认 | ⬜ |

## 3. 关键事实（本线技术栈 · 实测）

- **本机推理栈（零采购/零外部账号，全部可用）**：
  - `ollama` 0.40.15：`qwen3:8b`（分步引导·可用）、`qwen3:4b`、`gemma3:4b/1b`、`llava:latest`（OCR·可用）、`qwen3.5:latest`、`xmodel2:1b`
  - ⚠️ `qwen3-vl:32b`（20GB，最强 OCR）**已注册但 `/api/chat` 报 404「not found」**（manifest 与 blob 脱节，`D:\ollama\models\blobs` 为空）→ 当前 OCR 用 `llava:latest`；修复 = `ollama pull qwen3-vl:32b` 或升级 ollama
  - 🔴 **第 2 轮新发现**：`llava` OCR 读**纯算式**对、读**中文+算式混合**（真实题干形态）易错 → 过不了 L1「≥15/20」；须先修 `qwen3-vl:32b`
  - Windows SAPI TTS（`win32com`）：中文女声 `Microsoft Huihui`、英文 `Zira`，离线免费
- **Python**：`py -3.10`（3.10.11）；有 `requests`/`PIL`/`cv2`/`numpy`/`websockets`/`win32com`；**无** tesseract/paddleocr/pyttsx3/edge_tts
- **路线 = R3「不改系统」**：手机只做眼耳口（拍照/录音/播放），推理在 PC。R1（NEXT）/R2（4.x/EMUI）待手机型号确认后再引入。
- **教育红线**：① 不代写、只分步引导、答案默认不给；② 未成年保护（本地处理、25 分钟时长）；③ 家长可查、本地导出；④ 不编造出处；⑤ 评测只用自造/公开题。代码内置 `TUTOR_SYSTEM` + `redline_leak_check()`。
- **四条红线**：不代写作业 / 不采集真实学生隐私 / 不擅自采购硬件+不买 API+不注册账号 / 不碰 ComfyUI 与旧视频流水线。

## 4. 本唤醒流水（2026-11-07 · 第 1 轮）

- 读任务书 + `robot/README.md` ✅ → 环境勘察：adb/hdc 未装、手机未连、ollama 可用、SAPI TTS 可用。
- 建 `robot/` 代码：`host/tutor_agent.py`（OCR→分步引导→TTS）、`proto/mock_device.py`（模拟拍照）、`eval/sample_questions.md`（3 自造题）、`.gitignore`。
- **真跑通最小 demo**：题图 `2x+3=11` → llava 识别正确 → qwen3:8b 引导「你想先做什么呢？比如先移3还是先除以2？」（不含答案）→ 产出 48kHz 11.53s 真实 WAV。
- 诊断并定位 `qwen3-vl:32b` 404，临时切 `llava:latest`。
- 写 `P0_设备通路.md`（真实命令输出 + 路线裁决 + 用户 5 条清单）+ `ROADMAP.md`。
- 归档旧视频记忆 → `MEMORY_VIDEO_ARCHIVE.md`；重写本文件 ≤32KB；追加日流水；commit+push（robot:）。

## 4.1 本唤醒流水（2026-11-07 · 第 2 轮 · P0/demo 复验）

- 读任务书（按 11:10 令）+ `robot/README.md`；复验 P0 结论：`adb`/`hdc` 仍未装、`Get-PnpDevice` 无华为/ADB/HDC 设备、`ollama list` 8 模型在位。
- 复跑最小 demo：题图 → `llava` OCR → `qwen3:8b` 引导 → SAPI TTS，链路通、每步真实产物。
- 🔴 **新发现 OCR 最弱一环**：`llava` 读纯算式 `2x+3=11` 正确，读中文+算式混合 `解方程：2x+3=11` 连续误读（`二十一 加 二 等于 12` 等）；分步引导+TTS 两步稳定不泄答案。
- 诚实回写 `P0_设备通路.md` §0/§3.1/§5、`ROADMAP.md`、`host/README.md`；定位根因 = `qwen3-vl:32b` 404（manifest 与 blob 脱节）。
- 更新本文件 + 日流水；commit+push（robot:）。

## 5. 阻塞 / 待办

1. **⏳ 等用户 5 条回复**（P0_设备通路.md §4）：手机型号/系统版本、开 USB 调试、装 adb 或 HDC、确认形态、确认大模型来源。
2. **🔴 qwen3-vl:32b 404**（OCR 最弱一环的根因，本地可自修）：`ollama pull qwen3-vl:32b`（20GB）或升级 ollama → 换回更强 OCR，再跑 L1 识别准确率。
3. 下一轮候选：真机化 L0 / 补 100 题库跑 L1 指标（识别准确率 + 直接给答案率=0）。

## 6. 运维问答

> （暂无）
