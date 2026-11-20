# trace_deepread — 1793596317022_34b72 (chapinc @ hfeg0pkn002, spice_sim, mc=14)

## 来源
- session: `1793596317022_34b72` on `hfeg0pkn002` (10.129.2.11), user `chapinc`
- snapshot: `ssh_eda_search_20261105_192825/summary.tsv` (11-05 19:28)
- **发现路径**: 11-05 19:2x 重扫令履行 → spice 主导过滤重建（override 口径 spice≥10 ∧ ratio≥0.35，**无 mc 下限**）→ 11-05 snapshot 141 spice-dom rows / 81 mc≥30 全在 ledger / **37 not-in-ledger mc<30** → 本轮 scout 9 个 mc<30 候选（wbge3/mwijd/p8wm1/8fe71/zt2xq/9pm1x/z8zli/ne32u/34b72）→ 仅 **34b72 clean A-档**（余皆 trivial/GUI启动/脚本分析/skill编写）
- 文件结构: `<id>/` 目录含 `<id>.messages.json`(99KB,compact续) + `<id>.messages.archive.json`(2.3MB,137msgs,原始历史) + `<id>.json`(3.4KB,元数据)

## USER#0（逐字原文，A-档任务说明）
> 读取/home/chapinc/AIforstdcell/netlist_sp这个文件夹里面的netlist和.sp文件，我现在要做一个stdcell尺寸选取的.HTML网页链接。界面高科技并且清新一点，用户可以选择model以及要看的管子尺寸、以及一些IDDQ DUTY的值等等。你要以这些网表激励为模板自动修改里面的参数并且自动提交仿真。主要就是选取L W PNratio，具体怎么选择一步步来为跟你说。以上是任务大纲，并且自动提交仿真的代码在历史会话里已经生成过来，你可以在工作目录查看。现在你一步步问我问题逐渐进行任务。先不着急生成网页链接

**A-档判据**: 纯需求/目标轮 ✓（给目标=stdcell尺寸选取web应用 + 方法=网表模板自动改参数提交仿真 + 选 L/W/PNratio；🚫 未给根因/未给修复方案）

## trace 工具链
- tools 字段: netlist:660 hspice:438 pdk:79 .lef:57 synopsys:42 mosfet:9 skipper:8 verilog:4（archive, sp=354）
- agent: glm-5.3-flash (cxmt-glm)
- 大纲: 读 netlist_sp 模板 → 问用户参数(model/Wmin/Lmin/corner) → engine.py 改 .para/.tran sweep → LSF bsub hspice → 解析 mt0 → Flask web 5-corner 分图

## 资产（真实 attachments）
- `/home/chapinc/AIforstdcell/netlist_sp/`: IDDA.sp(2806B) / IDDQ.sp(2929B) / duty.sp(3251B) / trtf.sp(3808B) + 各自 _netlist
- 模板结构: `.option` + `.lib top_tt/pre_simu`(HL22 PDK) + `.temp 25` + `.para`(gvss0/gvcc0/Cthin/Cthick/CapO/Cgatein/PN_ratio/l0/Wn_Mult/Wn_basic) + `.include <netlist>` + stimulus + `.tran <step> <tstop> sweep <param> <start> <stop> <step>` + `.meas` + 4×`.alter`(top_ff/-40, top_ff/110, top_ss/-40, top_ss/110, 各改 gvcc0=0.96/0.72) + `.END`
- 参数修改规则（trace compact summary 明列）: 非 sweep 参数改 `.para NAME=` 值(set_para)；sweep 参数改 `.tran ... sweep` 行；.lib 行简化(贴一行 tt → 推导 ff/ss，top_tt→top_ff/top_ss)

## case 合成（交付范围收敛）
- **金标准 = trace 中 user 接受的 deck 参数修改引擎**（engine.py 核心组件，USER#0 明列「以网表激励为模板自动修改里面的参数」）
- case: `EDA-Eval-DesignFlow-StdcellDeckParamModify-001` (spice_sim A-faithful L1)
- 交付: 通用 `modify_deck.py <template.sp> <config.json> <output.sp>`
- A: IDDA.sp + config_A.json(sweep l0 30-100 step5, PN_ratio=17/14, Wn_basic=120)
- hidden B: duty.sp + config_B.json(sweep PN_ratio 1-4 step0.1, Wn_basic=200, l0=50, Wn_Mult=2) — A≠B(不同模板/不同 sweep 参数/不同量级)✓
- reference: modify_deck_ref.py + check.py **k=12 断言 a-l** + 5 negative(naive_empty/print_only/hardcode_B/copy_only/core_cut) + negative_selftest.py + reference_submit.zip
- 自验: REF PASS 12/12 + 5 neg 全 FAIL + §4.9 empty-zip/print-only/core-cut 三假 FAIL = SELFTEST PASS
- 断言闸门: k_rationale=12 == k_check=12 ≥8 ✓
