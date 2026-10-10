# BAIZE_PRETRAIN_2B_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

### 🆕 运维指令 · 2026-10-10（📄 昨夜工作汇报 HTML）· 用户直令 · 高优先

> **用户令**：「关于昨晚的工作，请 pretrain 写 html 报告。」

**① 交付**：`report_10_09_pretrain_overnight.html`（落 `doc/BaiZe-ISEDA2027/`）

**② 内容 = 昨夜（10-09 夜 → 10-10 晨）两项工作汇总**（均 ✅ 完成、各已有详报 → **本报告做「昨夜汇报」汇总 + 指针，不重复贴全文**）
1. **① 参数匹配对比基准（P-9.11-F，Dense-Match vs Hybrid/BaiZe）**：DM 可服务至 1M（prefill 2,351 / decode 64.9）· **2M 不可服务**（输入 > max_total_num_tokens≈1.23M）· 架构优势 **2×**（Hybrid 2M vs DM 1M）· warmup 归因修正 281×→24.5× · VRAM(128K) 52.36→59.02GB 修正。→ 详报 `report_pretrain_baize_vs_dense_fair_zh.html`（指针）。
2. **② Muon vs AdamW A/B**（各 1000 步 · GBS16 · seq4094 · bf16 · 同 seed）：Muon loss **3.112** vs AdamW **4.003**（**−22.3%**）· 吞吐 87K vs 118K tok/s（**−26%**）· 显存 53.8 vs 39.0GB（**+38%**）· 均 rc=0 / 0 NaN / 0 skip。→ 详报 `report_pretrain_muon_vs_adamw.html`（指针）。

**③ 格式（house style）**：自包含 · 内联 CSS + 内联 SVG · 零外链 · ≤200KB；已有详报只给指针。

**④ 必含「对 P-8 的启示」**：① DM 对比 → BaiZe 长上下文服务能力佐证；② Muon → **loss 质量更好但吞吐/显存有代价**，P-8 是否采 Muon/dist_muon 的取舍（只记结论，不启动 P-8）。

**⑤ 纪律**：🚫 不启动 P-8（10-02 暂缓令未撤）· 🚫 不 kill watchdog · 只汇总已固化数字、不新增实验 · 收尾按「收尾铁律」commit+push（前缀 `pretrain 昨夜报告:`）· 若 TASK 超 32KB，按规程自行归档已闭合旧块（含上方「运维调整/运维更正」两块）。
### 🆕 运维调整 · 2026-10-09（🔁 只用 `.29` + 改序：**① 对比基准 → ② Muon vs AdamW**；撤下 T1/T2/T3）· 用户直令 · **最高优先（覆盖下方 ⚗️Muon 与 🌙夜班 两块）**

> **用户令**：「pretrain 的实验都安排在 `.29`，`.12` 我会安排 vision 的实验。实验次序调一下：**1) 参数匹配对比基准；2) Muon vs AdamW（各自 1000 步，GBS=16，seq=4096，对比 loss）**。」

**① 机器改动**
- **所有 pretrain 实验一律在 `.29`**。🚫 **不要去 `.12`**（`.12` 归 vision）。
- ⇒ 撤销下方 ⚗️ 块里「占 `.12` + 登记 `GPU12_ALLOC.md`」的要求。

**② 次序**：**① 参数匹配对比基准**（`report_pretrain_baize_vs_dense_fair_zh.html`）**→ ② Muon vs AdamW**。

**③ Muon vs AdamW（用户给定口径，取代 ⚗️ 块的 Step 1）**
- **两臂各 1000 步 · GBS=16 · seq=4096 · bf16 · 同 seed**；**对比 loss 曲线**（附 grad-norm / 吞吐 / 显存）。
- 仍**先做接线三步核查**：本地 `megatron-core 0.16.1` 是否含 `muon.py`/`emerging_optimizers` → 缺则 `pip install emerging_optimizers`（环境隔离）→ `pretrain_launcher.py`/`recipe.py` 透传 `optimizer=muon`/`dist_muon`。**参数分组：2D 矩阵→Muon；1D/norm/embed/lm_head/SSM 标量→AdamW**。
- 先跑通 smoke（1 卡小步）再铺两臂；跑不通即如实报「卡在哪」，不熬夜 debug。

