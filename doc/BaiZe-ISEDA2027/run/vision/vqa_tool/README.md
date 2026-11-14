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

---

## #4 合成数据管线 + 基模能力自测基线（`synth_waveform_qa.py`）

把 #4 的「训练/合成数据管线」与「合成数据自测基线」做成可复算的确定性脚本（seed 固定）。

### 文件
| 文件 | 作用 |
|:--|:--|
| `synth_waveform_qa.py` | 合成管线主脚本：生成 SFT 数据集 / 跑自测基线 |
| `sft.jsonl` | 150 条多模态 SFT 记录（25/技能 × 6 技能），Qwen3.5-2B VL chat 格式（user=[image,text] / assistant=gt） |
| `dataset_meta.json` | 数据集 manifest（seed/counts/tau/skills） |
| `synth_selftest_baseline.json` | **基模能力自测基线**（pre-SFT/RL 底数，#4 配对对照的 before） |
| `sft_images/`、`selftest_images/` | 合成波形图（带网格，VLM 可「数格读数」）—— **已 gitignore，可由脚本确定性再生** |

### 架构口径（重要）
Qwen3.5-2B 是**原生多模态 VL 模型**（`Qwen3_5ForConditionalGeneration`，config 含 `image_token_id`），
**直接吃像素**。本管线把图喂给 VLM，**不做**「图→文本桥」降级——用户 09:5x 令明确反对把视觉判断
降级为脚本/文本；文本桥会把「看图」偷换成「读数」，无法度量多模态增益。#4 强化的是基模「看图」能力。

### 6 个识图技能（覆盖 waveview α/β）
`type_classification` / `cycle_count` / `amplitude_read` / `freq_comparison` / `duty_cycle` / `rise_edge`

### RL 奖励设计（预注册，🚫 不许看结果再调判据）
- 回归任务（cycle_count / amplitude_read / duty_cycle）：`R = exp(-rel_err/tau)`，`tau=0.15`（与 v11 TOL 对齐）——连续平滑，消除 v2–v11「全同档=无信号」病灶
- 二值任务（type / freq_compare / rise）：`R = 1.0/0.0`
- 群体：`group_std(rewards)`；为 0 则该组 advantage=0（v2–v4 病灶检测）
- **预注册判据**：成功 = post-RL ≥ post-SFT + 5pp，McNemar p<0.05，≥3 seeds 一致，cheat_rate=0；负结果同样上报

### 用法
```bash
PY=/nas_data/app.e0031982/miniforge3/envs/py310/bin/python
# 生成 SFT 数据集（150 题，渲染图像 + sft.jsonl）
$PY synth_waveform_qa.py --n_per_skill 25
# 跑自测基线（查常驻 VQA server，落 synth_selftest_baseline.json）
$PY synth_waveform_qa.py --selftest --selftest_n 2
```

### 自测基线结果（pre-SFT/RL · 2026-11-14 · native VL · GPU5:30001）
`synth_selftest_baseline.json`：**n=12，correct=7，acc=0.5833，mean_reward=0.6257**。

| skill | n | acc | mean_reward | 解读 |
|:--|--:|--:|--:|:--|
| type_classification | 2 | 1.00 | 1.00 | ✅ 四类波形辨识已掌握 |
| freq_comparison | 2 | 1.00 | 1.00 | ✅ 两波形频率比较已掌握 |
| rise_edge | 2 | 1.00 | 1.00 | ✅ 上升沿 sharp/gradual 已掌握 |
| cycle_count | 2 | 0.50 | 0.55 | 🟠 周期计数偏差（3→4） |
| amplitude_read | 2 | 0.00 | 0.20 | 🔳 峰峰值欠读（6→2、7→6） |
| duty_cycle | 2 | 0.00 | 0.00 | 🔳 25% 一律误读为 50% |

**这正是 #4（SFT/RL 强化）要攻的缺口**：精确计数、幅值读数、占空比区分。
同一脚本同一 seed 再生的图像/问题将用于 post-SFT/RL 配对对照（McNemar / paired bootstrap）。
与既有手作基线（`baseline_waveform_vqa_results.json` n=9 acc=0.5556）一致：rise_edge/freq/type 强、
duty_cycle/amplitude/cycle 弱——缺口稳定可复现，适合做强化对照。
