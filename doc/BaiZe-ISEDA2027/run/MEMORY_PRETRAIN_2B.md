# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

> 🆕 **2026-10-21 07:5x #660：🩺 L1 训练健康监控 step 820/5611 loss=1.03 + ckpt step_500 已存盘**：L1（.29 ssh, PID 1430363 torchrun, hostname=whag0pgpuap29）step **820/5611**（14.6%），loss=**1.0258**（step0=1.7510→step820≈1.0 稳步下降），lr=2.65e-04（warmup 100 完成、decay 中），296.5K tok/s，~12s/step，elapsed 164.4min，**0 error/OOM/traceback**（grep 仅 5 行 NCCL_ASYNC_ERROR_HANDLING 弃用 warning，无害）。GPU 8×100%/51763MiB 全满载。**ckpt step_500 已存盘**（`xmodel25_baize_L1_20b/step_500/model.safetensors` 2.7GB@06:45）+ verify_save_20 在位。**双移位修复再确认**：step0 loss=1.7510（正常）vs v2 step0 loss=11.72（随机/训坏）→ 修复有效。**ETA**：剩余 4791 步×12s≈16h → L1 预计 **10/22 ~00:00** 完成。**后续串行计划不变**（8 GPU 单线）：L1 完成→CS8 eval(~20min)→若≥55%启 L2→eval→L3→eval→2×2 因子分析。ops inbox 空 + .last_run_id 缺失=无新令。git origin/main...main=0/0。📦 体积：TASK=29.8KB / MEMORY=27.7KB（均<32KB，无需归档）。

> 🆕 **2026-10-21 06:3x #659：🩺 L1 训练健康监控 step 410/5611 loss=0.93 + 后续实验串行计划**：
> **L1 健康确认**（.29 ssh, PID 1430363 torchrun）：step **410/5611**（7.3%），loss=**0.9289**（step0=1.76→step410=0.93 稳步下降），lr=3.80e-04（warmup 100 完成，decay 中），295K tok/s，~12s/step，0 error/OOM/traceback。GPU 8×~50GB/100%（GPU1 偶见 0% 为 data load 间隙，正常）。
> **Loss 轨迹对比**：v2 step0 loss=11.72（=随机，双移位 bug 破坏学习）→ L1 step0 loss=1.76（正常，修复后模型正确学习）→ **双移位修复确认有效**。loss 100→410 步从 ~1.7 降至 ~0.93，decay 轨迹健康。
> **ETA**：剩余 5201 步 × 12s = ~17.3h → L1 预计 **10/22 ~00:00** 完成。ckpt save_interval=500（step_500 即将存盘）。输出 `xmodel25_baize_L1_20b/`，HF safetensors 格式，与 `baize_xmodel_eval.sh` 兼容。
> **后续串行计划**（8 GPU 单线，L1 占满无法并行）：① L1 完成 → 跑 CS8 eval（~20min）② 若 CS8≥55% → 启动 L2（fix+highLR 1.67e-3, ~19h）③ L2 完成 → eval CS8 ④ 启动 L3（bug+lowLR 5e-4, ~19h）⑤ eval CS8 ⑥ 2×2 因子分析：L1/L2/L3/v2 四格定主因。
> **2×2 判读逻辑**：L1≥55%→方向对；L2≈v2(44%)→LR 是主因；L3≈v2→双移位是主因；L1/L2 都好→双移位是主因（LR 次要）；L1/L3 都好→LR 是主因。
> ops inbox 无新指令（.last_run_id 缺失=无 ops 中继或无新令）。git origin/main...main=0/0。📦 体积：TASK=30.6KB / MEMORY=26.8KB（均<32KB）。
> 🆕 **2026-10-21 05:0x #658：🚀 L1 训练已启动（.29, 8×H100）+ 2×2 因子实验设计 + L2/L3 脚本就绪**：
> **L1 烟测通过**（100 步）：step 0 loss=**1.7574**（vs v2 step 0 loss=11.72=random）→ **双移位修复确认有效**。loss 稳定 1.70~1.78，LR warmup 正确（0→5e-4/100步），吞吐 80K→195K tok/s（compile warmup 中）。
> **L1 全量训练已启动**（05:04:52, PID 1430363 torchrun）：5611 步=20B tok, LR=5e-4→1e-5, 输出 `xmodel25_baize_L1_20b/`。step 0 loss=1.7510 ✓。~12s/step → 预计 ~19h 完成（step 5611 ≈ 10/22 00:00）。
> **2×2 因子实验设计**（每格 20B tok, 5611 步, ~19h/实验）：
> | | LR 5e-4（低） | LR 1.67e-3（高=v2） |
> |---|---|---|
> | **修复双移位** | **L1** ✅运行中 | **L2** 脚本就绪 |
> | **保留双移位 bug** | **L3** 脚本就绪 | **v2** 已完成（CS8=44.97%） |
> - L2 = 修复双移位 + 高 LR → 隔离双移位修复效果（若 L2 仍 ~60%+ → 双移位是主因）
> - L3 = 保留 bug + 低 LR → 隔离 LR 效果（若 L3 仍崩 → 双移位是主因）
> - L2 脚本 `baize_xmodel25_decay_L2.sh`（用 L1.py+LR=1.67e-3）；L3 脚本 `baize_xmodel25_decay_L3.sh`（用 v2.py+LR=5e-4）
> **CX6 基线失败原因**：bbh/gsm8k/math500 崩于 `TypeError: varlen_fwd()` （flash attention generation 兼容性问题）；humaneval/mbpp 需 `confirm_run_unsafe_code=True`。仅 mmlu 能跑但被 kill 以释放 GPU 给 L1。CS8=61.03% 已是关键判据，CX6 可后续补跑。
> 📦 体积：TASK=29.8KB / MEMORY=待测（均<32KB）。

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

