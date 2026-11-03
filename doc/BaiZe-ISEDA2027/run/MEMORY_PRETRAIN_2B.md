# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0
> 🛑 **【运维通告 · 2026-11-02 19:51】S1 已由 ops 中继重启并在跑**：`bash scripts/train.sh s1 --nodes 2`，launcher pid **4163528**，从 **ckpt 58000** 续（19:55:40 起 iter **58010**→58030，7.0–7.2 s/step ≈**582K tok/s**，双机 16 卡 **98–100%**、~75GB/卡、~690W）。⇒ **GPU 不再空闲**：🚫 严禁再起任何训练/GPU 评测进程（会双写 ckpt 或 OOM）；"GPU idle → 2.5h 评测"的结论已过期。原 **18:39:51 SIGKILL / 18:50:18 SIGBUS** 的现场日志已归档为 `/tmp/baize_s1_baize2b_worker.log.crash_1102_1839` 与 `..._master.log.crash_1102_1839`（🚫 勿删，待 root 查 dmesg 定 OOM vs 误杀）。CPU 评测继续但**必须降载**：`OMP_NUM_THREADS≤8` + `nice -n 19` + 每机并发 ≤2，**禁止 `pkill python`**（18:39 训练被 -9 的疑似原因）。另：本次 resume **未恢复 scheduler**，LR 从 warmup 重来（58010=5e-6，每 10 步 +5e-6，约 2000 步/3.9h 后回 1e-3）——实验日志须记一笔。详见 `BAIZE_PRETRAIN_2B_TASK.md` 顶部运维令。

