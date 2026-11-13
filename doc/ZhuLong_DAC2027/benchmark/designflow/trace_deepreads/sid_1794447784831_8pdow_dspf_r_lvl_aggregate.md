# trace_deepread: sid 1794447784831_8pdow — DSPF R-by-$lvl aggregator + lvl coordinate locator

- **session**: 1794447784831_8pdow · user e0024852 · host hfeg0plg78 (10.129.8.123) · mc25
- **keywords**: pex:36; lvs:93; calibre:24; netlist:5; transistor:6 · domain schematic_netlist (PEX/DSPF text processing, same family as r624 capfit)
- **scan src**: ssh_eda_search_20261113_131349/summary.tsv
- **selection**: r630 mc10-30 band, 4-shard-excluded 95 fresh; peeked 11 candidates (2tppk=batch_pex env-dep / dd0n2=rc_viz graphics / q3nek=CML swing Q&A / o8obe=svdb env-dep / 250y8=lib Q&A / 5z1pb=skill-cmd / u060n=task-doc single-turn / uu6ie=skill Q&A / 8pdow=HIT). 8pdow cleanest produce-task.
- **near-dup check**: e0024852 not in D.jsonl (grep 0); no prior DSPF/R-lvl case; 2tppk same user but different task (batch_pex) — not near-dup.

## Real task (5 user turns, 50 msgs)
- U0: 后仿 DSPF 寄生电阻大，贴 R12_1.. 行（带 $lvl），问对应关系
- U1: 怎么确认对应关系对
- U2: 寄生太大怀疑对应关系不对，逐层详细对应表格
- U3: **全部 R 按 $lvl 分组汇总 总电阻/最大 R/数量，哪层贡献最大** (core produce)
- U4: **把 lvl=37 那 6 个电阻在版图上坐标/中心位置定位** (extension produce)

## Real assistant produce (shell scripts, run via shell-runner; python-runner had locale/encodings SIGABRT)
- `r_by_lvl.sh` → awk 聚合全部 R by $lvl: count/total_ohm/max_ohm, 降序. 真实输出 259 个 R, lvl=37 (6 颗, total 792000, max 132000) 占 79.8% 主导; lvl=36 (6, 158400) 16%; lvl=29/30/33/15/17/22/21/23/31/32/28/27/25/26/34/3/4/5/6/13/14 次之.
- `locate_lvl37.sh` → grep lvl=37 的 6 颗 R (R12_7/9/11 SB:3/4/5→SB:22/23/24; R13_28/30/31 S:17/18/19→S:22/23/24) + *|S 子节点坐标. 两端坐标**重合**(零长度点接触, $a=3e-6) → 中心=该坐标. SB 侧 (0.0750, 0.0595/0.0605/0.0615); S 侧 (0.0270, 0.1295/0.1305/0.1315).
- 层对应验证: *LAYER_MAP (DSPF 头部 25-57 行) + tran.map 交叉 + 栅极语义 (MPU1:g→lvl=15 pgate) + R×A 常数 (37:132000×3e-6=0.396 == 36:26400×1.499e-5=0.396).

## Real DSPF format captured
- R 长度型: `R<name> <n1> <n2> <val> $l=<L> $w=<W> $lvl=<lvl>`
- R 面积型: `R<name> <n1> <n2> <val> $a=<A> $lvl=<lvl>` (通孔/接触孔, 无 $l/$w)
- `*|S (<node> <x> <y>)` 子节点坐标 (node 可含冒号 SB:3)
- `*|P (<node> <type> <dir> <x> <y>)` 端口
- `*|NET .. *|ENDNET` / `*LAYER_MAP .. *END_LAYER_MAP` 结构化记录 (*| 非注释)
- **关键 gotcha**: `$l=<长度>` vs `$lvl=<层号>` 字段名前缀冲突 — 朴素 `\$l=(\d+)` 抓到长度首位(0), 必须按 `$`-token 拆 `=` 精确匹配 key=='lvl'

## Synthesis (case EDA-Eval-DesignFlow-DspfRLvlAggregate-001)
- **SUT**: `dspf_r_aggregate.py` 纯 stdlib CLI 两模式:
  - 聚合 `python3 dspf_r_aggregate.py <dspf>` → stdout tab 表 `lvl count total max` 降序 + `TOTAL <rcount> <sum> -`
  - 定位 `python3 dspf_r_aggregate.py <dspf> --locate <lvl>` → stdout tab 表 `Rname n1 n2 value x1 y1 x2 y2 midx midy` (mid=两端中点, 文件顺序)
- **visible_A** = sample_A.dspf (13 R, 9 lvl, SB/S 两 net, 含 $l-vs-$lvl gotcha + 零长度(R3 SB:3==SB:21) + 不重合(R4) 坐标)
- **hidden_B** = sample_B.dspf (15 R, 10 lvl, DB/DQ 节点名, lvl=37 主导(4 颗 528000), R-count=15; locate37: 4 颗 R3/R4/R7/R8, 零长度 R3(DB:3==DB:10)/R7(DQ:17==DQ:22) + 不重合 R4/R8)
- **hidden_C** = sample_C.dspf (7 R, 4 lvl=44/46/48/55, WL/BL 节点, **lvl=55 主导** 反硬编码 B 的 37; locate55: R2 零长度 + R3 不重合)
- **check.py** 16 cond a-p, 内嵌独立 oracle (re-parse DSPF, 不 import SUT), TOL=1e-4 容 4-位小数舍入:
  - a/b zip合法仅1.py + py_compile / c compile / d 不硬编码 A 字面量(SB:21/S:24/SB:99/S:23/0.0585) / e B 聚合 exit0+表头 / f B (count,total,max)==oracle / g 降序 / h R-count==15 / i **$l-vs-$lvl gotcha**: 不含伪 lvl=0/1/2/5/6 且 lvl=28 total=11.0237 存在 / j B locate37 行数=4 / k (Rname,n1,n2)集==oracle / l 端点坐标==oracle(零长度+不重合) / m 中点==oracle 且含 R3/R4/R7/R8 / n C 聚合==oracle(反硬编码) / o C 降序且顶层=55 非37 / p C locate55 坐标/中点==oracle
- **4 neg** (distinct labels e/f/h/j): empty_shell→e / print_only(hardcode B 表,无locate)→j / hardcode_a(输出 A 数)→f / core_removed(聚合对但无 TOTAL)→h
- **§4.9 三假** empty/print/core 全 FAIL · NEG_RC=0 · ref PASS 16/16

## Self-verify result
```
REF: PASS (16/16 a-p)
NEG distinct labels: 4 (e,f,h,j) ALL FAIL
ALL GOOD: ref PASS, 4 negatives FAIL distinct, NEG_RC=0
```
k_rationale = k_check = 16 ✓ · D.jsonl 368 → 369
