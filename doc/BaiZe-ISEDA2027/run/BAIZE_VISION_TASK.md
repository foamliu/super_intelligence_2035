# BAIZE_VISION_TASK.md
> 📦 §运维令·2026-10-31 16:0x（ViT-L 68.236% + MLLM 26.10% 写进论文 ch6/ch7/摘要/intro）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#441+#442 交付 4 .tex 改稿 commit 1a2e19b2f，6页/ERR=0/UNDEF=0，数字全溯源 armE_r2 JSON + EXPERIMENTS §15.5，MME 用 ArmE-R2 实测值。需要时再读。

> 📦 §运维令·2026-10-31 11:2x（直接重写第6章 6_vision_encoder.tex）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#437+#439 交付 18行/6页/ERR=0/UNDEF=0 + report_vision_paper_edit_zh.html，commit f2ca45de5/e5145dc85。需要时再读。



> 📦 §运维令·2026-10-31 11:0x（审校第6章出修订计划）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#436 交付 report_vision_paper_revise_plan_zh.html，已被 11:2x 令升级为直接改稿并执行完毕。需要时再读。



> 📦 §运维令·2026-10-31 08:4x（波形图强化RL计划书）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#435 交付 report_vision_wave_rl_plan_zh.html 59241B/12节，覆盖9个必答问题+WaveView API实测事实引用。需要时再读。



> 📦 §运维令·2026-10-30 22:2x（写「2B MLLM 看懂波形图」能力与评测报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#424 交付 report_vision_waveform_zh.html 45236B/6节/14表，覆盖任务定义/能力拆解/数据/训练/评测/成本ETA。需要时再读。

> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

> 📁 **报告目录纪律（2026-10-28 用户直令 · 全局常驻 · 覆盖一切旧报告路径）**：所有 HTML/中文报告**一律产出在 `doc/BaiZe-ISEDA2027/reports/`**。🚫 **禁止产出到 `run/reports/` 或项目根 `reports/`**（生成器输出路径必须指向项目级 reports；run/reports 历史文件不得再新增）。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### ✅ §用户令·2026-11-06 21:3x（GRPO 为何空转：先做 advantage 方差诊断，**不训练**）· 用户直令 · 最高优先 · ✅ 已交付

