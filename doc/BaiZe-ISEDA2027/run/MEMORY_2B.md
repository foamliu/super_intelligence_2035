# MEMORY_2B.md — BaiZe 2B 架构搜索（从零训练）运行时状态（随 git 提交，重启用）

## 当前状态
- STAGE: S2 1000 步从零训练（两架构各 6 卡并行 running）
- PHASE: experiment_wait（等训练结束 → 提取 loss/tok/s → infer_bench）
- WAITING: 1  ← 两架构 1000 步训练 running。判断结束：`pgrep -f pretrain_launcher`（本机=minicpm5，`ssh 10.239.2.12 pgrep -f pretrain_launcher`=mamba2）；或日志尾部 "saving checkpoint at iteration 1000"
- ERROR_COUNT: 0
- BUDGET_USED（GPU·小时）: ~0.3（冒烟）+ 训练进行中
- 当前运行实验:
  - A1-01 MiniCPM5-2B：2.29 GPU0~5，日志 `/tmp/BAIZE2B_minicpm5_train.log`，~270ms/iter，几分钟跑完
  - A2-01 Mamba2-hybrid：2.12 GPU0~5，日志 `/tmp/BAIZE2B_mamba2_train.log`，SSM 慢，预计 ~3 小时
- 下一步: ① 提取 MiniCPM5 最终 loss/训练 tok/s；② Mamba2 跑完（~3h）后提取；③ 两架构齐 → infer_bench（ckpt→HF → SGLang）

## ⚠️ 本次会话关键变更（2026-09-29 晚，覆盖上一 agent 的「GBS=128 / 切 5.2M docs」计划）
- **GBS 定版为 6**（TP=1/DP=6/mb=1，无梯度累积，24.5K tok/步）：任务数据段「~4M tok/步」是数据规模估计，非硬约束（决策 3「相同 GBS，标注即可」才是硬约束）。**根因**：Mamba2 SSM 每步 ~11.6s，GBS=128（grad_accum≈21）会让 Mamba2 达 ~68h/站≈408 GPU·h，远超 20 GPU·h 预算；GBS=6 时 Mamba2 ≈3.2h×6卡≈19.3 GPU·h，刚好压线。故用 GBS=6（已记录于 EXPERIMENTS_2B.md）。
- **数据只需 200k docs / 165M tokens**（非 5.2M≈4B）：GBS=6 × 4096 × 1000 步 ≈ 24.6M tokens，165M 已 6.7× 余量，且够 LR 扫描再用 2 组。已 kill 上一 agent 的 `preprocess_data.py --max-docs 5200000`（PID 56513，切 13min 仅 1.5G，ETA 2.5h，属浪费），改用 200k docs（`data/ultrafineweb_l3_qa.bin/.idx/.json`，629M，387K tok/s，342.9s 完成）。

## 数据检查结论（data_check 完成）
- 选用子集：`openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa/`（618G，part-00000~...，每个 1.1G，约 519,627 行/part）。
- parquet 列：`uid` / `content`(正文) / `style`；切词取 `content`。
- 备选：`multi_style/`（554G）同样可用，暂不切。
- 磁盘估算：~1000 步 × ~4M tok/步 ≈ 4B tokens；每 part 文本约 ~275M tokens（DeepSeek 切词粗估），切 ~15~18 个 part 足够（数据 .bin/.idx 预计 ~16~20GB，两架构共用）。
- tokenizer 已确认：`/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash/`（tokenizer.json + tokenizer_config.json）。
- MiniCPM5-2B config 已确认：42 层 / hidden 2048 / intermediate 6144 / 16 heads / 2 KV heads / head_dim 128 / silu / rope_theta 5e6 / vocab(原始) 130560（本任务改用 DeepSeek 129281→pad 129408）。

## 候选架构（固定）
- MiniCPM5-2B（42 层 Llama）：config 见 doc/BaiZe-ISEDA2027/MiniCPM5-2B.config.json
- Mamba2-hybrid 2B（56 层 hybrid）：代码见 BASE_DIR/mamba2_hybrid_2b/

