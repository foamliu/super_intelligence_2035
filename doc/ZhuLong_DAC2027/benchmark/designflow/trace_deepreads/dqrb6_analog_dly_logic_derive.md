# Deepread Note — dqrb6 (analog delay cell logic derive)

- **session_file**: `1795066359545_dqrb6`
- **user / host**: chuanqiz @ hfeg0pnd001
- **match_count**: 86 (analog:244 / schematic:160)
- **round**: r1223 (shard D, domain analog_context)
- **case_id**: `EDA-Eval-DesignFlow-AnalogDlyCellLogicDeriveProduce-001`

## Real user intent

用户 chuanqiz 在做模拟 IP 的逻辑功能核对。analogIP 库里有一批 `CustomDly*` 延迟控制 cell（CustomDlyNcCtrlIP / CustomDlyPulse200nsVbnVbpCtrlBIP / CustomDlyRdColPlsGenIP），每个 cell 的 schematic 混了 stdcells_am 标准逻辑门（inv/nand2/nor2）和模拟器件（TECHLIB switch/resistor/MOS/supply）。用户想推导每个 cell「顶层 input→output 的稳态逻辑关系」，把内部 delay/模拟部分忽略掉。

agent 用 Virtuoso skill 逐个 cell 读 terminals / instances / nets，然后手工跟踪 stdcells_am 逻辑门链，把模拟 switch/MOS/resistor 当 delay，得出稳态布尔关系。

## 可离线判分内核

trace 里真正能离线判分的部分 = 「读连接关系 dump → 只穿过逻辑门做稳态推导 → 输出结构化 JSON 报告」。agent 的 Virtuoso 交互（开 cellview、读 schematic）不可复现，但导出的连接关系是确定数据，可以做成 dump 文件喂给离线脚本。

## Case 设计

- **A (visible)** = `CustomDlyPulse200nsVbnVbpCtrlBIP` → `dump_A.txt`（4 terminals: In/Out/Dly200nsCap(inputOutput)/OutN；7 logic gates；含 I28=nor2Lx2；delay port=Dly200nsCap）
- **B (hidden)** = `CustomDlyNcCtrlIP` → `dump_B.txt`（4 terminals: In/Out/OutN/cm1_ro_NcDly<4:0>(input)；16 logic gates；无 nor2；I10=nand2GFx2；Out driver=I36(invPFx2)；delay port=cm1_ro_NcDly<4:0>）
- 两个 cell 稳态布尔关系相同（Out=In, OutN=!In），但门级结构完全不交：
  - A 有 NOR2(I28)，B 无 nor2
  - A I10=nand2Lx4，B I10=nand2GFx2
  - A delay port=Dly200nsCap(inputOutput)，B delay port=cm1_ro_NcDly<4:0>(input，经模拟 switch 环形振荡器链不达逻辑输出)
  - A 7 门，B 16 门
  - A Out driver=I9(invLx4)，B Out driver=I36(invPFx2)

## §4.9 anti-hardcode 防御

A/B 布尔答案相同（Out=In/OutN=!In），所以 §4.9(c) hardcode_a 防御靠**结构差异**：check() 断言 B 专属门（I10=nand2GFx2、I36/I35=invPFx2）、断言无 NOR2、断言 delay port=cm1_ro_NcDly<4:0>（非 A 的 Dly200nsCap）、断言门数≥10（A 只有 7）。hardcode_a 把 A 的完整报告喂给 B，truth_table 虽对，但 ④⑥⑦⑧⑪ 五条结构断言全挂。

## 关键技术点

1. **inputOutput port = delay**：Dly200nsCap 是双向电容节点，虽接到 I28(NOR2) 的输入，但稳态按 delay=1 处理。若当逻辑主输入，truth table 会多一维且 Out 在 Dly200nsCap=0 时变常 0（脉冲整形态），与「稳态逻辑」语义不符。
2. **output port 不能当主输入**：Out 由 I9(INV)←OutN 驱动，OutN 由 I10(NAND2) 驱动。eval_net 遇到 output port 要递归进 driver，不能当自由变量赋值，否则 Out/OutN 互为独立变量，truth table 退化。
3. **bus 展开 `<*N>netname`**：dump_B 里 net0125 有多行 bus 展开（只连 MOS），普通 `net0125` 行才带 I10/B（逻辑连接）。parser 要能吃 `<*N>` 前缀不崩。
4. **cm1_ro_NcDly<4:0> 是 bus port**：port 名带 `<4:0>`，其 net 只挂 `-/<port>`（port pin 本身）。bit net（cm1_ro_NcDly<0..4>）分别接到 I7/I1/I3/I5/I17 的 inv 输入，但这些 inv 输出经模拟 switch 链（环形振荡器）才到 net0125，不过逻辑门，故 cm1_ro_NcDly 分类为 delay（不可达逻辑输出）。

## 12 条断言

①含.py ②B 跑通+合法JSON ③7字段齐全 ④ports角色(In=logic/Out=output/OutN=output/cm1_ro_NcDly=delay) ⑤logic_reachable==['In'] ⑥delay含cm1_ro_NcDly且不含Dly200nsCap ⑦B专属门(I10=nand2GFx2/I36=invPFx2/I35=invPFx2) ⑧无NOR2 ⑨complement==[['Out','OutN']] ⑩tt 2行(Out=In/OutN=!In) ⑪门数≥10 ⑫三次md5一致

## 验证结果

- gold_ref.py 在 A/B 都跑通，A 出 7 门+Dly200nsCap+has_nor2=True，B 出 16 门+cm1_ro_NcDly+has_nor2=False，truth table 都 Out=In/OutN=!In。
- negative_selftest: gold PASS, empty_stub/print_only/core_deleted/hardcode_a 全 FAIL。