> **用户令**：「好的 选A 听你的」——即选「advantage 方差诊断」方案。
>
> **不要重复劳动**：11-06 18:5x 令已 ✅交付（post-GRPO 6.2% < post-SFT 9.2%，open_ended 19.4%→11.7% 回退、numerical 5.5%→5.0% 持平，P1 50 步 loss≈0）。**假设待验**：在 9.2% 的基座上 group_size=4 时，绝大多数 prompt 的 4 条 rollout 奖励相同（全 0）⇒ 组内归一化 advantage=0 ⇒ 梯度为 0。**本令只做诊断，不训练。**
>
> **执行（一次性 · CPU · 总时长 ≤40 min）**：
> 1. 新建 `vision/wave_rl/diag_advantage_variance.py`：加载 **post-SFT step3000** ckpt（`/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/step3000`）+ `qwen3vl_2b_text_extracted`，对 **200 个 prompt**（取自 `sft_pilot_balanced.jsonl` / `waveqa_oracle_300.json`，固定 seed）各跑 **group_size=4** rollout，**完全复用** `grpo_train_wave.py` 的 rollout 与奖励函数（temperature 0.8 / max_turns 8 / max_new_tokens 48），**不得改写奖励口径**。
> 2. 每个 prompt 记：`reward[4]`、`std`、`mean`、`submit 成功数`、**题型标签**；落盘 `waveqa_advantage_diag_200.jsonl` + 汇总 JSON。
> 3. **统计口径（必须分开报）**：① 组内 std=0 的占比；② 其中「全 0 组」vs「全 1 组」各占多少（**意义完全不同**：全 1=已会做、全 0=学不到信号）；③ 按题型（numerical / open_ended / multiple_choice）分组的 std 分布与 mean；④ 有正样本但未采纳（0<mean<1）的组比例。
> 4. **决策（预注册，不许临时改口径）**：
>    - **std=0 组 ≥80% 且「全 0 组」占多数** ⇒ 判 **NO-SIGNAL**：先提基座成功率，给 3 条可选项（更多 SFT 步 / 更大 LoRA lr / 扩 SFT 数据）并各标预估成本。
>    - **std>0 组 ≥30%** ⇒ 判 **PARAM-ISSUE**：是 lr/步数不足，给 GPU 版建议配置（lr 1e-5、500 步、group_size 8、bf16）。
>    - 中间地带 ⇒ 判 **PARTIAL**：给出「group_size 加到 8」的验证方案。
> 5. **交付物**：`reports/report_vision_wave_rl_advantage_diag_zh.html`（中文单文件、无外链无 script，含分组统计表 + std 分布图（内联 SVG 或表格）+ 明确判定与下一步建议）+ `diag_advantage_variance.py` + JSONL/汇总 JSON + `EXPERIMENTS_VISION.md §21.1`。
>
> **护栏**：🚫 **本令禁止启动任何训练/GRPO/评测重跑**（不占 GPU、不改 ckpt、不写 ckpt）；🚫 不碰 pretrain（`.29`/`.12` 满载）；CPU `OMP_NUM_THREADS≤16` + `nice -n 19`；GPU-wait chain PID1365749 **不动**；🚫 不伪造数字（若 200 题跑不完，缩到 100 并如实标注）；每步 commit（`vision wave-rl-diag:` 前缀）+ push。
>
> **完成标记**：交付后本行标题改 `✅ 已交付`；未交付 ⇒ `WAITING: 0`。
>
> **✅ 交付摘要（wake #838 · 2026-11-06 23:4x）**：诊断脚本 `diag_advantage_variance.py`（CPU-only，复用 `rollout_episode`+`WaveformGymEnv` 奖励，不改口径）跑 94 prompt×4 rollout（受 40min 时限，未达 100 已如实标注，结论不受影响）。**判定 PARTIAL**：std=0 组 78.7%（<80% NO-SIGNAL 门槛）、std>0 组 21.3%（<30% PARAM-ISSUE 门槛）、全 0 组 0%（失败得 −0.5 非 0）。**关键发现**：假设"全 0 组"在本离散分档奖励下不成立——真正无信号机制是"全同档"（74 组 4 条 rollout 落同一奖励档⇒advantage=0）。按测量目标差异化：rise_time 100% std=0 全错（能力缺口，需补 SFT）、period 31.8% std=0（GRPO 信号最足，68% 有方差）、amplitude 87.5% 近饱和、duty_cycle 90.9% 近 NO-SIGNAL。建议：①group_size 4→8 验证 ②按目标差异化（rise_time/duty_cycle 补 SFT、period 即可上 GRPO）③奖励连续化（需用户批）。交付物：报告 HTML 14643B/10节 + JSONL + 汇总 JSON + EXPERIMENTS §21.1。零 GPU/未训练/未碰 pretrain/GPU-wait chain 未动。


> 📦 §用户令·2026-11-06 18:5x（vision 先上 CPU）**✅ 已交付**（wake#827-#835：P0 冒烟 5 步 365s（73s/步）、P1 50 步 ~2min/步、4 个 eval JSON、报告 15058B、EXPERIMENTS §21；结论 post-GRPO 6.2% < post-SFT 9.2% 未提升）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### §运维令·2026-11-05 17:5x（执行波形 RL 计划：Stage-1W SFT 冷启动 → Stage-2W GRPO · 分阶段）· 用户直令 · 最高优先 · ✅ 阶段0已交付 · ✅ 阶段1已交付

> **用户令**：「vision：执行 2026-10-31 波形 RL 计划书（`reports/report_vision_wave_rl_plan_zh.html`），让 2B MLLM 通过与 WaveView 交互学会看懂波形图。分阶段，先解锁待核项再训练。」
>
> **背景**：计划书已交付（59241B/12节），含环境/奖励/数据/训练/评测/成本全路线，但标注「本轮零实验·本机无 FSDB/无 license」+ 4 个「待核」项。本令把计划书从「方案」推进为「执行」，按风险分 4 阶段，**每阶段产出交付物并 commit 后再进下一阶段**。

