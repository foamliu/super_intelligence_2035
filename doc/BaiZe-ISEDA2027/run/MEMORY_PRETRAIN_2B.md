# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

> 🆕 2026-10-26 07:33 #789：✅ 通宵攻坚交付物复核全通过（收敛3条✓：①真因=CUDA Graph 顶格停滞·报告「一句话结论」节在位 ②修复=关 graph·seq=8192 复测 0.978×基线≥0.7×✓ ③报告 16,888B≥15KB✓ + seqlen 报告 20,332B banner 已改 rev3✓ + EXPERIMENTS rev3/§五·6/§五·7✓ + TSV 16 行✓ + 早报已写✓ + 全 commit faa01ac34 已推✓）；GPU .29 8 卡全空闲(8×4MiB/0%)·loop PID1401353 存活·无新运维令。**未完成指令：无** ⇒ **WAITING=1**。📦 体积：TASK=21.7KB / MEMORY=31.0KB（均≤32KB✓，本轮无归档）。


> 🆕 **2026-10-26 06:1x #788：✅ §3 seq=8192 验收复测达标·关 graph per-GPU 37,067=0.978×基线(满速)·5.48×恢复 vs cfg1·peak 77.3GB<81GB顶格·loss/gnorm/NaN 正常·§3+§4.3 闭合·通宵攻坚收工**（详→`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` §五·7 + `reports/report_pretrain_seq8192_slowdown_rootcause_zh.html` 五·5b 节 + 档位表新行；TSV `s8k2goff-seq8k`；脚本 `baize_rc_seq8k_graphoff_smoke.sh`）：
> - **配置**：seq=8192/mbs=2/gbs=256/DP8/accum=16，**tok/mb/GPU=16,384**（=cfg1 悬崖点，唯一变量 graph ON→OFF），单机 .29（.12 按 R2.4 不动；per-GPU 口径），60 iter，中位 iter 20–60 = **7,072.0 ms**。
> - **结果**：tok/s=296,543(DP8) / **per-GPU=37,067=0.978×基线(37,903)**（≥§3 bar 0.7×✓）/ vs cfg1(graph-ON 6,768)=**5.48×恢复** / vs cfg0ang(seq4096 graph-OFF 35,070)=1.058×⇒**tok/mb 不变性再证** / peak **77,265 MiB**<81,087顶格 / loss 7.7489 / gnorm 0.8202 / **nan 0**。16 卡外推≈593K=0.98×606K。
> - **结论**：rev3 修复（关 `--enable-cuda-graph`）在**用户目标 seq=8192** 复测达标，§3 验收闭合；结合 §五·5(seq4096)+本节(seq8192)，关 graph 在 tok/mb=16384 两 seq 点均满速 ⇒ 真因=CUDA Graph 顶格停滞(与 seq 无关)终判成立。**§3、§4.3 全部闭合**。**未完成指令：无** ⇒ **WAITING=1**（通宵攻坚收工）。**git**：`pretrain rc #788:` commit。

> 📦 §#786 流水（2026-10-26 02:0x，rev3 真因=CUDA Graph 顶格停滞·关 graph 561K=0.93×满速·recompute 证伪·报告 rev3·commit cb0a83307）已压缩 → daily-memories/2026-10-26.md；**结论**：rev3 root cause + 关 graph 修复独立成立，§3 seq8192 验收由 #788 补齐闭合。需要时再读。

> 🆕 **2026-10-26 03:2x #787：🔬 CP=2/4 可行性 smoke 出结果·32K 当前不可跑·cp1 OOM@81,049MiB·cp2 flash-attn-3 API 阻断·16K 关 graph=实用满速上限·早报已写**（详→`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` §五·6；TSV CP 两行；脚本 `baize_rc_cp_smoke_1n.sh`；结果 `/tmp/baize_rc_cp_smoke_1n/ALL_RESULTS.txt`）：
> - **cp1（CP=1, seq32768, mbs1, DP8, graph-OFF, tok/mb/gpu=32768）**：**OOM**，峰值 **81,049 MiB**，`torch.OutOfMemoryError` @ FP8 quantize（220MiB free / 78.93GiB in use）→ 证实 32K 须 CP（关 graph 不足以装 32K 激活）。
> - **cp2（CP=2, seq32768, mbs1, DP4×CP2, accum2, graph-OFF, tok/mb/gpu=16384）**：**FAIL**，峰值 23,639 MiB。`context_parallel_size:2` 接线正确、blend 加载正确、NCCL CP 组初始化完成；首个 attention 层抛 `RuntimeError: Unknown keyword argument 'window_size' for flash_attn_3::_flash_attn_forward`——CP ring-attn 路径用旧 `window_size=(l,r)` 元组签名，flash-attn-3 已改 `window_size_left/right` 标量。调用点在 **site-packages（非仓库源码）**。
> - **结论**：32K 当前不可跑（CP=1 OOM / CP=2 被 flash-attn-3 API 阻断，非 Mamba2 SSM 本身问题）；**rev3 关 graph 561K/75.5GB（tok/mb=16384）= 当前 16K 实用满速上限**。32K 修复=patch CP 路径 flash-attn 调用（代码任务，非 smoke/配置可解），列后续。**rev3 root cause + 关 graph 修复独立成立（commit #786）**。
> - **脚本 bug 修复（commit eda1e6c7d）**：`--train-data-path "$BLEND"`→`$BLEND`（unquoted，否则整串当 1 个 path prefix→AssertionError，首跑 cp1/cp2 均 FAIL data-path）；2-node master-ssh redirect 挂起→改单机 DP8。
> - **未完成指令：无**（CP smoke + 早报两项 #786 遗留均已交付）⇒ **WAITING=1**。**git**：`pretrain rc #787:` commit。

