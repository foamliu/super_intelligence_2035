# Deep-read: 1787728805982_txlfl — AutoVia/PowerFill cell removal (layout_virtuoso)

- **trace**: `1787728805982_txlfl` (e0014566 @ hfeg0plg58, mc=241, 317 msgs, 855KB, cline lead agent)
- **tools used**: run_commands×103, read_files×22, editor×35, RAG_search_apis×2
- **real task**: 在 `Library: auto_austin_case1, Cell: Array16G_T_rscalc` 的 layout 中，识别 autovia 和 powerfill 生成的 cell，并把这些 cell 去除。

## USER 轮
- **USER#1 (ts=1787728807797, 唯一意图轮)**：「请你识别到 Library: auto_austin_case1,  cell: Array16G_T_rscalc , 中 layout 的布局，识别出 autovia 和 powerfill 生成的cell, 并把这些 cell 去除。」← 纯意图/目标轮，A 档可用（但本 shard 走 B 档合成，与 r131/r132 一致）
- **USER#2 (ts=1787734179153, 指约束轮, 不作 A 档任务说明)**：「第三阶段：深层移除的那333个实例先不要移除。」← 给出约束（phase-3 deep-removal 333 个实例保留），属"已指出根因/给方案"轮。

## gold (agent 真实产物 + 用户接受)
**分类函数 `RL_IsAutoViaOrPowerFill(cellName)`**（case-sensitive，避免假阳性）：
- **autovia**：master cell name 含大写 `VIA`（如 `*_VIA`, `*_VIA_TOP`）。标准 via cell 用小写 `via`，**不匹配**。
- **powerfill**：master cell name 含 `_fill`(小写) / `improve` / `auto_pc` / `auto_pgdm` / `power_improve`。标准 filler cell 用大写 `FILL`，**不匹配**。

**识别出的 autovia cells**（agent 在 remove 脚本头注释中逐条记录）：
1. `zlib/Array16G_T_V4V3V2V1_20250716_vss_VIA` (inst I11, level 0)
2. `zlib/Array16G_T_20250711_VIA_TOP` (inst I10, level 0)
3. `zlib/Array16G_T_V4V3V2V1_20250716_vcc_VIA` (inst I12, level 0)
4. `zlib/Array16G_T_20250728_VIA_TOP` (inst I13, level 0)
5. `zlib/Array2G_Top_20250623_VIA_TOP` (inst I2 in Array2G_Top, level 1)
6. `zlib/ydec_Near_M5_RDL_rout_V4_*_VIA` (many insts in ydec_Near_M5_RDL_rout, level 1)
7. `zlib/ydec_Near_M5_RDL_rout_R_V4_*_VIA` (many insts in ydec_Near_M5_RDL_rout_R, level 1)

**识别出的 powerfill cells**：
8. `zlib/Ary16G_T_0708_mt2_fill_split` (inst I8, level 0)

**hierarchy 处理**：`RL_FindAllCellsWithAutoCells` 递归扫描任意深度 sub-cell，对每个含 autovia/powerfill inst 的 cell（top + nested）执行删除并 `dbSave`。

**phase-3 / 333 约束 (USER#2)**：第三阶段"深层移除"的 333 个实例**不删**。→ 即 ydec_Near_M5_RDL_rout_V4_*_VIA 等 level-1 深层 VIA 实例（共 333）属 phase-3 deep-removal，**保留**。最终移除集 = top-level autovia(I10/I11/I12/I13) + powerfill(I8) + level-1 Array2G_Top VIA(I2)；**不**含 333 个 deep VIA。

**Virtuoso 环境坑（真实）**：IC617ISR23，需手动构造 `LD_LIBRARY_PATH`（oa_v22.50.095/lib + tools.lnx86/lib/64bit + Qt/64bit/lib + dfII/lib/64bit + ...）+ `LD_PRELOAD=/home/e0025768/devops/bundle/lib-stdcxx/libstdc++.so.6`；`-nograph -nocdsinit -replay <cmd> -log <log>`；workdir 需 `cds.lib`。

## 失败模式（教学点）
1. **case 混淆**：把小写 `via_M2_M3`（标准 via）当 autovia 删了 / 把大写 `FILL_N28`（标准 filler）当 powerfill 删了 → 误删标准 cell。gold 严格要求 case-sensitive。
2. **忽略 phase 约束**：把 333 个 deep VIA 也删了 → 违 USER#2。gold 须按 phase tag 排除 phase-3。
3. **只扫 top level**：漏掉 level-1 nested Array2G_Top VIA / ydec 中的 VIA → 漏删。gold 递归。
4. **硬编码 A 的 lib/cell**：写死 `zlib` / `auto_austin_case1` → 跨输入（B 不同项目）穿。gold 须按 master name 模式分类，不依赖 lib 名。

## 合成方向（B 档）
单文件 Python `autovia_powerfill_remover.py`，CLI `<bundle.json>`/`--help`/无参 exit1。读 layout inventory bundle JSON（inst list: inst_name/lib/cell/level/phase），按上述 case-sensitive 规则分类 + phase-3 排除，输出 VERDICT/counts/removal_plan/ROOT_CAUSE/ACTION/CONFIDENCE，exit 0/2/1。隐藏 B（10 个嵌入 check.py 的 bundle，结构≠A，覆盖 clean/all-deep/standard-only/powerfill-variants/case-sensitivity/bad-bundle/nested/cross-input/edge）。L1-boundary（SUT 不跑 Virtuoso，离线分类）。