> 🆕 **2026-10-21 01:0x #651：🩺 稳态确认 + 心跳（无新令，21:5x 归因令 ①②③ 已闭环，仍等 step_532000 基线 eval 批准）**：唤醒复核——ops `.last_run_id=140`（=inbox 首个块 `<!-- RUN_ID: 140 -->` = 21:5x 归因令，已在 #648 取证 + #649 报告重做全部交付）、inbox mtime 10-20 21:12 未变 ⇒ **无新 pretrain 指令**。训练终态(.29 ssh, hostname=whag0pgpuap29)：8×GPU 0%/0MiB 全空、无 torchrun（训练已完成、eval 已释放）。**唯一待办**：step_532000 起点基线 eval —— 起点 ckpt 在盘 `xmodel25_history/step_532000/pytorch_model.bin`(2.7GB@10-16 14:50，注意是 .bin 非 safetensors)，⏸等用户批准。loop PID1294147 存活。git origin/main...main=0/0。🚫 未跑 eval/未重训/未改报告/未碰他线。📦 体积：TASK=26.1KB / MEMORY≈28.9KB（归档 ~3.8KB → daily-2026-10-20.md）。
> 🆕 **2026-10-21 00:2x #650：🩺 稳态确认 + 心跳（无新令，21:5x 归因令 ①②③ 已闭环，仍等 step_532000 基线 eval 批准）**：唤醒复核——ops `.last_run_id=140`（=inbox RUN_ID 140 = 21:5x「decay v2 vs Xmodel-2.5 final 归因前置取证」令，已在 #648 取证 + #649 报告重做全部交付）、inbox mtime 10-20 21:12 未变 ⇒ **无新 pretrain 指令**。21:5x 令交付状态：①正确对照口径铁定 ② 4 问取证完成（#648：71.2B final✅ / step_532000 无 eval / code≈26epoch / peak LR 1.67e-3 过高 / 🔴双移位bug）③ 报告 v2 已重做提交（#649, 21092B）。**唯一待办**：step_532000 基线 eval —— 起点 ckpt 已确认在盘 `xmodel25_history/step_532000`（可跑，⏸需用户批准）。训练终态(.29 ssh, hostname=whag0pgpuap29)：8×GPU 0MiB/0% 全空、无 torchrun（eval 已释放）。loop 存活 PID1294147。git origin/main...main=0/0。🚫 未跑 eval/未重训/未改报告/未碰他线。📦 体积：TASK=26.1KB/MEMORY≈31KB。
> 🆕 **2026-10-20 23:4x #649：📝 报告重做完成 + #648 笔误更正（21:5x 令 ③交付）**：21:5x 令第三阶段（取证齐全后改报告）——`reports/report_pretrain_decay_v2_final_eval_zh.html` **v2 已重做并提交（21092B）**：Xmodel-2.5 final 提为唯一主对照（§3，CS8 -20.43pp / CX6 -26.69pp）、改正 ~80B→71.2B、加「§4 失败归因」5 小节（双移位bug/LR过高/code过采样/loss异常/基线缺失）、P-8 降为§5旁注。**更正#648两处笔误**（经源文件复核）：①code 实测 **0.270B/≈26 epochs**（非0.17B/41；.bin=345M+687M→258M tok）；②架构为 **1.3B Dense Transformer**（非2.22B Mamba2-hybrid；config.json=48L/1536h/24heads/8KV/3840int/vocab129280）。双移位bug经 py:547-548+567-568+代码注释"double-shifts"三方确认✅。EXPERIMENTS:430 已同步更正。⏸ **仍等用户批准**：在.29跑 step_532000 基线 eval（~1h）→终判"decay训坏"还是"起点/加载问题"。🚫 未重训/未改配方/未跑eval/未碰他线。📦体积：TASK=26.1KB / MEMORY≈30KB。

