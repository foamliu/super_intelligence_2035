# 每日论文日报 · 2026-10-27（草稿存档 · 发出前入仓）

> 台账要求（`WATCH_RESEARCH_TASK.md` 运维块 ④）：发送前草稿先入仓 `research/mail/drafts/<date>-daily-report.md`；发送后当轮台账 + 心跳照写（**没写 = 没发**）。
> 本文件 = 当日实际发送内容的结构化摘要（正文全文见 `research/mail/2026-10-27-body.txt`）。

- 收件人：`paul.liu@cxmt.com`（固定，未加第三方）
- 主题：`[论文日报] 10-27 精选 5 篇（BaiZe/ZhuLong 相关）· 当日 5/5 收口（批次已刷新 2026-10-26）`
- 附件：5 个 PDF，合计 **8,003,455 B ≈ 7.63 MB ≤ 20 MB**（未分包）
- 发送：`python3 ~/hr_mail.py ...`（复用 recruit 通道 `foamliu@yeah.net`），日志 `/tmp/mail_send_r116.log`，**`SENT OK (2026-10-27 18:16:48)`**

## 一、今日 5 篇（早 3「借鉴」/ 晚 2「科普」）

| # | arXiv ID | 标签 | 一行价值 |
|:--|:--|:--|:--|
| 1 | `2610.32951` | 借鉴 | vLLM 采样 vs HF 重算 logprob 的「舍入位置失配」让 BF16 RL 训练崩塌；只把 RoPE / SwiGLU / 残差 RMSNorm 的中间量留 FP32 即稳，**只对齐 RoPE 也够**（静态 per-token KL 仅降 9.1–25.5%） |
| 2 | `2610.32881` | 借鉴 | 用同 prompt 的历史 rollout 当 n-gram 草稿（表放 CPU、不占显存）+ fan-out 预取；**3.60–7.77 token/step**、rollout 吞吐 **1.38×**、decode 26.1→19.2 ms |
| 3 | `2610.32483` | 借鉴 | 把 agent 失败拆成「模型 vs harness」：VCR + Model–Harness Fit + Cross-Model Fit + Interaction Residuals + Token Load；**111 设置 / 52,168 轨迹** |
| 4 | `2610.35857` | 科普（**TOP-1**） | 46 个视觉编码器 × 10 概念族：概念「2→3」形式内 **99.1%** 显著、跨形式仅 **52.2%** ⇒ **碎片化线性**（每种「三」各学一遍）；碎片化 0.67（监督 ViT）vs 0（CLIP） |
| 5 | `2610.34688` | 科普 | 3 秒 Moshi 表征泄漏 → 用受害者声音说任意文本：CAM++ **0.78** / WER **3.80%**（基线 SpInv+TTS 0.22 / 13.37%） |

## 二、取数证据（可复核）

- 探针 `raw/2026-10-27-pm-probe-r116.json`：arXiv 200 + `application/atom+xml`；`cat:cs.CL` `totalResults` **123669 → 123901**、最新 `published=2026-10-26T17:59:33Z`；广度 **637936 → 639007**；HF ❌ `Errno 101`；RSS 374 / 483 / 321（仅作发现）。
- 增量 `raw/2026-10-27-pm-fetch-r116-seen.json`：`window_mode=daily`（72h），15/15 `ok/200/attempts=1`，**kept 206 / dropped 366**（10-26 = 131 / 10-25 = 57 / 10-24 = 18）。
- 复核 `raw/2026-10-27-pm-idlist-r116a.{xml,headers}`：3 条请求 → 3 条完整返回（`STATUS=200`、`BYTES=9131`、`2.08s`）。
- PDF：5/5 校验通过（17 / 7 / 43 / 15 / 14 页）；`2610.34688` 首轮 urllib 读取超时 → 丢弃后 curl 重下并重新校验。
- 台账：`SEEN.md` 4,975 行（收录 261 / 候选 4,207 / RSS 补充 507）；`papers.jsonl` 261。

## 三、口径与红线自检

- 只发 `paul.liu@cxmt.com`（未加第三方）；凭据仓外（`~/.hr_smtp`，未入 git）；PDF 不入 git（`research/pdf/` 已被 `.gitignore` 排除）。
- 原题照抄、不改写；数字均标「作者自报 · 本线未复现」；「科普」与「借鉴」两口径不混用。
- 早 3 篇首次提交为 2026-10-23（UTC，非今日新提交），已在正文与日报页三处明示；晚 2 篇为当日新批（2026-10-26 UTC）。

## 四、配套产出

- 日报：`research/daily/2026-10-27.html`（5/5 收口）
- 分镜：`research/video/SCENES/10_27.html`（TOP-1 = `2610.35857`，5 镜 / 120s / 口播 446 字）
- 口径记录：`research/ARXIV_API.md §9.116`
- 台账：`research/mail/发送记录.md`（第 15 封）
