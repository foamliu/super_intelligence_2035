# trace deepread — 1g0xs Hierarchy Tracer (xinweif @ hfeg0pkn005)

## trace source
- user: xinweif · host: hfeg0pkn005 (10.129.2.14) · session: 1792204349915_1g0xs.messages.archive.json (2.8MB, 727 msgs)
- 11-05 重扫令：上轮(21:2x) peek .messages.json 判 "FineIM hierarchy check debug 暂缓 archive 待查"；本轮 archive 深查 → CLEAN A-faithful

## 用户意图轮（A-faithful prompt = U#70 逐字）
「帮我写一个python脚本，检查这个hierarchy：xi_c_top.xi_array16gtop.xi_array8g_e.xi_array1gbk3.xi_m1g_top.xi_m512meg_u.xi_msaq_28 在这个网表是否存在/rundata/ddgoa/V0/simdir/finesim/workdir/xinweif/simulation/trynet/netlist   脚本也帮我放在这个路径/rundata/.../trynet」
- U#0 是更广的诊断任务("分析两路仿真网表差异导致 rdqst fail vs pass")；U#70 是其可复用子流(写脚本检查 hierarchy)，更具体、gold 清晰，选作 prompt

## 金标准（assistant 迭代 ~15 版 check_hierarchy.py）
最终版 [472] SPICE 网表 Hierarchy Tracer：
1. scan_subckts → {UPPER_NAME:(start,end,orig)}（处理 .SUBCKT/.ENDS 嵌套 depth）
2. find_top = 第一个非标准单元(SKIP_ST 前缀) 的 .SUBCKT
3. 逐层 find_insts 在父 SUBCKT 内找 X-实例（处理 `+` 续行：+开头 extend tokens）
4. match_inst：精确实例名匹配 → 去XI_/X前缀公差匹配
5. 子 subckt = 实例行末 token；输出 chain + OK/BREAK，exit 0/1
- 关键 trap：(a) `+` 续行不处理则子名取错 (b) 标准单元(inv/nor2)被当顶层 (c) 硬编码 KNOWN_MAP 失败（终版改为动态提取）
- 结果：7 层 SUBCKT 全存在 xi_c_top→LP5TOP→Array16GTop→Array8G_E→Array1G_Top_W→M1G_Top→M512MEG_U→MSAQ_28

## 合成（本 case）
- case_id: EDA-Eval-DesignFlow-HierarchyTrace-001 · domain spice_sim · track faithful · layer L1
- A 网表(可见)：合成 SPICE fullchip，7 层 hierarchy + inv/nor2/nand2/buf 标准单元噪声 + xi_array8g_e `+`续行 + Array16GTop 内 Xother 诱饵实例
- hidden B：不同 subckt 名(WOWTOPB/LP5TOPB/.../MSAQ12B) + 续行在 xi_msaq_12 层(5-pin) + 不同叶子
- reference: check_hierarchy_ref.py（改进版：top=含首层实例的 SUBCKT，非"第一个非标准"，更鲁棒）
- check.py 14 断言(a-n)：zip含1个.py / py_compile / B合法exit0 / B含CHAIN行 / B CHAIN==期望链 / B断exit1 / B断含BREAK / A合法exit0(交叉) / A CHAIN==期望 / A≠B / B伪顶层exit1 / B链8名 / 3x幂等sha256 / B链顶=WOWTOPB(标准单元跳过)
- 自验：ref PASS 14/14 ✓ + 5 negative(empty→d / print_expected→f / hardcode_a→e / naive_first_subckt→e / naive_no_continue→c)全 FAIL distinct ✓ + NEG_RC=0 ✓ + §4.9 三假(empty/print_expected/no_continue)全 FAIL ✓ + 断言闸门 14==14≥8 ✓
- jsonl B 187→188 · ledger mark case
