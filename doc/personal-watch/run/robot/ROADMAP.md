# ROADMAP.md — robot 线分层目标与增量记录

> 权威指令：`run/WATCH_VIDEO_TASK.md` 顶部「2026-11-07 11:10」块（L0-L4 分层 + 判据）。
> 每轮一个**可验证增量**，🚫 不许只写文档。

| 层 | 目标 | 判据 | 状态 |
|:--|:--|:--|:--|
| L0 设备通路 | 手机与开发机连通：装包/截屏/拍照/出声 | 各一条命令拿到真实产物 | 🟢 **模拟器全通**（ADB+emulator+AVD+APK 安装+App 闭环+录屏，第10轮）；真机仍待用户 3 条（P0 §4） |
| L1 单题闭环 | 拍题 → 识图 → 结构化 → LLM 分步引导 → TTS | 20 题 ≥15 题识别正确，引导不含答案 | 🟢 **100 题全量达标（第 14 轮）**：识图 20/20=1.0、首步 P50 1.16s/P90 2.07s、直接给答案率 0、无静默降级 |
| L2 智能体 | 工具调用：题库/错题本/计算器/绘图/家长报告；多轮不丢上下文 | 5 工具可调，3 轮追问一致 | 🟢 **5 工具可调 + 已接 HTTP/App（第 15/16 轮）**：6 工具全调、直接给答案率 0、3 轮追问一致、LLM 工具决策正确；`/tool` `/agent` 端点 + App「换一题/记错题/报告/追问」；188 单测 |
| L3 学情 | 错题本 + 知识点画像 + 每日/每周摘要，本地存储 | 数据落本地，可导出 HTML | ⬜ |
| L4 形态 | 桌面实体机器人（需硬件） | 待用户确认 | ⬜（形态口径：自家 8 年级女儿用的桌面端，见 12:05 令） |

## 本轮增量（2026-11-07 · 第 1 轮）

- ✅ `P0_设备通路.md`：adb/hdc 未装、手机未连（真实命令输出），选定 **R3** 路线，用户清单 5 条。
- ✅ `host/tutor_agent.py`：题图/题文 → `llava` OCR → `qwen3:8b` 分步引导（内置「不泄答案」系统提示词 + `--answer` 红线自检）→ Windows SAPI TTS 出声。
- ✅ `proto/mock_device.py`：模拟手机「拍照」（渲染题图 PNG）。
- ✅ `eval/sample_questions.md`：3 道自造题（数学×2 + 物理×1）+ q1 分步 rubric。
- ✅ 端到端真跑通：`2x+3=11` 题图 → 识别正确 → 引导不含答案 → 产出 48kHz 真实 WAV。

## 第 2 轮复验（2026-11-07 · 定位「最弱一环 = OCR」）

- ✅ P0 结论复验：`adb`/`hdc` 仍未安装、`Get-PnpDevice` 未检测到任何华为/ADB/HDC 设备；`ollama list` 8 个模型在位。
- ✅ 链路复跑通：题图 → OCR → `qwen3:8b` 引导 → SAPI TTS，每步真实产物。
- ⚠️ **发现 OCR 不稳**：`llava` 读**纯算式**（`2x + 3 = 11`）正确，读**中文+算式混合**（`解方程：2x + 3 = 11`）连续误读（`二十一 加 二 等于 12` / `两个数相乘等于 11 加上 3`）→ 不满足 L1「≥15/20」。
- ✅ 分步引导 + TTS 两步稳定且不泄答案（文本路径红线自检未触发）。
- 根因 = `qwen3-vl:32b` 仍 404；修复 = `ollama pull qwen3-vl:32b`（20GB，后续轮做）。

## 第 3 轮增量（2026-11-07 · 评测基线 + 精确根因）

- ✅ 新增 `host/eval_l1.py`：可重复跑的 L1 基线评测（文本路径 3 题 + 对抗性「直接要答案」探针 + OCR 2 图），产出 `eval/l1_baseline.json`。
- ✅ 实测「直接给答案率 = 0」：正常引导 3/3 不含答案；**明确要答案时 3/3 拒绝**、仍只问思路——教育红线 1 顶得住。
- ⚠️ 实测 OCR 正确率 0.5：`llava` 读纯算式 `2x+3=11` ✅；读中文+算式混合 `解方程：2x+3=11` ❌（返回「无法解析图像」）。
- ✅ 精确定位 `qwen3-vl:32b` 404 根因：真实模型目录 `E:\ollama\models`，其 manifest 引用的 20GB GGUF blob `sha256-6e41…` 缺失（非「D:\ 为空」的误判）。
- ✅ 最小 demo 复跑：`--image q1_pure.png --speak --answer "4"` → 识别正确 → 引导不含答案 → 产出 1.15MB WAV。

