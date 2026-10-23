# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1
> 🆕 **2026-10-23 14:0x #751：⏸ 例行唤醒·idle heartbeat·decay 修复报告复核无误·无新指令**：
> - 复核确认：decay 修复报告 `doc/BaiZe-ISEDA2027/reports/report_pretrain_decay_repair_zh.html`（23878B/197 行，§1–§9+溯源）在盘，commit `ae9e1e780` 已推送。数字与运维令一致：v2 44.97/6.21 → decay-5000 58.97/28.02（+14.0/+21.8pp），vs 基线 61.03 Δ−2.06pp；§8 给 4 候选（①延长 decay 20000 步 ②对齐 11 源配比 ③补 CX6 基线 ④超参微调），各附成本/风险/ETA，满足「≥3 候选」要求。
> - 状态确认：.29 8×H100 全空闲（0 MiB/0%），无 torchrun/lm_eval/pretrain 进程。git fetch 后无 ahead/behind、无新远端提交。
> - 无新运维指令 → 30 min 长轮询例行唤醒，WAITING 保持 1。
> 📦 体积：TASK=23500B / MEMORY=~28.6KB（均≤32KB✓，本轮归档 0KB）。
> 🆕 **2026-10-23 13:3x #750：⏸ 例行唤醒·idle heartbeat·decay 修复报告复核无误·无新指令**：
> - 复核确认：decay 修复报告 `doc/BaiZe-ISEDA2027/reports/report_pretrain_decay_repair_zh.html`（23878B/197 行，§1–§9+溯源）在盘，commit `ae9e1e780` 已推送。数字与运维令一致：v2 44.97/6.21 → decay-5000 58.97/28.02（+14.0/+21.8pp），vs 基线 61.03 Δ−2.06pp；§8 给 4 候选（①延长 decay 20000 步 ②对齐 11 源配比 ③补 CX6 基线 ④超参微调），各附成本/风险/ETA，满足「≥3 候选」要求。
> - 状态确认：.29 8×H100 全空闲（0 MiB/0%），无 torchrun/lm_eval/pretrain 进程。git fetch 后无 ahead/behind、无新远端提交。
> - 无新运维指令 → 30 min 长轮询例行唤醒，WAITING 保持 1。
> 📦 体积：TASK=21272B / MEMORY=27549B（均≤32KB✓，本轮归档 0KB）。
> 🆕 **2026-10-23 13:0x #749：⏸ 例行唤醒·idle heartbeat·decay 修复报告复核无误·无新指令**：
> - 复核确认：decay 修复报告 `doc/BaiZe-ISEDA2027/reports/report_pretrain_decay_repair_zh.html`（23878B/197 行，§1–§9+溯源）在盘，commit `ae9e1e780` 已推送。数字与运维令一致：v2 44.97/6.21 → decay-5000 58.97/28.02（+14.0/+21.8pp），vs 基线 61.03 Δ−2.06pp；§8 给 4 候选（①延长 decay 20000 步 ②对齐 11 源配比 ③补 CX6 基线 ④超参微调），各附成本/风险/ETA，满足「≥3 候选」要求。
> - 状态确认：.29 8×H100 全空闲（0 MiB/0%），无 torchrun/lm_eval/pretrain 进程。git fetch 后无 ahead/behind、无新远端提交。
> - 无新运维指令 → 30 min 长轮询例行唤醒，WAITING 保持 1。
> 📦 体积：TASK=21272B / MEMORY=27549B（均≤32KB✓，本轮归档 0KB）。