**④ 撤下「其它实验」**（用户：「其它实验有价值吗，我还没看出来」）
- 🚫 **T1 长上下文适配 / T2 等参 Dense 训练侧 / T3 R3 配比迁移 A/B 一律不做**，**留作 backlog**（理由：T3 landscape 平坦→大概率 null；T2 属论文润色；T1 服务 Stage (ii)、宜用 P-8 真基座）。
- ⇒ 撤销下方 🌙 块的全部内容。

**纪律**：🚫 不启动 P-8 · 🚫 不 kill watchdog · 分阶段 commit（`pretrain 对比:` / `pretrain Muon:`）。

---

### 🆕 运维更正 · 2026-10-09（✅ **NeMo/Megatron 支持 Muon** —— 更正上条「未接入」的旧判断）· 最高优先

> **更正**：上条「Muon 未接入 / 实现风险」引的是 `run/EXPERIMENTS.md` 里 **S3-03 的旧结论（已过时）**。**查官方原文后**（2026-10-09）：
> - **Megatron-Core** 有 `core/optimizer/muon.py`（shim → `emerging_optimizers`）+ `core/optimizer/emerging_optimizers` + `layer_wise_optimizer`（`dist_` 前缀 = layer-wise **distributed** Muon）。
> - **Megatron-Bridge（NeMo）** 有 Muon recipe：`bridge/recipes/utils/optimizer_utils.py`（含 `muon_extra_scale_factor` / `muon_scalar_optimizer`＝嵌入/偏置/norm 的标量优化器）。
> - **NVIDIA blog（2026-04-22）**：Muon 经 **Emerging-Optimizers** 库进入 Megatron-Core；**NeMo Megatron Bridge 26.02** 已实测 Muon 吞吐（GB300 上近 AdamW 持平）。
> ⇒ **探针改为「三步核查」，不再当"从零实现"**：① 本地 `megatron-core 0.16.1` 是否含 `muon.py`/`emerging_optimizers`；② `megatron.bridge` 版本是否有 Muon recipe（`optimizer_utils`）；③ **缺则 `pip install emerging_optimizers`**（注意环境隔离）；④ 在 `pretrain_launcher.py` + `mamba2_hybrid_2b/recipe.py` 透传 `optimizer=muon`/`dist_muon` + muon 参数。**跑通即进 A/B。**
> ℹ️ 官方对大规模 Muon 推荐 **layer-wise distributed optimizer**（整层分给各 DP rank，避免正交化时的额外通信）。

---

> 📦 **§运维指令·2026-10-09（⚗️ Muon vs AdamW · 原 `.12` 方案）已被上方「🔁 运维调整」覆盖** → 原文见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（2026-10-09 搬运，**原文未改**）。

---

> 📦 **§运维指令·2026-10-09（🌙 夜班填空 T1/T2/T3）已被上方「🔁 运维调整」**取消**（用户看不出价值）** → 原文见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（2026-10-09 搬运，**原文未改**）。backlog：T1 长上下文 / T2 等参 Dense 训练侧 / T3 R3 配比迁移。

---

> 📦 §运维确认·2026-10-09（✅ GO：#252 门控通过）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：对比报告 report_pretrain_baize_vs_dense_fair_zh.html 23.7KB 已生成。需要时再读。

---

> 📦 §运维指令·2026-10-09（📊 补测+中文对比报告：参数匹配 Dense vs Hybrid）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：参数匹配 Dense Llama 2.229B vs Hybrid 2.220B SGLang 对比完成，ctx 扫到 hybrid OOM，报告 23.7KB/5表。需要时再读。

---

> 📦 §运维指令·2026-10-09（🔎 自查：BaiZe vs MiniCPM5 公平对比盘点）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：C1-C6 逐条自评完成。需要时再读。

---

> 📦 **§运维指令·2026-10-09（💡 提 3 个实验 idea）已闭合（#251 已交付：①P-8 彩排 ②P-8 44B 下限 ③R3 配比迁移，+ 建议立即起 P-8）** → 原文见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（2026-10-09 搬运，**原文未改**）。