## 第 4 轮增量（2026-11-07 · OCR 非确定性根因修复）

- 🔴 **定位 OCR「时对时错」真因 = 非确定性**：`llava` OCR 默认 temperature 随机，同一张 `2x+3=11` 题图 3 次读成 `我们不会看到这个问题` / `1+3=11` / `2x+3=11`（3 次只对 1 次）。
- ✅ **修复**：`tutor_agent.py` OCR 调用加 `options.temperature=0`（确定性解码）→ 同一张图 3 次全对、全一致。
- ✅ **OCR 正确率 0.5 → 1.0**（真跑 `eval_l1.py`）：纯算式、中文+算式混合（方程内容）都稳定读对；直接给答案率仍 = 0。
- ✅ 新增英文提示词兜底（中文提示词拒识时），`eval_l1.py` 加 `_math_norm`（只比数学骨架，忽略「解方程：」标签）。
- ⚠️ 残留：`llava` 读中文长题干（应用题/几何题）仍不可靠，只稳在算式/表达式；要覆盖中文应用题仍需 `qwen3-vl:32b`。

## 第 5 轮增量（2026-11-07 · 识图/引导切云端 DeepSeek + 端到端复跑 + P0 三度复验）

- ✅ **P0 三度复验（真实命令）**：`adb`/`hdc` 仍未装；把「没有华为设备」证到 **VID 级**——USB 上只有 `046D`(罗技摄像头)/`1A2C`(键鼠)/`30FA`/`8087`，**华为 VID `12D1` 一个都没有**；`qwen3-vl:32b` 仍 404；DeepSeek `GET /models` = 200（`deepseek-flash` / `deepseek-v4-pro`）。
- ✅ **`host/tutor_agent.py` 接云端（15:4x 令）**：`recognize()` **签名不变**，新增 `ROBOT_VISION_BACKEND=deepseek|ollama`（默认 deepseek）与 `ROBOT_TUTOR_BACKEND=deepseek|ollama`（默认 deepseek）；失败自动降级本机 ollama，**降级原因写进 `LAST_VISION_TRACE`/`LAST_TUTOR_TRACE` 并在 CLI 打印**（不许静默降级）；key 只从 `DEEPSEEK_API_KEY` 或 `~/.cline/data/secrets.json` 读，不落盘不打印。
- ✅ **识图正确率 0.5 → 1.0（4/4）**：新增中文应用题 `q2_geometry` 与代数式 `q3_expr` 两张题图；DeepSeek 逐字读对（含 `已知等腰三角形顶角为 40°，求底角的度数。`）；对照纯本地 `llava` 只 2/4。
- ✅ **首步时延达标（11:40 硬指标）**：DeepSeek 路径 **P50 2.0s / P90 2.92s**（目标 ≤2.5 / ≤4）；对照纯本地 `qwen3:8b` P50 5.72s / P90 6.83s（不达标）→ **主路径必须走云端**。
- ✅ **直接给答案率仍 = 0**：正常引导 3/3 + 对抗探针 3/3 全拒答（DeepSeek 与本地两套后端都验过）。
- ✅ **最小 demo 端到端**：中文应用题题图 → 识图 1.51s → 首步引导 1.31s → **总时延 2.81s** → 48kHz/17.72s WAV；降级演练（`DS_BASE` 指向不可达端口）同样跑通并明确标注降级。
- ✅ **`eval_l1.py` 升级**：4 张题图（算式/中文+算式/中文应用题/代数式）、`mode=math|text` 双口径判定、`ocr_fallback_count`、**P50/P90**、逐条记录真实后端；`_math_norm` 增加「中文算式词 → 符号」有限归一（`加→+`/`等于→=`…）。
- ✅ **修 headless TTS 崩溃**：无音频输出时 `SAPI.Speak()` 抛 COM 异常会让 demo 崩 → 改为**降级纯文字 + 提示**（`--speak out.wav` 仍恒可用）。
- ⚠️ **未达标（记入下一轮）**：单句长度超出 11:40 令「每句 ≤20 字 / 每次 ≤2 句」（实测约 75 字 / 3 句）；题图上云缺 UI 侧「云端/纯本地」可见标识与一键切换。

