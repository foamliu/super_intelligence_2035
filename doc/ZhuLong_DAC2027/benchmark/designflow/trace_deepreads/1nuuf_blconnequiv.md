# 深读笔记 · 1792743512849_1nuuf · victorq@hfeg0pkn002 · mc=49

- session: `1792743512849_1nuuf`（67 msgs / 432KB），user victorq@hfeg0pkn002，D-domain（netlist:115 schematic:25 lvs:8 hspice:3）
- 选料信号：U#2 干净 produce（未指根因/未给修复），可作 A 档任务说明原文候选

## 用户轮（完整）
- U#0 / U#1：`你可以对比电路网表吗`（确认能力，非任务）
- U#2（真正任务，原文）：`帮我对比一下这两个网表：1. /proj/drexp/V0/workdir/victorq/simulation/V3_miniarray_victorq/netlist_rnc  2. /proj/drexp/V0/workdir/victorq/simulation/AdamLi_Testbench_5sec_0805_wiDumSA_wr_976_schematic_ALPS/netlist。看下这两个网表BL的连接关系是否正确，我要进行TCS和WRTIME的仿真，这两个网表应该主要差异是BL LENGTH是1160和976，其他连接关系是否正确帮我看看`
  - 提需求 + 给出预期差异（BL LENGTH 1160 vs 976），但**未指出根因、未给修复**→ A 档任务说明可用原文
  - 目标：对比两份 SPICE 网表，验证 BL（位线）连接关系是否正确（除 BL 长度外其他连接是否一致），用于 TCS/WRTIME 仿真

## agent 工具链（msg#2→#66）
- ask_question（确认需求）→ list_allowed_files/read_files（探查 /proj/drexp 路径，系统映射到 /rundata/drexp）→ editor 写多个 Python 解析脚本：
  - `netlist_struct.py`：整体结构统计（13万+ 逻辑行，子电路清单）
  - `netlist_subs.py`：抽取子电路层次
  - `dump_blocks.py`：dump 关键 BL 模块体（WLHB Even/Odd、kcellBL）
  - `compare_conn.py`：**连接等价性自动校验**（忽略阻容值/m 倍数/W/L，只比节点连接）
  - `dump_top.py`：顶层 testbench 对比
  - `top_models.py`：顶层实例模型清单
  - `cmp_msaq.py`：写通路模块 msaq_write 对比
- run_approved_command 跑脚本，read_files 读结果

## 关键发现（assistant 结论，msg#66）
1. **核心 BL 单元/阵列连接关系一致**：所有「一一对应」的位线/阵列模块（kcellBLx4/kcellBLx16、WLHB）做连接等价校验（忽略数值）后拓扑一致，差异只在 R/C 值（按长度 1160/976 缩放）与 m 倍数（143.5/120.5）
2. **但二者并非「仅 BL 长度不同」**：
   - 1160 顶层用单一 `BL_Connection` 实例；976 拆成 `BL_Connection_Even`/`BL_Connection_Odd`（结构差异）
   - 写通路：1160 `msaq_write` vs 976 `msaq_write_wiRouting`（重命名 + 额外 routing，影响 WRTIME）
   - 顶层 testbench 实例化方式不同
3. 结论：BL 核心连接正确（可跑 TCS/WRTIME），但层级结构和外围环节有差异，跑前须知

## A-faithful 可行性
- ❌ 不可行：真实附件是 `/proj/drexp/...` 私有 DRAM 源树（数万行网表），沙盒不可复刻真值
- ✅ 做 **B-grade synthesized**：把核心操作「两份按 BL 长度缩放的 SPICE 网表 → 连接等价性校验（忽略数值缩放，只比节点拓扑）+ 结构差异（unpaired 子电路）报告」抽成自包含单文件任务

## B-grade synthesized 主题
候选 `bl_conn_equiv.py <netlist1.sp> <netlist2.sp> <out.json>`：
1. 解析 `.SUBCKT/.ENDS` + 实例（X 调用、R/C/M 器件）的节点连接
2. **配对**：子电路名按规范化（剥离 `_BLlength<num>` / `_WLx<num>` 长度/缩放后缀）分组，跨两文件的相同规范化名为一对
3. **连接等价**：对每对，比较实例多签集合 `(kind, model_norm, nodes_tuple)`，**忽略数值参数**（R/C 值、m=、W=、L=），只比节点连接拓扑
4. 输出 JSON：`{summary, pairs:[{norm_name,name1,name2,conn_equiv,n_inst1,n_inst2,diff_reasons}], unpaired1, unpaired2}`

A = `dram_bl_array_A.sp`（BL length 1160：kcellCore + kcellBLx4_BLlength1160 + OneSection_SecA_WLx1160 + BL_Connection(单块) + msaq_write + ssa_core + TBTop，7 subckts）
隐藏 B = `dram_bl_array_B.sp`（BL length 976：kcellCore + kcellBLx4_BLlength976 + OneSection_SecA_WLx976 + **BL_Connection_Even/BL_Connection_Odd(拆分)** + **msaq_write_wiRouting(重命名+routing)** + ssa_core + rt_buf + TBTop(4 inst vs A 3 inst)，9 subckts）
反硬编码：核心 BL 模块（kcellBLx4/OneSection）拓扑一致（equiv=True，仅 R/C/m 缩放）；外围 BL_Connection/msaq_write 结构性差异（unpaired）；TBTop 实例数 3 vs 4 + 模型集合不同（equiv=False）

预期 B 输出：n_sub1=7, n_sub2=9, n_pairs=5(kcellCore/kcellBLx4/OneSection_SecA/ssa_core/TBTop), n_equiv=4, n_diff=1(TBTop), unpaired1={msaq_write, BL_Connection}, unpaired2={msaq_write_wiRouting, BL_Connection_Even, BL_Connection_Odd, rt_buf}

## 与已有 case 区分（非重复）
- #437 VconnConsistCheck：**Verilog** 模块例化 `.port(sig)` 命名连接端口一致性比对（单方向 port 匹配）
- #436 HierNetTrace：**单**层级 SPICE net 跨层级 glob 追踪
- #434 NetlistStructDiff：HSPICE 网表结构化 diff（两文件行级结构对比）
- **本 case**：两份**按长度缩放**的 SPICE 网表的**连接等价性校验**（规范化配对 + 忽略数值缩放只比拓扑）+ 结构差异（unpaired）报告 —— 操作维度「参数缩放下的拓扑等价」+「规范化名配对」是新的
