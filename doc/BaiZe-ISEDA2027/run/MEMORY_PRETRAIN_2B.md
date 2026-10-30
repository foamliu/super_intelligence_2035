# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

> 🆕 2026-10-30 14:35 #959：**S1监控iter21690健康·loss~2.217稳态微降·0NaN·grad-norm稳(0.086~0.210)·~560K tok/s·ckpt@20000·TB6006OK**。iter 21690/700k(3.10%): lm loss last10 avg≈2.217[2.205~2.234], 全程0 NaN/Inf. LR=1e-3恒定, GBS=256, loss-scale=1.0. grad-norm last10 0.086~0.210(稳), iter21690温和gn=0.210(loss2.205), iter21430 spike(2.402/gn0.500)已恢复. ~7.5s/iter→~560K tok/s. 16卡.29 100%util(均~75GB/81GB). mem .29 1389G/2T(avail 512G). /nas_train 35T free(84%). ckpt@20000(10ckpt:2k~20k), next@22000(~310步~38min~15:13). TB6006 OK(0.0.0.0:6006 LISTEN). ETA~55天. 17:0x✅DONE. 10:0x✅DONE. 未完成指令：有(⑦PPL/passkey+RULER/needle eval, BLOCKED: 16/16 GPU满载训练; HF导出iter_18000✅=前置就绪, 待GPU空闲). WAITING=1(30min轮询). 📦 体积：TASK=30.2KB / MEMORY=~27.8KB(无需归档).
> 📦 §#958（10-30 14:17, S1监控iter21540健康·loss~2.225·0NaN·grad-norm极稳(0.075~0.155)·~566K tok/s·ckpt@20000）→ daily-memories/2026-10-30.md；**结论**：S1健康, loss~2.22稳态微降. 被#959更新。需要时再读。
> 📦 §#956（10-30 13:36, S1监控iter21210健康·loss~2.215·0NaN·grad-norm极稳(0.084~0.142)·~590K tok/s·ckpt@20000）→ daily-memories/2026-10-30.md；**结论**：S1健康, loss~2.22稳态微降. 被#957更新。需要时再读。
> 📦 §#955（10-30 13:17, S1监控iter21050健康·loss~2.222·0NaN·grad-norm极稳(0.083~0.107)·~574K tok/s·ckpt@20000）→ daily-memories/2026-10-30.md；**结论**：S1健康, loss~2.22稳态微降. 被#956更新。需要时再读。
> 📦 §#954（10-30 12:54, S1监控iter20860健康·loss~2.236·0NaN·grad-norm极稳·~591K tok/s·ckpt@20000）→ daily-memories/2026-10-30.md；**结论**：S1健康, loss~2.24稳态微降. 被#955更新。需要时再读。
> 📦 §#953（10-30 12:35, S1监控iter20700健康·loss~2.220·0NaN·grad-norm极稳(0.083~0.187)·~592K tok/s·ckpt@20000）→ daily-memories/2026-10-30.md；**结论**：S1健康, loss~2.22稳态微降. 被#954更新。需要时再读。
> 📦 §#952（10-30 12:14, S1监控iter20530健康·loss~2.220·0NaN·grad-norm极稳(0.088~0.111)·~566K tok/s·ckpt@20000）→ daily-memories/2026-10-30.md；**结论**：S1健康, loss~2.22稳态微降. 被#953更新。需要时再读。
> 📦 §#951（10-30 11:55, S1监控iter20378健康·loss~2.247·0NaN·grad-norm极稳·~556K tok/s·ckpt@20000）→ daily-memories/2026-10-30.md；**结论**：S1健康, loss~2.25稳态微降. 被#952更新。需要时再读。
> 📦 §#950（10-30 11:34, S1监控iter20204健康·loss~2.216·0NaN·grad-norm极稳·~568K tok/s·ckpt@20000）→ daily-memories/2026-10-30.md；**结论**：S1健康, loss~2.22稳态微降. 被#951更新。需要时再读。
> 📦 §#949（10-30 11:11, S1监控iter20010健康·loss~2.236·0NaN·~574K tok/s·ckpt@20000·prune dry-run@20k完成）→ daily-memories/2026-10-30.md；**结论**：S1健康, loss~2.24稳态, prune dry-run@20k keep3删7. 被#950更新。需要时再读。
> 📦 §#948（10-30 10:50, S1监控iter19850健康·loss~2.221·0NaN·~574K tok/s·ckpt@18000）→ daily-memories/2026-10-30.md；**结论**：S1健康, loss~2.22稳态. 被#949更新。需要时再读。
> 📦 §#947（10-30 10:23, S1监控iter19630健康·✅HF导出iter_18000+check_rope.py PASS）→ daily-memories/2026-10-30.md；**结论**：HF导出成功(2.22B, 323 tensors), check_rope PASS(56层/4注意力/max_pos=1M/theta=1e6). 被#949更新。需要时再读。
> 📦 §#929~#946（10-30 04:02~10:02, #929~#946共18轮, S1监控iter16530→19460, 全程健康·loss~2.23~2.29稳态微降·0NaN·多次温和grad-norm spike均秒恢复·~554~629K tok/s·ckpt 16000→18000）→ daily-memories/2026-10-30.md；**结论**：S1全程健康稳定, loss从~2.29微降至~2.23, ckpt从16000→18000, 所有spike均自恢复, abf_plan.py/长上下文数据体检/prune dry-run均完成. 被#947更新。需要时再读。
> 📦 §#928及更早（#918~#928, 10-30 00:15~03:41）已归档 → daily-memories/2026-10-30.md；**结论**：S1 iter14720~16370全程健康, loss~2.25~2.28稳态, 0NaN, ~554~580K tok/s, ckpt从14000→16000, 多次温和grad-norm spike均恢复. 需要 #918~#928 细节时读当日 daily-memories。
> 📦 §#894~#917（10-29 16:05~23:57, S1监控iter10680~14570, 24轮连续健康·0NaN·ckpt@10000→14000·loss 2.27~2.35·check_rope PASS·b67bf0c pushed·17:0x②实质完成）→ daily-memories/2026-10-29.md。需要时再读。
> 📦 §#884–#893（10-29 12:37–15:45, 10条S1监控流水·iter8950→10530·loss~2.34–2.40·ckpt@8000→10000）→ daily-memories/2026-10-29.md；**结论**：S1全程健康, 0NaN, ~580K tok/s, 多次grad-norm spike均自恢复。被#894+更新。需要时再读。
> 📦 §#834~#879（10-28 19:1x~10-29 11:00, S1监控iter270~8103健康×~35轮）→ daily-memories/2026-10-{28,29}.md；**结论汇总**：S1从iter270→8103持续健康, loss 6.12→2.376单调下降, 0 NaN, 559-665K tok/s, ckpt 2k→8k, pre-blend+nw=8恢复613K基线, check_rope PASS, abf_plan.py✅。需要时再读。