## 第 6 轮复验（2026-11-07 · 按 11:10 令全链路复跑 · 无回归）

- ✅ **P0 四度复验（真实命令）**：`adb`/`hdc` 仍未装（`ANDROID_HOME` 空）；USB 仍无华为 `12D1`（仅 `30FA`/`046D`/`1A2C`/`8087`）；DeepSeek `GET /models`=200；`ollama list` 8 模型在位。
- ✅ **路线 R3 维持**（复核：云端 DeepSeek 让 R3 一步达标，零新账号）。
- ✅ **最小 demo 端到端**：`mock_device --snap` 中文几何题 → DeepSeek 视觉**逐字读对**（1.52s）→ 首步引导「等腰三角形两个底角有什么特点？」（**不含 70°**，1.43s）→ **总时延 2.95s** → 48kHz WAV。
- ✅ **L1 四指标复跑（`eval_l1.py` 云端）**：识图 **4/4=1.0**；首步 **P50 1.51s / P90 2.22s**（≤2.5/≤4 达标）；**直接给答案率 0**（正常 3/3 + 对抗 3/3 全拒）；`ocr_fallback_count=0`（无静默降级）。
- 📌 **结论**：第 6 轮与第 5 轮一致、无回归；11:10 令（P0 → 选路线 → 最小 demo）已闭环；用户清单维持 **3 条（≤5）**。

## 第 7 轮复验（2026-11-07 · 按 11:10 令全链路复跑 · 无回归）

- ✅ **P0 五度复验（真实命令）**：`adb`/`hdc` 仍未装（`Get-Command` 均 `$null`，`ANDROID_HOME` 空）；USB `VID` 仍无华为 `12D1`（仅 `30FA`/`046D`/`1A2C`/`8087`）；`GET api.deepseek.com/models`=200 且 `deepseek-flash` 官方 `input_modalities=[text,image]`（key 来自 `secrets.json`，未打印）；`ollama list` 8 模型在位。
- ✅ **路线 R3 维持**（复核：云端 DeepSeek 让 R3 一步达标、零新账号/零采购）。
- ✅ **最小 demo 端到端（PC 端 mock）**：中文几何题 → DeepSeek 视觉逐字读对（1.58s）→ 首步引导「两个底角之间是什么关系呢？」（**不含 70°**，1.75s）→ **总时延 3.33s** → 48kHz WAV。
- ✅ **L1 四指标复跑（`eval_l1.py` 云端）**：识图 **4/4=1.0**；首步 **P50 1.6s / P90 1.78s**（≤2.5/≤4 达标）；**直接给答案率 0**（引导 0/3 + 对抗 0/3 全拒）；`ocr_fallback_count=0`（无静默降级）。
- 📌 **结论**：与第 6 轮一致、无回归；11:10 令（P0 → 选路线 → 最小 demo）持续闭环；用户清单维持 **3 条（≤5）**。

## 第 8 轮复验（2026-11-07 · 按 11:10 令全链路复跑 · 无回归）

- ✅ **P0 六度复验（真实命令）**：`adb`/`hdc` 仍未装（`Get-Command` 均 `$null`，`ANDROID_HOME` 空）；USB `VID` 仍无华为 `12D1`（仅 `30FA`/`046D`/`1A2C`/`8087`）；`GET api.deepseek.com/models`=200 且 `deepseek-flash` 官方 `input_modalities=[text,image]`、`deepseek-v4-pro` 仅 text（key 来自 `secrets.json`，未打印）；`ollama list` 8 模型在位。
- ✅ **路线 R3 维持**（复核：云端 DeepSeek 让 R3 一步达标、零新账号/零采购）。
- ✅ **最小 demo 端到端（PC 端 mock）**：中文几何题 → DeepSeek 视觉逐字读对（2.36s）→ 首步引导「我们先不急着算。先回忆一下：等腰三角形里，两个底角之间有什么关系呢？」（**不含 70°**，1.52s）→ **总时延 3.88s** → 48kHz WAV。
- ✅ **L1 四指标复跑（`eval_l1.py` 云端）**：识图 **4/4=1.0**；首步 **P50 1.25s / P90 1.27s**（≤2.5/≤4 达标）；**直接给答案率 0**（引导 0/3 + 对抗 0/3 全拒）；`ocr_fallback_count=0`（无静默降级）。
- 📌 **结论**：与第 7 轮一致、无回归；11:10 令（P0 → 选路线 → 最小 demo）持续闭环；用户清单维持 **3 条（≤5）**。