---

> 📦 **§运维指令·2026-10-09（📄 R3 数据配比搜索收官报告 HTML）已闭合（#246 报告已交付）** → 原文见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`（2026-10-09 搬运，**原文未改**）。**结论**：`report_pretrain_r3_data_mix.html` 52.6KB 已生成 + commit 00682e58 + push。

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_PRETRAIN.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_PRETRAIN_2B.md` / `daily-memories/` / `EXPERIMENTS_*`）。本节为「无」时按下方 Round 2 默认顺序推进。⚠️ **唯一例外（2026-10-06）**：按「📉 体积维护规程」，agent **可把「已闭合」的运维块/旧正文【原文】搬入** `run/ARCHIVE_OPERATOR_PRETRAIN.md`（**只搬迁、留 1 行指针**；不新增/不改写任何指令）。

> 📦 **2026-10-06 已归档**：「B1 ctx 扩到 1M」+「hybrid 优势论证」两个运维块均已完成，原文见 `ARCHIVE_OPERATOR_PRETRAIN.md`。结论：PPL 1M=55.42 无退化，bottleneck=(c) attention O(n²) ≥512K，目标 ctx=32K–128K，advantage report 已交付。

> 📦 §运维指令·2026-10-07⑤（T1 bf16-SSM重跑+T2公平对比+T3提速+T4效果）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：T1/T2 v2 ✅ warmup-corrected — float32 vs bf16 SSM **无差异**(1.00×)，hybrid 比 dense 快 2.8-4.3×(128K-256K)，「dense 3.3× faster」是 warmup 假象已撤回；T3 短名单(C1 FP8-TP1/C2 recompute+MBS4) + T4 短名单(Q1 100B tokens/Q2 data mixture) 已交付。需要时再读。

> 📦 §运维指令·2026-10-07④（5份研究型HTML报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：5份报告(r1-r5)全 ✅ 交付，r4 去重完成。需要时再读。

> 📦 §运维指令·2026-10-07③（hybrid ctx扩2M-16M+显存归因）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-9.11-F ✅ — 2M@0.6 SERVED(TTFT=427s), 4M@0.85 TIMED OUT(servable but ~33min), 8M/16M单卡不可服务；VRAM恒定=mem-frac=0.3预分配假象(0.6→76GB)；V4② bf16 vs f32 1.67× **已更正为warmup假象**。需要时再读。

> 📦 §运维指令·2026-10-07②（长上下文推理成本矩阵 128K-1M）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-9.11-E COMPLETE — Dense OOMs@512K(KV pool=455K tokens), Hybrid serves 1M@~26GB(near-constant = `--mem-fraction-static 0.3` 预分配 ~24GB, 与 ctx 无关); 128K-256K Dense faster 1.7-3.3x prefill / 2.2-2.6x decode。**sglang flag 沿用**：`--mem-fraction-static 0.3 --attention-backend flashinfer --mamba-ssm-dtype float32` + `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。需要时再读。
> 📦 §运维指令·2026-10-07（📊 交付：昨夜工作汇报 HTML）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：report_10_07_pretrain_overnight.html 已由 #164 交付(26.5KB,自包含,全自检过)。需要时再读。


> 📦 §运维指令·2026-10-09（T3 提速验证：recompute+FP8）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：Test 1 (recompute28+MBS4 TP1) **OOM** 79.2GB — recompute 对 Mamba2-hybrid 无效（52/56 层 SSM 激活常量级，仅省 ~0.6GB）；Test 4 (FP8 TP1 MBS2 M=8192) **s=0.915** 228K tok/s（慢 9%）；Test 2&3 跳过。**P-8 最优 = TP1·MBS2·bf16 = 249K tok/s 确认**。需要时再读。


> 📦 §运维指令·2026-10-08（R3 数据配比搜索）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：R3 6维搜索完成，r3_best_blend.txt 已生成，Stable段配比已回写 DATA_MIX_RECIPE.md。需要时再读。

> 📦 §运维指令·2026-10-08（更新论文 LaTeX）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：R2 实测数据已写入 4_llm_pretrain.tex / 3_architecture.tex，main.pdf 已 commit。需要时再读。

