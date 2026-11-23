# OPS_A5_LLAMACPP_Q4KM_RUN1.md — P0 令：llama.cpp + Q4_K_M 跑 A5 单 run（run1）

> 下发对象：posttrain（`.17`）· 2026-11-23 22:0x · 用户直令
> 用户原话：「posttrain 先用 Q4_K_M 量化 + llama.cpp 跑一个 A5 看结果」
>
> 前置已具备：19:53 测速 **verdict=FEASIBLE**（single-stream 30.16 / **8-way aggregate 132.52 tok/s** / 5-run 预计 20.6h / G3 重复=1 / G0 转换 OK）。
> 本令只跑 **1 个 run（run1）**，目的是「端到端能不能出可用数字」，**不是** 5-run 均值。

---

## A. 口径（先写进 MEMORY 再跑，跑完不许改）

| 项 | 值 |
|:--|:--|
| 臂 | **A5 = Qwen3.5-2B 原模型**（非 SFT / 非 adapter） |
| 权重 | `/nas_data/app.e0031982/models/qwen35_gguf/qwen3.5-2b-Q4_K_M.gguf`（**记录 sha256**） |
| 后端 | llama.cpp `rev 969d733`，`--parallel 8` / `-t 16 -tb 16` / `-c 262144` / `--jinja` / `--alias qwen3.5-2b-a5` |
| 端口 | **`:8095`**（`curl /v1/models` id 必须 == `qwen3.5-2b-a5`） |
| 协议 | **158 题 / Pass@1 / 2500s / 单 trace / `-p 8 -n`**（与 A0 完全一致，不许改） |
| 运行数 | **run1 单次**（不是 5-run，不许报 mean±std） |
| 标签 | `qwen35_q4km_llamacpp` |

🔴 **可比性红线**：A0 的 43.29% 是 **vLLM fp16** 口径。本次是 **Q4_K_M 量化 + llama.cpp** 口径 ⇒
**禁止**与 A0 做 McNemar / 配对检验，也禁止写「A5 比 A0 高/低 x pp」。
本轮结论只能是：**「A5 在 Q4_K_M+llama.cpp 下的单 run Pass@1 = x%，infra 是否干净」**。

## B. 执行步骤（总预算 ≤ 9h）

### B0 前置（5 min）
```bash
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader   # 记录；GPU4/6 不许碰
sha256sum /nas_data/app.e0031982/models/qwen35_gguf/qwen3.5-2b-Q4_K_M.gguf
cp ~/.cline/data/settings/providers.json /tmp/providers.pre_a5.json && sha256sum /tmp/providers.pre_a5.json
ss -ltn | grep -E ':(8095|8097|8098) ' || true     # 8095 必须空；8097 上的 v3 server 不许 kill
```

### B1 起服 + 预检（10 min，**不过就停**）
```bash
cd /nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027
PY=/nas_data/app.e0031982/miniforge3/envs/py310/bin/python \
NO_PROXY=127.0.0.1,localhost \
  bash run/baize_posttrain_a5_llamacpp_serve.sh
```
预检门（脚本自动跑，任一 FAIL 退出码=4 并自动收服）：
**P0 身份** `/v1/models` id 匹配 · **P1 非流式 tool_calls** · **P2 流式 tool_calls（cline 用的形态）** ·
**P3 工具结果回灌** · **P4 10 题×3 次零翻转** · **P5 无长 CoT 泄漏**。
> P4 尤其重要：llama.cpp 批处理会改变浮点累加顺序，若翻转不为 0，本次单 run 仍可报，但**必须**在结果里写明「5-run 复现性未验证」。
> 若 `-c 262144` 因内存分配失败起不来，按序降级 `CTX=131072`（8×16k）→ `CTX=98304`（8×12k），并在结果里记录实际 ctx；
> 若仍起不来 ⇒ 报 BLOCKED（infra），不要改 `--parallel`（会破坏 `-p 8` 对齐）。

### B2 开跑（~5–7h，硬上限 8h）
```bash
cd /nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027
bash run/baize_posttrain_5run_eval.sh \
  --endpoint http://127.0.0.1:8095/v1 --model qwen3.5-2b-a5 \
  --label qwen35_q4km_llamacpp --run 1
```
> 该脚本会自动把 `providers.json` 指向 `:8095`、跑 `run_cline_script.sh -p 8 -n`、再还原；**跑完必须人工复核还原**（见 B4）。

### B3 运行中看门狗（**关键：防再出一次 93.75% 空代码**）
- 开跑后 **20 min / 45 min** 各查一次 `~/eda_code_eval/completed_code_generation_*.jsonl`：
  若前 10 题里 **≥3 题空代码 / tool_calls=0** ⇒ **立即停**，判 `infra/throughput` 失败，
  **禁止**把这次 Pass@1 当能力结论（铁律 2），并保留 codegen.log。
- 同时抽查 server 日志：出现 500 / `failed to parse tool call` / context overflow ⇒ 停并记录。

### B4 收口（30 min）
1. 停服：`bash run/baize_posttrain_a5_llamacpp_serve.sh stop`（只 kill 自己 pidfile 里的进程）。
2. 还原核验：`sha256sum ~/.cline/data/settings/providers.json` 必须 == `/tmp/providers.pre_a5.json`；不等 ⇒ 从备份恢复并记事故。
3. 汇总（从 `/tmp/posttrain_5run_eval/qwen35_q4km_llamacpp/run1/` 抽）：
   Pass@1 / n_pass / n_total / **F1_no_code 计数** / timeout 计数 / **cheat rate** / 墙钟 / 总 output tokens / server prompt+decode tokens；
   落盘 `run/baseline_A5_qwen35_2b_llamacpp_q4km_run1_summary.json`。
4. 逐题：`run/baseline_A5_qwen35_2b_llamacpp_q4km_run1_pertask.json`。
5. 证据：`run/a5_llamacpp_server_<ts>.json` + `run/a5_llamacpp_preflight_<ts>.json` + server.log 路径写进 MEMORY。

## C. 判定（预注册）

| 结果 | 结论 | 下一步 |
|:--|:--|:--|
| 预检 FAIL | 不可跑 | 报具体门（P1/P2 尤其），**不许**改协议硬跑 |
| 空代码 ≥3/10 | infra 失败 | 报吞吐/解析根因；不许当能力结论 |
| run 完成且 empty<5% | ✅ 有效单 run | 报 Pass@1（标 Q4_K_M 口径）→ 再定 A0+A5 同栈 5-run |
| run 完成但 cheat rate >0 | 结果单列 | 逐题剔 cheat 后再算，并报告 |

## D. 纪律

- 🚫 不碰 GPU0-3 / GPU4(A0 base) / GPU6(vision) / GPU7；本令纯 CPU。
- 🚫 不改 `-p 8` / `2500s` / 158 题 / 题面 / `check.py` / 打分口径。
- 🚫 不 kill `:8097` 上的 v3 server（那是本线 idle 进程，但与本令无关）；端口冲突改用 `PORT=18098`。
- 🚫 不把 Q4_K_M 结果与 A0 vLLM fp16 43.29% 做配对或相减。
- ✅ 反作弊常开；负结果/失败分类如实写（`infra / harness / 能力` 三分）。