> 🆕 **2026-10-20 22:2x #648：🔬 decay v2 对照口径纠错 + 差 20pp 归因取证实测（21:5x 令）**：运维令21:5x——正确对照=Xmodel-2.5 final（非P-8），差20pp属「decay没练出来」。**只读取证完成（不写报告），4问+1额外发现**：①Q1 final=71.2B(19980步×960×3712)✅，但**step 0 loss=11.72(≈随机)**→50步内降回~2.0，权重大概率正确被扰动(compile/double-shift/distribution-shift)；②Q2 **step_532000无eval**，历史step_2000=0.4612/step_4000=0.4911/xmodel25_final=0.6540，**我方0.4497比step_4000还低**→⏸需用户批准跑step_532000基线eval；③Q3 **code 41 epoch**🔴(0.17B看41遍,计划标23.7)、math 4.9epoch正常；④Q4 **peak LR 1.67e-3过高**🔴(6-17×典型decay LR)；🔴额外发现**双移位bug**——训练脚本预移位+HF forward内部再移位=2-step预测，eval做1-step→train/eval不匹配→全14集退化（代码注释已承认"double-shifts"）。归因排序：1.双移位bug 2.LR过高 3.code过采样 4.loss异常 5.基线缺失。等用户批准：①跑step_532000 eval ②重做报告。git=0/0。📦体积：TASK=26.1KB/MEMORY≈30KB。

> 🆕 **2026-10-20 21:0x #647：🩺 稳态确认 + 心跳（无新令，14:2x 评测令 + 06:1x 事故复盘令均已闭环）**：唤醒复核——两项运维令均已全部交付：①14:2x 评测令(#635~#642)：CS8=44.97%/CX6=6.21%，中文报告`reports/report_pretrain_decay_v2_final_eval_zh.html`(16314B@18:32)+EXPERIMENTS:430「Decay v2 final」+commit`pretrain eval:`e5ecf5d35/3338566a5；②06:1x 事故复盘令(#617~#626)：报告`reports/report_pretrain_crash_20261020_zh.html`(15135B@06:06)+P0-a(.sh NCCL export 3行,commit 88d2377b7)+P0-b(watchdog 5166B,未常驻)+P2硬件正式回填(#626@10:31:transient一次性,无Xid/ECC/Retired/Remapped,dmesg干净,8×H100健康,无blocker)。ops .last_run_id=139=inbox RUN_ID=139(中继健康诊断,非pretrain指令)/inbox mtime 10-18 20:30未变⇒无新pretrain指令。训练终态(SSH .29,hostname=whag0pgpuap29)：8×GPU 0%/0MiB全空、温度25-28°C、throttle=0x1(idle)、ECC N/A、无torchrun(eval已释放)。本机=.12(hostname=whag0pgpuap12)本地GPU=vision ArmD训练(8×~50GB/96-100%),非pretrain(避#548/#550误判)。git origin/main...main=0/0。📦 体积：TASK=23.6KB / MEMORY=28.5KB（均<32KB）。

