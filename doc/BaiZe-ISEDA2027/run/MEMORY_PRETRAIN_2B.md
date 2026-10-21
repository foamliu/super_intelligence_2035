# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1
> 🆕 **2026-10-22 06:2x #708：🩺 L2 训练健康监控 step 1650/5611（29.4%）**：L2（修双移位+高LR1.67e-3）训练中 PID2754486，8×GPU 100%/51763MiB，loss=1.0104，lr=4.85e-04，~11.94s/step，297.6K tok/s，elapsed 329.5min（5.5h），ETA ~10-22 19:25。step0=1.7138（双移位修复在高LR下仍生效）。0 nan/0 CUDA error（日志顶部仅 1 条 00:51 首启 port29822 EADDRINUSE traceback，重试后即正常，非本轮崩溃）。ckpt step_500+step_1000+step_1500 已存。任务书 mtime 10-21 10:22 未变 ⇒ 无新 pretrain 令。git 0/0。📦 体积：TASK=32725B(31.96K)/MEMORY≈14.1K（均≤32KB）。
> 📦 §#707 流水（2026-10-22 05:5x，L2 健康监控 step 1490）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1490 loss1.02 0error。需要时再读。
> 📦 §#706 流水（2026-10-22 05:4x，L2 健康监控 step 1460 + 短途报告更新）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1460 loss1.11 0error，短途报告+EXPERIMENTS 同步至 step1460。需要时再读。
> 📦 §#705 流水（2026-10-22 05:1x，L2 健康监控 step 1320/5611）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1320 loss1.05 0error。需要时再读。
> 📦 §#704 流水（2026-10-22 04:4x，L2 健康监控 step 1150/5611）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1150 loss1.13 0error。需要时再读。
> 📦 §#703 流水（2026-10-22 04:3x，L2 健康监控 step 1100 + 短途报告更新）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1100 loss1.05 0error，短途报告+EXPERIMENTS 同步至 step1100。需要时再读。
> 📦 §#702 流水（2026-10-22 04:0x，L2 监控 step 970/5611 无新令）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step970 loss1.07 0error。需要时再读。
> 📦 §#700 流水（2026-10-22 03:2x，L2 监控 step740/5611 无新令）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step740 loss1.14 0error，ckpt step_500 已存。需要时再读。
> 📦 §#699 流水（2026-10-22 02:5x，L2 监控 step630/5611 无新令）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step630 loss1.30 0error，ckpt step_500 已存。需要时再读。
> 📦 §#698 流水（2026-10-22 01:1x，L2 监控+短途报告更新）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step370、短途报告补齐 L1 CS8=59.03%+L2 运行中。需要时再读。
> 📦 §#697 流水（2026-10-22 00:5x，L1 CS8 eval=59.03%→L2启动）已归档 → daily-memories/2026-10-22.md；**结论**：L1 CS8=59.03%≥55%门槛→方向正确→L2启动PID2754486 step4/5611 step0=1.71。需要时再读。
> 📦 §#696 流水（2026-10-21 23:5x，L1 训练完成+CS8 eval 启动）已归档 → daily-memories/2026-10-21.md；**结论**：L1 5611步/20B/final loss=0.8687，teardown SIGABRT 无损，CS8 eval 启动。需要时再读。
> 📦 §#677~#695 流水（2026-10-21 16:1x~23:38，19 条 L1 健康监控 step 3330→5570/5611 + 09:3x 报告交付复核）已归档 → daily-memories/2026-10-21.md；**结论**：L1 全程健康 0 error、loss 0.86→0.82 平稳降、ckpt step_500~5500 已存 12 个、09:3x 两份报告在盘已推远端（commit c44ef1fea）。需要时再读。
> 📦 §#669~#676 流水（2026-10-21 12:1x~15:3x，7 条 L1 健康监控 + 报告溯源复核）已归档 → daily-memories/2026-10-21.md；**结论**：L1 全程健康 0 error、loss 平稳降、源数据溯源全通过。需要时再读。

> 📦 §#666~#668 流水（2026-10-21 10:4x~12:0x，3 条「09:3x 两份报告交付复核 + L1 健康监控」心跳 step 1670→2100/5611）已归档 → daily-memories/2026-10-21.md；**结论**：两份中文 HTML 报告 10:50/10:52 交付并推远端（commit c44ef1fea），源数据溯源 spot-check 全通过，L1 全程健康 0 error、loss 0.88→0.91 平稳。需要时再读。

