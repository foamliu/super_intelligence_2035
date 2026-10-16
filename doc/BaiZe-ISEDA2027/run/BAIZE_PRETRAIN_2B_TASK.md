# BAIZE_PRETRAIN_2B_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🆕 运维指令 · 2026-10-16（🔧 **profile 不得与在训抢卡：改 CPU 侧计时 + 单卡小 profile**）· 运维纠正 · 最高优先

> **背景（运维已核你的 `baize_xmodel25_decay_profile.sh` / `..._v2.py`）**：方向**正确**（baseline `--grad_checkpoint` vs improved `--fast_data --adamw_fused`，`--profile_steps 15` + `timing_log.txt`），**且已把 `SEQ=3712 / ITERS=19980` 写对** ✅。**但脚本用 `--nproc_per_node=8` 跑在 `.29` 同一批卡**，而在训的 80B decay 已占 **58–60GB/卡** ⇒ **必然 OOM**（21:50 端口、21:59 OOM 两次修的都是次生问题，不是根因）。

**① 🚫 8 卡 profile 一律禁止（不得与在训抢卡）**，改为二选一：
- **(a) 纯 CPU 侧数据管线计时（首选，零 GPU）**：单起脚本只循环 `next(data_iter)`，对比「现在的 `tolist()`+`list.extend` 版」vs「`np.concatenate`+`torch.from_numpy`+`pin_memory` 版」的 **每 batch 毫秒**、**每次同步 H2D 毫秒**，各跑 50 次取中位数。**瓶颈假说就在数据侧 —— 这一步能直接证实/证伪，且完全不碰 GPU。**
- **(b) 单卡小 profile**：`CUDA_VISIBLE_DEVICES=0` + `--nproc_per_node=1` + `MBS=1` + `seq=512` + `--profile_steps 10`，只用 1 张卡测 `t_fwd_bwd / t_opt` 与 **GC on/off 的相对差**；**测完立刻退出**。
**② ⚠️ pkill 安全带**：`cleanup_gpus()` 里 `pkill -9 -f baize_xmodel25_decay_v2` 只匹配 v2 是**对的**；**今后任何 `pkill`/pattern 都不得匹配 `baize_xmodel25_decay_train.py`（在训进程）**。建议脚本内先 `ps` 打印「将杀哪些 PID」再执行。
**③ 顺序修正**：先做 **(a) 数据侧计时** → 定方案 → **一次性重起**（3712/19980 + fast_data + gc off + timers）→ 重起后再单独做 **MBS A/B**。🚫 在训期间不要反复起停。
**④ 交付**：数据侧计时表（ms/batch、ms/H2D）+ 重起后 tok/s 对比 + 新 ETA → `MEMORY_PRETRAIN_2B.md` + `daily-memories/`；commit `pretrain perf:`。


### 🆕 运维指令 · 2026-10-16（⚡ **decay 提速专项：先量化、再修数据管线/GC/MBS**）· 用户直令 · 最高优先

> **用户令（2026-10-16）**：「pretrain 训练效率太低（183K tok/s，我 BaiZe-2B 都有 249K）。是否 Muon 实现效率不高？**如果是就换 AdamW**。另外显存还有空间（58–60GB/卡），**看有没有机会把 MBS 提升一倍**。另外为省时间，**可考虑 seq-len 与总数据量都对齐 Xmodel-2.5（71.2B）**。」