> 🆕 **2026-10-20 20:5x #646：🩺 稳态确认 + 心跳（无新令，14:2x 评测令已闭环）**：唤醒复核——任务书 14:2x 评测令已在 #635~#642 全部交付（CS8=44.97%/CX6=6.21%，中文报告 16314B@18:32 + EXPERIMENTS:430「Decay v2 final」，commit `pretrain eval:` e5ecf5d35/3338566a5）。ops .last_run_id=139 / inbox.md mtime 10-18 20:30 未变 ⇒ 无新 pretrain 指令。训练终态(.29 本地，hostname=whag0pgpuap29)：8×GPU 0%/0MiB 全空、无 torchrun/decay 进程（eval 已释放）。交付物复核：report `doc/BaiZe-ISEDA2027/reports/report_pretrain_decay_v2_final_eval_zh.html` 16314B@18:32✓ + EXPERIMENTS_PRETRAIN_2B.md:430✓；数字溯源 eval_summary.txt（CS Avg 0.4497 / CX Avg 0.0621，14/14 齐）✓。git origin/main...main=0/0。本轮零写训练侧：仅稳态复核+心跳+日报。🚫 未重启/kill/改配方/动他线/启动watchdog/改报告。📦 体积：TASK=23.6KB / MEMORY=26.4KB（均<32KB）。
> 🆕 **2026-10-20 20:2x #645：🩺 稳态确认 + 心跳（无新令，14:2x 评测令已闭环）**：唤醒复核——任务书 14:2x 评测令已在 #635~#642 全部交付（CS8=44.97%/CX6=6.21%，中文报告 16314B + EXPERIMENTS:430「Decay v2 final」，commit `pretrain eval:` e5ecf5d35/3338566a5）。ops .last_run_id=139 / inbox.md mtime 10-18 20:30 未变 ⇒ 无新 pretrain 指令。训练终态(.29 本地，hostname=whag0pgpuap29)：8×GPU 0%/0MiB 全空、无 torchrun/decay 进程（eval 已释放）。交付物复核：report `doc/BaiZe-ISEDA2027/reports/report_pretrain_decay_v2_final_eval_zh.html` 16314B@18:32✓ + EXPERIMENTS_PRETRAIN_2B.md:430✓；数字溯源 eval_summary.txt（CS Avg 0.4497 / CX Avg 0.0621）✓。git origin/main...main=0/0。本轮零写训练侧：仅稳态复核+心跳+日报。🚫 未重启/kill/改配方/动他线/启动watchdog/改报告。📦 体积：TASK=23.6KB / MEMORY=25.4KB（均<32KB）。
> 🆕 **2026-10-20 19:4x #644：🩺 稳态确认 + 心跳（无新令，14:2x 评测令已闭环）**：唤醒复核——任务书 14:2x 评测令已在 #635~#642 全部交付（CS8=44.97%/CX6=6.21%，中文报告 16314B + EXPERIMENTS:430「Decay v2 final」，commit `pretrain eval:` e5ecf5d35/3338566a5）。ops .last_run_id=139 / inbox.md mtime 10-18 20:30 未变 ⇒ 无新 pretrain 指令。训练终态(.29 本地，hostname=whag0pgpuap29)：8×GPU 0%/0MiB 全空、无 torchrun/decay 进程（eval 已释放）。交付物复核：report `doc/BaiZe-ISEDA2027/reports/report_pretrain_decay_v2_final_eval_zh.html` 16314B✓（数字 CS8=44.97%/CX6=6.21% vs P-8 49.21%/6.81%）+ EXPERIMENTS_PRETRAIN_2B.md:430✓。git origin/main...main=0/0。本轮零写训练侧：仅稳态复核+心跳+日报。🚫 未重启/kill/改配方/动他线/启动watchdog/改报告。📦 体积：TASK=23.6KB / MEMORY=24.5KB（均<32KB）。
> 🆕 **2026-10-20 19:1x #643：🩺 稳态确认 + 心跳（无新令，评测令已闭环）**：唤醒复核——任务书 14:2x 评测令已在 #635~#642 全部交付（CS8=44.97%/CX6=6.21%，中文报告 16314B + EXPERIMENTS 「Decay v2 final」一节，commit `pretrain eval:` e5ecf5d35/3338566a5）。ops .last_run_id=139 / inbox.md mtime 10-18 20:30 未变 ⇒ 无新 pretrain 指令。训练终态(.29 本地，hostname=whag0pgpuap29)：8×GPU 0%/0MiB 全空、无 torchrun（eval 已释放）。交付物复核：报告 `reports/report_pretrain_decay_v2_final_eval_zh.html` 16314B@18:32✓、EXPERIMENTS_PRETRAIN_2B.md:430 「Decay v2 final」✓。git origin/main...main=0/0。本轮零写训练侧：仅稳态复核+心跳+日报。🚫 未重启/kill/改配方/动他线/启动watchdog/改报告。📦 体积：TASK=23.6KB / MEMORY=23.7KB（均<32KB）。
> 📦 **[已归档] #634~#641 流水（2026-10-20 14:33~18:2x, 评测 decay v2 final 14 集全过程）→ daily-memories/2026-10-20.md；**结论**：14/14 eval 完成 CS8=44.97%(8/8)/CX6=6.21%(6/6)，中文报告 16314B@18:32 + EXPERIMENTS:430「Decay v2 final」+commit `pretrain eval:` e5ecf5d35/3338566a5；含 sdpa 修复、humaneval/mbpp=0.0%、bbh=3.98%。需要时再读。**
>
> 📦 **[已归档] #614 crash→resume 流水（2026-10-20 04:00, .29 主 run 02:45 crash@step19920 NCCL timeout→resume from step_18000, PID1604723, step18020+）→ daily-memories/2026-10-20.md；结论：crash 确认+resume 成功+8×GPU 满载+0error，ETA~10:30。需要时再读。**

