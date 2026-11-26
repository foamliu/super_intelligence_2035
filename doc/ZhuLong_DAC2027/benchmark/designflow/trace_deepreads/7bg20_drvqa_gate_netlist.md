# Deepread: 1790650962650_7bg20 (fxian @ hfeg0pkn002, 10.129.2.11)

- **mc=131** (digital: synthesis=24 + netlist/schematic mixed), **190 msgs**, session file `/home/fxian/.cline/data/sessions/1790650962650_7bg20/1790650962650_7bg20.messages.json` (1.2MB, reachable, scp'd to .75 workdir)
- **domain**: digital (RTL → DRVQA stdcell-style gate netlist, Aether-schemable)
- **A档②**: ✓合格 (user#3 clean 提需求 "base on DRVQA db stdcell & environment, create circuit"; user#4/#5 refine "用 DRVQA stdcell 搭建电路, Aether 可查看"). 未给根因/修复 → A档 faithful.
- **真实资产可达性**: input RTL `addr_to_rowcol_v5.v` (58L, scp'd ✓) + gold netlist `R_BADEC_ADDR2ROWCOL_DRVQA.v` (279L, scp'd ✓) 可达; DRVQA 风格参考 `R_BADEC_R02.v` permission-denied (但风格可从 gold netlist 自提取: specify/CDS_LIBNAME/nand-nor-not/assign/_I_/#0.05); DRVQA cell 库 `drgqa_test.csv` 未取(非必需,判分纯静态).
- **A档⑥(真实资产可达)**: 部分可达 → 可走 A档 faithful 用真实 RTL + 合成 B 隐藏 RTL; 或纯 B档 synthesized. **建议 B档 synthesized**(金标准=agent 产物,非预存文件;且需异构 B 击破硬编).

## 会话流(逐轮)
- **user#0** "who are you" (greeting)
- **user#1** 逐字粘贴 RTL `addr_to_rowcol_v5.v`: 9-bit N(0..295)→(row[3:0],col[4:0],valid), 4 区域 R0(0..79)/R1(80..159)/R2(160..219,÷3 用并行逐位比较+小真值表 mod3)/R3(220..295), 纯组合 always@(*), 关键路径优化无乘除模. (隐含: 分析/优化)
- agent: 写 `sim_addr_to_rowcol.py` (python 全输入仿真), 产 `addr_to_rowcol_v5_areaopt.v` (R2 ÷3 改级联减法, 面积优化)
- **user#2** "3" (短确认)
- **user#3** 逐字 "base on DRVQA db stdcell & enviroment, create circuit" ← **clean 提需求**
- agent: 探 `/home/fxian/python/delay_optimizer/{drgqa_test.csv,cell_library.py,chain_config.py,reporter.py}` + `/home/fxian/verilog/{R_BADEC_R02.v,addr_to_rowcol_v3.v,addr_to_rowcol_compress.v,R_RH_CALCUTLATE.v,TOP_R_BADEC_R02_10G3.v,R_URADS...}` → 懂 DRVQA 风格; 写 `R_BADEC_ADDR2ROWCOL.v` (gate nand/nor/not + RTL 减法/比较, DRVQA specify)
- **user#4** 逐字 "我可以用华大的电路编辑软件（Aether）查看你生成的电路原理图么"
- agent: 查 pyAether API (`aeGenSymbolAndSchematicByVerilog`, `aeGenerateSchematicFromVerilog`, `aeCompileVerilogView`), 给 Aether CIWindow 用法 (emyInitAether + aeGenSymbolAndSchematicByVerilog(libName,cellName,verilogFile))
- **user#5** 逐字 "请继续生成原理图，我现在打开的是DRVQA的电路环境，希望看到你调用的也是DRVQA的stdcell 搭建了这个电路" ← 强调纯 DRVQA stdcell
- agent: 重写 `R_BADEC_ADDR2ROWCOL_DRVQA.v` (msg 155-189, 多轮 editor 拼装, 最终 279L) — **金标准**
- 用户接受 (会话末, 无进一步修正)

## 金标准: R_BADEC_ADDR2ROWCOL_DRVQA.v (279L, 已 scp 到 .75 workdir)
**DRVQA 风格约定** (从 gold 提取):
- 头注释: `// Verilog HDL and netlist of DRVQA <cell> schematic` + 功能描述 + `timescale 1ns / 10ps`
- module 声明: `module <name> ( row, col, valid, N );` (输出在前, 输入在后 — Cadence schematic 风格)
- **specify 块**: `specparam CDS_LIBNAME = "DRVQA"; specparam CDS_CELLNAME = "<name>"; specparam CDS_VIEWNAME = "schematic"; endspecify`
- **门原语**: `nand #(0.05)`, `nor #(0.05)`, `not #(0.05)`, `and #(0.05)` (实例名 `_I_<tag>`, 延迟统一 #0.05)
- **RTL 级**: `assign` 用于减法/比较/移位 (Aether 综合, 非纯门级) — gold 含 28 assign + 81 nand + 45 not + 4 nor + 1 and
- 结构: 区域检测树(le79/le159/le219/region_R0..R3) + 每 region 计算 r{0..3}_row/r{0..3}_col + 输出 MUX (4:1 nand-nor 选择 per bit, _I_mc<x>f)
- valid: N<=295 门级比较器

## 合成计划 (下一轮执行, DEBT 清零)
**verb = `rtl-to-drvqa-style-netlist-gen`** (组合 RTL → DRVQA stdcell 风格 Verilog 网表, Aether 可生成原理图). 与所有已有 shard-A verb 互斥:
- HierDcSynth=DC synth.tcl; DcDontuseGen=lib→dont_use tcl; CombSdcGen=RTL→SDC; StaFlowScaffold=STA flow 目录; AutoCellTclFlow=AutoCell 8-TCL; ConnFileNetChk=si.inp perl; PortCatch=CDL 端口; FlatNet, AprStampFix, AprSetupAudit, AprLogAudit, VcsEquiv, VcsMakefile, ItfCompare, CalibrePdf2md — 均不同工具/不同产物. ✓互斥.

**交付 = submit.zip{gen_drvqa_netlist.py + R_BADEC_ADDR2ROWCOL_A.v}**
- `gen_drvqa_netlist.py`: 通用生成器, CLI `--spec <spec.json> --rtl <in.v> -o <out.v>`, 纯 stdlib. 读 JSON spec(top name, port 宽度, 区域定义列表[bound,row_formula,col_formula,mode=gate|rtl], libname="DRVQA") + RTL(参考) → emit DRVQA 风格网表: 头注释 + timescale + module(输出在前) + specify{CDS_LIBNAME/CDS_CELLNAME/CDS_VIEWNAME} + 区域检测比较器树(nand/not 门级) + 每 region 计算(gate mode=nand/nor/not 门级; rtl mode=assign 减法/比较/移位) + 输出 4:1 MUX(nand per bit) + valid + endmodule. 实例名 `_I_<tag>`, #0.05.

**A 可见 bundle** (B档 synthesized faithful):
- `addr_to_rowcol_A.v` (= 真实 addr_to_rowcol_v5.v, 58L, 已取) — 4 区域 R0..R3, 9-bit N→row/col
- `spec_A.json`: top="R_BADEC_ADDR2ROWCOL", libname="DRVQA", 4 区域(0..79/80..159/160..219/220..295, R2 mode=gate 级联减法 ÷3, 余 rtl)

**B 隐藏 bundle** (异构 cross-input guard, 击破硬编 A):
- `addr_decode_B.v` (合成异构): 不同 module 名/端口 (e.g. 8-bit A(0..200)→(bank[2:0],idx[5:0]), 3 区域, 不同边界, 不同 ÷ 逻辑)
- `spec_B.json`: top="R_XDEC", libname="DRVQA", 3 区域, 不同 mode 分布
- 5 维全异: top 名 / 端口名宽度 / 区域数边界 / mode 分布 / MUX 选 3:1 vs 4:1

**判分纯 stdlib python3** (无 Aether/VCS license, 静态结构 + python sim oracle):
check.py **≥15 条 a-o** 独立断言:
- a) zip 含 2 文件 (gen_drvqa_netlist.py + .v)
- b) py_compile gen_drvqa_netlist.py
- c) 候选跑 A exit0 + 产 .v
- d) A .v 含 `specify` + `CDS_LIBNAME = "DRVQA"` + `CDS_CELLNAME = "R_BADEC_ADDR2ROWCOL"` + `CDS_VIEWNAME = "schematic"`
- e) A .v module 声明含 row/col/valid/N 端口
- f) A .v 仅用允许原语 (nand/nor/not/and/assign/wire, 无乘除模 `*` `/` `%` 在 assign 外, 无 always)
- g) A .v 实例名匹配 `_I_<tag>` 命名 + #(0.05) 延迟
- h) A .v 含 4 区域信号 region_R0..R3 + 比较器 le79/le159/le219
- i) A .v 含 输出 MUX (col_t<x>_<r> + nand 聚合 per bit)
- j) **行为 oracle**: 独立 python 解析 A .v 的 assign + 门 → 在 296 输入上仿真 → (row,col,valid) == 独立 oracle(addr_to_rowcol_v5 真实行为) 全 296 case (容差: valid 在 N>295 为 0)
- k) 候选跑 B exit0 + 产 .v
- l) 跨输入守卫 B .v CDS_CELLNAME == "R_XDEC" ≠ A
- m) 跨输入守卫 B .v 含 B 端口名(bank/idx) 不含 A 端口名(row/col)
- n) 跨输入守卫 B .v 区域数 3 (region_R0..R2) ≠ A 4
- o) 反硬编 gen_drvqa_netlist.py 源码不含 A/B 专有字面量 (R_BADEC_ADDR2ROWCOL / R_XDEC / addr_to_rowcol / addr_decode)
- (p) 随机化 3 seed 跑 A, 输出字节一致 (确定性)