> **运维实测结论（逐条，均有出处）**：
> - **① 🚫 不换 AdamW —— Muon 不是主因**。P-8 基线（`EXPERIMENTS_PRETRAIN_2B.md:108-120`）**同样是 MBS=2 / GBS≈1024 / seq4094 / DP8 / bf16**，却跑到 **249K tok/s（~17.5s/step、565 TFLOP/s/GPU）** ⇒ **MBS 相同、吞吐差 27%，问题不在 MBS、也不在 batch 形状**。差别在**技术栈**：P-8 = **Megatron-Core 全栈**；本 run = **HF `AutoModelForCausalLM` + 手写 DDP + 手写 `BlendedDataLoader`**（因 Megatron-Core 0.16.1 不实现 Xmodel μP 前向缩放，转换会破坏模型）。Muon 每**优化器步**仅更新一次（共 20346 步），被 **60 个 micro-step** 摊薄 ⇒ **非主因**；且换 AdamW 会**破坏与 Xmodel 官方「同配比·同优化器」的可比性**（本实验立论基础）⇒ **不许换**。
> - **② 真瓶颈（可修，配方中性）**：数据管线 **单进程 / 无 worker / 无预取**，且**在训练主循环内同步**做 `IndexedDataset` 随机取 doc → `doc.tolist()` → Python `list.extend` 拼到 4096（`baize_xmodel25_decay_train.py:116-138`，纯 Python 逐 token）→ `.to(device)` **未用 `non_blocking`**（L320）⇒ **每 micro-step GPU 都在等 CPU**（60 次/步）。
> - **③ 梯度检查点默认开着**（L214 `--grad_checkpoint` default=True）→ 反向重算 ≈ **+20~30%** 时间（P-8/Megatron 默认关闭）。
> - **④ seq / 总 token 口径已澄清（落地方案见 §⑤）**：计划书口径 = **seq 3712 / 3.56M tok·步⁻¹**（`reports/report_xmodel25_decay_80b_plan_zh.html` §4）；起训脚本曾按「**4096 = 2¹²**」铁令覆盖为 4096（`baize_xmodel25_decay.sh:17`）——**该铁令只约束 BaiZe-2B 自研模型**，本 run 训的是 Xmodel ⇒ **本轮改回 Xmodel 原生 3712**。

**① 先量化（改前必做，10 步）**：主循环加分段计时并打日志 —— `t_data`（next(data_iter) + H2D）/ `t_fwd_bwd` / `t_opt`（zero_grad + clip + muon + adamw），每 10 步打印均值。**用数据定位瓶颈，🚫 不许拍脑袋改配置。**
**② 配方中性提速（不改变训练语义；改完从 step_532000 重起跑）**：
- **a. 数据管线**：改 `torch.utils.data.DataLoader(num_workers=8, pin_memory=True, prefetch_factor=4, persistent_workers=True)`（或后台预取线程 + 队列）；`get_batch` 去掉 `.tolist()/extend`，改 `np.concatenate` + `torch.from_numpy`；H2D 改 `non_blocking=True`。
- **b. 关梯度检查点**：`--grad_checkpoint` 默认改 **False**（显存不足再回退）。
- **c. A/B `MBS 2→4`**：`grad_accum` 60→30（**GBS 保持 960 不变**），各跑 ~30 步测 tok/s；显存有 ~20GB 余量，预期可容纳。
- **d. 可选**：AdamW 组加 `fused=True`。
**③ 只有在①的分段计时**证明 Muon（含 `num_ns_steps=5` / `scale_mode="spectral"` / FP32 upcast 补丁）**占比显著**时，才允许动优化器 —— 且须**附计时证据**再定是否改。
**④ 交付**：**tok/s 前后对比表 + 分段计时表 + 新 ETA** → `MEMORY_PRETRAIN_2B.md` + `daily-memories/`；commit 前缀 `pretrain perf:`。
**⑤ ✅ 本轮执行「seq / 总 token 对齐 Xmodel-2.5」（用户 2026-10-16 澄清：「**4096=2¹²**」铁令**只约束 BaiZe-2B 自研模型**；本 run 训练的是 **Xmodel** ⇒ 按 **Xmodel 原生口径**走，两令不矛盾）**：
- `baize_xmodel25_decay.sh`：**`SEQ 4096 → 3712`**；**`ITERS 20346 → 19980`**（= **71.2B ÷ (960 × 3712 = 3.56352M tok/步)** ≈ 官方 **20,000 步 × 3.56M**，即 **总 decay token 与官方一致 = 71.2B**）。
- **`GBS` 保持 960**（与官方 3.56M tok/步 等价）；**优化器仍用 Muon**；**起点不变**（step_532000）；LR 曲线保持 `1.67e-3 → 1e-5`（WSD，warmup 100）。
- 收益：墙钟 **省 ~11% ≈ 0.5 天**，且与官方 **apples-to-apples**（唯一变量 = 数据配比，本实验的立论目标）。
**⑥ 一次重起、两件事一起落**：**seq/ITERS 对齐** 与 **§② 的配方中性提速（数据管线 + 关 GC）** 在**同一次重启**完成，避免重复起停；**MBS 的 A/B（2→4）放在重起之后单独测**（不与其它改动叠加，便于归因）。
**⑦ 交付**：对齐后的 **step / loss / LR / ETA 表** + **提速前后 tok/s 对比** + **分段计时表** → `MEMORY_PRETRAIN_2B.md` + `daily-memories/`；**并同步更新 `reports/report_xmodel25_decay_80b_plan_zh.html` §4 对照表**（our **80B→71.2B**、**19980 步**、公平性论述改为「**同 token 预算 71.2B，唯一变量 = 数据配比**」）；commit 前缀 `pretrain decay80b:` / `pretrain perf:`。
**⑧ 纪律**：⛔ 不干扰 data 线；任务书 >32KB 自滚归档。


