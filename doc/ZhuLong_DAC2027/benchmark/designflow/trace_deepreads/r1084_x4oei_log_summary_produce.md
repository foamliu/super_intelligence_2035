# r1084 deepread — x4oei (max7c @ hfeg0pkn005, mc175) → X4oeiLogSummaryProduce-001

## trace 源
- session: 1795421799906_x4oei.messages.json (381KB, 49 msgs: 30 user / 19 assistant)
- user: max7c, host: hfeg0pkn005 (10.129.2.14), keywords verilog:1013;analog:25;drc:10;cmos:4;netlist:2;rtl:1 → verilog 96%+ A-pure digital ✓
- scp 路径陷阱: 文件在子目录 sessions/<sid>/<sid>.messages.json (r1074 发现的格式)

## 用户意图 (两轮原话)
- U#0 (主意图): 「把 /proj/ddjoc/V0/simdir/verilog/max7c/verilog.lpddr5.ddjoc.Nov17/try_async_flow 里除了 backup 之外的子文件夹里的 user_cmd.log 总结一下，在 .../verilog.lpddr5.ddjoc.Nov17/ 目录下生成一个可执行文件」
- U#30 (追问): 「这里的子文件还有没有像 refresh_sr_diffdsm_a_0 和 refresh_sr_diffdsm_0 的这种情况」(同 pattern 不同 seed 的"情况")

## trace 中 assistant 实际做的事
1. list_allowed_files 探 try_async_flow 目录 → 36 子文件夹(basiccheck/casops/cbt/datacopy/dcm/ecc/loadmode/mbistppr/mrr/onebank/random/refresh_*/tm_*/wrrdfifo/zqcal 等)
2. 发现 user_cmd.log 在 `<case_dir>/<pattern>.x16/user_cmd.log` (两层深)，每文件**单行** vsim 启动命令:
   `./bin/vsim -sr <pattern> -d "<宏定义>" [--ncconfig "<抑制告警>"] [--noprobe] -q ASYNC_TEMP -l try_async_flow/<case> -g <seed>`
3. 读全部 40 个 user_cmd.log → 写 summarize_user_cmd.sh (解析 pattern/seed/defines/noprobe，输出 per-case 表 + SUMMARY + 同 pattern 字段差异组) → 部署到目标目录 + chmod +x + 校验
4. 追问 → 写 compare_same_pattern.sh (同 pattern 两两逐字段对比 seed/defines/ncconfig/noprobe) → 发现 refresh_sr_diffdsm_0 vs _a_0 seed 不一致

## case 合成 (A档 trace-faithful)
- 交付: outputs/submit.zip = summarize_user_cmd.sh (通用 bash 脚本)
- A 资产: try_async_flow_A/ — 11 valid case (basiccheck/casops/cbt/datacopy/dcm/ecc/loadmode/mbistppr/mrr/refresh_sr_diffdsm_0/refresh_sr_diffdsm_a_0) + backup(bk_old1/bk_old2, 排除). 真实 vsim 格式, refresh_sr_diffdsm 同 pattern 不同 seed (12354 vs 99999) 保留为 A 的"情况".
- hidden-B: try_async_flow_B/ — 10 valid case (onebank/random/wrrdfifo_0/wrrdfifo_1/zqcal_0/zqcal_a_0/casrw/autoprecharge/mdbist/tm_cmds) + emptycase_0(无 log, missing) + backup(bkq1, 排除). defines=LP5_ASYNC (A 用 DDR5_ASYNC, 零 token 相交). 2 个 situation: wrrdfifo(seed 100/200 diff) + zqcal(seed 300/400 + defines DBG_MODE diff). tm_cmds_0 无 --noprobe (测 noprobe=no 解析).

## check.py (16 断言, k=16)
a zip合法含sh | b bash -n | c [B]exit0 | d [B]SUMMARY cases=10 patterns=8 missing=1 | e [B]missing_list=emptycase_0 | f [B]bkq1不出现(backup排除) | g [B]per-case表含10有效case且不含emptycase_0 | h [B]seed解析 onebank_0=11 tm_cmds_0=88 | i [B]noprobe tm_cmds_0=no onebank_0=yes | j [B]zqcal_a_0 defines含DBG_MODE | k [B]situations含wrrdfifo+zqcal | l [B]wrrdfifo seed 100/200 | m [B]zqcal seed 300/400+DBG_MODE | n [B]确定性3x md5 | o 无参exit非零 | p anti-hardcode无A字面量

## 自验
- ref PASS 16/16 ✓ (A树 11case/10pattern/1situation + B树 10case/8pattern/2situation 全对)
- §4.9 三假 (empty/printonly/coredel) 全 FAIL ✓ (printonly→cond g B表缺真实dir, coredel→cond d SUMMARY mismatch)
- negative_selftest: ref PASS + 3 neg FAIL ✓
- 确定性 3x md5 一致 ✓
- anti-hardcode: 脚本源码无 A 专属字面量 ✓
- A/B token 零相交 (A: DDR5_ASYNC/basiccheck系/12345/99999; B: LP5_ASYNC/onebank系/11..400) ✓

## 三闸门
(a') 结构正交: 通用 bash 解析器 vs 既有 case 的 Python-JSON-diagnose (不同形态) ✓
(b') ≥4 不可复用断言: 16 条独立条件 ✓
(c') A/B token 不相交 ✓
