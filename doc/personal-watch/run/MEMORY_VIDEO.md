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
PHASE:        L0 设备通路**模拟器全通（ADB+emulator+AVD+APK 安装+App 闭环+录屏）**；L1 单题闭环达标；HCI 交互规范已交付；**可安装真 App 已跑通（22:50 令）**；**HCI 代码层（normalize_math.py 81 单测 + speech.py 12 单测）已交付（12:20 令）**；**presence.py 在座检测已交付（12:05 令）**
已完成:       P0 ✅；路线 R3 ✅；最小 demo ✅；L1 基线 ✅；识图 4/4 ✅；给答案率 0 ✅；时延达标 ✅；INTERACTION_SPEC.md ✅；可安装 APK + 模拟器跑通一题 ✅（22:50 令·第10轮）；**normalize_math.py + speech.py 交付、93 单测全绿 ✅（12:20 令·第11轮）**；**presence.py 交付、8 单测、PC 摄像头 20 次实测 P50 33ms ≤300ms、准确率 20/20 ✅（12:05 令·第12轮）**
第5轮:       识图+引导切云端 DeepSeek（recognize() 签名不变 / 可降级 / 路径可见）；识图 0.5→1.0；P50 2.0s·P90 2.92s；修 headless TTS 崩溃；P0 用户清单 5→3 条
第6轮:       按 11:10 令全链路复跑无回归——P0 四度复验、R3 维持、demo 端到端 2.95s、L1 四指标达标（识图 1.0·首步 P50 1.51s/P90 2.22s·给答案率 0）
第7轮:       按 11:10 令全链路复跑无回归——P0 五度复验、R3 维持、demo 端到端 3.33s、L1 四指标达标（识图 4/4·首步 P50 1.6s/P90 1.78s·给答案率 0·无静默降级）
第8轮:       按 11:10 令全链路复跑无回归——P0 六度复验、R3 维持、demo 端到端 3.88s、L1 四指标达标（识图 4/4·首步 P50 1.25s/P90 1.27s·给答案率 0·无静默降级）
第9轮:       执行 20:05 令——交付 `INTERACTION_SPEC.md`（四态+常听态状态机、三层提示阶梯、21 条话术、13 条时延指标、打断/降级/在座检测/语音链路选型）；P0 七度复验无回归
第10轮:      执行 22:50 令——自装工具链(adb/emulator/jdk17/gradle-8.7/镜像)+AVD；`app/` Kotlin App 构建 app-debug.apk(4.09MB)+`adb install` Success+模拟器跑通一题(选图→DeepSeek识图→引导不含答案→TTS朗读)+录屏 12.16MB；打断/朗读按钮工作
第11轮:      执行 12:20 令 §2/§3/§4 代码交付——`normalize_math.py`(口述→数学式, 81 单测)+`speech.py`(asr_stream/tts_stream/stop, 端侧默认+打断+mock ASR, 12 单测)；`pytest` 93 passed
第12轮:      执行 12:05 令 §1/§5 代码交付——`presence.py`(YuNet 人脸+亮度阈值三分类 person/left/unknown, 帧不落盘, 8 单测)+`eval_presence.py`+PC 摄像头 20 次实测(29.71fps/P50 33ms/P90 57ms/20-20≤300ms/准确率 20/20)；`pytest` 101 passed
当前动作:     第 12 轮：读任务书 → 识别 22:50/12:20 令已闭环 → 按 ROADMAP「下一轮候选」交付 presence.py（12:05 令）→ YuNet 模型自举(OpenCV5 移除 CascadeClassifier/HOG) + 8 单测 + PC 摄像头 20 次实测 → 回写 MEMORY/ROADMAP/host-README/INTERACTION_SPEC + 日流水 → commit+push(robot:)
下一步:       `eval/interaction_*.json`（时延/打断/模拟学生 3 人设，11:40 令 §3）；题库扩到 100 题；真机化（等用户 3 条）；端侧真实 ASR（sherpa-onnx）接入位落地
阻塞:         ⏳ 手机未连（型号/系统未知）——**只阻塞真机化，不阻塞 PC/模拟器任何工作**（adb/emulator 已自装好）；`qwen3-vl:32b` 已按 15:4x 令作废；端侧 ASR 权重未装（用 MockStreamingASR 验逻辑，不阻塞）
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
- **上次唤醒**：2026-11-08（第 12 轮 · 12:05 令 §1/§5：交付 `presence.py` 在座检测，101 单测全绿，PC 摄像头 20 次实测 P50 33ms ≤300ms）

