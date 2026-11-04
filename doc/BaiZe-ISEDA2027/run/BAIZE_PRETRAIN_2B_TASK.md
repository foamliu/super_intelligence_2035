# BAIZE_PRETRAIN_2B_TASK.md

> 📦 §用户令 2026-11-03 22:0x（llama.cpp pilot）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：✅已执行 pilot=FAIL(commit 9cdc4469f/0d1b0567e, 报告report_pretrain_llamacpp_pilot_zh.html 8422B)，根因=GGUF转换Duplicated key覆写hybrid元数据, 速度7.03x达标但Δacc16-18pp, 保留HF float32路线等用户令。需要时再读。

> 📦 §运维令 2026-11-02 19:51（S1 重启事故+CPU降载）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-04 第四批」节；**结论**：✅ S1 18:39 SIGKILL 后 19:51 从 ckpt58000 续跑恢复，训练在跑；CPU降载纪律(OMP≤8/nice19/禁pkill)已并入 11-02 11:1x 与 11-04 09:3x 令。需要时再读。

> 📦 §运维令 2026-10-31 18:2x（paper-slim 压 ch4 约 1750 字符 → 6 页）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31 第三批」节；**结论**：✅ 4_llm_pretrain.tex 15398→11960B（省 22.3%），6 页（正文 p1-p5 + refs p6），ERR=0/UNDEF=0/Overfull=0，commit 2fef637c8，报告 report_pretrain_paper_slim_zh.html 9.9KB。需要时再读。

> 📦 §运维令 2026-10-31 15:2x（全文事实审订 3_architecture.tex）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31 第三批」节；**结论**：✅ 84项审计，修复"52 Mamba-2"→24+28，Table1新增Mamba2/MLP行，5处.tex修改，ERR=0，commit d6ba844fc，报告 report_pretrain_paper_audit_zh.html 25.7KB。需要时再读。

> 📦 §运维令 2026-10-31 11:2x（直接落地改稿 4_llm_pretrain.tex + 刷新摘要/intro）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31 第三批」节；**结论**：✅ P0/P1×6/P2全部落地，0_abstract+1_intro+2_related+5_posttrain+9_conclusion刷新，编译0-error/6页，commit 85ea67b4d，报告 report_pretrain_paper_edit_zh.html。需要时再读。



> 📦 §运维令 2026-10-31 11:0x（论文第4章审校修订计划）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31 第二批」节；**结论**：✅ 交付 report_pretrain_paper_revise_plan_zh.html（34KB/6节），1 P0 + 6 P1 + 6 P2 逐条列出，已被 11:2x 令落地。需要时再读。

> 📦 §运维令 2026-10-31 09:1x（接手维护论文预训练章节）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31 第二批」节；**结论**：✅ 4_llm_pretrain.tex 事实核校+decay-A补全+§4.11修正，编译0-error，commit b12ddfb57。被 11:2x 令更新。需要时再读。

### [已完成] 🚨 2026-10-30 22:2x 运维直令：写「1M 长上下文 + 95% 大海捞针」技术报告 · ✅ 已完成（#983 2026-10-30 23:17 交付 `reports/report_pretrain_1m_needle_zh.html` 33,667B/6节+总结路线图/0 script/0外链，覆盖现状基线-怎么做到1M-怎么到>95% needle-实验矩阵6组-取舍建议-与Qwen/Llama3对比；commit d0424c1f1）→ 原文归档到 `run/ARCHIVE_OPERATOR_PRETRAIN.md`「归档 2026-10-31」节。需要时再读。



> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

> 📁 **报告目录纪律（2026-10-28 用户直令 · 全局常驻 · 覆盖一切旧报告路径）**：所有 HTML/中文报告**一律产出在 `doc/BaiZe-ISEDA2027/reports/`**。🚫 **禁止产出到 `run/reports/` 或项目根 `reports/`**（生成器输出路径必须指向项目级 reports；run/reports 历史文件不得再新增）。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### [运维令] 2026-11-04 22:1x（**llama.cpp 调试「每环节必须落盘」+ 清理残留**）· 用户直令 · 最高优先

> 用户原话（2026-11-04 22:1x）：「给 pretrain 下『每环节必须落盘 + 清理残留』的指令。」
> 触发事实（运维 22:00 中继实测）：14:05–21:43 有一个 cline 会话连续跑 **5.9h**，`llama.cpp` 工作区 **零改动、零提交**；21:43 新会话又从 RMSNorm/eps 重新查起。⇒ 本轮先解决「工作不可见 / 重复劳动」，再继续 14:0x 的定位与 PR。

