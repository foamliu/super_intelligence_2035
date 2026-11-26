# Deep-read: 1789545001824_x0t2m — Latch/FF Netlist Matching (ethanw @ hfhds201)

- **trace**: ethanw @ hfhds201 (= .75 local), session `1789545001824_x0t2m.messages.json`, 183 msgs / 1.575 MB, mtime 1789548452 (2026-09-04ish)
- **shard**: B (spice_sim) — latch/FF matching for finesim netlist characterization
- **A-档判定**: CLEAN ✓ — USER#2 是「提出需求/表达目标」轮（给目标=创建匹配流程 + 输出格式 + latrq2_ckUnit 示例 + 规则 subckt,refname,signame,data,RN,SN,R,S + cm... 跳过 + 三行 lib/cell/subckt 信息），未给根因/修复。USER#0/#1 是寒暄（hi / can you chinese），非任务轮。
- **USER#0 原话**: "hi,Can you read which files are currently present in the current directory?"
- **USER#1 原话**: "can you chinese"
- **USER#2 原话（任务轮，A-档 prompt）**: "I want to create a matching process that uses the information in DDR6TOP_Latch_FF_RS.list to match the netlist. For example, (dscqa_digital latrq2_ckUnit corresponds to * Library : dscqa_digital * Cell : latrq2_ckUnit, and the library and cell need to be exactly matched) After matching, the netlist will be * Library : dscqa_digital / * Cell : latrq2_ckUnit / * View : schematic / * Inherited view list : hspiceD spice cmos_sch spicesim_ecc ... / .SUBCKT latrq2_ckUnit Clk0 Clk0N Clk1 Clk1N D0 D1 Q RN vbn! vbp! vcc! vss! ... .ENDS / Capture, arrange according to the rules: subckt, refname, signame, data, RN, SN, R, S / latrq2_ckUnit,Clk0,Clk0N,D0,RN,,, / latrq2_ckUnit, Clk1, Clk1N, D1, RN, ... / In the template, there are reference arrangements available. In case of conflicts, the one that is captured will prevail. / Note special cases: If a library cell from the Netlist is matched, the following will be captured. SUBCKT AG_SCmosCkeRstCtrl ... cm0_ts_FsPgm cm1_gc_DlyPDXRst<1> ... / If "cm..." appears, it can be considered invalid and will not be processed. / (A file containing the matched output will be generated for viewing. There will be three lines of "lib cell subckt" information). Arrange the output (in a format similar to that of the template file)"

## 真实附件（来自 trace read_files tool_result）
- `DDR6TOP_Latch_FF_RS.list`：真实文件，含 3 节（#### Hirerarchy STD Latch/FF #### / #### Possible Flatten Latch/FF ####），每行 `<library> <cell>`，共 200+ 条目（dscqa_digital / dscqa_stdcells / stdcells_ac / dscqa_analog / dscqa_io 等）。本 case 用第一节的真实子集（8 条）作 visible A。
- `netlist`：真实 finesim 网表（symlink，198MB），格式为 `* Library : <lib>` / `* Cell : <cell>` / `* View : schematic` / `* Inherited view list : ...` / `.SUBCKT <name> <ports...>` / `XI... 实例` / `.ENDS <name>`。USER#2 给出的 latrq2_ckUnit 块是真实片段，本 case 用它 + 同格式构造块作 visible A netlist。

## assistant 工具链
list_allowed_files(3) + read_files(29) + search_codebase(10) + editor(42) + run_approved_command(1) + SandBox_MCP_Server__run_code(1) + get_agent_policy_status(3)。共 35 次 editor 迭代（文件腐蚀问题→最终在 `/home/ethanw/run_match.py` 全新重写）。最终脚本 `run_match.py` 完整捕获分类逻辑。

## 最终脚本逻辑（run_match.py，本 case reference 忠实复刻）
1. 解析 .list：跳过空行/#/*/#### 开头，每行 split 取前两段 (library, cell)。
2. 扫网表：逐行追踪 `* Library : <lib>` 与 `* Cell : <cell>`；遇 `.SUBCKT <name> <ports>` 时检查当前 (lib,cell) 是否在目标集合 → 精确匹配（lib+cell 都对才算）。
3. 过滤端口：`is_power_port`（name.lower() in POWER_PORTS 或 endswith('!')，POWER_PORTS={vbn!,vbp!,vcc!,vss!,vcc2sc!,vbn,vbp,vcc,vss,vcc2sc}）+ `CM_PAT = ^cm\d*_`（cm... 端口无效跳过）。
4. 端口分类（classify_format）：
   - CLOCK_PAT=`^(Clk|Ck|CLK|Lat|READ)\d*$` → clocks
   - CLOCK_N_PAT=`^(Clk|Ck|CLK|Lat|READ)\d*N$` → clock_ns
   - DATA_PAT=`^D\d*$` 或 DATA_EXT_PAT=`^(D|Din|DE|DO)\d*$` → data_in
   - RN_PAT=`^(RN|RstN|ResetN|RSTN|Reset_n|RST_N|rst_n|RSTN_R|RSTN_L)$` → rn
   - R_PAT=`^(R|RST|Reset|RESETB)$` → r
   - SN_PAT=`^(SN|SetN|Set_N)$` → sn
   - S_PAT=`^(S|Set)$` → s
   - Q 等其他端口无桶 → 静默丢弃
   - 门级单元（无 clock、无 clock_n、无 data）：信号两两配对放 R,S 列（`sub,,,,,,A,B` / 奇数尾 `sub,,,,,,C,`）
   - 时序单元：build_clock_pairs（Clk0↔Clk0N/Clk0n 配对，未配对者留空），data 与 clock pair 按 max 对齐循环；rn/sn/r/s 各取第一个
5. 输出格式：
   ```
   #### Matched Latch/FF cells from <list_basename> ####
   #### FMT: subckt,refname,signame,data,RN,SN,R,S ####

   * Library : <lib>
   * Cell    : <cell>
   .SUBCKT <name> <ports...>
   #### Capture arranged: subckt,refname,signame,data,RN,SN,R,S ####
   <sub>,<clk>,<clkN>,<data>,<rn>,<sn>,<r>,<s>
   ...
   ```

## case 合成（EDA-Eval-DesignFlow-LatchFFNetlistMatch-001, spice_sim A-faithful L1）
- 交付=通用 `match_latch_ff.py <list_file> <netlist_file> <output_file>`（便携 Python，做匹配+分类+输出）
- A=visible：真实 .list 子集（8 条：latrq2_ckUnit 真实 + latr3ckUnit/rsnand33LVx2/ffrqIOLVx1/latqLVx1_pwyfast_pc60/rsnand23LVx1_DQS/ffrqLx1/latrqLVSx1）+ netlist（真实 latrq2_ckUnit 块 + 同格式构造块；含 someOtherNotInList 测「只输出匹配项」）
- hidden B：不同 library（probe_dig/probe_std/probe_ac）+ 不同 cell（Probe_* 前缀）+ 不同端口组合（含 vcc2sc! 测电源过滤、cm1_sig 测 cm 过滤、unpaired Clk0N 测未配对 clock_n、other_lib/Probe_latrq2 测 lib 精确匹配、Probe_not_in_list 测排除）A≠B ✓
- reference=match_latch_ff_ref.py + check.py **k=16 断言 a-p** + negative/(empty_stub/print_expected/ref_core_deleted)
- 本地自验：REF PASS(B) + 3 neg 全 FAIL + §4.9 trio（empty/print-expected/ref-core-deleted）全 FAIL
- trace ethanw@hfhds201 1789545001824_x0t2m mc=183 hfhds201 local
