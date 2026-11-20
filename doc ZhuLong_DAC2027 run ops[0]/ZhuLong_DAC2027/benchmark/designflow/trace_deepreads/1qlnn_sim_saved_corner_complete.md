# Deepread — 1qlnn (ynbai @ hfhds201) — sim.saved.total PVT corner 补全

- **session**: `1794018867939_1qlnn.messages.json` (ynbai @ hfhds201, 39 msgs / 328KB)
- **fresh**: 写于 2026-11-07 10:56 (mtime epoch 1794019014)，本轮(11:06)在 hfhds201 本机 fresh-since-10:30 扫描中浮现的**唯一**新 session
- **trace 真实度**: ✅ 真实 cline trace（.75 本机 /home/ynbai/.cline/data/sessions/），非合成
- **domain**: characterization（PVT corner 补全：FF/TT/SS × V×T 5 corner 覆盖）

## 用户原话（逐字，A-档任务说明）

**USER#0**（纯需求轮，给目标 + 方法 + 输出位置，未给根因/修复 ✅）:
> 识别/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL下的sim.saved.total文件，文件为仿真输入文件，内容例如[5 行 case+corner 路径：Golden005_..._3600_FF.X4 FF1.3v110C X4 / _FF.X4 FF1.3v-40C X4 / _TT.X4 TT0.94v25C X4 / _SS.X4 SS0.94v110C X4 / _SS.X4 SS0.94v-40C X4] 为仿真case Golden005_..._3600的5个corner的输入，每一个case应该都有5个，但是文件不全，部分不是五个，帮忙补全，补全文件生成为sim.saved.total.zl，相同corner不同电压温度下前方相同，例如/proj/.../vec_golden/3600

**USER#1**（细化输出）:
> 多出来的case行输出到sim.saved.total.zl.more中

## 5 个 PVT corner（金标准结构）

| corner tag | path suffix | 备注 |
|:--|:--|--:|
| FF1.3v110C | _FF.X4 | FF 高温 |
| FF1.3v-40C | _FF.X4 | FF 低温（同 _FF.X4 路径，不同 V/T tag）|
| TT0.94v25C | _TT.X4 | TT 典型 |
| SS0.94v110C | _SS.X4 | SS 高温 |
| SS0.94v-40C | _SS.X4 | SS 低温（同 _SS.X4 路径）|

每行格式：`<base_path>_<FF|TT|SS>.X<4|8> <PVT_TAG> X<4|8>`（3 个空白分隔 token）。
base_path = 去掉末尾 `_FF|_TT|_SS.Xn` 后缀；同一 case 的行**连续**排列。

## trace assistant 工具链

read_files×11（读 sim.saved.total 分段 1-50/50-100/100-200/200-300/10300-10397 + 读产出的 .zl/.zl.more 校验）→ editor×2（写 fix_sim_saved.py 生成 .zl = 原始+补全；写 extract_more.py 仅输出补充行到 .zl.more）→ run_approved_command×4（python-runner 跑脚本）→ run_commands×1（wc -l）。

## 金标准（trace 末尾用户接受的真实产物）

- **extract_more.py 逻辑**（trace msg 29 editor new_text 完整捕获）：
  1. 正则 `^(\S+) (\S+) (X\d+)$` 匹配每行
  2. `(_FF|_TT|_SS)(\.X[48])$` 定位 case 后缀，base_path = 前缀
  3. 连续同 base_path 行组成 block，收集 corners_seen（PVT tag 集合）+ path_suffixes（每类型 corner 的实际后缀）
  4. missing = expected_corners 中不在 corners_seen 的；对每个 missing，用同类型 path_suffix（若无则用该 case 的 ext 构造 _FF/_TT/_SS.Xn）
  5. 仅把 missing 行追加到 .zl.more
- **真实结果**：`run_approved_command` stdout = "Added lines written to: .../sim.saved.total.zl.more\nTotal added lines: **244**"（122 case × 每个缺 2 corner）
- **真实 /proj/drvqa 文件**：Permission denied（t0002965 无权读 ynbai 的项目文件）→ 金标准从 trace 的 editor new_text + run stdout 重建，无需读真实文件

## case 合成决策

- **A-档 faithful**：任务说明 = USER#0 + USER#1 逐字原文；task_brief 仅写交付接口（≤3 行），不写"要做什么"
- **资产 A**（可见）：合成 sim.saved.total，复刻真实结构（长 Golden 路径 + 5 PVT corner + 部分 case 缺 corner），4 个 case（A1 完整 / A2 缺 TT+SS-40 / A3 缺 FF-40 / A4 完整）→ 3 行补充
- **隐藏 B**（判分用，不进 SUT 沙箱）：6 个 case（ProbeA-F，含 X8 宽度变体 ProbeF），缺 corner 模式与 A 不同 → 7 行补充
- **A≠B**：路径（Golden vs Probe）/ 行数（3 vs 7）/ 宽度（A 全 X4 vs B 含 X8）均不同 ✓ → 防硬编码（cond q）
- **reference** = sim_saved_corner_complete_ref.py（便携 Python，trace extract_more.py 逻辑泛化为 `<input> <output>` 双参）
- **check.py**：17 条断言 a-q，内嵌 B_LINES/A_LINES（隐藏 B 不在 SUT 沙箱）
- **L1**：离线 Python 文件处理，无 EDA tool run

## 自验

- ref 跑 B → 7 行 == B_EXPECTED ✓
- ref 跑 A → 3 行 == A_EXPECTED ✓
- check.py vs reference_submit.zip → True（PASS）✓
- negative_selftest：5 stub（empty/print_expected/hardcode_B/wrong_count/dup_existing）全 FAIL ✓
- §4.9 trio（空壳 / 只 print / ref 删核心）全 FAIL ✓
- 断言闸门：k_rationale == k_check == 17 ≥ 8 ✓

## trace_source

`{user: ynbai, host: hfhds201, session_file: 1794018867939_1qlnn.messages.json, match_count: 2736, real_task_summary: ...}`
