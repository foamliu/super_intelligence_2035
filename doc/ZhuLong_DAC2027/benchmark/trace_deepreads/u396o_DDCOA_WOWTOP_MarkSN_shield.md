# trace_deepreads/u396o_DDCOA_WOWTOP_MarkSN_shield.md

**session**: 1795781071051_u396o · **user**: xiwang · **host**: hfeg0plg107 · **mc**: 396
**domain**: layout_aether · **size**: 1.28MB / 413 msgs · **scanned**: 2026-11-28 (r1491)

## 用户意图（真实 design_flow produce-task）
- U[0]: 「帮我找出DDGOA WOWTOP下面，调用到TECHLIB中MarkSN的地方，列出每个MarkSN的instance中shielded的信号」
- U[355]: 「不仅要产生需要shielding的信号，还需要这些信号是被哪些信号shielding的，例如是被vss shielding」

MarkSN 是 TECHLIB 里的 "check net shielding" 标记 cell，放在需要 shielding 的 net 上（ChkNet pin）。用户要把 WOWTOP 层级下所有 MarkSN instance 列出，每个带其 shielded signal（ChkNet pin 上的 net），并进一步要 shielding net。

## 助手工具链（关键摩擦 + 决策）
1. 先探索 /home/xiwang 已有脚本（explore_techlib.py / scan_lib.py / dump_ctx.py）+ dump TECHLIB MarkSN sch.oa token（发现 MarkSN 是 noConn symbol，ChkNet pin，PERC 标注 vbb(-0.5)<BNV<vss 等）。
2. 搭 pyAether 环境：找到 Aether 2025.09.sp1.hf7 安装，建 pyae_run.sh wrapper（设 AETHER_ROOT + PYTHONPATH=tools/pyaether/3.9/linux26-x86_64/lib/pyAether），建 marksN/lib.defs（INCLUDE /proj/ddgoa/V0/lib.defs + DEFINE TECHLIB）。
3. 用 RAG search_apis 找 API：emyGetAllInstHeaders / emyGetInstNames / emyGetAllNets / dbOpenCVByType。
4. collect_marksn.py + scan_marksn_targets.py：从 ddgoa_top/WOWTOP BFS，每 cell 用 emyGetAllInstHeaders 枚举 instance header，cellName=="MarkSN" 的拿 getInsts()→getInstTerms()→getNet() 收集 shielded net；chunked 跑（SCAN_CHUNK=150，state 文件断点续扫），跳过 basic/TECHLIB/noConn leaf。
5. collect_tree.py：建 fullmap.json（parent→children cell + inst name）用于 hierarchy path。
6. build_marksn_report.py：dedup scan records → norm_inst（strip 括号/空格，<>→[]）→ merge by (cell,inst) union libs/nets → 排序 → 写 CSV（parent_cell,markSN_instance,libs,shielded_signals）+ JSON（by_cell_inst + per_cell{libs,n_inst,nets}）+ MD report（top 25 cells by n_inst）。
7. U[355] phase 2（shielding net）：probe CDF params（scan_MarkSN_cdf.py 解析 cdfParameter ParamDef）—— trace 在 chunk 跑 CDF 时截止，phase 2 无最终产出。

## 真实产出（phase 1，完整）
- DDGOA_WOWTOP_MarkSN_shielded_signals.csv（83651B, 1514 行含 header）
- DDGOA_WOWTOP_MarkSN_shielded.json（270615B, by_cell_inst 1513 + per_cell 276 cells）
- DDGOA_WOWTOP_MarkSN_report.md（5190B）
- 关键数字：1513 merged instances / 276 cells / 1482 单 net + 31 多 net instance
- 样本：AG_*_Com I65 commonIP CC；ActAdrCtrl I1 ddgoa_cmos_digital;ddgoa_cmos_work ActAdr[17:0]；LP5TOP I7-I13 PreSampleBG*In[3:0]；DLDO_ChanMid I35 VintRef,VintRefLi（多 net）；P2StopFbUnitV5c I_MarkSN_612 DNPER,DNPER_OUT

## 抽象决策（造题）
真跑需 pyAether + Aether 安装 + /proj/ddgoa lib + TECHLIB GDS（GB 级 + 许可）无法 ship ⇒ 抽成自包含 Python marksn_shield_report.py：输入 pre-extracted scan_records.json（list of {lib,cell,inst,nets}，nets=ChkNet pin net=shielded signal），复刻 buildMarksnReport 算法（clean 去 ERR/空 + norm_inst 归一化 + dedup + merge by (cell,inst) union libs/nets + 排序 + CSV/JSON/MD），L0/L1 静态可判，LIVE-NA。Q2 不被骗：hidden B 用不同 cell 族（AnalogRefEdgeL_new/ControllerM5/Channel/...）+ 括号/bus inst 名 + 空/ERR net 测归一化与清洗，硬编 A 的 stub 在 B 下 cell 键不匹配挂。

## 交付
EDA-Eval-DesignFlow-MarkSNShieldReport-001（layout_aether, [L0,L1], LIVE-NA, 20 断言 check.py 独立复算, 5 negative 全 FAIL distinct, §4.9 trio 3-distinct c_run/c3/c5）。
