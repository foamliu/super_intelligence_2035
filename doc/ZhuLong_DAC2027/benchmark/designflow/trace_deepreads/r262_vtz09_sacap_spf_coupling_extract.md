# r262 deepread — vtz09 (rongtaoy) SA BL coupling SPF extraction

## trace source
- user: rongtaoy  host: hfeg0pkn001 (10.129.2.10)  sid: 1790057512461_vtz09
- mc: 125  keywords: pex:563 netlist:280 transistor:70 .cdl:39 aether:33 .gds:33 lib.defs:28 lvs:21
- agent: lead  total_msgs: 126  real_user_turns: 9
- NEW user (rongtaoy 首个 shard-C case)

## user real intent (提出需求轮, 未给根因)
- U#4 (ts=1790061845092, 提出需求): 「现在电路更新了，我需要做改动：前面8个col不变，中间的ce/cc没有了，变成了cec，且一共有320个，所以cec<col> num = col*256 + n + 2048；col≥8 num = col*256 + n + 320；因为一个n里面有256个bl，cec是256+64，之前cc+ce是256*2+128，这是修改的逻辑。写一个sacap的md，说清楚BL的顺序逻辑和我们的改动以及日期版本路径。」
- U#5 (ts=1790063102792): 「我们要改的首先是 /proj/ddgoa/V0/ver/pex/rongtaoy/0.sacap_noanb/sacap_0627.pl …我们目前不动py脚本！」(指明改 .pl 不动 .py)
- U#6 (ts=1790063595459): 「切记 sacap_0922 的修改一定基于 0627 且只改动我说的那一小部分，且把任意改动详细完整记录在 md！这是红线！！！」
- U#7 (ts=1790065167632): 「/home/rongtaoy/Documents/python/coupling_compare 这里的几个 py 脚本都是什么功能？告诉我输入，输出，和目的即可」(问 coupling_compare 工具链功能)
- U#8 (ts=1790065790913): 「重新考虑启用 sacap_extract_V0.py，他有这方面的问题吗？」
- U#9 (ts=1790072000118, 提出需求): 「他的计算规则是不是并不完整，每一个<name>的 coupling 的计算规则是否和 sacap_0922.pl 一致？其中 bla/blb 的计算规则例外，他是一个 bla/b 和其他所有 net（包括任意 net，区别与 BL2BL 只包括任意 bl）。」
- U#1 (ts=1790057513876): 「我已经定位到根因了…0921BK 命名和 0916BK 不一样…msax320_fbcc cell…c00Bla<255..0> c01Bla<63..0> 单字母 c 前缀（320 bitline）」(用户已给根因 → 不能作 A 档任务说明，仅作 hint)

## grounding (真实产物, scp 自 .75:/home/rongtaoy/Documents/python/coupling_compare/)
真实文件可读（/proj/ddgoa 项目目录 permission denied，但 ~/Documents/python/coupling_compare/ 可读）：
- README.md (8830B) — 完整工具链文档
- sacap_extract.py (604 行, 21879B, executable) — **agent 真实产物** (v1.7a, 对齐 sacap_0922.pl)
- sacap_compare.py (229 行) — 两 BK CSV 对比
- sacap_visualize.py (462 行) — 6×6 耦合矩阵可视化
- spf_cc_extract.py (272 行) — SPF 轻量提取器

### sacap_extract.py 核心逻辑（agent 真实产物）
- **BL group 编号公式**（任务核心改动）:
  - `cn<col>bl[a|b]<n>` (col≤7) → `col*256 + n + 0`
  - `cn<col>bl[a|b]<n>` (col≥8) → `col*256 + n + 320`  (NEW: 旧版 640)
  - `cec<col>bl[a|b]<n>` → `col*256 + n + 2048`  (NEW: ce/cc 合并为 cec)
  - 4480 groups, each 6 nets: Bla/SaBla/Bla_local/Blb/SaBlb/Blb_local
- **net 类型识别** bl_type(): Bla_local/Blb_local/SaBla/SaBlb/Bla/Blb/other (按 seg.endswith)
- **ab_of()**: Bla→'a', Blb→'b'
- **signed cap sign rules** (name_rule):
  - total_BL2BL: same-side(a==a/b==b) → +cap; cross-side → -cap
  - NCS (NCSin_0): Bla → -cap, Blb → +cap
  - PCS (PCSin_0): Bla → +cap, Blb → -cap
  - NCSGate (SanEn[ABCD]): Bla → -cap, Blb → +cap
  - PCSGate (SapEn[ABCD]): Bla → +cap, Blb → -cap
  - signal: Bla → +cap, Blb → -cap
