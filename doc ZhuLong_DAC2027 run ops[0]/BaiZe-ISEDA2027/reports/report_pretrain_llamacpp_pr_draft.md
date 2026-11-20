# PR Draft — nemotron-h: fix RoPE and FFN activation for correct logits

> **状态：草稿，等用户确认后提交上游。**
> 分支：`fix/nemotron-h-undo-permute-and-rope`（基于 llama.cpp master `149f5641b`）
> commit：`5dc38db00` · 改动：`src/llama-model.cpp` / `src/models/models.h` / `src/models/nemotron-h.cpp`（+25 −7）
> 作者：Yang Liu <paul.liu@cxmt.com>
> 日期：2026-11-05

---

## 标题

`nemotron-h: fix RoPE application and FFN activation for correct logits`

## 背景

`nemotron_h` 架构（Mamba2/attention 混合，model_type=`nemotron_h`，
`NemotronHForCausalLM`）自 PR #15507 起被 llama.cpp 原生支持。但在我们的
Mamba2-hybrid 2.2B 模型（56 层：24 Mamba2 + 32 attention，n_groups=8，
rope_theta=1e6，mlp_hidden_act=gelu）上实测，llama.cpp 推理结果与 HuggingFace
`transformers` 参考实现存在严重偏差：**1 个 token 即偏 3.6 nats**，导致 lm_eval
常识推理任务（sciq/piqa zero-shot, limit=100）相对 HF 掉 16–19 个百分点。

排查排除了「F16 递归精度累积」（1-token 即偏，且 Mamba2 层全权重逐张量对照
max_diff=0.0），锁定为 attention 层的**映射/计算错误**。

## 根因（3 个 bug 叠加）

1. **`rope_type` 错误（主因之一）**：`src/llama-model.cpp` 的
   `llama_model_rope_type()` 把 `LLM_ARCH_NEMOTRON_H` / `LLM_ARCH_NEMOTRON_H_MOE`
   归入返回 `LLAMA_ROPE_TYPE_NONE` 的 case 分组。但 HF `NemotronHForCausalLM`
   对 attention 层的 Q/K 应用 RoPE（GPT-NeoX 布局，rope_theta 取自 config）。
   ⇒ GGML 完全不跑 RoPE，attention 的位置编码缺失。

2. **`build_attention_layer` 缺失 `ggml_rope_ext`（主因之二）**：
   `src/models/nemotron-h.cpp` 的 `build_attention_layer()` 只做 `build_qkv` →
   `build_attn`，**不像 `granite-hybrid.cpp` 那样对 Q/K 调用 `ggml_rope_ext`**。
   即使把 `rope_type` 改对，不调用 RoPE 也不会生效。

3. **FFN 激活函数错误**：三处 FFN 路径（dense / MoE experts / shexp）都用
   `LLM_FFN_RELU_SQR`，但 config.json 的 `mlp_hidden_act="gelu"`，应为
   `LLM_FFN_GELU`。

> 关于 `undo_permute`：`NemotronHModel` 继承自 `GraniteHybridModel`，其
> `undo_permute=True` 会在 GGUF 转换时对 q_proj/k_proj 做 permute，产出
> **NORM-rope layout** 的权重——这正是 `LLAMA_ROPE_TYPE_NEOX` 所期望的格式。
> 因此 `undo_permute=True` 是**正确的**，无需改动；原 bug 是
> 「permuted 权重 + 运行时不跑 RoPE」的**不匹配**。

## 修复

```diff
src/llama-model.cpp:
- 将 LLM_ARCH_NEMOTRON_H / LLM_ARCH_NEMOTRON_H_MOE 从 LLAMA_ROPE_TYPE_NONE 分组
  移到返回 LLAMA_ROPE_TYPE_NEOX 的 case 分组。

src/models/models.h:
- build_attention_layer 签名新增 ggml_tensor * inp_pos 参数。

src/models/nemotron-h.cpp:
- graph() 中新增 build_inp_pos()，并传入 build_attention_layer。
- build_attention_layer() 中对 Q/K 调用 ggml_rope_ext(...)（照抄 granite-hybrid 模式，
  含 rope_factors / n_rot / rope_type / freq_base 等参数）。
- 三处 FFN 激活 LLM_FFN_RELU_SQR → LLM_FFN_GELU。
```

完整 diff 见 commit `5dc38db00`（3 文件，+25 −7）。

## 验证

### 1. 1-token logits 对齐（GGML F16 vs HF float32）

| prompt | 指标 | 修复前 | 修复后 |
|---|---|---|---|
| "Hello" (1 token) | top-1 logit Δ | 3.6 nats | **0.006**（Δ abs.mean=0.0008） |
| "Hello" | top-5 token | 偏差大 | **完全一致**（id=14/989/3/4495/16） |
| "The quick brown fox" (4 token) | top-10 token | — | **完全一致**（顺序+ID） |

修复前 1-token 即偏 3.6 nats → 修复后 Δ max=0.006（**600× 改善**，F16 噪声级别）。

### 2. lm_eval 常识推理复判（zero-shot, limit=100，同 100 样本）

| 任务 | 指标 | HF float32 | GGUF F16 修复后 | Δ | GGUF 修复前 | 修复前 Δ |
|---|---|---|---|---|---|---|
| sciq | acc | 0.79 | 0.79 | **0.00** | 0.61 | −0.18 |
| sciq | acc_norm | 0.71 | 0.70 | **−0.01** | 0.54 | −0.17 |
| piqa | acc | 0.72 | 0.72 | **0.00** | 0.56 | −0.16 |
| piqa | acc_norm | 0.73 | 0.73 | **0.00** | 0.54 | −0.19 |

全部 4 项 |Δ| ≤ 1pp ✅。修复前 16–19pp 掉分 → 修复后 ≤1pp（统计噪声内）。

### 3. 无需重新转换 GGUF

现有 `undo_permute=True` 转出的 GGUF 与修复后的代码兼容，无需重新转换。

## 附加发现（可选另行报告，本 PR 不含）

- `conversion/nemotron.py` 的 MoE 路径（line 710）传原始 `A_log` 而非
  `-exp(A_log)`（dense 路径正确）。不影响 dense BaiZe，但影响 MoE Nemotron-H。
- `ssm_scan_f32`（`ops.cpp`）softplus 后未 clamp `dt ≥ mamba_dt_min`，HF 有
  `clamp(softplus(dt), min=0.001, max=inf)`。实测仅 1/64 head 受影响，影响极小。

## 测试方法

```bash
# 编译（CPU）
cmake -B build -DGGML_NATIVE=ON -DLLAMA_CURL=OFF -DGGML_CUDA=OFF
cmake --build build -j 32 --target llama-server

# 转换（undo_permute=True，无需改动）
python convert_hf_to_gguf.py <hf_ckpt> --outfile out_f16.gguf --outtype f16

# 1-token logits 对齐
build/bin/llama-server -m out_f16.gguf --port 8090 -t 8 -c 4096 --temp 0 --top-k 1
# 对照 HF: from transformers import NemotronHForCausalLM; ...

# lm_eval
python gguf_lmeval_run.py --base-url http://127.0.0.1:8090 \
  --hf-dir <hf_ckpt> --tasks sciq,piqa --limit 100
```
