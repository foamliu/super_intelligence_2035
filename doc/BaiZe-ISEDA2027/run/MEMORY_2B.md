# MEMORY_2B.md — BaiZe 2B 架构搜索（从零训练）运行时状态（随 git 提交，重启用）

## 当前状态
- STAGE: S1 打通从零冒烟（两架构均已打通 ✅）
- PHASE: arch_prepare（10 步 GPU 冒烟已完成 → 待进入 experiment_run 数据切词）
- WAITING: 0
- ERROR_COUNT: 0
- BUDGET_USED（GPU·小时）: ~0.1（仅 10 步冒烟）
- 当前运行实验: 无
- 下一步: ① 切 Ultra-FineWeb-L3 数据（~15 part ≈ 4B tokens，DeepSeek 切词，两架构共用）；② 启动两架构 1000 步训练（各 6 卡并行）

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
3. omegaconf 阻塞需 PYTHONPATH=/tmp/omegaconf_230 规避
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
- 10.239.2.29（8×H100，GPU0~7）；10.239.2.12（前 6×H100，GPU0~5）。两节点 ssh 免密已通。
- 建议：MiniCPM5-2B 用 2.29（GPU0~5）、Mamba2-hybrid 用 2.12（GPU0~5），剩余 2.29 的 GPU6~7 留冒烟/推理。

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