### 🚨 运维指令 · 2026-10-16 19:0x（⏱ **加急：立刻起训 80B decay，禁止再空转**）· 用户质询 · 最高优先

> **用户质询（2026-10-16）**：「pretrain：执行 80B decay 实验 —— 他俩到底还在等什么？不知道 GPU 很贵吗？」
> **事实（运维实测）**：放行令（13:47）+ NeMo 纠偏（15:32）均已下发，但本线**自 13:19 起零提交**，`.29` 8×H100 **空了 5.5 小时**。已另经 `ops/inbox.md` 下发 **RUN_ID 109** 核查 loop 死活并按需重启。

**① 立刻执行（🚫 不得再以「等运维指令」为由空转）**：按 13:47 放行令 + 15:32 NeMo 纠偏起训 80B decay —— 起点 = **Xmodel-2.5 stable 末 ckpt（step 532000）**；数据 = **BaiZe 80B 配比**；优化器 = **Muon（NeMo/Megatron-Core 0.16.1 自带）**；🚫 **禁止 `find 全树` 找 muon.py**。目标 = 14 集超越 Xmodel-2.5 final（CS8 65.40% / CX 32.90%）。

**② 执行顺序**：① `nvidia-smi` 确认 `.29` 空窗 → ② **HF ckpt → Megatron/NeMo 格式转换**（先跑小样本 smoke 再全量）→ ③ **复用 BaiZe P-8 的 muon 训练脚本**（只换模型）→ ④ 起训并回报 `step / loss / tok·s⁻¹ / ETA / 卡占用`。

**③ 每轮唤醒必须落盘**：`MEMORY_PRETRAIN_2B.md`（step / loss / ETA / 卡占用）+ `daily-memories/` —— 哪怕单轮 cline 只跑 25 分钟也要写，🚫 **禁止静默**。

**④ 阻塞必须显式报告**：卡在 ckpt 转换 / tokenizer 不兼容（128K vs 129K）/ 数据路径 / 依赖缺失等，须写明「**卡点 + 已试方案 + ETA + 需要什么**」，🚫 不许静默等待。

**⑤ 纪律**：🚫 不 kill 别线进程 · 与 data 线错峰 IO · commit 前缀 `pretrain decay80b:` · 任务书 >32KB 自滚归档。


> 📦 [已归档] **2026-10-16（🚀 放行执行 80B decay 实验 + 用 NeMo 训 Xmodel）** → 原文见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（2026-10-16 归档块）。⚠️ **已执行完毕**；**实测修正**：Megatron-Core 0.16.1 **不实现 Xmodel 的 μP 前向缩放**（embed×12 / attn·ffn 残差×1.4/√48 / logits×1/6）⇒ **HF→Megatron 转换会破坏模型**，最终落地为 **HF `AutoModelForCausalLM` + 手写 DDP + Megatron `TensorParallelMuon` 优化器**（见 `baize_xmodel25_decay_train.py` docstring）。