## 关键决策（勿违反）
1. 两架构统一走 NVIDIA/NeMo recipe（随机初始化从零），统一 tokenizer=DeepSeek-V4.1-Flash（vocab 129281/pad 129408）
2. 训练口径对齐（seq4096/mb1/同超参/同数据/同seed），**两架构必须同卡数**（建议各 6 卡并行）
3. omegaconf 阻塞需 PYTHONPATH=/nas_train/app.e0031982/omegaconf_230 规避（NFS 共享，两节点通用；/tmp 是节点本地不可跨节点）
4. 最终产出 HTML 报告 `doc/BaiZe-ISEDA2027/BAIZE_2B_ARCH_RESULT.html`

## arch_prepare 关键结论（S1 已打通，2026-09-29）
- **两架构均已从零跑通 10 步 GPU 冒烟 + 保存 checkpoint**（torch_dist），确认可运行。
- **统一 launcher**：`BASE_DIR/pretrain_launcher.py`（torchrun + `pretrain(pretrain_config(...), forward_step=gpt_step.forward_step)`），`--arch minicpm5|mamba2`。nemo_run 未装，已 bypass（`nvidia_resiliency_ext.CallWrapper` 内置可用）。
- **两个 megatron-core 0.16.1 兼容补丁（关键，勿删）**：
  1. `BASE_DIR/bridge_compat.py` 的 `apply_all_compat_shims()`：修 `get_megatron_optimizer` 旧→新签名（否则 `TypeError: multiple values for 'use_gloo_process_groups'`）。launcher 已在 `pretrain()` 前调用。
  2. 两 recipe 的 `CheckpointConfig(save_optim=False, save_rng=False)`：绕开 0.16.1 optimizer 态的 `ShardedTensor.flattened_range is not supported` 崩溃。从零训练无需恢复 optimizer 态，S3 推理只需模型权重。
- **根因**：megatron-bridge 0.2.0rc6 要求 `megatron-core<0.16,>=0.14`，而本环境装 0.16.1（为满足 1B 任务 mcore_bridge 1.6.4 的 `>=0.16`）。**不可降级**（会破坏 1B 任务），故用 monkeypatch 规避。
- **⚠️ 参数量不对齐（>10%，需在报告注明「非等参对比」）**：MiniCPM5-2B 实测 **2.51B**（transformer 1.98B + embedding 0.53B，tie=False 双嵌入）；Mamba2-hybrid 实测 **3.00B**（transformer 2.47B + embedding 0.53B）。差 ~19.5%。
- **⚠️ 冒烟初始 loss 差异异常**：MiniCPM5 loss=11.62（≈ln(129408)=11.77 正常）；Mamba2 loss=8.80（**显著偏低**，疑似非均匀随机初始化或 SSM 归纳偏置/init 异常）。需在 1000 步训练确认，若 Mamba 初值失真需排查 provider init。
- 冒烟吞吐（TP=2 / mock 数据，仅供参考，训练速度需 6 卡真实数据重测）：MiniCPM5 ≈1462ms/iter，Mamba2 ≈11619ms/iter（SSM 明显更慢）。
- MiniCPM5-2B provider：`BASE_DIR/minicpm5_2b/provider.py` 继承 `Llama3ModelProvider`，对齐 config（42层/hidden2048/ffn6144/16头/2kv头/rope5e6/eps1e-6/init0.02/tie=False），vocab 走 DeepSeek 129281→pad129408。✅ 可复用，**已从零可跑**。

## GPU 资源（双节点）
- 10.239.2.29（8×H100，GPU0~7，本机 hostname=whag0pgpuap29）；10.239.2.12（8×H100，GPU6~7 被他人占 72G，仅 GPU0~5 可用）。两节点 ssh 免密已通。
- 建议：MiniCPM5-2B 用 2.29（GPU0~5）、Mamba2-hybrid 用 2.12（GPU0~5），剩余 2.29 的 GPU6~7 留冒烟/推理。