> 🆕 2026-11-03 18:14 #1254：**监控轮·iter_50000 61.7%@16s/it ETA~22:37·.12 双 float32 13.2-13.3%@30s/it ETA~Nov4 12:47-48·iter_30000 SIGSTOP(144/2599)·watcher PID1999093 运行中·S1 iter69450/loss2.10/0NaN 健康·CPU .29 load32.6/.12 load32.5 均<<80% ✅·未完成指令：有**。
> **② eval 进度快照（18:14 实测，2599=8集合计请求，X/2599 即全程 X%）**：
> - iter_10000 ✅ **DONE** float32 全程 44665s(12.4h)：arc_c=0.29,arc_e=0.49,boolq=0.61,hs=0.36,obqa=0.20,piqa=0.72,sciq=0.79,wg=0.54,**Avg=50.0%**（results.json 23KB 已存，已核验）
> - iter_50000 🔄 bf16 .29(PID 2024390,elapsed 7h37m)：**1604/2599(61.7%)**,**~16s/it**(0 NaN,稳定),剩995×16≈4.4h→**done~22:37 Nov3** ✅on track
> - iter_30000 ⏸ float32 .29(PID 1744762,**SIGSTOP 暂停**,state=T,已做144/2599=5.5%)：watcher(`/tmp/baize_eval_watcher_30000.sh` PID **1999093 运行中**)待 iter_50000 退出后自动 SIGCONT→独享.29≈15s/it→2455×15s≈10.2h→**done~Nov4 08:50**
> - iter_20000 🔄 float32 .12(PID 1259403,elapsed 3h30m)：**343/2599(13.2%)**,稳定**~30s/it**,剩2256×30≈18.8h→**done~Nov4 12:48**
> - iter_40000 🔄 float32 .12(PID 1259184,elapsed 3h30m)：**346/2599(13.3%)**,稳定**~30s/it**,剩2253×30≈18.8h→**done~Nov4 12:47**
> **③ S1 训练**：iter 69450/700000,loss 2.10,0NaN,0skip,~7.0s/step≈598K tok/s,LR=1e-3(稳态)✅。GPU .29 100%/96% util/~75GB。ckpt iter_68000(next@70000)。
> **④ CPU**：.29 load 32.59/224核(≈14.5%)；.12 load 32.53/224核(≈14.5%)。均 <<80% ✅
> **⑤ SIGSTOP 优化（#1242 部署，持续有效）**：iter_30000(SIGSTOP)+iter_50000(bf16)在 .29 上→iter_50000 独享带宽。watcher PID 1999093 运行中，待 iter_50000 退出后自动 SIGCONT iter_30000。
> **⑥ 下一步**：①下轮唤醒查 iter_50000 是否 done(~22:37)→若 done 收 results.json 并确认 iter_30000 已 SIGCONT 恢复 ②持续监控 .12 双 float32(ETA Nov4 12:47-48) ③全部 5/5 done→汇总表+能力-vs-step 曲线+终版报告 report_pretrain_cpu_eval_8sets_zh.html+日报。**最坏 Nov4 12:48 < 24h deadline(Nov4 ~14:50) ✅**。未完成指令：有 ⇒ WAITING: 0。
> **📦 体积**：TASK=30602B(29.9KB)/MEMORY≈10.4KB（均 ≤32KB ✅，本轮无需归档）。
> 📦 §#1253（11-03 18:08, 监控轮·iter_50000 60.9%@15.94s/it）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 60.9% ETA~22:38, .12 双 float32 12.7-12.8% ETA Nov4 13:06-07, S1 iter69400健康。被#1254 确认继续有效(61.7%@16s/it)。需要时再读。
> 📦 §#1252（11-03 18:00, 监控轮·iter_50000 59.9%@16.92s/it）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 59.9% ETA~22:54, .12 双 float32 12.2% ETA Nov4 13:00, S1 iter69340健康。被#1253-#1254 确认继续有效。需要时再读。
> 📦 §#1251（11-03 17:51, 监控轮·iter_50000 58.4%@19.6s/it）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 58.4% ETA~23:45, .12 双 float32 11.4% ETA Nov4 13:08, S1 iter69250健康。被#1252 确认继续有效(59.9%@16.92s/it, 速度回升)。需要时再读。
> 📦 §#1250（11-03 17:38, 监控轮·iter_50000 57.3%@17.1s/it）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 57.3% ETA~22:54, .12 双 float32 10.6% ETA Nov4 13:05, S1 iter69150健康。被#1251-#1252 确认继续有效。需要时再读。
> 📦 §#1249（11-03 17:33, 监控轮·iter_50000 56%@15.6s/it）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 56% ETA~22:25, .12 双 float32 10% ETA Nov4 13:21, S1 iter69100健康。被#1250-#1251 确认继续有效。需要时再读。
> 📦 §#1243-#1248（11-03 16:32-17:18, 监控轮×6·iter_50000 47→56%）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 从47%→56% 稳定, .12 双 float32 从5.5%→10%, SIGSTOP优化有效。被#1249-#1250 确认继续有效。需要时再读。
> 📦 §#1243（11-03 16:32, 监控轮·iter_50000 47%@14.4s/it·.12 5.5%@31s/it）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 加速中, 最坏 Nov4 13:50<deadline。被#1244 确认继续有效。需要时再读。
> 📦 §#1242（11-03 16:25, 监控+优化轮·SIGSTOP iter_30000 释放带宽）→ daily-memories/2026-11-03.md；**结论**：SIGSTOP iter_30000→iter_50000 加速至 13.8s/it, watcher 部署, .12 双 float32@31s/it 稳定。被#1243确认继续有效。需要时再读。
> 📦 §#1241（11-03 16:13, 监控轮·ramp-down 校准）→ daily-memories/2026-11-03.md；**结论**：4 evals 推进, iter_10000 DONE Avg50%, iter_30000@4.1%/16.5s/it(后被#1242 发现实为 48s/it 带宽竞争,已 SIGSTOP 优化)。被#1242 校准+优化。需要时再读。
> 📦 §#1240（11-03 16:00, 监控轮·ramp-down 校准 2599=合计请求）→ daily-memories/2026-11-03.md；**结论**：4 evals 推进, iter_10000 DONE Avg50%, 2599=8集合计请求, iter_10000全程12.4h@17s/it, 全部 5/5 ETA Nov4 上午~中午。被#1241 校准(.12 双 float32 仍 31s/it 瓶颈, 最坏 Nov4 13:30)。需要时再读。
> 📦 §#1239（11-03 15:49, 监控轮·ramp-down 观察）→ daily-memories/2026-11-03.md；**结论**：4 evals 推进, iter_10000 DONE Avg50%, .12 瞬时 36-39s/it ramp-down。被#1240 校准。需要时再读。
>
> 📦 §#1238（11-03 15:35, OMP=8 收敛确认+监控）→ daily-memories/2026-11-03.md；**结论**：OMP=8 收敛 34.78s/it 省~10h, limit=100 生效(2599总请求), iter_50000 39.3% ETA~7.2h, .12 记 60s/it(后被#1239修正为 ramp-down)。需要时再读。
> 📦 §#1237（11-03 15:17, OMP=8 优化执行·iter_30000 重启）→ daily-memories/2026-11-03.md；**结论**：OMP=4→8 重启, 预计省~12h。被#1238确认收敛34.78s/it。需要时再读。
> 📦 §#1236（11-03 15:00, CPU eval 监控·float32 .29 加速中）→ daily-memories/2026-11-03.md；**结论**：4 evals 在跑, iter_10000 DONE(Avg50%), iter_50000 33% ETA~7.5h, float32 .29 55s/it↓加速, .12 93s 2进程竞争。被#1237优化。需要时再读。
> 📦 §#1235（11-03 14:55, CPU eval 监控·float32 ramp-up）→ daily-memories/2026-11-03.md；**结论**：4 evals 在跑, iter_10000 DONE(Avg50%), float32 刚启动ramp-up(73-95s/it), ETA Nov4-5。被#1236监控。需要时再读。
> 📦 §#1234（11-03 14:50, root cause bf16 NaN + 4 evals 重跑启动）→ daily-memories/2026-11-03.md；**结论**：bf16 CPU forward 对 iter_20000/30000/40000 产生 NaN logits(Mamba2 SSM bf16 溢出); float32 修复; 4 evals 启动(1 bf16+3 float32)。被#1236监控。需要时再读。