> 📦 [已归档] **2026-10-16（📋 Xmodel-2.5 stable 末 ckpt + BaiZe 80B 配比做 decay · 先出计划书）** → 原文见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（2026-10-16 归档块之二）。⚠️ **已执行完毕**：计划书 `reports/report_xmodel25_decay_80b_plan_zh.html`（36KB）已交付；**官方对照基准已落在计划书 §4**（Decay token **71.2B** = 20k 步 × **3.56M tok/步**、占总训练 1.4T 的 ~5%、**66.9% 高质量 SFT**、**AdamW→Muon**）；**decay 段用 Muon 的理由**（"stable 段全用 Muon 会发散 → 官方只把 Muon 缩到 decay 段；BaiZe P-8 的 dist_muon 发散不适用于 Xmodel"）亦已落计划书。

> 📦 §运维指令·2026-10-15（📘 v5 预训练计划书）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v5 报告 42.8KB ✅ 交付(commit fc0a292b)，5问速答+三方对照+推荐策略+配比实验+风险+附录，6表1SVG。需要时再读。

### 💡 最佳实践 / 硬口径（常驻 · 每次唤醒先看）

> 以下为**固定口径**，除非运维再下新令，否则**不得更改**——尤其写进报告/论文时，逐字遵守。

| 项 | 口径 | 依据（源码/台账） |
|:--|:--|:--|
| **seq_length** | **4096（非 4094）** | 用户直令（2026-10-14）：**4096 = 2¹²（2 的幂）**是正确的固定口径；P-8 脚本 `SEQ=4094` 系 agent 错误，须改正为 4096 |

> ⚠️ **`4094` 是错误的，须统一为 4096**：① 脚本 `baize_p8_train.sh:30` / `baize_p8_adamw_train.sh:33` = `SEQ=4094`（改 4096）；② `EXPERIMENTS_PRETRAIN_2B.md:4` / `MEMORY_PRETRAIN_2B.md:183` 记录的「4094」亦须改 4096；③ 论文 `3_architecture.tex:31`（tab:config）· `4_llm_pretrain.tex:75` · `4_llm_pretrain.tex:165` 三处 `4094`（改 4096）。🚫 今后报告/论文/脚本**一律 4096**。

> ✅ **P-8 处置（用户 2026-10-14 定）**：P-8 当前 run（`p8_adamw`，stable+decay 共 10490 步）**按 `seq=4094` 跑完，不干预**。**脚本 `SEQ` 改 4096 须等 P-8 整轮全部结束后再改**（stable + decay 都跑完、最后 ckpt 已保存）——尤其 `baize_p8_decay.sh:35` 在 step9441 切换时仍须保持 4094（与 stable 一致），🚫 不得中途改 decay 脚本。今后**新 run**（如正式训练）一律 4096。

> 📋 **评测口径（对齐 Xmodel-2 论文 Table 2/3 · 一律用 lm-eval）**：
> - **常识推理 8 集**（zero-shot · raw accuracy · 另报 Avg）：`ARC-Challenge` `ARC-Easy` `BoolQ` `HellaSwag` `OpenBookQA` `PiQA` `SciQ` `Winogrande`
> - **复杂推理 6 集**（n-shot 用 lm-eval 默认值 · 另报 Avg）：`GSM8K` `MATH` `BBH` `MMLU` `HumanEval` `MBPP`（HumanEval/MBPP 需代码执行，用 lm-eval 自带沙箱）
> - ⚠️ Xmodel-2 正文提 `TriviaQA` 但 Table 2 无此列 → **以表为准，只跑 8+6**，报告注明此差异；报绝对值时标 harness 版本 + shot 数。

> 📦 §运维指令·2026-10-15（🌐 下载 proxy 口径）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：proxy 口径 92.23→hf-mirror / 92.25→hf.co（常驻），Xmodel-2/2.5 final+history 均已下载完成。需要时再读。

> 📦 §运维指令·2026-10-15（📥 下载 Xmodel-2/2.5 decay final eval）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：Xmodel-2 final CS8=64.82%, Xmodel-2.5 final CS8=65.40%/CX=32.90% 均已实测。需要时再读。

