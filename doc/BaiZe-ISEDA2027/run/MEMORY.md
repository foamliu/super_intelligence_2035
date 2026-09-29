# MEMORY.md — BaiZe 1B 架构与超参搜索 运行时状态（不提交 git，重启用）

> 🔄 **任务重启说明**：此轮专攻 **Hymba / Jet-Nemotron 架构兼容性验证**。
> ⚠️ **前一轮检查路径有误**：agent 只查了 swift 注册表就判定 NOT_SUPPORTED，但 **Hymba 是 NVIDIA 自研架构**，底层的 megatron-core（NVIDIA 官方维护）很可能有原生模型定义。此轮修正检查顺序：**先查 megatron-core 模型库 → 再查 swift bridge 层**。

## 当前状态
- STAGE: **S0.5 架构兼容性验证** ✅ 收官（Hymba / Nemotron 均无 1B 变体，MiniCPM5-1B 唯一胜出）
- PHASE: **converged**（任务收官，步骤 G：无动作退出）
- ERROR_COUNT: 0
- BUDGET_USED（GPU·小时）: 0（上限 20）
- 当前运行实验: 无
- 下一步: converged — 步骤 G：胜出配置（MiniCPM5-1B）+ 可复现命令（bash train_s4_01.sh）已在 EXPERIMENTS.md 顶部就位，无动作退出

## 可用数据清单
- UltraData-Code: AVAILABLE (1.2T)
- UltraData-Math: AVAILABLE (515G)
- UltraData-SFT-2605: AVAILABLE (152K ⚠️ 极小，疑似未完整下载，主预训练用 FineWeb-L3 不受影响)
- UltraData-SFT-Agent-2609: AVAILABLE (51G)
- Ultra-FineWeb-L3: AVAILABLE (1.8T) ✅ 主预训练数据（历次实验已用）

## 实验看板
（架构类型维度扫描已完成，无新实验；胜出配置保持 MiniCPM5-1B，S4-01 loss 4.9690@160）

## 操作流水
| 时间 | 步骤 | 记录 |
|------|------|------|
| 2026-09-29 09:24 | data_check | ✅ 数据可用：5 数据集全部 AVAILABLE（Ultra-FineWeb-L3 1.8T / UltraData-Code 1.2T / UltraData-Math 515G / UltraData-SFT-Agent 51G / UltraData-SFT-2605 152K）。至少一个可用 → PHASE=env_check |
| 2026-09-29 10:34 | env_check | ✅ 环境验证通过（Python 3.10.18 / torch 2.8.0+cu128 CUDA 12.8 / megatron 可导入）。🔑 关键发现：底层 megatron-core 原生含 Mamba/SSM hybrid（core.models.mamba / core.ssm.mamba_hybrid_layer_allocation）及 bridge 层 nemotron/nemotronh/mamba 模型定义，需在 experiment_plan 修正前一轮「Hymba/Nemotron NOT_SUPPORTED」的判定依据（前一轮只查 swift 注册表遗漏了 megatron-core 层）。PHASE→data_preprocess |
| 2026-09-29 11:44 | data_preprocess | ✅ ①数据预处理：无需独立 .bin/.idx 脚本——Ultra-FineWeb-L3 `qa` 为 snappy.parquet，历次 S1~S4 已用 `--dataset .../ultrafineweb_en_l3/qa --streaming true --packing true --packing_length 4096` 直接流式 tokenize（Quick-start.md 确认复用 dataset/template 模块），原始格式直接可用 → 跳过预处理。②架构判定修正（先查 megatron-core）：mcore 原生含 `bridge/models/mamba/mamba_provider.py`（MambaModelProvider 支持 hybrid_attention_ratio/hybrid_mlp_ratio/hybrid_override_pattern，即 Hymba 式 hybrid，但仅 mamba2_hybrid_8b=8B 与纯 Mamba2 1.3B，无 ~1B hybrid）+ `bridge/models/nemotron`(Nemotron3 最小 4B) + `nemotronh`(最小 4B) + `core/ssm/mamba_hybrid_layer_allocation.py`。swift 层仅 `mamba`(classic Mamba1/model_arch=None) + `nemotron_h`(30B-A3B MoE/transformers>=5.0)，`grep hymba`=空。→ Hymba/Nemotron = ⚠️ **NOT_EXPOSED / 无 1B 变体**（非「0 处注册 NOT_SUPPORTED」），无可运行 1B 替代架构，MiniCPM5-1B 保持唯一胜出。PHASE→experiment_plan |
| 2026-09-29 12:53 | experiment_plan | ✅ S4 及架构类型维度扫描均已收官：实验表 S1-01~S4-01 全部 done（胜出配置 MiniCPM5-1B，S4-01 loss 4.9690@160，基线唯一改动 = Stable LR 6e-4→3e-4）；架构类型（MiniCPM5-1B/Nemotron/Hymba）扫描完成、megatron-core 虽原生含 Mamba/SSM-hybrid 与 Nemotron 但均无 1B 变体 → 无可运行 1B 替代架构。复核：nvidia-smi 计算进程空、pgrep 无 megatron/swift 残留、checkpoint-160 与 train_s4_01.sh 均就位。→ 无新实验，PHASE=converged |

