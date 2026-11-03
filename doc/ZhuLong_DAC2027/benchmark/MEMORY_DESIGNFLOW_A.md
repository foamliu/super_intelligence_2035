WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: 轮52 合成 ✓（A-档试点第 10 条 = A-档试点 10/10 达成）。kqelc(hbpeng/hfeg0pkn005/mc130, eda_other) 上轮 parked→本轮合成。UI#6 逐字 `请基于pyaether开发一个脚本，找出一个topcell里用到所有pcell`（clean intent, 规则②不命中 → A-faithful ✓）。金标 = trace [73] 助手 find_pcells.py（import pyAether→aeGetCurDesign→design.block→block.getInsts()→dbCheckIsPCell(inst)→打印 pcell 实例表）。**fixture 方案 = mock pyAether 模块 + JSON instance-DB**（不依赖 live Aether）：grading-only mock_pyAether.py 实现 aeGetCurDesign/mdeGetCurrentLibCellView/dbCheckIsPCell/design.block/getInsts/inst.{name,libName,cellName,viewName}，从 PYAETHER_FIXTURE 加载实例库；候选 find_pcells.py 经 subprocess 在 mock+fixture 上执行（§4.2 L2 结构判分），mock 记录每个 dbCheckIsPCell 调用以验全实例覆盖。**A-档 faithful prompt**（UI#6 逐字原文）+ task_brief（3 行交付接口）。
- ✅ **本轮交付**：EDA-Eval-DesignFlow-FindPcells-001 合成 ✓（eda_other / L2 / A-faithful，A-档试点 10/10 收口）。交付件 = find_pcells.py（pyAether 脚本）。check.py **15 条断言 (a)-(o)**：(a)zip恰含find_pcells.py (b)py_compile (c)import pyAether (d)aeGetCurDesign (e).block (f)getInsts() (g)dbCheckIsPCell (h)A运行exit0+设计头mylib/TOP_INV/layout (i)A dbCheckIsPCell覆盖全6实例 (j)A stdout含每Pcell名(I0/I1/I3/I4)+master(n18/p18)且无inv_core/res_core (k)B运行exit0+设计头mylib/TOP_BUF/layout(泛化) (l)B覆盖全7实例 (m)B stdout含每Pcell名(I0/I2/I3/I5/I6)+master(nmos_hv/pmos_hv)且无buf_core/cap_core (n)防硬编码源码不含fixture字面量(TOP_INV/TOP_BUF/inv_core/res_core/buf_core/cap_core/n18/p18/nmos_hv/pmos_hv) (o)确定性3跑byte-identical。**cross-input B 设计**：A 的 pcell master=n18/p18，B 的 pcell master=nmos_hv/pmos_hv（不同），非-pcell master 也不同(inv_core/res_core vs buf_core/cap_core)→候选若硬编码 master 名/实例名必在 B 挂。自验：gold PASS 15/15；4 negative（fake_empty→(c) / fake_print_expected→(c) / fake_core_deleted→(g) / fake_naive_no_filter→(j)）全 FAIL（NEG_SELFTEST NEG_RC=0）；§4.9 (a)空壳(b)print期望(c)删核心三假覆盖。**k_rationale=15=k_check=15≥8 GATE PASS ✓**。test==disk check.py roundtrip OK，A jsonl 37→38 条，ledger covered 36→37, eda_other 6→7。
- 📊 trace 覆盖率：37/696 = 5.3% mc≥100（covered=37 · touched=57 · parked=20；A jsonl 38 条；eda_other 6→7）
- 🎯 通过率: cline+hook **13 unique cases** = 4 PASS / 13（样本<30 不报百分比；FindPcells-001 未跑 cline，下轮跑）。①+④=2/13=15.4% ≤30% ✓。
- 🧾 断言: FindPcells-001 k=15 达标（本轮已验）；38 条全达标
- 📦 体积：TASK≈23.8KB / MEMORY_A≈13.5KB（轮47/49/50 已归档至 MEMORY_A_archive.md）
- 🔒 泄漏隔离: FindPcells-001 资产仅 prompt+brief（0 判分器/答案/fixture/mock/B）；fixture_A/B+mock_pyAether+check.py+gold+negative 全在 reference/（不进 SUT 沙箱）；判分独立 /tmp，check 把 mock_pyAether 复制为 pyAether.py 放 PYTHONPATH；anti-hardcode (n) 双向守卫防 master/实例名硬编码。
- ⚠️ 运维令进度：**A 档试点 10/10 收口**（FindPcells-001=第10条 faithful）。**待办**：①FindPcells-001 cline 实跑（验通过率，A-档目标≤10%pass）；②PyShebangFix-001 cline 实跑；③CdlBodyMapFix-001 cline 实跑；④SiliconInstGen-001 cline 实跑；⑤CalibreOpen1Fix-001 cline 实跑；⑥DeadLoopScan-001 cline 实跑；⑦PDKRunsetExplore-001 cline 实跑；⑧STAFlow ④naming 决策；⑨TLEFRules ④(w) guard；⑩SPFCoupling-001 cline 实跑；⑪DRCDeckOpt ③泛化缺口修复；⑫A-档试点 10 条跑完→统计 A/B 分档通过率（日报加两行）。
- ✅ **本轮交付**：EDA-Eval-DesignFlow-PyShebangFix-001 合成 ✓（pnr_signoff / L2 / A-faithful）。trace wj4ab (kenwang/hfeg0pkn005/mc253)。**A-档 faithful prompt**（轮[0] 逐字原文：报 encodings fatal + 问按 .bashrc 调 Python 版本）。金标 = 真实 trace 助手 shebang 改写诊断。交付件 = fix_shebang.py（python stdlib，CLI `python3 fix_shebang.py <drc_auto_py> <bashrc> <output_py>`，regex 提 `module switch/load python/<ver>` + 识别硬编码绝对路径 shebang → 改写为 `#!/usr/bin/env python3`，正文逐行保留）+ diagnose.json（6 键 root_cause/shebang_before/shebang_after/module_python_version/env_vars_conflict/fix_summary）。check.py **15 条断言 (a)-(o)**，subprocess 在 A fixture(drc_auto_A.py+.bashrc_A) + 隐藏 B fixture(drc_auto_B.py shebang `/usr/bin/python3.6` + .bashrc_B `module switch python/3.8.10`，不同 shebang 路径/不同 module 版本) 上跑候选 fix_shebang.py（§4.2 L2 结构判分，不跑 calibre）。自验：ref PASS 15/15；4 negative（fake_empty→(a) / fake_print_expected→(n) / fake_core_deleted→(d) / naive_stub→(m)）全 FAIL（NEG_SELFTEST ALL-FAIL）；§4.9 (a)(b)(c) 三假覆盖。**k_rationale=15=k_check=15≥8 GATE PASS ✓**。test==disk check.py roundtrip OK，A jsonl 36→37 条。
- 📊 trace 覆盖率：36/696 = 5.2% mc≥100（covered=36 · touched=55 · parked=19；A jsonl 37 条；pnr_signoff 12→13）
- 🎯 通过率: cline+hook **13 unique cases** = 4 PASS / 13（样本<30 不报百分比；PyShebangFix-001 + CdlBodyMapFix-001 + SiliconInstGen-001 均未跑 cline，下轮跑）。①+④=2/13=15.4% ≤30% ✓。PASS=4(PTSignoff/InnovusLaunchDiag/FormalityLaunchDiag/DelPgLib)；③=5(SynLintFlow/DCCombHier/PwrGlobals/ETMExtract/DRCDeckOpt)；④=2(STAFlow/TLEFRules)；②=1(Verification)。
- 🧾 断言: PyShebangFix-001 k=15 达标（本轮已验）；37 条全达标
- 📦 体积：TASK≈23.8KB / MEMORY_A≈26KB
- 🔒 泄漏隔离: PyShebangFix-001 资产仅 prompt+brief+A fixture(drc_auto_A.py+.bashrc_A)（0 判分器/答案/隐藏/B）；hidden B (drc_auto_B.py+.bashrc_B，不同 shebang 路径/module 版本) 不进 SUT 沙箱；判分独立 /tmp，check.py+hidden 从 reference/ 复制；anti-hardcode (n) 双向守卫防 3.11.9//apps/local/bin/python3 + 防 3.8.10//usr/bin/python3.6 硬编码。
- ⚠️ 运维令进度：A 档试点 9/10（本轮 PyShebangFix-001 = A-faithful；pool mc≥300 shard-A-tool 枯竭 → 降阈 mc≥50 全 summary.tsv 扫 fresh 候选 → wb03t 偏模拟/wj4ab calibre+innovus 数字味 3MB(本轮采)/7ucl8 innovus+calibre 纯数字但 session 已轮转删除/kqelc 偏 eda_other）。**待办**：①PyShebangFix-001 cline 实跑（判分纯本地，验通过率）；②CdlBodyMapFix-001 cline 实跑；③SiliconInstGen-001 cline 实跑；④CalibreOpen1Fix-001 cline 实跑；⑤DeadLoopScan-001 cline 实跑；⑥PDKRunsetExplore-001 cline 实跑；⑦STAFlow ④naming 决策；⑧TLEFRules ④(w) guard；⑨SPFCoupling-001 cline 实跑；⑩A-档试点最后 1 条（mc≥30 续挖：b7y8t shaoyou pyAether+innovus / kqelc hbpeng cellview+dbopencv 偏 eda_other，或更低阈）；⑪DRCDeckOpt ③泛化缺口修复。