> 📦 §#785 流水（2026-10-26 01:3x，rev2 报告重写 25,266B memory-bound + 修 #784 虚假交付）已压缩 → EXPERIMENTS_PRETRAIN_2B_ROUND2.md rev2 节；**结论**：rev2「memory-bound」归因已被 #786 rev3 复测修正为「CUDA Graph 顶格停滞」（显存顶格是必要条件非成因）。需要时再读。

> 📦 §#784 流水（2026-10-26 00:4x，tok/mb 悬崖 11 格实测 E1–E5a 全出数 + rev1 报告 16.9KB）已压缩 → EXPERIMENTS_PRETRAIN_2B_ROUND2.md「🔴 tok/mb 悬崖根因」节；**结论**：驱动变量=tok/mb=mbs×seq（与 seq/批几何无关）；11 格证 tok/mb≥16384 全慢全 81.1GB 顶格、≤12288 全快全 <70GB；rev1「GPU 饥饿」被 E2 证伪。**其 memory-bound 归因已被 #786 rev3 修正为 CUDA Graph 顶格停滞。** 需要时再读。

> 📦 §#782「GPU饥饿」+#781/#780 流水（2026-10-25，已被 #784 取代/证伪）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：#782「小批GPU饥饿(MFU14%)」被 E2(同小批84%MFU)证伪，真因=tok/mb≥16384 显存顶 80GB→memory-bound。需要时再读。
> 📦 §#781 流水（2026-10-25 21:28，cfg4跑完6格网格收尾+生成器落盘）已压缩 → daily-memories/2026-10-25.md；**结论**：6格全测完(cfg1-4 OK/cfg5-6 OOM@32768)，生成器确定性✓；其"SSM超线性"结论已被#782的cfg0a对照证伪。需要时再读。
> 📦 §#780 流水（2026-10-25 20:33，网格监控 cfg1✅cfg2✅cfg3🏃）已压缩 → daily-memories/2026-10-25.md；**结论**：cfg1-3=108K/112K/112K，seq4096→8192 per-GPU崩82%，编排器自治。需要时再读。
> 📦 体积：TASK=28.2 KB / MEMORY≈30.8 KB（均 ≤32KB ✓；本轮归档 #781 详块→1行指针+daily原文）。
> 📦 §#777 流水（2026-10-25 17:43，idle 复核三项运维令已交付，无新令）已归档 → daily-memories/2026-10-25.md；**结论**：07:4x报告/23:5x父令/16:0x 三项交付物在位已 commit，WAITING=1。需要时再读。


> 📦 §#776 流水（2026-10-25 16:2x，idle 心跳复核 07:4x 报告令交付物在位、纯验证零 GPU）已压缩 → daily-memories/2026-10-25.md；**结论**：dualnode 报告 24,970B+生成器已跟踪 commit+EXPERIMENTS L3691 指针均复核在位，三项运维令交付完毕，WAITING=1。需要时再读。

> 📦 §#775 流水（2026-10-25 15:10，idle 心跳复核依旧在位·纯验证零 GPU）已压缩 → daily-memories/2026-10-25.md；**结论**：与 origin/main 同步，dualnode 报告/生成器/EXPERIMENTS 指针均复核，三项运维令交付完毕，WAITING=1。需要时再读。
> 📦 §#774 流水（2026-10-25 14:00，idle 复核全部指令已交付）已归档 → daily-memories/2026-10-25.md；**结论**：07:4x 报告 24,970B+生成器+EXPERIMENTS L3691 均在位，三项运维令交付完毕，WAITING=1。需要时再读。

