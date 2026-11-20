# Deepread — sid_1793347412273_nq8l2 (zjqiao@hfhds201) — hcell missing/renamed block finder

**Trace source**: user=zjqiao, host=hfhds201, session_file=1793347412273_nq8l2.messages.json, match_count=98
**Domain**: spice_sim (SPICE netlist parsing, LVS hcell cross-check)
**File**: /home/zjqiao/.cline/data/sessions/1793347412273_nq8l2/1793347412273_nq8l2.messages.json (74 msgs, 11-04)
**Netlist**: /home/zjqiao/netlist (148 MB, AETHER-SE export, drvqa_top/WOWTOP_1C2A)
**Attachment**: /home/zjqiao/.cline/data/sessions/1793347412273_nq8l2/uploads/hcell (4017 B, 103 lines, 2-col col1=col2)

## USER#0 (verbatim, A-档 task statement)
> 现在我需要你做一件事情，将hcell这个文件的第一列逐行在netlist这个文件中进行检索，看看有没有哪个block是在netlist中找不到（改过名字）的
> [附件] hcell

**A-档 rule ② check**: USER#0 只给目标（找出 netlist 中找不到/改过名字的 block）+ 方法（hcell 第一列逐行在 netlist 中检索），未给根因/修复方案 → 纯需求轮 ✓

## USER#1 (msg[70], UNRELATED — pivot, not the A-档 task)
> 这个agent能不能做成那种交互式的agent，然后可以加一个提交完仿真以后top上去的选项...

(USER#0 已完成 → assistant 产出 check_hcell_in_netlist.py 并报告 missing blocks；USER 转新需求)

## Netlist format (SPICE, AETHER-SE)
- Header: `* Tool : AETHER-SE`, `* Top Design : drvqa_top/WOWTOP_1C2A/schematic`
- Subcell block: `* Library : <lib>` / `* Cell    : <cell>` / `* View    : schematic` header → `.SUBCKT <cell> <ports>` ... `.ENDS <cell>`
- Mixed case: `.subckt` (lowercase, e.g. switch_close/switch_open) + `.SUBCKT` (uppercase, e.g. IO_DqLdMdl)
- Instance refs: `X<name> <pins...> <subckt_name>` (last token = referenced subckt)
- 11876 `.` lines, 5875 `* Library`/`* Cell` headers

## Assistant approach (check_hcell_in_netlist.py)
1. read_hcell_blocks: hcell 每非空行 split() 取 [0] = block name (col1)
2. dedup preserving order
3. search_netlist_for_blocks: 扫 netlist 每行，对 block_set 中的 name 检查三类命中：
   - `.SUBCKT ` / `.subckt ` 行 → parts[1] (subckt definition name)
   - `* Cell` 行 → regex `^\*\s*Cell\s*:\s*(\S+)` (cell header value)
   - `X` 开头行 → parts[-1] (instance reference, last token)
4. report: found (有 evidence) vs missing (无 evidence) → missing = not found in any of 3 locations

## Gold standard (USER#0 spec 正确实现)
- 读 hcell col1 (block names)，去重保序，跳过空行
- 解析 netlist：block "found" = 在以下任一位置出现为 **exact token**：
  1. `.SUBCKT`/`.subckt` 定义名 (第 2 token)
  2. `* Cell` header 值
  3. X-instance 引用 (X 行末 token)
- 输出 = hcell col1 中 NOT found 的 block（missing/renamed），按 hcell 顺序（去重后），每行一个 block name
- **rename 陷阱**：block 改名（如 AG_VdivActTopSpare → AG_VdivActTopSpare_v2）→ exact match 失败 → 报 missing（substring match 会假阳性"找到"）

## Case 合成计划
- **id**: EDA-Eval-DesignFlow-HcellMissingFind-001
- **domain**: spice_sim, **track**: faithful, **level**: L1 (离线 Python 解析 netlist+hcell)
- **交付**: `check_hcell_missing.py <hcell_file> <netlist_file> <output_file>`
- **A** (SUT 可见): hcell_A (~24 block, 含空行+重复+rename 陷阱) + netlist_A (小型 SPICE netlist, mixed-case .subckt/.SUBCKT, * Cell header, X-instance ref)
- **hidden B** (判分): hcell_B + netlist_B (不同 library ddr5_cmos_phy, 不同 block, 不同 missing 集)
- **check.py** k=12 断言 (a-l): zip+py / compile / --help / 跑B exit0 / B 输出非空单 token / B missing 集==期望 / 无重复 / 保序 / 无假阳性(跨输入排除 A missing) / * Cell header 检测 / X-ref 检测 / 跨输入 A==期望∧A≠B∧rename 陷阱+dedup
- **negative** (5 stub): naive_empty / print_only / hardcode_A / substring_trap / subckt_only → 全 FAIL
- A missing 集 (5): {AG_VdivActTopSpare, AG_BCenterL_moscap_ntk_lv, AG_BCenterL_moscap_ptk_lv, R_GIDLPwr3, AG_AnalogEdgeLTop8G}
- B missing 集 (5): {AG_PhonyActSpare, AG_BCenterPhyR_moscap_ntk_lv, AG_BCenterPhyR_moscap_ptk_lv, R_GIDLPwrPhy3, AG_PhonyEdgeTop}
- A≠B ✓ (不同 block name)
