# 深读笔记 · 1793326498040_6ftap · irene1li@hfeg0pkn004 · spice_sim · 2026-11-07 19:1x

## Trace 概要
- **用户**: irene1li @ hfeg0pkn004 (10.129.2.13)
- **Session**: 1793326498040_6ftap, 360 msgs, 178 tool_use, 1.27MB
- **工具分布**: netlist:642, schematic:411, hspice:373, calibre:17 (spice=373, total=1446, ratio=0.258)
- **时间窗**: 2026-10-29~10-30 (updated_at: 2026-10-30T01:39)

## 用户意图（逐字原文 · A-档）
- msg1-2: 介绍 .sp 文件（finesim 仿真激励, option/param/.inc netlist 分段）
- **msg3 (核心需求)**: "我需要你帮忙仿真迭代出一版符合要求trtf的主体电路（包括P2S主体电路+P2SDRV+predrv（包括zqcode、AC和FFE支路））"
- msg4-5: "ss 0.82 110 trtf也可能会是最大的" + "我关心主体电路所有管子的trtf duty"
- msg6: "trtf取的是10%-90%"
- **判断**: CLEAN A-档 ✓（纯需求轮，给目标"仿真迭代出符合trtf的主体电路"，未给根因/修复）

## 电路结构（用户描述）
- P2S 主体电路: 4to2to1 并转串
- P2S drv → predrv(4级) → finaldrv(大尺寸)
- PU 4级示例: DqPuDin_STG1 → DqPu → pudrv_stg3<2:0> → PuMain<2:0>
- zqcode 支路 + FFE/AC boost 支路（预加重优化眼图）

## Assistant 解决方案
1. 复制 test_dout.sp 到 /home/irene1li/AI_test/m2701_tx/
2. 用 LSF 提交 finesim 仿真（7 corner: tt25/ss110/ssm40/ff110/ffm40/fsm40/sfm40）
3. 产 FSDB 波形后用 **_measure_allmain.py** (5857B) 计算:
   - 44 节点的 tr/tf(10%-90%) + duty
   - 用 fscript 读 FSDB → mid-crossing 算法 → tr/tf
   - 节点覆盖 PU/PD data path(stg1→stg3→main) + zqcode + AC boost + FFE/pre
4. 分析脚本: _analyze_dq.py, _analyze_puduty.py, _analyze_skew.py

## Case 合成
- **ID**: EDA-Eval-DesignFlow-TrtfMeasDeckGen-001
- **Domain**: spice_sim, **Track**: A-faithful, **Level**: L1
- **交付**: gen_trtf_meas.py <input.sp> <nodes_file> <outdir> → _meas.sp + parse_trtf.py + report.md
- **A**: 真实 test_dout.sp (12.5KB, 7 corner, 251行) + nodes.txt (44 节点)
- **hidden B**: test_dout_B.sp (FIN=4G, .tran 2p 20n, 5 corner, 不同 VVDD/zqcode) + nodes_B.txt (30 节点 tx_* 命名)
- **check.py**: 12 条断言 (a-l), 自验 ref PASS + 3 negative FAIL + §4.9 三假 FAIL
- **根因/金标准**: 原 deck 无 .measure → 需添加 tr/tf(10%-90%)+duty 的 .measure 语句 + .lis 解析器
