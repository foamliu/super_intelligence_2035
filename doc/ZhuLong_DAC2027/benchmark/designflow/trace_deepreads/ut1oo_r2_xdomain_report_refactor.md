# deepread: ut1oo — R2 cross-domain direct-drive report refactor (sim-sp-gen skill)

**session**: 1794215806676_ut1oo.messages.json
**user**: tongni @ hfeg0pkn004 (10.129.2.13)
**mc**: 89 (summary_1115_081559.tsv); B-ledger had 285 from older scan
**keywords**: netlist:349; schematic:76; hspice:48; .def:18; analog:12; mosfet:9; rtl:1
**trace size**: 696575 B / 116 msgs
**fetch**: eda_flow open_session + ssh .75(hfhds201)→10.129.2.13 cat /home/tongni/.cline/data/sessions/1794215806676_ut1oo/1794215806676_ut1oo.messages.json

## domain verdict: **D (schematic_netlist)** ✓

- hspice:48 keyword 触发 D-filter exclude（A r749 SHARD_EXCLUDE D: hspice|finesim|...），ledger domain=spice_sim → B-parked。
- 但 trace 实际工作 = **R1-R4 网表结构静态检查**（`run_netlist_checks.py` on VtscRef testbench netlist）+ **skill 脚本修改**（r1r2_report.py / r4_spare_report.py）。hspice kw 来自 sim-sp-gen skill 名（simulation-spice-gen）与 SPICE 注释，非真跑 hspice 仿真。
- B-ledger note 自标 "wrong-shard(D/schematic_netlist)" — B 已识别为 D 域，parked 等 D revival。**D-domain fit 确认**。

## 用户真实意图（按 msg 分轮）

- **U#0 (msg 0)**: 加载 sim-sp-gen skill，给一个 testbench 原理图 netlist，要求跑 R1-R4 检查产出报告。assistant 用 `run_netlist_checks.py` 跑 → 报告落 `/home/tongni/zmh_AI_VtscRef_standard_tb_sim_schematic_r1r2r3r4_report.txt`。
- **U#1 (msg 15)**: 加载 skill-creator，要求把「电平移位器（level shifter）」纳入 R2 跨域检查（护盾：挂 levelshft 的跨域 net 判正常）+ R4 Spare 检查（spare 也要含 levelshft 备份）。assistant 编辑 r1r2_report.py + r4_spare_report.py，加 `is_level_shifter()` + `_collect_leaves()` 层级作用域，验证 disjoint，同步 skill/workspace。
- **U#2 (msg 70)**: 用户指出 R2 **扁平误并** bug（同 name `net<N>` 跨子电路被盲目合并 → 假阳性跨域驱动）。assistant 重写 R2 为**层级作用域感知**（net 以 `(scope_path, name)` 为键，从 Top 递归下探）。验证：两张直接驱动表清空（No ... found）。
- **U#3 (msg 88)** — **本 case 选用轮**: 「/skills 不用列cross-dmain net 在报告中 只要给出存在直接驱动风险的」。要求 R2 报告**不再列出跨域 net**（含 [Level-Shifter Converted (Normal)] 清单），**只输出存在直接驱动风险的 net**。assistant 编辑 r1r2_report.py 移除 `shifted` 列表与 [Level-Shifter Converted (Normal)] 段，只保留 [Low->High] 与 [High->Low] 两张直接驱动风险表。同步 SKILL.md。
- **U#4 (msg 110)**: 最终核对确认所有改动落在 sim-sp-gen skill。assistant 跑 `_verify_skill_sync.py` 确认 r1r2_report.py / r4_spare_report.py / SKILL.md skill/workspace 一致且编译通过。

## 选用 U#3 (msg 88) 为 A档 trace-faithful case 的理由

- 用户轮分类：「提出需求 / 表达目标」✓（要求改报告格式，非指出根因或给修复方案）→ 符 A档选轮规则 ②。
- 任务自洽：附 r1r2_report_A.py（修改前状态，含 [Level-Shifter Converted (Normal)] 段 + 层级作用域 + LS 护盾）作 asset A，agent 读脚本理解当前 R2 逻辑后按用户原话移除跨域 net 列出。无需前序轮次状态。
- 判分有牙：check() 跑隐藏 B/B2 netlist 校验 (1) 跨域 net 段确实移除 (2) 直接驱动风险 net 正确检出 (3) 层级作用域保持 (4) 反硬编码 B2 (5) cross-input guard (6) 3 退化提交全 FAIL。15 独立条件 a-o。
- D-domain 纯：netlist 结构检查 + skill 脚本修改，schematic_netlist ✓。

## 资产

- **A (asset)**: `r1r2_report_A.py` — 修改前 skill 脚本（含 R1/R2/R3/R4，R2 有 [Level-Shifter Converted (Normal)] 段 + 层级作用域 + LS 护盾）。合成重建（保留真实结构签名：get_domain/is_level_shifter/parse_netlist 层级作用域/r2_check 三表/r1_check/r3_check/r4_check），非逐字拷贝（trace 中脚本在 .75 远端，本 case 用合成平行实现保结构签名）。
- **reference**: `r1r2_report.py` — A 移除 [Level-Shifter Converted (Normal)] 段 + `shifted` 列表，只保留两张直接驱动风险表。
- **hidden B (B.sp)**: 2 子电路 ModA/ModB 同名 sig5（层级作用域测试）+ 3 LS 护盾 net (lsout1/2/3) + 2 直接驱动风险 net (riskLH Low->High, riskHL High->Low)。
- **hidden B2 (B2.sp)**: robustness — 2 子电路 CellX/CellY 同名 data0 + 2 LS 护盾 net (lso1/lso2) + 1 Low->High 风险 (dLH) + 0 High->Low。反硬编码 B1。
- **hidden B3**: 不存在文件路径 → exit 0 优雅。

## 自验

- reference_submit.zip 跑 check.py: **15/15 PASS** ✓
- negative_selftest: 3 neg (空壳/只print硬编码/删核心) **全 FAIL** (distinct conds: d/k/i) ✓
- 🧾 断言: k_rationale=k_check=15 ✓（≥8 硬闸门过）