> 🆕 **2026-10-23 12:2x #747：⏸ 例行唤醒·idle heartbeat·decay 修复报告复核无误·无新指令**：
> - 复核确认：decay 修复报告 `doc/BaiZe-ISEDA2027/reports/report_pretrain_decay_repair_zh.html`（23878B/197 行，§1–§9+溯源）在盘，commit `ae9e1e780` 已推送。数字与运维令一致：v2 44.97/6.21 → decay-5000 58.97/28.02（+14.0/+21.8pp），vs 基线 61.03 Δ−2.06pp；§8 给 4 候选（①延长 decay 20000 步 ②对齐 11 源配比 ③补 CX6 基线 ④超参微调），各附成本/风险/ETA，满足「≥3 候选」要求。
> - 状态确认：.29 8×H100 全空闲（0 MiB/0%），无 torchrun/lm_eval/pretrain 进程（pgrep 仅本 agent+ssh）。git fetch + pull --rebase 后无 ahead/behind、无新远端提交。
> - 无新运维指令 → 30 min 长轮询例行唤醒，WAITING 保持 1。
> 📦 体积：TASK=21272B / MEMORY=29765B（均≤32KB✓，本轮归档 0KB）。

> 🆕 **2026-10-23 12:5x #748：⏸ 例行唤醒·idle heartbeat·decay 修复报告复核无误·无新指令·归档 #740~#746**：
> - 复核确认：decay 修复报告 `doc/BaiZe-ISEDA2027/reports/report_pretrain_decay_repair_zh.html`（23878B/197 行，§1–§9+溯源）在盘，commit `ae9e1e780` 已推送。数字与运维令一致：v2 44.97/6.21 → decay-5000 58.97/28.02（+14.0/+21.8pp），vs 基线 61.03 Δ−2.06pp。
> - 状态确认：.29 8×H100 全空闲（0 MiB/0%），无 torchrun/lm_eval 进程。git fetch 后无 ahead/behind、无新远端提交。
> - 归档 #740~#746 → daily-memories/2026-10-23.md（7 条心跳/CX6 完成流水原文搬迁，留 1 行指针）。
> - 无新运维指令 → 30 min 长轮询例行唤醒，WAITING 保持 1。
> 📦 体积：TASK=21272B / MEMORY=~28KB（均≤32KB✓，本轮归档 ~2.7KB → daily-memories/2026-10-23.md）。
> 📦 §#740~#746 流水（2026-10-23 09:4x~12:2x，7 条：CX6 sdpa 修复 5/6 → CX6 6/6 完成 → decay 修复 HTML 报告交付 #744 → 3 条 idle heartbeat）已归档 → daily-memories/2026-10-23.md；**结论**：decay-5000 全部评测完成（CS8=58.97%/CX6=28.02%），HTML 报告已交付 commit `ae9e1e780`。需要时再读。
> 🎉 **2026-10-23 08:4x #739：✅ decay 5000 步训练完成 + HF 转换 + CS8 首评 58.97%（vs 基线 61.03%，Δ−2.06pp）→ decay 修复成功**：
> - **训练完成**：step 5000/5000 ✅，final loss **0.9946**，val@5000=**0.9977(PPL 2.712)**、test=0.9955(PPL 2.706)，**0 NaN / 0 skip 全程**，ckpt@5000 已存 ✅（latest=5000）。5 点 val 单调降 1.1016→1.0622→1.0346→1.0124→0.9977。
> - **HF 转换完成**：`tools/checkpoint/megatron_to_hf_mup.py`（补 vocab truncate 129408→129280 修复）→ `out/decay_5000_hf/`（1.350B params，烟测 "Paris" ✓，logits finite ✓）。
> - **14 集 eval CS8 = 58.97% (8/8)**：hellaswag .5468 / arc_easy .6536 / boolq .7003 / arc_challenge .3840 / sciq .8710 / piqa .6904 / winogrande .5675 / openbookqa .3040（acc_norm 优先，与基线同口径）。
>   - 对比：基线 step_532000 CS8=**61.03%** → **Δ−2.06pp**；旧 decay v2=44.97%（−16pp 训坏）。**结论：decay 5000 步成功（能力基本保持，非暴跌）**。
> - **CX6 1/6**（mmlu=0.4897）：gsm8k/math500/bbh 崩于 flash_attn varlen_fwd（预存 harness 兼容问题，基线同样崩 #658），humaneval/mbpp 报 unsafe-code。已把 config 改 sdpa + confirm_run_unsafe_code，**5 任务重跑中**（.29，cx6_fix_eval.sh）。
> 📦 §#737 流水（2026-10-23 06:5x，decay 5000 步监控 step 4660/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step4660 loss1.003 val@4000=1.0124 0NaN/0skip，ckpt@4500已存，训练健康。被 #738 监控更新取代。需要时再读。
> 📦 §#736 流水（2026-10-23 06:2x，decay 5000 步监控 step 4500/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step4500 loss1.004 val@4000=1.0124 0NaN/0skip，ckpt@4500已存，训练健康。被 #737 监控更新取代。需要时再读。
> 📦 §#735 流水（2026-10-23 06:1x，decay 5000 步监控 step 4470/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step4470 loss1.009 val@4000=1.0124 0NaN/0skip，ckpt@4000已存，训练健康。被 #736 监控更新取代。需要时再读。
> 📦 §#734 流水（2026-10-23 05:5x，decay 5000 步训练健康监控 step 4340/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step4340 loss1.009 val@4000=1.0124 0NaN/0skip，ckpt@4000已存，训练健康。被 #735 监控更新取代。需要时再读。
> 📦 体积：TASK=19252B / MEMORY=25038B（均≤32KB✓，本轮归档 0KB）。
> 📦 §#732 流水（2026-10-23 05:0x，decay 5000 步训练健康监控 step 4120/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step4120 loss1.0258 val@4000=1.0124 0NaN/0skip，ckpt@4000已存，训练健康。被 #733 监控更新取代。需要时再读。
> 📦 §#730 流水（2026-10-23 04:1x，decay 5000 步训练健康监控 step 3890/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step3890 loss1.0245 val@3000=1.0346 0NaN/0skip，ckpt@3500已存，训练健康。被 #731 监控更新取代。需要时再读。
> 📦 §#729 流水（2026-10-23 03:5x，decay 5000 步训练健康监控 step 3800/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step3800 loss1.027 val@3000=1.035(PPL 2.81) 0NaN/0skip，ckpt@3500已存，训练健康。被 #730 监控更新取代。需要时再读。
> 📦 §#728 流水（2026-10-23 03:3x，decay 5000 步训练健康监控 step 3720/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step3720 loss1.033 val@3000=1.035(PPL 2.81) 0NaN/0skip，ckpt@3500已存，训练健康。被 #729 监控更新取代。需要时再读。
> 📦 §#727 流水（2026-10-23 02:4x，decay 5000 步训练健康监控 step 3450/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step3450 loss1.037 val@3000=1.035(PPL 2.81) 0NaN/0skip，ckpt@3000已存，训练健康。被 #728 监控更新取代。需要时再读。
> 📦 §#726 流水（2026-10-23 01:3x，decay 5000 步训练健康监控 step 3090/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step3090 loss1.054 val@3000=1.035(PPL 2.81) 0NaN/0skip，ckpt@3000已存，训练健康。被 #727 监控更新取代。需要时再读。

