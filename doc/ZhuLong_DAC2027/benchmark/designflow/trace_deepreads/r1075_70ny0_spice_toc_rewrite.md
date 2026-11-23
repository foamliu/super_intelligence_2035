# Deepread: 70ny0 (rhyanw@hfeg0pkn005, mc32, spice_sim)

**session**: 1794965335508_70ny0.messages.json (452KB, 89 msgs)
**trace_source**: rhyanw / hfeg0pkn005 / 1794965335508_70ny0 / mc32 / netlist:106;schematic:90;hspice:21;cmos:21;pex:20
**access**: .75 ssh → hfeg0pkn005 (rhyanw home world-readable via scp, no password)
**cross-4-shard-ledger**: fresh (NONE in A/B/C/D) ✓

## 用户真实意图（4 个 user 任务）

rhyanw 在做 DRAM sense amplifier (SA) 的 **SM gap mismatch characterization**，工作目录
`/proj/drvqa/V0/workdir/rhyanw/SM/05_SANEN_SAPEN/SMmismatch20261117/`。

**背景（msg 0/18/22）**: 用 FineSim/PrimeSim bisection 扫 16 种 pattern（CS/ISO/TPC/RVS/THR/FAR…），
找使被感知 BL 在 69n~70n 达到 GOAL=0.8V 的 VTarget。SM gap = 16 个 vtarget 的 max−min。
mismatch 经 `delvtoBL{0..3}_NsL/NsR/PsL/PsR` 注入 SA 输入对（ntnlvio_sa, w=228n l=97n）。
mixbest = 4 根 BL 同向系统偏差（correlated worst-case）：`Nsl=Maxn Nsr=-Maxn Psl=Maxp Psr=-Maxp`，
`Maxn=23.1m*ratio2 Maxp=27.28m*ratio2`，ratio2 从 0.1（mixbestrat1）到 1.0（mixbestrat10）。
用户困惑：不加 mismatch SM gap≈10，加很小 mismatch（每边几 mV）SM gap 涨到 40，问为什么。

### Task A（msg 23）— **本 case 选料**
> 「按照sp名称后面到1-10的数字更新一下对应到tOC 到sp文件中，对应关系如下 ratio→toc/ns:
> 0.1→1.16, 0.2→1.18, 0.3→1.22, 0.4→1.28, 0.5→1.34, 0.6→1.42, 0.7→1.5, 0.8→1.6, 0.9→1.73, 1→1.83」

assistant 读取全部 20 个 .sp（mixbestrat1-10 + mixworstrat1-10），确认每文件第 30 行
`.param toc=<old>n tsdt=15n tseldly=0 tsady=300p` 的当前 toc，按 ratio2=后缀/10 查表替换。
注意 mixbestrat6/mixworstrat6 (ratio2=0.6) 旧 toc=1.42n == 新 1.42n，无需改。
因 policy writableRoots 只有 /home/rhyanw，editor 改不了 /proj，改用 shell-runner 跑 sed 脚本。
替换为精确整行 old_text→new_text（`.param toc=1.19n tsdt=15n tseldly=0 tsady=300p`→`...1.16n...`）。
验证：grep 每文件 `.param toc=` 行确认新值。

旧→新 toc 映射（mixbestrat1-10 = mixworstrat1-10 同表）：
| suffix | ratio2 | old toc | new toc | changed? |
|---|---|---|---|---|
| 1 | 0.1 | 1.19n | 1.16n | ✓ |
| 2 | 0.2 | 1.21n | 1.18n | ✓ |
| 3 | 0.3 | 1.25n | 1.22n | ✓ |
| 4 | 0.4 | 1.29n | 1.28n | ✓ |
| 5 | 0.5 | 1.35n | 1.34n | ✓ |
| 6 | 0.6 | 1.42n | 1.42n | ✗ (unchanged) |
| 7 | 0.7 | 1.49n | 1.5n  | ✓ |
| 8 | 0.8 | 1.58n | 1.6n  | ✓ |
| 9 | 0.9 | 1.67n | 1.73n | ✓ |
| 10| 1.0 | 1.76n | 1.83n | ✓ |