> - 未完成指令：有（① en_v1_4 pre-blend ✅ ② activate ✅ ③ smoke ✅ ④ **16卡S1** ✅RUNNING(iter 21540/700k=3.08%, ~566K tok/s, 0 NaN, loss ~2.225 稳态微降, ckpt@20000, grad-norm极稳) ⑤ **check_rope.py ✅PASS**(56层/4注意力/max_pos=1M/theta=1e6) ⑥ lr-decay-shape exponential ✓(S1恒定1e-3, Decay段验证待Decay起跑) ⑦ 长上下文ABF[数据体检✅, abf_plan.py✅, HF ckpt@18000已导出, 零训练PPL/passkey基线待GPU空闲] ⑧ 项目目录脚本&文档 ✅(16脚本+9配置+2docs+README 19.4KB, git clean)）。**仅剩⑦**（需GPU空闲跑inference, 训练占用全部16卡~55天）。prune dry-run@20k✅(keep3删7=28GB, apply@50k)。ETA ~55天。WAITING=1(30min轮询)。
> - 📦 体积：TASK=30.2KB / MEMORY=27.6KB（无需归档）

> 📦 §#798（22:0x归因：613K→480K=固定开销摊薄 + 方案A gbs256 + num_workers降4 commit 8b8bf31）→ daily-memories/2026-10-26.md。**⚠️ num_workers=4只在.29生效，.12仍8→#801修复**。

