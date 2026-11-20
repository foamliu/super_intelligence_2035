# trace_deepread: opm9y — lvs pre_sim schematic 修复

- **session**: 1792380407268_opm9y.messages.json
- **user/host**: willashi @ hfeg0plg15
- **mc**: 279 · **NMSGS**: 282 · **size**: 1.09MB
- **domain**: schematic_netlist (schematic 修复；schematic/spectre/netlist)
- **toolsKW**: 574 schematic · 147 cellview · 83 spectre · 39 netlist · 25 hspice · 22 calibre · 21 pyAether · 11 virtuoso · 9 skill
- **status**: 本轮 (#241) 深读 + parked(deepread)；**下轮第一件事合成 case**（DEBT:1）

## 用户轮逐字（A-faithful 候选任务说明 = U0）
- U0: 「目前窗口的schemetic报错，帮我修一下，指名报错原因」← 提需求/表达目标，未指出根因 → **可用作 A 档任务说明**
- U1: 「你来直接修一下」（要 agent 直接执行修复）
- U2: 「I_pre_0.IN 浮空输入 (Error) 看起来像是连起来的，为什么说没连起来」（追问浮空原因）
- U3: 「where to find analoglib」
- U4: 「'/apps/cdsmgr/CRB/IC617ISR23/tools.lnx86/dfII/etc/cdslib/analogLib' does not exist」
- U5: 「目前打开的schemetic帮我把IN OUT VDD GND补全」← 第二个清晰提需求轮（补全 4 pin）
- U6: 「Error* setq: too many arguments (2 expected, 4 given) - (insts (cv~>instances) nets (cv~>nets))」（agent SKILL bug 反馈）
- U7: 「*WARNING* (DB-270208): dbOpenCellViewByType: unrecognized viewType 'a' / *Error* return: return can only be used within a prog」

## agent 工具链 / 关键产物
1. **诊断阶段**：read CDS.log（多段）→ 发现 `lvs pre_sim schematic` Check&Save 报 **7 errors + 8 warnings (SCH-1172)**。
   - 涉及 cell：lib=`lvs` cell=`pre_sim` view=`schematic`（testbench 顶层，例化子模块 `I_pre_0` = `lvs pre`）
   - 错误清单：① I_pre_0.IN 浮空输入 ② PIN0(ipin) 浮空 ③ net5 浮空输入 ④ I_pre_0.VSS 接 global gnd!（应改 VSS net）⑤ I_pre_0.OUT 相关 short ⑥ 多个 warning
   - 读 cds.lib、sch.hist、pre/symbol 确认结构
2. **尝试真跑**：SandBox_MCP_Server__run_code（pyAether + SKILL）多次 → **沙盒服务不可用**（每次返回 connection 失败）
3. **降级：写 SKILL 修复脚本**（editor 写 `/home/willashi/fix_pre_sim_v3.il`，经 v1/v2 多次结构混乱后 v3 干净版）：
   - `procedure (fixPreSimSchematic @key (lib "lvs") (cell "pre_sim") (view "schematic"))`
   - `let` 局部变量：cv insts nets terms instPre pin0 pin1 inTerm inNet outTerm outNet vssTerm gndNet vssNet oldNetsToFix pin0Term pin1Term p1 p2 midPt
   - `(setq cv (dbOpenCellViewByType lib cell view "a"))` ← open for edit（viewType "a"）
   - 取 `instPre` = 例化 `pre` 的 instance；`pin0`=ipin PIN0, `pin1`=opin PIN1
   - **Fix 1**: 替换 I_pre_0.VSS 上的 global `gnd!` → 正确 VSS net（dbSetInstTermNet）
   - **Fix 2**: 删浮空 net5 的 dangling wires（foreach cv~>shapes ... dbDeleteObject）
   - **Fix 3**: 连 I_pre_0.IN ↔ PIN0(ipin)（dbSetInstTermNet inTerm pin0Net；schCreateWire 或 dbCreatePath）
   - **Fix 4**: 连 I_pre_0.OUT ↔ PIN1(opin)
   - 清理 orphaned nets（foreach oldNetsToFix dbDeleteObject）→ `dbSave cv`
   - 用 CIW `load("/home/willashi/fix_pre_sim_v3.il"); fixPreSimSchematic()` 执行
4. **附加**：clean_locks.sh 删 `*.cdslck*` 残留锁文件
5. **后续轮 (U5)**：补全 IN/OUT/VDD/GND 4 pin（schCreatePin / dbCreatePin）
6. **bug 教训**（U6/U7）：
   - `setq` 不能多赋值：`(setq insts (cv~>instances) nets (cv~>nets))` 非法 → 须拆成多个 setq 或用 let 绑定
   - `return` 只能在 `prog` 内（不能在 let/procedure 顶层）
   - `dbOpenCellViewByType` 第 4 参 viewType 应为 `"a"`（analog?）→ 实际应是 `"schematic"` 或省略；报 unrecognized viewType 'a' 说明用法错（正确：`dbOpenCellViewByType(lib cell view "a")` 中 "a"=mode for append? 实际 SKILL 签名 `dbOpenCellViewByType(lib cell view mode)` mode="r"/"a"/"w"）—— 这里 "a" 是 mode（append/edit），合法；U7 报错可能是别的原因，需复核

## 金标（trace 末尾用户实际接受的结果）
- 用户未明确 "接受/拒绝"，但 U2 起追问细节、U5 要求补全 pin → 隐含 v3 脚本诊断正确但需进一步补全 pin。
- **金标取**：v3 SKILL 修复脚本逻辑结构（Fix1-4 + dbSave + clean orphaned nets），**降级为生成 SKILL 脚本 + fix plan**（真实 Virtuoso GUI 执行非确定性 + 沙盒不可用 → L1-boundary config-driven 生成器）。
- 真实产物：`fix_pre_sim_v3.il`（SKILL procedure）+ 诊断错误清单。

## 合成计划（下轮）
- **case id**: EDA-Eval-DesignFlow-SchFixFloating-001（L1-boundary schematic_netlist）
- **A 档 prompt** = U0 逐字「目前窗口的schemetic报错，帮我修一下，指名报错原因」+ assets=config_A.json（描述 pre_sim testbench：lib/cell/view + I_pre_0 instance of pre + 错误清单：I_pre_0.IN 浮空 / PIN0 浮空 / net5 浮空 / VSS 接 gnd!）
- **hidden B** = config_B（不同 cell 名 / 不同浮空 net 组合 / 不同 global net 名，规模/取值不同）
- **reference**: gen_fix_sch_ref.py → 生成 SKILL fix 脚本（dbOpenCellViewByType "a" + let 局部绑定【**不用多赋值 setq**】+ Fix: 替换 global net / 删 dangling wires / 连浮空 instTerm↔pin / dbSave + 清 orphaned nets）+ fix_plan.json
- **check.py** 条件（≥8，目标 ~14-15）：a zip 含 gen b py_compile c 跑 B exit0 出 .il + plan d dbOpenCellViewByType+mode "a" e let 局部绑定（无多赋值 setq） f Fix 替换 global gnd→proper net g Fix 删 dangling wires h Fix 连 instTerm↔pin i dbSave j 清 orphaned nets k plan 错误数/B 的浮空 net 清单一致 l cellview/cell 名匹配 B m 跨输入护栏 A-only 不泄 + B-must 齐 n 非退化+3 跑 sha256 一致 o §4.9 三假全 FAIL 且≥3 独立条件
- **bug 教训**必须入 check：多赋值 setq 非法（e 条须确保 let 多个独立绑定，负样本用 `(setq a x b y)` → FAIL e）；return 须在 prog/let 内
- **negatives**：fake_empty / fake_print_fixed_A（硬编 A plan）/ fake_multi_setq（用多赋值 setq → 触发 e FAIL）/ naive_no_global_fix（缺 Fix1 → f FAIL）/ naive_no_orphan_cleanup（缺清 orphan → j FAIL）

## 教训
1. schematic 浮空修复 SKILL 是 schematic_netlist L1-boundary 可行范式（dbOpenCellViewByType mode "a" + let 独立绑定 + dbSetInstTermNet 连 instTerm↔pin + dbDeleteObject 删 dangling + dbSave）；真实 GUI 非确定性→降级生成脚本+plan
2. trace 关键 SKILL bug：`setq` 不可多赋值（须 let 多个独立绑定 或 多个 setq）；`return` 须在 prog 内
3. 沙盒不可用时 agent 降级写 CIW load 脚本是常见模式（v1/v2 多次 editor 插入致结构混乱→v3 整文件重写）
4. CDS.log 是诊断 schematic Check&Save 错误的入口（SCH-1172 错误码 + "floating input" 描述）
