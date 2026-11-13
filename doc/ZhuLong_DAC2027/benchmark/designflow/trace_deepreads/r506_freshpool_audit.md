# r506 fresh-pool 独立审计 (2026-11-13)

**动机**：C 线自 r405（第 32 条 case RsCalcFlowOrchestrator-001）起连续 ~100 轮 0-case（r406–r505 全 omission 维护），MEMORY 反复写「质量饱和」「peek N 全 REJECT」。2026-11-11 用户令 rule 4 要求「池枯竭」结论须有 `mc10.fresh==0` 证据；实测 mc10.fresh=438≠0。本轮独立核查 fresh 池的域分布，判断 0-case 是真质量饱和还是 peek-REJECT 过激。

## 方法
- mc-matrix（src=summary_1109.tsv，shard C keywords 过滤后 3325 unique session）：mc≥10 fresh=438。
- .75 上跑 `cand_all.py`：对 summary.tsv 按 mc≥10 + shard C keywords 过滤、按 anchor 去重 → 2520 unique anchor（含已 ledger 的 711）。
- 取 top-180（mc≥385）+ low-mc [10,100) 头部，逐条与本地 trace_ledger_C.tsv（711 anchor）交叉，区分 fresh vs ledgered，并按 keywords 判域归属。

## 发现 1：高/mid mc（mc≥385，top-180）fresh 几乎全非 C 域
top-180 中 fresh（不在台账）的 session 域归属：
- **jason17w 簇**（xm22u/xh3mj/le1s7/lc81i/b460k/atgt9，6 session，mc 497–515）：verilog:drc:netlist = ~3800:2700:1500，verilog 主导，D 域（digital/netlist），drc 是命中词非主驱。
- **e0039602 簇**（j26fe/17trm/9dytw/cydnq/1nsgi/s9bc9/bghqo，7 session，mc 386–460）：verilog:lvs:netlist:drc，verilog 主导，C 侧仅 lvs 副命中；同用户多 session 疑似 near-dup。
- 68gc9（kli，mc431）：netlist:pex:lvs，netlist 主导，C 侧 pex/lvs 副命中。
- la00c（mc415）：hspice:virtuoso = SPICE（B 域）。
- 5hjg7 / wl9i4 / jkvft：netlist:verilog（D 域）。
- p64wo / uiykd：analog:drc，analog 主导。
- poh36（mc398）：cmos:schematic:aether:drc，cmos/schematic 主导。
- jhdvn（mc496）：cmos:schematic:aether，analog 主导。

**结论 1**：mc≥385 的 fresh 池被 verilog/netlist/spice/analog 主导；纯 C 域（layout_aether/layout_virtuoso/pg_layout/physical_verify）的高/mid mc session 已全部 ledgered。这与 MEMORY「高 mc C 域饱和」一致 —— **此段质量饱和成立**。

## 发现 2（关键）：low-mc [10,100) fresh 池含 substantial C 域候选
low-mc 头部（mc 97–99）fresh 中存在 aether/drc 主导的 session，**非 Q&A / 非 env-dependent**，未经深读：
| anchor | user | host | mc | keywords（C 域相关） |
|---|---|---|---|---|
| 1793758047628_xyaxc | adaml | hfeg0pkn002 | 98 | aether:987;waveview:667;drc:223;pyaether:96;calibre:62;virtuoso:58;schematic:58;lvs:55 |
| 1789973143978_7glsf | davidwu | ? | 97 | aether:2540;pyaether:361;netlist:135;schematic:126;drc:22;cmos:14;calibre:13 |
| 1789975385741_egm8i | davidwu | ? | 98 | aether:704;schematic:283;pyaether:126;floorplan:124;dbopencv:78;drc:47 |
| 1790168650173_mdx5g | e0041123 | ? | 98 | drc:1506;aether:528;pyaether:413;techfile:147;lib.defs:81;.def:42;calibre:13 |
| 1790219463471_6zy8a | e0041123 | ? | 98 | drc:1284;aether:1034;lib.defs:306;techfile:187;pyaether:92;calibre:26（疑 mdx5g near-dup 同用户）|
| 1793869595986_r342a | kenwang | ? | 98 | drc:1711;calibre:151;.def:29 |
| 1793666914540_bsypf | e0047488 | ? | 98 | .gds:124;drc:123;aether:96;gdsii:46;pyaether:43;techfile:20 |
| 1791768354807_ytvn2 | thomasz | ? | 97 | drc:920;.gds:52;.cdl:4;pyaether:3;aether:3 |
| 1789621916894_m8ndm | ellawu | ? | 97 | drc:393;.gds:183;aether:39;pyaether:26;calibre:22 |

**结论 2**：low-mc fresh 池**并非** C 域真空。`7glsf`（aether:2540 单峰）、`xyaxc`（aether:987+drc+calibre+virtuoso 四峰）、`mdx5g`（drc:1506+aether:528）等是 substantial layout/physical_verify session，命中数远超「Q&A / env-dependent」阈值，**值得深读**。

## 判断
- 高/mid mc C 域饱和**成立**（top-180 fresh 全非纯 C 域）。
- 但 r406–r505 的 100 连 0-case 不能完全归因「质量饱和」：low-mc C 域 substantial 候选存在，r414/r460 的「low-mc peek 全 REJECT」结论**本轮未复验**（仅看 keywords，未 scp messages.json 深读）。这些候选可能被 peek-REJECT 过激筛掉，或确有 near-dup/weak —— **需下一轮真深读定论**。

## 下轮行动建议（优先级最高）
1. **scp + 深读** `1793758047628_xyaxc`（adaml，aether:987+drc+calibre+virtuoso，最均衡 C 域四峰）→ 若为 produce-task 则 claim 造 case；若 weak/near-dup 写深读笔记。
2. 若 xyaxc 不行，依次深读 `7glsf`（aether 单峰最强）→ `mdx5g`（drc+aether）。
3. **目标**：打破 100 连 0-case；若 3 条全 weak，方可加强「low-mc C 域亦饱和」结论。

## 未做
- low-mc [10,97) 段未扫（438 fresh 中 mc<97 的尾部）。
- 上述 9 条均未 scp messages.json（仅 keywords 判定，非深读证据）。

## 口径
- mc-matrix src=summary_1109.tsv（A/B 已换池 11/09 ✓）。
- mc≥10 fresh=438≠0 ⇒ 按用户令 rule 4 **不写**「池枯竭/池耗尽」。
- 本审计为 keywords 级，非 trace 级；下轮须真深读。
