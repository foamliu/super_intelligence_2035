# r234 选料筛选轮（shard C）· 0 case · DEBT:1

> 日期 2026-11-08；r233 已交付 InstM0ShapePinIdentify；本轮选料筛选，10 条候选深读全判 non-seed，parked 入台账。

## 选料方法
- 扫描源：11-05 scan (`ssh_eda_search_20261105_192825`) + 10-28 scan 作为补充
- shard C mc>=15 + layout-affinity 打分 `score=ΣLAYOUT − ΣSIM`（LAYOUT={calibre,virtuoso,aether,cellview,dbGet,dbCreateInst,dbCreateRect,dbShape,pcell,layout,lvs,drc,pex,innovus,techfile}, SIM={netlist,hspice,schematic,synthesis,spectre,finesim,primesim,fsdb,verdi,ncsim}）
- 排除 ledger_C 383 session + 排除饱和用户（e0014566/xinqiaoz/miccao/ellawu/kenwang/yqlu/lvyy/jason17w/sinanz）
- 二次过滤：layout-geometry (dbCreateRect/dbCreatePath/dbShape/techfile/pcell>=8) OR calibre-dominant (cal/lvs/drc/pex>=30)

## 10 条候选深读结论

| session | user | mc | score | 判定 | 原因 |
|---|---|---|---|---|---|
| 1793846426867_874ye | e0044131 | 262 | 47 | **GONE** | session 文件已从 host 清理（host 仅剩 tzbss/d1yda/96crr） |
| 1782880010844_z79lb | e03179 | 64 | 29 | **DUP** | title="删除当前版图在所有M1的图形" = r232 jzzsv 同题；z79lb 是 6ktpb 的 fork |
| 1782879865358_6ktpb | e03179 | 64 | 29 | **DUP** | z79lb 的 fork-parent，同 M1-delete 任务 |
| 1793843002439_53nr3 | sinanz | 164 | 42 | **SCHEMATIC** | aeOpenDesign(lib,cel,**"schematic"**,edit)；全加器 stdcell 建例在 schematic view；wrong shard |
| 1791782422113_e1ll7 | steveny | 58 | 16 | **SCHEMATIC** | title="高亮 schematic view 中以 net 打头的 net"；Virtuoso SKILL 但 schematic；wrong shard |
| 1793846988442_zhq3r | e0039669 | 147 | 20 | **Q&A** | prompt="hi"，title="hi"，普通对话 scene，status=cancelled；非真实任务 |
| 1793782993086_d1yda | e0044131 | — | — | **Q&A** | title="华大aether如何批量copy cell"；AskEDA 知识库问答助手（RAG），非工具执行 |
| 1793772458676_tzbss | e0044131 | — | — | **SCHEMATIC** | title="是否可以帮我分析原理图"；schematic 分析 |
| 1792395640746_nce9i | colinxu | 116 | 35 | **Q&A** | title="当前打开的电路中存在vddtest这个pin吗？"；pin 存在性 Q&A，status=cancelled |
| 1793614615410_y612r | sinanz | 264 | 43 | **EXP** | title="DS_circuitEdit"，status=failed；circuit-edit A/B 模型对比实验，非有机 layout |

## 关键发现
1. **11-05 scan 已 3 天陈旧**：e0044131 的 874ye（mc=262，top1）已被清理；scan 与 host 现状脱节。
2. **shard C 真实 layout 候选枯竭**：mc>=15 + layout-affinity 顶部候选绝大多数是 (a) schematic view 任务（pyAether aeOpenDesign "schematic" / Virtuoso SKILL schematic）→ 属其他 shard；(b) Q&A/RAG（AskEDA 知识库）→ 无可执行交付物；(c) 已交付 case 的 fork/dup；(d) 饱和用户（e0014566 65 条）。
3. **scan keyword 无法区分 layout vs schematic**：cellview/dbGet/dbCreateInst 在两类 view 都出现；layout-geometry 二次过滤（dbCreateRect/dbCreatePath/dbShape/techfile/pcell）也仅返回 z79lb/6ktpb（dup）。
4. **calibre-dominant (physical_verify) 候选全在 ledger**：cal>=30 无新候选。

## 未深读但值得下轮关注（不在 11-05 scan，host 现存）
- **1793954643815_96crr**（e0044131@10.129.2.13）：title="项目实操"，cwd=/ai_sandbox/lacaa/TV1_FS/agentdir/e0044131，status=completed，input=37M tok。**超大**（37M input tok），需 scp 后本地解析，下轮若选需单独深读轮。e0044131 是 NEW user（0 ledger）。
- **1793861310425_dmk4f**（sinanz@10.129.2.14）：title="我在路径.../Skills"，同 sinanz circuit-edit 上下文，**大概率 schematic**，低优先。
- **6huq4**（colinxu, mc=110, pyAether+schematic+cellview）：schematic=92 dominant，**大概率 schematic**，低优先。
- **e0039669**（10.129.2.11）：NEW user，仅 zhq3r(parked "hi")+6g756 未扫，可下次 rescan 后重评。

## 下轮（r235）第一件事：补 DEBT:1
1. **触发 .75 rescan**：11-05 scan 陈旧，需新 scan 捕获 11-06~11-08 新 session（e0044131/colinxu/e0039669 等新用户活跃）。
2. **降 mc 到 >=10** 或 **扫 10-28 scan 独有 session**（10-28 scan 有 colinxu nce9i/6huq4 等 11-05 未复扫的）。
3. **优先 pg_layout**（34 最低覆盖）与 **physical_verify**（calibre 关键词直查，不依赖 layout/schematic 区分）。
4. **若 rescan 仍无 layout seed**：考虑深读 96crr（37M tok，需分段），或对 ledger 中 parked 的 "schematic-view" 候选重新评估是否可转 B-synthesized layout 题（如把 53nr3 的 full-adder stdcell 建例改成 layout view 建例）。
5. **🚫 禁止连续两轮只深读**：r235 必须交付 1 case，否则改主动 rescan + 降阈。

## 台账
- parked +10（z79lb/6ktpb/53nr3/e1ll7/zhq3r/nce9i/874ye/y612r/2m2ja/1y31v）
- ledger_C：case 228 · parked 171 · 已动过 399