> **🔴 阶段 0 · 可行性解锁（无 GPU · 必须先做 · 解锁 4 个「待核」）**
> 目的：在动任何 GPU / 训练前，确认 WaveView+FSDB+license 可用性并跑通最小闭环。
> 1. **定位 WaveView 主机**：确认哪台机器有 `wv` + Synopsys license + FSDB（候选：`.75` 沙盒 / ZhuLong benchmark 主机 `10.129.32.75` / 其它）。在 `MEMORY_VISION.md` 记录：主机 IP、license 串（6 server？）、可用 demo FSDB 路径（`mixed/mixed.fsdb`·`power/cpf_demo/demo.fsdb`·`hwsw_debug/multi_core/design.fsdb`·`dumper/modelsim_link_third_party/sample.fsdb`）是否真实在位。**若全不可得 ⇒ 阶段 0 即判 RED，写报告上报，不进阶段 1**（不得伪造可用性）。
> 2. **解锁 4 个待核项**（在沙盒实测，逐项记实测命令+返回）：
>    - ① FSDB 转换工具链：ngspice `.raw` / Verilator VCD → FSDB 是否有开源路径（vcd2fsdb 需 Synopsys？）；**备选**：直接用 `.raw`/VCD + Python 解析器代替 wv（保留 RL 环境框架但失去 API 兼容）——明确走哪条。
>    - ② `sx_export_image` 类截图导出 API 是否存在；若不存在 ⇒ 截图改为 episode 开始时外部预处理一次性截取。
>    - ③ `sx_open_sim_file_read` 是否计入「≥5 次 crash」阈值（决定单 episode wv 预算 = 3 还是 4）。
>    - ④ license 并发上限（决定 RL 并行 episode 数）。
> 3. **Gym wrapper 冒烟测试**：用 `vision/wave_rl/` 下新建 `waveview_gym.py`，包 `wv -ace_no_gui` 为确定性 Gym 环境（7 类受控 Tcl 动作 A1–A7，每 episode fresh wv 进程，单 episode wv 调用 ≤3）。在 `mixed.fsdb` 上跑 1 个 episode（open→get_signal(clock)→get_values→submit 周期），验证 observation/action/reward/terminate 全链路通。
> 4. **交付物**：`reports/report_vision_wave_rl_phase0_feasibility_zh.html`（中文 HTML/单文件/无外链）+ `vision/wave_rl/waveview_gym.py`（冒烟可跑）+ `EXPERIMENTS_VISION.md` 新增 §19「波形 RL 阶段 0」。**判据**：4 待核项各有实测结论（GREEN/RED/备选）+ Gym 冒烟 episode 跑通 OR 明确判 RED 上报。

> **🟠 阶段 1 · Stage-1W SFT 冷启动（gated on 阶段 0 GREEN · 2B MLLM · ~4 GPU·h pilot）**
> 1. **合成数据 pipeline**：ngspice（SPICE tran：RC/RL/反相器/差分对，参数随机化）+ Verilator（数字时序：分频器/FIFO/状态机）→ FSDB（或备选 .raw/VCD+Python）→ 自动生成「open→get_signal→get_values→submit」完整轨迹 + GT（周期/幅度/上升沿/下降沿/延迟）。**pilot 5000 轨迹**（含错误恢复轨迹：信号不存在→dump_hier→换名重试；FineSim 裸名 vs Verilog top.sig；时间窗空→换信号）。
> 2. **SFT 训练**：2B MLLM，LR 1e-5（LoRA r=64）或 5e-6（全量），GBS=128，~2000–3000 步（2–3 epoch）。**GPU 调度**：避开 vision R9（`10.239.2.12` 在跑）——确认用哪台 GPU 主机（.12 空闲窗口 or 别的 host），写进心跳。
> 3. **验收判据（预注册）**：held-out 合成数据上 **格式正确率 ≥90% + submit 成功率 ≥70%**。不达标 ⇒ 调数据/轨迹再训，不进阶段 2。
> 4. **交付物**：SFT checkpoint + `reports/report_vision_wave_rl_phase1_sft_zh.html` + `EXPERIMENTS_VISION.md` §20。