## S2 1000 步训练（已启动，两架构并行 running）
- **统一口径（决策 3，已定）**：seq=4096 / mb=1 / TP=1（DP=6）/ **GBS=6**（6 seq × 4096 = 24.5K tok/步，无梯度累积）/ AdamW lr=3e-4 warmup=100 decay→1000 / wd=0.1 / bf16 / train_iters=1000 / 同 seed=1234 / 同数据（DeepSeek `data/ultrafineweb_l3_qa.bin/.idx` 共用）/ eval 关闭（eval_iters=0）。
- **卡数对齐（关键）**：两架构均 6 卡、TP=1 DP=6 → 训练 tok/s 可比。MiniCPM5 在 2.29（GPU0~5），Mamba2 在 2.12（GPU0~5）。
- **GBS=6 理由**：见上「本次会话关键变更」——Mamba2 SSM ~11.6s/步，GBS>6 会让 Mamba2 超 20 GPU·h 预算。
- 启动脚本：`BASE_DIR/scripts/train.sh <arch> <name> <master_port> <nproc>`；日志 `/tmp/BAIZE2B_<arch>_train.log`。
- 关键兼容修法（本次会话补）：① 两 recipe `CheckpointConfig` 补 `load_optim=False`（否则 save_optim=False 的 ckpt 在 resume/load 时 `KeyError: 'optimizer'`）；② eval 关闭用 `eval_iters=0`（`eval_interval=0` 会在 `train_iters // eval_interval` 除零）；③ `/tmp/omegaconf_230` 已 cp 到 NFS `/nas_train/app.e0031982/omegaconf_230`（/tmp 是节点本地，2.12 看不到）。
- ⚠️ Mamba2 初始 loss 8.80 异常需在训练头几步复核（若失真排查 provider init）。

## git 提交（每 4~6 小时 push）
- 根目录 `/nas_train/app.e0031982/code/super_intelligence_2035`；remote foamliu/super_intelligence_2035（main）。
- PAT 已写入 `~/.git-credentials`（credential.helper=store），push 免交互；loop.sh 每 5 小时兜底 push。
- 只提交 `doc/` 文本（md/html/json/sh）；训练产物/checkpoint/.bin/.idx 在 git 外，不入库。

## 操作流水
| 时间 | 步骤 | 记录 |
|------|------|------|
| 2026-09-29 | init | ✅ 任务书 + loop.sh + 记忆文件初始化；PHASE=data_check |
| 2026-09-29 | data_check | ✅ 确认 qa 子集(618G, parquet 列 uid/content/style, 519627行/part)；tokenizer=MiniCPM5 config=Mamba2 dir 均就绪；PHASE→env_check |
| 2026-09-29 | env_check | ✅ PYTHONPATH=/tmp/omegaconf_230 下 `import megatron.bridge` 成功（torch2.8.0+cu128/cuda12.8）；两 provider/recipe import 均 OK；PHASE→arch_prepare |
| 2026-09-29 | arch_prepare | ✅ launcher + MiniCPM5 provider/recipe 落地；✅ 修 2 个 mcore0.16.1 兼容（get_megatron_optimizer shim + save_optim=False 绕 flattened_range）；✅ 两架构 10 步冒烟均跑通并保存 ckpt。⚠️ 参数量 2.51B vs 3.00B 不对齐；⚠️ Mamba 冒烟 loss 8.80 异常。PHASE→experiment_run |
| 2026-09-29 | experiment_run | ✅ 切 200k docs/165M tokens（kill 上一 agent 的 5.2M 切词，改用 200k）；✅ 补 load_optim=False + eval_iters=0 + omegaconf 上 NFS；✅ 真实数据冒烟两架构跑通；✅ **GBS 定版 6**；✅ 启动两架构各 6 卡 1000 步（MiniCPM5 ~270ms/iter、Mamba2 ~3h）。WAITING=1 |
