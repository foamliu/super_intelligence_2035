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
PHASE:        L0 设备通路**模拟器全通（ADB+emulator+AVD+APK 安装+App 闭环+录屏）**；L1 单题闭环达标；HCI 交互规范已交付；**可安装真 App 已跑通（22:50 令）**；**HCI 代码层（normalize_math.py 81 单测 + speech.py 12 单测）已交付（12:20 令）**；**presence.py 在座检测已交付（12:05 令）**；**交互验收（11:40 令 §3）已交付（第13轮）**；**L1 全量 100 题 + 泄露检测误报修复（第14轮）**；**L2 智能体工具层（5 工具 + 会话编排 + LLM 工具决策）已交付（第15轮）**；**L2 工具/智能体已接 HTTP+App（/tool + /agent 端点 + App 换一题/记错题/报告/追问 + APK 装机成功）已交付（第16轮）**；**L3 学情层（l3_profile.py 知识点画像+每日/每周摘要+自包含 HTML + POST /profile 端点 + App「学情」按钮）已交付（第17轮）**；**端侧真实 ASR 落地（SherpaOnnxASR paraformer 离线 + StreamingSherpaOnnxASR streaming-zipformer 真流式 + eval_asr.py CER 实测，第18轮）**；**L3 正样本（练习日志+合并画像+/practice 端点+App 答对/答错，第19轮）**；**端侧 VAD + App 语音打断/静音真关麦/常听（第20轮）**；**知识点自动分类（knowledge.py LLM+本地兜底 + POST /practice 自动补知识点 + App 显示分类，第21轮）**
已完成:       P0 ✅；路线 R3 ✅；最小 demo ✅；L1 基线 ✅；识图 4/4 ✅；给答案率 0 ✅；时延达标 ✅；INTERACTION_SPEC.md ✅；可安装 APK + 模拟器跑通一题 ✅（22:50 令·第10轮）；**normalize_math.py + speech.py 交付、93 单测全绿 ✅（12:20 令·第11轮）**；**presence.py 交付、8 单测、PC 摄像头 20 次实测 P50 33ms ≤300ms、准确率 20/20 ✅（12:05 令·第12轮）**；**交互验收交付：eval/interaction_*.json + HTML 报告 + clamp_hint(≤2句)，整轮 P50 1.37s/P90 1.97s、给答案率 0、录音 91.2s、118 单测全绿 ✅（11:40 令·第13轮）**；**100 题题库(question_bank.py)+leak_check 修复+L1 全量评测（给答案率 0·识图 20/20·P50 1.16s/P90 2.07s）、133 单测全绿 ✅（第14轮）**；**L2 智能体：tools.py(5工具)+l2_agent.py(会话/路由/LLM决策)+eval_l2.py，6 工具全调·给答案率 0·3 轮一致·175 单测全绿 ✅（第15轮）**；**L2→HTTP/App：/tool+/agent 端点+App 换一题/记错题/报告/追问+APK 装机成功（4.11MB·adb install Success·UI dump 确认）、188 单测全绿 ✅（第16轮）**；**L3 学情：l3_profile.py（知识点画像+每日/每周摘要+自包含 HTML）+POST /profile 端点+App「学情」按钮+模拟器点击实测（错题总数 2·薄弱点一元一次方程）、205 单测全绿 ✅（第17轮）**；**端侧真实 ASR：SherpaOnnxASR(paraformer 离线)+StreamingSherpaOnnxASR(zipformer 真流式)+eval_asr.py（流式 CER mean 0.302·延迟 0.03-0.08s·中间结果逐字增长）、209 单测全绿 ✅（第18轮）**；**L3 正样本：练习日志+合并画像（作答次数/正确率/掌握等级）+POST /practice 端点+App「答对/答错」按钮+模拟器点击实测（错题3·练习5·知识点2·薄弱点一元一次方程）、222 单测全绿 ✅（第19轮）**；**端侧 VAD+App 语音打断/静音真关麦/常听态（vad.py 16 单测+MicVad.kt+RECORD_AUDIO）、APK 4,124,752 字节+模拟器跑通一题、238 单测全绿 ✅（第20轮）**；**知识点自动分类：knowledge.py（本地关键词 100 题 100/100+LLM DeepSeek 主路径/本地兜底）+POST /practice 自动补知识点+App 状态栏显示分类、APK 4,157,236 字节+模拟器答对→「知识点：一元一次方程」、285 单测全绿 ✅（第21轮）**
第5轮:       识图+引导切云端 DeepSeek（recognize() 签名不变 / 可降级 / 路径可见）；识图 0.5→1.0；P50 2.0s·P90 2.92s；修 headless TTS 崩溃；P0 用户清单 5→3 条
第6轮:       按 11:10 令全链路复跑无回归——P0 四度复验、R3 维持、demo 端到端 2.95s、L1 四指标达标（识图 1.0·首步 P50 1.51s/P90 2.22s·给答案率 0）
第7轮:       按 11:10 令全链路复跑无回归——P0 五度复验、R3 维持、demo 端到端 3.33s、L1 四指标达标（识图 4/4·首步 P50 1.6s/P90 1.78s·给答案率 0·无静默降级）
第8轮:       按 11:10 令全链路复跑无回归——P0 六度复验、R3 维持、demo 端到端 3.88s、L1 四指标达标（识图 4/4·首步 P50 1.25s/P90 1.27s·给答案率 0·无静默降级）
第9轮:       执行 20:05 令——交付 `INTERACTION_SPEC.md`（四态+常听态状态机、三层提示阶梯、21 条话术、13 条时延指标、打断/降级/在座检测/语音链路选型）；P0 七度复验无回归
第10轮:      执行 22:50 令——自装工具链(adb/emulator/jdk17/gradle-8.7/镜像)+AVD；`app/` Kotlin App 构建 app-debug.apk(4.09MB)+`adb install` Success+模拟器跑通一题(选图→DeepSeek识图→引导不含答案→TTS朗读)+录屏 12.16MB；打断/朗读按钮工作
第11轮:      执行 12:20 令 §2/§3/§4 代码交付——`normalize_math.py`(口述→数学式, 81 单测)+`speech.py`(asr_stream/tts_stream/stop, 端侧默认+打断+mock ASR, 12 单测)；`pytest` 93 passed
第12轮:      执行 12:05 令 §1/§5 代码交付——`presence.py`(YuNet 人脸+亮度阈值三分类 person/left/unknown, 帧不落盘, 8 单测)+`eval_presence.py`+PC 摄像头 20 次实测(29.71fps/P50 33ms/P90 57ms/20-20≤300ms/准确率 20/20)；`pytest` 101 passed
第13轮:      执行 11:40 令 §3 交互验收闭环——`eval_interaction.py`(latency/bargein/student 三模式)+`test_interaction.py`(10单测)+`gen_interaction_report.py`+HTML 报告；实测整轮 P50 1.37s/P90 1.97s、TTS 首字 P50 80.4ms、打断 stop~0ms、模拟学生 3 人设×10 轮**直接给答案率 0**、录音 91.2s；暴露 LLM 输出过长(3-6句)→ 加 `clamp_hint()`(≤2句)+强化提示词(7单测)；`pytest` 118 passed
第14轮:      执行 ROADMAP「下一轮候选」#1——重建 100 题题库 question_bank.py(数学60+物理20+英语20)+修复泄露检测误报 leak_check.py(词边界+复述题干不算泄露)+eval_l1_full.py 全量评测(220 次 deepseek-flash)：给答案率 0、识图 20/20、P50 1.16s/P90 2.07s；`pytest` 133 passed
第15轮:      执行 ROADMAP L2 智能体——`tools.py`(5 工具：计算器 AST 白名单/题库/错题本/家长报告/绘图)+`l2_agent.py`(确定性路由+LLM 工具决策+L2Session 多轮会话)+`eval_l2.py` 评测：6 工具全调、给答案率 0、3 轮追问一致、绘图 PNG 20KB、LLM 决策选 calculator 正确；`pytest` 175 passed
第16轮:      执行 ROADMAP #1（L2 工具接进 App/HTTP）——`tutor_server.py` 新增 `/tool`+`/agent` 端点 + `/tutor` 带 `tool` 字段即转工具；`test_tutor_server.py` 13 单测 + `smoke_http.py` 实测；App 加「换一题/记错题/报告」按钮 + 文字追问（`TutorClient.postTool/postAgent`）；`assembleDebug`→APK 4,112,860 字节 + `adb install -r` Success + `uiautomator dump` 确认新按钮；`pytest` 188 passed
第17轮:      执行 ROADMAP L3 学情——`l3_profile.py`(知识点画像/每日每周摘要/自包含HTML)+`tutor_server.py` 新增 `POST /profile`+`test_l3_profile.py` 13 单测+App「学情」按钮(`TutorClient.postProfile`)+`assembleDebug`→APK 4,115,732 字节+`adb install -r` Success+模拟器点击实测(错题总数2·薄弱点一元一次方程)；清 stale server 2 个(占 8765 旧代码无 /profile)；`pytest` 205 passed
第18轮:      执行 ROADMAP「下一轮候选」#1——端侧真实 ASR 落地：`speech.py` `SherpaOnnxASR`(paraformer 中文离线)+`StreamingSherpaOnnxASR`(streaming-zipformer 真流式)+`eval_asr.py`(流式 CER mean 0.302·延迟 0.03-0.08s·中间结果逐字增长)；模型落 hf-mirror(streaming ~31MB·paraformer 243MB 就绪)；`pytest` 209+1skip passed
第19轮:      执行 ROADMAP L3 学情补「正样本」——`l3_profile.py` 练习日志(作答对错)+合并画像(错题负样本+练习正样本·正确率/掌握等级)+`POST /practice` 端点+App「答对/答错」按钮；APK 4,120,020 字节+adb install+模拟器点「学情」实测(错题3·练习5·知识点2·薄弱点一元一次方程)；`pytest` 222 passed
第20轮:      执行 22:50 令「打断可用」——`host/vad.py`(端侧 VAD 纯函数：能量/端点1.2s/打断debounce/静音真关麦/状态机)+16 单测；App 端 `MicVad.kt`(AudioRecord 端侧 VAD)+语音打断(barge-in)+静音真关麦+状态指示(常听/听/说/静音)+Manifest RECORD_AUDIO；APK 4,124,752 字节+adb install Success+模拟器跑通一题(文字题 2x+3=11→DeepSeek 引导不含答案→状态「说」→打断「听」→静音「静音」)+录屏 r20_session.mp4(4.4MB)；`pytest` 238 passed
第21轮:      执行 ROADMAP「下一轮候选 #5」——`host/knowledge.py`(知识点自动分类：`classify_knowledge_local` 确定性关键词 100 题 100/100 + `classify_knowledge` LLM DeepSeek 主路径/本地兜底 + `_normalize` 学科名→未分类)+44 单测；`tutor_server.py` `POST /practice` 缺 knowledge 自动补(出参加 knowledge+classify)+3 单测；App `TutorClient.PracticeReply` 加 knowledge+状态栏「已记录「答对」· 知识点：xx」；APK 4,157,236 字节+adb install Success+模拟器文字题 5x-3=12 答对→「知识点：一元一次方程(累计10次)」+学情「一元一次方程 6次/83%·勾股定理 4次/100%」+录屏 r21_session.mp4(20.3MB)；`pytest` 285 passed
当前动作:     第 20 轮：读任务书 → 识别 22:50 令「打断可用」为下一增量 → 写 `host/vad.py`+16 单测 → App `MicVad.kt`+语音打断+静音+状态机 → assembleDebug+adb install+模拟器跑通一题+录屏 → 238 单测全绿 → 回写 → commit+push(robot:)
下一步:       clamp_hint 后 full 30 会话复跑验证；App「答对/答错」知识点自动分类（LLM）；真机化（等用户 2 条）
阻塞:         ⏳ 手机未连（型号/系统未知）——**只阻塞真机化，不阻塞 PC/模拟器任何工作**（adb/emulator 已自装好）；语音打断/静音/常听态已落地（真机 AEC/首字时延/近场 CER 待真机复测）
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
- **上次唤醒**：2026-11-09（第 20 轮 · 22:50 令「打断可用」落地：`host/vad.py` 端侧 VAD + App `MicVad.kt` 语音打断/静音真关麦/常听态指示、APK 4,124,752 字节装机+模拟器跑通一题、238 单测全绿）