## 第 9 轮增量（2026-11-07 · 执行 20:05 令交付 INTERACTION_SPEC.md）

- ✅ **`INTERACTION_SPEC.md` 交付（20:05 令本轮唯一交付）**：四态状态机 + 常听 `ambient` + 异常态（`clarify`/`encourage`/`presence`/`idle`/`muted`），状态机 2 图（ASCII 29 行 + mermaid 17 行）+ 状态表 10 行；三层提示阶梯 L1/L2/L3（禁跳级、禁给答案）；**话术模板 21 条**；**时延指标 13 条**（P50≤2.5s/P90≤4s/打断≤300ms/静默 6s→10s 等）；打断协议、静默/超时/降级矩阵、在座检测（presence）、语音链路端侧定稿。
- ✅ **P0 七度复验（真实命令）**：`adb`/`hdc` 仍未装（`Get-Command` 均 `$null`）、`ANDROID_HOME` 空、USB `VID` 无华为 `12D1`（仅 `30FA`/`046D`/`1A2C`/`8087`）——与第 8 轮一致、无回归。
- 📌 **结论**：HCI 规范的「设计/口径」已定稿；代码（speech.py/presence.py/normalize_math.py）与实测验收留待下一轮，本轮不谎称已测。11:10 令（P0→路线→demo）维持闭环，不再重复复跑。

## 第 10 轮增量（2026-11-08 · 执行 22:50 令：可安装真 App + 自建开发环境 + 模拟器跑通）

- ✅ **自建开发环境落地（真实命令）**：`C:\Android\` 下 `platform-tools`(adb 37.0.1) + `cmdline-tools` + `jdk17`(Temurin 17.0.16+8) + `gradle-8.7` + `emulator` + `build-tools` + `platforms;android-34` + `system-images;android-34;google_apis;x86_64` 全在；AVD `robot34` 已建（`emulator -list-avds` → `robot34`）。
- ✅ **模拟器启动 + 验收**：`emulator -avd robot34 -gpu swiftshader_indirect -no-window ...` → `adb devices` 见 `emulator-5554 device`，`getprop sys.boot_completed=1`（WHPX 硬件加速 `operational`）。
- ✅ **APK 构建**：`app/`（Kotlin + CameraX + 系统 TTS + HttpURLConnection，零第三方网络依赖）`:app:assembleDebug` → `app-debug.apk` = 4,088,176 字节，BUILD SUCCESSFUL in 3m22s。
- ✅ **`adb install` Success** + App 启动 UI 完整渲染（`uiautomator` 见 tvStatus「语音就绪」/ 拍照/选图/朗读/打断 / 服务地址 `http://10.0.2.2:8765`）。
- ✅ **App 端完整闭环（模拟器内跑通一题）**：选图 `q2_geometry.png` → 上传 → DeepSeek 视觉识图「已知等腰三角形顶角为 40°，求底角的度数。」→ 分步引导「…等腰三角形的两个底角，大小有什么关系呢？」（**不含 70°**）→ 屏幕显示 + 系统 TTS「朗读中」。打断/朗读按钮工作。
- ✅ **录屏取证**：`logs/robot_session.mp4` = 12,162,070 字节（45s；打断→朗读→选图→出引导）。
- ✅ **PC 侧 `/tutor` 服务**：`host/tutor_server.py` 监听 `0.0.0.0:8765`；`/health`=200；文本题 1.2s（deepseek-flash，无静默降级）；App 经 `10.0.2.2:8765` 联调成功。
- 📌 **结论**：22:50 令（可安装真 App）+ 22:30/22:35/22:40 令（模拟器跑通客户端 + 自装工具链）**全部闭环**；模拟器「能信/不能信」已写入 `P1_模拟器.md` §7。