### Task B（msg 59）: runsim1-4 保存路径 result2 → result18（sed `./result2`→`./result18`）
### Task C（msg 73）: 删 `Maxn=23.1m *ratio2`/`Maxp=27.28m *ratio2`/`ratio2= 0.2` 多余空格
### Task D（msg 83）: 检查 sp 文件是否还有多余空格（trailing + `C_BL2SUB =` 等号前空格）

## Reframe（选 Task A）

**case = EDA-Eval-DesignFlow-SpTocParamRewrite-001**
`toc_update.py <deck_dir> <spec.json> <out_report.json>`: 参数化 SPICE deck `.param toc=` 批量更新器。
读 spec.json 的 `ratio_to_toc` 映射 + `toc_param` + `toc_unit`，逐 .sp 文件：
- 抽 `.param ratio2=<val>` 查映射得 new_toc
- 抽 `.param toc=<old><unit> ...` 行，若 old != new 则替换 `<old><unit>`→`<new><unit>`（仅改 toc 值，行内其余参数字节不动）
- 无 ratio2 / ratio2 不在映射 → skipped
- old == new → unmodified
- 输出 JSON report: {spec, files_scanned, files_modified, files_unmodified, files_skipped, total_replacements, per_file:[{file, ratio2, old_toc, new_toc, action}]}
L1 纯 Python 无 EDA 依赖。

## A / hidden B 设计

**A**（rhyanw 真实结构）: deck_A/ 20 .sp（mixbestrat1-10 + mixworstrat1-10），ratio2=0.1-1.0，
toc 旧值 1.19/1.21/1.25/1.29/1.35/1.42/1.49/1.58/1.67/1.76，spec_A ratio_to_toc 同 rhyanw 表。
**hidden B**（五重 anti-hardcode）:
1. 文件名/系列异 A: sensampA1-6.sp + sensampB1-6.sp（12 文件）
2. ratio2 异 A: 0.15/0.25/0.35/0.45/0.55/0.65（非 0.1 整数倍）
3. toc 映射异 A: 0.15→2.05, 0.25→2.12, 0.35→2.19, 0.45→2.31, 0.55→2.44, 0.65→2.42
4. 含 1 个 old==new 不改 case (sensampB6 ratio2=0.65 old=2.42n==new)
5. toc 行 surrounding 参数异 A: `tsdt=20n`（A 是 15n）+ 含 1 个无 ratio2 的 skipped .sp + 1 个非 .sp(.txt) 测 glob 过滤
核心齿反: naive `sed s/toc=[0-9.]*n/toc=<A 硬编>/` 会在 B 上写错值/漏文件/动错行。

## check.py 12 条 (a-l)
①(a)zip+py_compile+size>200 ②(b)B exit0+非空 JSON report ③(c)顶层键⊇{spec,files_scanned,files_modified,files_unmodified,files_skipped,total_replacements,per_file}
④(d)n_scanned==13(B 仅 *.sp) ⑤(e)n_modified==11 ⑥(f)n_unmodified==1(sensampB6) ⑦(g)n_skipped==1(无 ratio2)
⑧(h)每 modified .sp 磁盘: `.param toc=<new>n` 在场、`<old>n` 缺席 ⑨(i)precision: 每 modified .sp 除 toc 行外逐字节==pristine
⑩(j)anti-hardcode: B 新 toc 值在场、A 的 toc 值(1.16/1.18/...)缺席 ⑪(k)report.spec==B ⑫(l)3-seed sha256 一致

## 3 negs
- neg_empty(空壳→a/b) / neg_print_only(打 A 硬编 report 不改文件→h/i/j) / neg_sed_fixed(sed 用 A 固定映射→h/j; 或整行替换丢 tsdt→i)