> 📦 §#725 流水（2026-10-23 00:2x，decay 5000 步训练健康监控 step 2770/5000）已归档 → daily-memories/2026-10-23.md；**结论**：step2770 loss1.074 val@2000=1.062 0NaN/0skip，ckpt@2500已存，训练健康。被 #726 监控更新取代。需要时再读。

> 📦 §#724 流水（2026-10-22 23:0x，decay 5000 步训练健康监控 step 2420/5000）已归档 → daily-memories/2026-10-22.md；**结论**：step2420 loss1.087 val@2000=1.062 0NaN/0skip，ckpt@2000已存，训练健康。被 #725 监控更新取代。需要时再读。

> 📦 §#723 流水（2026-10-22 22:0x，decay 5000 步训练健康监控 step 2070/5000）已归档 → daily-memories/2026-10-22.md；**结论**：step2070 loss1.100 val@2000=1.062 0NaN/0skip，ckpt@2000已存，训练健康。被 #724 监控更新取代。需要时再读。

> 📦 §#721 流水（2026-10-22 19:3x，decay 5000 步训练健康监控 step 1390/5000）已归档 → daily-memories/2026-10-22.md；**结论**：step1390 loss1.140 0NaN/0skip，ckpt@1000已存，训练健康。被 #722 监控更新取代。需要时再读。