- STAGE: **✅ Xmodel-2.5 80B decay v2 COMPLETE @.29（step 19979/19980, final ckpt 已保存）**——02:45 crash@step19920→03:55:29 resume from step_18000→10:30 收尾 step19979 + final ckpt。torchrun PID1604723 收尾中。①②③ 全部闭合：报告核对一致、P0 已落地(commit 88d2377b7)、P2 正式判 transient（无永久故障）。
  - PHASE: **decay80b_v2_eval_14set_DONE（converged）** — 14:2x 评测令已全部交付（#635~#641）：final 14 集 lm-eval 完成，**CS8=44.97%(8/8) / CX6=6.21%(6/6)**，中文报告 `reports/report_pretrain_decay_v2_final_eval_zh.html` + EXPERIMENTS "Decay v2 final" 一节已 committed（`pretrain eval:` e5ecf5d35）。.29 8 卡已释放、等运维新指令。原 run 02:45 crash@step19920（NCCL transient）→resume→10:30 收尾；P2=transient；①②③ 闭环；P0-a/P0-b 已落地。
  - 轮询状态：**#655（02:3x，稳态确认，无新令）**：21:5x 归因令已全部交付（#648 取证 + #649 报告重做 21092B）；ops .last_run_id=140、inbox mtime 10-20 21:12 未变 ⇒ 无新指令。唯一待办 step_532000 基线 eval（起点 ckpt 在盘 nemo_experiments/xmodel25_history/step_532000/pytorch_model.bin 2.70GB@10-16，⏸等用户批准）。.29 8 卡全空、loop PID1294147 存活、报告 v2 复核通过（§3 主对照/§4 归因/§5 旁注）。git origin/main...main=0/0。
  > 📦 **[已归档] #630~#634 流水（2026-10-20 12:54~14:33, 5 轮稳态确认+心跳 .29/.12 零写训练侧）→ daily-memories/2026-10-20.md；**结论**：①②③（06:1x 事故复盘令）均闭合、P0-a .sh 66-69 NCCL export✓、P0-b watchdog 5166B 未常驻✓、报告 15135B@06:06 未改✓、P2=transient 无永久故障、训练终态 step19979/19980 + final ckpt 2.7GB@10:30。需要时再读。**
  > 📦 **[已归档] #617~#629 流水（2026-10-20 06:3x~12:21, crash 复盘核实+P0 两项落地+P2 硬件回填+多轮稳态巡检）→ daily-memories/2026-10-20.md；**结论**：报告 6 项事实一致（2 处小差异已记）；P0-a .sh 66-69 NCCL export+P0-b watchdog 4583→5166B 已入 commit 88d2377b7；P2=transient（无 Xid/ECC/Retired/dmesg 异常）；训练 10:30 收尾 step19979/19980。需要时再读。**

  > 📦 **[已归档] #614~#616 流水（2026-10-20 04:00~06:00, 🔧 crash→resume + 🩺 v2 巡检 step18020→18630）→ daily-memories/2026-10-20.md；**结论**：crash@02:45:25 确认+resume step_18000 成功 PID1604723+8×GPU 满载+0error+稳态~12s/step，ETA~10:30。需要时再读。**
  > 📦 **[已归档] #612~#613 流水（2026-10-20 01:12~02:27, 🩺 v2 巡检 step19460→19830, 崩溃前最后两次健康巡检）→ daily-memories/2026-10-20.md；**结论**：v2 全程健康 0error、step_18000 ckpt 2.7GB 完好、稳态~12s/step；崩溃@02:45:25 前无先兆。需要时再读。**
  > 📦 **[已归档] #605~#611 流水（2026-10-19 17:41~23:51, 🩺 v2 巡检 step17190→19050）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、step_16000/18000 ckpt 2.7GB 完好、稳态~11.9-12.3s/step；保留最近 #612+。需要时再读。**
  > 📦 **[已归档] #599~#604 流水（2026-10-19 14:14~17:38, 🩺 v2 巡检 step16150→17170）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、step_16000 ckpt 2.7GB 完好、稳态~11.9s/step；保留最近 #605+。需要时再读。**
  > 📦 **[已归档] #596~#598 流水（2026-10-19 13:06~13:54, 🩺 v2 巡检 step15810→16050）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、step_16000 ckpt 2.7GB 完好、稳态~11.2-12s/step；保留最近 #599+。需要时再读。**
