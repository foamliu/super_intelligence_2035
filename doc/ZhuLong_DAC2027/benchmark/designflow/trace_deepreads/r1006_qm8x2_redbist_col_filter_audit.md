# Deepread r1006 — qm8x2 RedBist COL_FILTER audit

- **session**: `1794807475487_qm8x2.messages.json` (72 msgs)
- **user/host**: thomas1w @ hfeg0pjn197 (10.129.40.206)
- **match_count**: 41 (kw verilog:98 systemverilog:15 netlist:14 → A-pure verification)
- **domain**: verification (A)
- **fresh**: yes (absent from all 4 shard ledgers at round start)

## 用户意图（verbatim）
- U#0: irun.log 中存在有效注错的地址信息，A_Compare.rpt 有注错地方，根据 TM_RedBist.sv 中错误地址位置解析来判断筛查逻辑是否有问题。
- U#46: `[COL_FILTER] idx=18 arr=W bk=0 ba=0 sec_t=32 secg=3 sec_in_g=4 -> out of range ...` 没被采集，其他参数算得有问题。
- U#60: 整体看下代码校验逻辑有没有问题，整理 check 思路。

## Trace gold
Agent M#25 写 `redbist_log_scan2.py`，正则
`idx=(\d+) arr=(\w+) bk=(\w+) ba=(\d+) sec_t=(\d+) secg=(\d+) sec_in_g=(\d+) -> out of range \(ba\[(\d+):(\d+)\] sec\[(\d+):(\d+)\] secg\[(\d+):(\d+)\]\)`，
按 `sec_t//7` 与打印 `secg` 比对：128 行 COL_FILTER，120 mismatch，8 YES。

## Case reframe (debug-Q&A → diagnose produce-task)
通用脚本 `audit_redbist_col_filter.py <irun_log> <output_json>`：解析 COL_FILTER 行 → 重算 secg=sec_t//7 → 分类 match/mismatch → 结构化 JSON（含 root_cause + fix_recommendation）。

## Fixtures
- A (`irun_A.log`): 37 COL_FILTER, 30 mismatch, 7 match, sorted_fail=4×forced32, pattern 1/1/2。trace-faithful 脱敏摘录。
- B (`hidden/irun_B.log`): 45 COL_FILTER, 36 mismatch, 9 match, sorted_fail=3×forced48, pattern 2/3/5。全部具体值与 A 不相交 (idx 50-99 / arr D,F / bk 4,5,9 / ba 4-7 / sec_t 60-99 / secg 2,4,6,7,8-13)。

## Judge
check.py 16 断言（含 §4.9 三假：空壳/print-only/core-deleted 均 FAIL；3-neg selftest 通过；ref 16/16 PASS；3-run md5 一致）。

## 结论
1 case 交付，A 档 trace-faithful。
