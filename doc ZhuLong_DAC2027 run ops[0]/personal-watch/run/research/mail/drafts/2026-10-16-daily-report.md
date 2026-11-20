# 【日报草稿】2026-10-16 论文日报邮件（收件人 paul.liu@cxmt.com）

> 类型：**论文日报**（内部日报 · 免审直发）｜ 依据：`WATCH_RESEARCH_TASK.md` 运维指令 2026-10-12（📨 每日论文日报）
> 正文文件：`research/mail/2026-10-16-body.txt` ｜ 发送器：`~/hr_mail.py`（`foamliu@yeah.net` / `smtp.yeah.net:465`）
> 附件：`research/pdf/2026-10-16/{2610.19605,2610.19210,2610.18616,2610.22319,2610.22333}.pdf`（5 个 · 9,828,547 B ≈ 9.37 MB ≤ 20MB）
> 校验结果（逐文件 `%PDF-` 头 + `pdfinfo` 页数 + `pdftotext` 正文可解析）：2610.19605 23页/1,307,212 B · 2610.19210 15页/1,181,834 B · 2610.18616 27页/775,549 B · 2610.22319 17页/6,215,260 B · 2610.22333 19页/348,692 B（均 %PDF- + %%EOF + pdfinfo + pdftotext 通过，且字节数 = 服务端 content-length）

---

**主题**：`[论文日报] 10-16 精选 5 篇（BaiZe/ZhuLong 相关）`

**发送命令**（实发记录）：

```bash
python3 ~/hr_mail.py --to paul.liu@cxmt.com \
  --subject "[论文日报] 10-16 精选 5 篇（BaiZe/ZhuLong 相关）" \
  --body-file research/mail/2026-10-16-body.txt \
  --attach research/pdf/2026-10-16/2610.19605.pdf \
  --attach research/pdf/2026-10-16/2610.19210.pdf \
  --attach research/pdf/2026-10-16/2610.18616.pdf \
  --attach research/pdf/2026-10-16/2610.22319.pdf \
  --attach research/pdf/2026-10-16/2610.22333.pdf
```

**正文**：见 `research/mail/2026-10-16-body.txt`（同内容留档）。

**选文（5 篇 · 3 借鉴 + 2 科普；早 3 = 06:00 轮「借鉴」，晚 2 = 18:00 轮「科普」，取自本日 `2026-10-15` 新批）**：

| # | 标签 | 原文标题 | arXiv ID | 为何值得读（一行） |
|:--|:--|:--|:--|:--|
| 1 | 借鉴 | PN-Mix: Pair-Norm Guided Mixed-Precision Key Cache Quantization for Efficient Long-Output LLM Inference | 2610.19605 | 在 RoPE 通道对层面找「量化误差对 logit 贡献大」的通道对、prefill 定一次全程复用 → 对口 BaiZe 高效推理 / KV cache 量化 |
| 2 | 借鉴 | Titan-Llama: Retrofitting Pre-trained LLMs with External Neural Memory Modules | 2610.19210 | 后训练即可把历史压进固定大小神经记忆模块、替换注意力层（免从头训练）→ 对口长上下文 / 记忆架构 |
| 3 | 借鉴 | Knowledge Graphs as Files: An Agent Harness Where Tool Creation and Tool Use Co-Evolve | 2610.18616 | agent 直接在节点/边文件上写 Python 造工具、工具创建与使用共演化 → 对口 ZhuLong agent harness 工具供给方式与评测设计 |
| 4 | 科普 | A team of Gemini 4 Argon agents beats Minecraft（**TOP-1**） | 2610.22319 | 4 个 AI 自己商量分工、自己写程序，27 小时 14 分 / 2783 个程序通关 Minecraft → 长时程自主任务的直观参照 |
| 5 | 科普 | Evaluation Awareness Beyond English: Do LLMs Act Differently When Tested in Indic Languages? | 2610.22333 | 「AI 知道自己被考试就更爱拒答」，且评测语言偏英 → 安全评测的可信度边界 |

**红线自查**：① 收件人仅 `paul.liu@cxmt.com`（🚫 不加第三方）；② 原题照抄未改写；③ 数字均标「作者自报 · 未复现」，第 4 篇的「首次」照原文限定为「据作者所知（To our knowledge）」；④ 🚫 不夸大（不写「AI 已超越人类玩家 / SOTA / 颠覆」）；⑤ PDF 不入 git（`.gitignore` 命中 `pdf/` + `*.pdf`）；⑥ 附件合计 ≤ 20MB。
