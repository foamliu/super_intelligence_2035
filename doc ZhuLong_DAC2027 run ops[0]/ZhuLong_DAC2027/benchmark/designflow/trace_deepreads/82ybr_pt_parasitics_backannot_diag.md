# Trace 深读 #4 — 82ybr：PrimeTime 寄生参数反标失败诊断（DRAM STA signoff）

> 原始 messages.json 1.56MB / 333 msgs / 168 user / 165 assistant / 131 tool_use（109 run_commands + 12 SandBox run_code + 7 search_apis + 3 get_api_details）。
> 已 scp 到 .75 workdir 解析后 close_session keep=false cleaned（不入库，不入 git）。

## 一、Trace 溯源（脱敏）
- session_file: `1787798131361_82ybr`（实际路径 `<ip>:/home/haoyut/.cline/data/sessions/1787798131361_82ybr/1787798131361_82ybr.messages.json`，1,560,701 字节）
- summary.tsv 命中：match_count=878，keywords netlist:1462 / schematic:361 / cellview:198 / cadence:175 / calibre:139 / analog:129 / virtuoso:85 / synopsys:83
- 工具分布：netlist 1229 / schematic 325 / cellview 89 / pyAether 69 / calibre 26 / "lang":"skill" 11 / "lang":"pyAether" 11 / synthesis 8 / virtuoso 6 / spectre 2
- 用户 hash：sha1("haoyut")[:12]（脱敏，host/session_file 保留以溯源）
- 热点机：hfeg0plg49 / hfeg0pkn003 / hfeg0plg15 / hfeg0plg102（同一 NFS home，scp 任一即可）
- 域归类：**pnr_signoff / STA**（PrimeTime 寄生反标 + 时序签核），兼涉 physical_verify（Calibre LVS net 映射）。pnr_signoff 类 503 命中，**此前无 proper design_flow case** → 本 trace 填补该域 proper 空白。

## 二、用户真实工作过程（完整对话流提炼）

用户是 DRAM 时序/寄生工程师，在 PIM LPDDR6 双芯（Logic Die=iejoal / DRAM Die=iejoad）验证平台上做 **PrimeTime 寄生参数反标（read_parasitics）失败诊断**。37 条 user_input 可分 5 个阶段：

**阶段 A — 环境全景掌握（user #1/#5/#6/#7）**
- 目标：掌握 `verilog.pim.iejoad.AIagent/` 整个路径环境，构建框架/框图。
- agent 产出：完整架构框图 — 基于 Cadence Xcelium/irun + SDF 时序反标的双芯 Verilog/SV 仿真测试平台；config/bin/libs/netlist/sdf/coverage/test/basiccheck_v3/Regressions 等子目录逐一剖析。

**阶段 B — Virtuoso 原理图层次定位（user #2/#3/#4）**
- 目标：从已打开的 LOGICTOP view 一层层 descend 到 `I_LowSpeedCtrlM6_4.I373`。
- agent 推理链：config/tbconfig（tbprojectname=iejoal=Logic Die, dram_projname=iejoad=DRAM Die, tbarchetecture=pim）→ 文件系统 find → OA 库 `iejoal_digital/LowSpeedCtrlM6_22ull`（22nm ULL 工艺后缀）→ 层次链 LOGICTOP→I_ChannelLogic→I_ChanMid→I_ChanMidSC0→I_Controller→I_RdLatencyDecTopM6_620→I_LowSpeedCtrlM6_4→I373（invx1_22ull 反相器，cm1_fc_SpeedSel3200to2133 取反）。
- 关键 SKILL 调用：`deOpenCellView("iejoal_digital" "LowSpeedCtrlM6_22ull" "schematic" "schematic" nil "a")`。

**阶段 C — V0_LOGICTOP 文件来源解析 + PT 输入清单（user #30/#31/#32/#33/#34/#35）**
- 目标：理解 V0_LOGICTOP 各文件来自哪个 EDA 工具 + 给流程框图。
- agent 产出：Cadence Virtuoso ADE SI Verilog Netlister 生成 690,934 行网表 / 4,827 个 block；ihnl/ 增量块级网表；si.log 网表生成日志。
- PT 必备 5 输入：① Gate-level netlist ② Libraries (.db) ③ Net Parasitics(SPEF) ④ Design Constraints(SDC) ⑤ OCV related files（set_timing_derate 0.95）。sdf.tcl = SDF 生成/反标脚本。spef `.cvps` 后缀 = Calibre CVPS 工艺角点压缩格式。

