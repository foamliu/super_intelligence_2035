# 深读 1794469889494_pr2uh — chapinc@hfeg0pkn002 (mc=1186, schematic_netlist)

**session**: `/home/chapinc/.cline/data/sessions/1794469889494_pr2uh/1794469889494_pr2uh.messages.json` (~? KB, 仅含用户单条提问, assistant 从未回复, session 弃用)
**扫描 kw**: schematic/netlist 域 dominant (mc=1186, 具体细分待 trace scp 落地后回填, 工作目录 `/home/chapinc/agentdir/degnt/V0_CMOS` 强 schematic_netlist 信号)

## 真实任务（U#0 逐字原文，analysis-Q&A）
> Count the type and name of the MOSFET used in the RWCbusGap_channelMid block, its size (W and L), and the voltage range it is in, as well as which lib library it comes from

**任务类型**: analysis-Q&A（用户对已存在网表提问统计性信息，不是 produce）。按 2026-11-15 用户令，分析问答/doc-search/debug-Q&A 恢复为可造档。

## session 特征
- **唯一一条 user turn**，assistant 未响应。但提问本身清晰、信息完整（块名 RWCbusGap_channelMid + 4 维度 type/name/W,L/voltage/lib），是干净的 A-faithful analysis-Q&A 意图。
- **无需深读 assistant 答案**（不存在），意图本身就构成可造的 case prompt。
- **trace_source 字段**记 `user=chapinc / host=hfeg0pkn002 / session_file=1794469889494_pr2uh.messages.json / match_count=1186`。

## 真实资产
- 工作目录 `/home/chapinc/agentdir/degnt/V0_CMOS`，NFS 属性 chapinc 私有不可沙盒复用。
- 真实块名 `RWCbusGap_channelMid`（出现在网表 `.subckt`/`.ends` 段），真实库族 `c18a_hfs`（1.2V core）/`c18a_hfs33`（3.3V I/O），真实器件名 `MRwc0..3`（命名约定 M+Rwc 前缀）。
- voltage 域后缀规则真实：`c18a_hfs`→1.2V（无后缀），`c18a_hfs33`→3.3V（含 33），`c18a_hfs50`→5.0V（含 50，未在此 session 出现但同族一致）。

## synthesized-reframe 决策
真实 NFS 网表不可沙盒 → 合成 `netlist_A.sp`：
- 保留真实块名 `RWCbusGap_channelMid` + 真实库族 `c18a_hfs`/`c18a_hfs33` + 真实器件名 `MRwc0..3`（4 MOSFET，2 PMOS+2 NMOS，2 电压域 1.2V+3.3V）
- 加 2 干扰块 `RWCbusGap_channelTop`（2 MOSFET）/`RWCbusGap_channelBot`（1 MOSFET），测候选块定位准确性而非粗暴全表扫
- 顶层 3 个 `XRwcTop/XRwcMid/XRwcBot` 实例化，干扰候选把顶层实例错当 MOSFET

## hidden B 设计（与 A 完全 token 不相交）
- 块名 `LdoBiasGen_topMid`（Ldo 前缀，与 Rwc 不相交）
- 库族 `c18d_hfs`（1.2V）/`c18d_hfs50`（5.0V，换 5.0V 测后缀 50 分支）
- 器件名 `MLdo0..4`（5 MOSFET，3 PMOS+2 NMOS，2 电压域 1.2V+5.0V）
- 干扰块 `LdoBiasGen_topTop`/`LdoBiasGen_topBot`
- A-only 11 token：`RWCbusGap_channelMid`/`MRwc0..3`/`nch_hfs`/`pch_hfs`/`nch_hfs33`/`pch_hfs33`/`c18a_hfs`/`c18a_hfs33`
- B-only 12 token：`LdoBiasGen_topMid`/`MLdo0..4`/`nch_dfh`/`pch_dfh`/`nch_dfh50`/`pch_dfh50`/`c18d_hfs`/`c18d_hfs50`
- 两个集合完全不相交（A-only 集合 ∩ B-only 集合 = ∅）

