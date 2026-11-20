# 深读笔记 · rfcu4 (shanliny@hfeg0pkn001, mc72, verification)

## trace_source
- user: shanliny
- host: hfeg0pkn001 (10.129.2.10)
- session_file: 1791879279182_rfcu4.messages.json (6.0 MB, 185 msgs)
- match_count: 72
- model: deepseek-v4-flash (cxmt-deepseek-flash), agent=lead, status=completed
- started 2026-10-13T08:14Z, ended 2026-10-14T02:52Z (interactive, ~18.5h span)
- real_task_summary: UVM-like SRAM 验证环境（TIMING_VALIDATION 路径）build_rand 多轮调试，最终定位 CR 信号状态不同步根因 + monitor 采样稳定性问题。

## 对话流（user 意图 → assistant 工具链 → 关键产物）

- USER#0: 「这是一个形似UVM的验证程序，你理解一下结构」+ 11 个 SV 文件（driver/env/interface/monitor/package/ref_model/strategy_base/strategy_ext/top/transaction_base/transaction_ext）。→ A#1 结构分析（UVM 分层：driver/monitor/scoreboard/ref_model/strategy，3 个 clocking block drv_cb/mon_cb/vec_cb，4 个 modport DRIVER/MONITOR/TIMING/COLLECTOR）。
- USER#2: 「这是基于makefile的面向用户的用于调度验证文件的接口」+ file.list + makefile。
- USER#4: 「这是top.sv里的待测dut」+ CXN4HC1PS8X16M1B1C1R1W1BW1RE1_FS.v（SRAM 行为模型硬宏）。
- USER#6: 「我用 make DEPTH=8 DATA_WIDTH=16 MUX=1 build_readwrite vcheck timing_validation timing_debug all > log 跑了一下，timing.vcd 中 Q_REF 和 dut_q 全为 x，根本没正常输出…修改后将修改部分详细标出」+ log + timing.vcd。→ 这是第一个 bug（输出全 X）。
- USER#74: 「输出为 x，build_readwrite、bitwrite、redundancy_all_states 确实被你修复了，但我现在用 make … build_rand … 还是要报不少错，这是新的 log 和 timing.vcd，你看看错误在哪，怎么修复」。→ build_rand 155/408 mismatch（核心未解问题）。
- USER#86: 「你错了，绝对另有病因，仔细检查，整体检查，一步一步推导的检查，不需要吝啬算力」+ 新 timing.vcd/log。→ 推翻前一个诊断。
- USER#126: 「在 random 模式下我怀疑是 monitor 的对比有问题，对比波形我我并没有发现哪里有问题，但 error_flag 就是变为 1 了，你仔细检查下」。→ monitor 比对假阳性方向。
- USER#174: 「你在这些操作中加上 crs0e==0、crs1e==0，但这些操作本身就不应该对 crsxe 有改动，因为 sram 冗余功能本身就是和这些功能相联动的，所以我觉得这个改法可能有些问题」。→ 用户否定「在非 CR 事务约束里强制 crs0e==0」的 workaround。
- USER#176: 「所以你步骤 A 的问题怎么解决呢」。
- USER#178/181（用户给出修复方向，A 档不可用作任务说明）: 「我改完了，但还是有这个问题…error_flag 变化那个时间点有个极小的结果跳变或者说是不稳定，你让 monitor 在输出稳定的时候再对比结果应该就能解决问题」。

## 根因推导链（assistant 的多轮诊断，最终收敛）

### Bug 1（USER#6，输出全 X，已修复）
- 根因多重：① `init_driver()` TIMING 路径未初始化 bwen/test/ra_e/wa_e/wat/wav/wt/rt/trkt/byp 共 10 个信号 → X 被 DUT 误判时序违例。② `drive_transaction()` 时序竞争：Step1 在 posedge 同 delta 设 rdata_valid(NBA)，monitor 采样竞争。③ `strategy_base.add_element()` 创建 read_transaction 时从未调用 `randomize()`，`we_n` 保留 rand bit 默认 0 → 读被当写 → rdata_valid 永不为 1 → scoreboard 比对 0 次。修复：补全 10 信号初始化；`@(negedge)` 前置；`add_element` 显式设 ce_n/we_n。

