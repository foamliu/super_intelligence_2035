# Deepread: gs5dr (lorikx@hfeg0pkn005, mc66, 728KB, 53 msgs, 3 user turns)

## Trace provenance
- session: 1788859959654_gs5dr.messages.json
- user/host: lorikx / hfeg0pkn005 (also synced on hfeg0plg52, hfeg0pjn200, hfeg0pkn001 via shared home)
- scan kw: synopsys:158;verilog:89;rtl:68;synthesis:4;pyaether:4;systemverilog:2 (tools col: 4 synthesis, 4 pyAether)
- match_count: 66 ; digital-dominant (digi6/ana1)
- domain: verification (RTL sim bug diagnosis + fix verification)
- selected at: shard A r206 (2026-11-07)

## User turns (verbatim, real — non-tool-result)
- USER#0 (clean requirement, A-faithful rule2 OK — reports suspected bug, no root-cause/fix given):
  「验证的同事帮忙修改的代码，说是查处了TEST Mode下，出现X态后，恢复的时候如果没有在写入，不应该把值写入进去，但是现在写进去了，你检查一下，是否有这个问题？仿真错误出现在了1242000ps到1248000ps左右， 你可以用插件iverilog试着跑一下仿真看看 please compare original code @rtl/.sp_2pram.v.swp and modified code @rtl/sp_2pram_new.v」
- USER#43: 「你可以在sim目录下按照Makefile的提示去输入指令跑仿真检查结果吗，指令： bs make xxxx 这样」(依赖前文，非干净需求)
- USER#51: 「那现在你告诉我怎么操作，然后返回给你哪些信息可以判断错误是否被修复」(依赖前文，非干净需求)

## Selection: USER#0 → A-faithful case
- gold = assistant msg#42 (完整诊断) + msg#52 (手动运行指引 + 判据)

## Real attachments (e0031982 ssh-readable on hfeg0pkn005)
- /home/lorikx/2prfbv_refer/verification/v0908/rtl/sp_2pram.v (3136 lines, symlink, original/buggy)
- /home/lorikx/2prfbv_refer/verification/v0908/rtl/sp_2pram_new.v (3117 lines, modified/fixed)
- /home/lorikx/2prfbv_refer/verification/v0908/sim/simv.log (1107 lines, original: 18q FAIL + TESTS FAILED:1)
- /home/lorikx/2prfbv_refer/verification/v0908/sim_2/simv.log (1107 lines, modified: 18q PASS + ALL TESTS PASSED)
- /home/lorikx/2prfbv_refer/verification/v0908/sim/tb_sp_2pram.v (4262 lines, testbench)
- /home/lorikx/2prfbv_refer/verification/v0908/sim/filelist.f (5 lines)

## Gold diagnosis (msg#42)
- sim config: simv__32______x8________tv_td_fi_cm1 → NW=32×NB=8, Side Decode (CENTER_DECODE=0), CM1=1, TV=1, TD=1, FI=1 → active gen_sd block
- **gold 的机制解释有误**: gold 称原/改唯一差异是 SD TEST negedge block 加了 `test_op_type_w=2'd2` / `test_op_type_r=2'd2` clear-after-consumption 行。**实际 grep 显示两文件都有 clear 行** (orig 2074/2131/2884/2951, mod 2055/2112/2865/2932)。
- **真实 RTL diff (full diff)**: 30 removed + 11 added，差异主要在 CR_ADDR_WIDTH 参数计算 (orig 有 max(1, ...) 下溢保护 + 多行注释，mod 简化为直接 clog2 三元链) + 一处 $display 警告删除。即真正的 fix 是 CR_ADDR_WIDTH 参数简化，**不是** clear 行。
- sim 证据 (ground truth，无歧义):
  - 原 sim/simv.log: line 417 `--- 18q: CLKW=x in TEST mode (mem=X) ---`, line 422 `FAIL [1251000] 18q: mem not X after CLKW=x (expected corruption)`, line 1100 `TESTS FAILED: 1 errors`
  - 改 sim_2/simv.log: line 422 `PASS [1251000] 18q: mem=X after CLKW=x in TEST mode`, line 1100 `ALL TESTS PASSED`
- assistant 另发现并修了 CD 模式 copy-paste bug (line 2932: `test_op_type_w` 应为 `test_op_type_r`)
- msg#52: 给用户手动跑 sim 指引 (bs make TV=1 TD=1 FI=1 CM1=1 vcs/run) + grep 判据 (18q PASS/FAIL, ALL TESTS PASSED)
- 注意: trace 中 run_commands 被 policy 禁用 (Raw shell disabled + prc_step1 denied 0775)，故 gold 全程静态分析 + 复用已有 VCS 日志，未真跑 iverilog/VCS。

## Case design (A-faithful, L2-static)
- task_id: EDA-Eval-DesignFlow-RtlSimfixVerdict-001
- 交付: gen_simfix_verdict.py — 通用 RTL-simfix 诊断报告生成器 (CLI --orig-rtl/--mod-rtl/--orig-log/--mod-log/--out → JSON)
- 诊断基于 **sim 证据 (ground truth)**，RTL diff 作辅助证据 (不依赖 gold 的有误机制解释)
- A 资产 (真实子集): sp_2pram_orig.v (lines 48-92, CR_ADDR_WIDTH 含保护), sp_2pram_mod.v (48-92, 简化), sim_orig.log (18q FAIL + TESTS FAILED:1 tail), sim_mod.log (18q PASS + ALL TESTS PASSED tail), filelist.f
- 隐藏 B (合成, 与 A 零标识符重叠): dp_1pram 单口 RAM, RD_GUARD_WIDTH 参数, 测试 07c/07d, 信号 CLKR, 时间戳 882000, fail count 2, 消息 "Q not X after CLKR=x"
- check.py 16 conds (a-p): a zip含py无禁import / b py_compile / c [B]exit0合法JSON含必需键 / d bug_confirmed / e sim_orig FAIL / f sim_mod PASS / g all_tests_passed / h failing含07c / i mod无failing / j rtl_diff_present / k added>0&removed>0 / l fix_verified_by_sim / m summary含TESTS FAILED / n [A]反硬编守卫(18q FAIL→PASS+ALL TESTS PASSED) / o 源码无A字面量(sp_2pram/18q/1251000/CR_ADDR_WIDTH/CLKW) / p [B']随机化(seed7/11)结论稳定+recommendation非空
- 自验全绿: ref PASS 16/16 + 5 negs 全 FAIL (distinct first_fail {c,d,j,n}) + §4.9 三假 (empty_shell→c / print_expected→n / core_deleted→d) 全 FAIL + negative_selftest PASS
- k 闸门: k_rationale=k_check=16 ≥8 ✓
