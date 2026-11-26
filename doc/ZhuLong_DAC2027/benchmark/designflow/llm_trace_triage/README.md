# LLM Trace Triage（llama.cpp + Qwen3.5-0.8B Q8_0）

> 目的：把 DesignFlow 候选池从「**mc>=100 关键词计数**」升级为「**语义预筛 + 排序**」。
> 定位：**triage（预筛）**，不是 ground truth。最终 case 仍须 deepread + .75 实跑验证。
> 模型：`Qwen3.5-0.8B` Q8_0（CPU ~90 tok/s，见 `doc/ZhuLong_DAC2027/reports/report_zhulong_llamacpp_qwen08b_zh.html`）。

## 0. 要回答的三个问题

1. `mc>=100` 的候选里，有多少其实**不是** EDA 工作流（关键词误命中）？
2. `mc<100` 的 trace 里，有多少是**真实 EDA 工作流**（被粗筛漏掉）？
3. 用 0.8B 的语义分替代/叠加 mc，能否得到一个更干净的候选池？

## 1. 三阶段

```
summary.tsv ──(02_make_sample)──> triage_input.jsonl
                                      │  (agent: open_session -> 01_condense_session)
                                      ▼
llama-server(Q8_0) ──(04_triage)──> labels.jsonl
                                      │
                                      ▼
                              (05_compare_mc) ──> compare.json / .md
                                      │
                                      ▼
                              (06_report_zh) ──> HTML 报告
```

## 2. 输出标签（严格 JSON）

```json
{
  "is_eda_workflow": true,
  "domain": "digital|analog|layout_virtuoso|layout_aether|pg_layout|verification|spice_sim|pnr_signoff|schematic_netlist|physical_verify|characterization|eda_other|none",
  "task_type": "short English description (<=12 words)",
  "tools": ["innovus", "calibre", "..."],
  "stage": "setup|run|debug|signoff|analysis|unknown",
  "evidence": ["verbatim phrase 1", "verbatim phrase 2"],
  "confidence": 0.0
}
```

## 3. 采样与评测

- 分层采样：mc ∈ [1,40) / [40,100) / [100,300) / [300,∞)，每层 25 条 → **100 条**。
- 人工金标：每层 5 条（共 20 条）由 agent deepread 后标 `yes/no`，写入 `gold.tsv`。
- 判据：
  - 金标一致率 **>= 80%**（低于则调 prompt / 加 few-shot，不准直接上线）；
  - `mc>=100` 的 LLM 真阳性率（precision）与 `mc<100` 的漏检数要**分开报**；
  - 新候选池 `pool_llm_v1.tsv` 需给出「按 confidence 排序后前 100 条的域分布」。

## 4. 成本

- 输入：每 session 压缩到 ≤6000 字符（约 1500–2500 token）。
- 速度：prompt ~394 tok/s、生成 ~90 tok/s（64 核，`-t 32`）。
- 100 条约 **15–25 分钟**；1000 条约 **2.5–4 小时**（可夜间跑）。

## 5. 硬约束

- 只喂**压缩后的文本**；不要把原始 `messages.json`（含用户名/IP/大文件）上传或入库。
- `user/host/session_file` 一律用 sha1[:12]（沿用现有脱敏口径）。
- 0.8B 的结论只能写「triage/候选排序」，不得写成「已确认是 EDA case」。
- 结果 JSONL 不入库（与评测结果同口径）。