> 📦 **[已归档] #589~#595 流水（2026-10-19 09:51~12:35, 🩺 v2 巡检 step14830→15650）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、step_14000 ckpt 2.7GB 完好、#589 补推闭环；保留最近 #596+。需要时再读。**
  > 📦 **[已归档] #586~#588 流水（2026-10-19 08:31~09:29, 🩺 v2 巡检 step14420→14710 + #588 push 失败 ahead1）→ daily-memories/2026-10-19.md（#586@368/#587@382/#588@405 已存原文）；**结论**：v2 全程健康 0error、step_14000 ckpt 2.7GB 完好、#588 push 失败由 #589 补推闭环；保留最近 #589+。需要时再读。**
  > 📦 **[已归档] #582~#585 流水（2026-10-19 06:31~07:42, 🩺 v2 巡检 step13830→14170）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、step_14000 ckpt 2.7GB 完好、稳态~11.9s/step；保留最近 #586+。需要时再读。**
  > 📦 **[已归档] #579~#581 流水（2026-10-19 05:21~05:58, 🩺 v2 巡检 step13470→13650）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、step_12000 ckpt 2.7GB 完好、稳态~11.9s/step；保留最近 #582+。需要时再读。**
  > 📦 **[已归档] #572~#578 流水（2026-10-19 02:29~04:49, 🩺 v2 巡检 step12600→13300）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、step_12000 ckpt 2.7GB 完好、稳态~12s/step、0 真实错误；保留最近 #579+。需要时再读。**
