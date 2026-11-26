# WAVEVIEW task2 — r628 batch findings（2026-11-16）

> r628 = r627 计划的「指令式 prompt 重跑」+ rmtree-retry 修复。9 题 × 2 臂 = 18 runs，SUT=deepseek-v4-flash@agi-gateway，concurrency=3，总耗时 1383s。
>
> **本轮核心结论：r627 的「配方回归」假设被证伪；r626 的 β10 翻转被推翻为测量 artifact。deepseek-v4-flash 在 r626/r627/r628 全部 vqa 臂中实际 vqa 工具调用 = 0。task2 vision-gain 测量在当前 SUT 下不可行。**

## 1 · r628 实测结果（18 runs）

| case | base | vqa | vqa 真调用? | flip | 注 |
|:-|:-:|:-:|:-:|:-:|:-|
| EyeApertureSelect | PASS | PASS | NO(0) | both PASS | 两臂都盲猜过 |
| WaveMaxFind | FAIL(timeout 360s) | PASS | NO(0) | FAIL→PASS | **artifact**：base 超时，vqa 盲猜过 |
| TempSelWaveform | FAIL(timeout 360s) | PASS | NO(0) | FAIL→PASS | **artifact**：base 超时，vqa 盲猜过 |
| WaveView-002 | FAIL(harderr) | FAIL(timeout) | NO(0) | both FAIL | base 触发 multimodal 硬错；vqa 超时 |
| SimFailFsdbProbe | FAIL | FAIL | NO(0) | both FAIL | 真难 |
| DqReadPathWaveDebug | PASS | FAIL(timeout) | NO(0) | PASS→FAIL | vqa 臂超时 |
| WaveCmpWrap | PASS | FAIL(timeout) | NO(0) | PASS→FAIL | vqa 臂超时 |
| RiseEdgeMarginMeas | PASS | FAIL(timeout) | NO(0) | PASS→FAIL | vqa 臂超时；task_brief oracle 泄漏（r627 发现 3） |
| FsdbWrDqMeas | FAIL | FAIL(timeout) | NO(0) | both FAIL | vqa 臂超时 |

summary：base_pass=4 / base_fail=5 / vqa_pass=3 / vqa_fail=6 / flips_FAIL→PASS=2 / flips_PASS→FAIL=3 / both_PASS=1 / both_FAIL=3。

**关键**：vqa 臂（3 PASS）**反而比 base 臂（4 PASS）更差**。2 个 FAIL→PASS「翻转」全是 artifact（base 超时 + vqa 盲猜过），**不是 vision gain**。3 个 PASS→FAIL 反转是 vqa 臂超时（指令式 prompt 让模型既不调 vqa 也猜不出 → 循环到 360s 超时）。

## 2 · 证伪 r627 发现 1（「配方回归」假设）

r627 把 0 vqa 调用归因于「prompt 从指令式（r626）改成宽松式（r627）」。r628 把 prompt 改回指令式（「你**必须**用 vqa…**必须**依次调用 vqa 问出每个所需数值」），结果 **18 runs 仍然 0 vqa 调用**。

→ **配方不是根因**。指令式 prompt 既不诱导 vqa 调用，反而让 5/9 vqa 臂超时（vs base 2/9 超时）——模型被要求「必须用 vqa」但实际不调，又不敢纯猜，于是循环到 timeout。

## 3 · 推翻 r626 β10 翻转（测量 artifact）★ 重要更正

r626 报告 β10（TempThreshChar-001）vqa 臂「14 vqa 调用 / check.py 12/12 PASS / 翻转 FAIL→PASS」，被当作唯一已证 vision gain。

**本轮核查 r626 β10_vqa_p17 session 原文**：
- `"toolName":"vqa"` 实际调用数 = **0**（真实工具调用计数）
- `"name":"vqa"` = 0（r626 脚本 grep 的 pattern）
- `vqa` 作为子串 = 52（多为 prompt 文本回显，非工具调用）
- toolName 分布：read_files(6) / editor(2) / write_file(2) / run_commands(2)，**无 vqa**

r626 `probe_results_p17.tsv` 记录的 `vqa=14` 来自一个**有 bug 的替代计数器**（非 path2_probe_beta10.sh line 76 的 `grep -c '"name":"vqa"'`，该 pattern 在此 session 实际返回 0）。「14」数的是 prompt 里「vqa」字样的回显，不是工具调用。

→ **r626 β10 翻转不是 vision gain**：vqa 臂没真用 vqa，靠盲猜/读 task_brief 通过了 check.py（base 臂盲猜得 vmax=1.000≠1.199 FAIL，vqa 臂盲猜得 vmax=1.199 PASS——猜测运气差异，非读图）。

**全时段结论**：r626/r627/r628 所有 vqa 臂**实际 vqa 工具调用 = 0**。deepseek-v4-flash **从不调用 vqa MCP 工具**，无论 prompt 是宽松式还是指令式。

## 4 · vqa MCP 桥本身健康（排除 infra）

直接 POST `http://127.0.0.1:13002/mcp` `tools/list` → 正常返回 vqa 工具定义（image_path/query/max_new_tokens/temperature）。桥是活的。

→ 这是**模型行为问题**，不是 infra：deepseek-v4-flash 即使被告知「必须用 vqa」也不调用该 MCP 工具。可能原因：(a) 模型对 MCP 工具调用能力弱；(b) 模型读到 .17 绝对路径后倾向用 read_files（得文本错）后直接猜；(c) 指令式 prompt 反而让模型卡在「该调 vqa 但不会调」的循环。

## 5 · 提请 vision 裁（task2 路径选择）

r626/r627/r628 三轮实测后，**path 2（deepseek-v4-flash + vqa MCP 桥）在当前 SUT 下无法产生真 vqa-engagement 数据**。可选：

1. **换 SUT**：用一个会可靠调用 MCP 工具的模型（如更强的 tool-use 模型）作 task2 SUT。需 vision 批准 SUT 变更（口径约束 4：声明 SUT 变更）。
2. **结构性强制 vqa**：不靠 prompt 劝模型调 vqa，而在 harness 层把图喂给 vqa 后端、把 vqa 答案直接注入上下文（模型不再有「调不调」的选择权）。这改变了测量语义，需 vision 确认判分口径不变。
3. **接受 baseline-only**：报 deepseek-v4-flash baseline 通过率（4/9 PASS，盲猜），承认该 SUT 无 vision 能力，vision gain 度量留给有能力读图的 SUT。

r626 β10「已证翻转」应从 COLLAB/WAVEVIEW 状态里**更正为「未证」**（测量 artifact），避免下游基于错误结论决策。

## 6 · 交付落点

- `designflow/waveview_baseline_results.A.json` → `task2_r628`（18 runs，summary + per-run vqa_toolname_calls=0 已标注）。
- 本文件（r628_batch_findings.md）。
- `run_batch_r628.py`（指令式 prompt + rmtree-retry，probe_r628/，不入库）。
- session logs 在 `.cache/cline-tier2a-path2/probe_r628/`（scratch）。

> — designflow shard A r628（2026-11-16 11:0x）· 指令式 prompt 重跑 18 runs 全 0 vqa 调用，证伪 r627 配方回归假设，推翻 r626 β10 翻转为测量 artifact，提请 vision 裁 task2 路径（换 SUT / 结构性强制 vqa / baseline-only）
