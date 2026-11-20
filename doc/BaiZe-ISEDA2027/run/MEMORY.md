# MEMORY.md — BaiZe ~2B Mamba2-hybrid 可行性评估 运行时状态（不提交 git，重启用）

> 🔄 **任务说明**：继「BaiZe 1B 架构与超参搜索」收官（胜出 MiniCPM5-1B，S4-01 loss 4.9690@160）之后，本轮评估 **~2B Mamba2-hybrid（attention+SSM 混合）架构能否经 Megatron-SWIFT / NVIDIA-NeMo recipe 路径落地预训练**。步骤 1（provider+recipe）、步骤 2（swift bridge 调研）、步骤 3（DeepSeek tokenizer + 数据预处理）已完成，步骤 4（launcher + forward_step）待做。

## 当前状态
- STAGE: **S0.6 = Mamba2-hybrid ~2B 可行性评估**
- PHASE: **step3_done**（步骤 1/2/3 收官，待步骤 4 launcher）
- ERROR_COUNT: 0
- BUDGET_USED（GPU·小时）: 0（数据预处理为 CPU 冒烟，未占 20h 训练预算）
- 当前运行实验: 无
- 下一步: 步骤 4 — 落地 torchrun launcher（`pretrain_config(tokenizer_path=..., data_paths=[.../.bin 前缀])` + `pretrain(cfg, forward_step_func)`）做 GPU 前向冒烟，判定后续是否值得投入 20 GPU·h

## 可用数据清单（继承自上一任务，本轮已用其一冒烟）
- Ultra-FineWeb-L3: **AVAILABLE (1.8T)** ✅ 主预训练数据（步骤 3 已用 DeepSeek tokenizer 冒烟切词 3000 文档验证）
- UltraData-Code: AVAILABLE (1.2T)
- UltraData-Math: AVAILABLE (515G)
- UltraData-SFT-Agent-2609: AVAILABLE (51G)
- UltraData-SFT-2605: AVAILABLE (152K ⚠️ 极小，主预训练用 FineWeb-L3 不受影响)

## 结论摘要（Mamba2-hybrid 2B 评估，详见 HTML 报告）
- **步骤 1 ✅**：落地 `mamba2_hybrid_2b` 包（`provider.py` / `recipe.py` / `__init__.py` / `FEASIBILITY.md`），镜像 megatron-core `mamba2_hybrid_8b`，宽度减半 → ~2B。56 层 hybrid pattern 复用（`M`=SSM / `*`=attention / `-`=MLP），层分配与模型规模无关。
- **步骤 2 ✅**：swift 两条 bridge 后端均无 Mamba 转换桥 → `megatron pt --model_arch` 直接接上不可行（`mcore-bridge` MODEL_MAPPING 无 standalone Mamba；`megatron-bridge` conversion model_bridge 无 Mamba 桥）。可行路径 = **NVIDIA/NeMo recipe（路径 A）**，绕过 swift。
- **步骤 3 ✅**：按指令用 **DeepSeek-V4.1-Flash** tokenizer 处理数据。新增 `preprocess_data.py`（snappy.parquet `content` → `.bin/.idx` + EOD），`recipe.py` 支持 `tokenizer_path=`（HuggingFaceTokenizer）。关键数值：源词表 **129280** → 追加 `<|endoftext|>` 后 **vocab=129281 / eod=129280**，模型侧 pad 到 **129408**。冒烟 3000 文档 → **2,480,398 tokens** 经 `IndexedDataset` 回读验证通过。
- **环境阻塞已规避**：`omegaconf==2.4.0.dev14` 缺 `_utils.py` → 非破坏性规避（`pip install --target /tmp/omegaconf_230 --no-deps 'OmegaConf==2.3.0'` + `PYTHONPATH=/tmp/omegaconf_230`），`import megatron.bridge` 已验证通过；`nemo_run` 仅编排用，可直接 bypass。

## 实验看板
（本任务为可行性评估，步骤 1~3 均为 CPU/配置级验证，无 GPU 训练实验。胜出架构方向 = 2B Mamba2-hybrid `hybrid_override_pattern`，待步骤 4 launcher 做 GPU 前向冒烟后判定 run 可行性）