## 2. 分层目标与状态（L0-L4）

| 层 | 目标 | 判据 | 状态 |
|:--|:--|:--|:--|
| L0 设备通路 | 手机与开发机连通 | 装包/截屏/拍照/出声各一条命令真实产物 | 🟡 PC mock 全通；真机待用户 3 条（P0 §4） |
| L1 单题闭环 | 拍题→识图→结构化→LLM 分步引导→TTS | 20 题 ≥15 识别正确，引导不含答案 | 🟢 4/4 识图 · P50 2.0s/P90 2.92s · 直接给答案率 0（题库待扩到 100 题） |
| L2 智能体 | 工具调用/多轮追问 | 5 工具可调、3 轮一致 | ⬜ 仅验 2 轮一问一答（不丢上下文、不泄答案） |
| L3 学情 | 错题本+画像+家长摘要 | 本地可导出 HTML | ⬜ |
| L4 形态 | 桌面实体机器人 | 待用户确认 | ⬜（口径：自家 8 年级女儿用的桌面端 · 12:05 令） |

## 3. 关键事实（本线技术栈 · 实测）

- **主路径 = 云端 DeepSeek（11:30 / 15:4x 令定稿）**：
  - 端点 `POST https://api.deepseek.com/chat/completions`（OpenAI 兼容）；`GET /models` 实测 200，仅两项：`deepseek-flash` / `deepseek-v4-pro`
  - **模型 ID 就是 `deepseek-flash`**（🚫 不写 `deepseek-v4.1-flash-1017` 之类）；识图与文本都用它
  - key 只从 `DEEPSEEK_API_KEY` 或 `C:\Users\Administrator\.cline\data\secrets.json` 的 `deepSeekApiKey` 读 → **不落盘/不进日志/不进报告**
  - 实测（第 5 轮）：识图 **4/4**；识图时延 P50 2.41s / P90 2.62s；分步引导 P50 2.0s / P90 2.92s
  - ⚠️ 题图上云 = 学生题目外发（`P0_设备通路.md` §5 写了口径与纯本地开关）
- **本机兜底栈（零采购/零新账号，全部可用）**：
  - `ollama` 0.40.15：`qwen3:8b`（分步引导）、`qwen3:4b`、`gemma3:4b/1b`、`llava:latest`（识图兜底）、`qwen3.5:latest`、`xmodel2:1b`
  - `qwen3-vl:32b`（20GB）**已按 15:4x 令作废**：`/api/chat` 始终 404（manifest 与 blob 脱节），保留记录但不再为它排期
  - `llava` 定位 = **离线兜底**：算式 2/2 对、中文应用题与代数式 0/2 对（第 5 轮实测 0.5），首步 P50 5.72s
  - Windows SAPI TTS（`win32com`）：中文女声 `Microsoft Huihui`，离线免费；**无音频设备时已改为降级纯文字**（不再崩）
- **Python**：`py -3.10`（3.10.11）；有 `requests`/`PIL`/`cv2`/`numpy`/`websockets`/`win32com`；**无** tesseract/paddleocr/pyttsx3/edge_tts
- **路线 = R3「不改系统」**：手机只做眼耳口（拍照/录音/播放），推理在 PC/云。R1（NEXT）/R2（4.x/EMUI）待手机型号确认后再引入。
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

## 4.2 本唤醒流水（2026-11-07 · 第 3 轮 · 评测基线 + 精确根因）

