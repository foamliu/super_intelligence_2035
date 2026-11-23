# r1088 0-case stop-loss 侦察轮（14:20-14:50）

## 候选选取
从 fresh_b_spice_local.tsv（141 行）中取 3 个 **cross-4-shard ledger 真正 NONE** 的候选：
- yd89p (joeyl@hfeg0pkn004/mc196/370msgs)
- qsn6y (joeyl@hfeg0pkn004/mc23/52msgs)
- 1wvdl (e02141@hfeg0pkn005/mc704/617msgs)

其余 top-mc 候选已在台账：o7ljl(case C2cCornerAmplifierAudit-001)、22w7w(parked r1031)、1d03e(parked r1031)、bp1x8(parked r1087)。

## .75 访问
eda_flow session(agentB_designflow-loopB-20261123_shardB-peek-r1088_0) open+ssh 通 hfeg0pkn005(e02141) + hfeg0pkn004(joeyl snapshot)。
scan 仍 ssh_eda_search_20261123_064315，无 1123 全量 scan。

## peek 结果

### yd89p (joeyl@hfeg0pkn004/mc196/370msgs) — CROSS-SHARD D 已占 + near-dup
- **trace**: U0 要求调节 WCKTOP testbench 前三级 CML 电路，5corner 下正常放大，可调电阻 length/bias管/输入管 width/finger。joeyl WCKTOP CML 5corner 项目。
- **跨 shard**: claim 时 REFUSED → **shard D status=deepread**（2026-11-19）。非 B 可用。
- **near-dup**: 同 joeyl WCKTOP CML 5corner 起振 tuning = parked 22w7w(r1031) + o7ljl(C2cCornerAmplifierAudit-001) 同主题。且 r1031 note "needs real finesim non-portable"（真跑 FineSim 验证，离线不可复刻）。
- **结论**: 不选（cross-shard D + near-dup + non-portable）。

### qsn6y (joeyl@hfeg0pkn004/mc23/52msgs) — CROSS-SHARD D 已 case + near-dup
- **trace**: U0 要求写脚本为 netlist 中 pulvt_ckt/nulvt_ckt 减小 vth，在行尾加 `_delvto=-0.2`，用 cfg 文件选 netlist 路径和 vth 值。
- **跨 shard**: claim 时 REFUSED → **shard D status=case, case_id=EDA-Eval-DesignFlow-UlvtDelvtoReducer-001**（2026-11-13）。**已经是 D 的 case！**
- **near-dup**: verbatim 同 DelvtoNetlistModifier-001 + r1086 parked 12-slug joeyl delvto 族（9t9um/gn43h/dq5p2/...）。
- **结论**: 不选（cross-shard D 已 case + near-dup）。

### 1wvdl (e02141@hfeg0pkn005/mc704/617msgs) — OUT-OF-DOMAIN
- **trace**: U0 要求研究 Sentaurus TCAD deck 示例（/apps/synopsys/sentaurus/V-2023.12/.../Applications_Library），总结新 deck setup 所需常见文件。后续 617 msgs 全是 Sentaurus 学习/mentor 会话：学 TCL 规则、读手册、debug GAA_FET deck、配 swb-python-api、加 sdevice/svisual 工具、导 CSV、学 25 课 GettingStarted 示例、存讲义到 reference-lessons/、最后 "从零 setup 一个 DRAM"（未完成）。
- **domain**: **Sentaurus TCAD**（sprocess/sdevice/svisual/swb/sde/snmesh），非 SPICE 电路仿真、非 characterization。scan 关键词匹 "simulator" 但实际是 TCAD device simulation。**不属于 shard B (spice_sim/characterization)**，应归 eda_other (shard A) 或 TCAD 专属。
- **viability**: 长 mentor 会话（40+ "继续"消息），交付物是 lesson notes（markdown 讲义），无可 subprocess 执行的脚本交付件，check() 难有牙。最后 "setup DRAM" 未完成。
- **结论**: 不选（out-of-domain + not viable）。

## 3 候选全不选
- 0 新 claim/mark（yd89p/qsn6y cross-shard D 拒绝，1wvdl out-of-domain 不 park 归他 shard）
- B cases 数不变

## 指标
- 📊 trace 覆盖率: covered=566/target=4398=12.9% (mc≥10, 不变)
- 🎯 通过率: 最近20条 20/20=100% (观察值)
- DEBT: 1 (r1057 campaign「55 legacy B 缺 selftest」余 53, 51 缺独立 reference 目录)

## fresh 池状态
fresh_b_spice_local.tsv 的 cross-shard dedup **已过期**：yd89p/qsn6y 在 shard D 台账但 B 的 fresh list 仍标 fresh。真正 cross-4-shard NONE 且 in-domain 的 B 候选已耗尽。需新 scan 刷新 fresh 池 + cross-shard dedup。

## 下一步
- 等新 scan（ssh_eda_search_20261123_064315 之后）
- 或对 fresh 池剩余低 mc 候选深 peek（但 yd89p/qsn6y 已证 cross-shard 占据，剩余大概率同样）
- §4.9 selftest campaign 已收口（2/55 可补的已补，51 缺独立 reference 目录另议）
