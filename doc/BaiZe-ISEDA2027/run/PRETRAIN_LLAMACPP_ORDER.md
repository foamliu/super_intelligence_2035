# PRETRAIN_LLAMACPP_ORDER.md — 用户令（2026-11-03 22:0x）：用 llama.cpp 加速 CPU 评测（pilot）

> 下发对象：pretrain 线（.29 / .12）。
> 背景：当前 CPU 评测走 PyTorch 参考实现，bf16 **15.3–17.6 s/req**，float32 **30+ s/req**；
> 5 ckpt × 8 集（limit=100）最坏要到 11-04 13:24，离 deadline 仅 ~1.5h。
> 试运行资产已入库（commit `2906b2b3c`）：`run/pretrain_cpu_eval_gguf/`。
> 本令只做**等价性 pilot**，不改变任何现有评测口径；是否全量切换由用户在看结果后决定。

## 0. 硬约束（违反任何一条即停）

1. **不碰 GPU / S1 训练**：禁止起任何 GPU 进程、禁止 `pkill python`、禁止动 `/tmp/baize_s1_baize2b_*` 崩溃日志。
2. **不动现有 3 个 HF 评测**（iter_50000 / iter_30000-暂停 / .12 双 float32）：不 kill、不 SIGSTOP、不重启。
3. CPU 负载：`nice -n 19`，llama-server `-t 16`，`OMP_NUM_THREADS=1`；两机 load 目前 ~15%，可承受。
4. 结果 JSON 一律不入库（`lm_eval_results/` 已在远端机器，不入 git）。
5. 先在 **.29** 完成 pilot；**不要**在 .12 上另建一份共享目录的 build（`GGML_NATIVE=ON` 的二进制跨机可能 SIGILL）。
6. 失败如实报，禁止编造 tok/s、Δpp 或“已切换”。

## 1. 编译（.29，约 5–10 分钟）

```bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027
bash run/pretrain_cpu_eval_gguf/00_build_llamacpp.sh
```

- 默认 `LLAMA_DIR=/nas_train/app.e0031982/tools/llama.cpp`（仓库外），走 proxy `172.19.92.23:13128`。
- 若 GitHub 不通：如实报 `curl -I https://github.com` 的 http_code，不要反复重试。
- 记录：`llama-server --version`、`lscpu` 型号、`nproc`、`free -g`。

## 2. 转换 iter_10000（约 3–6 分钟，F16）

```bash
bash run/pretrain_cpu_eval_gguf/01_convert_hf_to_gguf.sh \
  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_10000 \
  /nas_train/app.e0031982/models/baize2b_gguf/bz2b-10000-f16.gguf f16
```

- 脚本先自检 `model_type=nemotron_h` 与 `hybrid_override_pattern`，再转 F16（**不要用量化做第一步**）。
- 记录 GGUF 大小；若转换报 unsupported architecture：立即停，抄完整报错进报告。

## 3. 一键评测（转换 + 起服 + 自检 + 评分 + 收服）

```bash
bash run/pretrain_cpu_eval_gguf/04_run_one_ckpt.sh 10000 \
  --limit 100 --tasks sciq,piqa --port 8080 --threads 16 --parallel 2
```

内部顺序（任一失败即退出，不会产生脏结果）：
1. `06_server_selftest.py`：验证 `/tokenize`、`prompt=[token ids]`、`logit_bias`、`n_probs` 四个契约；
2. `02_check_tokenizer.py`：GGUF vs HF 分词**逐 id 对拍**（12 条中英/代码样例）；
3. `gguf_lmeval_run.py`：lm_eval `simple_evaluate`，结果写
   `nemo_experiments/baize2b/lm_eval_results/gguf_iter_10000/{results.json,meta.json}`。

> 若第 1 步报 `prompt` 类型错误：**停**，把完整响应体写进报告（说明这版 llama.cpp 不支持 token-id prompt，需要改字符串方案）。

## 4. 等价性判定

```bash
python3 run/pretrain_cpu_eval_gguf/05_compare_with_hf.py 10000
```

判据（全部满足才 PASS）：
- `max|Δacc| <= 1.0pp` 且 `Avg|Δ| <= 1.0pp`（对比对象：`hf_iter_10000/results.json`，同为 limit=100）；
- 加速 `>= 5x`；
- `meta.json` 里 `s_per_token_request` 与 `elapsed_sec` 合理（无异常重试）。

## 5. 交付（无论成败）

1. 中文 HTML 报告：`reports/report_pretrain_llamacpp_pilot_zh.html`（单文件自包含，0 script / 0 CDN / 0 外链）。必含：
   环境与版本、模型/GGUF 路径与大小、四个契约自检结果、分词对拍结果、逐任务 acc/Δpp、Avg、速度（s/req、总时长、加速比）、失败项与原因、是否建议全量。
2. `run/MEMORY_PRETRAIN_2B.md` 顶部加 1 条状态（含结论与路径），并写当日 daily。
3. commit 前缀 `pretrain llamacpp:` + push。

## 6. 后续（PASS 后**先报告再等令**，不要擅自切换）

- 若 PASS 且用户批准切换：建议 **5 个 ckpt 全部用 GGUF（F16）重跑**，避免 HF/GGUF 混画曲线；
  先 `--limit 100` 复现 5 点，再视速度决定是否把 limit 提到 300/500。
- 若 FAIL：保留现有 HF 路线；可另报“`.12` float32 → bf16”的应急收益（约 2x），但**重启评测需用户批准**。
- 不要在 .12 上重复编译共享目录；如需 .12 本地跑，用
  `LLAMA_DIR=$HOME/tools/llama.cpp_12 bash run/pretrain_cpu_eval_gguf/00_build_llamacpp.sh` 独立编译。