## case 关键属性
- **case_id**: `EDA-Eval-DesignFlow-MosfetBlockInventoryQA-001`
- **task_id**: `MosfetBlockInventoryQA-001`
- **domain**: `schematic_netlist`
- **grade**: `B synthesized`（A-faithful 意图 + synthesized-reframe 资产，因 assistant 无答案无法做纯 A 档）
- **track**: `synthesized`
- **level**: `L1`（通用脚本，离线验证）
- **k_check = k_rationale = 17** (a-q)
- **check_sha256**: `e6db4562695a0e79602499a694efd3298688b81d95c4e834e4392a09a69275fc`
- **check_size**: `12153`
- **D.jsonl**: 556 → 557

## 17 条断言（a-q）
1. **a** zip 合法含 ≥1 mosfet*.py
2. **b** py_compile 通过
3. **c** 反空壳 src≥600B
4. **d** B 运行 exit0 + JSON≥100B
5. **e** JSON 含 block/mosfets/summary 顶层键
6. **f** block==LdoBiasGen_topMid（取自 manifest 不硬编码）
7. **g** count==5（_gt 独立重解析）
8. **h** names 集合==_gt {MLdo0..4}
9. **i** types==_gt model→type 映射（不猜模型名）
10. **j** W==_gt W 抽取
11. **k** L==_gt L 抽取
12. **l** voltage==_gt lib 后缀推导
13. **m** lib==_gt model→lib 映射
14. **n** 反硬编码-1：A-only token 零泄漏
15. **o** 反硬编码-2：B-only token 全出现
16. **p** 3-seed md5 确定性
17. **q** A-gold 交叉校验（喂 netlist_A+RWCbusGap_channelMid 必须出 A 金标 count=4/names={MRwc0..3}/types 匹配；专门击败 B-only 硬编码）

## §4.9 / neg 自验
- reference_submit.zip（mosfet_block_inventory.py 来自 reference produce-script）→ 17/17 PASS ✓
- fake_empty.py → FAIL (c)
- fake_print_only.py（B-only 硬编码，无视输入直接打 B 答案）→ FAIL (q) — 由条件 q 专门捕获
- fake_core_deleted.py（实现核心被删，只留 shell）→ FAIL
- §4.9 (a)(b)(c) 三假全 FAIL ✓
- NEG_RC=ALL FAIL ✓
- k_check=k_rationale=17≥8 GATE PASS ✓

## 选料 & infra 备注
- 选料: 从 `/home/t0002965/log/ssh_eda_search_20261121_005100/summary.tsv` D-pure fresh 候选池排除 4885-entry touched union 后选 pr2uh（chapinc@hfeg0pkn002 mc=1186，单 user 干净无 sister-turn 风险）
- infra: eda_flow MCP open_session ok；ssh .75:22 timed out 须走 fleet 跳板（与 r1044 一致）
- ledger: pr2uh 已 claim→mark case ✓
- DEBT: discuss 配额 next due r1050（r1045+3 more case rounds r1046/r1047/r1048/r1049）；PUSH-BLOCKED 待 infra 恢复

## flag
- r1046 = `mosfet-block-inventory-qa` 子型（D 域首例 schematic_netlist **analysis-Q&A** 类，区别于 r1040 NetlistPortMismatchDiagProduce 诊断类/r1041 SramNetlistStructAuditProduce 审计类：本例做块内 MOSFET 器件清单**问答**而非**审计/诊断**）
- A-faithful U#0 逐字 + synthesized-reframe（真实 NFS 网表→紧凑 SPICE fixture 保留真实块名/库族/器件名）+ 合成 hidden B（Ldo*/c18d_hfs* 全 token 不相交）+ 独立 _gt 重解析（check.py 与候选不同实现互验，强 anti-echo）+ 条件 q A-gold 交叉校验专门击败 B-only 硬编码（§4.9(b) 修复点）
