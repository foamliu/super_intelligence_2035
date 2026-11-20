# Deep-read: nrep6 — tapered-buffer DOE rank builder (characterization)

- **session**: `1793151811279_nrep6.messages.json` (401 msgs, 1.36 MB)
- **user / host**: thqu @ hfeahpc503 (10.129.33.26)
- **match_count**: 215; **domain**: characterization
- **case_id**: `EDA-Eval-DesignFlow-DOERankBuild-001`
- **commit**: EDA-Flow-Bench `3b6af7ba` (jsonl append) + `a5df3224` (shard-B merge: reference/assets auto-commit)
- **ledger**: row 884, marked `case` (prior `parked` note "meta-skill DOE reject" overridden — gold deliverable is the rank CSV builder, not the meta-skill wrapper)

## Task (real)
锥形驱动器（tapered buffer）DOE 优化。电路：第一级 2-input NAND（nand2GSx1 / nand2GSx4）+
三级反相器链（invGSx{1,2,3,4,6,8,16}），固定负载 LOAD=48.0。thqu 跑 168 个 design point 的
HSPICE 扫描，用 `.measure` 取每点四级下降延迟 f1/f2/f3/fL（ns, logical-effort 模型），希望按
PDP（dA = dly × area）与 delay 两个指标排序找最优点。

## User voice (verbatim, from trace)
- 「你 check 一下这个网表，跟其他的对比一个，看看对不对，确认一下有没有问题」
- 「sp 文件参考其他几个仿真的，不要用你现在的」
- 「谁让你改这个参考文件的，给我恢复到上午的版本」
- 「把这个锥形驱动器的优化流程做成一个 skill，sp 文件就参考我现在的，如果后续需要修改的话也是以我这个为模板微调，你先看看思路，然后告诉我不用急着做，先问清楚我的需求」
- 「我希望用这个 skill 的时候，你可以问我基础的网表是什么，需要优化的 cell 是什么，有那些指标，然后以基础网表为基础生成不同 DOE 的网表，并进行 Check，check 完没问题后，告诉我激励是什么」
- 「交互式问答，指标名字（dly_avg, pwr 等）在你的 SP 里定义，组合的话你是用交互式确认清楚需求」
- 「我要优化的不仅仅是现在这个电路，以后还可能有其他的电路」
- 「这个能做成 agent 吗」

## What the agent did
1. 补 D09 网表（n4→x6→x6→x8，大 NAND nand2GSx4 + invGSx6→invGSx6→invGSx8），因无 `/proj/ddgoa` 写权限落到 `/home/thqu/doe_D09_n4x6x6x8/`。
2. 跑 168-design 扫描，按 PDP（dA=dly×area）与 delay 排序，输出 DOE ranking 表（列 variant_id/nand/inv chain/f1-f3/fL/dly/area/dA）。
3. 抽象成通用 DOE-optimizer skill：交互式问答 → 生成 DOE 网表 → HSPICE → 排序 CSV。反复迭代"通用性"（不针对单一电路、支持任意 block/mosfet 优化）。

## Gold standard (extracted for the case)
**DOE 排序 CSV 构建器**：读 `.lis` + `doe_variants.tsv` + `cell_library.tsv` → 合理点筛选（dly≤45）→
计算 dly/area/dA → 按 dA 升序 rank → CSV（13 列 rank,variant_id,nand,inv1,inv2,inv3,f1,f2,f3,fL,dly,area,dA）。
判分器在隐藏 B1（不同 design point 链，泛化）和 B2（同链但 cell_library 面积 ×1.15，反硬编码）上重跑脚本。

## Synthesized model (deterministic, source of truth = gen_assets.py)
```
LOAD=48.0; NAND_LE={n1:1.00,n4:0.85}; NAND_SIZE={n1:1,n4:4}
INV_LE=1.0; INV_AREA_PER=0.20; NAND_AREA={nand2GSx1:1.00,nand2GSx4:2.80}
DLY_TARGET=45.0
f1 = NAND_LE[n]*(1 + i1/(NAND_SIZE[n]*2.0))   # round 2dp
f2 = 1 + i2/i1                                 # round 2dp
f3 = 1 + i3/i2                                 # round 2dp
fL = 1 + 48/i3                                 # round 2dp
dly = round(f1+f2+f3+fL, 2)
area = round(NAND_AREA[nand] + 0.2*(i1+i2+i3), 2)
dA  = round(dly*area, 2)
reasonable = dly <= 45.0
```
dly 从 .lis 中**已四舍五入的** f 值求和（与 .lis 文本解析器口径一致）。

## Asset sets
- **A** (visible): 27 variants D02-D28; 25 reasonable (D21/D22 dly>45 剔除, D01 baseline 不入列); PDP-opt=**D04** (dA=51.0); delay-opt=**D28**.
- **B1** (hidden, generalisation): 16 disjoint chains E02-E17; 15 reasonable; 不同的 NAND/inv 组合, 测试脚本是否真正从输入读取而非背 A 的排名.
- **B2** (hidden, anti-hardcode): 同 A 的 27 链, 但 cell_library.tsv 整张面积表 ×1.15; PDP-opt 仍为 D04 但 dA=58.65≠A 的 51.0; 硬编码 A 面积的脚本必失败.

## Judge (check.py, 16 assertions a-p, sha1 d5cb80a06b)
a zip 含 doe_rank.csv · b 非空可解析 · c 表头 13 列严格匹配 · d 行数==合理点数 · e dly==f1+f2+f3+fL ·
f area==cell_library 四 cell 面积和 · g dA==round(dly*area,2) · h dA 升序 · i rank 1..N ·
j rank-1==PDP-opt · k min-dly==delay-opt · l nand 标签 · m inv 整数 · n 无不合理点 ·
o B1 泛化逐格一致 · p B2 反硬编码逐格一致.

## Self-verification
- ref (doe_rank_ref.py) PASS **16/16**
- negatives FAIL: badhdr (c), unsorted (h), hardcode_area (f/j/o/p)
- §4.9 three-fake FAIL: empty (b), fixedout (o/p), no-script (o/p)

## Layer
L1 — 离线 Python 复刻：读 .lis/variants/cell_library 文本，按逻辑努力模型计算 dly/area/dA 并排序，不真跑 HSPICE 仿真。

## Notes for next loop
- nrep6 之前一轮被 parked 为 "meta-skill DOE reject"——那轮只看到 skill-creator meta-task 表层，
  没挖到 DOE ranking 这个具体可判分的 gold deliverable。本轮重 peek 抓到 168-design 扫描 +
  rank CSV 表，才落地成 case。教训：**对 skill-creator / agent-builder meta-task，应继续挖到
  它要自动化的具体 EDA 输出（CSV/网表/报告），那才是可判分的 deliverable**。
- nrep6 trace 还有"交互式问答需求收集"那条线（用户描述要做的通用 DOE-optimizer agent），未来可考虑
  做成 L2/L3 的 multi-turn 交互式 case（不在本轮 L1 范围）。
