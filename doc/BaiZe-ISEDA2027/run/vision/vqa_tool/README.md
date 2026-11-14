# Qwen3.5-2B VQA Tool (vision line · 用户令 2026-11-14 09:1x #3/#4)

把 **Qwen3.5-2B**（多模态 VL 模型，`Qwen3_5ForConditionalGeneration`，
含 `image_token_id`）封装成「看图答波形问题」的 VQA tool，供 cline /
designflow 调用，用于度量「基线 fail → 上 VQA 后 pass」的多模态增益。

## 文件
| 文件 | 作用 |
|:--|:--|
| `qwen35_vqa_server.py` | 常驻 HTTP 服务：加载模型一次，提供 `GET /health`、`POST /vqa`、`POST /shutdown` |
| `qwen35_vqa_client.py` | 薄 CLI 客户端（cline 当工具调）：`--image X --question Y` 打印答案 |
| `baseline_waveform_vqa.py` | 预增强基线评测：合成带 GT 的波形图，查 VQA，落 `baseline_waveform_vqa_results.json` |
| `baseline_images/` | 基线用合成波形图（9 张，含网格） |
| `baseline_waveform_vqa_results.json` | 基线结果（#4 SFT/RL 前后配对对照的底数） |

## 环境（已验证）
- conda env：`/nas_data/app.e0031982/miniforge3/envs/py310`（**transformers 5.20.2** 认 `qwen3_5`，torch 2.6.0+cu124，CUDA 8 卡）
- 模型：`/nas_data/app.e0031982/models/Qwen3.5-2B`（4.3GB safetensors，本机在位）
- ⚠️ 线性注意力核（`causal_conv1d` / `flash-linear-attention`）未装 → transformers 回退到参考 PyTorch 实现，慢但正确（2B 模型在 A40 上 ~2.7s/req）。要提速可后装这两个包。

## 启动服务
```bash
CUDA_VISIBLE_DEVICES=5 /nas_data/app.e0031982/miniforge3/envs/py310/bin/python \
  qwen35_vqa_server.py --port 30001 --gpu 0
# 首次冷加载 ~127s（NFS）；page cache 热 后 ~2.6s
```
当前已在本机 **GPU 5（空闲 A40）、端口 30001** 常驻运行（pid 见 `pgrep -f qwen35_vqa_server`）。
停止：`curl -s -X POST http://127.0.0.1:30001/shutdown` 或 `pkill -f qwen35_vqa_server.py`。

## 调用
```bash
# CLI（cline 当工具）
python qwen35_vqa_client.py --image /path/wave.png -q "How many cycles?"
# HTTP
curl -s -X POST http://127.0.0.1:30001/vqa \
  -H 'Content-Type: application/json' \
  -d '{"image_path":"/path/wave.png","question":"...","max_new_tokens":256}'
```
支持 `image_path`（共享 NFS，首选）或 `image_b64`。

## 基线结果（预增强 · 2026-11-14）
`baseline_waveform_vqa_results.json`：**n=9，correct=5，acc=0.5556**。
| skill | n | correct | acc | 说明 |
|:--|--:|--:|--:|:--|
| rise_edge | 2 | 2 | 1.00 | ✅ α 类 waveview 技能，模型已掌握 |
| freq_compare | 1 | 1 | 1.00 | ✅ 两波形频率比较 |
| duty_cycle | 2 | 1 | 0.50 | 25%/50% 区分不开（默认猜 50%） |
| cycle_count | 3 | 1 | 0.33 | 计数偏差（3→4、5→7） |
| amplitude | 1 | 0 | 0.00 | 幅值欠读（3 格看成 2 格） |

**这正是 #4（SFT/RL 强化）要攻的缺口**：duty_cycle 区分、cycle 精确计数、幅值读数。
同一批图+问将用于 post-SFT/RL 配对对照（McNemar / paired bootstrap）。

## 与 designflow 的对接（#3 依赖链）
1. designflow 据 `reports/waveview_need_image_handoff.md` 恢复 11 题「原意图需看图」形态 → 跑无多模态新基线（预期大量 fail）。
2. designflow 用本 VQA tool 对同一批题再评（唯一变量=有没有 VQA）→ 对比报告「哪些题靠 VQA 翻转」。
3. vision 用合成数据/SFT/RL 强化基模（#4）→ 再评 → 证明显著提升（对照+显著性）。
本仓库仅交付工具+基线；跨线实跑由 designflow shard 执行（vision 不擅改 designflow 任务书）。