**阶段 D — 寄生反标失败根因诊断（核心，user #8–#29）**
- 用户抛出真实数据：
  - SDF INTERCONNECT 段：`(INTERCONNECT .../I218_1_/Y .../I34_1_/A2 (0.000::0.000))`
  - 反标报告 Error：`Error: Invalid capacitor (I_Array16GTop.I_Array8G_SC1...I_CMAryB_222.I34_1_:A2 5.29591e-06) on net ...ACLevelA[1]: Pin '...I34_1_:A2' is not connected to net (PARA-044)`
  - SPEF 头：`*SPEF "IEEE 1481-1999" *DESIGN "DRAMTOP" *VENDOR "Synopsys Inc." *PROGRAM "StarRC" *VERSION "R-2020.09-SP5-4" *T_UNIT 1.0 NS *C_UNIT 1.0 FF *R_UNIT 1.0 OHM`
  - SPEF *D_NET 块：`*D_NET *9977688 0.306163` + *CONN（*I *14315654:Y B *D invLx1 / *I *14315655:A3 B *D mx4Lx2）+ *CAP（8 行）+ *RES（3 行）+ *END *9977688 I_Array16GTop.I_Array8G_SC1...I_CMAryB_222.ACDef[3]
  - Verilog 网表实例：`mx4Lx2 I34_3_ (.vbp(inh_vbp), .vbn(inh_vbn), .vcc(inh_vcc), .S3(SetABODefault), ..., .A2(cm1_ro_ACThLevelA[3]), .A3(cm1_ro_ACThDefN[3]), .Y(net0296[3]));`
  - Calibre LVS rule 段：`LAYOUT PATH "DRAMTOP.gds" / SOURCE PATH "DRAMTOP.cdl.mod" / SOURCE SYSTEM SPICE / LVS BOX GRAY ... / LVS PREFER NETS FILTER ...`
  - net 名映射格式：`CellName#OldNetName#NewNetName`（schematic→layout net 映射表）
- agent 定位到 `parasitics_command.log`：`netlist/V0_DRAMTOP_2026Aug12.091738/pt_dir/parasitics_command.log`（10,460 行，PrimeTime U-2022.12-SP5，DRAMTOP，sharynl@shdd22，Aug 13 11:07:02 2026）。
- **反标汇总表（真实数字）**：

| Net Type | Total | RC network | Not Annotated |
|---|---|---|---|
| Internal nets (pin to pin) | 1,005,545 | 1,002,982 | 2,563 |
| Boundary/port nets (pin to pin) | 35,464 | 28,367 | 7,097 |
| **TOTAL** | **1,041,009** | **1,031,349** | **9,660 (0.93%)** |

- **三种 Error 类型**：
  - `PARA-044`：Invalid capacitor — pin 未连接到 net（如 ACLevelA[1] 上的电容）
  - `PARA-043`：Invalid coupling capacitor — 耦合电容至少一个节点不在当前 net 上
  - `PARA-124`：Cannot find net — 寄生网表中存在但设计网表中找不到的 net
- **反标匹配机制**（agent 验证）：PT 执行 read_parasitics 时，对 SPEF 中每条 net/pin：在 Verilog 网表中搜索同名 net → 验证 pin 确实连接到该 net → 找不到则记 PARA-124/044 → 该 net 未反标。
- **根因（用户引导得出）**：SPEF 由 **Synopsys StarRC** 生成，Verilog 网表由 **Cadence SI Netlister** 生成，PT（Synopsys）做反标——**跨 EDA 厂家 hierarchy 提取策略不同**：StarRC 会 merge 掉一些不重要的中间节点（如 net023 内部节点），而 Cadence 网表保留了完整层级 → 名称对不上 → 反标失败。这类因 merge trivial 节点导致的失败**不是 critical 路径**，可在 CDL 中加 ignore 规则过滤。
- 用户结论性诉求（user #25）：把反标报告中"跨厂家 hierarchy 策略不同"类型的 error，对应在 netlist 和 SPEF 中的完整层级显示出来比较 → 若是 merge 掉的不重要节点 → 不算 critical → 后续在 CDL 中加上。

