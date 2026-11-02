# 深读：1792572733650_pfubi — PrimeTime TimingECO flow 构建（e0046913 / agent=lead）

- **trace**: `1792572733650_pfubi.messages.json`（hfeg0plg52，1.34MB，253 msgs，match_count=153）
  - keywords: netlist:654 synopsys:357 primetime:213 icc2:194 innovus:60 cadence:20 tempus:16 pdk:10
  - **真实设计流（非 Q&A）**：agent=lead 真跑 pt_shell + cshell + 文件编辑，构建完整 TimingECO flow
- **case_id**: `EDA-Eval-DesignFlow-TimingECO-001`（domain=verification，L2/L3 真跑 PrimeTime + ECO loop + re-signoff）

## 用户真实意图（逐字）
- USER[0]：问"Top Timing ECO"是什么 —— ①Timing ECO flow 与 Top STA flow 衔接适配 ②ECO patch 生成策略与 P&R 对齐 ③跑通 ECO 后时序重签核全流程 ④输出流程说明文档。
- USER[17/18]（**主任务，A 档任务说明用此逐字**）：给 STA_flow 描述作模板，要求在 `/home/e0046913/TimingECO_flow` 构建 TimingECO flow + demo 跑通。关键结构要求：
  - 目录：run/（cshell 运行脚本）、scr/（tcl，按读入顺序编号 `1_setup.tcl;2_read_constraint.tcl;…;10_rpt.tcl`）、setup/、data/、sdc/、log/、rpt/、session/、patch/
  - enable：环境配置、工具选型、子模块 lib 输入件读入；选项传参适配不同 corner/模式
  - 参考 `/apps/imctf/cad/script/digital_flow/feint` synopsys pt reference flow；工具 `/apps/synopsys/primetime`（需 module load license）
  - 思考过程用中文展示

## assistant 工具链（真产物）
- read STA_flow 已有脚本（run_sta.csh / 1_setup..10_rpt.tcl）作模板
- run_approved_command 跑 STA_flow demo（mac 设计）确认环境
- **真跑 pt_shell 探针**（_eco_probe.tcl v1-v5）：read_db core_typ.db → 列 lib cell → 找 buffer/delay/flop cell + pin 名（clk1b27/clk1b54/clk1a27/clk1b3, fdf1a3）
- editor 创建完整 TimingECO_flow：
  - `data/eco_demo/eco_demo.vg`（2-flop：u_din_reg→u_dout_reg，fdf1a3）
  - `sdc/eco_demo.sdc`（period 6.0, hold_unc 0.50 故意造 reg→reg hold viol, setup_unc 0.05, in/out delay）
  - `setup/common_setup.tcl`（STA_ROOT 相对路径便携；DESIGN/PT_CORNER/MODE/ECO_STAGE/ECO_BUFFER_LIST/LIB_PROFILE；tutorial→core_typ.db）
  - `scr/main_eco.tcl` + `scr/1_setup.tcl`..`scr/10_rpt.tcl`（11 个编号 tcl）
  - `run/run_eco.csh`（cshell launcher，-design/-corner/-mode/-stage/-eco_types/-buffer/-profile/-ptver/-ideal_clock/-propagated_clock/-extra 选项）
  - `run/run_demo.csh`（一键 3 阶段：signoff→eco→resignoff，自检 signoff HOLD_VIOL>=1 且 post-ECO setup=0 hold=0）
  - `README.md`（流程说明文档 = 用户目标④）
- 真跑 demo：signoff → fix_eco_timing -type hold 插 buffer → re-signoff CLEAN

## 金标准（.75 真跑验证 2026-11-02 15:00，pt_shell U-2022.12-SP5）
- **signoff**：`rpt/eco_demo_tt0p8v25c_func_signoff.summary.txt` = `SETUP_VIOL=0 HOLD_VIOL=4`（baseline 4 hold viol）
- **eco**：`patch/eco_demo_tt0p8v25c_func_eco.eco_changes.txt` = 4 × `ADDITION U_PTECO_HOLD_BUF1..4 ( clk1a27 )`；`eco_applied.flag` = `ECO_TYPES=hold ECO_CELLS_ADDED=4 ECO_BUFFER_LIST=clk1b27 clk1b54 clk1a27 clk1b3`；`eco_changes.icc2tcl` = 4 × `insert_buffer ... clk1a27 -new_cell_names U_PTECO_HOLD_BUF1..4`（ICC2 handoff）
- **re-signoff**（in-session post-ECO）：`rpt/eco_demo_tt0p8v25c_func_eco.post.summary.txt` = `SETUP_VIOL=0 HOLD_VIOL=0`（CLEAN）
- run_demo.csh 退出 0，打印 `TimingECO demo PASS: signoff -> ECO(hold fix) -> re-signoff loop OK.`
- 7_signoff.tcl：report_timing -delay_type max/min -nworst 2，count `slack (VIOLATED)` 写 `SETUP_VIOL=/HOLD_VIOL=` summary

