# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

> 🆕 2026-11-01 23:13 #1106：**S1 健康监控**。git clean（与origin同步）。S1 PID1415997/.29（torchrun master via ssh→.12, etimes~125566s/~34.9h）活着，iter 48060/700k（6.87%），loss 近5步 avg~2.123（range 2.118-2.138），grad-norm 0.088-0.187（极稳无spike），lr 1e-3 constant，loss-scale 1.0，0 NaN/0 Inf/0 skipped（48060步全clean），step~6.9s/~605K tok/s（150步 in ~18min since #1105），ckpt@iter_48000已保存@23:06（next@50000, 路径 nemo_experiments/baize2b/checkpoints/iter_0048000）。双机16×H100 GPU .29 8×97-100%util/.12 8×97-100%util，均~75GB/80GB。论文6页/ERR=0 维持。ETA ~52.1天。未完成指令：无。📦 体积：TASK=23.7KB / MEMORY=10.5KB（归档0KB）。
> 📦 §#1105（11-01 22:55, S1健康监控iter47910/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47910(6.84%), loss~2.13稳态, grad-norm 0.086-0.225极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1106监控。需要时再读。
> 📦 §#1104（11-01 22:38, S1健康监控iter47740/loss~2.131/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47740(6.82%), loss~2.131稳态, grad-norm 0.087-0.143极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1105监控。需要时再读。
> 📦 §#1103（11-01 22:18, S1健康监控iter47580/loss~2.122/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47580(6.80%), loss~2.122稳态, grad-norm 0.083-0.181极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1104监控。需要时再读。
> 📦 §#1102（11-01 22:00, S1健康监控iter47430/loss~2.127/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47430(6.77%), loss~2.127稳态, grad-norm 0.091-0.181极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1103监控。需要时再读。
> 📦 §#1101（11-01 21:42, S1健康监控iter47270/loss~2.122/0NaN/~607K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47270(6.75%), loss~2.122稳态, grad-norm 0.086-0.137极稳(minor spike 0.987@47220已恢复), ~607K tok/s, ckpt@iter_46000(next@48000)。被#1102监控。需要时再读。
> 📦 §#1100（11-01 21:25, S1健康监控iter47120/loss~2.122/0NaN/~607K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47120(6.73%), loss~2.122稳态, grad-norm 0.086-0.112极稳(minor spike 0.947@46910已恢复), ~607K tok/s, ckpt@iter_46000(next@48000)。被#1101监控。需要时再读。
> 📦 §#1099（11-01 21:07, S1健康监控iter46970/loss~2.125/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46970(6.71%), loss~2.125稳态, grad-norm 0.087-0.102极稳(minor spike 0.947@46910已恢复), ~605K tok/s, ckpt@iter_46000(next@48000)。被#1100监控。需要时再读。
> 📦 §#1097（11-01 20:30, S1健康监控iter46650/loss~2.116/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46650(6.66%), loss~2.116稳态, grad-norm 0.083-0.370极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1098监控。需要时再读。
> 📦 §#1096（11-01 20:13, S1健康监控iter46500/loss~2.116/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46500(6.64%), loss~2.116稳态, grad-norm 0.082-0.257极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1097监控。需要时再读。
> 📦 §#1095（11-01 19:55, S1健康监控iter46340/loss~2.119/0NaN/~606K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46340(6.62%), loss~2.119稳态, grad-norm 0.082-0.257极稳无spike, ~606K tok/s, ckpt@iter_46000(next@48000)。被#1096监控。需要时再读。
> 📦 §#1094（11-01 19:37, S1健康监控iter46190/loss~2.122/0NaN/~606K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46190(6.60%), loss~2.122稳态, grad-norm 0.083-0.151极稳无spike, ~606K tok/s, ckpt@iter_46000(next@48000)。被#1095监控。需要时再读。
> 📦 §#1093（11-01 19:18, S1健康监控iter46030/loss~2.118/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46030(6.58%), loss~2.118稳态, grad-norm 0.083-0.099极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1094监控。需要时再读。
> 📦 §#1092（11-01 19:00, S1健康监控iter45870/loss~2.131/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter45870(6.55%), loss~2.131稳态, grad-norm 0.088-0.193 minor spike 0.776@45760已恢复, ~605K tok/s, ckpt@iter_44000(next@46000)。被#1093监控。需要时再读。
> 📦 §#1091（11-01 18:43, S1健康监控iter45720/loss~2.129/0NaN/~606K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter45720(6.53%), loss~2.129稳态, grad-norm极稳无spike, ~606K tok/s, ckpt@iter_44000(next@46000)。被#1092监控。需要时再读。
> 📦 §#1090（11-01 18:26, S1健康监控iter45570/loss~2.123/0NaN/~607K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter45570(6.51%), loss~2.123稳态, grad-norm 0.084-0.408 minor无spike, ~607K tok/s, ckpt@iter_44000(next@46000)。被#1091监控。需要时再读。
> 📦 §#1089（11-01 18:06, S1健康监控iter45410/loss~2.123/0NaN/~607K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter45410(6.49%), loss~2.123稳态, grad-norm极稳无spike, ~607K tok/s, ckpt@iter_44000(next@46000)。被#1090监控。需要时再读。
> 📦 §#1087（11-01 17:30, S1健康监控iter45090/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter45090(6.44%), loss~2.13稳态, grad-norm minor spike 0.335@45040已恢复, ~605K tok/s, ckpt@iter_44000(next@46000)。被#1088监控。需要时再读。
> 📦 §#1086（11-01 17:11, S1健康监控iter44930/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter44930(6.42%), loss~2.13稳态, grad-norm spike 2.352@44720单步瞬态已恢复, ~605K tok/s, ckpt@iter_44000(next@46000)。被#1087监控。需要时再读。
> 📦 §#1085（11-01 16:54, S1健康监控iter44780/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter44780(6.40%), loss~2.13稳态, grad-norm spike 2.352@44720单步瞬态已恢复, ~605K tok/s, ckpt@iter_44000(next@46000)。被#1086监控。需要时再读。
> 📦 §#1084（11-01 16:37, S1健康监控iter44630/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter44630(6.38%), loss~2.13稳态, grad-norm minor spike 0.704@44590已恢复, ~605K tok/s, ckpt@iter_44000(next@46000)。被#1085监控。需要时再读。
> 📦 §#1083及更早流水（11-01 16:17前, iter≤44470, 含S1监控链#1077~#1083）均已归档 → daily-memories/2026-11-01.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.12-2.16稳态, 吞吐~550-631K tok/s(多数~605K), ckpt从iter_38000递进至iter_44000; decay 5000步CS8=58.97%; 论文6页ERR=0。需要时再读 daily-memories/2026-11-01.md。
> 📦 §#1076及更早流水（11-01 14:10前, iter≤43360, 含S1监控链#1068~#1076、#1067及更早）均已归档 → daily-memories/2026-11-01.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.12-2.16稳态, 吞吐~550-631K tok/s(多数~605K), ckpt从iter_38000递进至iter_42000; decay 5000步CS8=58.97%; 论文6页ERR=0; baize-llm项目目录就绪。需要时再读 daily-memories/2026-11-01.md。
> 📦 §#1067及更早流水（11-01 11:26前, iter≤41950, 含S1监控链#1044~#1067、#1043及更早）均已归档 → daily-memories/2026-11-01.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.12-2.16稳态, 吞吐~550-631K tok/s(多数~605K), ckpt从iter_38000递进至iter_42000; decay 5000步CS8=58.97%; 论文6页ERR=0; baize-llm项目目录就绪。需要时再读 daily-memories/2026-11-01.md。

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
- **S1 全量预训练运行中** 10.239.2.29 + .12 双机 16×H100：iter 48060/700k(6.87%), loss~2.12, 0NaN, ~605K tok/s, ckpt@iter_48000(next@50000, 路径 nemo_experiments/baize2b/checkpoints/)。GPU .29 8×97-100%util/.12 8×97-100%util, 均~75GB/80GB。
- S1 日志：.29 `/tmp/baize_s1_baize2b_worker.log`（实时训练进度，每10步一行）+ `/tmp/baize_s1_baize2b_master.log`。
- watchdog `baize_pretrain_loop.sh` 必须 7×24 存续，🚫 绝不 kill。
- P-9 系列实验全部 ✅ 完成（P-9.1~P-9.11）；R2 P-1~P-8 全部 ✅ 完成；论文 6 页 ERR=0。