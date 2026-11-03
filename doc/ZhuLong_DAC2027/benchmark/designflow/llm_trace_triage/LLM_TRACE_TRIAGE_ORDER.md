# LLM_TRACE_TRIAGE_ORDER.md — 用户令（2026-11-03 22:3x）：用 llama.cpp 做 trace 语义预筛

> 背景：候选池一直用 `mc>=100`（EDA 关键词命中次数）粗筛。它既会**误收**（关键词刷分但非工作流），
> 也会**漏掉**（真实工作流但关键词少）。本 pilot 用本机 `Qwen3.5-0.8B Q8_0` 做语义判定，量化这两个误差。
> 工具目录：`benchmark/designflow/llm_trace_triage/`（README 有 schema 与成本）。
> **定位：triage，不是 ground truth。** 最终 case 仍须 deepread + .75 实跑。

## 0. 硬约束

1. 只跑本 pilot；**不改** 现有 case 队列、jsonl、ledger、rewrite_queue。
2. 原始 `messages.json` **不入库**；只保存 6000 字符以内的压缩文本，sid 用 sha1[:12]。
3. 0.8B 结论只能写「候选排序/预筛」，不得写成「已确认 EDA case」。
4. 不占 8090；llama-server 用 **18081**，测完关闭。
5. 失败如实报（编译/下载/解析失败都写报告），禁止编造一致率。

## 1. 环境（缺则装，仓库外）

```bash
ls -l $HOME/tools/llama.cpp/build/bin/llama-server \
      $HOME/models/Qwen3.5-0.8B/Qwen3.5-0.8B-Q8_0.gguf
# 缺任一：
bash doc/ZhuLong_DAC2027/run/setup_llamacpp_qwen35.sh
```

- 该脚本已含 **ModelScope 回退**（实测 hf-mirror 会 308 跳回 huggingface.co 被代理封 503）。
- 模型/工具都在 `$HOME`，**不要**放进 repo。

## 2. 分层抽样（32 条）

```bash
cd doc/ZhuLong_DAC2027/benchmark/designflow/llm_trace_triage
SUMMARY=<现有扫描 summary.tsv 路径>     # 用 trace_ledger.py 同源文件
python3 02_make_sample.py --summary "$SUMMARY" --per-bin 8 \
  --out /tmp/triage/input_raw.jsonl --seed 13
```

- 分箱：`[1,40) / [40,100) / [100,300) / [300,∞)`，每箱 8 条。
- 若 `summary.tsv` 不可达，先用现有 `summary_stats.json` 的生成脚本重建，或如实报缺。

## 3. 导出并压缩文本（agent 做）

对 `input_raw.jsonl` 中每条：
1. `open_session(BENCH-DEEPREAD)` → `scp messages.json` 到本机 `/tmp/triage/raw/<session_file>.json`；
2. `python3 01_condense_session.py /tmp/triage/raw/<session_file>.json --out /tmp/triage/texts/<session_file>.txt --max-chars 6000`；
3. 回填：重新跑 `02_make_sample.py --texts /tmp/triage/texts --out /tmp/triage/input.jsonl`。

> 大 session（>2MB）只压缩，不整包复制进 repo；超时/失败标 `needs_fetch`，不要卡住。

## 4. 启动 + 推理

```bash
bash 03_serve.sh 18081 32 2
python3 04_triage.py --input /tmp/triage/input.jsonl \
  --out /tmp/triage/labels.jsonl --parallel 2 --resume
```

- 1000 条约 2.5–4h；32 条约 **10–15 分钟**。
- 若 `json_schema` 被拒（HTTP 400），脚本会自动回退；仍失败则记录错误，不要改判据。

## 5. 金标（12 条，人工）

从 4 个箱各挑 3 条，deepread 后写 `/tmp/triage/gold.tsv`：

```
<sid>\t<0|1>      # 0=非 EDA 工作流，1=真实 EDA 工作流
```

> 金标只看**是否真实 EDA 工作流**，不看 domain 细类；避免主观分歧。

## 6. 对比 + 报告

```bash
python3 05_compare_mc.py --labels /tmp/triage/labels.jsonl \
  --gold /tmp/triage/gold.tsv --out /tmp/triage/compare.json \
  --pool-out doc/ZhuLong_DAC2027/benchmark/designflow/llm_trace_triage/pool_llm_v1.tsv
python3 06_report_zh.py --compare /tmp/triage/compare.json \
  --out doc/ZhuLong_DAC2027/reports/report_designflow_llm_triage_zh.html
```

## 7. 判据与交付

- **PASS**：金标一致率 `>= 80%`；报告给出
  - `mc>=100` 的 precision（误命中率）；
  - `mc<100` 中被找回的真 EDA 条数；
  - 按 confidence 排序的新候选池前 20 条；
  - 建议（是否把 triage 分叠加到 mc 上、阈值取多少）。
- 交付物：
  1. `reports/report_designflow_llm_triage_zh.html`（中文，自包含）；
  2. `compare.json`（不入库，落远端）；
  3. `llm_trace_triage/pool_llm_v1.tsv`（可入库，已脱敏）；
  4. `MEMORY_DESIGNFLOW.md` 顶部 1 条状态 + `commit designflow triage:`。
- **PASS 后先报告再等令**：是否扩到 25/箱、是否接入下一轮选料，由用户决定。
- **FAIL（<80%）**：先调 prompt/few-shot（加 2 个难例），不要直接换阈值；仍 FAIL 则如实写「0.8B 不足以做该判定」。