> 📦 §#660~#665 流水（2026-10-21 07:5x~10:1x, 6 条 L1 健康监控心跳 step 820→1560/5611）已归档 → daily-memories/2026-10-21.md；**结论**：L1 全程健康 0 error，loss 1.03→0.90 稳步降，step0 1.75 vs v2 11.72 双移位修复确效，ckpt step_500/1000/1500 已存。需要时再读。
> 📦 §#659 流水（2026-10-21 06:3x, 🩺 L1 step 410/5611 健康 + 后续串行计划/2×2 判读逻辑）已归档 → daily-memories/2026-10-21.md；**结论**：L1 step0 loss=1.76 vs v2 11.72→双移位修复确效、loss 稳步降、串行计划 L1→CS8 eval→L2→L3→2×2 因子定主因定案。需要时再读。
> 📦 §#658 流水（2026-10-21 05:0x, 🚀 L1 训练启动 + 2×2 因子实验设计 + L2/L3 脚本就绪）已归档 → daily-memories/2026-10-21.md；**结论**：L1 烟测通过（step0 loss=1.76 vs v2 11.72→双移位修复确效），全量训练已启动 PID1430363/5611步=20B tok，L2/L3 脚本就绪，CX6 基线崩于 varlen_fwd 兼容性。需要时再读。

> 🆕 **2026-10-21 04:5x #657：🔥 step_532000 基线 eval CS8=61.03% → decay 确认训坏模型 + L1 实验脚本就绪**：用户 02:3x 令授权自主实验。.29 8×GPU 全空确认（ssh hostname=whag0pgpuap29）。烟测通过（XmodelForCausalLM 1.350B params, logits 非 nan, 预测 "Paris" 正确）。14 集基线 eval 在 .29 启动（04:48:07），**CS8 Phase1 已完成**：
> | task | acc | acc_norm | | task | acc | acc_norm |
> | hellaswag | .4396 | **.5895** | | piqa | .7258 | **.7356** |
> | arc_easy | .6915 | **.6641** | | winogrande | **.6101** | — |
> | boolq | **.5924** | — | | openbookqa | .296 | **.394** |
> | arc_challenge | .3524 | **.3865** | | sciq | .934 | **.910** |
> **CS8 = (0.5895+0.6641+0.5924+0.3865+0.910+0.7356+0.6101+0.394)/8 = 61.03%**（acc_norm 优先，与 collect 脚本一致）。
> 🔴 **关键判据**：起点 61.03% ≫ decay v2 final 44.97% → **decay 训坏模型（-16pp）**，问题在 decay 段非起点。Xmodel-2.5 官方 final 65.40% 仅比起点高 4pp → 正确 decay 应微升非暴跌。CX6（Phase2）仍在跑（gsm8k/math500/mmlu/bbh/humaneval/mbpp）。
> **L1 实验脚本已就绪**：`baize_xmodel25_decay_L1.py`（修双移位：chunked CE 去掉 `hidden[:,:-1]`+`labels[:,1:]` 额外移位；non-chunked 传 `input_ids` 作 labels 让 HF 内部单移位）+ `baize_xmodel25_decay_L1.sh`（ITERS=5611=20B tok, LR=5e-4, WARMUP=100, 其余同 v2）。py_compile 通过。待 CX6 完成后启动 L1 训练。📦 体积：TASK=29.8KB / MEMORY=待测（均<32KB）。

> 📦 §#650~#656 流水（2026-10-21 00:2x~03:0x, 7 条稳态心跳「等用户批准跑基线 eval」）已归档 → daily-memories/2026-10-21.md；**结论**：均无新指令，重复确认 .29 GPU 全空、训练完成、起点 ckpt 在盘、等批准。需要时再读。

> 📦 **[已归档] #643~#649 流水（2026-10-20 19:1x~23:4x, 7 条稳态确认 + 归因取证 #648 + 报告重做 #649）→ daily-memories/2026-10-20.md；**结论**：14:2x 评测令已闭环（CS8=44.97%/CX6=6.21%，中文报告 16314B）；#648 归因取证 4 问完成（双移位bug/LR过高/code26epoch/step0=11.72）；#649 报告 v2 重做提交（Xmodel-2.5 final 唯一主对照 + 失败归因节）。需要时再读。**
> 📦 **[已归档] #634~#641 流水（2026-10-20 14:33~18:2x, 评测 decay v2 final 14 集全过程）→ daily-memories/2026-10-20.md；**结论**：14/14 eval 完成 CS8=44.97%(8/8)/CX6=6.21%(6/6)，中文报告 16314B@18:32 + EXPERIMENTS:430「Decay v2 final」+commit `pretrain eval:` e5ecf5d35/3338566a5；含 sdpa 修复、humaneval/mbpp=0.0%、bbh=3.98%。需要时再读。**
>
> 📦 **[已归档] #614 crash→resume 流水（2026-10-20 04:00, .29 主 run 02:45 crash@step19920 NCCL timeout→resume from step_18000, PID1604723, step18020+）→ daily-memories/2026-10-20.md；结论：crash 确认+resume 成功+8×GPU 满载+0error，ETA~10:30。需要时再读。**

