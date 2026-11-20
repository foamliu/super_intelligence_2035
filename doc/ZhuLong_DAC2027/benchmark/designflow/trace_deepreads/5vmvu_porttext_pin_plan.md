# Deepread: 1791611132079_5vmvu (ellawu / hfeg0pkn005, mc165)

- **Domain**: schematic_netlist (Cadence SKILL port-text / pin label generation)
- **Session**: 310 msgs / 4 user turns, size 1.33 MB
- **Tools**: read_files ×76, editor ×66, run_commands ×2, ask_question ×1, search_codebase ×1
- **Real task**: 改造 `cxmt_autoPR_generatePortText.il`（Cadence SKILL，把 schematic 端口/网络以 Label+Pin 生成到 Layout 顶层）

## User turns (逐字原文，pinyin 无声调)
- U#0: `FENXIYIXIAZHEGEJIAOBEN` + attachment `cxmt_autoPR_generatePortText.il` (20.7 KB)
- U#4: `genjuzhegejiaobenxiugai shidedicengdepinnengfudaodingceng`（根据这个脚本修改 使得底层的pin能浮到顶层）
- U#228: `chuangjiandicengchule vcc vss desuoyou pin`（创建底层除了 vcc vss 的所有 pin）
- U#270: `dubantudicengweizhishizaidaimanagebufentixiande`（读版图底层位置是在 dbManage 部分体现的）

## Assistant 流程
1. read attachment → 分析原脚本（仅 schematic 追踪到的 pin 才创建，只处理 schematic instance）
2. ask_question 确认「底层 pin 浮到顶层」含义 → 用户选 **情况B**（layout 中所有 instance 的 pin 都被处理，包括 layout 独占）
3. 用 editor 工具迭代修改 `/home/ellawu/cxmt_autoPR_generatePortText_v2.il`（66 次 editor 调用，修语法、补 proceedCreate 标志）
4. 最终产物 `/home/ellawu/cxmt_autoPR_generatePortText_v2.il`：用 `proceedCreate` 标志实现——有 schematic 映射无条件创建（即便映射为 VCC/VSS），layout 独有仅当非电源地才创建

## 金标准逻辑（proceedCreate 模式，msg [309] 总结）
```
foreach(labelId labelList
    mappedNetName = updatepinTerminal_table[...]
    proceedCreate = nil
    if(mappedNetName then          ;; 有 schematic 映射
        netNameToUse = mappedNetName
        labelxy = labelId~>xy
        proceedCreate = t           ;; 无条件创建
    else                            ;; layout 独有
        netNameToUse = labelId~>theLabel
        if(netNameToUse == "VCC" || "vcc" || "VSS" || "vss" then
            ;; 跳过 VCC/VSS
        else
            labelxy = labelId~>xy
            proceedCreate = t       ;; 非电源地，创建
    if(proceedCreate then ...)
```

## A-faithful 判定
不可行：真实 `/home/ellawu` 的 Virtuoso cellview/layout DB 不可附加，live SKILL `dbCreateLabel`/`dbCreatePin` 不可移植 → **B 档 synthesized L1**。

## 合成 plan
spec-driven 生成器 `gen_porttext_plan.py --spec --outdir`：读 pin 盘点 spec JSON（design/top_cell/label_layer/pin_layer/power_nets/pins[]），产 `<design>_porttext.il`（SKILL proceedCreate 模式）+ `pin_plan.csv`（每 pin 决策）+ `plan_summary.json`（统计）。决策逻辑忠实 trace：mapped→created 无条件；layout-only + 电源地→skipped；layout-only + 非电源地→created。check 16 条件 a-p 验结构+决策+跨输入+确定性。

## check 16 条件清单
a(防泄漏+py_compile+has gen) b(B exit0+三件) c(dbCreateLabel) d(dbCreatePin) e(proceedCreate t/nil) f(SKIP+引用 B power_nets 不含 A VCC) g(mapped 全 created) h(layout-only 电源地 skipped) i(layout-only 非电源地 created) j(summary 对账+design) k(B .il 用 LPDDR4_PHY 不泄漏 DDR5) l(B2 跨输入 SerDes_RX+total_pins≠B+AVDD/AVSS) m(A-run≠B-run sha256+A 含 DDR5/VCC) n(B .il 含 M2+labelxy+xy 值) o(power nets from spec 注释含 VDD) p(确定性 3x sha256)