- 读任务书（11:10 令）+ `robot/README.md`；复验 P0：`adb`/`hdc` 仍未装、`Get-PnpDevice` 无华为/ADB/HDC 设备、`ollama list` 8 模型在位。
- 新增 `host/eval_l1.py`：可重复跑的 L1 评测基线（文本 3 题 + 对抗性直接要答案探针 + OCR 2 图）→ 产出 `eval/l1_baseline.json`。
- 🔴 真跑出「直接给答案率 = 0」：正常引导 3/3 不含答案；**明确要答案时 3/3 拒绝**、仍只问思路（红线 1 顶得住）。
- ⚠️ 真跑出 OCR 正确率 0.5：`llava` 读纯算式 `2x+3=11` ✅；读中文+算式混合 `解方程：2x+3=11` ❌（返回「无法解析图像」）。
- ✅ 精确定位 `qwen3-vl:32b` 404 根因：真实模型目录 = `E:\ollama\models`，其 manifest 引用的 20GB GGUF blob `sha256-6e41…` 缺失；之前「`D:\ollama\models\blobs` 为空」是误判（`OLLAMA_MODELS` 指 D:，ollama 实际用 E:）。
- ✅ 最小 demo 复跑：`--image q1_pure.png --speak --answer "4"` → 识别正确 → 引导不含答案 → 产出 1.15MB WAV。
- 诚实回写 `P0_设备通路.md`（§0/§3.2/§5）、`ROADMAP.md`、`host/README.md`；更新本文件 + 日流水；commit+push（robot:）。

## 4.3 本唤醒流水（2026-11-07 · 第 4 轮 · 修 OCR 非确定性）

- 读任务书（11:10 令）+ `robot/README.md`；复验 P0：`adb`/`hdc` 仍未装、`Get-PnpDevice` 无华为/ADB/HDC 设备、`ollama list` 8 模型在位（`qwen3-vl:32b` 仍 404）。
- 🔴 **定位 OCR「时对时错」真因 = 非确定性**：`llava` OCR 默认 temperature 随机，同一张 `2x+3=11` 题图 3 次读成 `我们不会看到这个问题` / `1+3=11` / `2x+3=11`（只对 1/3）。
- ✅ **修复**：`tutor_agent.py` 的 OCR 调用加 `options.temperature=0` → 同一张图 3 次全对全一致；另加英文提示词兜底（中文拒识时）。
- ✅ **OCR 正确率 0.5 → 1.0**（真跑 `eval_l1.py`）：纯算式、中文+算式混合（方程内容）都稳定读对；`eval_l1.py` 加 `_math_norm`（只比数学骨架，忽略「解方程：」标签）。
- ✅ 最小 demo 全链路复跑：`--image q1_mixed.png --speak --answer "4"` → 识别 `2x+3=11` → 引导「你先想，这道题要怎么开始解？」（不含答案）→ 产出 1.6MB WAV。
- 诚实回写 `P0_设备通路.md`（§0/§3.3/§5）、`ROADMAP.md`（第 4 轮）、`host/README.md`；更新本文件 + 日流水；commit+push（robot:）。

## 4.4 本唤醒流水（2026-11-07 · 第 5 轮 · P0 复验 + 路线复核 + demo 端到端）

- 读任务书全文（384 行）+ `robot/README.md`；按 11:10 令做 **P0 → 选路线 → 最小 demo**，并顺手清掉 15:4x 识图令（它是 demo 达标的必要条件）。
- **P0 复验（真实命令）**：`adb`/`hdc` 仍不在 PATH；把「无华为设备」**证到 VID 级**（`046D`/`1A2C`/`30FA`/`8087`，**无华为 `12D1`**）；`qwen3-vl:32b` 仍 404；DeepSeek `GET /models` = 200。
- **路线**：R3 **维持**（复核理由已更新：云端 DeepSeek 让 R3 一步到位达标，且零新账号）。
- ✅ **代码**：`host/tutor_agent.py` 接双后端（`ROBOT_VISION_BACKEND` / `ROBOT_TUTOR_BACKEND`，默认 deepseek），
  `recognize()` **签名不变**；失败降级本机 ollama 且**降级原因可见**（`LAST_*_TRACE` + CLI）；key 只读不打印。
  另修 **headless TTS 崩溃**（`SAPI.Speak()` COM 异常 → 降级纯文字）。
