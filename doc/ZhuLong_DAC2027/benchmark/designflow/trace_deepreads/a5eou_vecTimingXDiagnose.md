# 深读笔记 · a5eou · VecTimingXDiagnose (SRAM UVM-like 验证程序 timing 全-X 诊断)

## trace_source
- user: shanliny · host: hfeg0pkn001 (10.129.2.10) · session: 1791946337611_a5eou.messages.json
- match_count: 72 · keywords: systemverilog:1240;verilog:370;synopsys:38;rtl:26;aether:15;analog:7;synthesis:2
- domain: verification (shard A) · track: A档 faithful
- 文件: 6.2MB / 183 msgs / 93 user / 90 assistant (子目录布局 /home/shanliny/.cline/data/sessions/1791946337611_a5eou/)
- 附件源: /home/shanliny/.cline/data/sessions/1791879279182_rfcu4/uploads/ (rfcu4 为上传文件的父会话)

## 项目背景
shanliny 构建了一个「形似 UVM」的 SRAM 验证平台（自写类 UVM，非真 UVM），验证 CXN4HC1PS8X16M1B1C1R1W1BW1RE1_FS（一款 auto-generated 单口 SRAM DUT，gen1prf_spsram.py 生成）。平台用 makefile 调度，支持 build_readwrite / build_rand / build_bitwrite / redundancy_all_states / testmode 等策略，含 TIMING_VALIDATION 模式（独立 TIMING modport 路径，无 clocking block，negedge 驱动 / posedge 采样）。

## 关键用户轮（A档 eligible = 提目标、未给根因）
- **U#0 (idx=0)**: 「这是一个形似UVM的验证程序，你理解一下结构」+ driver.sv/env.sv/interface.sv/monitor.sv/package.sv
- **U#1 (idx=2)**: 「这是基于makefile的面向用户的用于调度验证文件的接口」+ file.list/makefile
- **U#2 (idx=4)**: 「这是top.sv里的待测dut」+ CXN4HC1PS8X16M1B1C1R1W1BW1RE1_FS.v
- **U#3 (idx=6) ★A档任务说明**: 「我用这个语句 make DEPTH=8 DATA_WIDTH=16 MUX=1 build_readwrite vcheck timing_validation timing_debug all > log 跑了一下验证程序，但我发现 timing.vcd 中 Q_REF 和 dut_q 全为 x，也就是根本没正常输出，文件我发给你了，你帮我看看我的 vec 验证程序错在哪，修改后将你修改的部分详细标出并告诉我」+ log + timing.vcd
  - 用户只给**症状**（Q_REF/dut_q 全 X、没正常输出），**未给根因**，要求诊断+修复+标出修改。✅ A档 eligible。
- U#37: 「build_readwrite、bitwrite、redundancy_all_states 确实被你修复了，但 build_rand 还是要报不少错」(确认 U#3 修复部分有效，暴露新问题)
- U#43: 「你错了，绝对另有病因，仔细检查」(push back)
- U#63: 「在 random 模式下我怀疑是 monitor 的对比有问题…但 error_flag 就是变为 1 了」(后续 monitor 跳变问题，非 A档任务)
- U#87-92: error_flag 跳变 / monitor 在输出稳定时再对比 (用户给修复方向 → 非 A档)

## assistant 对 U#3 的诊断（gold，idx=7/15/27）
经过多轮 read_files（driver.sv / transaction_base.sv / transaction_ext.sv / CXN..._FS.v / strategy_base.sv / ref_model.sv / monitor.sv）+ log/VCD 分析，assistant 定位**三个根因**：

### 根因 1（核心，CORE）— driver.sv TIMING_VALIDATION 路径未调用 execute()
- **位置**: `sram_driver::drive_transaction()` 的 `ifdef TIMING_VALIDATION` 分支（driver.sv Step 1 + Step 2）
- **机制**: TIMING 路径 Step 2 直接读 `op.ce_n`/`op.we_n`/`op.addr`... 驱动 DUT；但事务对象的 `execute()` **从未被调用**（仅 `else` 非 TIMING 分支调 `strategy.execute(vif)`）。`read_transaction::execute()` 才把 `we_n = 1'b1`（transaction_ext.sv:25）；不调用则 `op.we_n` 保留 `rand bit` 默认值 0。
- **后果链**:
  1. 读操作 `we_n=0` → DUT 误判为写 → `Q_r` 永不更新（Q 只在读路径更新）→ dut_q 全 X
  2. Step 1 判 `op.ce_n==1'b0 && op.we_n==1'b1` 永为 false → `rdata_valid` 永不置 1
  3. monitor 在 posedge 采 `rdata_valid==0` → Scoreboard「总比对次数: 0」
  4. Q_REF 也因参考模型路径未正常联动而全 X
- **修复方向**: TIMING 路径驱动前先调 `op.execute()` 或显式按操作类型设 `we_n`（read→1, write→0）。

### 根因 2（次要）— init_driver() TIMING 路径遗漏初始化信号
- **位置**: `sram_driver::init_driver()` TIMING 分支
- **机制**: 原版未初始化 `bwen`/`test`/`ra_e`/`wa_e`/`wat`/`wav`/`wt`/`rt`/`trkt`/`byp`，保持 X 可能被 DUT 时序检查误判。
- **注意**: 当前磁盘上的 driver.sv 是会话后期状态，init_driver 已补上这些赋值（RC2 已修复）；但 RC1（execute 未调用）**仍在磁盘版本中存在**（Step 2 仍 `vif_tm.we_n <= op.we_n`，无 execute 调用）。

