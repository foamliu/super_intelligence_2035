# host/ · PC 侧家教 agent（R3 路线）

> 手机只做「眼耳口」（拍照 / 录音 / 播放），**推理跑在 PC 或云**。
> 本目录是 PC 侧核心。真机接上后，手机端只替换 `proto/mock_device.py`，
> `tutor_agent.py` 的接口不变。

## 组成

| 文件 | 作用 |
|:--|:--|
| `tutor_agent.py` | 最小闭环：题图/题文 → 识图（默认 DeepSeek 视觉）→ 分步引导（默认 DeepSeek，不泄答案，`clamp_hint()` 确定性裁剪 ≤2 句）→ Windows SAPI 出声 |
| `tutor_server.py` | HTTP 服务（App 经 `10.0.2.2:8765` 调它）：`POST /tutor`（识图+引导，带 `tool` 字段即转工具）+ `POST /tool`（L2 工具）+ `POST /agent`（智能体多轮）+ `POST /profile`（L3 学情合并画像）+ `POST /practice`（L3 补正样本，记录作答对错）+ `GET /health` |
| `speech.py` | 语音链路适配层（12:20 令 §2/§3）：统一接口 `asr_stream()/tts_stream()/stop()`；端侧默认（SAPI 分句流式 + 打断 + `MockStreamingASR`），**端侧真实 ASR = `SherpaOnnxASR`（sherpa-onnx paraformer 中文离线模型）**，云端留空实现（默认 off） |
| `normalize_math.py` | 口述→数学式纠错（12:20 令 §4）：覆盖平方/立方/根号/分之/负/运算符/关系/π/度/角/几何符号/术语等，`cn_to_int` 中文数字转换 |
| `eval_l1.py` | L1 评测基线：文本 3 题 + 对抗探针 + **4 张题图**（算式/中文+算式/中文应用题/代数式）→ `eval/l1_baseline.json`（直接给答案率 / 识图正确率 / 首步时延 P50·P90 / 逐条后端与降级原因） |
| `probe_ds_vision.py` | DeepSeek 视觉一次性探针（读 key 不打印 key，产出 `ds_vision_probe.json`） |
| `eval_asr.py` | **端侧 ASR 实测（第 18 轮）**：SAPI TTS 合成已知文本 → `SherpaOnnxASR` 识别 → CER（字错率）→ `eval/asr_paraformer_zh.json` |
| `vad.py` | **端侧 VAD 纯函数（第 20 轮）**：`rms`/`rms_db` 能量、`EndpointDetector`（静音 ≥1.2s 端点）、`BargeInDetector`（打断 debounce + hangover）、`MuteGate`（静音真关麦）、`SessionController`（INTERACTION_SPEC §3 状态机） |
| `test_vad.py` | `vad.py` 单测（16 条：能量/端点 1.2s/打断 debounce/hangover/静音真关麦/状态机 happy path + barge_in + muted） |
| `test_normalize_math.py` | `normalize_math.py` 单测（**81 条**，12:20 令要求 ≥30） |
| `test_speech.py` | `speech.py` 单测（分句/打断/流式/落盘 WAV/云端 off/端侧模型缺失报错/WAV 读取与重采样/端侧真实识别〔模型在场时〕） |
| `presence.py` | 在座检测（12:05 令 §1/§5）：单帧 320×240 + YuNet 人脸（`cv2.FaceDetectorYN`，OpenCV 5）+ 亮度阈值，三分类 person/left/unknown；帧不落盘不上传；`measure()` 连拍测帧率/耗时 |
| `test_presence.py` | `presence.py` 单测（8 条：三分类 / 300ms 预算字段 / 模型缺失报错 / 自动找模型） |
| `eval_presence.py` | presence 评测：PC 摄像头连拍 20 次（帧率/耗时/300ms 达标率）+ 20 张标注样本三分类准确率 → `eval/presence_pc_camera.json` |
| `eval_interaction.py` | 11:40 令 §3 交互验收：三模式 latency / bargein / student（模拟学生 3 人设×10 轮）→ `eval/interaction_*.json` |
| `gen_interaction_report.py` | 读 `eval/interaction_*.json` 生成自包含中文 HTML → `doc/BaiZe-ISEDA2027/reports/report_robot_hci_interaction_zh.html` |
| `test_interaction.py` | `eval_interaction.py` 纯函数单测（10 条：归一化/分位数/红线判定/汇总/会话评分） |
| `test_tutor_agent.py` | `clamp_hint()` 单测（7 条：≤2 句裁剪 / 删句不硬截 / 空值 / 换行分句） |
| `tools.py` | **L2 工具集（第 15 轮）**：5 工具——计算器（AST 白名单安全求值、拒变量）/ 题库（剥离答案）/ 错题本 / 家长报告 / 函数绘图；`tool_spec()`/`call_tool()` 注册表 |
| `l2_agent.py` | **L2 智能体编排（第 15 轮）**：`route_tool()` 确定性路由 + `decide_tool_llm()`（DeepSeek 选工具）+ `L2Session` 多轮会话（工具轮与引导历史分离） |
| `eval_l2.py` | L2 评测：5 工具真调 + 多轮一致性 + 直接给答案率 → `eval/l2_tools.json` |
| `test_tools.py` | `tools.py` 单测（21 条：安全求值 / 红线拒变量 / 5 工具 / 注册表） |
| `test_l2_agent.py` | `l2_agent.py` 单测（21 条：路由 / 表达式抽取 / LLM 决策解析 / 会话多轮与红线） |
| `test_tutor_server.py` | `tutor_server.py` 单测（**20 条**：/tool 红线拒变量、题库不泄答案、错题本/报告、/agent 多轮回放、/tutor 工具路由、/profile 学情、/practice 正样本） |
| `smoke_http.py` | HTTP 冒烟：起临时实例实测 `/health /tool /agent /profile` 四端点真实 JSON（不依赖 App/模拟器） |
| `l3_profile.py` | **L3 学情层（第 17/19 轮）**：错题本（负样本）+ 练习日志（正样本，作答次数/正确率）→ `merged_profile()` 合并画像 + 每日/每周摘要 + 自包含 HTML（`build_profile_html_full`）；`mastery_from_stats()` 富化掌握等级（含「已掌握」）；本地、不上传、不泄答案 |
| `test_l3_profile.py` | `l3_profile.py` 单测（**22 条**：掌握等级/时间归一/画像聚合/薄弱点/每日每周/HTML 自包含与不泄答案 + 正样本：练习摘要/合并画像/富化掌握/日志追加/合并 HTML） |