**negatives** (≥5, 全 FAIL):
- fake_empty → a
- fake_print_expected (硬编 A .v 字面量打印) → o (源码含 A 字面量) 或 l (B 不符)
- fake_core_deleted (无 specify/CDS_LIBNAME) → d
- naive_hardcode_a (硬编整个 A netlist, B 跑崩) → l/m/n
- naive_no_mux (缺输出 MUX) → i
- §4.9 (a)空壳 (b)只 print (c)参考解删 specify 块 → 全 FAIL

**本地自验**: ref 跑 check.py PASS 全 15+; 5 negatives 全 FAIL; §4.9 三假全 FAIL; NEG_RC=0.
**断言闸门**: k_rationale == k_check ≥ 8, 格式 `k 条断言：①…`.

## 关键设计点 (避坑)
- gold 非纯门级 (含 28 assign) — spec mode 字段控制 gate vs rtl, 生成器按 mode 分支, 判分 f 允许 assign (但禁 always/乘除模)
- 行为 oracle (j) 是反硬编核心: 候选若硬编 A 真值表但 B 跑不出 → j 在 B 上 FAIL (跨输入); 单纯结构断言不够, 需仿真
- A .v 行为必须匹配真实 addr_to_rowcol_v5 (user#1 RTL) — gold netlist 是 agent 产物, 需先验证 gold 自身行为正确 (若 gold 有 bug, 以真实 RTL 行为为准, gold 仅作风格参考)
- 真实 RTL addr_to_rowcol_v5.v 已 scp 到 .75 workdir (58L), 可直接用作 A 可见资产
- gold netlist R_BADEC_ADDR2ROWCOL_DRVQA.v (279L) 已 scp, 作风格/结构参考 (不直接入 submit.zip, 避免泄题)

## 台账
- 7bg20: claim → deepread (r57), covered 65 不变, digital 19 不变, **DEBT=1** (下一轮第一件事合成 DrvqaGateNetlist-001)