> 📦 §#773（2026-10-25 12:4x，报告 HTML 严格有效性修复+清理 run/reports 残留）已归档 → daily-memories/2026-10-25.md L59–69；**结论**：占位符转义修复，0 script/0 外链/标签配平双过，单一来源=项目级 reports/。需要时再读。
> 📦 §#772（2026-10-25 11:1x，报告位置纠正落地项目级 reports/）已归档 → daily-memories/2026-10-25.md L39–57；**结论**：REPORT_DIR 修回 os.path.join(HERE,..,reports)，与 gen_perf/gen_longctx 一致。需要时再读。

> 📦 §#771（2026-10-25 09:5x，报告 HTML 落地+纠正#770未运行生成器）已归档 → daily-memories/2026-10-25.md L25–37；**结论**：运行生成器产出 rev1 HTML（24.4KB），3 已测 TAG 闭合+6 未测，机制闭合。需要时再读。

> 📦 §#770（2026-10-25 08:3x，双机16卡吞吐报告 rev1 交付）已归档 → daily-memories/2026-10-25.md L13–23；**结论**：双机扩展效率 99.4%(606K)，Task B 3 TAG 全无收益，机制=allreduce<1%步时，#767 误报已纠正。需要时再读。

> 🆕 **2026-10-25 01:3x #768：⚠️纠正#767误报·双机16卡e18真实扩展效率=99.4%(606K tok/s)·非84%/BF16+mock·launcher bug已修并rerun复现·任务A完成·任务书归档**：
> - **#767误报纠正**：#767报「513K/84%/BF16+mock/64.4GB/611TFLOP」**全部错误**。核验`/tmp/baize_dualnode_16gpu_prevrun_23x/`原始日志：①`mock:false`→真实数据(16片p5b_l3)非mock ②`fp8_recipe:tensorwise`→FP8 TW已生效非BF16 ③中位步时6.81s非8.05s ④tok/s=4,128,768/6.81=606,300非513K ⑤扩展效率99.4%非84% ⑥峰值显存69,275MiB=67.6GB非64.4GB ⑦729TFLOP/s/GPU非611。误报根因:脚本因`WORKER_SSH_PID`unbound挂起→summary.txt残缺无RESULT PARSING段→agent手工解析混淆2-rank排障数据。
> - **launcher bug已修(working copy)**：`baize_dualnode_16gpu_test.sh` ①`wait $WORKER_SSH_PID`→`wait $MASTER_SSH_PID` ②`kill $MON_M`→`kill $MON_W`（set -u下两处unbound变量,导致脚本收尾挂起→summary.txt永远缺RESULT PARSING段）。
> - **rerun复现(01:18–01:30,80步)**：clean summary.txt产出✓(bug fix验证通过)。中位步时6808.1ms,throughput **606,449 tok/s**,扩展效率**99.4%**,per-GPU 37,903,峰值显存69,245/69,275MiB(67.6GB),loss 7.5733/gnorm 0.529/0NaN。与prev逐位一致(iter10 loss=10.93756 vs prev 10.93718;step 30-70=6802/6809/6807/6817ms)。`TEST COMPLETE @ 01:30:33`,16卡全释放。
> - **物理印证**：2.2B模型梯度~4.4GB,RoCE busbw≈46GB/s→allreduce传输~0.7%步时→99.4%近线性扩展是物理预期。DP16显存67.6GB<DP8 72.7GB(distributed-optimizer分摊更多卡)。
> - **任务A(e18口径对齐)完成**。下一步:BF16对照组(`--precision bf16`无FP8,16卡80步,量化FP8在DP16增益)→任务B(NCCL/IB调参)/C(overlap grad-reduce/param-gather)/D(MBS4)/E(distributed-optimizer)。
> - **落盘**：`EXPERIMENTS_PRETRAIN_2B_ROUND2.md`新节「双机吞吐优化」(含纠正+结果表)。summary@`/tmp/baize_dualnode_16gpu/summary.txt`(rerun,clean)。
> - **任务书归档**：45.5KB→25.0KB(归档11个已闭合运维块→`ARCHIVE_OPERATOR_PRETRAIN.md`)。
> 📦 体积：TASK=25.0KB / MEMORY=30.7KB（均≤32KB✓；本轮归档~20KB→ARCHIVE_OPERATOR_PRETRAIN.md + #766→daily-memories/2026-10-24.md）。

> 📦 §#767（2026-10-24 23:3x，误报已纠正）已归档 → daily-memories/2026-10-24.md；**结论**：#767报513K/84%/BF16+mock系误报,#768纠正为606K/99.4%/FP8+real。需要时再读。

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
