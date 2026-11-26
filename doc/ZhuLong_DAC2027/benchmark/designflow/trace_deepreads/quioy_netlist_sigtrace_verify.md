# Deepread: 1794192133796_quioy — NetlistSigTraceVerify-001

- trace: `1794192133796_quioy.messages.json` · daiweilu@hfhds209 · mc=102 · 355KB · 54 msgs · 28 user-role (1 真实用户输入 @idx0，余为 tool_result)
- shard B · domain spice_sim · track synthesized · level L1
- ledger: claimed → case(EDA-Eval-DesignFlow-NetlistSigTraceVerify-001)

## A-faithful 用户轮 (U#0, idx0)
```
我要验证cm1_ag_VkbSenseAddActBiasEn这个testmode，这是我的网表
/proj/ddgoa/V0/simdir/verilog/daiweilu/verilog.lpddr5.ddgoa.1106/netlist/，要求是
1. 功能描述: VkbSense add active bias current
2. 细节解释: 0：default（do not add bias current）; 1：add 2*glbbias current
我该如何验证
```
纯需求陈述，未给根因/修复 → A-faithful eligible。

## assistant 解法 (gold)
- 写 `search_netlist.py`：读 Verilog 网表，按 `module...endmodule` 归属每条命中行的 enclosing module，搜目标信号（大小写不敏感），输出 `{"target","total","occurrences":[{"line","module","text"}],"modules_found","num_modules"}`。7 个 editor 版本（内容在 `new_text` 键，非 `content`）。
- 最终验证指南：信号路径 ChanEdgeL→CmLeft→VkbSenseIP→VncsgnSenseCompHysIP，MPSW5 PMOS 开关，ActHBiasN 逻辑。

## Case 重构
- case id: `EDA-Eval-DesignFlow-NetlistSigTraceVerify-001`
- 资产 A: `netlist_A.v`（testmode cm1_ag_VkbSenseAddActBiasEn，模块链 CmLeft/VkbSenseIPA/VkbSenseLogicA/VncsgnSenseCompHysA/PumpSenseA/AnalogChEdgeA/ChanEdge/testbench_top）
- 隐藏 B: `hidden/netlist_B.v`（testmode cm1_ag_XkbSenseAddSbyBiasEn，全部模块/信号名不同：CmRight/VSenseIpX/VSenseLogicX/VSenseCompHysX/PumpSenseX/AnaRefEdgeX/AnaChEdgeX/ChanEdgeX/tb_x）
- ref: `trace_signal_ref.py`（25 occ / 8 modules on B）
- check.py: 15 独立断言 a–o（hidden B 存在 / zip 含脚本 / exit0+stdout / 合法JSON / list 字段 / ≥20 occ / ≥7 modules / CmRight·VSenseLogicX·ChanEdgeX·VSenseIpX 在 / occurrence 字段类型+行范围 / 反硬编码 A 名不泄漏 / 大小写不敏感 ≥20）
- 自测：ref PASS · 3 neg(naive_empty/hardcoded_a/no_module_ctx) 全 FAIL · §4.9 三假提交(empty/print-expected/ref-minus-core) 全 FAIL
- k_check==k_rationale==15 (≥8 gate)

## 关键发现 (推翻前轮结论)
前轮"spice mc≥30 池 ledgered 尽 / 0 candidate / WAITING:1"基于**后缀 mismatch bug**：ledger 部分 sid 带 `.messages.json` 后缀，pool sid 已归一化，未归一化直接 diff 误判全已 ledgered。归一化后：969 unique spice mc≥30 sid 中仅 323 在 ledger → **532 真未 ledgered**（存 `unledgered_spice_mc30_v2.txt`）。本轮从中 claim quioy 交付，下轮仍有大量候选。