## 单测（第 20 轮：238 passed）

```powershell
cd D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\robot\host
py -3.10 -m pytest -q                                                  # 222 passed
py -3.10 normalize_math.py "x的平方加三x等于零" "二分之根号三"        # 演示口述→数学式
py -3.10 -W ignore speech.py                                          # 演示分句/合成 WAV/打断/ASR mock
py -3.10 -W ignore smoke_http.py                                      # HTTP 冒烟（/health /tool /agent /profile）
```

## 交互验收（11:40 令 §3 · 第 13 轮交付）

```powershell
cd D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\robot\host
py -3.10 -W ignore eval_interaction.py --mode all          # latency + bargein + student（3 人设×10 轮）
py -3.10 -W ignore gen_interaction_report.py               # 生成 doc/BaiZe-ISEDA2027/reports/report_robot_hci_interaction_zh.html
```

- 实测：整轮响应 P50 1.37s / P90 1.97s（n=12）；TTS 首字 P50 80.4ms（n=10）；打断 stop 信号 ~0ms（n=8）；模拟学生 3 人设×10 轮**直接给答案次数 = 0**；会话录音 91.2s。

## 在座检测（presence · 12:05 令 §1/§5）

```powershell
cd D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\robot\host
py -3.10 -W ignore presence.py --measure            # 单帧 + 连拍 20 次（帧率/耗时）
py -3.10 eval_presence.py                           # 连拍 20 次 + 20 标注样本准确率 -> ../eval/presence_pc_camera.json
```

- **三分类**：`person`（YuNet 检出人脸）/ `left`（无人）/ `unknown`（太暗/无帧/坏帧）。
- **实测（PC 摄像头，Logitech 046D，20 次）**：帧率 **29.71 fps**；单次抓帧+检测 **P50 33.0ms / P90 57.4ms / max 66.4ms**，**20/20 达标 ≤300ms**（12:05 令 §1 硬指标）。
- **准确率（20 标注样本）**：**20/20 = 1.0**（person 8 + left 8 + unknown 4 全对）。
- ⚠️ 样本为「无歧义」集（清晰人脸 / 明显无人风景静物 / 合成暗帧）；遮挡/逆光/侧脸/远景小脸等**难例待真人/真机复测**（16:5x 令「能信/不能信」）。
- **模型**：`models/face_detection_yunet_2023mar.onnx`（OpenCV Zoo YuNet，Apache-2.0，232KB）。OpenCV 5.0 已移除 CascadeClassifier/HOGDescriptor，故用 YuNet；缺模型时报明确 RuntimeError，不静默。
  - ⚠️ 模型权重 `*.onnx` 按 `run/.gitignore` 体积红线**不入库**，新环境需拉取：
    `curl.exe -sL -o models/face_detection_yunet_2023mar.onnx https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx`