> 📦 §运维指令·2026-10-15（📈 下载 Xmodel-2/2.5 history ckpt scaling）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：Xmodel-2 s1 4 ckpt eval ✅ (10K CS8=46.65%, 40K CS8=50.31%), BaiZe 39.6B CS8=49.21% > XM2 s1/10K 39.3B CS8=46.65% (+2.56pp), scaling report 含 15 points + 2 SVG。需要时再读。

> 📦 §运维指令·2026-10-15（📈 P-8 中间 ckpt 14集 scaling）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-8 6 中间 ckpt CS8 eval ✅ (4.4B→44.4B, 44.04%→49.21%), BaiZe 44B CS8=49.21% ≈ XM2 s1/40K 157.2B CS8=50.31% (差1.10pp)。需要时再读。

> 📦 §运维指令·2026-10-15（⚡ 评测提速 v2）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：8 GPU 并行评测完成，14集全部跑完，CS8 Avg=49.21%, Complex Avg=6.81%。需要时再读。

> 📦 §运维指令·2026-10-15（📊 P-8 final 14集 eval）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-8 final(iter_1149, 44.4B) 14集 eval ✅ 全部完成, CS8=49.21%, CX=6.81%, scaling_report.html 已生成。需要时再读。

> 📦 §运维指令·2026-10-14（📋【v4 重做】正式训练计划）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v4 报告 47KB 已交付(commit 826ae3f7, 14源精确token/int32 dtype/密度归因/D-scan 6档/SVG曲线/全量配比+epoch表)。需要时再读。

