# dek1i — TempHalfWL 网表优化 + 对比报告 (schematic_netlist)

- **trace**: session 1793001881089_dek1i.messages.json, user easont, host hfhds207, mc=590
- **tools**: 1921 netlist / 575 schematic / 445 analog / 418 cmos / 334 waveview / 38 aether / 33 hspice (SpiceAgent/cosim)
- **msgs**: 393 msgs / 10 substantive user turns (agent=lead)

## 用户意图弧（substantive turns）
- U[0] 读 /proj/ddgoa/.../cosim/tt0.94v45c.vdd2h/finesim.fsdb
- U[17] 用 waveview-fsdb-readerV2-2 skill 读 fsdb，根据波形说明 signal 功能
- U[63] 读 cosim/netlist_AI 结合 fsdb 分析，说明模块功能
- U[97] 分析 netlist 是否最简，直接输出优化后 netlist 到 cosim 命名 netlist_pro
- U[204] fsdb 波形有问题，自己分析后迭代 netlist
- U[234] 结构参考 netlist_AI，你生成的都是错的
- U[278] 理解网表，分析可优化点，直接在 netlist 上修改
- U[383] **对比修改后的网表和原先的网表，生成 markdown 形式的报告** ← 本 case 选料
- U[392] 分析 cosim 文件夹，说明整体仿真流程

## 助手工具链
list_allowed_files → read_files(cosim.sv/svh, netlist_AI, finesim.vcd) → skills(waveview-fsdb-readerV2-2) → run_approved_command(bsub wv_queue 跑 sx_export_data 导 .tbl) → editor 写 netlist_pro / write_netlist_pro*.py / fix_netlist_pro_v*.py / optimize_netlist.py / final_clean*.py 多轮迭代 → editor compare_nl.py 生成对比报告。

## 真实产物（金标准）
- **netlist_AI**（原始，802 行）: 37 个子电路定义（switch_close/switch_open/inv/bufLx4/invLx4/nand3/nand3Lx2/xnord2/xnor2Lx1/nand2/nand2Lx2/nor3/nor3Lx1/nand3Lx1/nor2/nor2Lx1/invLx1/nand2Lx1/nand4/nand4Lx1/or2Lx1/invhiz/dlyg2s2_gut2/dlyg2s2_gut1/dlyg0of8s2_ut/dlyg2of8s2/or3Lx1/oai21/oai21Lx1/aoi21/aoi21Lx1/nand4Lx2/inv_org/invhiz_org/dlyg2s2_gut2_org/dlyg2s2_gut1_org/gfilt）+ 顶层 TempHalfWL（XI187<0..7> Temp→TempN buffer 阵列 + XI_selN26_* 主使能 nand2Lx1/invLx1 链 + XIcmp_10xx sel28/sel50 比较器链 + XIgfilt_sel50/54 gfilt 滤波 + XIxnor_sel62 + XI_switch_CS1/CS2 switch_close）。
- **netlist_pro_clean**（优化后，431 行）: 15 个子电路（inv/bufLx4/invLx4/nand3/nand3Lx2/xnord2/xnor2Lx1/nand2/nor2/nor2Lx1/invLx1/nand2Lx1/inv_org/invhiz_org/gfilt）+ 同 TempHalfWL 顶层（去掉 XI_switch_CS1/CS2）。
- 文件头注释写 "Removed 18 unused cell definitions" 但**真实结构差是 22**（手动注释不准 → 本 case 的判分陷阱）。
- **结构差真值**：removed=22, preserved=15, added=0；顶层实例 34→32（删 2 个 XI_switch_CS*）。

## 大小写陷阱（关键）
真实 netlist_AI 用小写 `.subckt` 定义 7 个 cell（switch_close/switch_open/inv_org/invhiz_org/dlyg2s2_gut2_org/dlyg2s2_gut1_org/gfilt），其余 30 个用大写 `.SUBCKT`；netlist_pro_clean 用小写 3 个（inv_org/invhiz_org/gfilt）+ 大写 12 个。case-sensitive grep 会漏算 → naive_grep_only negative 的攻击点。

## 合成的 case
**EDA-Eval-DesignFlow-NetlistCmp-001**（B 档，L1 离线 Python 网表结构差）：
- 候选写 netlist_compare.py（CLI: orig mod out.md）解析两 HSPICE 网表 → markdown 对比报告（removed/preserved/added 子电路名 + 计数 + 顶层 TempHalfWL + selN26/gfilt/bufLx4/xnor2Lx1 不变量）
- assets A: netlist_AI（466 行，37 子电路，结构保真由 gen_netlists.py 从真实 trace 派生）+ netlist_pro_clean（232 行，15 子电路）+ task_brief + prompt + example_output_A
- hidden B: B_original(9 子电路)/B_modified(6 子电路) removed=4/preserved=5/added=1，结构完全不同于 A（杀 A 硬编码）
- check.py 15 条件 a–o：zip/compile/markdown/top名/removed=22(非18)/preserved=15/added=0/列≥5被删名/列≥5保留名/不抄袭18头/gfilt+bufLx4+xnor2Lx1保留/selN26逻辑块保留/重跑A removed=22/跨输入B 4-5-1+newB/重跑A列≥10被删名
- 5 negatives 全 FAIL(NEG_RC=0)，distinct labels c/e/h/j/n；§4.9 三假(空壳/print期望/删核心)全 FAIL ✓
- k_rationale=k_check=15≥8 GATE PASS