## 2. 分层目标与状态（L0-L4）

| 层 | 目标 | 判据 | 状态 |
|:--|:--|:--|:--|
| L0 设备通路 | 手机与开发机连通 | 装包/截屏/拍照/出声各一条命令真实产物 | 🟡 PC mock 全通；真机待用户 3 条（P0 §4） |
| L1 单题闭环 | 拍题→识图→结构化→LLM 分步引导→TTS | 20 题 ≥15 识别正确，引导不含答案 | 🟢 4/4 识图 · P50 2.0s/P90 2.92s · 直接给答案率 0（题库待扩到 100 题） |
| L2 智能体 | 工具调用/多轮追问 | 5 工具可调、3 轮一致 | 🟢 5 工具 + 多轮一致（第15轮）；**已接 HTTP/App（/tool+/agent+App 换一题/记错题/报告/追问，第16轮）** |
| L3 学情 | 错题本+画像+每日/每周摘要 | 本地可导出 HTML | 🟢 **已交付（第17轮）**：l3_profile.py + POST /profile + App「学情」按钮；画像/摘要/HTML 全通，205 单测 |
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

## 4.12 本唤醒流水（2026-11-08 · 第 13 轮 · 11:40 令 §3 交互验收闭环 + clamp_hint）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md`；识别 22:50/12:20/12:05 令已闭环（第 10/11/12 轮），本轮按 ROADMAP「下一轮候选」#1 + 11:40 令 §3 交付**交互验收**（`eval/interaction_*.json`）。ComfyUI 全程未碰（已冻结）。
- ✅ 接续上一轮已 staging 未提交的 `host/eval_interaction.py`（latency/bargein/student 三模式）+ `test_interaction.py`（10 单测）+ `gen_interaction_report.py`：跑通并产出三个 JSON + 转写 + 91.2s 会话 TTS 录音（≥60s 达标）。
- ✅ **实测数字（`eval/interaction_*.json`）**：整轮响应 **P50 1.37s / P90 1.97s**（n=12，deepseek-flash 无静默降级）；TTS 首字 **P50 80.4ms / P90 99.3ms**（n=10，PC SAPI）；打断 stop 信号 **~0ms** + 在途句丢弃（n=8，逻辑版）；模拟学生 3 人设×10 轮，**直接给答案次数 = 0**（redline 确定性判定 ✅）。
- ✅ **`tutor_agent.py` 新增 `clamp_hint()`**：交互验收暴露 LLM 原始输出 3-6 句、超 11:40 令 §1.1「每次回复 ≤2 句」→ 新增确定性裁剪（≤2 句）+ 强化 TUTOR_SYSTEM 提示词（≤2 句/每句≤20 字）；`test_tutor_agent.py` 7 单测；smoke 实测 DeepSeek 单步输出「先想想，怎样让 2x 单独留在等号左边？」（0.82s，1 句，无答案）。
- ✅ **HTML 报告** `doc/BaiZe-ISEDA2027/reports/report_robot_hci_interaction_zh.html`（7.8KB，自包含：三项时延 / 打断 / 模拟学生 / 10 条可用性走查）。
- 🔧 **修 `gen_interaction_report.py` 两处 bug**：① CSS `width:100%` 的 `%` 未转义 → `ValueError: unsupported format character ';'`（改 `%%`）；② `REPORT_DIR` 少跳一级，把报告写进 `doc/personal-watch/BaiZe-ISEDA2027/` 错误目录（改 `../../../../BaiZe-ISEDA2027/reports`，并删掉误建目录）。`.gitignore` 补 `*.pid`/`*.err`，`git rm --cached` 撤掉误入索引的运行时 `.pid`/`.err`。
- ✅ **host 全量 `pytest` = 118 passed**（81 + 12 + 8 + 10 + 7）。
- 📌 **能信/不能信**：整轮响应 / TTS 首字（PC SAPI）/ 打断逻辑 = 本机实测；ASR 出字为 mock、当前句音频硬件中断 ≤300ms、AEC = **待真机**（16:5x 令「能信/不能信」，不谎称已测）。
- 回写：`eval_interaction.py`/`test_interaction.py`/`gen_interaction_report.py`/`test_tutor_agent.py`（新建）、`tutor_agent.py`（clamp_hint）、`.gitignore`、`INTERACTION_SPEC.md`（§7.1 实测值 + §10 交付状态）、`ROADMAP.md`（第 13 轮）、本文件、`daily-memories-video/2026-11-08.md`；HTML 报告。
- commit+push（`robot:`）。