> 📦 §#797 流水（2026-10-26 23:05，RoPE θ 修复：选路径(ii) `--rotary-base` CLI + recipe 透传，commit ae3a093，三重验证 PASS；rank15 结论=θ非崩因；data 阻塞 l1_en_hq）已压缩 → daily-memories/2026-10-26.md；**结论**：θ=1e6 修复 commit ae3a093，静态/--help/mock 三重验证 PASS；**#799 已运行时确认 θ=1e6 + 0崩**（DDP 崩因=DETAIL wrapper，非 θ）；data 阻塞已由 #799 解除。需要时再读。

> 📦 §#796/#794/#795/#793/#792/#791 流水（2026-10-26）→ daily-memories/2026-10-26.md。**结论汇总**：#796 rendezvous OK 但 rank15 崩(EOFError 修复 ae964bc)；#794 预训练构想报告 22KB+ETA 54d；#795 全令闭合 WAITING=1；#793 吞吐报告补写；#792 双机16K=613,992/32K CP2=351,526(commit 594c9cb1b)；#791 FA3 CP patch+首跑通。需要时再读。

> 📦 §#768~#790 流水（2026-10-24~10-26，吞吐调优/CUDA Graph根因/双机实测/报告交付）已归档 → daily-memories/2026-10-{24,25,26}.md & ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：CUDA Graph顶格停滞=吞吐下降真因(关graph修复)；双机16K=613,992 tok/s；32K CP2=351,526；RoPE θ=1e6修复commit ae3a093；多份报告已交付。需要时再读。

> 📦 §#766（2026-10-24 15:0x）已归档 → daily-memories/2026-10-24.md；**结论**：CUDA12.9驱动级BLOCKED(570<575),7/7建议全闭合,吞吐上限305K确认,data未就绪。需要时再读。

> 📦 §#765（2026-10-24 13:5x）已归档 → daily-memories/2026-10-24.md；**结论**：R2c全部完成,e18=305K新纪录,e19OOM,e20=300K,上限判定305K,6/7建议完成。需要时再读。

> 📦 §#764（2026-10-24 12:3x）已归档 → daily-memories/2026-10-24.md；**结论**：R2c启动,e18 preliminary 306K(后精修305K),R2b全部完成。需要时再读。

> 📦 §#762（2026-10-24 08:30）已归档 → daily-memories/2026-10-24.md；**结论**：idle heartbeat，三份报告在盘，无新指令。需要时再读。

> 🆕 **2026-10-24 11:0x #763：R2已跑完5组·R2b结果见#764**：R2 ① e10 MBS4=OOM ② e11 MBS3=OOM(77.8GB) ③ e12 CE-fusion=296K ④ e13 NCCL-Ring=297K ⑤ e14 recompile=AssertionError。R2b 5组结果详见 #764。
> 📦 §#760~#761 流水（2026-10-24 06:08~07:20，2 条 idle heartbeat）已归档 → daily-memories/2026-10-24.md；**结论**：三份10-23报告均在盘，无新指令。需要时再读。
> 📦 §#758~#759 流水（2026-10-24 03:4x~04:57，2 条 idle heartbeat 复核三份报告无误）已归档 → daily-memories/2026-10-24.md；**结论**：三份10-23报告均在盘+committed，无新指令。需要时再读。
> 📦 §#757（2026-10-24 02:3x）已归档 → daily-memories/2026-10-24.md；**结论**：吞吐优化10/10完成，新纪录297K tok/s(+19.4% vs 249K) @ FP8 TW+CG协同效应，HTML报告已交付(commit 74ef3e523)。需要时再读。
> 📦 §#754~#755 流水（2026-10-23 20:5x~21:5x，2 条 idle heartbeat 复核两份报告无误）已归档 → daily-memories/2026-10-23.md；**结论**：两份10-23报告复核无误，无新指令。需要时再读。
> 📦 §#752（2026-10-23 18:2x）已归档 → daily-memories/2026-10-23.md；**结论**：长上下文3模型评测完成，Qwen3.5-2B独享1M上下文且全程最快(64K 70.8K→1M 11.3K tok/s)，HTML报告已交付(commit a04b4503b)。需要时再读。
> 📦 §#749~#751 流水（2026-10-23 13:0x~14:0x，3 条 idle heartbeat 复核 decay 修复报告无误）已归档 → daily-memories/2026-10-23.md；**结论**：decay 修复报告复核无误（v2 44.97/6.21→decay-5000 58.97/28.02），无新指令。需要时再读。