- ✅ **真跑数字**：识图 **4/4 = 1.0**（含中文应用题 `已知等腰三角形顶角为 40°…`）；首步 **P50 2.0s / P90 2.92s**；
  直接给答案率 **0**（正常 3/3 + 对抗 3/3）；demo 端到端 **2.81s**，产出 48kHz/17.72s WAV。
  对照本地：识图 0.5、P50 5.72s（不达标）→ 云端为主路径成立。
- 🔴 **自查并修正自己的错误**：首次跑出 `ocr_accuracy=0.25` 是**评测口径 bug**（DeepSeek 口述成「2x 加 3 等于 11」），
  不是模型不会；改提示词（标准写法）+ `_math_norm` 中文算式词归一后重跑 = 4/4。已写进 P0 §3.4「诚实说明」。
- **P0 用户清单 5 → 3 条**（形态/大模型来源已被 12:05 / 11:30 令回答，删除）。
- 回写：`P0_设备通路.md`（§0/§1.1/§2/§3.4/§4/§5）、`ROADMAP.md`（L0-L4 状态 + 第 5 轮增量 + 下一轮候选）、
  `host/README.md`（后端表/隐私口径/新命令）、`robot/README.md`（当前状态表）、本文件、`daily-memories-video/2026-11-07.md`。
- commit+push（`robot:`）。


## 4.5 本唤醒流水（2026-11-07 · 第 6 轮 · 按 11:10 令全链路复跑 · 无回归）

- 读任务书全文（384 行）+ `robot/README.md`；按用户指定口径执行 **11:10 令（P0 设备通路 → 选路线 → 最小 demo）**；ComfyUI 全程未碰（已冻结）。
- **P0 四度复验（真实命令）**：`adb`/`hdc` 仍未装（`Get-Command` 均 `$null`，`ANDROID_HOME` 空）；USB `VID` 仍无华为 `12D1`（仅 `30FA`/`046D`/`1A2C`/`8087`）；`GET api.deepseek.com/models`=200（key 来自 `secrets.json`，未打印）；`ollama list` 8 模型在位。
- **路线复核**：**R3 维持**（手机=眼/耳/口，推理在 PC/云；云端 DeepSeek 一步达标、零新账号）。
- ✅ **最小 demo 端到端（PC 端 mock，16:5x 令方案 C）**：`mock_device --snap` 中文几何题 → DeepSeek 视觉逐字读对（1.52s）→ 首步引导「等腰三角形两个底角有什么特点？」（**不含 70°**，1.43s）→ **总时延 2.95s** → 48kHz WAV。
- ✅ **L1 四指标复跑（`eval_l1.py` 云端）**：识图 **4/4=1.0**；首步 **P50 1.51s / P90 2.22s**（11:40 硬指标 ≤2.5/≤4 达标）；**直接给答案率 0**（正常 3/3 + 对抗 3/3 全拒）；`ocr_fallback_count=0`（无静默降级）。
- 📌 **结论**：第 6 轮与第 5 轮一致、无回归；11:10 令（P0 → 选路线 → 最小 demo）已闭环；用户清单维持 **3 条（≤5）**。
- 回写：`P0_设备通路.md`（§0/§1.2/§4）、`ROADMAP.md`（第 6 轮复验）、本文件、`daily-memories-video/2026-11-07.md`。
- commit+push（`robot:`）。

## 4.6 本唤醒流水（2026-11-07 · 第 7 轮 · 按 11:10 令全链路复跑 · 无回归）

