# 深读笔记 — sid 1793021121702_24h7g (hemiao1w @ hfeg0plg75, mc=225, 341 msgs/1.1MB)

## trace_source
- user: hemiao1w (hemiao1.wang@cxmt.com), host: hfeg0plg75 (10.129.32.80 类), session: 1793021121702_24h7g
- match_count=225; keywords: schematic:878 cellview:622 dbopencellviewbytype:480 cadence:175 virtuoso:137 analog:45 opamp:24
- domain: layout_virtuoso (Virtuoso SKILL schematic 操作)

## 用户意图轮（逐字原文，唯一真意图轮）
- U#1 (idx 0): `/proj/lagat/V0/workdir/hemiao1w 分析读取这个路径都有什么东西` （探查工作目录）
- **U#2 (idx 15): `根据lagat_sch_hemiao1w中的电路设计，可以帮我在顶层插入 text吗，对电路的层级进行描述和说明`** ← 核心意图轮（纯意图，未给根因/修复 → A-档可用；但"层级描述"需具体化 → 取 B-档 synthesized）
- U#3-U#7: SKILL 加载/运行回灌日志（tool_result 回灌，非意图）
- **U#8 (idx 292): `牛逼，text加上了，但是你怎么把我的电路给删了？`** ← 关键负反馈：脚本能加 text 但**删除了用户电路**！

## agent 真实工作
1. 探查 /proj/lagat/V0/workdir/hemiao1w 目录结构（cds.lib / lagat_sch_hemiao1w / lagat_sim_hemiao1w / logs / RX_AFE_model_vs_circuit / oceanScript.ocn / sim CSV）
2. 深入分析顶层 cell `dq_rx_afe` (library `lagat_sch_hemiao1w`, view `schematic`) 层级：读 Ocean 脚本 save 语句 + 各子 cell 目录 → 推出 6 块层级
3. 写 SKILL 脚本 `addHierText_labels.il`（先写 agentdir，再 cp 到 home）：
   - `dbOpenCellViewByType("lagat_sch_hemiao1w" "dq_rx_afe" "schematic" "" "w")` 打开 cellview
   - `labelList = list(...)` ~80 条 `list("text" x y textString nil)`，含：TITLE 块 / 6 个 BLOCK 段（### 分隔，含 [n] cell (inst) -- role / desc / Input/Output / Params / Subblocks(+--) / Note）/ Top-Level Pin/Signal Summary（Supply/Input/Output/Bias&Control）/ Signal Flow / Footer
   - `foreach item labelList schCreateNoteLabel(cv x:y textStr "lowerLeft" "R0" "fixed" 0.125 "normalLabel")`
   - `dbSave(cv); dbClose(cv)`
4. **踩坑**：SKILL 沙箱只支持 ASCII，初次含中文注释 + Unicode 装饰字符 ▓▒░，重写为纯 ASCII（用 Python 分 part1-4 写）
5. **重大 bug**：`"w"` 模式 dbOpenCellViewByType 打开**空白** cellview（非追加），schCreateNoteLabel 在空白上建 text，dbSave **覆盖原电路** → 用户电路被删
6. 进入恢复模式（A[323]+）：查 sch.hist / OA 内部版本 / Check&Save 恢复指南

## 关键真实事实（gold 依据）
- library=`lagat_sch_hemiao1w`, cell=`dq_rx_afe`, view=`schematic`, tech=`22nm HLMC`, VDD2D=0.85V, vddq=0.5V
- 6 块（含 instance 名）：
  - [1] dq_rx_vbias (Bias Generator): in=ibias, out=vbp
  - [2] dq_rx_vref (Reference Voltage Generator): in=vdd2d,bias_vref; out=ref; notes: vcm_in=125mV, schematic_Radj variant
  - [3] dq_rx_afe_eq (I_dq_rx_afe_eq_1, CTLE Equalizer): in=inp,inn; out=vop_eq,vom_eq; params Rs1=300 Cs1=550f Rs2=100 Cs2=300f; 6 subblocks: inpair/Rdeg/Cdeg/rload/tail/ofst_tail
  - [4] dq_rx_afe_s2d (I_dq_rx_afe_s2d_0, S2D Converter): in=vop_eq,vom_eq; out=vop_s2d,vom_s2d; bias ibias_s2d=1mA; 4 subblocks: inpair/rload/tail/ofst_tail
  - [5] dq_rx_afe_vga (I_dq_rx_afe_vga_2, VGA): in=vop_s2d,vom_s2d; out=vop,vom (outp=vop,outn=vom); bias ibias1=3mA ibias2=3mA rtrim=100; 5 subblocks: inpair/Rdeg/rload/tail/ofst_tail
  - [6] dq_rx_4to15thermal_decode (4-to-15 Thermo Decoder): in=code[3:0]; out=therm[14:0]
- pins: input=[in,ref], output=[outp,outn], bias_control=[ibias,vbp,bias_vref,vcm_in]
- supplies: vdd2d=0.85V(Core), vddq=0.5V(DQ termination)
- signal flow: in→[EQ]→[S2D]→[VGA]→outp/outn; ref→; ibias/vbp; Rs/Cs; Therm Decoder 控制 EQ/VGA
- footer: Generated 2026-10-26, tool addHierText_labels.il, note "Drag text boxes to align with your layout."
- SKILL note 创建签名: `schCreateNoteLabel(cv x:y textStr "lowerLeft" "R0" "fixed" 0.125 "normalLabel")`

## 合成 B-档 case 设计（HierTextLabelGen-001, layout_virtuoso, L1-boundary）
- **离线可验核心**：给定 hierarchy bundle JSON（library/cell/view/title/supplies/blocks[{index,cell,inst,role,desc,inputs,outputs,params,notes,subblocks}]/pins/signal_flow/footer），生成 addHierText_labels.il SKILL 脚本（纯 ASCII，结构同 trace gold）
- SUT 交付 `hier_text_label_gen.py`（标准库），CLI `<bundle.json> [--out PATH]`/`--help`/无参 exit1/缺文件 exit1/坏 JSON exit1
- **判分静态**（L1，不真跑 Virtuoso 避免 "w" 覆盖破坏）：check.py subprocess 跑 SUT on 隐藏 B，正则解析生成的 .il 结构
- gold = hier_text_label_gen_ref.py（复刻 trace gold 结构，确定性，无运行时时间戳，用 bundle.footer.generated）
- **真实 bug 教训**：纯 ASCII（k 断言）、cross-input 守卫（m，防硬编码 A）、确定性（n）

## 失败模式（SUT 易错点）
①硬编码 A 的 dq_rx_afe/lagat_sch_hemiao1w 内容跨 B 穿（被 m 守卫拦）
②含非 ASCII（中文/Unicode 装饰）→ 被 (k) 拦（trace agent 真踩此坑）
③漏 schCreateNoteLabel / dbSave/dbClose → (d)(e)
④运行时时间戳破坏确定性 → (n)
⑤缺 subblocks/signal_flow 时崩溃 → (o)
⑥labelList 结构错（漏 block 段/漏 pin summary/漏 signal flow）→ (g)(h)(i)(j)