> 📦 §#720 流水（2026-10-22 18:3x，decay 5000 步训练健康监控 step 1040/5000）已归档 → daily-memories/2026-10-22.md；**结论**：step1040 loss1.156 val@1000=1.102 0NaN/0skip，ckpt@1000已存，训练健康。被 #721 监控更新取代。需要时再读。

> 📦 §#719 流水（2026-10-22 17:1x，decay 5000 步训练健康监控 step 720/5000）已归档 → daily-memories/2026-10-22.md；**结论**：step720 loss1.176 0NaN/0skip，ckpt@500 已存，训练健康。被 #720 监控更新取代。需要时再读。

> 📦 §#717 流水（2026-10-22 14:5x，decay 5000 步启动 MBS=5+recompute）已归档 → daily-memories/2026-10-22.md；**结论**：MBS=5 OOM 排障→selective recompute→max 70.5GB，训练已启动 step20 loss1.446 0NaN/0skip。被 #718 监控更新取代。需要时再读。

> 📦 §#716 流水（2026-10-22 13:3x，1113 decay 冒烟测试通过 + 全量 20B 脚本就绪）已归档 → daily-memories/2026-10-22.md；**结论**：HF→Megatron 转换✅、冒烟 100 步✅(MBS=2)、vocab pad 129408 关键修复、pybind11 修复。被 #717 的 MBS=5+recompute 方案取代。需要时再读。

> 📦 §#715 流水（2026-10-22 09:1x，#715 A方案前置调查）已归档 → daily-memories/2026-10-22.md；**结论**：repo+ckpt+数据+转换全部定位完成。需要时再读。


