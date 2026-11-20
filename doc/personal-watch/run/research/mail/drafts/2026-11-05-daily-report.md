# 日报邮件草稿 · 2026-11-05（第 24 封）

- 类型：论文日报（内部 · 免审直发，见运维指令 2026-10-12）
- 收件人：`paul.liu@cxmt.com`（固定，不加第三方）
- 主题：`[论文日报] 11-05 精选 5 篇（BaiZe/ZhuLong 相关）· 当日 5/5 收口`
- 附件：5 个 PDF（`research/pdf/2026-11-05/`，不入 git），合计 14,711,758 B ≈ 14.03 MiB（< 20 MB，未分包）
- 正文：`research/mail/2026-11-05-body.txt`

## 选文（当日 5/5）

| # | arXiv ID | 原题 | 口径 | 一行价值 | PDF |
|:--|:--|:--|:--|:--|:--|
| 1 | 2611.05234 | ARLoop: Fully-Open Pre-trained Looped Transformers with Attention Residuals | 借鉴 | attention residuals 用到循环深度；1.2B / 0.5T token / R=3 在 8 个评测全部超过 Huginn-3.5B | ✅ 1,542,092 B / 26 页 |
| 2 | 2611.05304 | LoopVQ: Sub 1-bit KV Cache Quantization for Looped Transformers | 借鉴 | 亚 1 bit KV 量化；SGLang 32K decode 延迟近乎减半、吞吐 4.3×/6.1× | ✅ 645,661 B / 17 页 |
| 3 | 2611.05266 | Stabilizing On-Policy Targeted Guidance in Agentic Reinforcement Learning | 借鉴 | 只在失败轮自蒸馏 + 逐准则 RL；7 准则 0.55–0.99 且 pass-rate 持平 | ✅ 1,636,164 B / 14 页 |
| 4 | 2611.06840 | Same Layout, Different Count: What Number Words Do Past Ten in Text-to-Image Models | 科普（TOP-1） | 文生图十以上不听数字；画进 latent 59% vs 提示词 4% | ✅ 10,170,708 B / 43 页 |
| 5 | 2611.06704 | Where It Breaks: Diagnosing Perception, Memory, and Decision Failures of a Vision-Language Agent in Pac-Man | 科普 | 吃豆人 agent 0/96→77/96，但峰值在 335 步、425 步回落到 60/96 | ✅ 717,133 B / 35 页 |

## 发送记录（发送后回填）

- 实际发送时间：**2026-11-05 18:14:51**
- 附件：5 个 PDF，合计 **14,711,758 B ≈ 14.03 MiB**（`ATTACH` 逐项：1.47 / 0.62 / 1.56 / 9.70 / 0.68 MB）
- 状态：**✅ SENT OK**（`/tmp/mail_send_r134.log`；台账 `research/mail/发送记录.md` 同日行）
- 事故如实登记：首次调用因 `--attach` 只接受单值而报 `unrecognized arguments`（**未投递**、无副作用），改为重复 `--attach` 后一次成功。
