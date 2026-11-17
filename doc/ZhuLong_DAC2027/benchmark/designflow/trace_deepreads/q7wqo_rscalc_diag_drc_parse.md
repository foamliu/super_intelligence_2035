# Deepread — q7wqo → RscalcDiagDrcRuleParse-001

## trace

- session: `1793861805853_q7wqo`
- user: `t0002062` @ `hfeg0pkn004` (10.129.2.13 cluster)
- mc: 34 (lvs:353 / drc:227 / netlist:149 / calibre:121 / aether:61 / .spi:7)
- model: deepseek-v4-flash (cxmt-deepseek-flash provider)
- 17 messages (9 user / 8 assistant), 2026-11-05 ~ 11-16
- agent policy-engine enforcing; run_commands DISABLED (use run_approved_command)
- terminal_marker: failed_external_process_exit (stale_session_reconciler)

## 3 intents

### U#1: rscalc 失败诊断（主意图）

逐字：「为什么Run rscalc 失败」+ 附件 `rscalc.log`（848KB / 17669 行）

附件 log 关键内容（真实）：
- `Job <1654174> is submitted to queue <rscalc>`
- `*****run rsbuild*****` → `rsbuild rsb.target | tee rsb.log`
- `!!!WARNING<parameter>[0002] The layer is not found (7230,layer = METAL3)` ×3
- `!!!WARNING<parameter>[0002] The layer is not found (4708,layer = METAL3)` ×1
- `!!!ERROR<parameter>[0153] Pad text is not specified (5302)`
- `*****run rsnodeinfo*****` → `tee: RSDB_vsszColCtrl/rsnodeinfo.log: No such file or directory`
- `!!!ERROR<base>[0102] Failed to open file (101,List File:RSDB_vsszColCtrl/vsszColCtrl.rvn)`
- `!!!ERROR<main>[0050] Failed to write nodelist file (588,status:-1 nodelistfile:RSDB_vsszColCtrl/vsszColCtrl.lis)`

assistant U#3 诊断（run_commands 被禁用，纯静态读 log）：
- 根因：rsb.param 中 pad text 未指定（错误码 5302）
- METAL3 层（GDS 7230/4708）在 tech file 中未定义（warning）
- 下游 rsnodeinfo 因 RSDB 未构建而失败（downstream）

### U#4: argusdrc GUI 排障

逐字：「我的argusdrc界面唤不起来怎么办」

assistant 调 `skills` → argus-tool-helper skill（39 条 ARGUS 排障条目），读 5 个 reference md 文件，输出 6 类排查指南：license / DISPLAY / DRC 结果卡 / queue pending / 工具闪退 / 速查表。

### U#12/U#13: SVRF DRC rule 解释

逐字粘贴完整 SVRF rule：
```
AT4_W_000_02
RULE AT4_W_000_02 {
; Min- AT4 width [ 0.2 ]
; DRC measure the separation between the interior sides of two AT4 edges , both edges to other AT4 space meet condition: space >1.0um.
A0 = copy ( AT4 )
A1 = space (  ( A0 )  <= 1  adjacent < 90  point_touch )
width (  A1 < _AT4_W_000_02_ adjacent < 90  region )
A2 = width (  ( A0 )  < _AT4_W_000_02_ adjacent < 90  )
A3 = geom_with_edge ( A0 A2 )
A4 = space (  A0 < _AT4_W_000_02_ adjacent < 90  point_touch region )
A5 = ~geom_interact (  A3 A4 )
geom_interact (  A5 geom_not (  geom_edge_to_rect ( A2 inside _AT4_W_000_02_ ) A0 ) )
}
```
问「这是什么意思」

assistant 解释：Calibre/Argus SVRF DRC rule，检查 AT4 层最小宽度 0.2μm，但只报孤立区域（space>1.0μm）的窄 AT4，密集区域放过。逐行解读 A0-A5 操作序列 + 两层过滤逻辑 + 报错场景 + 修复方法。

## reframe（mock-behavioral，纯 stdlib）

承 r645-r702 mock-behavioral 家族。**新子型 `rscalc-log-diag-drc-rule-parse`**：
- rscalc.log ERROR/WARNING 正则解析 + failed-stage 定位（`*****run <stage>*****` 标记）+ root-cause 分类
- SVRF DRC rule deck 结构化解析（rule name / 约束类型 / 约束值 / 主层 / 操作序列）
- distinct vs r690 DrcVarMisMatchDiag / r697 PgDummyFillFlowOrganize / r698 ErcRulecheckStatsScan / r700 PexCharConfigReview

## case 设计

- **candidate**: `rscalc_diag_drc_parse.py`（纯 stdlib，regex 解析 + JSON sort_keys 确定性）
- **A**（visible）: rscalc_log_A.txt（3 ERROR @ rsbuild，4 WARNING METAL3）+ drc_rules_A.svrf（3 rules，rule0=AT4_W_000_02 width/AT4/0.2 op_count=8）
- **B**（hidden，反 A）: rscalc_log.txt（2 ERROR @ rsext，2 WARNING METAL5）+ drc_rules.svrf（4 rules，rule0=M5_W_0010 width/M5/0.25 op_count=5）
- **B2**（hidden，边角 + 反 B）: rscalc_log.txt（0 ERROR / 0 WARNING，rsbuild+rsnodeinfo 均成功）+ drc_rules.svrf（2 rules，rule0=GT_W_0050 width/GT/0.3 op_count=3）
- **check.py**: 19 条件 a-s
- **4 negatives**: empty_shell→c / only_print_A→e / always_clean_log→e / ignore_svrf_rules→l（3 distinct first-fail tags）

## 自验

- gold PASS on B+B2 (19/19) ✓
- gold on A parses correctly (3 errors, rsbuild, AT4_W_000_02, parameter_missing) ✓
- 4 negatives all FAIL, 3 distinct first-fail tags (c, e, l) ✓
- §4.9 three-fake (empty / only-print-A / delete-core) all FAIL (a, e, e) ✓
- determinism 2x md5 e2d18c1ee07d3c3bcc90e64b083f7f93 一致 ✓
- jsonl test round-trip PASS ✓
- k_rationale == k_check == 19 ≥ 8 GATE PASS ✓
- anti-hardcode: A∩B∩B2 failed_stage / error_count / warning_count / primary_error_code / primary_error_message / classification / rule_count / rule[0].name / layer / constraint_value / op_count 全 disjoint ✓