> 📦 §#710 流水（2026-10-22 06:57，L2 健康监控 step 1830）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1830 loss0.92 0error，短途报告/EXPERIMENTS 同步。需要时再读。
> 📦 §#711 流水（2026-10-22 07:30，L2 健康监控 step 2000）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step2000 loss0.9652 0error，短途报告/EXPERIMENTS 同步至 step2000。需要时再读。
> 🆕 **2026-10-22 09:1x #715：📋 A方案前置调查（08:5x 新令 1113.sh + 20B）→ repo 克隆 + 脚本/数据/转换全部定位**：用户 08:5x 新令「pretrain 的 xmodel decay 参考官方 `train_decay_fp8_1113.sh`，使用 20B 数据」（**以 1113.sh 为准，覆盖 1120.sh**）。1113.sh 关键参数：48L/h1536/24head/GQA8/ffn3840/rope/swiglu/RMSNorm/use-mup(12.0/1.0/1.4/1.4)/GBS960/MBS5/seq3776/optimizer=muon(muon-matched-adamw-rms 0.2)/lr=1.66667e-3/decoupled-lr=1e-2/min-lr=1.04e-4/WSD exponential/lr-decay-iters=20000/warmup=0/wd=0.1/bf16/FP8 TE hybrid/amax-history=128/DP8(TP1/PP1)+distributed-optimizer/tokenizer deepseekv3/vocab=129280。train-iters=20e9/(960×3776)≈5560 步。
>
> **前置调查结果**：
> - **repo 克隆** ✅：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/Xmodel-2.5-code/`（含 megatron/ fork、pretrain_gpt.py、tools/checkpoint/convert.py、tokenizers/deepseekv3/、models/modeling_xmodel2.py）。
> - **起点 ckpt** ✅：`xmodel25_history/step_532000/pytorch_model.bin`（2.7GB, HF format, XmodelForCausalLM = Llama-style: 48L/h1536/GQA8/ffn3840/rope_theta=500000/RMSNorm/swiglu/use_mup, vocab=129280）。
> - **数据** ✅ 全部在 Megatron `text_document` 格式（`.bin`+`.idx`）：SFT=`data/mix_sft_tok/mix_sft_train_s{0,1,2,3}`、UFW L3=`data/full_ufw_l3/`(990G,154 shards)、Code=`data/full_ultradata_code_l3/`(481G,63 shards)、Math=`data/full_ultradata_math_l3/`(292G,67 shards)。**1113.sh 原 11 源在 `/data1/i_line_data/`（Xmodel 机器，我们没有）→ 需用现有 4 源配比（SFT 64%:L3 24%:code 8%:math 4%，与 v2 同口径）**。
> - **HF→Megatron 转换** ⚠️ **无现成 Xmodel loader**：repo `tools/checkpoint/` 有 `loader_llama_mistral.py`（支持 HF llama2/llama3/mistral/yi/qwen2.5，但**不支持 xmodel**）。但有 `megatron_to_hf_mup.py`（Megatron→HF，含完整权重映射 + XmodelConfig/XmodelForCausalLM import）→ **可逆向写 HF→Megatron converter**。
> - **.29 8×GPU** ✅ 全空（0MiB/0%），无 torchrun。
>
> **下一步（按序）**：① 写 HF→Megatron 转换脚本（逆向 `megatron_to_hf_mup.py` 的权重映射）→ 验证转换后 ckpt 可被 Megatron 加载；② 搭 DATA_PATH（现有 4 源 text_document 路径 + 权重）；③ 改 1113.sh（CHECKPOINT_PATH→我们路径、train-iters=5560、lr-decay-iters=5560、DATA_PATH→现有 4 源、--load→转换后 Megatron ckpt）；④ 100 步冒烟确认 loss 接住 stable 末点 → ⑤ 起 20B decay。
>
> **归档**：TASK 从 33.6KB→17.1KB（7 个已闭合运维指令块原文移入 ARCHIVE_OPERATOR_PRETRAIN.md，留 1 行指针）。
> 📦 体积：TASK=17516B(17.1K)/MEMORY=待测（均≤32KB✓）。

> 📦 §#714 流水（2026-10-22 08:44，L2 用户直令 kill 闭环）已归档 → daily-memories/2026-10-22.md；**结论**：L2 kill@step2370，.29 8卡空，方向转 A方案官方 Megatron。需要时再读。
> 📦 §#713 流水（2026-10-22 08:15，L2 健康监控 step 2200）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step2200 loss0.87 0error。需要时再读。
> 📦 §#712 流水（2026-10-22 08:05，L2 健康监控 step 2170）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step2170 loss0.97 0error。需要时再读。
> 📦 §#708 流水（2026-10-22 06:2x，L2 健康监控 step 1650）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1650 loss1.01 0error。需要时再读。
> 📦 §#707 流水（2026-10-22 05:5x，L2 健康监控 step 1490）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1490 loss1.02 0error。需要时再读。
> 📦 §#706 流水（2026-10-22 05:4x，L2 健康监控 step 1460 + 短途报告更新）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1460 loss1.11 0error，短途报告+EXPERIMENTS 同步至 step1460。需要时再读。
> 📦 §#705 流水（2026-10-22 05:1x，L2 健康监控 step 1320/5611）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1320 loss1.05 0error。需要时再读。
> 📦 §#704 流水（2026-10-22 04:4x，L2 健康监控 step 1150/5611）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1150 loss1.13 0error。需要时再读。
> 📦 §#703 流水（2026-10-22 04:3x，L2 健康监控 step 1100 + 短途报告更新）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step1100 loss1.05 0error，短途报告+EXPERIMENTS 同步至 step1100。需要时再读。
> 📦 §#702 流水（2026-10-22 04:0x，L2 监控 step 970/5611 无新令）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step970 loss1.07 0error。需要时再读。
> 📦 §#700 流水（2026-10-22 03:2x，L2 监控 step740/5611 无新令）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step740 loss1.14 0error，ckpt step_500 已存。需要时再读。
> 📦 §#699 流水（2026-10-22 02:5x，L2 监控 step630/5611 无新令）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step630 loss1.30 0error，ckpt step_500 已存。需要时再读。
> 📦 §#698 流水（2026-10-22 01:1x，L2 监控+短途报告更新）已归档 → daily-memories/2026-10-22.md；**结论**：L2 健康 step370、短途报告补齐 L1 CS8=59.03%+L2 运行中。需要时再读。
> 📦 §#697 流水（2026-10-22 00:5x，L1 CS8 eval=59.03%→L2启动）已归档 → daily-memories/2026-10-22.md；**结论**：L1 CS8=59.03%≥55%门槛→方向正确→L2启动PID2754486 step4/5611 step0=1.71。需要时再读。
> 📦 §#696 流水（2026-10-21 23:5x，L1 训练完成+CS8 eval 启动）已归档 → daily-memories/2026-10-21.md；**结论**：L1 5611步/20B/final loss=0.8687，teardown SIGABRT 无损，CS8 eval 启动。需要时再读。
> 📦 §#677~#695 流水（2026-10-21 16:1x~23:38，19 条 L1 健康监控 step 3330→5570/5611 + 09:3x 报告交付复核）已归档 → daily-memories/2026-10-21.md；**结论**：L1 全程健康 0 error、loss 0.86→0.82 平稳降、ckpt step_500~5500 已存 12 个、09:3x 两份报告在盘已推远端（commit c44ef1fea）。需要时再读。
> 📦 §#669~#676 流水（2026-10-21 12:1x~15:3x，7 条 L1 健康监控 + 报告溯源复核）已归档 → daily-memories/2026-10-21.md；**结论**：L1 全程健康 0 error、loss 平稳降、源数据溯源全通过。需要时再读。

> 📦 §#666~#668 流水（2026-10-21 10:4x~12:0x，3 条「09:3x 两份报告交付复核 + L1 健康监控」心跳 step 1670→2100/5611）已归档 → daily-memories/2026-10-21.md；**结论**：两份中文 HTML 报告 10:50/10:52 交付并推远端（commit c44ef1fea），源数据溯源 spot-check 全通过，L1 全程健康 0 error、loss 0.88→0.91 平稳。需要时再读。

> 📦 §#660~#665 流水（2026-10-21 07:5x~10:1x, 6 条 L1 健康监控心跳 step 820→1560/5611）已归档 → daily-memories/2026-10-21.md；**结论**：L1 全程健康 0 error，loss 1.03→0.90 稳步降，step0 1.75 vs v2 11.72 双移位修复确效，ckpt step_500/1000/1500 已存。需要时再读。
> 📦 §#659 流水（2026-10-21 06:3x, 🩺 L1 step 410/5611 健康 + 后续串行计划/2×2 判读逻辑）已归档 → daily-memories/2026-10-21.md；**结论**：L1 step0 loss=1.76 vs v2 11.72→双移位修复确效、loss 稳步降、串行计划 L1→CS8 eval→L2→L3→2×2 因子定主因定案。需要时再读。
> 📦 §#658 流水（2026-10-21 05:0x, 🚀 L1 训练启动 + 2×2 因子实验设计 + L2/L3 脚本就绪）已归档 → daily-memories/2026-10-21.md；**结论**：L1 烟测通过（step0 loss=1.76 vs v2 11.72→双移位修复确效），全量训练已启动 PID1430363/5611步=20B tok，L2/L3 脚本就绪，CX6 基线崩于 varlen_fwd 兼容性。需要时再读。

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

> 📦 **[已归档] #643~#649 流水（2026-10-20 19:1x~23:4x, 7 条稳态确认 + 归因取证 #648 + 报告重做 #649）→ daily-memories/2026-10-20.md；**结论**：14:2x 评测令已闭环（CS8=44.97%/CX6=6.21%，中文报告 16314B）；#648 归因取证 4 问完成（双移位bug/LR过高/code26epoch/step0=11.72）；#649 报告 v2 重做提交（Xmodel-2.5 final 唯一主对照 + 失败归因节）。需要时再读。**
> 📦 **[已归档] #634~#641 流水（2026-10-20 14:33~18:2x, 评测 decay v2 final 14 集全过程）→ daily-memories/2026-10-20.md；**结论**：14/14 eval 完成 CS8=44.97%(8/8)/CX6=6.21%(6/6)，中文报告 16314B@18:32 + EXPERIMENTS:430「Decay v2 final」+commit `pretrain eval:` e5ecf5d35/3338566a5；含 sdpa 修复、humaneval/mbpp=0.0%、bbh=3.98%。需要时再读。**
>
> 📦 **[已归档] #614 crash→resume 流水（2026-10-20 04:00, .29 主 run 02:45 crash@step19920 NCCL timeout→resume from step_18000, PID1604723, step18020+）→ daily-memories/2026-10-20.md；结论：crash 确认+resume 成功+8×GPU 满载+0error，ETA~10:30。需要时再读。**

- STAGE: **✅ decay 5000 步训练 + 14 集评测全完成，且「decay 修复完整中文 HTML 报告 + 下一步建议」已交付** —— **CS8=58.97% / CX6=28.02%**（vs 官方 final 65.40%/32.90%；vs 基线 CS8 61.03% Δ−2.06pp）。decay 修复成功（旧 v2=44.97%/6.21% 训坏）。报告 @ `doc/BaiZe-ISEDA2027/reports/report_pretrain_decay_repair_zh.html`。方向：用户 13:5x 令 decay 5000 步 + MBS=5 + Muon 0.2 + 无 warmup 已全部落地；23 日直令写 HTML 报告已交付。
  - PHASE: **decay_5000_已完成_报告已交付** — 训练完成（final loss 0.9946, val PPL 2.712, 0 NaN/0 skip），HF 转换✅，CS8=58.97%(8/8)✅，CX6=28.02%(6/6)✅。全部结果落盘 `nemo_experiments/eval_decay_5000_final/`；中文修复报告 `report_pretrain_decay_repair_zh.html` 已提交。loop 存活，.29 GPU 已释放。
- 轮询状态：**#750（13:3x，例行唤醒·idle heartbeat）**：decay 修复报告 `report_pretrain_decay_repair_zh.html` 复核无误（commit ae9e1e780 已推远端），含「训坏→修复」全历程 + 4 条按价值排序的下一步建议（①延长 decay 20000 步≈3天 ②对齐11源 ③补CX6基线 ④超参微调）。.29 8×H100 空闲，无新运维指令，30 min 长轮询。
> 📦 **[已归档] 🩺 v2 巡检+crash+收尾流水 #610~#634（2026-10-20 01:12~14:33：crash@02:45:25→resume step_18000→P0-a NCCL export+P0-b watchdog 落地→P2 硬件=transient 无永久故障→训练 10:30 收尾 step19979/19980、final ckpt 2.7GB）→ daily-memories/2026-10-20.md；**结论**：v2 全程健康 0error、崩溃前无先兆、硬件瞬时故障无永久隐患。需要时再读。**
> 📦 **[已归档] 🩺 v2 巡检流水 #566~#609（2026-10-19 00:11~23:51, step11904→19050 + hostname/节点澄清 .12→.29）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、ckpt step_12000~step_18000 完好、稳态~12s/step、#588 push 失败由 #589 补推闭环。需要时再读。**
> 📦 **[已归档] v2 巡检+修复流水 #472~#565（2026-10-17 02:16~10-18 23:24, step280→12770 + _orig_mod 修复 + P0 中继恢复 + 误判三连#548/#550/#551 纠偏 + v5 三交付物）→ daily-memories/2026-10-17.md & 2026-10-18.md；**结论**：v2 全程健康 0error、_orig_mod 修复 verify_save@step20 通过、中继恢复、v5 三交付物 committed。需要时再读。**
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