## 4.13 本唤醒流水（2026-11-08 · 第 14 轮 · L1 全量 100 题 + 泄露检测误报修复）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md`；识别 22:50/12:20/12:05/11:40 令已闭环（第 10-13 轮），本轮按 ROADMAP「下一轮候选」#1 交付**题库扩到 100 题跑 L1 全量**。ComfyUI 全程未碰（已冻结）。
- 🔍 **发现上一轮（未提交）残留**：`eval/l1_full.json`（100 题）已生成，但 `question_bank.py` 源码丢失（只剩 pycache），且 summary 显示 `guidance_leak_rate=0.02` / `adversarial_leak_rate=0.02`（2 处「泄露」）。逐条定位：这 2 处是**误报**——`e009`「a 和 an 是按什么来选」（复述选项）、`e010` `Monday` 含子串 `on`、`e019`「填 Would 还是 Do」（复述选项），**不是真给答案**。
- ✅ **修复 `host/leak_check.py`**（确定性纯函数）：① 短英文单词改「词边界」匹配（`on` 不再命中 `Monday`、`an` 不再命中 `many`）；② 答案 token 已在题干原文（选项/复述）则不算泄露。`test_leak_check.py` 10 单测；用修复后判定回验旧 `l1_full.json` 同 100 条输出 → text_path/adversarial 泄露均 = 0（证明是误报非真泄露）。
- ✅ **重建 `eval/question_bank.py`**：100 题（数学 60 + 物理 20 + 英语 20），每题知识点 + 最终答案 + 泄露模式，题号/题干与上一轮 `l1_full.json` 一致；`test_question_bank.py` 5 单测。
- ✅ **`host/eval_l1_full.py` 全量实测**（100 文本 + 100 对抗 + 20 识图 = 220 次 deepseek-flash）：**直接给答案率 = 0**（guidance 0.0 / adversarial 0.0）；**识图正确率 1.0（20/20）**、`ocr_fallback_count=0`（无静默降级）；**首步 P50 1.16s / P90 2.07s**（11:40 令 ≤2.5s/≤4s ✅）；识图 P50 2.37s/P90 3.13s。
- ✅ **host 全量 `pytest` = 133 passed**（81 + 12 + 8 + 10 + 7 + 10 + 5）。
- 📌 **能信/不能信**：leak 判定为确定性纯函数（10 单测）；100 题引导/对抗/识图/时延为本机实测（无降级）。🚫 仍非真人/真机；识图只跑 m001-m020（几何/统计题含 △∠√°² 特殊字符，走文本路径评测，不做 snap 渲染识图）。
- 回写：`eval/question_bank.py`/`host/leak_check.py`/`host/eval_l1_full.py`/`host/test_leak_check.py`/`host/test_question_bank.py`（新建）、`eval/sample_questions.md`、`ROADMAP.md`（第 14 轮）、本文件、`daily-memories-video/2026-11-08.md`。
- commit+push（`robot:`）。

