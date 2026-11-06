# Deepread: sid_1793843849886_hsizo — finesim_ignore 脚本生成

- **trace_source**: user=ynbai · host=hfhds201 · session=1793843849886_hsizo · mc=211
- **domain**: spice_sim (finesim ignore 配置文件生成)
- **size**: 907955 B · 325 msgs · 164 user msgs
- **trace 末尾状态**: USER#162/163 报 bug「执行后 8 个文件为空」—— trace 未以用户接受产物收尾 → **合成金标准**（USER#0 spec 的正确实现）

## USER 轮（选 A-档任务说明）

- **USER#0 (idx 0)** ← A-档任务说明（逐字原文）:
  「写一个脚本，输入为netlist，输出为finesim ignore文件，脚本帮忙抓出来 XIctop.XI_Channel.XI_BnkGTopX4_Top.XI_BnkGTopX4_gut.XI_BnkGTop_AC.XI_D_RWCBG 下的所有instance的hierachy，只到下一级，例如 …XI_D_RWCBG.XI_D_CasBnkGRptLR，输出到 …/finesim_ignore.list文件中，文件内容为 .option finesim_ignore = "hierachy" 例如 .option finesim_ignore = "XIctop…XI_D_CasBnkGRptLR" 下一行为下一个instance, netlist文件path为 …/netlist」
  - 纯需求轮 ✓（给目标+方法，未给根因/修复）→ 合格 A-档
- USER#69: 加排除 AbusEnRdCtrl（后续扩展，不进 prompt）
- USER#74: 生成 8 个文件按 hierarchy 区分（后续扩展）
- USER#89/142: 更复杂 ignore 逻辑 + 嵌入抽网表 flow（后续扩展）
- USER#162/163: bug 报告「8 个文件为空」→ trace 未闭合

## 金标准（合成）

USER#0 spec 的正确实现：扁平 SPICE 网表中，instance model 名以 dot 路径编码 hierarchy；
脚本提取所有以 `parent_path + "."` 开头的 model 名，取下一级 segment（split('.')[0]），去重排序，
输出每行 `.option finesim_ignore  = "<full_path>"`。

- 关键边界：`startswith(parent + ".")` 而非子串匹配（防 XI_D_RWCBGextra 陷阱）
- 只到下一级：`remainder.split('.')[0]` 折叠更深层
- A: parent=…Top…XI_D_RWCBG, 6 children (RptLR/PllLR/GrdR/GrdL/WLT/WLB)
- B: parent=…Bot…XI_D_RWCBG, 7 children (RptRL/PllRL/GrdR2/WLT2/SATop/SABot/BufCtrl)

## case 设计

- task_id: EDA-Eval-DesignFlow-FinesimIgnoreGen-001
- track: faithful (A-档), level: L1 (离线 Python netlist 解析)
- 交付: gen_finesim_ignore.py <netlist> <hierarchy_path> <output>
- check: 12 断言 a-l (zip/compile/help/runB/format/underParent/oneLevel/complete/noDup/crossParent/crossInput/substringTrap)
- negative: 5 stub (empty/print_only/hardcode_B/substring_trap/recurse_all) + §4.9 (empty_zip/core_cut)
- 自验: REF PASS 12/12 + 5 neg FAIL + 2 fake FAIL = SELFTEST PASS ✓