## 环境备注
- ✅ 环境验证通过（2026-09-29 10:34 env_check）：Python 3.10.18（conda py310）、PyTorch **2.8.0+cu128** / CUDA **12.8**、megatron 可导入（namespace 包，无 __version__；site-packages: `/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/megatron`）
- 🔑 **重大发现（修正前一轮「Hymba/Nemotron NOT_SUPPORTED」的判定依据）**：底层 megatron-core **原生含 Mamba/SSM hybrid 与 nemotron 支持**，前一轮只查 swift 注册表遗漏了 megatron-core 层：
  - `megatron.core.models.mamba`（mamba_model.py / mamba_layer_specs.py）
  - `megatron.core.ssm`（mamba_block / mamba_layer / mamba_mixer / **mamba_hybrid_layer_allocation** / mamba_context_parallel）
  - `megatron.bridge.models.mamba`（mamba_provider）+ `megatron.bridge.recipes.mamba`（mamba2_130m/370m/780m/1.3b/2.7b/8b 及 **mamba2_hybrid_8b**）
  - `megatron.bridge.models.nemotron`（nemotron_provider/bridge）+ `megatron.bridge.models.nemotronh`（nemotron_h_provider/bridge）+ `megatron.bridge.recipes.nemotronh`（nemotronh_4b/8b/47b/56b/nemotron_nano_9b_v2/12b_v2）
  - → Hymba（attention+SSM hybrid）的底层 SSM-hybrid 能力在 megatron-core 已存在；NemotronH 亦有 bridge 模型。能否经 swift 桥接为「1B 可训练配置」留待 experiment_plan 详查（注意 Hymba 属 NVIDIA 自研 hybrid，megatron-core 的 `mamba_hybrid_layer_allocation` 很可能就是其底层实现）。

## 架构判定修正（2026-09-29 data_preprocess 收官）
- 正确检查顺序（先 megatron-core → 再 swift）复核结论：megatron-core **原生支持** Mamba/SSM-hybrid 与 Nemotron，但**均无 1B 变体**。
- mcore `bridge/models/mamba`：`MambaModelProvider` 支持 hybrid（`hybrid_attention_ratio` / `hybrid_mlp_ratio` / `hybrid_override_pattern`，Hymba 式），现有规模 130M / 370M / 780M / **1.3B(纯 Mamba2，override "M"*48，无 attention)** / 2.7B / 8B / **hybrid_8B** → **无 ~1B hybrid recipe**。
- mcore `bridge/models/nemotron`（Nemotron3 4B/8B/22B，最小 4B）+ `bridge/models/nemotronh`（4B/8B/47B/56B/nano，最小 4B）。
- swift 层：`mamba`（classic Mamba1 HF，`model_arch=None` 无 mcore bridge 路径）+ `nemotron_h`（30B-A3B MoE / `transformers>=5.0`），`grep hymba`=空。
- **判定**：Hymba = ⚠️ **NOT_EXPOSED / 无 1B 变体**；Nemotron/NemotronH = ⚠️ **NOT_EXPOSED / 无 1B 变体**（非「0 处注册 NOT_SUPPORTED」）。→ 无可运行 1B 替代架构，MiniCPM5-1B 保持唯一胜出，无新实验、无预算消耗。