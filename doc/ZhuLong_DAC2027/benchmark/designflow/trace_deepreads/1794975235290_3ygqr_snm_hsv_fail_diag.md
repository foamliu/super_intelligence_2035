# Deepread · 1794975235290_3ygqr · Solido HSV SNM fail-diag

- **trace**: e0030760 @ hfeg0pkn001 (10.129.2.10), session 1794975235290_3ygqr, 167 msgs, 613KB
- **match_count**: 155 (hspice:329 dominant, spice tool share 2089/4144=0.50)
- **domain**: spice_sim (真 B 域), NEW-user (全 4-shard ledger 0 记录)
- **变现**: r872 → EDA-Eval-DesignFlow-SnmHsvFailDiag-001

## 真任务
Solido Variation Designer High-Sigma Verification (HSV) 做 DDR SRAM Static Noise Margin
(SNM) 分析。`/proj/lacaa/V0/workdir/e0039809/solido/CH252_Single_Bitcell_fix/results` 下
HSV-7 及之后的 high sigma 分析**一直在边界点取不到点**，RSNM 测量对全部样本判 failed 后被
Solido drop ("Output RSNM has failed for quite awhile, ignoring going forward")。

## 根因 (trace msg95-98 + msg166 终态诊断)
testbench.sp 中 `*.Print DC V(Q_HNM)` 和 `*.Print DC V(QB_HNM)` 两行被 `*` 注释掉，
但 `solido_snm_custom_output.py` 声明 `NODES=("q_rnm","qb_rnm","q_hnm","qb_hnm")` 期望 4 张
DC sweep table；hspice stdout 只有 q_rnm/qb_rnm 两张表 → custom_output.py 打印
"ERROR: DC sweep tables ... not found" 并 `sys.exit(1)` → `solido_parameters.out0` 不生成 →
Solido 每样本 RSNM 判 failed → drop。

修复 = 取消注释两行 `.Print DC V(Q_HNM)` / `.Print DC V(QB_HNM)`，使 NODES 与 active print
对齐。

## 关键 trace 节点
- msg10 用户原话：HSV-7 之后 high sigma 一直在边界点取不到点
- msg95-98: agent 读 testbench.sp，发现 Q_HNM/QB_HNM 的 .Print 行被 `*` 注释
- custom_output.py verbatim: `NODES=("q_rnm","qb_rnm","q_hnm","qb_hnm")` + "ERROR: DC sweep
  tables ... not found" + `sys.exit(1)`
- msg166: 终态诊断 "Output RSNM has failed for quite awhile, ignoring going forward" /
  "Dropped aim"

## reframe (harness-for-teeth 第十三实证)
Q&A/diag → produce 参数化诊断工具 `solido_hsv_diag.py` (--run-dir/--out)，纯 python 解析
testbench.sp + custom_output.py + simulator_stdout.log + full_summary.txt，判
root_cause_category ∈ {commented_print_lines / nodes_misalignment / missing_dc_tables /
unknown}，输出 11 字段 diag_report.json。无 EDA 二进制 → layer=L1。

## asset 重建 (format-faithful, 权限拒访第七实证)
/proj/lacaa/V0/workdir/e0039809 对 ssh 10.129.2.10 permission-denied (仅 lead-as-e0039809
可读)。按 trace verbatim 重建：testbench.sp .Print 注释行 / custom_output.py NODES+exit(1) /
simulator_stdout.log Hspice DC table 格式 / full_summary.txt "Output RSNM has failed" +
"Dropped aim"。

## hidden 设计
- B (CH180 6T, HSV-22): HSNM fails, q_rnm/qb_rnm commented (5 维度差异 vs A CH252/HSV-15/
  RSNM/q_hnm/61samples)
- B2 (CH220 8T, HSV-31) anti-stub: 两 .Print 全生效 (无注释行)，但 NODES 期望 q_hnm_alt 与
  testbench 打印 q_hnm 不一致 → root_cause=nodes_misalignment。只查注释行的 stub 误判 B2 →
  check (k) 断言抓此 stub。这是本 case 的关键 discriminator。

## check
k_check=k_rationale=14(a-m); ref 14/14 PASS; §4.9 5 neg (empty_shell/print_only/hardcode_a/
core_deleted/only_count) 全 FAIL NEG_RC=5/5; 3-seed 确定性 ✓
check.py sha256 = 2a05c36a296d51ed4b1bb4231db41d096bf81627352c137f525806985f485edc

## 选料防 dup
- q3y71: parked dup of Mt0FolderAggStat/Mt0AggMinMax (非 fresh) → 弃
- r06g9: 已 case RonMonoDiag-001 → 弃
- 2xqbx: sibling dup of IbisZqCalibMerge-001 (同 user joeyl 同 ZQ 任务) → 弃
- g7b4c: wrong-domain D (DES 密钥提取类) → 弃
- 3ygqr: NEW-user, 真 B 域 spice_sim, mc155 hspice dominant → 选