- 读任务书全文（384 行）+ `robot/README.md`；按用户指定口径执行 **11:10 令（P0 设备通路 → 选路线 → 最小 demo）**；ComfyUI 全程未碰（已冻结）。
- **P0 五度复验（真实命令）**：`adb`/`hdc` 仍未装（`Get-Command` 均 `$null`，`ANDROID_HOME` 空）；USB `VID` 仍无华为 `12D1`（仅 `30FA`/`046D`/`1A2C`/`8087`）；`GET api.deepseek.com/models`=200（`deepseek-flash` 官方 `input_modalities=[text,image]`、`deepseek-v4-pro` 仅 text，key 来自 `secrets.json` 未打印）；`ollama list` 8 模型在位。
- **路线复核**：**R3 维持**（手机=眼/耳/口，推理在 PC/云；云端 DeepSeek 一步达标、零新账号）。
- ✅ **最小 demo 端到端（PC 端 mock，16:5x 令方案 C）**：`mock_device --snap` 中文几何题 → DeepSeek 视觉逐字读对（1.58s）→ 首步引导「两个底角之间是什么关系呢？」（**不含 70°**，1.75s）→ **总时延 3.33s** → 48kHz WAV。
- ✅ **L1 四指标复跑（`eval_l1.py` 云端）**：识图 **4/4=1.0**；首步 **P50 1.6s / P90 1.78s**（11:40 硬指标 ≤2.5/≤4 达标）；**直接给答案率 0**（引导 0/3 + 对抗 0/3 全拒）；`ocr_fallback_count=0`（无静默降级）。
- 📌 **结论**：第 7 轮与第 6 轮一致、无回归；11:10 令（P0 → 选路线 → 最小 demo）持续闭环；用户清单维持 **3 条（≤5）**。
- 回写：`P0_设备通路.md`（§0/§1.3/§4）、`ROADMAP.md`（第 7 轮复验）、本文件、`daily-memories-video/2026-11-07.md`。
- commit+push（`robot:`）。

## 4.7 本唤醒流水（2026-11-07 · 第 8 轮 · 按 11:10 令全链路复跑 · 无回归）

- 读任务书全文（409 行）+ `robot/README.md`；按用户指定口径执行 **11:10 令（P0 设备通路 → 选路线 → 最小 demo）**；ComfyUI 全程未碰（已冻结）。
- **P0 六度复验（真实命令）**：`adb`/`hdc` 仍未装（`Get-Command` 均 `$null`，`ANDROID_HOME` 空）；USB `VID` 仍无华为 `12D1`（仅 `30FA`/`046D`/`1A2C`/`8087`）；`GET api.deepseek.com/models`=200 且 `deepseek-flash` 官方 `input_modalities=[text,image]`、`deepseek-v4-pro` 仅 text（key 来自 `secrets.json`，未打印）；`ollama list` 8 模型在位。
- **路线复核**：**R3 维持**（手机=眼/耳/口，推理在 PC/云；云端 DeepSeek 一步达标、零新账号/零采购）。
- ✅ **最小 demo 端到端（PC 端 mock，16:5x 令方案 C）**：`mock_device --snap` 中文几何题 → DeepSeek 视觉逐字读对（2.36s）→ 首步引导「我们先不急着算。先回忆一下：等腰三角形里，两个底角之间有什么关系呢？」（**不含 70°**，1.52s）→ **总时延 3.88s** → 48kHz WAV。
- ✅ **L1 四指标复跑（`eval_l1.py` 云端）**：识图 **4/4=1.0**；首步 **P50 1.25s / P90 1.27s**（11:40 硬指标 ≤2.5/≤4 达标）；**直接给答案率 0**（引导 0/3 + 对抗 0/3 全拒）；`ocr_fallback_count=0`（无静默降级）。
- 📌 **结论**：第 8 轮与第 7 轮一致、无回归；11:10 令（P0 → 选路线 → 最小 demo）持续闭环；用户清单维持 **3 条（≤5）**。
- 回写：`P0_设备通路.md`（§0/§1.4/§4）、`ROADMAP.md`（第 8 轮复验）、本文件、`daily-memories-video/2026-11-07.md`。
- commit+push（`robot:`）。

