# 深读笔记 · wdnwl (1792737644972) — LVS-MRC brknet_BAD 诊断

## trace 元信息
- session: 1792737644972_wdnwl
- user: cuij · host: 10.129.2.11 (hfeg0) · match_count: 42
- domain: schematic_netlist (LVS netlist diagnosis)
- 文件: /home/cuij/.cline/data/sessions/1792737644972_wdnwl/ (dir-based)
  - 1792737644972_wdnwl.messages.json (696KB, 63 msgs)
  - 1792737644972_wdnwl.json (2.4KB)
- 5 user turns (mode=act), 多轮 Q&A 诊断

## 用户意图（逐字原文，仅 key/token 掩码）
- **U#0**: `分析一下/proj/ddgoa/V0/ver/lvs/cuij/DQByte_MRC/layout_top.lvs.rep，lvs为什么没过` ← **clean produce**（提出诊断需求）
- U#16: `如何理解/proj/ddgoa/V0/ver/lvs/cuij/DQByte_MRC/layout.spi的内容` ← clean（解释需求）
- U#20: `为什么layout中会多出brknet_BAD呢` ← ❌ 已给根因假设（禁 A 档）
- U#22: `brknet_BAD的作用是什么` ← 解释需求
- U#24: `/proj/ddgoa/V0/ver/lvs/cuij/DQByte_MRC/lpe_C.rule中有brknet_BAD的定义` ← ❌ 已给位置/根因
- U#55: `发现报告中的brknet_BAD都与M2_resistance相关` ← ❌ 已给观察结论
- U#65: `我们重新来分析，首先report中报出来的brknet_BAD是指DEVICE brknet_BAD BRKNET_M2_BAD M2net(POS) M2net(NEG) (POS NEG)` ← ❌ 已给规则定义
- U#72-74: `我发现report中报告错误的位置 没有M2_term` ← ❌ 已给修复方向

## assistant 工具链
1. list_allowed_files → 列 DQByte_MRC 目录
2. read_files layout_top.lvs.rep (1935 行) + lpe.log + cci_lvs.log
3. read_files lvs.rep 分段 (100-1935)
4. read_files DQByte_MRC.cdl + search_codebase "brknet_BAD/brknet/skip_cell" + read_files skip_cell + hcells-lpe
5. read_files asOut.log + query_results + cdl 头
6. → 产出 ## DQByte_MRC LVS 报告分析（结构化诊断报告）
7. 后续多轮 read_files layout.spi + lpe_C.rule（python-runner search_brknet.py grep brknet）
8. 最终: brknet_BAD 是 MRC 故障指示器，BRKNET_M2_BAD marker 层标记 M2 路由不匹配，错误位置缺 M2_term

## 关键事实（金标准 = assistant 诊断结论）
- **Cell**: DQByte_MRC
- **总体结果**: INCORRECT
- **错误**:
  - Different numbers of nets: Layout 523, Source 489 (多 34)
  - Different numbers of instances: Layout 35, Source 1 (多 34)
- **Warning**: Ambiguity points were found and resolved arbitrarily.
- **Ports**: Layout 487 = Source 487 (一致)
- **brknet_BAD**: Layout 34, Source 0 (核心问题)
- **34 个 brknet_BAD pattern**: `Xnn(xxx.xxx,5141.729) brknet_BAD`, POS=WCK2Tib<N>, NEG=Net XXX
- **WCK2Tib 分组**:
  - WCK2Tib<0>: 7 个 (X1-X7), Nets 404,406,407,408,409,411,412
  - WCK2Tib<1>: 10 个 (X8-X17), Nets 414,415,416,417,418,420,421,422,423,424
  - WCK2Tib<3>: 9 个 (X18-X26), Nets 426,427,428,429,430,432,433,434,435
  - WCK2Tib<2>: 8 个 (X27-X34), Nets 436-443 (推断: 7+10+9+8=34)
- **brknet**: PDK 标准 cell (`Translating design TECHLIB/brknet/layout`), 设计者主动摆放做 MRC 检查
- **BRKNET_M2_BAD**: M2 marker 层, 路由不匹配时生成 polygon
- **lpe_C.rule 定义**:
  - `DEVICE brknet_BAD BRKNET_M2_BAD M2net(POS) M2net(NEG)`
  - `TRACE PROPERTY R(brknet) lay lay STRING`
  - `brknet_M2 = (M2resi WITH EDGE (LENGTH M2resi == 0.006)) TOUCH M2_term == 2`
  - `#IFDEF LVS_CHECK`
- **根因**: 错误位置缺 M2_term → brknet 单元 NEG 端浮空 → Calibre 提取为 brknet_BAD 而非正常 brknet