> 📦 §#747~#748 流水（2026-10-23 12:2x~12:5x，2 条 idle heartbeat 复核 decay 修复报告无误 + 归档 #740~#746）已归档 → daily-memories/2026-10-23.md；**结论**：decay 修复报告复核无误，无新指令。需要时再读。
> 📦 §#740~#746 流水（2026-10-23 09:4x~12:2x，7 条：CX6 sdpa 修复 5/6 → CX6 6/6 完成 → decay 修复 HTML 报告交付 #744 → 3 条 idle heartbeat）已归档 → daily-memories/2026-10-23.md；**结论**：decay-5000 全部评测完成（CS8=58.97%/CX6=28.02%），HTML 报告已交付 commit `ae9e1e780`。需要时再读。
> 🎉 **2026-10-23 08:4x #739：✅ decay 5000 步训练完成 + HF 转换 + CS8 首评 58.97%（vs 基线 61.03%，Δ−2.06pp）→ decay 修复成功**：
> - **训练完成**：step 5000/5000 ✅，final loss **0.9946**，val@5000=**0.9977(PPL 2.712)**、test=0.9955(PPL 2.706)，**0 NaN / 0 skip 全程**，ckpt@5000 已存 ✅（latest=5000）。5 点 val 单调降 1.1016→1.0622→1.0346→1.0124→0.9977。
> - **HF 转换完成**：`tools/checkpoint/megatron_to_hf_mup.py`（补 vocab truncate 129408→129280 修复）→ `out/decay_5000_hf/`（1.350B params，烟测 "Paris" ✓，logits finite ✓）。
> - **14 集 eval CS8 = 58.97% (8/8)**：hellaswag .5468 / arc_easy .6536 / boolq .7003 / arc_challenge .3840 / sciq .8710 / piqa .6904 / winogrande .5675 / openbookqa .3040（acc_norm 优先，与基线同口径）。
>   - 对比：基线 step_532000 CS8=**61.03%** → **Δ−2.06pp**；旧 decay v2=44.97%（−16pp 训坏）。**结论：decay 5000 步成功（能力基本保持，非暴跌）**。
> - **CX6 1/6**（mmlu=0.4897）：gsm8k/math500/bbh 崩于 flash_attn varlen_fwd（预存 harness 兼容问题，基线同样崩 #658），humaneval/mbpp 报 unsafe-code。已把 config 改 sdpa + confirm_run_unsafe_code，**5 任务重跑中**（.29，cx6_fix_eval.sh）。
> 📦 §#717–§#737 decay 5000 步训练健康监控链（2026-10-22 14:5x ~ 10-23 06:5x，step 20→4660/5000）已归档 → daily-memories/2026-10-22.md & 2026-10-23.md；**结论**：全程健康 0NaN/0skip，loss 1.176→1.003 单调递降，ckpt 每 500 步存（@500…@4500），decay 训练成功。逐条监控流水已合并为本指针。需要时再读各日 daily 文件。

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

> 📦 §#657 流水（2026-10-21 04:5x, 基线 eval CS8=61.03% + L1 脚本就绪）已归档 → daily-memories/2026-10-21.md；**结论**：起点 61.03% ≫ decay v2 final 44.97% → decay 训坏模型(-16pp)；L1 实验脚本(baize_xmodel25_decay_L1.py/.sh)就绪待 CX6 完成后启动。需要时再读。

> 📦 §#650~#656 流水（2026-10-21 00:2x~03:0x, 7 条稳态心跳「等用户批准跑基线 eval」）已归档 → daily-memories/2026-10-21.md；**结论**：均无新指令，重复确认 .29 GPU 全空、训练完成、起点 ckpt 在盘、等批准。需要时再读。