> **🟢 阶段 2 · Stage-2W GRPO 强化（gated on 阶段 1 达标 · ~12 GPU·h full）**
> 1. **RL 训练**：GRPO（无 value 网络，2B 省显存），奖励 = R_main（数值相对误差分档：≤1%→1.0 / ≤5%→0.7 / ≤10%→0.4 / ≤25%→0.1 / >25%→0）+ R_evidence(0.3) + R_dense(0.2) + R_anti(防 hack，直输 GT −2.0) + R_budget(0.1)。双盲抽检：每 100 episode 插 5 个隐藏 FSDB 题，>20% 差距=过拟合信号。
> 2. **评测**：WaveQA-RL ≥300 题（数值/多选/开放）+ 双参照线（纯看图 2B / Oracle Tcl 上限）+ **回归护栏**（MMStar/MMBench 掉幅 ≤1pp）。
> 3. **交付物**：RL checkpoint + WaveQA-RL 评测结果 + `reports/report_vision_wave_rl_phase2_rl_zh.html` + `EXPERIMENTS_VISION.md` §21。

> **🟣 阶段 3 · 全量扩展（可选 · gated on 阶段 2 GREEN · 用户另行批）**：合成 20000 + 真实 2000（Oracle Tcl 回放 698 机 368 命中）+ 派生 8000 = 30000 题，~12 GPU·h + ~16 CPU·h / ~4 天。**需用户再批预算**，本令不自动进。

> **铁律与约束**：
> - 🚫 不伪造任何评测数字 / API key / license；所有「待核」项必须实测，不得臆断 GREEN。
> - 🚫 不杀健康训练：阶段 1/2 的 GPU 调度必须避让 vision R9（`10.239.2.12`）；重 I/O 避让 `10.239.2.12`/`10.239.2.29`。
> - WaveView 合规：沙盒隔离、只读打开（`sx_open_sim_file_read`）、不写回设计库、受控 Tcl 子集、license 不超并发；真实 FSDB 用前确认脱敏/授权。
> - 每阶段产出交付物并 commit（`vision wave-rl-pN:` 前缀）+ push 后再进下一阶段；阶段 0 若判 RED 立即上报，不得硬推进。
> - 数字全溯源计划书 `report_vision_wave_rl_plan_zh.html` §1–§9 + 附录 A 实测踩坑；成本 ETA 标「估算」。
> - 体积：`MEMORY_VISION.md`/`BAIZE_VISION_TASK.md` 各 ≤32KB，超限自滚。

> **完成标记**：阶段 0 交付后标 `✅ 阶段0已交付`；阶段 1/2/3 各自标各自阶段。**任一阶段未交付 ⇒ `WAITING: 0`（不睡）**。



> 📦 §运维令·2026-10-28 17:3x（OCR 合成数据 10M 质量偏差裁定：接受现状）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#330 用户裁定 accept-as-is，不重生成/不过滤，10M 数据集可用于预训练/OCR SFT。需要时再读。

### [已归档] §运维令·2026-10-26 08:2x（写最近工作报告 · 中文 HTML）**已完成**（wake#279 交付 `reports/report_vision_recent_work_zh.html` 40423B/5节/0 script/0 外链）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### [已归档] §运维令·2026-10-25 22:4x（生成 1000 万 OCR 图文对）**已完成**（wake#275：9,999,999 对/2000 shard/470GB；去重 2.4486%、泄漏 113 已如实披露；用户已裁定 accept-as-is）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### [已归档] §运维令·2026-10-25 19:5x（路线①细化为执行方案报告）**已完成**（wake#272 交付 report_vision_ocr_sft_plan_zh.html 22,706B/9节）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### [已归档] §运维令·2026-10-25 17:5x（OCR 类评测偏低：OCR 合成数据调研）**已完成**（wake#271 交付 report_vision_ocr_synthdata_zh.html 29177B/8节）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### [已归档] §运维指令·2026-10-24 16:1x（写「下一步如何提升 ProtB 与 MLLM 成绩」报告）**已完成**（wake#250 交付 `reports/report_vision_next_steps_protb_mllm_zh.html` 21.1KB / 8 节 / 0 script / 0 外链，后续 A3 + B4 已执行）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。