> 📦 §运维指令·2026-10-08（R2 收官报告 HTML）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：report_pretrain_r2_final.html ✅(46KB) 已生成并 commit。需要时再读。


> 📦 §运维指令·2026-10-06（裁决+提速令：批准A/B/D，C暂不动/E不做，NCCL拓扑核查+提速清单）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-9.12 NCCL已在用NVLink(P2P 100%,用户PCIe假设证伪,busbw 164.56GB/s),P-9.13 env无提速(249K tok/s上界),A 36/36✅(BBH峰值14.26%@2.62B),B✅(ABF不降反升+2.71pp,passkey 0%),D✅(VRAM 5.35GB恒定4K→128K)。需要时再读。

> 📦 §运维指令·2026-10-06（空窗提案：5条候选A-E）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：运维裁决✅A/B/D批准,⏸C暂不动,🚫E不做。A/B/D均已✅COMPLETE。需要时再读。

### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**（「收尾铁律」第 0 步已同步此判据）。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）**原文**搬入 `run/ARCHIVE_OPERATOR_PRETRAIN.md` / `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）/ `daily-memories/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `pretrain 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**40KB**（已过 40KB 红线）⇒ **下次唤醒先归档到 ≤32KB**，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。


### 🧭 收尾铁律 · 2026-10-06（**用户指令 · 每轮唤醒必须执行，不许省**）

> **为什么新增（真实事故）**：2026-10-06 06:55 → 08:30，**data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新**（其间 agent 在改别的文件、push 得出去），**外部运维只能靠 git 判断死活** ⇒ 被**误判成静默卡死并上机排查**。
> 根因：**「更新记忆 + push」以前只是建议、没有硬约束**；loop 的兜底 push 间隔是 **5h**（本日已缩短），且只覆盖固定白名单 —— **不许依赖兜底**。
> 🚫 **旧口径（已废）**：「每 5 小时由 loop 兜底 push 一次」**不再作为交付保障** —— 兜底只是保险丝，**不是你的提交手段**。

**每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：**

