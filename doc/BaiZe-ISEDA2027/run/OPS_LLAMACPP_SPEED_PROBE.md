# OPS_LLAMACPP_SPEED_PROBE.md — P0 令：llama.cpp × Qwen3.5-2B（CPU）测速判定

> 下发对象：posttrain 线（`.17`）· 2026-11-23 19:0x · 用户直令
> 用户原话：「posttrain：听说 llama.cpp + qwen3.5-2b + 8线程 decode 速度可以有 30-60 tok/s，评估一下这个路线是否可行（本机llama.cpp server)」
> ⇒ 结论是**先测聚合吞吐**，不是先评单流速度。
>
> **背景（不要再复述错口径）**：wake744 实测 40 tok/s 是 **8 并发聚合** ⇒ 每 agent ~5 tok/s ⇒ 平均题 2,491s ≈ 2500s 超时 ⇒ 93.75% 空代码。
> 单流 30–60 tok/s 在 GPU5 上本来就实测到 **35.1 tok/s**（wake739），**它不能回答可行性**；
> 能回答的只有「8 路连续批处理后的聚合 tok/s」。

---

## A. 本轮唯一任务（~45 min，CPU-only）

在 `.17` 上跑 **`run/baize_posttrain_llamacpp_speed_probe.sh`**（已随本令入库，配套 `..._load.py`）：

```bash
cd /nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027
git fetch origin && git rebase origin/main   # 或按本线纯对象库流程
bash run/baize_posttrain_llamacpp_speed_probe.sh
```

脚本自动完成 5 个阶段并落盘，**不需要改任何代码**（缺 llama.cpp 自动 clone+build；缺 gguf 包自动 pip 安装）：

| 阶段 | 内容 | 失败含义 |
|:--|:--|:--|
| P1 G0 | 定位/编译 llama.cpp，记录 `rev / --version / lscpu / nproc / free -g` | 编不出来 ⇒ BLOCKED（如实报，别硬测） |
| P2 | `convert_hf_to_gguf.py` HF→F16，再 `llama-quantize` → Q4_K_M | **`unsupported model type qwen3_5` ⇒ 路线当场死，直接收口** |
| P3 G1 | `llama-bench` 线程扫描 `-t 8 16 32`（`-p 512 -n 128 -r 3`） | 拿到单流 pp/tg 曲线 |
| P4 G2 | `llama-server --parallel 8 --metrics --jinja`，跑 1 路 / 8 路 / 8 路长 prompt 三组负载 | **核心数字：8 路聚合 tok/s** |
| P5 | 解析 + 门禁 + 写 `run/llamacpp_speed_probe_<TS>.json` | verdict ∈ FEASIBLE / CONDITIONAL / NOT_FEASIBLE / BLOCKED |

## B. 预注册判据（**先写进 MEMORY 再跑，跑完不许改**）

| 门 | 判据 | 不通过怎么办 |
|:--|:--|:--|
| G0 架构 | F16 转换成功 + server 能起 | **停**，报「llama.cpp 不支持 qwen3_5」 |
| G1 单流 | 记录 `tg128` 最好值（预期 20–60 tok/s） | 仅作参照，不单独判定 |
| **G2 聚合** | **8 路聚合 ≥ 100 tok/s = PASS；64–100 = CONDITIONAL；< 64 = FAIL** | FAIL ⇒ 路线作废，**禁止**拿它跑 158 题 |
| G3 重复 | 任何输出 8-gram 最大重复 ≤ 5（防 BaiZe SSM-bug 式 repetition loop，见 `MEMORY_PRETRAIN_2B.md` §P2-001） | 超限 ⇒ `NOT_FEASIBLE_REPETITION`，先查权重映射再谈速度 |
| G4 工具 | `--jinja` 成功 = 可用；失败脚本自动回退并记 `tool_support=no_jinja` | 无 jinja ⇒ 后续需薄代理，本令不展开 |

脚本顺带算 **5-run 预计墙钟 / 每 agent tok/s / 平均题解码时长 / 超时余量比**
（锚点：12,453 tok/题 × 158 题 × 5 run ⇒ 9,837,870 tok）。
**判定读法**：`timeout_headroom_ratio < 1` 才不超时；`hours_5run` 是全部 5 轮墙钟。

## C. 交付（缺一不可）

1. `run/llamacpp_speed_probe_<TS>.json`（脚本产出；**不得手改**）。
2. 原始证据目录 `/tmp/baize_llamacpp_probe_<TS>/`：`probe.log` / `server.log` / `bench_*.log` / `load_c1.json` / `load_c8.json` / `load_c8_long.json`。
3. `MEMORY_POSTTRAIN.md` 顶部加 **1 行**：verdict + 三个数（single-stream / 8-way aggregate / 5-run 预计小时）。
4. `daily-memories-posttrain/2026-11-23.md` 一节：命令 + 结果 + 失败项。

## D. 纪律（硬红线）

- 🚫 **只 CPU**：`CUDA_VISIBLE_DEVICES=""`；不碰 GPU0-3 / GPU4(A0 base) / GPU6(vision)。
- 🚫 **不跑 158 题**、不改协议/题面/`check.py`/超时/`-p`、不起 SFT/RL。
- 🚫 不 kill 别线进程；只 kill 本脚本自己起的 `llama-server`（已按 PID 回收）。
- 🚫 **不许把 BLOCKED / infra 失败写成「模型太弱」**（`doc/AGENTS.md` 铁律 2）。
- ⚠️ 若 G2 = PASS，**先报告再等令**，不要自动接 5-run。

## E. 顺带义务（同一 wake 内必须处理）

`run/baize_posttrain_a5_server_v3_realstream.py` docstring 写着
「flash-linear-attention installed (wake745) batched throughput ~221 tok/s」——
**全仓无任何 221 tok/s 的落盘证据，wake745 的 daily 只有 A0 报告复验**。按铁律 1：
**要么补测落盘（作为 v3 路径对照数字），要么删掉该句**；不得继续留在代码注释里被引用。

## F. 用户侧的判定表（供 ops/用户读，不用 agent 填）

| 测量结果 | 结论 | 下一步 |
|:--|:--|:--|
| G0 失败（不支持 qwen3_5） | 路线不可行 | 回 vLLM nightly（ops 升驱动）或 v3 realstream |
| G2 < 64 tok/s | 路线不可行 | 同上；**不要**用 llma.cpp 跑 158 题 |
| 64 ≤ G2 < 100 | 有条件可行 | 先算 5-run 墙钟再决定；必要时减 `-n`/提线程 |
| G2 ≥ 100 且 G3 过 | 可行 | 报用户 → 决定是否做 A0+A5 同栈（同量化）重跑 |