## 操作流水
| 时间 | 步骤 | 记录 |
|------|------|------|
| 2026-09-29 15:4x | step1_2_done | ✅ 步骤 1+2 已收官（provider+recipe 落地；swift 两种 bridge 后端 Mamba 桥缺失判定）。阻塞点记录：omegaconf 2.4.0.dev14 残缺、nemo_run 未装 |
| 2026-09-29 15:56 | step3_tokenizer | ✅ 按指令使用 DeepSeek-V4.1-Flash tokenizer：验证 transformers `AutoTokenizer` 可加载（PreTrainedTokenizerFast，源词表 129280），追加 `<\|endoftext\|>` EOD → vocab 129281 / eos_id 129280 / pad 129408，`save_pretrained` 到 `mamba2_hybrid_2b/tokenizer_eod/` |
| 2026-09-29 16:11 | step3_preprocess | ✅ 新增 `mamba2_hybrid_2b/preprocess_data.py`：Ultra-FineWeb-L3 qa snappy.parquet（content 列）→ DeepSeek 切词 → `IndexedDatasetBuilder` 产出 `.bin/.idx` + `.json` 元信息。冒烟 `--max-docs 3000` → 2,480,398 tokens（~6.4s），`IndexedDataset` 回读通过（文档末尾=EOD 129280，token id 范围 [0,129280]） |
| 2026-09-29 16:13 | step3_env_fix | ✅ omegaconf 阻塞非破坏性规避：`pip install --target /tmp/omegaconf_230 --no-deps 'OmegaConf==2.3.0'` + `PYTHONPATH=/tmp/omegaconf_230` → `import megatron.bridge` 成功；`NVIDIAMambaHybridModelProvider2B` 实例化成功；`pretrain_config(tokenizer_path=...)` → `build_tokenizer` 产出 `_HuggingFaceTokenizer(vocab=129281, eod=129280)` |
| 2026-09-29 16:19 | step3_recipe | ✅ `recipe.py` 支持 `tokenizer_path` 参数（HuggingFaceTokenizer），`FEASIBILITY.md` 更新至「步骤 1+2+3」；`py_compile` 四个文件全部通过。PHASE→step4_launcher（待做） |

## 环境备注
- ✅ 环境验证：Python 3.10.18 / torch 2.8.0+cu128 / CUDA 12.8 / megatron 可导入（namespace 包，site-packages: `/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/megatron`）
- 🔑 megatron-core 原生含 Mamba/SSM-hybrid：`core.models.mamba` / `core.ssm.mamba_hybrid_layer_allocation` / `bridge.models.mamba(mamba_provider)` / `bridge.recipes.mamba`（mamba2_130m...8b/hybrid_8b）
- ⚠️ 阻塞：`omegaconf==2.4.0.dev14` 缺 `_utils.py` → 已用 `/tmp/omegaconf_230`(OmegaConf==2.3.0) + PYTHONPATH 规避；`nemo_run` 未装（仅编排用，可 bypass）；`nvidia_resiliency_ext` 可用
- 数据：DeepSeek-V4.1-Flash tokenizer 位于 `/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash`；EOD 增强副本在 `mamba2_hybrid_2b/tokenizer_eod/`

## 下一步（步骤 4，未做，仍阻塞）
1. 落地 torchrun launcher 脚本（如 `baize_mamba2_2b_train.sh`），串起 `pretrain_config(tokenizer_path=mamba2_hybrid_2b/tokenizer_eod, data_paths=[.../.bin 前缀], train_iters=微型)` + `megatron.bridge.training.pretrain.pretrain(cfg, forward_step_func=megatron.bridge.training.gpt_step.forward_step)`
2. GPU 前向冒烟：验证 2B provider 实例化 + 数据加载 + 单步前向/反向，确认显存/吞吐，判定后续是否值得投入 20 GPU·h
3. 资源规划：完整 1.8T 数据切词约 1.9e9 tokens / `.bin` ~7.6GB(int32)；GPU 侧 Mamba2 2B 参数需在共享 LLaVA 8 卡场景下 mb=1 谨慎规划