## 4.8 本唤醒流水（2026-11-07 · 第 9 轮 · 执行 20:05 令交付 INTERACTION_SPEC.md）

- 读任务书全文（409 行）+ `robot/README.md`；识别到**最新最高优先 20:05 令**：HCI 四条令（11:40/11:55/12:05/12:20）未交付前，**暂停 L1/OCR 重跑**，本轮唯一交付 = `INTERACTION_SPEC.md`。故不再第 5 次重跑 11:10 demo（第 5–8 轮已连续复跑 4 次），改为交付 HCI 规范。ComfyUI 全程未碰（已冻结）。
- **P0 七度复验（真实命令）**：`adb`/`hdc` 仍未装（`Get-Command` 均 `$null`）；`ANDROID_HOME` 空；USB `VID` 仍无华为 `12D1`（仅 `30FA`/`046D`/`1A2C`/`8087`）。
- ✅ **交付 `INTERACTION_SPEC.md`**（可数可核）：状态机 **2 图**（ASCII 29 行 + mermaid 17 行）+ 状态表 **10 行**（ambient/listen/think/speak/wait_student/clarify/encourage/presence/idle/muted）；三层提示阶梯 L1/L2/L3（禁跳级、禁给答案）；**话术模板 21 条**（T01–T21）；**时延指标 13 条**（M01–M13：P50≤2.5s / P90≤4s / 打断≤300ms / 静默 6s→10s 等）；打断协议、静默/超时/降级矩阵、在座检测（presence）、语音链路端侧定稿（含「云端语音默认 off」）。
- 📌 **结论**：20:05 令（交付 `INTERACTION_SPEC.md`）✅ 闭环；HCI 代码（speech.py / presence.py / normalize_math.py）与 11:40 交互验收（录音 / 打断 / 模拟学生 / 走查）留待下一轮，本轮**不谎称已测**。
- 回写：`INTERACTION_SPEC.md`（新建）、`ROADMAP.md`（第 9 轮增量 + 下一轮候选）、本文件、`P0_设备通路.md`（§0 第 9 轮注）、`daily-memories-video/2026-11-07.md`。
- commit+push（`robot:`）。

## 4.9 本唤醒流水（2026-11-08 · 第 10 轮 · 执行 22:50 令可安装真 App + 自建开发环境 + 模拟器跑通）

- 读任务书全文 + `robot/README.md`；识别到**最新最高优先 22:50 令（总纲）**：做可安装真 Android App（Kotlin+CameraX+系统TTS+HTTP）、自建开发环境、取消微操条款；结合 22:30/22:35/22:40 令（模拟器跑通客户端 + 自己装工具链）。ComfyUI 全程未碰（已冻结）。
- ✅ **工具链已就绪（前轮已下，本轮验收）**：`C:\Android\` 下 platform-tools(adb 37.0.1)/cmdline-tools/jdk17(Temurin 17.0.16+8)/gradle-8.7/emulator/build-tools/platforms;android-34/system-images;android-34;google_apis;x86_64 全在；AVD `robot34` 已建。
- ✅ **模拟器启动**：`emulator -avd robot34 -gpu swiftshader_indirect -no-window ...` → `adb devices` 见 `emulator-5554 device`、`getprop sys.boot_completed=1`（WHPX `operational`）。
- ✅ **APK 构建**：`app/`（Kotlin + CameraX 1.3.4 + 系统 TTS + HttpURLConnection/org.json，零第三方网络依赖）`:app:assembleDebug` → `app-debug.apk` = 4,088,176 字节，BUILD SUCCESSFUL in 3m22s（37 tasks）。
- ✅ **`adb install` Success**；App 启动 UI 完整渲染（`uiautomator`：tvStatus「语音就绪」、拍照/选图/朗读/打断、服务地址 `http://10.0.2.2:8765`）；相机权限弹窗→`pm grant`→重进。
- ✅ **App 端完整闭环（模拟器跑通一题）**：选图 `q2_geometry.png`（推入 MediaStore）→ 上传 → DeepSeek 视觉识图「已知等腰三角形顶角为 40°，求底角的度数。」→ 分步引导「…等腰三角形的两个底角，大小有什么关系呢？」（**不含 70°**）→ 屏幕显示 + 系统 TTS「朗读中」；打断/朗读按钮工作。
- ✅ **PC 侧 `host/tutor_server.py`**：监听 `0.0.0.0:8765`；`GET /health`=200（vision=tutor=deepseek）；文本题 1.2s（deepseek-flash，无静默降级）；App 经 `10.0.2.2:8765` 联调成功。
- ✅ **录屏取证**：`logs/robot_session.mp4` = 12,162,070 字节（45s：打断→朗读→选图→出引导；sha256 `B2C73493…D9B16848`）。
- 📌 **结论**：22:50 令 + 22:30/22:35/22:40 令（真 App + 模拟器 + 自装工具链）**全部闭环**；模拟器「能信/不能信」写进 `P1_模拟器.md` §7。回写 P1/ROADMAP/本文件 + `daily-memories-video/2026-11-08.md`；commit+push（`robot:`）。

