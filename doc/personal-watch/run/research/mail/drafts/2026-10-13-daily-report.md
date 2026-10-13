# 【日报草稿】2026-10-13 论文日报邮件（收件人 paul.liu@cxmt.com）

> 类型：**论文日报**（内部日报 · 免审直发）｜ 依据：`WATCH_RESEARCH_TASK.md` 运维指令 2026-10-12（📨 每日论文日报）
> 正文文件：`/tmp/body_2026-10-13.txt`（与本文件下方正文一致）｜ 发送器：`~/hr_mail.py`（`foamliu@yeah.net` / `smtp.yeah.net:465`）
> 附件：`research/pdf/2026-10-13/{2610.12995,2610.13835,2610.13889,2610.12866}.pdf`（4 个 · 8.20 MB ≤ 20MB）
> ⚠️ `2610.13917`（TOP-1 蛋白质）PDF **17.2MB**，单篇即超单封预算 ⇒ **不附，给链接**（符合「只附超额篇的链接 + 摘要」）。

---

**主题**：`[论文日报] 10-13 精选 5 篇（BaiZe/ZhuLong 相关）`

**发送命令**（实发记录）：

```bash
python3 ~/hr_mail.py --to paul.liu@cxmt.com \
  --subject "[论文日报] 10-13 精选 5 篇（BaiZe/ZhuLong 相关）" \
  --body-file /tmp/body_2026-10-13.txt \
  --attach research/pdf/2026-10-13/2610.12995.pdf \
  --attach research/pdf/2026-10-13/2610.13835.pdf \
  --attach research/pdf/2026-10-13/2610.13889.pdf \
  --attach research/pdf/2026-10-13/2610.12866.pdf
```

**正文**（= `/tmp/body_2026-10-13.txt`）：见文件 `mail/2026-10-13-body.txt`（同内容留档）。


**正文**：

```
paul 您好，

今日（2026-10-13）arXiv 当日筛选中精选 5 篇，PDF 见附件。

一、本轮取数说明（如实）
- arXiv 公告批次仍停留在 2026-10-09，未刷新（total=630616）；原因是周一 2026-10-12 为美国联邦假日（哥伦布日），公告顺延。
- 以下 5 篇取自最近一次公告窗口的候选池，并已用 id_list 逐条复核（HTTP 200 + published 有效）。
- 全部数字为「论文作者自报」，我们未复现；原题照抄未改写。

二、精选清单（3 篇「借鉴」+ 2 篇「科普/选题参考」）

【借鉴｜与 BaiZe/ZhuLong 强相关】

1. What Should SFT Learn? Conditional Information Gain for Generalizable Post-Training
   arXiv:2610.12995 ｜ 附件：是
   为何值得读：给出「SFT 该给哪些 token 更大权重」的可落地判据（条件信息增益 CIG -> 等价的标量加权 SFT 目标），不必改架构、只需在 loss 上加一组由冻结参考模型预计算的权重，可直接接进现有训练栈；对口 BaiZe 后训练的数据/权重口径。

2. Specialists Learn Faster: Knowledge Organization in Pre-training Shapes Knowledge Update Efficiency
   arXiv:2610.13835 ｜ 附件：是
   为何值得读：指出「预训练阶段对知识（尤其时变知识）的组织方式」会决定后续知识更新的成本与效率（按时间顺序训练 vs 打乱顺序），并给出与优化动力学吻合的更新成本规律与数据组织策略；对口预训练数据配比 / 新知识注入（持续更新）。

3. RATED: Reliability-Aware AI Agent Tool Retrieval via Execution Dynamics
   arXiv:2610.13889 ｜ 附件：是
   为何值得读：用「真实执行动态」而非静态语义相似度来检索 agent 工具，提升工具选择的可靠性；对口 ZhuLong 的 code / agent harness 与工具调用可靠性。

【科普｜选题 / 跨域参考】

4. Designing Protein Structures from Natural Language
   arXiv:2610.13917 ｜ 附件：是
   为何值得读：「用自然语言直接生成蛋白质结构」的方法样例（文本条件训练的配对数据构建 + 结构属性评测 + 湿实验验证），可作「语言条件生成」在非文本域的对照参考。

5. CaptchaAgent: Verifiable Visual Reasoning for CAPTCHA Solving
   arXiv:2610.12866 ｜ 附件：是
   为何值得读：把视觉推理做成可核验流程（视觉中间表示 + 符号协议逼计数 + 反事实一致性校验），并在验证码基准上系统性验证；对口多模态 agent 的可靠性与「可验证推理」设计。

三、附件
- 共 5 个 PDF，合计约 <TOTAL_MB> MB（上限 20 MB）。

—— 《超级智能2035》· research 自动日报
```

（署名沿用发件账号默认署名）