### [已归档] §运维指令·2026-10-24 10:3x（ArmE-R2 完整实验报告）**已完成**（wake#247 交付 `reports/report_vision_armE_r2_20261024_zh.html` 26,522B / 7 节；wake#267 复核仍在位）-> 原文归档到 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

> **已归档**（2026-10-24 11:43）：ArmE 停止降 LR 重跑 / 启动 ArmE（ViT-L14）/ Stage-2 改原版 780k 三块 —— 原文均在 `run/ARCHIVE_OPERATOR_VISION.md`。


### 📦 运维指令 · 2026-10-20 08:2x（**ArmD-R2：LR 1e-3 / min_LR 1e-5 / 数据不变**）· 用户直令 · 最高优先 — 已归档

> **已闭合**（ArmD-R2 全链路 DONE 2026-10-21：①训练✅63400步 / ②ProtB✅lp64.3373·5-NN55.956 / ③MLLM三阶段✅Stage-2原版数据 / ④12集✅avg26.12% / ⑤报告✅）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-21 归档）。**结论**：ArmD-R2 vs ArmC(LR轴一致,仅data3→6源+epoch4→3) ProtB Δlp+2.005pp/Δ5-NN+1.238pp 双双正向；MLLM下游几乎持平→ProtB→MLLM传递性再次证伪。ArmD-R2 是 ArmE 的对照基线（口径值见上方 ArmE 块口径表）。需要时再读。
> **已归档**（2026-10-24 11:43）：🔥 运维令 · 2026-10-19 22:5x（**立即启动 ArmD，不要再 idle**）· 用户直令「vision：尽快启动」 — 原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


### 📦 已归档（08:2x）：ArmD 原始块（2026-10-19 21:2x）

> 已被 **08:2x「ArmD-R2」块**取代（LR 2e-3→1e-3，数据不变）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。


### 📦 运维指令 · 2026-10-18 17:1x（ArmC：min_lr 1e-4→1e-5 + wd 0.1→0.01 · 4 阶段）— 已归档

> **已闭合**（ArmC 全链路 DONE 2026-10-19）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-19 归档）。**结论**：ArmC = 两变量；训练 57250 步 ✓ / ProtB lp 62.332·5-NN 54.718 / MLLM 三阶段 ✓ / 12 集 12/12 DONE avg 25.78%（vs ArmB 26.10%，**不可分辨**）。ArmC 配置已被 ArmD 承接（见顶部 ArmD 块，**wd 0.01 沿用**）。需要时再读。

### 📦 运维指令 · 2026-10-17 12:4x/12:2x/12:0x（kill .12 pretrain→起 ArmB / .12 专属 / 启动 ArmB）— 已归档

> **已闭合**：ArmB 已训完并评测（ProtB 62.093/58.102、MLLM 26.10%），ArmC/ArmD 依次承接。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### [已归档] §运维令·2026-10-17（ArmA 中文报告 + open_clip×AIMv2-style 兼容性评估）**已完成**（wake#133：数字全溯源 EXPERIMENTS §10，不得写「AIMv2好 9pp」）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。


> 📦 2026-10-13 ~ 10-16 历史运维指令指针（~90 条单行摘要）已原文归档 → `run/ARCHIVE_OPERATOR_VISION.md`；需要时再查，不要读进上下文。
### 🏆 最佳实践（BEST PRACTICES）— 2026-10-08 锁定 · 如无特殊指定，一律按此执行

> 以下三项由 R2–R14 全线实验预注册 + 收敛后裁定，证据见对应报告/实验记录。
> 默认执行：除非运维另有指令，所有视觉编码器训练与评测一律遵循以下配置。
> 不得回退：禁止在未经运维明确批准的情况下，使用以下已被实验否定的旧配置。

#### BP-1 · 目标函数 = AIMv2-style dense objective（`--loss aimv2`）