> 📦 §运维指令·2026-10-14（🔧 修复 decay 段 LR 未衰减 + 重跑 decay）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：decay fix 完成(#432)，只加载权重+warmup100+WSD线性 1e-3→1.85e-5，final ckpt@1149 已保存，8 GPU 释放。需要时再读。

> 📦 §运维指令·2026-10-14（✍️ 放行刷新论文 —— 执行审视报告修改）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：H1-H4+S1-S10 全修完成（commit 75963f3d, 11pp 0-error ✅）。F2（P-8 结果）待 P-8 完成后再填。需要时再读。

> 📦 §运维指令·2026-10-14（📝 训练空窗期审视论文·LLM侧·中文HTML）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：报告 26.5KB 已交付(#413, 4🔴+10🟠+3🟢)，随后 #414 执行改稿。需要时再读。

> 📦 §运维指令·2026-10-13（📋【再重做 v3】正式训练计划·实盘盘点口径）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v3 报告已交付 `reports/report_pretrain_formal_train_plan.html`（实盘盘点，在 origin/main）。需要时再读。


> 📦 §运维指令·2026-10-13 v2（📋 重做正式训练计划 · 禁 100B 假设）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v2 已交付(commit fa25d488, 30.4KB, 300B token基准) → 被用户再次否决(CSDN二级源无一手依据) → v3 重做(实盘盘点口径)。需要时再读。


> 📦 §运维指令·2026-10-13（📋 正式训练 HTML 计划：全量 MiniCPM5 + en_v1_4 · 双机 16 卡 · 超参 + 空窗期试验）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：`report_pretrain_formal_train_plan.html` 27.9KB ✅ 交付（commit 42399927，10 节自包含 HTML：数据/算力/超参/占卡协调/空窗期 5 试验/ckpt/纪律/launcher 模板）。需要时再读。

> 📦 §运维指令·2026-10-11（📚 文献借鉴报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：`report_pretrain_lit_ideas.html` 29.8KB ✅ 交付（TOP-5+附表8+§4待验证+§5去重+§6映射+§7口径, 每条6字段齐全）。需要时再读。

> 📦 §运维指令·2026-10-10（⚗️ MBS 2→3 A/B 验证）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：B/A=1.031 < 1.12 → FAIL → MBS=2/GBS=1024 原定稿保留。需要时再读。

> 📦 §运维指令·2026-10-12（🛑 停训 P-8 · Muon→AdamW 重新启动）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：dist_muon step8490 loss=2.623 发散 → 停训换 AdamW 从零重启 ✅。AdamW 训练健康（PID 771300, step~4966/10490, loss~2.66, grad_norm~0.13, LR=1e-3）。需要时再读。

> 📦 §运维指令·2026-10-10（🚀 撤 P-8 暂缓令 · dist_muon 启动）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：dist_muon 44B 跑到 step8490(80.9%) loss 慢速发散(2.62 新高/grad_norm 0.89) → 用户令停训换 AdamW 重启。需要时再读。

> 📦 §2026-10-10（✅dist_muon默认 + ⚗️dist_muon重测 + 📄刷新Muon报告 + 📄昨夜报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：dist_muon=loss3.110/122,415tok/s/37.3GB（plain Muon −26%吞吐/+38%显存 全消除→P-8默认，LR 1e-3 保留）；Muon报告§7补外部基准+overhead归因；昨夜报告11.6KB。

> 📦 §2026-10-09（🔁只用.29+改序 / ✅NeMo支持Muon）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：对比基准+Muon A/B完成，T1/T2/T3留backlog；Megatron-Core 0.16.1含muon.py，三步核查通过。

---

> 📦 §运维指令·2026-10-09（⚗️ Muon vs AdamW · 原 `.12` 方案）已被上方「🔁 运维调整」覆盖 → 原文见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（2026-10-09 搬运，原文未改）。

---

> 📦 §运维指令·2026-10-09（🌙 夜班填空 T1/T2/T3）已被上方「🔁 运维调整」取消（用户看不出价值） → 原文见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（2026-10-09 搬运，原文未改）。backlog：T1 长上下文 / T2 等参 Dense 训练侧 / T3 R3 配比迁移。

---

> 📦 §运维确认·2026-10-09（✅ GO：#252 门控通过）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：对比报告 report_pretrain_baize_vs_dense_fair_zh.html 23.7KB 已生成。需要时再读。

---

> 📦 §运维指令·2026-10-09（📊 补测+中文对比报告：参数匹配 Dense vs Hybrid）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：参数匹配 Dense Llama 2.229B vs Hybrid 2.220B SGLang 对比完成，ctx 扫到 hybrid OOM，报告 23.7KB/5表。需要时再读。

---

> 📦 §运维指令·2026-10-09（🔎 自查：BaiZe vs MiniCPM5 公平对比盘点）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：C1-C6 逐条自评完成。需要时再读。

---

> 📦 §运维指令·2026-10-09（💡 提 3 个实验 idea）已闭合（#251 已交付：①P-8 彩排 ②P-8 44B 下限 ③R3 配比迁移，+ 建议立即起 P-8） → 原文见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（2026-10-09 搬运，原文未改）。

---

> 📦 §运维指令·2026-10-09（📄 R3 数据配比搜索收官报告 HTML）已闭合（#246 报告已交付） → 原文见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（2026-10-09 搬运，原文未改）。结论：`report_pretrain_r3_data_mix.html` 52.6KB 已生成 + commit 00682e58 + push。

> 📦 历史运维指令已归档 → `run/ARCHIVE_OPERATOR_PRETRAIN.md`（已执行完 / 已作废的块；需要时再读，不要读进上下文）。

> 本节由外部运维通过 git 修改。agent 禁止修改本节（只写 `MEMORY_PRETRAIN_2B.md` / `daily-memories/` / `EXPERIMENTS_*`）。本节为「无」时按下方 Round 2 默认顺序推进。⚠️ 唯一例外（2026-10-06）：按「📉 体积维护规程」，agent 可把「已闭合」的运维块/旧正文【原文】搬入 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（只搬迁、留 1 行指针；不新增/不改写任何指令）。

> 📦 §2026-10-06~07（ctx扩展+推理对比+5份报告+提速+裁决，共7块）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：PPL 1M=55.42无退化, hybrid vs dense prefill 2.18×, 5份HTML✅, A/B/D✅(BBH 14.26%, VRAM 5.35GB恒定), T1/T2 warmup-corrected(hybrid快2.8-4.3×), T3=recompute无效+FP8慢9%。需要时再读。


> 📦 §2026-10-08~09（R3配比+论文LaTeX+R2收官HTML+T3提速验证，共4块）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：R3 6维搜索✅, LaTeX更新✅, R2报告46KB✅, T3=recompute对Mamba2-hybrid无效(52/56层SSM激活常量级)+FP8慢9%, P-8最优=TP1·MBS2·bf16=249K tok/s。需要时再读。

> 📦 §2026-10-06（裁决+空窗提案，2块）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：NVLink P2P 100%(busbw 164.56GB/s), A 36/36✅(BBH 14.26%), B✅(ABF+2.71pp), D✅(VRAM 5.35GB恒定), C暂不动, E不做。需要时再读。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）原文搬入 `run/ARCHIVE_OPERATOR_PRETRAIN.md` / `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）/ `daily-memories/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `pretrain 归档: …` 前缀。
> 本轮动作：本任务书现 ≈40KB（已过 40KB 红线）⇒ 下次唤醒先归档到 ≤32KB，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底 push 一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_PRETRAIN.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_PRETRAIN.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_PRETRAIN_2B.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_PRETRAIN_2B.md \
              doc/BaiZe-ISEDA2027/run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md doc/BaiZe-ISEDA2027/run/daily-memories
   git commit -m "pretrain #<轮次>: <一句话>"   # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。

> 📦 §2026-10-05（3项：sglang上界+对比+环境）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：sglang vllm env 可用(0.5.9), proxy=172.19.92.25:13128, P-9.11 prefill 2.18×, 128K failed。需要时再读。
### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_PRETRAIN_2B_TASK.md` ≈ 38KB、`MEMORY_PRETRAIN_2B.md` ≈ 14KB。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_PRETRAIN.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md` 等；
  ④ 较早的唤醒流水（保留最近 ~20 条） → `daily-memories/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 /「进度快照」③ 最近 ~20 条流水。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变（正文/流水/快照里不得再出现以 `WAITING:` 开头的行）。

---



# ══════════════ ROUND 2 · 现行部分（只保留仍未完成/仍有效的）══════════════

> R2.0/R2.1/R2.2 清单 · R9.0-bis · P-4R · P-5a 与 Round 1（S0–S5） 均已完成并归档 →
> `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md`（需要时再去读，不要把整份读进上下文）。

> 📦 §P-6 lm_eval 8集+scaling law（已完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md；结论：P-6① Avg=0.4395@655M, P-6② 48/48 runs Avg 33.26%→49.22% R²=0.986, 55%→~55B tok. 需要时再读。
> 📦 §P-7 训练吞吐核查（已完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md；结论： dense +8% (not +24%), hybrid 85.6K vs dense 89.7K. 需要时再读。

> 📦 §P-8 细节 + R2.3 交付物（P-8 已完成：10590步/44.4B tok/final loss 1.357）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-8 AdamW 44.4B 训练完成，14集eval CS8=49.21%/CX=6.81%，ckpt@iter_1149 已保存。需要时再读。

## R2.4 约束

- 总预算（分三档）：
  - P-1 / P-2 / P-3 / P-4 / P-6 / P-7：短程实验，≤ 5 小时墙钟（P-6 视加载路径难度可到 6 h；P-7 ≤1h）。
  - ⭐ P-5 是独立长任务，≤ 8 天墙钟（P-5a 4–5 h + P-5b 20B token ≈ 2.5 天；预算允许可延到 60B ≈ 7.5 天）。
  - 超时按 P-5a > P-6 第 1 步（现有 ckpt 的 8 集）> P-1/P-2 > P-4 > P-5b > P-6 第 2 步 逆序裁剪，并在报告记录裁剪决策。
- GPU：只用 `10.239.2.29` 的 GPU 0–7（8 卡）。绝不杀他人进程。
  ⚠️ 另有 vision 任务在 `10.239.2.12`（另一台机器）跑——与你无关，不要去动那台。
- 每次启动训练前后都要记录 GPU 占用核验结果（`nvidia-smi --query-compute-apps=...`）。
- ⚠️ NFS 与 vision 任务共享（重要）：两台 GPU 节点用的是同一块 `/nas_train` 盘。
  vision 任务的 R2-4 需要"无争用的干净吞吐测量"，而你启动训练同样会打这块盘。
  → 启动 P-1 之前，先读 `run/MEMORY_VISION.md`（共享盘，你直接可见）看它的 R2 进度：
  - 若 R2-4 尚未完成：先做不占 GPU 的准备工作（代码/数据核对、P-3 的 Round 1 基线复核、脚本落地），
    每轮唤醒重查一次它的进度；
  - 最多等 2 小时；超过 2 小时则照常启动 P-1，并在报告里注明"当时 vision 任务在并发"。
  → 你的每次测量都要记录"当时 vision 任务在跑什么"。
- 数据：P-1/P-2 沿用现有 200k docs / 165M token 即可（5000 步 ≈ 164M）；
  P-3 若需更长的数据覆盖，先核对再启动，不要中途断数据。
- 收尾不杀 loop（关键）：R2 的 P-1/P-2/P-3 全部完成（或按预算裁剪到只剩需等待的项）后，把结果写进报告并 git push，然后停在原地：`MEMORY_PRETRAIN_2B.md` 的 `PHASE` 置 `converged`、`WAITING` 置 `1`（30 分钟长轮询）；🚫 绝不 kill / pkill `baize_pretrain_loop.sh`。loop 必须持续运行，以便运维远程下发新任务（会改写本任务书，下次唤醒即按新指令执行）。

---



> ⚠️ 本文件为只读指令文件，agent 禁止修改本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。

你是推进 BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 从零 + 24h 预算高置信度超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

## ⚠️ git 同步规则（必读，2026-10-01 新增，每次唤醒都要走）

### 前提：这是一个共享工作副本

vision 任务的 agent 与本任务共用同一份工作副本——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

因此：
- 只需一个人 pull，另一个立刻看到：vision agent 拉取后，你读到的 `$TASK_MD` 与所有文件都会同步更新。
  不要重复 pull，也不要因为"工作区里出现了别的任务的改动"而困惑。
- 工作区里陌生的未提交改动很可能是 vision 任务的在途文件。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉另一个任务的成果。
- 两个 loop 每 5 小时各自 `git add -A && commit && push`，会互相把对方在途的文件一起提交。
  这是既有设计的已知副作用，不要试图"修正"它。

### 但 loop 本身只 push 不 pull

`baize_pretrain_loop.sh` 的 `git_push_if_needed()` 只做 `add → commit → push`。
一旦远端被别人推进，它的 push 会 `! [rejected] (fetch first)` 失败、每 5 小时重试一次、永远失败。
所以 pull 必须由你（agent）来做。

每次唤醒按顺序执行：

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. 提交时显式指定你自己的文件：
   `git add MEMORY_PRETRAIN_2B.md EXPERIMENTS_PRETRAIN_2B_ROUND2.md daily-memories/`
   🚫 不要用 `git add -A`——那会把 vision 任务的在途文件卷进你的提交。
3. 若显示 behind / diverged：`git pull --rebase origin main`。
   - 报 `cannot rebase: You have unstaged changes` → 是双方的在途改动：
     先把你自己要提交的文件 commit 掉再 rebase；🚫 不要 stash / 丢弃别人的改动。
   - 报 `Unable to create '.git/index.lock'` → 另一个 agent 正在做 git 操作：
     等 30–60 秒重试（最多 3 次）；仍失败就记一行流水并跳过本次 git 操作，下次唤醒再试。
   - 🚫 绝不 `git push --force`；🚫 绝不 `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` 无 ahead/behind 才算闭环。
5. 流水记一行 git 结果（沿用你已有格式）。

> 参照实现：vision 任务的 agent 在 `daily-memories-vision/2026-10-01.md:198` 已按同样方式
> `git pull --rebase` 合并远端后 push 成功——沿用同一做法。

---


---