- **约束**：帧端侧处理、立即丢弃不落盘不上传；`speak` 态绝不抓帧、检测频率 ≤1 次/90s 由**调用方**调度（本模块只提供 `grab()`，不内部循环）。

## 推理后端（11:30 / 15:4x 用户令定稿）

| 环节 | 默认（主路径） | 兜底（断网/无 key） | 开关 |
|:--|:--|:--|:--|
| 识图 | 云端 **`deepseek-flash`** 视觉（实测中文题干 4/4） | 本机 `llava:latest`（只稳算式，中文长题干弱） | `ROBOT_VISION_BACKEND=deepseek\|ollama` |
| 分步引导 | 云端 **`deepseek-flash`**（P50 2.0s） | 本机 `qwen3:8b`（P50 5.7s） | `ROBOT_TUTOR_BACKEND=deepseek\|ollama` |
| TTS | Windows SAPI（Huihui 中文女声，离线免费） | 无音频设备时**降级纯文字** | `--speak out.wav` 落盘 |

- **降级绝不静默**：`LAST_VISION_TRACE` / `LAST_TUTOR_TRACE` 记录 `{backend, model, fallback, latency_s}`，CLI 会打印 `⚠️ 降级：<原因>`，`eval_l1.py` 逐条写进 JSON。
- **key 来源**：环境变量 `DEEPSEEK_API_KEY` 优先，其次 `~/.cline/data/secrets.json` 的 `deepSeekApiKey`。🚫 不写进仓库/日志/报告/截图。
- ⚠️ `qwen3-vl:32b`（20GB，本机 404）**已作废**，不再等它；`llava` 只做离线兜底。

## 隐私口径（题图上云 = 学生题目外发）

- 默认路径会把**题图**（可能含学生字迹）base64 上传到 `api.deepseek.com`；服务端不留存原图，本机不落盘中间图。
- **纯本地模式**（零外发）：`ROBOT_VISION_BACKEND=ollama` + `ROBOT_TUTOR_BACKEND=ollama`（可用 `--vision-backend ollama --tutor-backend ollama` 单次指定）。
- 待补（下一轮）：UI 上「当前模式：云端 / 纯本地」可见标识 + 一键切换。

## 跑一次（端到端）

```powershell
cd D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\robot\host
py -3.10 ../proto/mock_device.py --snap "已知等腰三角形顶角为 40°，求底角的度数。" --out ..\eval\q2_geometry.png
py -3.10 -W ignore tutor_agent.py --image ..\eval\q2_geometry.png --speak demo_round5.wav --answer "70"
```

预期输出：
1. `[识别] …s backend=deepseek(deepseek-flash)` + 题干原文（逐字读出中文应用题）
2. `[引导] …s backend=deepseek(deepseek-flash)` + 一段**不含最终答案**的第一步引导
3. `[总时延] …s（识别 + 首步引导，不含 TTS）`
4. 生成 `demo_round5.wav`（48kHz 立体声，可证伪的「出声」产物）

## 多轮追问（模拟学生-家教对话）

```powershell
py -3.10 -W ignore tutor_agent.py --interactive
```

## 跑评测（L1 基线，可重复）

```powershell
cd D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\robot\host
py -3.10 -W ignore eval_l1.py                                         # 云端主路径
py -3.10 -W ignore eval_l1.py --vision-backend ollama --tutor-backend ollama `
    --out ..\eval\l1_baseline_local.json                              # 纯本地对照
