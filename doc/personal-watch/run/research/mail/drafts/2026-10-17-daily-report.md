# 【日报草稿】2026-10-17 论文日报邮件（收件人 paul.liu@cxmt.com）

> 类型：**论文日报**（内部日报 · 免审直发）｜ 依据：`WATCH_RESEARCH_TASK.md` 运维指令 2026-10-12（📨 每日论文日报）
> 正文文件：`research/mail/2026-10-17-body.txt` ｜ 发送器：`~/hr_mail.py`（`foamliu@yeah.net` / `smtp.yeah.net:465`）
> 附件：`research/pdf/2026-10-17/{2610.21126,2610.20673,2610.22344,2610.22372}.pdf`（**4 个 · 17,007,768 B ≈ 16.22 MB** ≤ 20MB）
> **第 5 篇 Gen4P（2610.22371）不附**：服务端 `content-length` = **38,108,462 B ≈ 36.3 MB > 单封 20 MB 上限** ⇒ 正文仅给 `https://arxiv.org/abs/2610.22371`（口径同 10-13 轮 17.2MB 超限件；本机 ≈13 KB/s，下完需 ≈50 min，已主动终止）
> 校验结果（逐文件 `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 正文可解析 + 本地字节 = 服务端 content-length）：2610.21126 16 页 / 724,384 B · 2610.20673 20 页 / 1,205,152 B · 2610.22344 23 页 / 1,114,838 B · 2610.22372 {{PAGES_22372}} 页 / 13,963,394 B（均通过）；2610.22371 未下载（超限，见上）

---

**主题**：`[论文日报] 10-17 精选 5 篇（BaiZe/ZhuLong 相关）`

**发送命令**（实发记录）：

```bash
python3 ~/hr_mail.py --to paul.liu@cxmt.com \
  --subject "[论文日报] 10-17 精选 5 篇（BaiZe/ZhuLong 相关）" \
  --body-file research/mail/2026-10-17-body.txt \
  --attach research/pdf/2026-10-17/2610.21126.pdf \
  --attach research/pdf/2026-10-17/2610.20673.pdf \
  --attach research/pdf/2026-10-17/2610.22344.pdf \
  --attach research/pdf/2026-10-17/2610.22372.pdf
```

**正文**：见 `research/mail/2026-10-17-body.txt`（同内容留档）。

**选文（5 篇 · 3 借鉴 + 2 科普；早 3 = 06:00 轮「借鉴」，晚 2 = 18:00 轮「科普」；⚠️ 周六 arXiv 不公告，5 篇均取自第九十四轮 PM 已入账的窗口内候选池）**：

| # | 标签 | 原文标题 | arXiv ID | 为何值得读（一行） |
|:--|:--|:--|:--|:--|
| 1 | 借鉴 | Compression Does Not End at Selection: Post-Selection Positional Geometry for Sparse KV Caches | 2610.21126 | 稀疏 KV「选完之后」位置坐标仍是全长 → RoPERelay 用紧凑保序 RoPE 坐标迁移已缓存 key 相位（不重选/不重预填）→ 互补 PN-Mix，对口 BaiZe 长上下文高效推理 |
| 2 | 借鉴 | HPCAgent-Bench: A Framework for Sound Benchmarking of Code-Optimizing Agents, Harnesses, and Skills | 2610.20673 | 689 kernel / 3 赛道 / 隐藏 fuzz 裁判 + 加权 token 成本 → 可度量「harness/技能/工具各自的贡献」，对口 ZhuLong 评测方法学 |
| 3 | 借鉴 | MLExpert: Towards a Generalist Agentic Model for Autonomous Machine Learning Engineering | 2610.22344 | 35B MoE agentic 模型 + 分层 SFT + 窗口化交互 RL（WIRL）+ Kaggle-MLE Factory → 长时程执行反馈训练的 credit assignment 设计，桥接 BaiZe 与 ZhuLong |
| 4 | 科普 | Gen4P: Video Generators are 4D Perceivers（**TOP-1** · 不附 PDF，超 20MB） | 2610.22371 | 视频生成器改成前馈 4D 感知器：不迭代去噪、一次前向 + 轻量解码器按查询出 4D 属性 → 「生成器可被改造成测量器」的直观参照 |
| 5 | 科普 | LIBERO-PeRM: Benchmarking Personalized Robotic Manipulation | 2610.22372 | 把「完成任务」与「满足偏好」拆开评：312 任务 / 5 套件，作者实测零样本个性化普遍很弱 → 「会干活」≠「懂你」 |

**红线自查**：① 收件人仅 `paul.liu@cxmt.com`（🚫 不加第三方）；② 原题照抄未改写；③ 数字均标「作者自报 · 未复现」，第 4 篇的 SOTA 照原文限定为「state-of-the-art or competitive」；④ 🚫 不夸大（不写「AI 已理解物理世界 / 家用机器人已成熟 / 颠覆」）；⑤ PDF 不入 git（`.gitignore` 命中 `pdf/` + `*.pdf`）；⑥ 附件合计 16.22 MB ≤ 20MB（Gen4P 36.3MB 超限 ⇒ 只给链接，不硬塞）。
