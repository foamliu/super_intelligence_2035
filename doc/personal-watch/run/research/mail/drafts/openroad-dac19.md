# 请教信草稿 · OpenROAD（DAC 2019，无 arXiv）

- 收件人：Andrew B. Kahng（UCSD，CSE/ECE 教授；OpenROAD / TILOS 核心）
- 邮箱：`abk@ucsd.edu`（来源 `https://vlsicad.ucsd.edu/~abk/index.html`，`HTTP 200`，页内 `mailto:abk@ucsd.edu`）
- 语言：英文（非中文姓名）
- 论文：Toward an Open-Source Digital Flow: First Learnings from the OpenROAD Project（DAC 2019，DOI `10.1145/3316781.3326334`）
- 主题：OpenROAD 的 flow 作为「LLM 驱动设计 agent」的可复现评测基线 —— 三个问题
- 问题映射：
  1. 版本耦合 / 不变量 → designflow（保真度与可复现性）
  2. 最小固定集 + QC 抓静默回归 → harness（判分口径）
  3. agent 改脚本的最小护栏 → zhulong（闭环动作接受条件）
- 红线：单收件人、不群发、不催、不承诺合作/署名/资助、不透露未公开内部信息、不加第三方。
- 发送前置：`wc -w` ≤200。

## 正文

Subject: OpenROAD's flow as a fixed baseline for LLM-driven design agents — three questions

Dear Professor Kahng,

I am Yang Liu, an engineer working on BaiZe (ISEDA 2027) and ZhuLong (DAC 2027), two projects that apply language models to chip design flows. We are re-reading "Toward an Open-Source Digital Flow: First Learnings from the OpenROAD Project" (DAC 2019) because we want to use an open, scriptable flow as a reproducible evaluation base instead of a proprietary one.

Three questions:

1. Among the "lessons learned", which tool-to-tool interfaces (synthesis, placement, CTS, routing, or timing and parasitic extraction) proved most brittle across tool versions? If an agent's actions must survive a version bump, which invariants should we depend on?

2. To use the flow as a scoring baseline, what is the minimal fixed set you would pin (tool commit, PDK, design suite), and which QC checks catch silent regressions before metrics drift?

3. When an agent edits scripts or constraints, what minimal guardrails did you find necessary before accepting a change (DRC clean, timing report parse, metric gates), and where did naive automation fail?

Any pointers would directly shape our benchmark design.

Thank you,
Yang Liu