- STAGE: **✅ decay v2 根因排查进行中 + 09:3x 报告令已交付** —— v2 训坏模型（CS8 44.97% vs 官方 65.40%）。起点基线 CS8=61.03%。**L1（修双移位+LR5e-4）✅ CS8=59.03%≥55% → 方向正确**；**L2（只修双移位+高LR1.67e-3）训练中 step 1650/5611**；L3（bug+低LR）待启。09:3x 两份中文 HTML 报告已交付。吞吐 297.6K tok/s ⇒ 18.7h/变体，L2 剩 ≈ 13.1h。
  - PHASE: **decay80b_v2_scrootcause_L2（L1 完成 CS8=59.03% / L2 训练中 / L3 待启）** — 2×2 因子：L1(fix+lowLR)=59.03% 基准，L2(fix+highLR) 隔离 LR 贡献，L3(bug+lowLR) 隔离双移位贡献。判定门槛 CS8≥55%（L1 已过 → 方向对）。
  - 轮询状态：**#708（06:2x，L2 健康监控）**：L1 CS8=59.03%（#697）、L2 训练中 step 1650/5611（29.4%）health 0 error。下一步：L2 ~19:25 训完 → CS8 eval(~20min) → L3 → 2×2 因子定主因。任务书 mtime 10:22 未变 ⇒ 无新 pretrain 令（ops RUN_ID 145 是 relay 执行 clone Xmodel-2.5，非 pretrain 任务令）。loop 存活。git 0/0。
> 📦 **[已归档] 🩺 v2 巡检+crash+收尾流水 #610~#634（2026-10-20 01:12~14:33：crash@02:45:25→resume step_18000→P0-a NCCL export+P0-b watchdog 落地→P2 硬件=transient 无永久故障→训练 10:30 收尾 step19979/19980、final ckpt 2.7GB）→ daily-memories/2026-10-20.md；**结论**：v2 全程健康 0error、崩溃前无先兆、硬件瞬时故障无永久隐患。需要时再读。**
> 📦 **[已归档] 🩺 v2 巡检流水 #566~#609（2026-10-19 00:11~23:51, step11904→19050 + hostname/节点澄清 .12→.29）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、ckpt step_12000~step_18000 完好、稳态~12s/step、#588 push 失败由 #589 补推闭环。需要时再读。**
> 📦 **[已归档] v2 巡检+修复流水 #472~#565（2026-10-17 02:16~10-18 23:24, step280→12770 + _orig_mod 修复 + P0 中继恢复 + 误判三连#548/#550/#551 纠偏 + v5 三交付物）→ daily-memories/2026-10-17.md & 2026-10-18.md；**结论**：v2 全程健康 0error、_orig_mod 修复 verify_save@step20 通过、中继恢复、v5 三交付物 committed。需要时再读。**
> 📦 §🗣️ 运维问答·2026-10-09（补测对比报告·先报后跑门控）（P-9.11 baize-vs-dense 公平对比方案，"等运维确认后执行"未执行即被 80B decay v2 方向取代）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：参数匹配 Dense Llama 36L=2.229B(+0.389%)/测试矩阵 ctx×2 until hybrid OOM/mem-frac{0.6,0.85}/WARMUP=1/ETA 6-10h，方案未执行（方向已转 80B decay v2）。需要时再读。

> 📦 **[已归档] 🗣️ 运维问答「提 3 个实验 idea」（2026-10-09, #251 已交付）→ daily-memories/2026-10-09.md；结论：3 idea 按价值排序（①P-8彩排续跑 ②P-8 44B下限档 ③R3配比迁移A/B），建议「立即起P-8」。需要时再读。**

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
- 主训练 10.239.2.29（8×H100 GPU0~7）：P-5b ✅ 已结束；P-9.1~P-9.7 全 ✅ 定稿；P-9.8 ✅ / P-9.9 ✅ / P-9.10 ①②③ ✅ / **P-5b 8-set eval ✅ COMPLETE**（GPU0-1 已释放）；**⭐ 全 8 GPU 空闲**（data agent @08:06 kill S0a → GPU2-7 释放；proxy 标定尚未起跑）；**P-9.11 ① HF 转换 ✅ BOTH DONE**（p3_hybrid→nemotron_h + p3_dense→Llama，待 sglang 起服）。
- watchdog `baize_pretrain_loop.sh` PID 1391466 必须 7×24 存续，🚫 绝不 kill。
- P-9（P-9.1 ✅ / P-9.2 ✅ / P-9.3 ✅ / P-9.4 ✅ / **P-9.5 ✅ COMPLETE** — 崩溃修复 + 5-way 归因 + HTML / P-9.6①② ✅ / P-9.7 ✅ / P-9.8 ✅ COMPLETE → delayed FP8 可用于 P-8 / **P-9.9 ✅ COMPLETE → tensorwise T1/T4 FAIL → P-8 沿用 delayed** / **P-9.10 ① ✅ sglang ✅ 可用(vllm env) [第109次更正] → eager 下界✅已测 + sglang 上界待 HF 转换补测，② ✅ COMPLETE eager 下界 H1✅H2❌H3❌H4✅**）；🚫 不对 live 长跑做 nsys/ncu attach。
