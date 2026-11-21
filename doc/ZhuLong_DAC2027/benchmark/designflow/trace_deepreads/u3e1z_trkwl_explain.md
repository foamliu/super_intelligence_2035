# 深读 1795071662224_u3e1z — xavierw@hfeg0pkn002 (mc=329, schematic_netlist)

**session**: `/home/xavierw/.cline/data/sessions/1795071662224_u3e1z/1795071662224_u3e1z.messages.json` (173KB, 27 msgs, agent=lead/Aether)
**trace_source**: user=xavierw / host=hfeg0pkn002 / session_file=1795071662224_u3e1z.messages.json / match_count=329

## 真实任务（A-faithful U#12 逐字原文，analysis-Q&A）
> 现在问题解决了，给我解释一下trkWL和trkwl_BK是什么线，他要接什么？

**任务类型**: analysis-Q&A（用户已解决 20031/20068/20040 报错，请求解释 TRKWL/TRKWL_BK 信号含义与接法）。按 2026-11-15 用户令，分析问答恢复为可造档。

## session 对话流
- **U#0**: 用户贴 6 条 check&save 报错（4×Error(20031) 总线位宽不匹配 TRKWL/TRKWL_BK，2×Error(20040) D/BWEB floating），问"怎么改？我的 BWEB 和 D 和 Q 设置的一样啊？"
- **A#9**: assistant 归类报错：第一类 TRKWL/TRKWL_BK 位宽不匹配（`<*2>TIEL,<*2>TRKWL`(4bit) vs 8bit 引脚），第二类 D/BWEB floating；建议用 8-bit 总线 `TRKWL<7:0>` 接到 TIEL/VSS
- **U#10**: 用户报 Error(20068) symbol/schematic 引脚位宽不一致（Q/D/BWEB 16bit schematic vs 8bit symbol）
- **A#11**: assistant 解释 20068 = symbol 和 schematic 引脚位宽不一致，建议重新生成 symbol
- **U#12 (A-faithful 取此轮)**: "现在问题解决了，给我解释一下trkWL和trkwl_BK是什么线，他要接什么？"——用户声明问题已解决，请求解释 TRKWL/TRKWL_BK 含义与接法。**这是干净的"表达目标/提问"轮，不含根因或修复方案**。
- **A#13**: assistant 解释：
  - TRKWL = Tracking Word Line（跟踪字线）= 复制字线，走和真实 WL 一样的路径/负载，模拟字线延迟，供片内时序参考
  - TRKWL_BK = Backup Tracking Word Line（备用跟踪字线），功能本质同 TRKWL
  - 这两根线是"配置/测试(trim)引脚"，正常不参与读写，固定接死到 VDD/VSS
  - 如果跟踪关闭 → 接 VSS(TIEL)；如果开启 → 按 datasheet 接参考电平
- **U#14**: "所以这个也要跟实际wl的数量相等吗？所以要改成8吗？那为什么有4条都改成接Tiel了？"
- **A#15**: assistant 拆分 WL 数量(64) vs TRKWL 引脚位宽(8)——TRKWL 位宽 ≠ WL 个数；位宽由 symbol 定义
- **U#16**: "但我这个实际上只有8根wl啊"
- **A#17**: 如果真实 WL=8 且 TRKWL 引脚=8bit，则一一对应；接 8 位就对了
- **U#18**: "但是实际上是<*4>TIEL,<*4>TRKWL"
- **A#19**: `<*4>TIEL,<*4>TRKWL` = 4bit TIEL + 4bit TRKWL = 8bit 混合总线（一根线上有两种信号名）；正确改法是让线变成单一信号的 8 位（`<*8>TIEL`）
- **U#20**: "xtop文件是什么？"
- **A#26**: xtop = 顶层视图/cellview，和 schematic/symbol/layout 并列

## 真实资产（NFS-bound 不可沙盒）
- 工作器件: `HD1P_CXN4S1P64X16M4B2C1R1W1BW1RE1`（64×16 单口 SRAM 宏，16-bit 数据）
- 真实信号名: TRKWL, TRKWL_BK, TIEL, GIO<15:8>, D<15:0>, Q<15:0>, BWEB<15:0>
- 真实总线记号: `<*4>TIEL,<*4>TRKWL` (4+4=8bit 混合), `<*8>TIEL` (8bit 干净 tie-low)
- TRKWL/TRKWL_BK = 8-bit 引脚，各自接 8 个 TIEL（tie-low）

## synthesized-reframe 决策
真实 NFS 网表/Aether schematic 不可沙盒 → 合成 `netlist_A.sp`：
- 保留真实 cell 名 `HD1P_CXN4S1P64X16M4B2C1R1W1BW1RE1` + 真实信号名 TRKWL/TRKWL_BK/TIEL/GIO/D/Q/BWEB
- 8-bit TRKWL<7:0> / TRKWL_BK<7:0> 各接 8× TIEL（tie-low）
- 干扰信号: TRKBL<3:0>（tracking bit line，接 TIEH）+ D<15:0> 部分 bit 接 TIEH（测候选能区分 tracking vs non-tracking）
- 顶层实例 XGIO_HD1P

## hidden B 设计（与 A token 完全不相交）
- cell: `HD2P_CXN4S1P128X8M8B2C2R1W1BW1RE1`（双口 128×8 SRAM，与 A 单口 64×16 不同）
- tracking 信号: TRKDQ<3:0> / TRKDQ_BK<3:0>（DQ tracking，4-bit，与 A 的 TRKWL 8-bit 不同）
- tie: TIEH（tie-high，与 A 的 TIEL tie-low 不同）
- 实例: XRAMDP_HD2P
- 干扰: TRKCL<1:0>（tracking column line，接 TIEL）+ DIN<7:0>
- token 不相交: A-only{HD1P/TRKWL/TRKWL_BK/TIEL/XGIO/D/Q/BWEB/TRKBL/64X16} ∩ B-only{HD2P/TRKDQ/TRKDQ_BK/TIEH/XRAMDP/DIN/DOUT/BWEN/TRKCL/128X8} = ∅

## A-faithful 适用性判定
- U#12 = "提出需求/表达目标"轮（请求解释），🚫 不含根因/修复方案 → 符合 A-faithful 选轮规则
- 用户已声明"问题解决了"→ 此轮是纯求知/解释请求，非故障修复 → 干净 analysis-Q&A