- 轮 48 SiliconInstGen-001（eda_other/L2/A-faithful，SiliconSmart .inst 生成）已归档 → ARCHIVE_OPERATOR_DESIGNFLOW.md「归档批次 49」；detail 见 daily_A_2026-11-03.md / jsonl 第35行 / reference/SiliconInstGen-001。

### 2026-11-03 shard A 轮 47 — 已归档（detail 见 daily_A_2026-11-03.md / MEMORY_A_archive.md）。

### 2026-11-03 shard A 轮 46：DeadLoopScan-001 合成 ✓（verification / L2 / A-faithful，SV bind 死循环静态排查）— 已归档（detail 见 daily_A_2026-11-03.md / jsonl 第33行 / reference/DeadLoopScan-001）；trace wl9i4(xingx/mc290)，金标 trace[751] 92 forever+4 while+2 do 死循环候选 L2719/L2727/L156/L612，check 20 断言 k=20，ref PASS 20/20，4 neg ALL-FAIL。
- ⬜ 待跑 cline。

### 2026-11-03 shard A 轮 45：PDKRunsetExplore-001 合成 ✓（eda_other / L2 / A-faithful，PDK runset 目录结构探索）— 已归档（detail 见 daily_A_2026-11-03.md / jsonl 第32行 / reference/PDKRunsetExplore-001）；trace s4xs4(xinqiaoz/mc283)，金标 trace[85] /apps/imctf/runset/calibre 37 平台探索，check 17 断言 k=17，ref PASS 17/17，4 neg ALL-FAIL。
- ⬜ 待跑 cline。