## 第 11 轮增量（2026-11-08 · 交付 HCI 代码层：normalize_math.py + speech.py）

- ✅ **`host/normalize_math.py`（12:20 令 §4）**：口述→数学式纠错，覆盖全部词表（平方/立方/根号/分之/负/加减乘除/等于/大于小于/π/度/角/三角形/平行/垂直/相似/全等/分母/分子/一次项/二次项/移项/合并同类项）；权威示例实测一致：`x的平方加三x等于零 → x^2+3x=0`、`二分之根号三 → √3/2`；术语「三角形/一次项/二次项/分母/分子/移项/合并同类项」不破坏（汉字数字不误转）。
- ✅ **单测 81 条**（要求 ≥30，超标 2.7 倍）`pytest` 全绿。
- ✅ **`host/speech.py`（12:20 令 §2/§3 + INTERACTION_SPEC §9）**：统一接口 `asr_stream()/tts_stream()/stop()`；端侧默认（Windows SAPI 分句流式 + 句间停顿 + 打断 + `MockStreamingASR` 流式 mock），云端 `CloudASR/CloudTTS` 留空实现（默认 off，构造即报「不新增语音厂商账号」），`SherpaOnnxASR` 接入位（未装权重给明确报错、不静默）。
- ✅ **单测 12 条**（分句/打断标志/ASR 流式顺序与打断/TTS 落盘 WAV/打断丢弃在途/云端与端侧未装报错），全绿；实测 TTS 合成 48kHz WAV、打断后丢弃剩余句。
- ✅ **实测输出**：`py -3.10 -m pytest test_normalize_math.py test_speech.py -q` → **`93 passed in 0.46s`**（81 + 12）。
- 📌 **结论**：12:20 令 §2/§3/§4 代码交付闭环；`speech.py` 的 ASR 真实 CER / TTS 首字 / 打断 ≤300ms / AEC 均**标注待真机**（本机无端侧 ASR 权重，用 mock 只验逻辑，不谎称已测）。

## 第 12 轮增量（2026-11-08 · 交付 host/presence.py 在座检测 + PC 摄像头实测）

- ✅ **`host/presence.py`（12:05 令 §1/§5）**：单帧 320×240 + 亮度阈值 + **YuNet 人脸**（`cv2.FaceDetectorYN`，OpenCV 5 内置；因 5.0 已移除 CascadeClassifier/HOGDescriptor）三分类 `person/left/unknown`；帧端侧处理、立即丢弃不落盘不上传；统一帧源抽象 `FrameSource`（`WebcamSource` 默认 / 测试可 mock）；`measure()` 连拍测帧率耗时。
- ✅ **模型自举**：`host/models/face_detection_yunet_2023mar.onnx`（232KB，OpenCV Zoo Apache-2.0）；缺模型报明确 RuntimeError 不静默；权重 `*.onnx` 按体积红线不入库（`run/.gitignore`）。
- ✅ **单测 8 条**（`test_presence.py`）：三分类 / 300ms 预算字段 / 模型缺失报错 / 自动找模型；**host 全量 101 passed**（81 + 12 + 8）。
- ✅ **PC 摄像头实测（Logitech 046D，20 次）**：帧率 **29.71 fps**；单次抓帧+检测 **P50 33.0ms / P90 57.4ms / max 66.4ms**，**20/20 ≤300ms**（12:05 令硬指标 M12 ✅）。
- ✅ **准确率 20 标注样本 = 20/20 = 1.0**（person 8 + left 8 + unknown 4 全对）。
- ⚠️ 样本为「无歧义」集（清晰人脸 / 明显无人风景静物 / 合成暗帧）；遮挡/逆光/侧脸/远景小脸等**难例待真人/真机复测**（16:5x 令「能信/不能信」，不把 PC 结论当真机结论）。

## 第 13 轮增量（2026-11-08 · 11:40 令 §3 交互验收闭环 + `clamp_hint` 修复「输出过长」）