**阶段 E — 反标报告结构精读（user #36/#37）**
- 报告分三段：① 仅读取 RC ② 全部类型反标结果（含 DES024，同种报错最多显示 100 条限制）③ pin to pin net。
- DES024 警告对应第二段（用户纠正 agent 看错）。
- 用户追问：为什么 error/warning 数量比最终"标不上"的数量少很多 → 因为 100 条/类显示上限 + 部分 warning 不计入未反标。

## 三、Case 提炼方向（下轮合成，domain=pnr_signoff）

**任务**：给定 PrimeTime parasitics_command.log（反标报告）+ DRAMTOP SPEF 片段 + Verilog 网表片段 + Calibre LVS rule 片段，产出反标失败诊断交付件。

**交付件（outputs/submit.zip）**：
1. `annot_diag_report.md` — 诊断报告：分类 9,660 条未反标 net（按 PARA-043/044/124）+ 根因（跨厂家 hierarchy 策略差异）+ 反标匹配机制说明 + 汇总表
2. `hierarchy_compare.tsv` — error → netlist 完整层级 + SPEF 完整层级 对照表（针对跨厂家 mismatch 类）
3. `noncritical_ignore_list.txt` — 非关键（merge trivial 节点）net 的 CDL ignore 条目，格式 `CellName#OldNetName#NewNetName`
4. `critical_fails.tsv` — 关键失败（需真实修复，非 merge 导致）清单

**test（Python 双参 check(deliverable, workdir)）牙齿设想**：
- a) zip 存在且解压成功，含 4 文件
- b) annot_diag_report.md 同时提到 PARA-043 + PARA-044 + PARA-124 三类
- c) report 含反标汇总数字（1,041,009 / 9,660 或 0.93%）
- d) report 指出根因为跨 EDA 厂家 hierarchy 策略差异（StarRC vs Cadence SI）
- e) hierarchy_compare.tsv 至少 N 行，每行同时含 netlist 层级路径 + SPEF 层级路径
- f) noncritical_ignore_list.txt 条目符合 `CellName#OldNetName#NewNetName` 格式（`#` 分隔三段）
- g) critical_fails.tsv 非空且与 noncritical 区分（不能把所有失败都归为 noncritical）
- **牙齿**：naive 报告只统计 error 数量、不做 hierarchy 对照、不区分 critical/noncritical、把全部 9,660 都当 noncritical ignore → 多条件 FAIL。

**attachments（assets/，从真实 trace 脱敏合成）**：
- `parasitics_command.log`（脱敏：人名 sharynl→<USER>，机器 shdd22→<HOST>，保留 PrimeTime 版本/汇总表/PARA error 样例）
- `dramtop.spef`（SPEF 头 + 若干 *D_NET 块含 *CONN/*CAP/*RES/*END，IEEE 1481-1999 StarRC）
- `dramtop_netlist.v`（Verilog 网表片段，含 mx4Lx2 等实例层级）
- `calibre_lvs.rule`（LVS rule 片段含 LVS PREFER NETS FILTER + net 映射格式说明）
- `sdf_interconnect.sdf`（SDF INTERCONNECT 段片段）
- `task_brief.md`（任务说明 + PT 5 输入清单 + 反标匹配机制提示）

**与已有 case 区分**：
- PDKQA-001（physical_verify）：Calibre VCO env aok/aoi autoswitch bug → 假 MGC_HOME 绕过。环境配置类。
- 本 case（pnr_signoff）：跨厂家 hierarchy 提取差异 → 反标失败分类 + critical/noncritical 区分 + CDL ignore。数据分析/诊断类。
- 两者 domain 不同、技术点不同、牙齿机制不同，无重叠。

## 四、执行备注
- 本轮（第113轮）= 深读（即时令 IX §五 两轮节奏的"深读"轮）。
- 下轮（第114轮）= 合成 EDA-Eval-DesignFlow-Backannot-001（pnr_signoff 域首条 proper），按本节契约建 assets + reference + test（7 条件独立有牙）+ pi-SUT 调试 + 追加单一 jsonl。
- close_session keep=false cleaned=true（已执行）。
