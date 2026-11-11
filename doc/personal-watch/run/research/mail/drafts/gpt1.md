# 草稿 · GPT-1 作者请教信（Karthik Narasimhan）

- 论文：Improving Language Understanding by Generative Pre-Training（GPT-1，2018，无 arXiv / 无 DOI）
- 收件人：karthikn@princeton.edu（来源：本人主页 `https://karthiknarasimhan.com/` 的 `mailto:`，percent-encoded）
- 语言：英文（印度裔 ⇒ 按英文，`RESEARCH_MAIL_SPEC §2`）
- 主题：GPT-1  hindsight + agent harness 的记账口径
- 轮次：2026-11-11 18:00 时窗 · 第六轮（经典轨）
- 频率合规：每轮 ≤3 封（本轮 1 封）· 同作者 ≤1 · 不群发不催 · 无附件

## 正文（发出版）

Subject: GPT-1 in hindsight: how should we account for LLM agents on EDA tasks?

Dear Prof. Narasimhan,

I am Yang Liu, author of "Superintelligence 2035". I lead BaiZe-ISEDA2027 and ZhuLong-DAC2027, where we build a small (~2B) model for electronic design automation and an evaluation harness for EDA agents. Our two-stage recipe (generative pretraining, then task-format fine-tuning) traces back to your GPT-1 paper, and your later agent work shapes how we score agents.

Two questions where your experience would change our design:

1. ReAct-style explicit Thought/Action loops versus letting the model emit tool calls directly: in hindsight, which task properties make the explicit loop pay off? Our tools (simulation, synthesis) cost minutes per call, so wasted calls are expensive.

2. When grading agents, how much of the measured score comes from the checker versus the user/environment simulator? We report cost per solved task and need a defensible way to count retries and simulated turns.

Happy to share a short summary of our harness if useful. Thank you for your time.

Best regards,
Yang Liu
《超级智能2035》author · BaiZe-ISEDA2027 / ZhuLong-DAC2027

## 备注

- 🚫 未承诺合作 / 署名 / 资助 / 数据共享；🚫 未透露任何未公开内部信息（只说明「小模型 ~2B」与「EDA agent 评测」这一公开层面的定位）。
- 问题均指向**可回填研发决策**的点：harness 的显式推理循环取舍、成本记账口径（retry / 模拟轮次）。
- 同机构（Princeton）今日已有 Shunyu Yao 一封（11:43）⇒ 本封为当日第 2 封，**达上限、不再追加**。
