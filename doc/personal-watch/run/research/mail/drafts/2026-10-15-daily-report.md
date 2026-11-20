# 【日报草稿】2026-10-15 论文日报邮件（收件人 paul.liu@cxmt.com）

> 类型：**论文日报**（内部日报 · 免审直发）｜ 依据：`WATCH_RESEARCH_TASK.md` 运维指令 2026-10-12（📨 每日论文日报）
> 正文文件：`research/mail/2026-10-15-body.txt` ｜ 发送器：`~/hr_mail.py`（`foamliu@yeah.net` / `smtp.yeah.net:465`）
> 附件：`research/pdf/2026-10-15/{2610.17637,2610.17202,2610.20193,2610.19587,2610.19863}.pdf`（5 个 · 10,623,379 B ≈ 10.13 MB ≤ 20MB）
> 校验结果（逐文件 `%PDF-` + `%%EOF` + `pdfinfo` 页数 + `pdftotext` 正文可解析）：`2610.17637` 26p / `2610.17202` 12p / `2610.20193` 20p / `2610.19587` 17p / `2610.19863` 21p
> ⚠️ 本轮为**补跑**：第九十二轮原唤醒被 `pkill -f 'arxiv.org/pdf'` 自匹配误杀（exit 143）⇒ 已下载 PDF 全部截断（`pdfinfo` 报 `Couldn't find trailer dictionary`、`pdftotext` 输出 0 字节）⇒ 本轮**全部重下 + 严格校验**（`%PDF-` 头 + 尾部 `%%EOF` + 字节下限 + `pdftotext` 可解析 + `pdfinfo` 页数）。

---

**主题**：`[论文日报] 10-15 精选 5 篇（BaiZe/ZhuLong 相关）`

**发送命令**（实发记录）：

```bash
python3 ~/hr_mail.py --to paul.liu@cxmt.com \
  --subject "[论文日报] 10-15 精选 5 篇（BaiZe/ZhuLong 相关）" \
  --body-file research/mail/2026-10-15-body.txt \
  --attach research/pdf/2026-10-15/2610.17637.pdf \
  --attach research/pdf/2026-10-15/2610.17202.pdf \
  --attach research/pdf/2026-10-15/2610.20193.pdf \
  --attach research/pdf/2026-10-15/2610.19587.pdf \
  --attach research/pdf/2026-10-15/2610.19863.pdf
```

**正文**：见 `research/mail/2026-10-15-body.txt`（同内容留档）。

**选文（5 篇 · 3 借鉴 + 2 科普，取自本日 `2026-10-14` 新批）**：

| # | 标签 | 原文标题 | arXiv ID | 为何值得读（一行） |
|:--|:--|:--|:--|:--|
| 1 | 借鉴 | Mixed Precision Scaling Laws for Quantized Pretraining | 2610.17637 | 把「量化伤容量」与「量化伤优化」分开建模的混精度规模律 → 对口 BaiZe 预训练算力/精度预算 |
| 2 | 借鉴 | MLAfication: Efficiently Enabling High-Fidelity MLA for Modern LLMs | 2610.17202 | 免从头重训的 MHA/GQA→MLA 转换（支持 QKNorm + MoE）→ 对口长上下文推理 KV cache 成本 |
| 3 | 借鉴 | SWE-Stream: Scaling Executable Training Data for SWE Agents via Progressive Construction and Elastic Streaming | 2610.20193 | 「开发历史 → 可执行 SWE 任务」的规模化数据管线 → 对口 ZhuLong code agent 数据构造 |
| 4 | 科普 | Moral Combat: Exploiting Moral Foundations Theory to Jailbreak LLMs（**TOP-1**） | 2610.19587 | 「换个说法就能说服 AI」+ 安全基准在道德维度上分布不均 → 大众话题 + 安全评测维度参考 |
| 5 | 科普 | When Extremists Enter LLM Societies: Investigating Extreme Behavior in Multi-Agent Systems | 2610.19863 | AI 社会模拟里掺入少量极端角色是否带偏集体 → 多智能体模拟可信度边界 |

**红线自查**：① 收件人仅 `paul.liu@cxmt.com`（🚫 不加第三方）；② 原题照抄未改写；③ 数字均标「作者自报 · 未复现」；④ 第 4 篇为 AI 安全主题 ⇒ 正文只作研究动态转述、🚫 不提供任何可操作攻击方法；⑤ PDF 不入 git（`.gitignore` 命中 `pdf/` + `*.pdf`）；⑥ 附件合计 ≤ 20MB。