> 📦 **[已归档] #643~#649 流水（2026-10-20 19:1x~23:4x, 7 条稳态确认 + 归因取证 #648 + 报告重做 #649）→ daily-memories/2026-10-20.md；**结论**：14:2x 评测令已闭环（CS8=44.97%/CX6=6.21%，中文报告 16314B）；#648 归因取证 4 问完成（双移位bug/LR过高/code26epoch/step0=11.72）；#649 报告 v2 重做提交（Xmodel-2.5 final 唯一主对照 + 失败归因节）。需要时再读。**
> 📦 **[已归档] #634~#641 流水（2026-10-20 14:33~18:2x, 评测 decay v2 final 14 集全过程）→ daily-memories/2026-10-20.md；**结论**：14/14 eval 完成 CS8=44.97%(8/8)/CX6=6.21%(6/6)，中文报告 16314B@18:32 + EXPERIMENTS:430「Decay v2 final」+commit `pretrain eval:` e5ecf5d35/3338566a5；含 sdpa 修复、humaneval/mbpp=0.0%、bbh=3.98%。需要时再读。**
>
> 📦 **[已归档] #614 crash→resume 流水（2026-10-20 04:00, .29 主 run 02:45 crash@step19920 NCCL timeout→resume from step_18000, PID1604723, step18020+）→ daily-memories/2026-10-20.md；结论：crash 确认+resume 成功+8×GPU 满载+0error，ETA~10:30。需要时再读。**

- STAGE: **✅ decay 5000 步训练 + 14 集评测全完成 + ✅ 吞吐优化 7/7 建议全部闭合（305K tok/s 上限确认）** —— decay: CS8=58.97% / CX6=28.02%；吞吐: 249K→305K(+22.5%), e18=MBS3+CG+FP8 TW 新纪录, #2 CUDA12.9=❌驱动级BLOCKED(570.x需575+)。报告 @ `reports/report_pretrain_2b_throughput_optim_zh.html` + `reports/report_pretrain_decay_repair_zh.html`。**等 data 就绪（5源迁移→/nas_env 完成）起全量预训练**。
  - PHASE: **吞吐优化全部完成_等data就绪起全量预训练** — 7/7 建议闭合：#1✅(e18=305K) #2❌BLOCKED(驱动570.x<575,无sudo) #3✅ #4✅ #5✅ #6✅ #7✅。吞吐上限=305K tok/s(8×H100-80GB, 当前驱动条件)。.29 8×H100 空闲。data: en_v1_4分词110/110✅, 5源迁移→/nas_env早期进行中。loop 存活，30 min 长轮询。
- 轮询状态：**#766（15:0x，#2 CUDA12.9驱动级BLOCKED实测→7/7建议全闭合→吞吐上限305K definitively confirmed→等data就绪起全量预训练）**：本轮纯诊断+报告更新（无GPU实验）。.29 8×H100 空闲，无新运维指令，30 min 长轮询。
> 📦 [已归档] 🩺 v2 巡检+crash #610~#634（10-20）→ daily-memories/2026-10-20.md；**结论**：v2 全程健康 0error、崩溃前无先兆、硬件瞬时故障无永久隐患。
> 📦 [已归档] 🩺 v2 巡检 #566~#609（10-19）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、ckpt step_12000~18000 完好、稳态~12s/step、#588 push 失败由 #589 补推闭环。
> 📦 [已归档] v2 巡检+修复 #472~#565（10-17~10-18）→ daily-memories/2026-10-17.md & -18.md；**结论**：v2 健康 0error、_orig_mod 修复 verify_save@step20 通过、中继恢复、v5 三交付物 committed。
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
- P-9（P-9.1 ✅ / P-9.2 ✅ / P-9.3 ✅ / P-9.4 ✅ / **P-9.5 ✅ COMPLETE** — 崩溃修复 + 5-way 归因 + HTML / P-9.6①② ✅ / P-9.7 ✅ / P-9.8 ✅ COMPLETE → delayed FP8 可用于 P-8 / **P-9.9 ✅ COMPLETE → tensorwise T1/T4 FAIL → P-8 沿用 delayed** / **P-9.10 ① ✅ sglang ✅ 可用(vllm env) [第109次更正] → eager 下界✅已测 + sglang 上界待 HF 转换补测，② ✅ CO