## 4.10 本唤醒流水（2026-11-08 · 第 11 轮 · 交付 HCI 代码层：normalize_math.py + speech.py）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md`；识别到**最新 22:50 令已闭环**（第 10 轮已交付可安装 App + 模拟器跑通一题），本轮按 ROADMAP「下一轮候选」+ 12:20 令 §2/§3/§4 交付一直欠的 HCI 代码（11:40/11:55/12:05/12:20 四条令，spec 第 9 轮已定稿、代码未写）。ComfyUI 全程未碰（已冻结）。
- ✅ **`host/normalize_math.py`（12:20 令 §4）**：口述→数学式纠错，覆盖全部词表（平方/立方/根号/分之/负/加减乘除/等于/大于小于/π/度/角/三角形/平行/垂直/相似/全等/分母/分子/一次项/二次项/移项/合并同类项）；权威示例实测一致：`x的平方加三x等于零 → x^2+3x=0`、`二分之根号三 → √3/2`；术语「三角形/一次项/二次项/分母/分子/移项/合并同类项」按不破坏处理（汉字数字不误转）。
- ✅ **`host/normalize_math.py` 单测 81 条**（要求 ≥30，超标 2.7 倍）+ `cn_to_int` 数字转换 9 条，`pytest` 全绿。
- ✅ **`host/speech.py`（12:20 令 §2/§3 + INTERACTION_SPEC §9）**：统一接口 `asr_stream()/tts_stream()/stop()`；端侧默认（Windows SAPI 分句流式 + 句间停顿 + 打断 + `MockStreamingASR` 流式 mock），云端 `CloudASR/CloudTTS` 留空实现（默认 off，构造即报「不新增语音厂商账号」），`SherpaOnnxASR` 接入位（未装权重给明确报错、不静默）。
- ✅ **`host/speech.py` 单测 12 条**（分句/打断标志/ASR 流式顺序与打断/TTS 落盘 WAV/打断丢弃在途/云端与端侧未装报错），全绿；实测 TTS 合成 48kHz WAV、打断后丢弃剩余句、ASR mock 逐字 partial+final。
- ✅ **实测输出**：`py -3.10 -m pytest test_normalize_math.py test_speech.py -q` → **`93 passed in 0.46s`**（81 + 12）。
- 📌 **结论**：12:20 令 §2/§3/§4 的「口述→数学式 + 语音链路适配层」代码交付闭环；`normalize_math` 已达标（≥30 单测）；`speech.py` 的 ASR 真实 CER / TTS 首字 / 打断 ≤300ms / AEC 均**标注待真机**（本机无端侧 ASR 权重，用 mock 只验逻辑，不谎称已测）。
- 回写：`host/normalize_math.py` + `test_normalize_math.py`、`host/speech.py` + `test_speech.py`（新建）、`host/README.md`、`INTERACTION_SPEC.md`（§10 交付状态）、`ROADMAP.md`（第 11 轮增量）、本文件、`daily-memories-video/2026-11-08.md`。
- commit+push（`robot:`）。