### 2026-11-03 shard A 轮 45：DRCDeckOpt-001 cline+hook 实跑 = FAIL ③（cross-input 泛化缺口）— 已归档（detail 见 daily_A_2026-11-03.md / status jsonl 第18行）；cline 1480s/exit0，A 侧 4 rule 全过，B 侧 0 rule 全挂 → ③ capability cross-input generalization，①+④=2/13=15.4% ≤30% ✓，run_one.sh list[str] attachments 双 bug 已修。
- ⬜ 待办：STAFlow ④naming / TLEFRules ④(w) / SPFCoupling cline / mc≥100 续挖。


### 2026-11-03 shard A 轮 49 — 已归档（detail 见 daily_A_2026-11-03.md / MEMORY_A_archive.md）。

### 2026-11-03 shard A 轮 50 — 已归档（detail 见 daily_A_2026-11-03.md / MEMORY_A_archive.md）。

### 2026-11-03 shard A 轮 52：FindPcells-001 合成 ✓（eda_other / L2 / A-faithful，pyAether pcell 枚举，A-档试点 10/10 收口，WAITING: 0）
- 任务卡本轮路径 = 合成 1 条新 case（上轮 todo「下轮第一件事：建 kqelc pcell fixture → 合成 A-faithful #10」）。
- kqelc 上轮 parked 原因 = live-Aether cellview fixture 不可在预算内建。本轮**改用 mock-pyAether 方案**绕开 live Aether：grading-only mock_pyAether.py 模拟 pyAether API 面（aeGetCurDesign/mdeGetCurrentLibCellView/dbCheckIsPCell/design.block/getInsts/inst 属性），从 JSON instance-DB fixture 加载实例；候选 find_pcells.py 经 subprocess 在 mock+fixture 上执行（§4.2 L2 结构判分，不依赖 live Aether/不跑 Aether 二进制）。
- **深读复核**：scp kqelc.messages.json（1473KB/316msgs）→ UI#6 逐字 `<user_input mode="act">请基于pyaether开发一个脚本，找出一个topcell里用到所有pcell</user_input>`（clean intent，规则②不命中 → A-faithful ✓）；金标 = trace [73] 助手 editor 写 /home/hbpeng/find_pcells.py（[77] 总结：aeGetCurDesign+mdeGetCurrentLibCellView→design.block→block.getInsts()→dbCheckIsPCell(inst=inst)→inst.name/libName/cellName/viewName→打印表）。
- **资产**：A = prompt.txt（UI#6 逐字原文 36B）+ task_brief.md（3 行交付接口：find_pcells.py，import pyAether→取当前设计→block→getInsts→dbCheckIsPCell→打印 pcell 表）。trace UI#6 无 attachments → assets 无文件输入。fixture/mock/check 全在 reference/（hidden）。
- **fixture**：fixture_A.json（mylib/TOP_INV/layout，6 insts：I0/I1/I3/I4 pcell master=reference_pdk/n18|p18，I2=inv_core/M0=res_core 非 pcell）；fixture_B.json（mylib/TOP_BUF/layout，7 insts：I0/I2/I3/I5/I6 pcell master=reference_pdk/nmos_hv|pmos_hv，I1=buf_core/I4=cap_core 非 pcell）。A/B 的 pcell master 名**不同**（n18/p18 vs nmos_hv/pmos_hv）+ 非-pcell master 名不同 → 防候选硬编码 master 名/实例名。
- **mock_pyAether.py**：aeGetCurDesign→_Design(lib,cell,view,insts)；design.block→_Block.getInsts()→list[_Inst]；dbCheckIsPCell(inst=)→inst._is_pcell + 记录调用到 PYAETHER_CALL_LOG（验全实例覆盖）；stub emyInitAether/emyCdbaNS/emyString/emyDesignGetName 兼容 gold fallback 路径。
- **交付件 = find_pcells.py**（gold = gold_find_pcells.py，faithful 复刻 trace [73] API 链 + 中文表输出）。
- **check.py 15 条断言(a)-(o)** 见 MEMORY 顶部。**k_rationale=15=k_check=15≥8 GATE PASS ✓**。
- **自验**：gold 在 mock+fixture_A → stdout 含 `当前设计: mylib/TOP_INV/layout` + `总共扫描了 6 个实例` + `Pcell 实例: 4 个` + 表 I0/I1/I3/I4(n18/p18) 无 inv_core/res_core；dbCheckIsPCell 覆盖全 6。在 fixture_B → 7 实例 + 5 pcell(I0/I2/I3/I5/I6, nmos_hv/pmos_hv) 无 buf_core/cap_core；覆盖全 7。reference_submit.zip → check() **PASS 15/15**。4 negative（fake_empty→(c) / fake_print_expected→(c)硬编码无API / fake_core_deleted→(g)无dbCheckIsPCell / fake_naive_no_filter→(j)非pcell master泄露）**全 FAIL**，NEG_SELFTEST NEG_RC=0。§4.9 (a)空壳(b)print期望(c)删核心三假覆盖。test==disk check.py roundtrip OK。
- **难度评估**：L2（subprocess 在 mock+fixture 上跑候选 find_pcells.py，§4.2 结构判分；live Aether 二进制不参与）。A-faithful 真实难度 = 模型须从一句中文需求写出正确 pyAether API 链（aeGetCurDesign→block→getInsts→dbCheckIsPCell 逐实例判定→打印表），且**不能硬编码 master/实例名**（B 用不同 master 名+不同 pcell 实例集，硬编码必挂）。预期 ≤10% pass（A-档目标）。
- **防泄题**：资产仅 prompt+brief（0 判分器/答案/fixture/mock/B）；fixture_A/B+mock+check+gold+negative 全在 reference/（不进 SUT 沙箱）；判分独立 /tmp，check 把 mock_pyAether 复制为 pyAether.py 放 PYTHONPATH；anti-hardcode (n) 守卫 10 个 fixture 字面量。
- 落库：追加 EDA-Eval-DesignFlow_A.jsonl 第 38 行（task_id=FindPcells-001, domain=eda_other, track=faithful, level=L2, harness=cline）。台账 mark case → covered 36→37, eda_other 6→7。assets(prompt+brief) + reference(check.py+mock_pyAether.py+fixture_A/B.json+gold_find_pcells.py+reference_submit.zip+negative/4+negative_selftest.py) 落 EDA-Flow-Bench 仓。
- ⬜ 下轮：①FindPcells-001 cline 实跑（验 A-档≤10%pass）；②PyShebangFix-001 cline 实跑；③CdlBodyMapFix-001 cline 实跑；④SiliconInstGen-001 cline 实跑；⑤CalibreOpen1Fix-001 cline 实跑；⑥DeadLoopScan-001 cline 实跑；⑦PDKRunsetExplore-001 cline 实跑；⑧STAFlow ④naming；⑨TLEFRules ④(w)；⑩SPFCoupling-001 cline；⑪DRCDeckOpt ③缺口修复；⑫A-档试点 10 条 cline 跑完→A/B 分档通过率统计（日报加两行）。