## A-faithful 判定
**不可行**:
1. 真实文件 `/rundata/ddgoa/V0/ver/lvs/cuij/DQByte_MRC/*` 属 cuij 私有，.75 as e0031982 读取 `Permission denied`（已验证）
2. lvs.rep 1935 行 + lpe_C.rule 7232 行，体积过大不宜作 A 附件
3. U#0 是 clean produce 但后续多轮 U#20/U#24/U#55/U#65/U#72 用户已给根因/修复，A 档若只用 U#0 则丢失多轮上下文（仍可，但文件不可附加是硬约束）
→ **B 档 synthesized**

## 合成 plan（B 档）
**技能**: LVS-MRC brknet_BAD 诊断器（gen_lvs_mrc_diag.py --report <lvs.rep> --rule <rule> --outdir <dir>）
- 解析结构化 LVS report（ mimic Calibre 格式）: overall / errors / warnings / layout-source counts / BAD device 列表 / BAD instance 详情 (id/coord/pos/neg)
- 解析 rule 文件: DEVICE <BAD> <MARKER> <POS>(POS) <NEG>(NEG) + brknet_<metal> = (...) TOUCH <metal>_term == 2
- 交叉引用: 每个 BAD device → marker layer + metal + pos/neg term
- 按 POS signal 分组 BAD instances
- 输出:
  - `lvs_mrc_diag.json` (cell/overall/errors/warnings/layout_counts/source_counts/bad_devices[*]/{name,count,marker_layer,pos_term,neg_term,metal,groups[*],instances[*]}/rule_mappings[*]/summary)
  - `report.md` (## Summary / ## Discrepancy 表 / ## BAD Device Analysis / ## Rule Mapping)

**A 输入** (trace-faithful, mimic DQByte_MRC):
- lvs.rep_A: DQByte_MRC, INCORRECT, 523/489 nets, 35/1 inst, 487 ports, 34 brknet_BAD, WCK2Tib<0..3>
- rule_A: DEVICE brknet_BAD BRKNET_M2_BAD M2net(POS) M2net(NEG), brknet_M2 = ... TOUCH M2_term == 2

**hidden B** (反硬编码):
- lvs.rep_B: DQSByte_MRC, INCORRECT, 411/389 nets, 27/5 inst, 256 ports, 22 brknet_M1_BAD, DQS_Tib<0..2>
- rule_B: DEVICE brknet_M1_BAD BRKNET_M1_BAD M1net(POS) M1net(NEG), brknet_M1 = ... TOUCH M1_term == 2

**hidden B2** (CORRECT 路径, 反 always-error):
- lvs.rep_B2: AN2Byte_MRC, **CORRECT**, 198/198 nets, 12/12 inst, 64 ports, **0 BAD devices**
- rule_B2: 无 BAD device 定义 (只有正常 brknet)

**反硬编码五轴**:
1. cell name: DQByte_MRC / DQSByte_MRC / AN2Byte_MRC 全不同
2. BAD device: brknet_BAD / brknet_M1_BAD / 无 (B2)
3. marker layer: BRKNET_M2_BAD / BRKNET_M1_BAD / 无
4. counts: 34/22/0 BAD, 523-489/411-389/198-198 nets
5. signal pattern: WCK2Tib<0..3> / DQS_Tib<0..2> / 无
6. overall: INCORRECT / INCORRECT / **CORRECT** (B2 测 no-error 路径)

## check.py 16 条件 a-p
a. zip 含 lvs_mrc_diag.json + report.md, 无 check/reference/negative/jsonl 泄漏
b. candidate py_compile 通过
c. B-run subprocess exit 0 + 产 2 文件
d. JSON overall == "INCORRECT" (B)
e. JSON cell == "DQSByte_MRC" (B)
f. JSON layout_counts.nets == 411 (B)
g. JSON source_counts.nets == 389 (B, diff=22)
h. JSON bad_devices 1 项, name == "brknet_M1_BAD"
i. JSON bad_devices[0].count == 22
j. JSON bad_devices[0].marker_layer == "BRKNET_M1_BAD"
k. JSON bad_devices[0].instances 22 项含 id/coord/pos/neg
l. JSON rule_mappings 映射 brknet_M1_BAD → BRKNET_M1_BAD, metal == "M1"
m. report.md 含 ## Summary / ## Discrepancy / ## BAD Device Analysis / ## Rule Mapping
n. B2-run (CORRECT): overall == "CORRECT", bad_devices 空 list (反 always-error)
o. 反硬编码: 源码无 A 字面量 "DQByte_MRC"/"WCK2Tib"/"BRKNET_M2_BAD"/"523"/"34" + A-run overall=="INCORRECT" & cell=="DQByte_MRC" & bad_devices[0].count==34
p. 3 次 subprocess sha256 一致 (确定性)

## 断言闸门
k_rationale = k_check = 16 ✓ (a-p 一一对应)