0. **体积自检（先跑，数字要抄进下一步的心跳）**：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 **≤ 32KB**；**任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档**（见本文件「📉 体积维护规程」：只把**已闭合**内容**原文**移入 `run/ARCHIVE_OPERATOR_PRETRAIN.md`、留 1 行指针），直到两者都 ≤ 32KB；**> 40KB（红线）⇒ 必须先归档再提交**（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_PRETRAIN.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. **写心跳**：更新 `run/MEMORY_PRETRAIN_2B.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并**追加 1 行「本唤醒流水」**：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. **写日报**：`run/daily-memories/<YYYY-MM-DD>.md` 追加本轮记录（**当天文件必须建**）。
3. **自己提交 + 推送**（**不许等 loop 兜底**）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_PRETRAIN_2B.md \
              doc/BaiZe-ISEDA2027/run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md doc/BaiZe-ISEDA2027/run/daily-memories
   git commit -m "pretrain #<轮次>: <一句话>"   # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 **绝不用 `git add -A`** —— 这是**共享工作副本**，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是**提交归属不可溯**（运维查不出谁在干活）。
4. **闭环自检**：`git status -sb` ⇒ **无 ahead / 无 behind**；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   **push 失败（`error: Forbidden` / 网络）**：重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下一轮唤醒第一件事就是补推**。

> ⏱️ **运维判死判据（硬）**：**心跳文件 >60 min 无新提交 ⇒ 按卡死处理**，**不再等你**。**你干得再多，心跳不动 = 仍会被判死。**

> 📦 §运维指令·2026-10-05深夜2（sglang上界+P-5b 8集+P-6②+P-9.5）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：4项全COMPLETE，4 HTML在doc/BaiZe-ISEDA2027/。
> 📦 §运维指令·2026-10-05深夜（sglang可用→BaiZe vs MiniCPM5推理对比）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-9.11 COMPLETE，H1✅prefill 2.18×, H2⚠decode 1.18×, 128K failed。
> 📦 §运维指令·2026-10-05晚（sglang conda env+proxy口径+环境隔离）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：sglang在vllm env可用(0.5.9)，proxy=http://172.19.92.25:13128，训练=py310/推理=vllm env隔离。
### 📉 体积维护规程（2026-10-03 立 → **2026-10-06 升级为「记忆 + 任务书」双约束**，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` **都每次唤醒被全文读进 prompt**（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_PRETRAIN_2B_TASK.md` ≈ **38KB**、`MEMORY_PRETRAIN_2B.md` ≈ **14KB**。
- **上限（两者相同）**：**≤ 32KB**；**红线 40KB** ⇒ **超红线当轮必须先归档才能收尾**。
- **自检**：见「收尾铁律」第 0 条（`wc -c` 两文件，**数字抄进心跳**）。
- **归档去向（只归档「历史」，🚫 不许归档「活口径」）**：
  ① 已执行完/已作废的**运维指令块** → `run/ARCHIVE_OPERATOR_PRETRAIN.md`（**留下 1 行指针**）；
  ② 被取代的**候选表/推导过程**（保留现行档 + 实测结果） → `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md` 等；
  ④ 较早的**唤醒流水**（保留最近 ~20 条） → `daily-memories/<条目日期>.md`（原文不改）。
- 🚫 **不许归档**：硬规则 / 验收标准 / **现行口径** / `WAITING:` 状态头 / 「运维问答」区。
- 指针（**必须留、只 1 行**）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 **不许改小节编号/标题**（别处有交叉引用）。
- **谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）**：`MEMORY_*.md` 一直由 agent 自滚，**任务书同理** —— **本线 agent 自己**把「已闭合」内容**原文**移入对应归档文件、留 1 行指针。⚠️ **本文件「agent 只读」的唯一例外 = 仅此「搬迁」**：原文一字不改、不动小节编号/标题、**不新增/不改写任何运维指令**（本区作者仍是运维）。**并发安全**：归档前先 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `<线> 归档: …` 前缀。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 /「进度快照」③ 最近 ~20 条流水。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变（正文/流水/快照里**不得**再出现以 `WAITING:` 开头的行）。

---



# ══════════════ ROUND 2 · **现行部分**（只保留仍未完成/仍有效的）══════════════

> R2.0/R2.1/R2.2 清单 · R9.0-bis · P-4R · P-5a 与 **Round 1（S0–S5）** 均已**完成并归档** →
> **`run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md`**（**需要时再去读，不要把整份读进上下文**）。

> 📦 §P-6 lm_eval 8集+scaling law（已完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md；**结论**：P-6① Avg=0.4395@655M, P-6② 48/48 runs Avg 33.26%→49.22% R²=0.986, 55%→~55B tok. 需要时再读。
> 📦 §P-7 训练吞吐核查（已完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md；**结论**： dense +8% (not +24%), hybrid 85.6K vs dense 89.7K. 需要时再读。

**P-8 细节 —— 🏁 Stage (i) 完整训练（正式预训练）**

> ## ⏸ **运维 2026-10-02 指令：P-8 暂缓启动**
>
> **原话**：「**测数据配比需要时间，下载 base 也需要时间…因此 P-8 暂缓启动，先做配比实验和下载 base。**」
>
> **原因（两条前置都未就绪）**：
> 1. **`Ultra-FineWeb`(base) 还在下载**（115/64624，2.99 TB）—— 而它是 **stable 段的主力数据**；
> 2. **WSD 双阶段配比实验还没做**（见 `BAIZE_DATA_TASK.md` §0.6）—— **P-8 吃什么配比是它要定的**。
>
> **→ 所以：不要因为"P-5b 快跑完了"就顺手启动 P-8。** 前置未齐之前，P-8 不启动。
> **→ 本唤醒及后续唤醒：做完 P-4R / 恢复 P-5b 之后，仍然等 data agent 的配比方案 + base 就绪。**

> ## 🎯 这是 Stage (i) 的**本体**
> **Stage (i) 的 scope 不变 = LLM 预训练（from scratch）。**
> P-1…P-7 全部只是**前置选型实验**（token 量级 164M–655M，合计 ~85 GPU·h）。
> **P-8 才是真正把 2.22B hybrid 训出来**，作为 Stage (ii)–(v) 的基座。
> 🚫 **不要**因为"实验都做完了"就把 Stage (i) 标成完成。

> ### ⭐ P-8 训练配方（T3 定稿 · 2026-10-09）
>
> | 项 | 值 | 来源 |
> |:--|:--|:--|
> | 架构 | Mamba2-hybrid 2.22B（`--arch mamba2`，52 SSM + 4 Attn） | P-3 |
> | 并行 | **TP1 · DP8**（无通信税） | P-9.7 |
> | **MBS** | **2**（⚠️ 不是 P-5b 的 MBS=1） | P-9.7 |
> | seq | 4096 | P-9.7 |
> | 精度 | **bf16**（FP8 在 TP1 上 s=0.91 慢 9%，不用） | T3 Test 4 |
> | GBS | 1024 | P-5b / P-5a |
> | LR / 调度 | 1e-3 / WSD / warmup 5% / decay 10% | P-5a |
> | recompute | 不用（对 Mamba2-hybrid 无效：52/56 层 SSM 激活常量级，仅省 ~0.6GB） | T3 Test 1 |
> | **实测吞吐** | **249K tok/s**（last-100 步均值，1100 步长跑确认） | P-9.7 |
>
> **FP8 死路**：TP1 上 M 上限 = MBS2×seq4096 = 8192（recompute 无效 → MBS 封顶 2）→ M << FP8 交叉点 M\*≈30–32K → FP8 overhead > 加速 → s=0.91。FP8 转正需 M≥32768 → 需 TP4 → 但 TP4 通信税 −6% → 净增益被吃掉。→ **bf16 TP1 MBS2 是最终最优，无更优解**。
>
> **⚠️ P-5b 的 148K 是 MBS=1 的数字**；P-8 改用 MBS=2 → 249K（1.7× 提速：GEMM 效率翻倍 + micro-step/grad-accumulation 减半）。旧参照表里的 92.6K 是 Round 1 跨节点旧值，已作废。


**输入（全部来自前序任务，不要自行改动）**

| 项 | 来自 |
|:--|:--|
| **GBS** | P-5a 的 GBS×LR 扫描结论（若无右移则沿用 GBS=8；若 P-5a 指向更优大 GBS 则采用并注明） |
| **LR / 调度 / 退火配比** | Round 1 胜出配置（LR 1e-3 / WSD / warmup 250 / decay 500 / min_lr 1e-5 / L3(86%)+code(10%)+math(4%)）；若 P-5a 给出新 LR 则改用并注明 |
| **token 预算** | ⭐ **由 P-5b 的 loss-vs-tokens 曲线决定**（曲线何时变平 → 就在那附近取预算） |
| **精度** | 若 P-4 证明 FP8 对本架构确有加速且**不劣化 loss**，可用 FP8；否则 bf16。**必须记录采用与否及理由** |

**token 预算的三档参照（按 T3 定稿吞吐 8×H100 = 249K tok/s · MBS2 · bf16 折算）**

| 档位 | token | 墙钟 | GPU·h | 说明 |
|:--|:--|:--|:--|:--|
| **下限** | **44 B** | **≈2.0 天** | ≈384 | Chinchilla 最优（2.22B × 20）。**低于此不足以称为训练好的模型** |
| **推荐** | **100 B** | **≈4.6 天** | ≈883 | 超 Chinchilla ≈2.3×；契合论文**推理效率**卖点（推理最优需过训练） |
| **上限** | 200 B | ≈9.3 天 | ≈1786 | 时间仍充裕，可考虑 |
| ⚠️ 不计入 | 690 B（真实全语料） | **≈32 天** | ≈6144 | `/nas_train` 只剩 32T，**不要定这个档** |

> **默认按「推荐档 100B」准备**；**P-5b 曲线出来后，若曲线在更早处变平，就下调**（省钱省时）。
> ⚠️ **最终 token 预算定下后，必须在 `MEMORY_PRETRAIN_2B.md` 里写明并上报**，再启动长跑。

**训练要求**

1. **从零开始**（不加载任何预训练权重），**真实语料**（`Ultra-FineWeb-L3` 全量 en 子集 + code + math 退火配比），
   **不是** `ultrafineweb_l3_qa_700m` 那个 742M 小分片 —— **本次必须跑真正的全量语料**。
2. **WSD 完整走完**：warmup 250 → stable → **decay 尾段必须真的吃到退火混合**（这是 Stage (i) 的核心配方之一）。
3. **checkpoint 规划**：至少保留 `final` + **每 10% 一个**（供 Stage (ii) 选起点、供 P-6 画能力曲线）。
   ⚠️ 每个 ckpt（2.22B 含 AdamW 状态）≈ **~30 GB**；**`/nas_train` 只剩 32T**，先算好 ckpt 留存策略与清理时机。
4. **训练中每 500 步**记 `train loss` / `val loss` / `grad norm` / `tok/s` / **GPU 独占核验**。
5. **禁止在 P-8 期间叠加其它重 I/O 或抢卡任务**（vision / data 侧要避让）。
6. **失败即如实记录**：NaN / 发散 / OOM 一律记录**并保留当时的 ckpt 与日志**，不要静默重启掩盖。

**产出**

1. **Stage (i) 最终 checkpoint**（Stage (ii)–(v) 的基座）—— 这是本项目**最关键的单个产物**。
2. `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 追加 **P-8 节**：完整 loss 曲线、实际 token 数、实际 GPU·h、
   最终 `val loss`、与 P-5b 曲线预测值的对照（**预测量 vs 实测量**，这是对 scaling 曲线的一次真检验）。