## 4.14 本唤醒流水（2026-11-08 · 第 15 轮 · L2 智能体工具层落地）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md`；识别 22:50/12:20/12:05/11:40 令均已闭环（第 10-14 轮），L0/L1/HCI 全部交付，唯一未交付的是 **ROADMAP L2 智能体（5 工具可调）**。本轮落地 L2。ComfyUI 全程未碰（已冻结）。
- ✅ **`host/tools.py`（5 工具 + 注册表）**：`calculator`（**AST 白名单**安全求值，🚫 不用 `eval`，拒绝变量→封堵「代解方程」）、`question_bank_lookup`（检索 `eval/question_bank.py` 100 题，**剥离 answer/leak** 只回题干）、`wrong_book_add/list`（本地 JSON 错题本，不上传）、`parent_report`（自包含中文 HTML，本地）、`plot_function`（matplotlib Agg 画 y=f(x)）。`tool_spec()/call_tool()` 供 LLM 决策与评测共用。
- ✅ **`host/l2_agent.py`（智能体编排层）**：`route_tool()` 确定性意图路由（离线可用）+ `decide_tool_llm()` 让 DeepSeek 从工具清单选工具（智能体主路径，失败回退路由）+ `L2Session` 维持一道题多轮会话。**关键修复**：工具轮次与引导历史分离（`history` 只喂 `tutor_step`，`tool_log` 单独记）——否则工具问答污染引导上下文，实测出现过「2x+3 没有等号」的幻觉。
- ✅ **`host/eval_l2.py` 实测**（`eval/l2_tools.json`）：**6 工具全调**（含 wrong_book_list）；**直接给答案率 = 0**（3 轮追问 + 「算方程解」红线封堵均不含答案）；**多轮 3 轮一致**（`history_len=3`，不再被工具轮污染）；`plot_function` 产出真实 PNG（20,347 字节）；`llm_tool_decision` 实测 DeepSeek 正确选 `calculator`（params `{"expr":"6*7"}`）。
- ✅ **host 全量 `pytest` = 175 passed**（原 133 + test_tools 21 + test_l2_agent 21）。
- 🔧 **本轮修 3 处 bug**：① 绘图路由未抽表达式 → `_extract_func()`；② 工具轮次混入引导历史 → 引导上下文幻觉；③ `\w` 默认匹配中文 → 表达式多抽「的」→ 改 `[0-9a-zA-Z...]` 显式 ASCII 字符类。另有 HTML 模板 `width:100%` 的 `%` 未转义（`%%`）。
- 📌 **能信/不能信**：5 工具 / 路由 / 红线封堵为**确定性纯函数**（42 单测）；`eval_l2.json` 的引导多轮与 LLM 工具决策为本机实测（deepseek-flash）。🚫 工具层目前只在 host 内跑，**未接进 App/HTTP**（`/tutor` 暂不支持工具参数），待下一轮接入。
- 回写：`host/tools.py`/`host/l2_agent.py`/`host/eval_l2.py`/`host/test_tools.py`/`host/test_l2_agent.py`（新建）、`host/README.md`、`ROADMAP.md`（第 15 轮）、本文件、`daily-memories-video/2026-11-08.md`。
- commit+push（`robot:`）。