- ✅ **11:40 令 §3 交互验收闭环**：`host/eval_interaction.py`（三模式 latency/bargein/student）+ `test_interaction.py`（10 单测）+ `gen_interaction_report.py`（自包含中文 HTML）。实测：整轮响应 **P50 1.37s / P90 1.97s**（n=12，deepseek-flash 无降级）；TTS 首字 **P50 80.4ms / P90 99.3ms**（n=10，PC SAPI）；打断 stop 信号 **~0ms** + 在途句丢弃（n=8，逻辑版）；模拟学生 3 人设×10 轮，**直接给答案次数 = 0**（redline ✅）。
- ✅ **会话录音 91.2s（≥60s ✅）** + 转写 `eval/interaction_session_transcript.md`（git 内）+ `interaction_session_audio.wav`（git 外，体积红线 `*.wav`）。
- ✅ **HTML 报告** `doc/BaiZe-ISEDA2027/reports/report_robot_hci_interaction_zh.html`（7.8KB，自包含：三项时延 / 打断 / 模拟学生 / 10 条可用性走查）。
- ✅ **`tutor_agent.py` 新增 `clamp_hint()`（≤2 句裁剪）**：交互验收暴露 LLM 原始输出 3-6 句、超 11:40 令 §1.1「每次回复 ≤2 句」；新增确定性裁剪 + 强化 TUTOR_SYSTEM 提示词（≤2 句/每句≤20 字）；`test_tutor_agent.py` 7 单测；smoke 实测 DeepSeek 单步输出「先想想，怎样让 2x 单独留在等号左边？」（0.82s，1 句，无答案）。
- ✅ **host 全量 118 passed**（81 + 12 + 8 + 10 + 7），`pytest` 全绿。
- 🔧 **修 `gen_interaction_report.py` 两处 bug**：CSS `width:100%` 的 `%` 未转义（`ValueError: unsupported format character ';'`）；REPORT_DIR 少跳一级写错目录（`doc/personal-watch/BaiZe...` → 修正为 `doc/BaiZe...`）。`.gitignore` 补 `*.pid`/`*.err`，unstage 误入索引的运行时 `.pid`/`.err`。
- 📌 **能信/不能信**：整轮响应 / TTS 首字（PC SAPI）/ 打断逻辑为**本机实测**；ASR 出字为 mock、当前句音频硬件中断 ≤300ms、AEC 均**待真机**（16:5x 令「能信/不能信」）。

## 第 14 轮增量（2026-11-08 · L1 全量 100 题评测 + 泄露检测误报修复）

- ✅ **重建 100 题题库** `eval/question_bank.py`（数学 60 + 物理 20 + 英语 20，每题知识点 + 最终答案 + 泄露模式）+ `test_question_bank.py`（5 单测）。
- ✅ **修复泄露检测误报** `host/leak_check.py`：旧 `contains_answer` 用子串匹配，对短英文答案误报（`e009`「a 和 **an** 是按什么来选」、`e010` `M**on**day` 子串、`e019`「填 **Would** 还是 Do」）。改为：① 短英文单词「词边界」匹配；② 答案 token 已在题干原文（选项/复述）则不算泄露。`test_leak_check.py` 10 单测。修复前旧 `l1_full.json` 的 4 处「泄露」→ 修复后全 0（确定性证明是误报，非真泄露）。
- ✅ **`host/eval_l1_full.py` 全量评测**（100 文本 + 100 对抗 + 20 识图 = 220 次 deepseek-flash）：**直接给答案率 = 0**（guidance 0.0 / adversarial 0.0）；**识图正确率 1.0（20/20）**、`ocr_fallback_count=0`；**首步 P50 1.16s / P90 2.07s**（≤2.5s/≤4s ✅）；识图 P50 2.37s/P90 3.13s。
- ✅ **host 全量 133 passed**（81 + 12 + 8 + 10 + 7 + 10 + 5）。
- 📌 **能信/不能信**：leak 判定为确定性纯函数（10 单测）；100 题引导/对抗/识图/时延为本机实测（无降级）。🚫 仍非真人/真机；识图只跑 m001-m020（几何/统计题含 △∠√°² 特殊字符，走文本路径，不做 snap 渲染识图）。

## 第 15 轮增量（2026-11-08 · L2 智能体工具层落地）

