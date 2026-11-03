# BaiZe 2B CPU 评测加速：llama.cpp（GGUF）pilot

> 目标：把 `hf_iter_*` 的 8 集 CPU 评测从 **16.44 s/req**（PyTorch 逐 token Mamba2 reference）
> 降到 **1 s/req 量级**，从而在 11-04 14:50 前把 limit 从 100 提到 500 / 全量。
> 本目录只做“加速 + 等价性验证”，**不改任务口径、不改评分逻辑、不碰 GPU/S1**。

## 0. 结论与前提

- 模型是 **Nemotron-H 式 Mamba2-hybrid**（56 层 = 24 Mamba2 + 4 Attention + 28 MLP，
  `hybrid_override_pattern=M-M-M--M-M*-...`），HF 导出为 `nemotron_h`；
  llama.cpp 原生支持 `nemotron_h`，`convert_hf_to_gguf.py` 可直接转换。
- 评测要的是 **loglikelihood**（不是生成）。llama-server 的 `echo` 不回传 prompt token 的
  logprob（llama.cpp issue #27174），因此采用与 lm_eval 官方 `gguf` 后端相同的办法：
  **用 `logit_bias` 强制目标 token，读它的 logprob**，逐 token 累加。
- 为避免 BPE 边界误差，prompt 直接传 **token id 数组**（native `/completion` 支持），
  分词也走 server 的 `/tokenize`，全程只用一套分词器。
- 已知限制：
  1. `loglikelihood_rolling` 不支持（8 个常识集用不到）；
  2. HellaSwag 的 continuation 较长，会放大“逐 token HTTP”开销；
  3. 量化（Q4/Q8）会改变 logits。**官方数字只用 F16**，量化只用于冒烟。

## 1. 目录

```
run/pretrain_cpu_eval_gguf/
  README.md                    本文件
  00_build_llamacpp.sh         编译 llama.cpp（CPU，带 proxy）
  01_convert_hf_to_gguf.sh     hf_iter_<it> -> bz2b-<it>-f16.gguf
  02_check_tokenizer.py        GGUF 分词 vs HF 分词 逐 id 对拍（硬门槛）
  03_serve_llama_server.sh     起 llama-server（nice 19 / 限线程 / prompt cache）
  gguf_lmeval_run.py           自定义 LM 后端 + lm_eval.simple_evaluate
  04_run_one_ckpt.sh           单个 ckpt 一条龙（转换->起服->自检->评测->收服）
  05_compare_with_hf.py        与同 ckpt 的 HF results.json 做等价性对比
  06_server_selftest.py        校验 token-id prompt + logit_bias + n_probs 三个契约
```

产物（都落在远端，不入库）：

```
/nas_train/app.e0031982/models/baize2b_gguf/bz2b-<it>-f16.gguf
.../nemo_experiments/baize2b/lm_eval_results/gguf_iter_<it>/results.json
.../lm_eval_results/gguf_iter_<it>/meta.json
```

## 2. 快速开始（远端 .29 / .12 上执行）

```bash
# 远端仓库根：/nas_train/app.e0031982/code/super_intelligence_2035
# 本目录：    $REPO/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf
REPO=/nas_train/app.e0031982/code/super_intelligence_2035
D=$REPO/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf
PROJ=$REPO/doc/BaiZe-ISEDA2027

# 2.1 编译（约 5-10 分钟，走 proxy）
bash $D/00_build_llamacpp.sh

# 2.2 单 ckpt 冒烟：iter_10000，先 sciq+piqa 各 100 题（约 10 分钟）
bash $D/04_run_one_ckpt.sh 10000 --limit 100 --tasks sciq,piqa --port 8080

# 2.3 等价性判定
python3 $D/05_compare_with_hf.py 10000
```

通过后铺开 5 个 ckpt：

```bash
for it in 10000 20000 30000 40000 50000; do
  bash $D/04_run_one_ckpt.sh $it --limit 500 --port 8080
done
```

生成与 HF 版同款中文 HTML 报告（复用现有生成器，只换前缀/路径）：

```bash
cd $PROJ
BAIZE_CKPT_PREFIX=gguf_iter_ \
BAIZE_REPORT_PATH=$PROJ/reports/report_pretrain_cpu_eval_gguf_zh.html \
python3 run/gen_cpu_eval_8sets_report.py
```

## 3. 验收判据（任一不过 => 不切换）

1. `06_server_selftest.py` 通过（token-id prompt / logit_bias / n_probs 三个契约都成立）；
2. `02_check_tokenizer.py` 在 10+ 条中/英/混排/代码样例上 **token id 完全一致**；
3. 同一 ckpt、同一 limit、同一任务：`|Δacc| <= 1.0pp`，且 8 集 Avg `|Δ| <= 1.0pp`；
4. 速度 `>= 5x`（meta.json 里的 s/req vs HF 的 16.44 s/req；可用 `--hf-s-per-req` 覆盖）；
5. 结果 JSON 能被 `run/gen_cpu_eval_8sets_report.py` 直接读出（结构兼容）。

> 数字口径：**F16**（不是 Q4/Q8）。若为提速用 Q8_0，只允许出现在 `--limit 20` 的冒烟里。

## 4. 已知坑

- **分词器**：llama.cpp 曾把 Nemotron 的 Tekken 分词错标成 `pixtral`（issue #30894，
  2026-10-20；修复 #30960）。必须用较新的 master，并**以 `02_check_tokenizer.py` 为准**。
- **logprob 抖动**：2026-10 有 issue #31206（SYCL+MoE 下 logprobs 不确定）。
  本机是 CPU + 非 MoE，但仍建议 server 固定 `--temp 0 --top-k 1 --seed 1234`，
  且同一题 4 个候选 pin 到同一 slot。
- **`-c` 是总上下文**：`--parallel N` 会把 `-c` 均分。脚本默认
  `-c = 2048*N`，保证每个 slot 有 2048。
- **不要与 HF 的点混画一条曲线**：要么 5 个 ckpt 全用 GGUF，要么只用 GGUF 做 limit 扩展，
  HF 的 iter_10000 仅作等价性桥接并在报告里注明。
- **降载**：`nice -n 19`、`OMP_NUM_THREADS=1`、`-t 32`。本机还有 S1 训练和别的 CPU 评测，
  严禁 `pkill python`。

## 5. 回退方案

- 任何一个判据不过：直接删/忽略 `gguf_iter_*`，继续用 `baize_cpu_lmeval.sh`（HF）。
- 若只是“慢但准”：把 `.12` 上的两个 float32 改为 `--dtype bfloat16`（约 2x，零口径风险），
  仍用原脚本 `baize_cpu_lmeval.sh <hf_dir> <out> --dtype bfloat16`。
- 若 GPU 在 Nov 4 前空出：优先 `sglang`（原生 `nemotron_h`），精度最高、工量最小。

## 6. 时间预算

| 步骤 | 预计 |
|---|---|
| 编译 llama.cpp | 5-10 min |
| 转 1 个 ckpt F16（2.2B，4.4GB） | 3-6 min |
| 分词对拍 | <1 min |
| sciq+piqa limit=100（800 req） | 5-15 min（取决于实测） |
| 全 8 集 limit=100（2599 req） | 1-3 h（若 5-10x） |
| 全 8 集 limit=500（13000 req） | 6-15 h（若 5-10x） |

> 如果实测 < 3x：不要铺开，直接用 bf16 回退方案。