## 4.15 本唤醒流水（2026-11-08 · 第 16 轮 · L2 工具/智能体接进 HTTP + App）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md`；识别 22:50/12:20/12:05/11:40 令均闭环（第 10-15 轮），本轮按 ROADMAP「下一轮候选」#1 交付**L2 工具接进 App/HTTP**（`/tutor` 增加 `tool`/`params`，App 加「换一题/记错题/报告」）。ComfyUI 全程未碰（已冻结，本轮提示再次确认停用）。
- ✅ **`tutor_server.py` 新增两端点 + 一处路由**：`POST /tool {tool, params}`（直接调 5 工具，`ToolError`→`{ok:false,error}`，红线拒变量/不泄答案）；`POST /agent {question, utterance, history?, use_llm?}`（L2 多轮，默认确定性路由离线可用，可选 LLM 决策）；`POST /tutor` 带 `tool` 字段即转工具（等价 `/tool`）。
- ✅ **`test_tutor_server.py` 13 单测** + `smoke_http.py`（起临时实例实测 `/health /tool /agent` 真实 JSON，静默服务端访问日志避免 PS 误判 stderr）。🔧 修 1 处 bug：`do_POST` 路由字典键漏 `/` 前缀 → `KeyError: '/tool'`。
- ✅ **App 接工具/追问**：`TutorClient.postTool/postAgent`；`MainActivity` 加「换一题/记错题/报告」三按钮（→`/tool`）+ 文字追问输入框 +「发送」（→`/agent`，无题干回退 `/tutor` 文字题）；`activity_main.xml` + `strings.xml` 同步。
- ✅ **构建 + 装机验证**：`assembleDebug` 成功 → `app-debug.apk` **4,112,860 字节**；`adb install -r` **Success**；`am start` + `uiautomator dump` 确认「换一题/记错题/报告/发送/追问」UI 元素在位。
- ✅ **host 全量 `pytest` = 188 passed**（175 + 13 新增）。
- 📌 **能信/不能信**：`/tool`/`/agent` 的确定性路由/红线封堵/不泄答案 = 确定性纯函数（13 单测）+ `smoke_http.py` 实测真实 JSON；App 侧为**装机 + UI dump 验证**（未在模拟器内端到端点按钮触发 DeepSeek，因本轮 ComfyUI 停用 + 不引入真实学生数据，工具链路已在 host 侧跑通）。🚫 端侧真实 ASR 仍未落地。
- 回写：`host/tutor_server.py`/`host/test_tutor_server.py`/`host/smoke_http.py`（新建）、`host/README.md`、`app/.../TutorClient.kt`/`MainActivity.kt`/`activity_main.xml`/`strings.xml`、`app/README.md`、`ROADMAP.md`（第 16 轮）、本文件、`daily-memories-video/2026-11-08.md`。
- commit+push（`robot:`）。

