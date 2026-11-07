# host/ · PC 侧家教 agent（R3 路线）

> 手机只做「眼耳口」（拍照 / 录音 / 播放），**推理与智能体跑在 PC**。
> 本目录是 PC 侧核心。真机接上后，手机端只替换 `proto/mock_device.py`，
> `tutor_agent.py` 的接口不变。

## 组成

| 文件 | 作用 |
|:--|:--|
| `tutor_agent.py` | 最小闭环：题图/题文 → `llava` OCR 识别 → `qwen3:8b` 分步引导（不泄答案）→ Windows SAPI 出声 |

## 依赖（本机已具备，零采购 / 零外部账号）

- `ollama`：`llava:latest`（视觉+OCR，实测可用）、`qwen3:8b`（分步引导）
- `win32com`（pywin32）：Windows SAPI TTS（中文女声 Huihui）
- `requests` / `PIL` / `cv2`

## 跑一次（端到端）

```powershell
cd D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\robot\host
py -3.10 ../proto/mock_device.py --snap "解方程：2x + 3 = 11" --out ..\eval\q1_equation.png
py -3.10 -W ignore tutor_agent.py --image ..\eval\q1_equation.png --speak demo_step1.wav --answer "4"
```

预期输出：
1. `[识别]` 打出题干原文（视觉模型读图）
2. 打出一段**不含最终答案**的第一步引导
3. 生成 `demo_step1.wav`（可证伪的「出声」产物）

## 多轮追问（模拟学生-家教对话）

```powershell
py -3.10 -W ignore tutor_agent.py --interactive
```

## 教育红线（内置约束，见 `tutor_agent.py` 的 TUTOR_SYSTEM）

1. 不直接给最终答案、不代写作业，只分步引导、每次推进一步。
2. `--answer` 给出已知答案时，`redline_leak_check()` 会自检引导文本是否泄露答案。

## 备注

- 首选 OCR 模型 `qwen3-vl:32b` 当前 `/api/chat` 报 404「not found」（manifest 与 blob 脱节），
  临时用 `llava:latest`；修复后改 `tutor_agent.py` 顶部 `VISION_MODEL` 即可。
- ⚠️ OCR 可靠性（第 2 轮复验）：`llava` 读**纯算式**（`2x + 3 = 11`）正确，
  读**中文+算式混合**（`解方程：2x + 3 = 11`，真实题干形态）易误读；
  分步引导与 TTS 两步稳定。→ 要过 L1「≥15/20 识别正确」必须先修 `qwen3-vl:32b`。