3. **论文回填建议**：§4 应写清 **实际训练 token 数 / GPU·h / 最终 loss**，
   把"从零训练一个 2.22B hybrid"的**规模与代价如实写出来**（并处理 §6 #13 的 1.8T 误读问题）。
4. `BAIZE_PRETRAIN_RESULT.html` 更新为**含 P-8 的最终版**。
5. git commit + push（**只提交文本**；checkpoint 不入库）。

**时间盒**：**下限 2.0 天 / 推荐 4.6 天**（按 token 预算 · 249K tok/s）。**超时或连续失败不要硬撑**，
记录卡点并上报 —— 但**除非运维叫停，P-8 应跑到底**。


## R2.3 交付物

1. **`run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`**（新文件）：P-1/P-2/P-3 全部结果表 +
   每条可复现命令 + 与 Round 1 的差异说明 + **「论文回填建议」段落**（给出精确数值与文字建议，
   特别是「最优点是否在边界」「Δ 是否在噪声内」这两个结论该怎么写）。
2. 更新 `doc/BaiZe-ISEDA2027/BAIZE_PRETRAIN_RESULT.html` 或新建 `BAIZE_PRETRAIN_RESULT_ROUND2.html`（自包含）。
3. 🚫 **不要修改** `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` 与 `main.tex`——
   论文已由外部统一重构并推送，回填由外部完成。你只在报告里给「回填建议」。
