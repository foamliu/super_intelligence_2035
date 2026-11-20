# 深读笔记 · 5vo44 · sacap Perl 电容摘要工具信号丢失诊断

## trace 来源
- user: rongtaoy @ hfeg0pkn001
- session: 1792986549258_5vo44.messages.json (1.8 MB, 449 msgs, 26 user turns)
- match_count: 154 (kw: netlist-dominant; sacap Perl cap-summary tool)
- domain: eda_other (post-pex cap-summary CSV 异常诊断, L1-static + subprocess)
- 工具命中: sacap_0922.pl / run_single.sh / SPF .spf_CC / CSV Total_Summary

## A档选轮
- **USER#0 (idx 0)** = A档任务说明（逐字原文）：
  > `你帮我看看/proj/ddgoa/V0/ver/pex/rongtaoy/0.sacap_noanb/run_single.sh为什么没有识别/proj/ddgoa/V0/ver/pex/rongtaoy/msaq_U_CCR_fBcc_int_0921BK/msaq_U_CCR_fBcc_int.spf_CC的SapEnA/SanEnA，明明有*|NET SapEnA`
- ✅ 纯目标轮（提出"为什么没识别"的问题，未给根因/未给方案）→ A档 eligible
- 用户在 msg 41 接受 assistant 的根因分析（"对，就是这个问题"），但用户本人未提供根因 → gold = assistant 的诊断
- 后续 user turns 为补充文件路径/确认/微调，不作 A档任务说明

## 金标准（trace 中 assistant 给出、用户接受的根因）
- assistant 深入读取 sacap_0922.pl 的 `Get_Caps_Pair` 子程序（line ~443-460），定位 bug：
  1. **硬编码正则路由分支在 @signame foreach 循环之前**：
     - `$couplenet =~ /^SapEn[ABCD]$/i` → 路由到 `PCSGate` 聚合桶（line ~447）
     - `$couplenet =~ /^SanEn[ABCD]$/i` → 路由到 `NCSGate` 聚合桶（line ~450）
  2. **@signame foreach 循环在更后面**（line ~454）：`foreach my $sigterm (@signame) { if ($couplenet =~ /^${sigterm}$/i) {...} }`
  3. **后果**：run_single.sh 的 `SIG_NAME` 显式列出了 `SapEnA SapEnB0 SapEnC0 SanEnA SanEnB0 SanEnC0`，但由于 SapEnA/SanEnA 先被硬编码正则匹配到 PCSGate/NCSGate 桶，它们被并入聚合行；其命名的 CSV 行（row[08] SapEnA / row[11] SanEnA）保持全 0。
  4. **SPF 确有声明**：`*|NET SapEnA = 0.199581PF` / `*|NET SanEnA = 0.19121PF`（用户已观察到）
  5. **修复方向**：重排 Get_Caps_Pair 分支——先评估 @signame 匹配，再做硬编码聚合路由；或排除 -sig 显式列出的信号不被硬编码聚合路由吞没。
- 用户 msg 41 接受："对，就是这个问题，谢谢"（无修订）

## 合成计划
- task_id: `EDA-Eval-DesignFlow-SacapSignalMissingDiagnose-001`
- 交付: `outputs/submit.zip` 含 `diagnose_signal_missing.py`
- 接口: `diagnose_signal_missing.py` 读 `config.json{perl_script, shell_script, spf_excerpt, csv_summary, missing_signals}` → 解析 Perl Get_Caps_Pair 硬编码正则路由分支（标记 before_signame）+ SPF *|NET 声明 + CSV 行全 0 状态 → 输出结构化 JSON 诊断到 stdout
- A（SUT 看）: 真实 `sacap_0922.pl` (22671B) + `run_single.sh` (1959B) + `spf_sap_san_nets.txt` (SPF 摘录) + `csv_total_summary.txt` (CSV 摘要, SapEnA/SanEnA 行全 0)
- 隐藏 B（check 仅跑 B）: 合成结构对立 **Vref/VrefN 族**
  - `B_sacap_vref.pl`: 硬编码 `/^Vref[WXYZ]$/i → VrefGate` + `/^VrefN[WXYZ]$/i → VrefGrndGate`（before @signame）；同 bug 模式，不同信号族 + 不同聚合桶
  - `B_run_vref.sh`: SIG_NAME=`VrefW VrefX0 VrefY0 VrefNW VrefNX0 VrefNY0 ...`
  - `B_spf_vref_nets.txt`: Vref*/VrefN* 的 *|NET 声明
  - `B_csv_vref_summary.txt`: VrefW/VrefNW 行全 0（被 VrefGate/VrefGrndGate 吞没）
  - missing_signals = [VrefW, VrefNW]
- B'（交叉输入守卫）: `Bp_sacap_nobug.pl` = no-bug 变体（@signame 先评估→VrefW/VrefNW 得到自己的行→CSV 非全 0；VrefGate/VrefGrndGate 全 0）→ 候选脚本须报 `root_cause == no_hardcoded_routing_bug`
- gold: `diagnose_signal_missing.py` — config 驱动，泛化解析任意 sacap Perl 的 Get_Caps_Pair；不硬编码 A 的 SapEn/SanEn/PCSGate/NCSGate（反硬编码条件 m）
- check.py: 14 conds a-n（L1-static + subprocess）
  - a zip含diagnose_signal_missing.py / b py_compile / c [B]子进程 exit0+合法JSON / d [B]必需顶层键 / e [B]root_cause==regex_routing_before_signame / f [B]≥2 路由规则 / g [B]正则 Vref[WXYZ] 正相族 / h [B]正则 VrefN[WXYZ] 负相族 / i [B]桶含 VrefGate+VrefGrndGate 且不含 PCSGate/NCSGate / j [B]missing 全覆盖 VrefW/VrefNW / k [B]每条 missing spf声明+csv全0+routed非空 / l [B]nonmissing 尾数字信号 routed==null+csv非全0 / m 反硬编码无 A 专属字面量 / n [B']交叉输入守卫 root_cause==no_hardcoded_routing_bug

## 自验结果（.75 sandbox）
- REF PASS 14/14 a-n
- 3 negatives FAIL distinct: naive_noop→{d}, print_expected(硬编码 A SapEn/PCSGate)→{g}, core_deleted(删 parse_hardcoded_routing)→{e}
- §4.9 三假全 FAIL: empty_shell→{c}, print_expected_fake→{j}, core_deleted→{e}
- negative_selftest PASS distinct=3
- 断言闸门 k_rationale=k_check=14 ≥ 8 PASS

## 交付
- 追加 `EDA-Eval-DesignFlow_A.jsonl` (162 entries)
- mark 5vo44 → case (covered 159→160, eda_other 28→29)
- 本地自验同样全绿（base64 传输 16 文件，REF 14/14, negs distinct=3, §4.9 全 FAIL）