## 隐藏 B（结构性不同，.75 真跑验证 2026-11-02 15:01）
- `eco_demo_B.vg`：3-flop 移位寄存器（u_r1→u_r2→u_r3，fdf1a3），vs A 2-flop
- `eco_demo_B.sdc`：period 4.0, hold_unc 0.60, setup_unc 0.10, in_delay 0.80, out_delay 0.30
- corner `ss0p7v125c`（vs A `tt0p8v25c`）
- **B signoff**：HOLD_VIOL=6（vs A 4），SETUP_VIOL=0
- **B eco**：9 × ADDITION clk1a27（vs A 4），ECO_CELLS_ADDED=9
- **B re-signoff**：SETUP_VIOL=0 HOLD_VIOL=0（CLEAN）
- → B 与 A 在拓扑/违例数/buffer 数/corner 全不同，击败硬编码 A

## .75 资源
- pt_shell：`/apps/synopsys/SRB/pts/U-2022.12-SP5/bin/pt_shell`，license OK（probe PTOK exit 0）
- core_typ.db：4.4MB，已缓存到 `/home/e0031982/teco_case_lib/core_typ.db`（check.py 复制此路径到 SUT flow 的 data/libs/）
- tcsh 6.18.01 可用；run_eco.csh 需 `unset LD_PRELOAD; unset LD_LIBRARY_PATH`（agent framework 注入旧 libstdc++ 破坏 pt_shell）

## check.py 设计（≥8 条断言，待写）
- (a) submit.zip 结构：run/run_demo.csh + run/run_eco.csh + scr/编号 tcl(1..10)+main + setup/common_setup.tcl
- (b) run_demo.csh 是 cshell（`#!/bin/csh`）+ 可执行 + 3 阶段 signoff/eco/resignoff 逻辑
- (c) scr/ 编号 tcl 齐全（1_setup..10_rpt 模式）+ main_eco.tcl
- (d) 8_eco.tcl 含 `fix_eco_timing` -type hold（真用 ECO 引擎，非手写 patch）
- (e) **A 真跑**：run_demo.csh 在 A（eco_demo）上 exit 0 + 打印 demo PASS
- (f) A signoff summary：HOLD_VIOL>=1（baseline 有 hold viol）+ SETUP_VIOL==0
- (g) A ECO patch：eco_changes.txt 存在 + >=1 `ADDITION` 行（buffer 真插入）
- (h) A post-ECO re-signoff：post.summary HOLD_VIOL==0 + SETUP_VIOL==0（fix 生效）
- (i) **B 真跑 cross-input guard**：run_eco.csh -design eco_demo_B -corner ss0p7v125c signoff exit 0 + HOLD_VIOL>=1（B 也有 viol，非硬编码 A）
- (j) B eco：eco_changes.txt >=1 ADDITION（B fix 也插 buffer）
- (k) B post-ECO：post.summary HOLD_VIOL==0（B resignoff CLEAN）
- (l) run_eco.csh 参数化：接受 -design/-corner/-mode/-stage 选项（非硬编码 eco_demo/tt0p8v25c）
- (m) README.md 存在（流程说明文档 = 用户目标④）
- (n) 输出命名 `<design>_<corner>_<mode>_<stage>` 模式（A: eco_demo_tt0p8v25c_func_*，B: eco_demo_B_ss0p7v125c_func_*）

## 负样本（待写 negative/）
- fake_empty（空 submit）→ (a)
- fake_print_expected（只打印 "demo PASS" 不真跑 pt_shell）→ (e)/(f)（无真 summary 文件）
- fake_core_deleted（8_eco.tcl 删 fix_eco_timing，手写假 patch）→ (d)/(g)
- naive_hardcode_a（run_eco.csh 硬编码 eco_demo/tt0p8v25c，不接受 -design）→ (l)/(i)（B 跑不了）
- naive_no_eco_engine（跳过 fix_eco_timing，patch 空）→ (g)/(h)

## 进度
- ✅ 深读 + 金标准 + 隐藏 B 全部 .75 真跑验证通过
- ✅ lib 缓存 /home/e0031982/teco_case_lib/core_typ.db
- ⬜ check.py + reference/ + negative/ + self-verify + jsonl + 日报（DEBT，下轮第一件事）