### Bug 2（USER#74，build_rand 155/408 mismatch，部分修复）
- 根因：`vif_tm.test <= op.test`，而 write/bitwrite/CR 事务约束 `test==1`，randomize() 后 test=1 → DUT 进入 TEST 模式（self-timed bypass）→ Q 输出时序从 posedge+tcd 变为 negedge+tcdt → monitor 在 posedge 采到上一拍旧 Q → 整体偏移一拍。march_c（build_readwrite）不调 randomize() 故 test 默认 0 不受影响。修复：强制 `vif_tm.test <= 1'b0`。

### Bug 3（USER#126/178/181，build_rand 残余 mismatch，核心未解根因 — 本 case 选题）
- 错误数据：`Cycle #25, addr=0x0, expected=0x0051, actual=0x37e2`（actual 是有效数据，非 X → 推翻「CR 跳变致内存 X 污染」理论）。
- **最终根因（A#180）**：CR 信号状态不同步。
  - `drive_transaction()` Step2 每周期从当前事务对象的随机化字段读 CR 信号驱动 DUT：`vif_tm.crs0e <= op.crs0e; vif_tm.crs0a <= op.crs0a; vif_tm.crs1e <= op.crs1e; vif_tm.crs1a <= op.crs1a;`。
  - `random_strategy` 对非 CR 事务（read/write/bitwrite/idle）调 `randomize()`，`crs0e/crs1e`（rand bit）随机变 1 → DUT 看到 CR 边沿 → CR 地址重映射。
  - ref_model.write() 用 `crs0e_repair`（get_repaired 给的一致修复态）写；DUT 用 `op.crs0e`（随机值）写 → 数据写到不同映射地址 → 后续同地址读 mismatch。
  - 用户「crsxe 和这些功能相联动」印证：CR 模式改变读写数据映射，ref_model 与 DUT 必须用完全相同 CR 状态。
- **正确修复（A#177/A#180）**：CR 信号是 driver 维护的**全局状态**，仅 CR 操作（op.name == "COLUMN REDUNDANCY"）可更新；Step2 永远驱动状态变量 `drv_crs*` 而非 `op.crs*`；init_driver 复位 `drv_crs*=0`。**撤销**之前在非 CR 事务约束里加 `crs0e==0,crs1e==0` 的错误 workaround（破坏 CR 模式下读写联动）。
- 用户补充方向（A#181）：monitor 在输出稳定时再比对（跳过 error_flag 跳变瞬间的瞬态）。

## 金标准（取自 trace 真实产物 + 人工复核）
- 真实 driver.sv（uploads/driver_real.sv, 139 行）已含 Bug1/Bug2 修复，**Bug3 的 CR-desync 仍在**（Step2 直接 `vif_tm.crs0e <= op.crs0e`，无 CR 状态变量）。
- 本 case 金标准 = Bug3 的结构化修复模式：① 声明 `drv_crs0e/drv_crs1e/drv_crs0a/drv_crs1a` 状态变量；② Step2 用 `if (op.name == "COLUMN REDUNDANCY")` 守卫更新状态；③ Step2 驱动 `vif_tm.crs* <= drv_crs*`（不读 op.crs*）；④ init_driver 复位状态；⑤ 不出现「非 CR 事务约束 crs0e==0」式 workaround。

## 选轮判定（A 档规则）
- USER#0 「理解一下结构」= 理解任务，非交付型，不单独做 A 档。
- USER#6 / USER#74 = 干净「提出需求/表达目标」轮（诊断+修复），用户未给根因 → 可作 A 档任务说明候选。
- USER#178/181 = 用户给出修复方向 → 🚫 不可作 A 档任务说明。
- 本 case 采用 **B 档 synthesized**：真实交互 185 msg/6MB 对单轮 SUT 过重 + 无单一干净接受产物 → 合成 minimal repro（仅 Bug3 CR-desync），prompt 描述场景，金标准=结构化修复模式。

## case 规划
- case_id: EDA-Eval-DesignFlow-CrStateDesyncFix-001
- domain: verification
- track: B (synthesized)
- layer: L1-static（check 静态断言修复结构 + iverilog 语法子进程真跑 §4.2）
- 交付: `fix_cr_driver.py <in_sv> <out_sv> <report.json>` 变换脚本
- hidden B: 不同 CR 信号名（cre0/cre1/cra0/cra1）+ 不同 CR-op 名 + 不同位宽，反硬编 A
- 16 conds a-p