> 📦 **[已归档] #570~#571 流水（2026-10-19 01:56~02:03, 🩺 v2 巡检 step12430→12470 + hostname/节点澄清 .12→.29）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、step_12000 ckpt 2.7GB 完好、#571 澄清 #554~#570「在.29直查」实为 .12 NFS 只读误标（此后 #572+ 均为 .29 本地直查）；下一 ckpt@step_14000 ~07:0x。需要时再读。**
> 📦 **[已归档] #566~#569 流水（2026-10-19 00:11~01:21, 🩺 v2 巡检 step11904→12260, 含 step_12000 ckpt 落盘核验）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、step_12000(00:29) ckpt 2.7GB 完好、下一 ckpt@step_14000 ~07:0x。需要时再读。**
> 📦 **[已归档] #558~#565 流水（2026-10-18 20:42~23:24, 🩺 v2 巡检 step10850→12770）→ daily-memories/2026-10-18.md；**结论**：v2 全程健康 0error、step_10000/12000 ckpt 落盘、双节点视角（.12 NFS只读 / .29本地直查）均已核验、MEMORY 滚动归档。需要时再读。**
> 📦 **[已归档] #552~#557 流水（2026-10-18 17:52~20:07, 🩺 v2 巡检 step9990→10680 + MEMORY 滚动归档）→ daily-memories/2026-10-18.md；**结论**：v2 全程健康 0error、step_10000 ckpt 落盘、#535~#546 旧流水滚入 daily-memories、ETA~10-20 02:5x。需要时再读。**
> 📦 **[已归档] #548~#551 流水（2026-10-18 15:55~17:19, 🚨 误判三连：训练死亡误报→resume误判→.12重复训练被杀 + 纠偏闭合）→ daily-memories/2026-10-18.md；结论：#548/#550 均为误判（主 run PID2597555 从未死、0 步丢失），#550 resume 落成 .12 重复训练已被运维 ops134 杀，#551 纠偏闭环，v2 训练健康。需要时再读。**
  > 📦 **[已归档] #515~#518 流水（2026-10-17 23:48 ~ 2026-10-18 01:04, 🩺 v2 巡检 step4540→4910 + P0中继只读核验）→ daily-memories/2026-10-18.md；结论：step4540/4570/4740/4910 健康 loss1.29~1.52 tok/s298.4K 0 error, 中继2706247健康, ckpt step_2000+4000 已保存, ETA~50h→10-20 03:0x。需要时再读。**
  > 📦 **[已归档] #519~#521 流水（2026-10-18 01:04~02:12, P0中继误报与纠偏）→ daily-memories/2026-10-18.md；结论：#519误报"2706247已死"重启1048010→#520纠偏2706247存活(22:07起)为唯一健康→#521(.12视角)1048010亦健康(两机各一中继互不冲突)；v2 step5100/5260 健康 0 error。需要时再读。**
  > 📦 **[已归档] #522~#534 流水（2026-10-18 02:19~08:12, 🩺 v2 常规巡检 step5290→7079 + P0 中继只读核验）→ daily-memories/2026-10-18.md；**结论**：v2 全程健康 0error、ckpt step_2000/4000/6000 已存、P0 中继两机闭环、ETA~10-20 02:5x。需要时再读。**
> 📦 **[已归档] #535~#538 流水（2026-10-18 08:46~11:17, v5 中文HTML/R3降级/数字一致性补丁/溯源补丁）→ daily-memories/2026-10-18.md；**结论**：v5 三交付物（中文HTML+PLAN_V5_STABLE_1.5T.md+PLAN_V5_DATA_PREREQ.md）全部落盘并提交（5 个 pretrain plan-v5:），10-18② 令闭合。需要时再读。**
  > 📦 **[已归档] #539~#542 流水（2026-10-18 11:40~13:37, v5 三交付物终验/复验 + P0 ops中继核验闭合）→ daily-memories/2026-10-18.md；**结论**：v5 三交付物（HTML+PLAN_V5_STABLE_1.5T.md+PLAN_V5_DATA_PREREQ.md）全部落盘并 committed（5 个 pretrain plan-v5:），P0 中继 .last_run_id=123 回执闭环。需要时再读。**
> 📦 **[已归档] #543~#546 流水（2026-10-18 14:09~15:20, 🩺 v2 巡检 + P0 中继/v5 三交付物核验）→ daily-memories/2026-10-18.md；**结论**：v2 全程健康 0error、P0 中继闭环+无新命令、v5 三交付物 committed、ckpt step_2000/4000/6000/8000 已存。需要时再读。**

> 📦 **[已归档] #472~#514 流水（2026-10-17 02:16 ~ 23:20, 🩺 v2 监控 step280→4400 + 🔧_orig_mod修复重启续跑 + 🚨P0 中继恢复 relay-fix）→ daily-memories/2026-10-17.md；结论：v2 全程健康 0error、step_2000/4000 ckpt 已存、_orig_mod 修复 verify_save@step20 通过、ops 中继 PID2706247(22:07)已恢复(RUN_ID118-121 exit=0/.last_run_id=121 无新命令)、两项 P0 运维令均已闭环。需要时再读。**

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