### 根因 3（次要）— VCD 文件名不匹配
- **机制**: Makefile 检查 `dump.vcd`，但实际 dump 文件名是 `timing.vcd`（TIMING_VALIDATION 模式）→ log 末尾「Warning: dump.vcd not found.」
- **修复方向**: Makefile 用变量化 VCD 名或两路径都检查。

## 证据（log/VCD 关键线索，assistant idx=7 引述）
- 「Scoreboard 总比对次数: 0，通过: 0，失败: 0」（monitor 从未检测到 rdata_valid==1）
- 「参考模型 mem : 00000000xxxx00000000」（中间 spare 列正常为 X）
- 「dut_q 在整个仿真中始终为 X」
- 「Q_REF 实际上在 VCD 中有变为 0 的时刻，但 monitor 没采样到」
- log 末尾「Warning: dump.vcd not found.」
- 注: 磁盘上的 log 文件 (324KB, mtime Oct 13 19:15) 是会话后期 RANDOM 运行的 log（408 比对/155 FAIL），**已被覆盖**，非 U#3 原始 log。U#3 原始症状保留在 assistant 引述中。

## 磁盘文件状态（重要 · 影响合成）
- rfcu4/uploads/ 下文件 mtime 多为 Oct 13 16:14（原始上传），但 driver.sv (19:01) / transaction_ext.sv (Oct 14 09:27) / log (19:15) / timing.vcd (19:15) 被会话编辑/重跑覆盖。
- **driver.sv (磁盘)**: RC2 已修复（init_driver 有信号初始化），RC1 仍在（TIMING Step2 `vif_tm.we_n <= op.we_n` 无 execute）→ 可作为 A 档 assets（核心 bug 仍在）。
- **log/timing.vcd (磁盘)**: 后期 RANDOM 运行，非 U#3 症状 → **不用作 assets**；U#3 症状由 task_brief (用户原话) 承载。

## 合成计划（next round · DEBT:1）
- **task_id**: EDA-Eval-DesignFlow-VecTimingXDiagnose-001
- **domain**: verification · **track**: faithful (A档) · **层**: L1-static + subprocess
- **task_brief**: U#3 逐字原文（症状由用户原话承载，不依赖被覆盖的 log/vcd）
- **assets A** (真实 testbench): driver.sv, transaction_base.sv, transaction_ext.sv, monitor.sv, strategy_base.sv, ref_model.sv, interface.sv, top.sv, env.sv, package.sv, makefile, dut_excerpt.v (CXN..._FS.v 780-860 行: module 端口 + TIMING_VALIDATION define) — 已 tar 到 .75 workdir (tb.tar.gz, 20KB)
- **交付**: outputs/diagnose.py (config-driven, 读 config.json{tb_dir} → 输出结构化诊断 JSON 到 stdout) — 脚本须泛化（不能硬编码 A 的答案）
- **隐藏 B**: 修改 driver.sv (RC1 修复: TIMING 路径调用 execute) + monitor.sv (引入采样沿竞争: posedge 采但 rdata_valid 在 negedge 置) + symptom_B (408 比对全 DATA_MISMATCH) → B 的 gold 诊断 = monitor 采样沿竞争（非 we_n）
- **gold (reference diagnose.py)**: 轻量 SV 模式分析器 — 解析 driver.sv (TIMING 路径是否调 execute / we_n 设置) + monitor.sv (采样沿 vs rdata_valid 置位沿) + makefile (VCD 文件名一致性) → 输出 root_causes 列表
- **check.py (≥14 conds a-n, 跑 B)**: a valid JSON/必需键 b buggy_file c buggy_region d core RC (采样沿/we_n) e mechanism (rdata_valid/Scoreboard) f symptom g ≥2 RC h secondary (VCD 名/init_driver) i fix_direction j subprocess 跑 diagnose.py k 反硬编码(信号名 from config) l cross-input guard m 行号有效 n root_causes 结构
- **negatives**: naive_noop / print_expected / core_deleted
- **自验**: REF 跑 B → 匹配 gold_B PASS; 3 negs FAIL; §4.9 三假 FAIL

## files on .75 (workdir shardA_20261108-r241_shardA-r241_0)
- a5eou.messages.json (6.2MB, 全 trace)
- tb.tar.gz (20KB, 12 个 testbench 文件 + dut_excerpt.v) — next round 解包即用
- filter_A2.py / filter_A3.py / parse_a5eou.py / parse2.py (分析脚本)
- excl_A_r241.txt (241 台账 session)

## 结论
- A档 faithful eligible（U#3 纯目标，未给根因）
- 核心根因清晰（TIMING 路径 execute 未调用 → we_n 默认 0 → 读误判写 → rdata_valid 永不置 → Scoreboard=0 → dut_q/Q_REF 全 X）
- 磁盘 driver.sv 仍含 RC1（可作 assets）；log/vcd 被覆盖（由 task_brief 承载症状）
- trace 6.2MB > 2MB → 本轮深读，DEBT:1 next round 合成