**① 每环节必须落盘（硬性，违反即视为未完成）**
把 14:0x 的定位拆成 5 个检查点，**每完成一个就必须落盘 + commit**，不许攒到最后：
- A. group 展开语义（`repeat` vs `repeat_interleave`，n_groups=8；`ssm_scan_f32` 的 `g=h/(nh/ng)`、B/C 的 `view_4d`）
- B. conv1d 维度与顺序（`conv→+bias→silu`；d_inner=4096 / d_state=128 / n_group=8 ⇒ 6144）
- C. dt 投影 + softplus + **dt_clamp(min/max)**（已发现 llama.cpp 可能未 clamp，优先收口）
- D. RMSNormGated（eps=1e-5、`mamba-base.cpp:292` 的 reshape/ne 顺序）
- E. 逐层 hidden dump，定位首个偏差层

每个检查点写入 `doc/BaiZe-ISEDA2027/llamacpp.txt` §6 的表格（一行一项）：
`检查点 | 假设 | 命令/文件行号 | 实测结果 | 判定(PASS/FAIL/待验) | 下一步`
- **commit 前缀 `pretrain llamacpp-probe:`**，只 `git add` 明确文件（`llamacpp.txt` + MEMORY + daily）。
- **单会话超过 90 分钟仍无 commit ⇒ 先停下，把当前发现落盘并 commit，再继续**；会话被截断前必须至少留下一条检查点记录。
- 每个新唤醒**先读 `llamacpp.txt` §6 表格**：已判定 PASS/FAIL 的检查点不许重跑，只做「待验」项。

**② 清理残留（只清本项目、只按 PID）**
- 先盘点：`ps -eo pid,lstart,etimes,pcpu,rss,args | grep llama-server`，记下 PID/端口/模型/启动时间。
- **保留当前正在用的 1 个**（若有），其余全部 `kill <PID>`；10 秒后仍在的再 `kill -9 <PID>`。🚫 禁止 `pkill` / `pkill -f` / 按名字批量杀（18:39 红线）。
- GGUF 去重：对 `/tmp/baize_*.gguf` 计算 `md5sum` + 大小，**只删除与保留副本完全相同的重复文件**；至少保留 `/tmp/baize_iter10000_f16.gguf` 与 f32 各一份；🚫 不删 `/nas_train/.../models/` 下的正式 GGUF、不删 `hf_iter_*` / ckpt。
- 清理前后各记一次：`pgrep -fc llama-server`、`du -ch /tmp/baize_*.gguf | tail -1`、`df -h /tmp`，写进 MEMORY。
- 清理只做一次；完成后在 `llamacpp.txt` §7 记「残留已清」+ 保留清单。

**③ 交付与纪律**
- 交付：① `llamacpp.txt` §6 检查点表（A–E 至少 3 项有结论）② 清理报告（前后计数 / 释放空间 / 保留清单）③ MEMORY 顶部 1 条状态 + 当日 daily ④ 若已定位 bug，按 14:0x 令给修复 diff + PR 草稿（先报告等确认）。
- 纪律不变：`CUDA_VISIBLE_DEVICES=""`；`-t 8`、`nice -n 19`、CPU ≤80%；🚫 不碰 GPU/S1、不碰其他线；结果 JSON 不入库；心跳写 `未完成指令：有` ⇒ `WAITING: 0`。


### [运维令] 2026-11-04 14:0x（**继续调试：定位 llama.cpp 映射 bug 的具体环节，修复并贡献 PR**）· 用户直令 · 最高优先

> 用户原话（2026-11-04）：「安排 pretrain 继续调试，争取解决这个问题，给 llama.cpp 贡献 PR。」（friend 复核：定案已到「错误类型=映射/计算错误」，但「具体哪个环节」尚未收口，需逐层定位。）

**① 背景（已定案的部分）**：logits 1-token 即偏 3.6 nats（`"Hello"` 后 HF top -0.78 vs llama.cpp -4.38），已排除「F16 递归累积精度」，锁定为「映射/计算错误」。裁决「当前不采纳」不变。**本轮要做的 = 把「映射错误」收口到「具体哪一步」，修复之，并产出可提交上游的 PR。**

