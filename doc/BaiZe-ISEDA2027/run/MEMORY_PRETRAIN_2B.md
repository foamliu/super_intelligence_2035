# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

> 🆕 2026-11-01 10:35 #1064：**S1 健康监控**。git 同步（无 ahead/behind）。S1 PID1415997/.29（torchrun master via ssh→.12，etimes ~79931s ≈ 22.2h）活着，iter 41490/700k（5.93%），loss 近10步 avg~2.122（range 2.111-2.140，稳态），grad-norm 近10步 avg~0.095（range 0.086-0.109，极稳无spike），lr 1e-3 constant，loss-scale 1.0，0 NaN/0 Inf/0 skipped（41490步全clean），step~6.9s/~607K tok/s（160步 in ~18min since #1063），ckpt@iter_40000（next@42000，~510步≈~59min后到达）。双机16×H100 GPU .29 97-100%util×8/~75GB。论文6页/ERR=0 维持。ETA ~52.1天。未完成指令：无。📦 体积：TASK=23.7KB / MEMORY=9.5KB（无归档）。
> 📦 §#1063（11-01 10:15, S1健康监控iter41330/loss~2.12/0NaN/~607K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter41330(5.90%), loss~2.12稳态, grad-norm极稳无spike, ~607K tok/s, ckpt@iter_40000(next@42000)。被#1064监控。需要时再读。
> 📦 §#1062（11-01 09:51, S1健康监控iter41130/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter41130(5.88%), loss~2.13稳态, grad-norm极稳无spike, ~605K tok/s, ckpt@iter_40000(next@42000)。被#1063监控。需要时再读。
> 📦 §#1060（11-01 09:14, S1健康监控iter40811/loss~2.12/0NaN/~603K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter40811(5.83%), loss~2.12稳态, grad-norm minor spike@40806已恢复, ~603K tok/s, ckpt@iter_40000(next@42000)。被#1061监控。需要时再读。
> 📦 §#1059（11-01 08:52, S1健康监控iter40624/loss~2.13/0NaN/~606K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter40624(5.80%), loss~2.13稳态, grad-norm极稳无spike, ~606K tok/s, ckpt@iter_40000(next@42000)。被#1060监控。需要时再读。
> 📦 §#1058（11-01 08:28, S1健康监控iter40432/loss~2.14/0NaN/~631K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter40432(5.78%), loss~2.14稳态, grad-norm极稳无spike, ~631K tok/s, ckpt@iter_40000(next@42000)。被#1059监控。需要时再读。
> 📦 §#1057（11-01 08:15, S1健康监控iter40258/loss~2.14/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter40258(5.75%), loss~2.14稳态, grad-norm极稳无spike, ~605K tok/s, ckpt@iter_40000(next@42000)。被#1058监控。需要时再读。
> 📦 §#1056（11-01 07:50, S1健康监控iter40087/loss~2.14/0NaN/~615K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter40087(5.73%), loss~2.14稳态, grad-norm极稳无spike, ~615K tok/s, ckpt@iter_40000(next@42000)。被#1057监控。需要时再读。
> 📦 §#1055（11-01 07:30, S1健康监控iter39911/loss~2.16/0NaN/~550K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter39911(5.70%), loss~2.16稳态, grad-norm spike@39803已恢复, ~550K tok/s(本区间偏低), ckpt@iter_38000(next@40000已存)。被#1056监控。需要时再读。
> 📦 §#1054（11-01 07:08, S1健康监控iter39738/loss~2.14/0NaN/~621K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter39738(5.68%), loss~2.14稳态, grad-norm极稳无spike, ~621K tok/s, ckpt@iter_38000(next@40000)。被#1055监控。需要时再读。
> 📦 §#1053（11-01 06:49, S1健康监控iter39569/loss~2.16/0NaN/~609K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter39569(5.65%), loss~2.16稳态, grad-norm极稳, ~609K tok/s, ckpt@iter_38000(next@40000)。被#1054监控。需要时再读。
> 📦 §#1052（11-01 06:32, S1健康监控iter39404/loss~2.15/0NaN/~608K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter39404(5.63%), loss~2.15稳态, grad-norm极稳, ~608K tok/s, ckpt@iter_38000(next@40000)。被#1053监控。需要时再读。
> 📦 §#1051（11-01 06:12, S1健康监控iter39240/loss~2.15/0NaN/~608K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter39240(5.60%), loss~2.15稳态, grad-norm极稳, ~608K tok/s, ckpt@iter_38000(next@40000)。被#1052监控。需要时再读。
> 📦 §#1050（11-01 05:50, S1健康监控iter39066/loss~2.15/0NaN/~611K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter39066(5.58%), loss~2.15稳态, grad-norm极稳, ~611K tok/s, ckpt@iter_38000(next@40000)。被#1051监控。需要时再读。
> 📦 §#1049（11-01 05:30, S1健康监控iter38880/loss~2.15/0NaN/~608K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter38880(5.55%), loss~2.15稳态, grad-norm spike@38830已恢复, ~608K tok/s, ckpt@iter_38000(next@40000)。被#1050监控。需要时再读。
> 📦 §#1048（11-01 05:15, S1健康监控iter38729/loss~2.13/0NaN/~608K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter38729(5.53%), loss~2.13稳态, grad-norm极稳无spike, ~608K tok/s, ckpt@iter_38000(next@40000)。被#1049监控。需要时再读。
> 📦 §#1047（11-01 04:54, S1健康监控iter38550/loss~2.15/0NaN/~608K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter38550(5.51%), loss~2.15稳态, grad-norm正常波动(0.212 minor spike已恢复), ~608K tok/s, ckpt@iter_38000(next@40000)。被#1048监控。需要时再读。
> 📦 §#1046（11-01 04:34, S1健康监控iter38390/loss~2.14/0NaN/~608K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter38390(5.48%), loss~2.14稳态, grad-norm正常波动(0.656 spike已恢复), ~608K tok/s, ckpt@iter_38000(next@40000)。被#1047监控。需要时再读。
> 📦 §#1045（11-01 04:15, S1健康监控iter38227/loss~2.14/0NaN/~566K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter38227(5.46%), loss~2.14稳态, grad-norm极稳, ~566K tok/s, ckpt@iter_38000(next@40000)。被#1046监控。需要时再读。
> 📦 §#1044（11-01 03:53, S1健康监控iter38057/loss~2.15/0NaN/~596K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter38057(5.44%), loss~2.15稳态, grad-norm极稳, ~596K tok/s, ckpt@iter_38000(next@40000)。被#1045监控。需要时再读。
> 📦 §#1043及更早流水（11-01 03:45前, iter≤37873, 含S1监控链#1039~#1043、10-31监控链#984~#1009、10-24~10-26吞吐调优/RoPE修复/CUDA-Graph根因、10-20~10-23 decay训练/评测/L1L2监控、10-17~10-19 v2巡检、10-09实验idea）均已归档 → daily-memories/2026-{10-09..11-01}.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip；吞吐305K上限确认；decay 5000步CS8=58.97%；论文6页ERR=0；baize-llm项目目录就绪。需要时再读各日 daily 文件。

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)+已杀的#550 resume 日志(止于 step8070@17:17 SIGTERM)，**误判主 run 已死** ⇒ 这正是 #548/#550 两起误判的根因。SSH 已验证可用。判活三件套只在 .29 上有效；.29 的 `/tmp` log 才是主 run 实时日志（NFS `$OUTPUT_DIR/...train.log` 是 .12 旧日志，亦不可作判据，见 16:4x）。
- transformer_engine 2.12.0+5671fd36 / torch 2.8.0+cu128 / CUDA 12.8 / megatron-core 0.16.1 / mamba-ssm 2.2.6.post3（P-9.4 已核实，与任务书预期一致）。
- 结果主文件：R2=`EXPERIMENTS_PRETRAIN_2B_ROUND2.md`；Round1=`EXPERIMENTS_PRETRAIN_2B.md` + `BAIZE_PRETRAIN_RESULT.html` + `ISEDA2027/4_llm_pretrain.tex`。
- ckpt：p3_hybrid/iter_0005000 → **HF nemotron_h ✅**（`nemo_experiments/p3_hybrid/hf_iter_5000/`，323 keys, 2.220B）+ p3_dense/iter_0005000 → **HF Llama ✅**（`nemo_experiments/p3_dense/hf_iter_5000/`，381 keys, 2.512B）；原始 mcore distcp @ `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/`。

## GPU / 进程
- **S1 全量预训练运行中** 10.239.2.29 + .12 双机 16×H100：iter 41490/700k(5.93%), loss~2.12, 0NaN, ~607K tok/s, ckpt@iter_40000(next@42000)。GPU .29 97-100%util×8/~75GB/卡。
- S1 日志：.29 `/tmp/baize_s1_baize2b_worker.log`（实时训练进度，每10步一行）+ `/tmp/baize_s1_baize2b_master.log`。
- watchdog `baize_pretrain_loop.sh` 必须 7×24 存续，🚫 绝不 kill。
- P-9 系列实验全部 ✅ 完成（P-9.1~P-9.11）；R2 P-1~P-8 全部 ✅ 完成；论文 6 页 ERR=0。