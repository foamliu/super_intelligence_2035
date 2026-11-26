# trace_deepread: 1789713877959_wuhci — Batch LVL GDS Compare Script

- **sid**: 1789713877959_wuhci
- **user/host**: miccao @ hfeg0plg37 (10.129.35.75 域)
- **match_count**: 40 (keywords: drc:3082 等纯 layout, sim=0, dig=0)
- **affinity score**: 3082 (mc≥15 widen 池, non-ledgered non-xinqiaoz non-jkxu)
- **msgs**: 94 msgs / 5 user turns
- **status**: 未明确 completed，但用户实跑反馈 + assistant 修正构成 accepted gold

## 选料路径
- mc≥30 viable_uniq 15 non-ledgered: 2 jkxu (ocmhu=verilog coverage read REJECT / i6pnk=ddr5_test.sv SV delay how-to REJECT) + 13 xinqiaoz (PDK_QA DrcPatternCheck/DrcValueCheck saturated, 全 explain/diagnose REJECT)
- widen mc≥15: 1883 候选 → top-60 仅 3 fresh (wuhci/qwreb/hasla): qwreb=ellawu AVOID; hasla=zqzhan Finesim SPICE deck shard B REJECT; wuhci=CLEAN produce-task

## 用户意图 (U#3 逐字)
> /home/miccao/autocell/decqa/gds和/home/miccao/autocell/ddcpc/gds下面的gds文件同名的多吗？不要子做聪明去autocell别的目录下找东西。将同名的cell使用flashlvl进行lvl，一致的标记为PASS,不一致的标记为FAIL，lvl结果放/home/miccao/autocell/lvl/decqa/下，统计报告也放这里。你写这个脚本，我执行

## 真实 gold 行为
assistant 受 agent-policy 锁死（run_commands 禁用；hello_world profile owner uid 10741≠运行 200329；skill-creator 只写 SKILL.md 不能执行脚本）。无法实跑，但写出 `batch_lvl_decqa_ddcpc.sh`（分多次 editor 调用拼接，~250 行）：
1. scan `$DIR_REF`/`$DIR_CMP` 同名 `*.gds` (find -printf '%f' | sort + mapfile + 关联数组交集)
2. only_ref / only_cmp 列表写入 summary
3. 逐 common cell 调 flashlvl → `run_flashlvl()` 函数
4. PASS/FAIL/ERROR 判定 + per-cell log
5. 输出 `lvl_summary.txt` + `lvl_summary.csv` + `lvl_stats.txt` + `<cell>/` 子目录

**关键修正事件** (U#4): 用户手跑报 `flashlvl 执行失败 (exit code: 1)` on and2GF47x1 → assistant 读 `and2GF47x1.log` 发现 flashlvl Usage: `flashlvl <layout1> [topcell1] <layout2> [topcell2] <outdb> [options]`，**之前误用 `-ref/-cmp/-out` 选项格式 → Command Line Error exit1**。修正为位置参数:
```
flashlvl "$ref_file" "$cmp_file" "$out_dir/flashlvl_result.gds" -Xor -SuppressEmpty -SUMfile "$sum_file"
```
并更新判定: exit1=差异=FAIL (非工具错误)；exit>1 或 log 含 `Command Line Error`/`Usage:` = ERROR。用户反馈后无进一步抱怨 → accepted gold。

## case 改造
- prompt = U#3 逐字 (A档 faithful)
- 通用化: `batch_lvl.sh <ref_dir> <cmp_dir> <out_dir>` 三位置参数 (miccao 路径作为默认值)
- runtime grading + mock_flashlvl (位置参数: cmp -s 一致→exit0+SuppressEmpty / 不同→exit1+写非空 outdb / 空文件或 - 开头 arg→exit2 Command Line Error)
- A 可见 (6+6 .gds, 5 common: inv/buf PASS + nand/nor/xorg FAIL)
- B hidden (8+7→6 common: c0-c3 PASS / d0,d1 FAIL)
- B2 hidden (含空 broken.gds → ERROR)
- B3 hidden (全一致 → 5 PASS exit0)
- 12 条件 a-l, 3 negatives, §4.9 三假, ref self-test 12/12 PASS, negative_selftest ALL FAIL

## 交付
- EDA-Eval-DesignFlow-BatchLvlGdsCmp-001
- jsonl_C 281→282, ledger_C case 282→283, DEBT:0
- r326