**② 排查优先级（friend 提供的历史 bug 先例，运维已验，按此顺序）**：
1. **group 展开语义（最高嫌疑）**：HF Mamba2 早期用 `torch.repeat`（tile 模式 `[W,X,Y,Z,W,X,Y,Z,...]`）是 bug，正确语义是 `repeat_interleave`（`[W,W,W,W,X,X,X,X,...]`）；Nemotron-H 的 Mamba2 mixer 有过对应 `repeat→repeat_interleave` 修复。BaiZe `n_groups=8`。对照 `ggml/src/ggml-cpu/ops.cpp` 的 `ssm_scan_f32` 里 `g = h / (nh/ng)`（repeat_interleave 语义）是否正确、以及 `src/models/mamba-base.cpp` 的 `build_mamba2_layer` 里 B/C 的 `view_4d(..., d_state, n_group, ...)` 是否与 reference 一致。
2. **conv1d 维度**：llama.cpp Nemotron-H 早期有 conv 维度 bug（`ggml_ssm_conv` 断言的 `ne[1]=17728` vs 期望 `d_inner=12288`，PR #15572 相关；后 fix 用实际值 12288）。核对当前 `build_mamba2_layer` 里 `conv` 的 reshape 与 `d_inner + 2*n_group*d_state` 展开是否正确，BaiZe 实际 d_inner=4096、d_state=128、n_group=8 ⇒ `2*8*128=2048`，`d_inner+2048=6144`，需对照 reference 该维度。
3. **dt 投影 / softplus 映射**：`mamba_dt_min=0.001, mamba_dt_max=0.1` 的 softplus 对称映射是否与 HF 一致（`ggml_compute_softplus_f32` + `expf(dt_soft_plus * A[h])`）。
4. **逐层 dump 定位首个偏差层**（friend 最有效手段）：1-token prompt，逐层 dump hidden state，找出「第一层 Mamba2 之后即偏」还是「第 1 层一致、后续放大」→ 前者锁 `build_mamba2_layer`，后者查层间传递/attention 路径。

**③ 修复与 PR**：
- 定位到具体 bug 后：改 `src/models/mamba-base.cpp` / `ggml/src/ggml-cpu/ops.cpp`（或 nemotron-h.cpp），重编译 → 重跑 1-token logits 对齐（目标 |Δ|→0），再重跑 sciq/piqa limit=100 与 HF 对照（目标 Δ≤1pp）。
- **PR**：修复确认后，按 llama.cpp 贡献规范整理 commit + PR 描述（背景：Mamba2-hybrid n_groups=8 / 现象 1-token logit 偏差 3.6 nats / 根因 / 修复 / 前后 logits+lm_eval 对照），提交到 `/nas_train/app.e0031982/code/llama.cpp` 的 fork/branch（🚫 直接 push master）；落地前先报告 PR 草稿等用户确认再发。

**④ 交付**：① 定位结论（具体是哪个环节 + 证据：首偏差层/逐层 logit 对照）② 修复 diff + 重编后 1-token 对齐结果 + sciq/piqa 复判 Δ ③ PR 草稿（等确认）④ 更新 `llamacpp.txt` §6：标题「定案」改为「定案（错误类型）」，补「具体环节已定位为 X」，§7 裁决同步。

**⑤ 纪律**：🚫 不碰 GPU（`CUDA_VISIBLE_DEVICES=""`）；🚫 不影响 S1（`-t 8`、`nice -n 19`、两机 CPU ≤80%）；🚫 禁止 `pkill python`/宽泛 kill；不碰 vision/data/harness；commit `pretrain eval:`；心跳写 `未完成指令：有` ⇒ `WAITING: 0` 直到交付。

> 📦 §运维令 2026-11-04 13:2x（logits 逐 token 对齐定案）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-04 第五批」节；**结论**：✅ 1-token 即偏 3.6 nats，定案=映射/计算错误（非精度累积），llamacpp.txt §6+§7 已更新，commit eca8b7f49。需要时再读。

> 📦 §运维令 2026-11-04 09:3x（llama.cpp 提速 pilot）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-04 第五批」节；**结论**：✅ llh 打分打通、5/5 eval 完成（10K/30K 有效 Avg=50.00%/50.25%；20K/40K/50K 因权重 NaN 无效）；llama.cpp 精度不可用，保留 HF float32。需要时再读。