| 项 | 值 |
|:--|:--|
| 损失 | `1.0 × InfoNCE + 1.0 × masked-patch-MSE`（双向 ViT + 随机掩码） |
| 文本塔 | 冻结 CLIP-ViT-L/14-336（768-d），不解冻 / 不用 LoRA |
| 注意力 | 双向（bidirectional）—— 🚫 禁用 causal AR（④ 已证明坍缩或 lp 极低） |
| 证据 | R11-G：lp 7.40% → 19.76%（+12.36 pp，11 点全单调，R²=0.91，无饱和）；3-epoch 续跑达 20.27% |
| 否决项 | ❌ 纯 InfoNCE（天花板 ~7.4%）· ❌ CoCa（caption-CE 坍缩 trunk）· ❌ 纯 AR（step 600 坍缩 C1=0.97）· ❌ AR+InfoNCE hybrid（lp=1.37%，−12.1 pp）· ❌ SigLIP / LocalLoss（均低于基线）· ❌ 文本塔 LoRA 解冻（−0.30~−0.80 pp） |
| 报告 | `report_vision_aimv2_impl.html` · `EXPERIMENTS_VISION_ROUND11.md §14–§17` |

#### BP-2 · 超参 = mask-ratio 0.6 + contrast:patch weight-ratio 1:1

| 超参 | 最优值 | 消融设计 | 证据 |
|:--|:--|:--|:--|
| `--mask_ratio` | 0.6 | 5 臂（0.3/0.5/0.6/0.75/0.9），倒 U 形，lp@30k=13.49% 为峰 | `EXPERIMENTS_VISION.md` mask-ratio 节 · `report_vision_mask_ratio.html` |
| `--contrast_weight` / `--patch_loss_weight` | 1.0 / 1.0（即 1:1） | 4 臂（1:2 / 1:0.5 / 0.5:1 / 2:1），1:1 最优；patch-heavy 方向更宽容但无翻盘；contrast 过高显著有害（−3.28 pp） | `EXPERIMENTS_VISION.md` weight-ratio 节 |

#### BP-3 · 评测协议 = Protocol B（主流对齐）

| 项 | Protocol A（旧 · 🚫 废弃为默认） | Protocol B（新 · ✅ 默认） |
|:--|:--|:--|
| 优化器 | AdamW lr=3e-3，无 schedule | SGD + momentum 0.9 + cosine（5-ep warmup） |
| Batch size | full-batch（49,970） | mini-batch 1024 |
| Epochs | 100（= 100 次梯度更新） | 90（≈ 112,605 次更新） |
| Probe-train | 50/类 = 49,970 张 | IN-1k full train = 1,281,167 张 |
| Eval 集 | 自切分 val（50/类 = 5,000） | IN-1k 官方 validation（50k） |
| Normalization | CLIP mean/std | ImageNet mean/std |
| 重复 | seed 0 单次 | 3 seeds（0,1,2）→ mean ± σ |
| 证据 | Δlp ≈ +10.05 pp（B−A，3 ckpts: +10.05/+10.05/+10.17，σ_cross-ckpt=0.06 pp）；主因 = 更新次数 100 vs 112,605（1126×）+ probe-train 25.7× 小 → 分类器欠拟合 | `report_vision_lp_protocol.html` · `vision/lp_protocol_bridge.py` |
| 内部横比 | 旧实验（R2–R14）均用 Protocol A，相对排序仍有效（A/B 排序一致）；但绝对数字须标注 "BaiZe internal protocol" | 新实验一律用 Protocol B；与 DINOv2/MAE/iBOT 等公开值可直接横比 |

> ⚠️ Protocol A → B 迁移说明：旧实验的相对结论（架构排名、目标函数翻盘、消融排序）不受协议切换影响—— Protocol A/B 排序一致（20.22>19.77>18.79 vs 30.27>29.94>28.84）。正式训练后的评测一律用 Protocol B；论文中旧数据标 "BaiZe internal protocol"，新数据标 "mainstream protocol"，不混表。

---