4. 正常更新 `MEMORY_PRETRAIN_2B.md` 与 `daily-memories/`。
5. **git commit + push，并严格走本文件顶部的「git 同步规则」**（fetch → 必要时 `pull --rebase` → push → 确认 0/0）。

## R2.4 约束

- **总预算**（分三档）：
  - **P-1 / P-2 / P-3 / P-4 / P-6 / P-7**：短程实验，≤ 5 小时墙钟（P-6 视加载路径难度可到 6 h；P-7 ≤1h）。
  - ⭐ **P-5 是独立长任务，≤ 8 天墙钟**（P-5a 4–5 h + P-5b 20B token ≈ 2.5 天；预算允许可延到 60B ≈ 7.5 天）。
  - 超时按 **P-5a > P-6 第 1 步（现有 ckpt 的 8 集）> P-1/P-2 > P-4 > P-5b > P-6 第 2 步** 逆序裁剪，并在报告记录裁剪决策。
- **GPU**：只用 `10.239.2.29` 的 **GPU 0–7**（8 卡）。**绝不杀他人进程**。
  ⚠️ 另有 vision 任务在 **`10.239.2.12`**（另一台机器）跑——**与你无关，不要去动那台**。
- **每次启动训练前后都要记录 GPU 占用核验结果**（`nvidia-smi --query-compute-apps=...`）。
- ⚠️ **NFS 与 vision 任务共享（重要）**：两台 GPU 节点用的是**同一块 `/nas_train` 盘**。
  vision 任务的 **R2-4 需要"无争用的干净吞吐测量"**，而你启动训练同样会打这块盘。
  → **启动 P-1 之前**，先读 `run/MEMORY_VISION.md`（共享盘，你直接可见）看它的 R2 进度：
  - 若 **R2-4 尚未完成**：先做**不占 GPU** 的准备工作（代码/数据核对、P-3 的 Round 1 基线复核、脚本落地），
    **每轮唤醒重查一次**它的进度；
  - **最多等 2 小时**；超过 2 小时则照常启动 P-1，并在报告里注明"当时 vision 任务在并发"。
  → 你的**每次测量都要记录"当时 vision 任务在跑什么"**。