## 4.16 本唤醒流水（2026-11-08 · 第 17 轮 · L3 学情层落地 + 接 HTTP/App）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md`；识别 22:50/12:20/12:05/11:40 令均已闭环（第 10-16 轮），L0/L1/L2/HCI 已交付，唯一 ⬜ 是 **ROADMAP L3 学情（知识点画像 + 每日/每周摘要 + 可导出 HTML）**。本轮落地 L3 并接 HTTP/App。ComfyUI 全程未碰（已冻结）。
- ✅ **`host/l3_profile.py`（L3 学情层）**：错题本（`tools.WRONG_BOOK_PATH` 同源，本地不上传）→ `knowledge_profile()`（按知识点聚合 → 错题数/首末次出错/掌握等级「待练习/待巩固/薄弱/重点突破」）、`daily_summary()`/`weekly_summary()`（按日期/ISO 周聚合）、`build_profile_html()`（自包含中文 HTML，不泄答案/不含隐私）、`profile_report()`（落盘 + 摘要 JSON）。复用 `tools.WRONG_BOOK_PATH`（动态引用，可被 `ROBOT_WRONG_BOOK`/monkeypatch 覆盖）。
- ✅ **`tutor_server.py` 新增 `POST /profile {html?: bool}`** → `{ok, profile}`（知识点画像 + 每日/每周摘要）；`html=true` 另生成 `logs/profile_report.html`。
- ✅ **`test_l3_profile.py` 13 单测** + `test_tutor_server.py` 增 4 单测（/profile 摘要/不泄答案/HTML/空）。
- ✅ **App 接学情**：`TutorClient.postProfile()` + `MainActivity`「学情」按钮（→`/profile`，显示错题总数/涉及知识点/薄弱点）；`activity_main.xml` + `strings.xml` 同步。
- ✅ **构建 + 装机 + 端到端**：`assembleDebug` 成功 → `app-debug.apk` **4,115,732 字节**；`adb install -r` **Success**；`uiautomator dump` 确认「学情」按钮；**模拟器点击「学情」实测** → 显示「错题总数：2 / 涉及知识点：1 个 / 薄弱点：一元一次方程」。
- 🔧 **清 stale server**：前几轮遗留 2 个 `tutor_server.py` 进程仍占 `0.0.0.0:8765`（旧代码无 `/profile`，App 点「学情」拿到 404 回显 0）→ `netstat -ano | Select-String ':8765'` 定位 PID → `Stop-Process` → 端口释放后复测通过。
- ✅ **host 全量 `pytest` = 205 passed**（188 + 13 + 4）。
- 📌 **能信/不能信**：画像/摘要/HTML 为确定性纯函数（13 单测）+ `smoke_http.py` 实测真实 JSON + App 模拟器点击端到端；`logs/wrong_book.json` 为本地自造题数据。🚫 画像基于「错题本」单边数据（缺正样本「练习/作答」）；端侧真实 ASR 仍未落地。
- 回写：`host/l3_profile.py`/`host/test_l3_profile.py`（新建）、`host/tutor_server.py`/`host/test_tutor_server.py`/`host/smoke_http.py`、`host/README.md`、`app/.../TutorClient.kt`/`MainActivity.kt`/`activity_main.xml`/`strings.xml`、`app/README.md`、`ROADMAP.md`（第 17 轮）、本文件、`daily-memories-video/2026-11-08.md`。
- commit+push（`robot:`）。

## 4.17 本唤醒流水（2026-11-08 · 第 18 轮 · 端侧真实 ASR 落地：sherpa-onnx 离线 + 真流式）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md`；识别 ROADMAP「下一轮候选」#1 = 端侧真实 ASR（sherpa-onnx）接入位落地（`SherpaOnnxASR` 现为报错占位），是 12:20 令「端侧为主」最后一环。本轮落地。ComfyUI 全程未碰（已冻结，本轮提示再次确认停用）。
- ✅ **`host/speech.py` `SherpaOnnxASR` 报错占位 → 真实离线识别**：`sherpa_onnx.OfflineRecognizer.from_paraformer`（中文离线，16kHz）→ `transcribe(samples,sr)` / `transcribe_file(wav)` / `stream(wav, chunk_ms)`（前缀增量模拟流式中间结果，如实标注「非真流式」）。
- ✅ **`host/speech.py` 新增 `StreamingSherpaOnnxASR`（真流式）**：`sherpa_onnx.OnlineRecognizer.from_transducer`（streaming-zipformer 中文）→ `stream(wav, chunk_ms)` 逐块喂入、逐块 yield 增长中间结果；`transcribe_file()` 整段。修复 1 处 bug：sherpa-onnx 2.0.1 `get_result()` 返回 str（非 `.text`），用 `hasattr` 兼容。
- ✅ **`host/speech.py` 新增 `load_wav_mono()` / `_resample_linear()`**：任意 WAV（含 48k 立体声）→ 16kHz mono float32。
- ✅ **`host/eval_asr.py`**：SAPI TTS 合成 8 条已知中文（6 自然句 + 2 数学口述）→ 两引擎识别 → CER；产出 `eval/asr_streaming_zipformer_zh.json`（离线 paraformer 未就绪则 skip）。
- ✅ **模型落地（hf-mirror，直连 GitHub releases 超时）**：流式 `streaming-zipformer-zh-14M`（encoder 21,621,684 + decoder 7,509,745 + joiner 1,795,562 + tokens 48,697 字节，~31MB）已就绪；离线 `paraformer-zh`（`model.int8.onnx` 243,371,218 字节）后台下载中。
- ✅ **流式 CER 实测（真实输出）**：streaming-zipformer mean_cer=0.302 / easy_mean_cer=0.297，单条延迟 0.03–0.08s，中间结果逐字增长（`我们→我们先→我们先把→…`）。⚠️ 14M 小模型精度偏低，属「真流式落地」证据；高精度待 paraformer 离线下载完成补测。
- ✅ **`test_speech.py` 增测**：模型缺失报错×2 / WAV 读取 16k / 48k→16k 重采样 / 真实识别（离线+流式，skipif 模型在位时跑）。
- ✅ **host 全量 `pytest` = 209 passed + 1 skipped**（205 → +4 新增）。
- 📌 **能信/不能信**：CER 为「SAPI 合成语音回读」字错率（PC 端端侧真实推理证据，非估算）；真机麦克风近场 CER / 流式首字延迟 / AEC 待真机复测。🚫 14M 流式模型精度低；离线 paraformer 本轮未跑（下载中）。
- 回写：`host/speech.py`/`host/test_speech.py`/`host/eval_asr.py`（新建）、`host/README.md`、`INTERACTION_SPEC.md`、`ROADMAP.md`（第 18 轮）、本文件、`daily-memories-video/2026-11-08.md`。
- commit+push（`robot:`）。

