# Deep-read: sid 1787122756811_pj0ax — rscalc RTEXT + checkPoints planning

- **trace_source**: user=`e0014566`, host=`hfeg0plg58` (10.129.35.82), session_file=`1787122756811_pj0ax.messages.json`, match_count=379, domain=pg_layout.
- **file**: 1.42 MB / 384 msgs / scp 到 .75 workdir。
- **真实工具链**: pyAether/SKILL `dbOpenCellViewByType`/`dbGetTrueOverlaps` 探 layout `auto_austin_case1/BCenterDQ`；`dbCopyCellView` 拷贝到 `BCenterDQ_rscalc`；`dbCreateLabel` 打 RTEXT/RNODE；`editor` 改 `rscalc.config`；`gen_rscalc_agent.py` 生成 batch 脚本；`shell("nohup ... virtuoso -nograph -replay ...")` 跑 RsCalc 引擎。

## 用户轮（逐字原文，仅掩 key/token）
- **UI#0 (idx 0)**：『先看一下配置参数 rscalc.config, 获取到 目标 layout. 我现在要用rscalc计算电阻，看看其powernet 上的RTEXT，没有的话，帮忙在合适的位置上打上。既然不能修改原本的layout, 请先原封不动拷贝一份这个layout, 然后分析，然后打上RTEXT。另外，请在配置文件rscalc.config 中修改 checkPoints, 以计算这点的电阻。增加的量控制在50左右，分布要广泛典型。』—— **纯需求 A-档 seed 候选**（只给目标，未给根因/修复）。
- **UI#1 (idx 104)**：『不用真正打上RNODE，直接用checkPoints 表示RNODE就可以了。』—— 改交付形态：checkPoints 代替物理 RNODE。
- **UI#2 (idx 109)**：『好的，来吧，计算电阻吧，并且生成电阻分布报告。』—— 触发真跑 RsCalc。
- **UI#3 (idx 173)**：『自主排查下你发现的这些问题，看看RTEXT打得是否合理，以及powernet自动检测得是否合理？不合理的修改掉吧。』—— 触发自审。
- **UI#4-6 (idx 307-312)**：报告去修正前内容 / 英文无乱码 / 保存文档。
- **UI#7+ (idx 328-362)**：meta——总结 RTEXT+checkPoints skill、问 memory 不够原因、问一次性跑通。**末轮是 meta 提问，非单一产物接受。**

## 真实产物与事实
- 顶层 `BCenterDQ` bBox `(686.41,-736.146)-(16556.28,740.04)`，4537 shape / 22 label（全 signal pad M1/pin）/ 63 inst，RTEXT=0 RNODE=0。
- power net 名来自子 cell `BCenterDQ_interface`：`vdd1!`(M4+M5 label)、`vss!`(M4 label，**M5 无 label**)、`vcc!`(M4+M5 label)。
- power stripe（dbGetTrueOverlaps 扫描确认）：
  - `vdd1!` M5 @ y=-265，x=3000..14000（M4/M3 也有）；
  - `vss!` M4 @ y=393，x=4000..14000（M5 该 y 有金属但**非 vss! 网络**——核心坑）；
  - `vcc!` M4 @ y=116，x=3000..14000。
- agent 流程：拷贝→打 3 RTEXT + 50 RNODE→改 config(cellName/pwrNets/checkPoints)→UI#1 删 RNODE 留 3 RTEXT→跑 RsCalc→UI#3 自审发现 **vss! RTEXT 错打 M5**（M5 上 vss! 无 label→不出数）→改 M4 + vss! checkPoints 改 M4/M3→重跑出数（vdd1! IR drop 1.69→25.46Ω，vcc!/vss! 出数）。

## A-档 vs B-档判定
- UI#0 是纯需求 seed，但末轮是 meta skill 总结提问，**无单一 byte-faithful 被用户干净接受的最终产物**（多轮迭代 + 报告 + skill 总结）→ **A-档 disqualified → B-档 synthesized**。
- 真 L2（真跑 Virtuoso + RsCalc + OA）沙盒不可复现 → **L1-boundary**。

## 合成 gold 核心难度
1. **primary_layer = topmost(label_layers)**，**不是** topmost(metal_layers)——vss!-on-M5 是陷阱（metal 有 M5 但 label 只在 M4）。
2. RTEXT 每 net 1 个 @ (pad_x, stripe_y) on primary_layer。
3. checkPoints ~target 总数，按 x-span 按比例分到各 net，[x_start,x_end] 内 midpoint 均匀铺开，全在 primary_layer。
4. rscalc.config 三处 patch（cellName→`<cell>_rscalc`、pwrNets→net 名空格连、checkPoints 行→SKILL list），其余参数保留。

## 与既有区别
- RNodePlan-001 (r42, 9cg75)：RNODE label 放置计划 JSON（RDL-only、range-aware count、不打 via-stack / 内部金属 / 信号 net）。
- 本案 (RTextChkPlan-001)：**RTEXT（1/net on primary label layer）+ checkPoints 配置生成（x 均匀分布）+ rscalc.config patch**；核心坑是「label_layers vs metal_layers 选层」（vss!-on-M5），主题/断言与 RNodePlan 完全独立。