- **build_group_map_from_spf()**: 两遍扫描 .spf_CC
  - 第一遍: `*|NET <name> <pincap>` 行 → 收集顶层 bitline (group_of_top_bitline 可解析) + 层级 net (正则 `^(.+?)\.(XI_[^.]*)<(\d+)>\.(Bla|Blb|...)<(\d+)>$`)
  - 第二遍: `C<id> <n1> <n2> <cap>` 行 → 层级 net 与顶层 bitline 耦合投票定列 (n == M*4+i 匹配)
  - 每 (blk, sa) 取票数最多 (prefix, col) → 为层级 net 算 group
- **extract_caps()**: 流式扫 C 行, 双向归类 cap[group][net][couplegp][couplenet]=fF; *|NET 行 → pincap[net]=fF
  - classify_couplegp(): NCSin_0→NCS, PCSin_0→PCS, SapEn[ABCD]→PCSGate, SanEn[ABCD]→NCSGate, in gpmap→groupN, sig pattern→sig, else other
- **summarize()**: 每 group 算 total_BL2BL = Σ|g2g_noise[couplegp]| (couplegp 以 group 开头且 ≠ self) + NCS/PCS/NCSGate/PCSGate/signal signed + Bla/Blb self pin cap
- **to_ff()**: PF→fF (×1e3), 科学计数法拉拉→fF (×1e15)
- **输出**: <outdir>/BL_index.csv (BL,group,Bla,Blb,SaBla,SaBlb,Bla_local,Blb_local) + <name>/summary_report.txt + <name>/BL<g>.csv (net1,net2,outname) + <name>/all_top<N>.csv
  - outname 格式: total_BL2BL → `BL{g}__{type1}__BL{dst}__{type2}_{signed:+.8f}`; 其他 → `BL{g}__{type1}__{name}_{signed:+.8f}`

### SPF .spf_CC 文件格式（StarRC EXTRACTION:C 纯电容输出）
- `*|NET <netname> <pincap_value>` — 节点行 (pincap = 对地/自电容)
- `C<id> <net1> <net2> <cap_value>` — 耦合电容行 (cap = 两 net 间耦合)
- cap 值单位: PF 后缀 (如 1.234e-15PF) 或科学计数法拉拉 (1.234e-15)

## 为何 B 档重定义为离线 SPF 解析器
- 真实 StarRC/PEX 二进制 + rongtaoy 私有项目 /proj/ddgoa 在 .75 对 e0031982 不可访问 (permission denied)，无法取真实 .spf_CC 作 A 输入；
- 但 trace 的 grounding 价值在「SPF .spf_CC 格式解析 + BL group 编号公式 + signed cap 规则 + total_BL2BL 计算」规范提取——agent 的真实产物 sacap_extract.py 是 stdlib only (argparse/csv/os/re)，可参数化。
- 故重定义为 `sacap_extract.py -spf <spf_CC> [-name ...] [-top ...] [-outdir <dir>]`(stdlib only)：解析合成 .spf_CC → build_group_map → extract_caps → summarize → 输出 BL_index.csv + per-metric reports。
- 判分用合成的 .spf_CC (含 cn/cec bitline + 层级 net + C 耦合行 + *|NET pin 行)，验证 group 编号/signed cap/total_BL2BL/输出结构。

## DISTINCT from 现有 physical_verify 系
- r248 SpfRcAggregateAudit (SPF RC 聚合审计, 电阻电容聚合统计) — 不同: 本 case 是 SPF **耦合电容**提取+group 编号+signed cap 规则, 非 RC 聚合
- r257 GloryRcFlowSetup (RC flow 编排) — 不同: 本 case 是 PEX 后处理解析, 非 flow 编排
- r250 HcellPairGen / r251 LvsAmbiguityDiag / r254 EmyCdlNetlistExtract / r255 CmMaOpTableGen / r256 LdrSvrfRuleGen / r258 ConnChkSummaryGen / r259 DrcConnectGraphGen / r260 ErcSchMarkNetDump / r261 HilightCsvGroupGen — 全不同域 (LVS/DRC 规则/连通图/ERC marker/高亮分组)
- 本 case 是 **PEX SPF 耦合电容提取 + SA bitline group 编号公式** 域 (首次 ground on StarRC .spf_CC 解析 + signed coupling cap 语义)