```

产出 JSON 里含四组真实数字：
1. **直接给答案率**（引导 + 对抗性「直接要答案」探针，必须 0）；
2. **识图正确率**（4 张题图，算式用数学骨架、中文题干用字符相似度 ≥0.9）；
3. **首步时延 P50 / P90**（11:40 令硬指标 P50≤2.5s / P90≤4s）；
4. **每条 OCR 的真实后端 + 降级原因**（`ocr_fallback_count`）。

## L2 智能体（工具调用 · 第 15 轮）

```powershell
cd D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\robot\host
py -3.10 tools.py                          # 工具自检：calculator/question_bank/拒变量
py -3.10 -W ignore l2_agent.py             # 会话编排离线演示（6 条学生话 → 工具/引导）
py -3.10 -W ignore eval_l2.py              # L2 评测 → ../eval/l2_tools.json
```

- **5 工具**：`calculator`（AST 白名单、拒变量→不代解方程）/ `question_bank_lookup`（只回题干不泄答案）/ `wrong_book_add|list`（本地错题本）/ `parent_report`（本地 HTML）/ `plot_function`（函数图像 PNG）。
- **智能体骨架**：`route_tool()` 确定性路由（离线）+ `decide_tool_llm()`（DeepSeek 选工具，失败回退路由）+ `L2Session`（一道题多轮会话，工具轮与引导历史分离）。
- **实测（第 15 轮）**：6 工具全调；直接给答案率 0；3 轮追问一致；`plot_function` PNG 20,347 字节；LLM 决策正确选 `calculator`。
- ✅ **已接 HTTP（第 16 轮）**：`tutor_server.py` 新增 `POST /tool`（直接调工具，红线拒变量/不泄答案）、`POST /agent`（L2 多轮，确定性路由默认）、`POST /tutor` 带 `tool` 字段即转工具；App 加「换一题/记错题/报告」按钮 + 文字追问 → 均已跑通（`smoke_http.py` 实测 + `adb install` 成功 + 模拟器 UI dump 确认新按钮）。

## L3 学情（错题本 + 练习正样本合并画像 · 第 17/19 轮）

```powershell
cd D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\robot\host
py -3.10 l3_profile.py                     # 自检：画像/每日/每周/合并画像/HTML 全链路
py -3.10 -W ignore smoke_http.py           # 冒烟里含 POST /profile 实测 JSON
```

- **数据来源（正负样本）**：错题本 `logs/wrong_book.json`（负样本，L2 `wrong_book_add` 同源）+ 练习日志 `logs/practice_log.json`（正样本，作答次数/正确率，本地不上传）。
- **能力**：`knowledge_profile()`（错题口径画像）、`practice_summary()`（正样本摘要）、`merged_profile()`（**错题 + 作答合并画像**：`wrong_count/attempt_count/correct_count/correct_rate/mastery`）、`mastery_from_stats()`（富化掌握等级，新增「已掌握」）、`build_profile_html()`/`build_profile_html_full()`（自包含中文 HTML，不泄答案、不含学生隐私）、`profile_report()`/`profile_report_full()`（落盘 + 摘要 JSON）。
- **HTTP**：`POST /profile {html?: bool}` → `{ok, profile}`（合并画像 + `total_practice` + 正样本 `knowledge_points`）；`html=true` 另生成 `logs/profile_report.html`。`POST /practice {question, correct, knowledge?, student_answer?}` → 记录一次作答对错，返回累计 `total_practice` 与合并画像摘要（第 19 轮）。
- **App**：新增「学情」按钮 → 显示「错题总数/练习次数/涉及知识点/薄弱点/作答摘要」；新增「答对/答错」按钮 → `TutorClient.postPractice()` 记录作答（第 19 轮，`adb install` + 模拟器点击实测，见 `logs/r19_session.mp4`）。
- **红线**：报告只统计自造题，不出现学生姓名/学校/照片，不泄露原题答案（`test_l3_profile.py`/`test_tutor_server.py` 断言「HTML 不含答案 / 画像不含学生作答原文」）。

## 端侧真实 ASR（sherpa-onnx paraformer 中文 · 第 18 轮）

> 落地 12:20 令「端侧为主」最后一环：`SherpaOnnxASR` 从「报错占位」升级为**真实离线识别**。

```powershell
cd D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\robot\host
py -3.10 -W ignore eval_asr.py            # TTS 合成已知文本 -> ASR 识别 -> CER -> ../eval/asr_paraformer_zh.json
```

**模型下载（一次性，走 hf-mirror，直连 GitHub 超时）**：

```powershell
$base='https://hf-mirror.com/csukuangfj/sherpa-onnx-paraformer-zh-2023-09-14/resolve/main'
New-Item -ItemType Directory -Force C:\Android\asr-models\paraformer-zh | Out-Null
Invoke-WebRequest "$base/model.int8.onnx" -OutFile C:\Android\asr-models\paraformer-zh\model.int8.onnx   # 243,371,218 字节
Invoke-WebRequest "$base/tokens.txt"      -OutFile C:\Android\asr-models\paraformer-zh\tokens.txt
```

- **口径**：`SherpaOnnxASR.transcribe_file()` 一次性识别；`stream()` 按块「前缀增量」模拟流式中间结果（paraformer 为**离线**模型，非 OnlineRecognizer 真流式，真流式待接 streaming 模型）。
- **能信/不能信**：CER 是「SAPI 合成语音 → 离线识别」的回读字错率，属 PC 端真实推理证据；真机麦克风近场 CER / 流式首字延迟 / AEC 待真机复测。

## 教育红线（内置约束，见 `tutor_agent.py` 的 TUTOR_SYSTEM）

1. 不直接给最终答案、不代写作业，只分步引导、每次推进一步。
2. `--answer` 给出已知答案时，`redline_leak_check()` 会自检引导文本是否泄露答案。
3. 评测只用自造题，不采集真实学生作业。