> 📦 §运维令 2026-10-29 14:1x（整理并提交 baize-llm 独立仓库）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：✅ commit e1c6be4 pushed to origin/master，28 files（README 19.6KB + configs/9 + scripts/18 + docs/2 + .gitignore），symlink 已删除+纳入 .gitignore，ls-remote 匹配。需要时再读。

### [运维令] 2026-11-02 11:1x（**CPU 评测 5 个 checkpoint 的常识推理 8 集（1w–5w 步），先估 ETA**）· 用户直令 · 最高优先

> 🧭 **运维提示（2026-11-02 16:0x）——CPU 冒烟卡点的根因已定位，别再在 dtype/device_map 上绕**：
> export 已完成（`hf_iter_10000/18000/20000/30000/40000` 都在，safetensors 完整），**卡点在 HF 模型加载报错**：`p6_tf5` 的新版 transformers（含 `nemotron_h`）要求 `mamba_dt_limit`（→HF 侧 `time_step_limit`）是 **tuple**，但 `export_hf.sh` 生成的 `config.json` 里写成了 **JSON list** `["mamba_dt_limit": [0.0, "inf"]]`，触发 `huggingface_hub` strict 校验：`expected a tuple, got list`。
> **修法（很小）**：改 `config.json`（或 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/convert_mcore_to_hf.py` 的 config 写出逻辑），把 `mamba_dt_limit` 写成 HF 能接受的形态——最简单是**直接删掉 `config.json` 里这个字段**让它用默认（`time_step_limit=inf`），或改为 `[0.0, null]`/对应 tuple；改完重新 `python -c "from transformers import NemotronHForCausalLM; ..."` 在 CPU 加载验证 PASS 再继续。注意 vllm env 的 transformers 4.57 不认 nemotron_h，必须用 py310 + `PYTHONPATH=p6_tf5` 前置。修正后可跳过重复 export，直接在此 config 上冒烟测速 → 报 ETA。

> 用户原话（2026-11-02 11:1x）：「先用 CPU 评测 5 个检查点：1w–5w 步各一个。需要先估 ETA（多少时间，多少 CPU 核等）。」

**① 现状（运维已核）**：
- **GPU 全满**：`.12`+`.29` 各 8 卡 100% util、~75GB/卡，全被 S1 占用；**评测必须纯 CPU，🚫 不许碰 GPU**。
- **checkpoint 齐备**：`nemo_experiments/baize2b/checkpoints/` 下 `iter_0010000/0020000/0030000/0040000/0050000` 均存在（5000 步一档，save_interval=2000，故 10000/20000/30000/40000/50000 全有）。
- **HF 导出脚本就绪**：`baize-llm/scripts/export_hf.sh <iter>`（mcore distcp → HF safetensors，CPU 操作，产出 `hf_iter_<iter>/`）。已有 `hf_iter_18000`（4.4GB）作样例。
- **评测链已通（历史 P-6）**：环境 = `PYTHONPATH=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5`（transformers 5.17 含 NemotronHForCausalLM）+ `vllm` env 的 lm_eval 0.4.13；脚本 `run/baize_p6_lmeval.sh`（`--model hf` + `dtype=bfloat16`）。⚠️ 原脚本**走 GPU**，CPU 评测需改 `device=cpu`。
- **8 集**（Aligned Xmodel-2 Table 2，zero-shot，与 P-6 同口径）：`arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande`（同一 Avg）。
- **CPU 资源**：两机各 224 核。

**② 本轮必做（先估 ETA 再全量，不许跳过）**：
1. **export 5 个 ckpt**：`for it in 10000 20000 30000 40000 50000; do bash baize-llm/scripts/export_hf.sh $it; done`。记**单个 export 实测耗时**（`export_hf.sh` 内 `check_rope.py` 若加载模型，务必 `device=cpu`/`CUDA_VISIBLE_DEVICES=""`，别抢 GPU）。
2. **CPU 冒烟 + 测速**：改 `baize_p6_lmeval.sh` 为 `device=cpu`（`--model_args "pretrained=...,dtype=bfloat16,device=cpu"`），先 `--limit 8` 冒烟（8 任务 × 8 样本）确认 CPU 跑通+出分，再测**单集全量 CPU 耗时**（hellaswag ~40k 样本、arc_easy ~5.7k 等大头）→ 反推「8 集全量 / 5 ckpt」的总耗时。
3. **报 ETA（先回报，不直接全量）**：给 ① 5×export 耗时 ② 单集 CPU 全量耗时 ③ 8集×5ckpt 总墙钟 ④ 推荐 CPU 核数/并行度（每 ckpt 用多少核、8 集是否多进程并行） ⑤ 是否 24h 内可完成。写进 `MEMORY_PRETRAIN_2B.md` 心跳回报。
4. **ETA 确认后全量评测**：5 ckpt × 8 集 CPU 评测，结果落 `nemo_experiments/baize2b/lm_eval_results/`。

**③ 交付**：① 5×8 集汇总表（Avg + 逐集）+ 对照 P-6 起点 0.4395@20k/655M + Xmodel-2/Phi-1.5 参照线；② 能力-vs-step 曲线数据（1w~5w 五点）；③ `reports/report_pretrain_cpu_eval_8sets_zh.html`（中文 HTML，0 script/0 外链）；④ 日报。

**④ 纪律**：🚫 不碰 GPU（`device=cpu` 硬性、必要时 `CUDA_VISIBLE_DEVICES=""`）；🚫 不影响 S1（CPU eval 线程数别挤训练进程，可 nice）；不碰 vision/data/harness；commit `pretrain eval:`；心跳写 `未完成指令：有` ⇒ `WAITING: 0` 直到报告交付。

**⑤ ⚠️ 机器分工（2026-11-02 用户补令 · 硬性）**：本轮 5 ckpt 的 export + CPU 评测**可以用 `.12` + `.29` 两机 CPU**（此前 `.29` 的 harness 失控评测已被 kill，CPU 已恢复正常）。硬约束：**两机各自的整机 CPU 利用率都 ≤80%**——用 `taskset`/`OMP_NUM_THREADS` 限单进程线程、`nice` 降权、控制跨 ckpt 并行度，实测并在心跳报 `.12`/`.29` 各自 CPU%。export 与评测文件走 NFS 共享路径（`/nas_train`、`/nas_user`），两机同盘，结果互通。

> 📦 §运维令 2026-10-28 17:0x（预训练项目目录定位）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-04 第四批」节；**结论**：✅ 脚本&文档落 baize-llm/baize-llm，commit e1c6be4 pushed 28 files；启动口径 `bash .../baize-llm/scripts/train.sh <stage>` 仍有效。需要时再读。

> 📦 §运维令 2026-10-28 11:5x（blend 逻辑中文 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：报告已交付 `reports/report_pretrain_blend_logic_zh.html`（11KB, commit aa6d3eddf），澄清训练时不会串行出不同源（索引层交错）。需要时再读。

> 📦 §运维令 2026-10-28 10:0x（预训练计划定稿）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31」节；**结论**：计划已定稿并执行，GBS=256/2.94T/700k运行中，pre-blend完成/nw=8恢复/613K，Decay后置待data线。需要时再读。

> 📦 §运维令 2026-10-28 09:3x（锁定 613K 配置 + spawn 调优）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：613K 配方已冻结（16K/CP1/DP16/FP8/graph-OFF），根因=数据加载串行化(nw=0)，spawn 路径被 10:0x pre-blend 取代。需要时再读。

> 📦 §运维提示 2026-10-27 15:2x（cimi MCP web search 已配好）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：MCP 工具就绪（cimi_search/cimi_fetch/vqa/text_to_image），授权永久有效。需要时再读。

> 📦 §运维令 2026-10-27 13:1x（杀掉 S1 + spawn smoke）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：S1 已杀，spawn 方案被 2026-10-28 10:0x pre-blend 取代。需要时再读。
> 📦 §运维令 2026-10-27 10:4x（不放弃：spawn 验证 + web 调研）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：spawn 被 pre-blend 取代；web 调研授权仍有效（见 15:2x）。需要时再读。
> 📦 §运维提示 2026-10-27 09:2x（DataLoader OOM fork-COW 根因 + spawn 方案）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：fork-COW 是 RSS 累积根因，spawn 方案被 pre-blend 取代。需要时再读。

> 📦 §运维提示 2026-10-27 08:4x（内存使用率>95%触发告警）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：内存纪律已纳入日常监控，调试时盯内存+swap，逼近95%先降载。需要时再读。

> 📦 §运维令 2026-10-26 22:0x（S1 吞吐对齐 613,992：归因 + 方案 A/B/C）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：#798 归因=gbs128 固定开销摊薄不足；吞吐目标 ≥600K 由后续 10:4x/13:1x 令推进（spawn 验证中）。参数口径 2.220B 仍有效。需要时再读。


> 📦 §运维令 2026-10-26 21:3x（RoPE θ 未生效：评估 + 方案 + 重启）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：θ=1e6 实现路径(ii) `--rotary-base` CLI + recipe 透传，commit ae3a093，三重验证 PASS；#799 运行时确认 θ=1e6 + 0崩；rank15 崩因=DDP DETAIL wrapper（非θ）；--dir 修正已落地。**仍有效红线**：check_rope.py PASS 需 ckpt（待 S1 重启）；lr-decay-shape exponential Decay 前验证。需要时再读。


> 📦 §运维令 2026-10-26 19:2x（预训练正式落地并开跑）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31」节；**结论**：全10步已完成，S1运行中(iter30660/700k,loss2.151,~598K tok/s)，TB6006常驻，RoPE PASS，Decay阻塞待data线。需要时再读。

> 📦 §运维令 15:3x（预训练构想报告 + ETA）**已完成**（#794：`report_pretrain_baize2b_pretrain_plan_zh.html` 22.5KB；§五执行口径已补）→ 原文归档 run/ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 14:3x（补写 #792 双机实测进吞吐报告）**已完成**（#793：报告 14,208→20,888B）→ 原文同上归档。
> 📦 §运维令 13:2x（FP8 真实数据 16K/32K 实测）**已完成**（#792：16K=613,992 / 32K CP2=351,526）→ 原文同上归档。
> 📦 §运维令 11:1x（双机 16 卡调优 seq16K/32K）**已完成**（#791 8卡首跑 + #792 双机实测覆盖）→ 原文同上归档。
> 📦 §运维令 09:1x（优化 16K/32K 吞吐至 600K+）**已完成**（#791 8卡 + #792 双机 16K=613,992 ≥600K）→ 原文归档 ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 08:2x（写最近工作报告 · 中文 HTML）**已完成**（#790，report_pretrain_recent_work_zh.html 20KB）→ 原文同上归档。
> 📦 §运维令 2026-10-25 23:0x（通宵攻坚：tokens/microbatch 悬崖）**已完成**（#784–#789：真因=CUDA Graph 顶格停滞·关 graph 修复·16K 双机 613,992 达标；根因报告 + seqlen rev3）→ 原文归档 ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 2026-10-25 20:2x（seq 掉速排查初版）已并入 23:0x 通宵令 → ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维令 2026-10-25 17:5x（seq×tok/step 16卡网格）已完成（cfg1-4 OK）→ ARCHIVE_OPERATOR_PRETRAIN.md；注意「seq≥8192 崩 5x」已被 cfg0a 证伪。需要时再读。
> 📦 §运维令 2026-10-25 07:4x（双机 16 卡吞吐报告）已完成（#770-#776）→ ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维令 2026-10-24 23:5x（双机调通→吞吐优化）已完成（606,300 tok/s）→ ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维指令 2026-10-24 16:0x（305K 最佳实践+longctx 报告）已完成 → ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

> 📦 §2026-10-16:4x（#548 误判更正）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：#548 误判根因=NFS 旧日志，判活规则已修正。需要时再读。

> 📦 §2026-10-16:2x（P0 resume + 长期授权）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v2 resume 闭环，长期授权训练挂了自行重启。需要时再读。


> 📦 §2026-10-17 两块（P0 中继抢修 / `_orig_mod` 崩溃修复）均已闭合 → 原文已在 `daily-memories/2026-10-17.md`；结论：中继 PID2706247 健康（RUN_ID118-122 exit=0）；`_orig_mod` 修复验证通过，断点续跑至 6890/19980 无崩。

### 💡 最佳实践 / 硬口径（常驻 · 每次唤醒先看）
> 📦 已归档（R3配比 / LaTeX / R2收官 / T3）→ `ARCHIVE_OPERATOR_PRETRAIN.md`。

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

> 📦 §R2.4 约束（R2 实验预算/超时裁剪/vision 让行；R2 P-1~P-8 已全部完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md。**仍有效条款**：绝不杀他人进程 / 收尾不杀 loop（见 git 同步规则）。需要时再读。

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