> 📦 2026-10-06~08 运维指令（8 条：①论文LaTeX ②全线报告 ③mask-ratio消融 ④GPU12对账 ⑤昨夜汇报 ⑥下一步建议 ⑦AIMv2 AR范式 ⑧队列裁定 ⑨lp协议研究）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）原文搬入 `run/ARCHIVE_OPERATOR_VISION.md` / `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）/ `daily-memories-vision/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `vision 归档: …` 前缀。
> 本轮动作：本任务书现 ≈24KB（在上限内）⇒ 暂时无需归档；一旦 >32KB 即自行滚动（`MEMORY_VISION.md` 已贴 32KB 上限，优先滚它）。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底 push 一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_VISION.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_VISION.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_VISION.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-vision/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_VISION.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-vision doc/BaiZe-ISEDA2027/run/vision
   git commit -m "vision <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。

### 0. 🎯 当前状态速览

> 📦 §0 当前状态速览（2026-10-05 晚版本，已过时）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；当前状态以 `MEMORY_VISION.md` 顶部状态头为准。需要时再读。

> 📦 §运维指令（2026-10-05 深夜2 · 两份 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_lp_eval.html + report_vision_aimv2_impl.html 已产出并提交。需要时再读。


> 📦 §运维指令（2026-10-05 深夜 · R12→3epoch + 方向建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：3-epoch 续跑 lp=20.27%（35 点 R²=0.94）；VISION_NEXT_DIRECTIONS.md 已交（方向2/3已批，方向4作废）。需要时再读。

> 📦 §运维指令 · 2026-10-05（晚 · 全量 AIMv2 训练 + 论文 §6 改写 + proxy/环境隔离口径）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：R12b 训练完成(lp_max=18.81%) + 论文 §6 改写完成 + proxy/env 口径已同步。需要时再读。

### 1. 📌 全局口径与铁律（一次性质，对所有 R 生效）


- 🚫 不许闭门造车：涉及"别人怎么做"（架构/loss/评测/数据）必须去读官方仓库或论文原文（能 clone 就 clone）—— 不得凭二手描述下结论（本线已因此出错一次）。
- 不重跑已落盘训练；不改 R8/R9/R10 已落盘结论（只在 §2 明确"修正"条目下补限定）。
- 控变量：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- 公平性：加 decoder 的臂必须报「参数量 + 训练 token + 每步耗时」，不许只比 acc。
- 预注册：判据先定后测，不许事后改。
- 体积：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` 各 ≤32KB（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（✅ C1/C2 均已完成 → 归档 `ARCHIVE_OPERATOR_VISION.md`）

> 📦 C1（数据量口径）✅ 已在报告中统一三类分母（18.5M/29M/103M）；C2（R8 结论限定）✅ 已在报告中标注「自研改编版，非官方模型」。需要时读归档。

### 3. 🔜 任务队列

> 📦 §3 任务队列（全部已完成/取消/暂缓）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：R14/E1/R11-L/L2/F/G/H/R13 全部完成，臂⑤/iGVLM 已取消。当前活跃任务见运维指令区（④-4ep 训练 + LLaVA-OV1.5 复现计划 + 中文报告）。需要时再读。

---

### 5. 📚 背景参考（输入素材，不是任务）

> 📦 §5 背景参考（2026-10-03）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：含 R9/R10 关键事实 + 官方资源核实 + 数据侧硬约束 + 口径提醒。需要时再读。
> ⚠️ **口径提醒（现行）**：R6/R7 的「正式训练切 GPIC `short`」是另一条线；R9/R10 的 scaling 实际用的是 CC12M+Amshaker —— 报告里必须写清这条区分。

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_VISION_TASK.md` ≈ 21KB、`MEMORY_VISION.md` ≈ 32KB（已贴上限）。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_VISION.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/vision/ARCHIVE_ROUNDS_2-9.md` 等；
  ④ 较早的巡检/流水条目（保留最近 ~20 条） → `daily-memories-vision/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 ③ 最近 ~20 条。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---




---

## 📁 历史轮次已归档（为省 prompt token）

ROUND 2–9 的完整任务原文已移至 `run/vision/ARCHIVE_ROUNDS_2-9.md`。

- 这些轮次均已完成；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- 需要查旧轮细节时再去读归档文件；不要把整份归档读进上下文。
- 当前指令全部在本文件上半部分（运维指令区）。
