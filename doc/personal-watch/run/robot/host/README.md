# host/ · PC 侧家教 agent（R3 路线）

> 手机只做「眼耳口」（拍照 / 录音 / 播放），**推理跑在 PC 或云**。
> 本目录是 PC 侧核心。真机接上后，手机端只替换 `proto/mock_device.py`，
> `tutor_agent.py` 的接口不变。

## 组成

| 文件 | 作用 |
|:--|:--|
| `tutor_agent.py` | 最小闭环：题图/题文 → 识图（默认 DeepSeek 视觉）→ 分步引导（默认 DeepSeek，不泄答案）→ Windows SAPI 出声 |
| `eval_l1.py` | L1 评测基线：文本 3 题 + 对抗探针 + **4 张题图**（算式/中文+算式/中文应用题/代数式）→ `eval/l1_baseline.json`（直接给答案率 / 识图正确率 / 首步时延 P50·P90 / 逐条后端与降级原因） |
| `probe_ds_vision.py` | DeepSeek 视觉一次性探针（读 key 不打印 key，产出 `ds_vision_probe.json`） |

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

## 教育红线（内置约束，见 `tutor_agent.py` 的 TUTOR_SYSTEM）

1. 不直接给最终答案、不代写作业，只分步引导、每次推进一步。
2. `--answer` 给出已知答案时，`redline_leak_check()` 会自检引导文本是否泄露答案。
3. 评测只用自造题，不采集真实学生作业。