- 数据：P-1/P-2 沿用现有 200k docs / 165M token 即可（5000 步 ≈ 164M）；
  **P-3 若需更长的数据覆盖，先核对再启动**，不要中途断数据。
- **收尾不杀 loop（关键）**：R2 的 P-1/P-2/P-3 全部完成（或按预算裁剪到只剩需等待的项）后，把结果写进报告并 git push，然后**停在原地**：`MEMORY_PRETRAIN_2B.md` 的 `PHASE` 置 `converged`、`WAITING` 置 `1`（30 分钟长轮询）；🚫 **绝不 kill / pkill `baize_pretrain_loop.sh`**。loop 必须持续运行，以便运维远程下发新任务（会改写本任务书，下次唤醒即按新指令执行）。

---



> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。

你是推进 **BaiZe Stage(i) LLM 预训练**（Mamba2-hybrid 2B 从零 + 24h 预算高置信度超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

## ⚠️ git 同步规则（**必读，2026-10-01 新增，每次唤醒都要走**）

### 前提：这是一个**共享工作副本**

vision 任务的 agent 与本任务**共用同一份工作副本**——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

**因此：**
- **只需一个人 pull，另一个立刻看到**：vision agent 拉取后，你读到的 `$TASK_MD` 与所有文件都会同步更新。
  **不要重复 pull**，也不要因为"工作区里出现了别的任务的改动"而困惑。
- 工作区里**陌生的未提交改动很可能是 vision 任务的在途文件**。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉另一个任务的成果。
- 两个 loop 每 5 小时各自 `git add -A && commit && push`，**会互相把对方在途的文件一起提交**。
  这是既有设计的已知副作用，**不要试图"修正"它**。

### 但 loop 本身**只 push 不 pull**

`baize_pretrain_loop.sh` 的 `git_push_if_needed()` 只做 `add → commit → push`。
一旦远端被别人推进，它的 push 会 `! [rejected] (fetch first)` 失败、每 5 小时重试一次、永远失败。
**所以 pull 必须由你（agent）来做。**

**每次唤醒按顺序执行：**

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. **提交时显式指定你自己的文件**：
   `git add MEMORY_PRETRAIN_2B.md EXPERIMENTS_PRETRAIN_2B_ROUND2.md daily-memories/`
   🚫 **不要用 `git add -A`**——那会把 vision 任务的在途文件卷进你的提交。
3. 若显示 **behind / diverged**：`git pull --rebase origin main`。
   - 报 `cannot rebase: You have unstaged changes` → 是**双方的在途改动**：
     先把你自己要提交的文件 commit 掉再 rebase；🚫 不要 stash / 丢弃别人的改动。
   - 报 `Unable to create '.git/index.lock'` → **另一个 agent 正在做 git 操作**：
     等 30–60 秒重试（最多 3 次）；仍失败就记一行流水并**跳过本次 git 操作**，下次唤醒再试。
   - 🚫 **绝不** `git push --force`；🚫 **绝不** `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` **无 ahead/behind** 才算闭环。
5. 流水记一行 git 结果（沿用你已有格式）。

> 参照实现：vision 任务的 agent 在 `daily-memories-vision/2026-10-01.md:198` 已按同样方式
> `git pull --rebase` 合并远端后 push 成功——**沿用同一做法**。

---


---

