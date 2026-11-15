# Deepread · ibwba · virtuoso netlist SFE 语言上下文不匹配根因诊断

- **session**: 1794212917714_ibwba (zhililu@hfeg0pkn002, mc154, spice_sim)
- **trace 路径**: /home/zhililu/.cline/data/sessions/1794212917714_ibwba/1794212917714_ibwba.messages.json (26 msgs, 214KB)
- **旧判定**: parked "consultation virtuoso-netlist-sim debug-sfe" (r435 peeked)
- **r618 reaudit**: 可造 (debug-Q&A 根因诊断)

## 真实用户意图（3 真实用户轮）

1. **U#0**: 「virtuoso怎么用已生成的netlist仿真」 — how-to Q&A：如何在 Virtuoso 里用已生成的 netlist 做仿真
2. **U#16**: 贴 SFE-868 报错 — `input.scs` line 16: Cannot open input file '.../netlist/netlist' + AMS-1245 AMS UNL netlisting failed。问「这是什么原因」
3. **U#23**: 贴新一组报错 SFE-1802 / SFE-1025 / SFE-1703 / SFE-874 — `analog/netlist` line 6/66/100: Spectre "subckt" statements not supported in spice language sections. Use "simulator lang=spectre" + Instance 'INM0': extra value 'nsvt_dbc' in SPICE syntax + Wrong number of nodes (2-3 terminals Spectre / 2 terminals Spice) + Unexpected end of line

## 助手工具链

- #1-#3: skill eda_agent + read_files fullchip_simulation/README + list_allowed_files
- #9: RAG_MCP search_apis (schPinListToVerilog / annLoadAnnotationData / rdeSource — 均不相关)
- #12: search_codebase (timeout)
- #15: **给出 4 方法 how-to 指南**（命令行 spectre/hspice、ADE Run、外部 include、ViVA 看波形）
- #17: SFE-868 诊断 — 初判「主网表 netlist 文件未生成」，list_allowed_files + get_agent_policy_status 验证路径可达
- #19-#20: 发现 netlist 文件**实际存在**（dir listing 含 `netlist` file）→ 修正诊断方向
- #21: read_files input.scs（line 6 `simulator lang=spectre binding=vlog`，line 16 include `.../netlist/netlist`）
- #24: **关键诊断** — 读 SFE-1802/1025/1703/874，判「语言上下文不匹配」：netlist 文件用 Spectre subckt 但无 `simulator lang=spectre` 声明
- #25: read_files analog/netlist（line 1 空，line 6 `subckt INV_2X_SVT`，无 lang 声明；实例 INM0/IPM0 用 nsvt_dbc/psvt_dbc 三端）

## 根因链（实测确认）

**input.scs**（顶层网表，Virtuoso 为 finesim 生成）:
- line 6: `simulator lang=spectre binding=vlog` — 设 Spectre 语言上下文
- line 9-15: include 7 个 model lib section（35H_DBCFS_Model_PF_v0d1_Rev05.lib, section=ttg_mos_varactor_dbc / tt_diode_bjt_dbc / tt_res_dbc / tt_hir_dbc / tt_mim_dbc / tt_mom_dbc / pre_sim_dbc）
- **line 16**: `include ".../netlist/netlist"` — 引入子网表

**analog/netlist**（被 include 的子网表）:
- line 1: 空
- line 2-5: 注释（Library/Cell/View/Inherited view list）
- **line 6**: `subckt INV_2X_SVT` — Spectre subckt，但**文件顶部无 `simulator lang=spectre` 声明**
- 实例 NM0_DUMMY/INM0 (nsvt_dbc, 3 端 VSS/O_INV/I_INV)，PM0_DUMMY/IPM0 (psvt_dbc, 3 端 VDD/O_INV/I_INV)

**报错分型**:
- **SFE-1802** (line 6/66/100): Spectre "subckt" not supported in spice language sections → 子网表缺 lang 声明 → finesim 落回 SPICE 上下文
- **SFE-1025** (INM0/IPM0): extra value `nsvt_dbc`/`psvt_dbc` in SPICE syntax → SPICE 把模型名当多余位置参数
- **SFE-1703** (line 33): Wrong number of nodes → SPICE 端口实例只支持 2 端，Spectre 支持 2-3 端
- **SFE-874** (line 65/99): Unexpected end of line → SPICE 上下文解析续行符失败

**根因**: 被 include 的子网表 `analog/netlist` 顶部缺 `simulator lang=spectre` 指令，finesim 在 include 边界后落回 SPICE 语言上下文，把 Spectre 格式的 subckt/instance 卡当 SPICE 解析，触发 4 类 SFE 错误。
**修复**: 在 `analog/netlist` 文件顶部加 `simulator lang=spectre` 指令（或确保 netlister 对每个可 include 的网表片段都发 lang 声明）。

## 造题形态

- **域**: spice_sim · **层**: L1 便携 debug-Q&A 根因诊断
- **A 档不可行**: 真实 /proj/lacaa PDK 私有 + /rundata 仿真目录依附内网，不可离线沙盒交付
- **B 档 synthesized**: mock input.scs + netlist + error_log + dir_listing fixtures，算法忠实（解析 include 链 → 检测 lang 声明缺失 → 分类 SFE 错误 → 定位根因 → 给修复动作）
- **新形态**: reaudit「Virtuoso netlist SFE 语言上下文不匹配」操作化 + simulator-lang-directive 跨 include 边界丢失首例 + SFE 错误四分型(1802/1025/1703/874)首例 + Spectre-vs-SPICE 语法上下文边界诊断首例
- **hidden B**: 全异设计 + SFE-868 file-missing 真根因（netlist 文件确实不存在于 dir listing）→ error_type/root_cause/fix_action 全异 cross-input guard