## 4.11 本唤醒流水（2026-11-08 · 第 12 轮 · 交付 presence.py 在座检测）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md`；识别到 22:50/12:20 令已闭环（第 10/11 轮），本轮按 ROADMAP「下一轮候选」+ 12:05 令 §1/§5 交付一直欠的 `presence.py`（在座检测）。ComfyUI 全程未碰（已冻结）。
- ✅ 环境复验：emulator 仍在线（`adb devices` → `emulator-5554 device`）；PC 摄像头可开（`cv2.VideoCapture(0)` 640×480）；发现 OpenCV 5.0 已移除 `CascadeClassifier`/`HOGDescriptor` → 改用内置 YuNet（`cv2.FaceDetectorYN`）。
- ✅ 模型自举：下 `face_detection_yunet_2023mar.onnx`（232KB，OpenCV Zoo Apache-2.0；jsdelivr 对 Xet 存返回「Access denied」→ 改 HuggingFace resolve 200）到 `host/models/`（权重 `*.onnx` 按体积红线不入库）。
- ✅ `host/presence.py`：单帧 320×240 + 亮度阈值 + YuNet 三分类 person/left/unknown；帧端侧处理立即丢弃不落盘不上传；`FrameSource` 抽象 + `WebcamSource` 默认 + `measure()` 连拍测帧率耗时。
- ✅ 单测 8 条（`test_presence.py`）：三分类 / 300ms 预算字段 / 模型缺失报错 / 自动找模型；host 全量 **101 passed**（81 + 12 + 8）。
- ✅ PC 摄像头实测（Logitech 046D，20 次）：帧率 **29.71 fps**；单次抓帧+检测 **P50 33.0ms / P90 57.4ms / max 66.4ms**，**20/20 ≤300ms**（12:05 令 M12 达标）；准确率 20 标注样本 **20/20**（person 8 + left 8 + unknown 4）。
- ⚠️ 样本为「无歧义」集（清晰人脸 / 明显无人风景静物 / 合成暗帧）；遮挡/逆光/侧脸/远景小脸等难例 + 真人准确率**待真人/真机复测**（16:5x 令「能信/不能信」，不把 PC 结论当真机结论）。
- 回写：`presence.py` + `test_presence.py` + `eval_presence.py`（新建）、`host/README.md`、`INTERACTION_SPEC.md`（§7.1 M12 + §10 交付状态）、`ROADMAP.md`（第 12 轮增量）、本文件、`daily-memories-video/2026-11-08.md`。
- commit+push（`robot:`）。

## 5. 阻塞 / 待办

1. **⏳ 等用户 2 条回复**（`P0_设备通路.md` §4）：① 手机型号/系统版本 ② 开 USB 调试并连线（adb/hdc 已由本线自装，不再需要用户装）。
   🚫 **只阻塞「真机化」，不阻塞 PC/模拟器任何工作**（16:5x 令 §5：不得再以此为由停摆）。
2. ~~`qwen3-vl:32b` 20GB GGUF 缺失~~ → **已作废**（15:4x 令：识图走 DeepSeek，本地 `llava` 只做离线兜底）。
3. **下一轮候选（按优先级）**：
   1. `eval/interaction_*.json`（时延 / 打断 / 模拟学生 3 人设）——11:40 令 §3 交互验收（语音链路接口已就绪，可先跑逻辑版）；
   2. 题库扩到 100 题跑 L1 全量指标；
   3. 端侧真实 ASR（sherpa-onnx）接入位落地（`SherpaOnnxASR` 现为报错占位）；真机化 L0（等用户 3 条）。

## 6. 运维问答

> （暂无）