## 4.18 本唤醒流水（2026-11-08 · 第 19 轮 · L3 学情补「正样本」：作答次数/正确率合并错题本）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md`；识别 ROADMAP「下一轮候选」#3 = L3 学情补「正样本」（当前画像只有错题单边数据）。本轮落地。ComfyUI 全程未碰（已冻结，本轮提示再次确认停用）。
- ✅ **`host/l3_profile.py` 新增练习日志（正样本）+ 合并画像**：`PRACTICE_LOG_PATH`（`ROBOT_PRACTICE_LOG` 可覆盖）+ `load_practice_log()`/`log_practice()`（记录作答对错，落本地不上传）+ `practice_summary()`（按知识点作答次数/答对数/正确率）+ `mastery_from_stats()`（富化掌握等级，新增「已掌握」）+ `merged_profile()`（错题本负样本 + 练习正样本合并：`wrong_count/attempt_count/correct_count/correct_rate/mastery`）+ `build_profile_html_full()`/`profile_report_full()`（自包含中文 HTML，不泄答案/题干/作答原文）。
- ✅ **`host/tutor_server.py` 新增 `POST /practice`**（`{question, correct, knowledge?, student_answer?}` → 记录作答、返回累计 `total_practice` + 合并画像）；`POST /profile` 升级为**合并画像**（错题 + 正样本，含 `total_practice`/`knowledge_points`/`practice`）。
- ✅ **单测 +13**：`test_l3_profile.py` +9（练习摘要/合并画像/富化掌握/日志追加/合并 HTML）、`test_tutor_server.py` +3（/practice 记录+合并/不泄答案/缺 question 报错）；host 全量 **`pytest` = 222 passed**（第 18 轮 209+1 skip → 222，paraformer 已就绪）。
- ✅ **App 接正样本**：`TutorClient.postPractice()` + `ProfileReply` 富化（`totalPractice`/`practiceSummary`）；`MainActivity`「答对/答错」按钮（→`/practice`，自动刷新学情）+「学情」显示「错题总数/练习次数/涉及知识点/薄弱点/作答摘要」；`activity_main.xml`/`strings.xml` 同步。
- ✅ **构建 + 装机 + 端到端 + 录屏**：`assembleDebug` 成功 → `app-debug.apk` **4,120,020 字节**；`adb install -r` **Success**；模拟器点「学情」实测显示「错题总数：3 / 练习次数：5 / 涉及知识点：2 个 / 薄弱点：一元一次方程 / 作答：一元一次方程 2次/50% · 勾股定理 3次/100%」；录屏 `logs/r19_session.mp4`（18s，2,756,131 字节）。
- 📌 **能信/不能信**：合并画像/富化掌握/不泄答案为**确定性纯函数**（单测）+ seed 脚本实测真实 JSON + App 模拟器点击端到端；`logs/wrong_book.json`/`logs/practice_log.json` 为本地自造题数据。🚫 App「答对/答错」暂以「未分类」记录知识点（LLM 知识分类未接入）；真机近场 ASR/AEC 仍待复测。
- 回写：`host/l3_profile.py`/`host/test_l3_profile.py`/`host/tutor_server.py`/`host/test_tutor_server.py`/`host/README.md`、`app/.../TutorClient.kt`/`MainActivity.kt`/`activity_main.xml`/`strings.xml`/`app/README.md`、`ROADMAP.md`（第 19 轮）、本文件、`daily-memories-video/2026-11-08.md`。
- commit+push（`robot:`）。

## 4.19 本唤醒流水（2026-11-09 · 第 20 轮 · 22:50 令「打断可用」：端侧 VAD + App 语音打断/静音/常听）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md`；识别 22:50 令里程碑最后一项「打断可用」仍只有按钮打断（手动），缺「语音打断 + 静音真关麦 + 常听态」，且 INTERACTION_SPEC §9「VAD 端侧」无独立代码。本轮落地。ComfyUI 全程未碰（已冻结）。
- ✅ **`host/vad.py`（端侧 VAD 纯函数）**：`rms`/`rms_db`、`EndpointDetector`（静音 ≥1.2s 端点）、`BargeInDetector`（连续 2 帧超阈 + hangover；单帧尖峰不触发）、`MuteGate`（静音真关麦）、`SessionController`（状态机 ambient/listen/think/speak/wait_student/muted）。16 单测；host 全量 **238 passed**（222 → +16）。
- ✅ **App 端语音打断 + 静音真关麦 + 常听态指示**：新增 `MicVad.kt`（`AudioRecord` 16kHz 端侧 VAD，`start()/stop()`，无麦克风/无权限优雅降级不崩溃）；`MainActivity` 状态指示 +「静音」按钮（真关麦=释放 AudioRecord）+ 语音打断（朗读中检测到人声 → `stopSpeaking()`）；`AndroidManifest.xml` 加 `RECORD_AUDIO`；`activity_main.xml`/`strings.xml` 同步。
- ✅ **构建 + 装机 + 端到端 + 录屏**：`assembleDebug` 成功 → `app-debug.apk` **4,124,752 字节**；`adb install -r` **Success**；模拟器跑通一题（文字题 `2x+3=11` → DeepSeek 引导「我们一起来看看这道题。你觉得第一步该先动哪个数呢？」**不含答案 x=4** ✅红线 → 状态「说」→ 打断「听」→ 静音「静音」→ 解除「常听」）；录屏 `logs/r20_session.mp4`（4,431,529 字节）+ 截图 `logs/r20_app_launch.png`。
- 📌 **能信/不能信**：VAD 纯逻辑（16 单测）+ App 状态机 UI 流转 + 文字题端到端为可验证证据；🚫 真实声学语音打断（AEC 自听回声）、首字时延、近场 CER 待真机/真麦克风复测（模拟器无真实人声输入）。
- 回写：`host/vad.py`/`host/test_vad.py`、`app/.../MicVad.kt`/`MainActivity.kt`/`AndroidManifest.xml`/`activity_main.xml`/`strings.xml`/`app/README.md`、`ROADMAP.md`（第 20 轮）、`INTERACTION_SPEC.md`、本文件、`daily-memories-video/2026-11-09.md`。
- commit+push（`robot:`）。

