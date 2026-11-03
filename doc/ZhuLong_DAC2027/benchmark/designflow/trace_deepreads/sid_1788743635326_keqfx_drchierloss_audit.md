# 深读笔记 — sid_1788743635326_keqfx (miccao, hfeg0plg37, mc=303)

**case**: EDA-Eval-DesignFlow-DRCHierLossAudit-001（physical_verify, B-档 synthesized, L1-boundary）
**轮**: shard C #64 (2026-11-03)

## trace 来源
- user: miccao, host: hfeg0plg37 (10.129.32.47), session: 1788743635326_keqfx.messages.json
- match_count: 303 (calibre:392; netlist:239; transistor:92; aether:87; schematic:46; cellview:38; .gds:34; pyaether:33)
- msgs: 318 (user:160 / assistant:158), 16 user_input 块
- 本地路径(.75 NFS): /home/miccao/.cline/data/sessions/1788743635326_keqfx/1788743635326_keqfx.messages.json

## 真实任务（user 原话逐字）
- UI#0: `分析这个log: /proj/drvsa/V0/ver/drc/drvsa_top/WOWTOP/0906/rundrc.log 看哪步耗时最长`
- UI#19: `分析下这条耗时最长的rule图形计算的情况`
- UI#31 (skill-creator 详述): `你是一个argus/calibre log分析大师，主要任务是通过分析DRC log来看本次job主要花费时间在哪里。首先你要对log进行整体分析，看DRC的几个大模块的时间分布，在总结后再进入细节分析。连接关系的建立时间要展现出来，重点在于图形计算的时间，要将花时间最长的图形计算步骤摘出，溯源到是哪条rule，定位到rule后，对这条rule每一步计算的图形数量做统计，看他的FGC和HGC比，来判断是不是图形失去了hierarchy关系，导致计算量过大`
- UI#102: `将耗时最长的connet对应的deck中的步骤提取出来，放到报告里`
- UI#112: `你能看出哪些连接关系实际上没有用上的吗`
- UI#128: `将计算后层次化被破坏的运算步骤单独列出，标明步骤名，时间，hgc/fgc前后变化`
- UI#294: `将我分析drc log的这些思路封装成一个skill，结果就是得出log的拆解报告`

## 真实 skill 产物
- /home/miccao/.cline/skills/calibre-drc-log-analysis/SKILL.md（四模块拆解报告 skill）
  1. 各大步骤时间占比总结（TOTAL CPU/REAL、模块 REAL 占比、cumulative WITH WIDTH/EDGE/SIZE/BOOLEAN/CONNECT）
  2. 连接关系建立时间总结（每次 CONNECT REAL/NETS/EPINS、cumulative、冗余分析 near-empty/冗余路径/DISCONNECT 重做）
  3. 图形计算部分（Top-N 按 REAL 排序、HGC/FGC/VHC、HGC→FGC 放大倍数、VHC=F 比例、huge cell 清单 instance≥1M 或 polygon≥1e5）
  4. deck 优化建议（瓶颈 rule 改前/改后、预估节省、优先级）

## Calibre DRC-H log 关键字段（来自 SKILL.md，case 合成依据）
- 模块完成: `--- <MODULE> MODULE COMPLETED.  CPU TIME = X  REAL TIME = Y  LVHEAP = ...`
- 操作计时块（两行）:
  `<Layer> (HIER TYP=.. CFG=.. HGC=.. FGC=.. HEC=.. FEC=.. IGC=.. VHC=.. VPC=..)`
  `CPU TIME = a  REAL TIME = b  ... OPS COMPLETE = m OF N  ELAPSED TIME = c`
  - HGC=层次图形数 / FGC=扁平图形数 / VHC=层次压缩标志(T 保留 F 放弃) / VPC=平面压缩
- RuleCheck 完成: `DRC RuleCheck <NAME> COMPLETED. Number of Results = X (Y)`
- CONNECT: `CONNECT ... completed. NETS = N EPINS = E CPU TIME = C REAL TIME = R` + `Cumulative CONNECT Time`
- huge cell: `ARGUS LAYOUT INPUT INFORMATION` 段 `cell: <name>, instance: <N>, box: <B>, polygon: <P>, path: <path>, text: <T>`
- 总览: `--- TOTAL CPU TIME = X  REAL TIME = Y` / `--- PROCESSOR COUNT = N` / `--- TOTAL RULECHECKS EXECUTED = N` / `--- TOTAL RESULTS GENERATED = M`

## 与既有 case 区别
- r27 DRCTimeStats-001 = 每条 rule CPU/REAL 总耗时排序 + nested-:: 变量聚合 + HIER 多变量均分（耗时排序主题）
- 本案 = hierarchy 失效审计：VHC=F 检出 + HGC→FGC 扁平爆炸 + huge cell + CONNECT 冗余 + per_rule has_loss + Top-N（hierarchy 主题），断言全独立

## A-档 disqualified 理由
gold 依赖私有 /proj/drvsa/V0/ver/drc/drvsa_top/WOWTOP/*/rundrc.log（真实 calibre log，沙盒无权访问且几十万行），不可在 .75 sandbox 复现 → B-档 synthesized L1-boundary（离线 Python3 stdlib 解析合成 log fixture）。

## 合成产物
- assets/rundrc_A.log（可见 A）+ assets/hidden/rundrc_B.log + B2 + B3 + gen_logs.py + hidden_manifest.json
- reference/drc_hier_audit.py（参考解）+ check.py（14 断言 a-n）+ reference_submit.zip + negative/(5 fake)
- jsonl: EDA-Eval-DesignFlow_C.jsonl 第 66 行

## 自验
- ref PASS 14/14 ✓
- 5 negative 全 FAIL（NEG_RC=0）✓
- §4.9 (a)空壳 (b)只 print (c)删核心 三假 + 2 naive(vhc_only/always_loss) 全 FAIL ✓
- k_rationale=k_check=14 ≥ 8 GATE PASS ✓
