# 请教信草稿 · A Case for Intelligent RAM（IEEE Micro 1997，无 arXiv）

- 收件人：David A. Patterson（UC Berkeley EECS 荣休教授；IRAM 一作）
- 邮箱：`pattrsn@cs.berkeley.edu`（来源：EECS 院系现行页 `https://www2.eecs.berkeley.edu/Faculty/Homepages/patterson.html`，`HTTP 200` / 249,647 B，页内明文；**旧个人页自述「not been kept up」⇒ 不用旧页**）
- 语言：英文（非中文姓名）
- 论文：A Case for Intelligent RAM（IEEE Micro 17(2):34–44, 1997；DOI `10.1109/40.592312`）
- 主题：IRAM 论证在 HBM / chiplet 时代还剩什么 —— 三个问题
- 问题映射：
  1. 论证的哪部分仍成立 → zhulong（架构-成本论证）
  2. 最小可信实验（保真度 / 基线） → zhulong + harness（判分口径）
  3. 未成主流的主因 → zhulong（立项取舍）
- 红线：单收件人、不群发、不催、不承诺合作/署名/资助、不透露未公开内部信息、不加第三方。
- 发送前置：`wc -w` ≤200。

## 正文

Subject: IRAM in hindsight: three questions on the memory-wall argument

Dear Professor Patterson,

I am Yang Liu, an engineer working on BaiZe (ISEDA 2027) and ZhuLong (DAC 2027), two projects that apply language models to chip design and memory-systems analysis. We re-read "A Case for Intelligent RAM" (IEEE Micro, 1997) because it is the cleanest statement of merging compute and memory when the gap keeps widening, and we now face a similar bandwidth-versus-compute argument with HBM.

Three questions:

1. Your case rested on a 50%-per-year processor-DRAM speed gap plus awkward DRAM organization. Which part of that argument survives HBM and chiplet packaging, and which part was overtaken by them?

2. If you were restating the case today for bandwidth-bound LLM inference, what is the minimum credible experiment — in simulation fidelity, baselines, and metrics — that would make you believe a PIM speedup claim?

3. IRAM did not become mainstream. In hindsight, was the binding constraint manufacturing cost, the programming model, or the absence of a killer application — and which one should a new project solve first?

Any pointers would directly shape our architecture-cost analysis.

Thank you,
Yang Liu