> 📦 §#1154-#1241（11-02 19:55→11-03 16:13, CPU eval监控·1-80轮+bf16 NaN根因+float32重跑+OMP优化+SIGSTOP）→ daily-memories/2026-11-02.md & 2026-11-03.md；**结论汇总**：5 export完成, bf16 NaN→float32修复, OMP=8, SIGSTOP优化, 速度收敛(.29~16s/.12~30s), iter_10000 DONE Avg=50%, ETA从~10天下修至<24h, CPU全程<<80%。需要时再读 daily-memories。
> 📦 §#1076-#1151（11-01 11:26→11-02 12:55, S1健康监控iter41950→55140, 共~70轮）→ daily-memories/2026-11-01.md & 2026-11-02.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.10-2.16稳态, 吞吐~550-631K tok/s(多数~605K), ckpt iter_38000→54000, grad-norm极稳(偶发瞬态spike均自恢复), decay 5000步CS8=58.97%, 论文6页ERR=0, baize-llm项目目录就绪。需要时再读 daily-memories。
> 📦 §#1043及更早（11-01 11:26前, iter≤41950, S1监控链#1044~#1067及更早）→ daily-memories/2026-11-01.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.12-2.16稳态, ckpt iter_38000→42000; decay CS8=58.97%; 论文6页ERR=0。需要时再读。

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)+已杀的#550 resume 日志(止于 step8070@17:17 SIGTERM)，**误判主 run 已死** ⇒ 这正是 #548/#550 两起误判的根因。SSH 已验证可用。判活三件套只在 .29 上有效；.29 的 `/tmp` log 才是主 run 实时日志（NFS `$OUTPUT_DIR/...train.log` 是 .12 旧日志，亦不可作判据，见 16:4x）。
- transformer_engine 2.12.0+5671fd36 / torch 2.8.0+cu128 / CUDA 12.8 / megatron-core 0.16.1 / mamba-ssm 2.2.6.post3（P-9.4 已核实，与任务书预期一致）。
- 结果主文件：R2=`EXP