## 4.20 本唤醒流水（2026-11-09 · 第 21 轮 · ROADMAP「下一轮候选 #5」：App 答对/答错「知识点自动分类」）

- 读任务书全文 + `robot/README.md` + `ROADMAP.md` + `INTERACTION_SPEC.md`；识别 ROADMAP 唯一剩余可交付候选「App 答对/答错知识点自动分类（LLM）」——此前 `POST /practice` 在 App 不带 `knowledge` 时一律记「未分类」，正样本进不了知识点画像。本轮落地。ComfyUI 全程未碰（已冻结）；手机未连走 Android 模拟器（emulator-5554 在线）。
- ✅ **`host/knowledge.py`（知识点自动分类，LLM + 本地兜底）**：`classify_knowledge_local()` 确定性关键词分类（纯函数、无网络，**100 题全对 100/100**，61 类知识点规则表，英语选项里的 `/` 不会被误判成分式）+ `classify_knowledge()`（主路径 DeepSeek 分类、失败/判不出自动降级本地关键词，trace 里 `fallback` 非空即降级，🚫 不静默）+ `_normalize()`（LLM 输出归一，学科名「数学/物理」与整句废话→「未分类」，不瞎猜）。
- ✅ **`host/tutor_server.py` 接自动分类**：`POST /practice` 缺省 `knowledge` 时调 `knowledge.classify_knowledge()`，出参新增 `knowledge` + `classify`（trace）。
- ✅ **App 显示分类**：`TutorClient.kt` `PracticeReply` 增 `knowledge`；`MainActivity` 答对/答错后状态栏显示「已记录「答对」· 知识点：xx（累计作答 N 次）」，`showProfile(keepStatus=true)` 刷新学情不覆盖该状态。
- ✅ **单测 +47**：`test_knowledge.py` 44 条 + `test_tutor_server.py` +3 条；host 全量 **`pytest` = 285 passed**（238 → 285）。
- ✅ **构建 + 装机 + 端到端 + 录屏**：`assembleDebug` → `app-debug.apk` **4,157,236 字节**；`adb install -r` **Success**；模拟器文字题 `5x-3=12` → 答对 → 状态栏「已记录「答对」· 知识点：一元一次方程（累计作答 10 次）」+ 学情「作答：一元一次方程 6次/83% · 勾股定理 4次/100%」；HTTP 直测 `/practice`（无 knowledge）→ `knowledge=勾股定理`（LLM deepseek，fallback=null）；录屏 `logs/r21_session.mp4`（20,301,907 字节）+ 截图 `logs/r21_mark.png`（344,168 字节）。
- 📌 **能信/不能信**：本地关键词分类 100 题 100/100 + LLM 分类 DeepSeek 实测 + App 状态栏/学情端到端为可验证证据；🚫 分类「准确性」对任意真实/变形题干仍以 LLM 为主、本地关键词兜底，未做超题库准确率回归；真机近场 ASR/AEC 仍待复测。
- 回写：`host/knowledge.py`/`test_knowledge.py`、`host/tutor_server.py`/`test_tutor_server.py`、`app/.../TutorClient.kt`/`MainActivity.kt`、`host/README.md`、`app/README.md`、`ROADMAP.md`（第 21 轮）、`INTERACTION_SPEC.md`、本文件、`daily-memories-video/2026-11-09.md`。
- commit+push（`robot:`）。

## 5. 阻塞 / 待办

1. **⏳ 等用户 2 条回复**（`P0_设备通路.md` §4）：① 手机型号/系统版本 ② 开 USB 调试并连线（adb/hdc 已由本线自装，不再需要用户装）。
   🚫 **只阻塞「真机化」，不阻塞 PC/模拟器任何工作**（16:5x 令 §5：不得再以此为由停摆）。
2. ~~`qwen3-vl:32b` 20GB GGUF 缺失~~ → **已作废**（15:4x 令：识图走 DeepSeek，本地 `llava` 只做离线兜底）。
3. **下一轮候选（按优先级）**：
   1. ~~端侧真实 ASR（sherpa-onnx）接入位落地~~ ✅ **已交付（第 18 轮，paraformer 离线 + streaming-zipformer 真流式）**；
   2. ~~22:50 令「打断可用」（语音打断/静音真关麦/常听态 + 端侧 VAD）~~ ✅ **已交付（第 20 轮，`vad.py` + App `MicVad.kt` 语音打断/静音/常听）**；
   3. `clamp_hint` 后的 full 30 会话复跑验证（第 13 轮只做了单次 smoke）；
   4. ~~L3 学情补「正样本」~~ ✅ **已交付（第 19 轮，练习日志 + 合并画像 + `/practice` 端点 + App「答对/答错」）**；
   5. ~~App「答对/答错」知识点自动分类（LLM）~~ ✅ **已交付（第 21 轮，`knowledge.py` LLM+本地兜底 + `POST /practice` 自动补 + App 状态栏显示分类）**；
   6. 真机化 L0（等用户 2 条）。

## 6. 运维问答

> （暂无）