- ✅ **`host/tools.py`（5 工具）**：`calculator`（AST 白名单安全求值、拒绝变量封堵「代解方程」）、`question_bank_lookup`（检索 100 题题库、剥离 answer/leak 只回题干）、`wrong_book_add/list`（本地 JSON 错题本）、`parent_report`（自包含中文 HTML）、`plot_function`（matplotlib Agg 画函数图）。`tool_spec()`/`call_tool()` 注册表 + 统一 `ToolError`（不做静默降级）。
- ✅ **`host/l2_agent.py`（智能体编排）**：`route_tool()` 确定性意图路由 + `decide_tool_llm()` 让 DeepSeek 选工具（智能体主路径，失败回退路由）+ `L2Session` 多轮会话；**工具轮次与引导历史分离**（`history` 只喂 `tutor_step`，`tool_log` 单记）避免污染引导上下文。
- ✅ **`host/eval_l2.py` 实测**（`eval/l2_tools.json`）：**6 工具全调**；**直接给答案率 = 0**；**多轮 3 轮一致**（`history_len=3`）；`plot_function` PNG 20,347 字节；`llm_tool_decision` DeepSeek 正确选 `calculator`。
- ✅ **host 全量 `pytest` = 175 passed**（133 + test_tools 21 + test_l2_agent 21）。
- 🔧 修 3 处 bug：绘图路由未抽表达式、工具轮次污染引导历史（幻觉「没有等号」）、`\w` 匹配中文多抽「的」。
- 📌 **能信/不能信**：5 工具/路由/红线封堵为确定性纯函数（42 单测）；引导多轮 + LLM 工具决策为本机实测（deepseek-flash）。🚫 工具层未接进 App/HTTP（`/tutor` 暂无工具参数），待下一轮。

## 第 16 轮增量（2026-11-08 · L2 工具/智能体接进 HTTP + App）

- ✅ **`tutor_server.py` 新增两个端点 + 一处路由**（ROADMAP #1「`/tutor` 增加 `tool`/`params`，App 加换一题/记错题/报告入口」）：
  - `POST /tool {tool, params}`：直接调用 5 工具，`ToolError`（红线拒变量/参数非法）→ `{ok:false, error}`（HTTP 200，业务拒绝非服务端错误）；calculator 拒变量、题库/错题本列表剥离 answer/leak。
  - `POST /agent {question, utterance, history?, use_llm?}`：L2 智能体多轮，默认确定性路由（离线），可选 DeepSeek 工具决策；回放 history 重建多轮上下文。
  - `POST /tutor` 带 `tool` 字段即转工具（等价 `/tool`）。
- ✅ **`test_tutor_server.py` 13 单测** + `smoke_http.py`（起临时实例实测 `/health /tool /agent` 真实 JSON）。修复 1 处 bug：`do_POST` 路由字典键漏 `/` 前缀导致 `KeyError: '/tool'`（`path` 保留前导斜杠）。
- ✅ **App 接工具/追问**：`TutorClient.postTool/postAgent`；`MainActivity` 加「换一题/记错题/报告」三按钮（→`/tool`）+ 文字追问输入框 +「发送」（→`/agent`，无题干时回退 `/tutor` 文字题）；`activity_main.xml` + `strings.xml` 同步。
- ✅ **构建 + 装机验证**：`assembleDebug` 成功 → `app-debug.apk` **4,112,860 字节**；`adb install -r` **Success**；`am start` 启动 + `uiautomator dump` 确认「换一题/记错题/报告/发送/追问」UI 元素在位。
- ✅ **host 全量 `pytest` = 188 passed**（175 + 13 新增）。
- 📌 **能信/不能信**：`/tool` `/agent` 的确定性路由 / 红线封堵 / 不泄答案为**确定性纯函数**（13 单测）+ `smoke_http.py` 实测真实 JSON；App 侧为**装机 + UI dump 验证**（未在模拟器内端到端点按钮触发 DeepSeek，因本轮 ComfyUI 停用 + 不引入真实学生数据，工具链路已在 host 侧跑通）。🚫 端侧真实 ASR 仍未落地。

## 下一轮候选（按优先级）

1. 端侧真实 ASR（sherpa-onnx）接入位落地（`SherpaOnnxASR` 现为报错占位）——12:20 令「端侧为主」的最后一环。
2. `clamp_hint` 后的 full 30 会话复跑验证（第 13 轮只做了单次 smoke）。
3. L3 学情：错题本 + 知识点画像 + 每日/每周摘要，本地存储、可导出 HTML（工具已备 wrong_book/parent_report，缺定时聚合与画像）。
4. 收用户 3 条回复 → 复验 `hdc list targets` / `adb devices`，打通真机「拍照/出声」（L0 真机化）。
