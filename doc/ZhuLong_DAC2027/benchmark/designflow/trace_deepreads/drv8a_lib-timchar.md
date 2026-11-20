# deepread — 1792314492243_drv8a (e0035227 @ hfeg0pkn004, mc=34)

- trace: `/home/e0035227/.cline/data/sessions/1792314492243_drv8a/1792314492243_drv8a.messages.json` (63 msgs, 680KB)
- model: glm-5.3-flash (cxmt-glm)
- domain: **digital / eda_other** (CCS timing library characterization). shard A.
- keywords: `virtuoso:273; .cdl:40; .gds:8; synopsys:5; netlist:5; analog:4; cmos:3; primetime:2`
- 已查重: 不在 4-shard jsonl (master set 284) 内 = 真 fresh。与 LibPVT-001(w6omm)/ETMExtract-001(t8yss)/LibToParm-001(9eh38)/DelPgLib-001(spnfh) **不同任务**（那些是 PVT 变体 / ETM 抽取 / lib→参数 / del_pg，本条是 **CCS .lib 完整时序弧抽取 + 多比特(MB)展开**）。

## 用户意图（逐字原文）
1. 「帮我解读这个路径下的文件：`/proj/lacaa/TV1_DBC_Virtuoso/workdir/e0029308/N7_Lib/tcbn07_bwph240l8p57pd_base_lvttt_0p75V_25C_typical_ccs.lib`」
2. 「可以，先读取主要摘要信息，不用遍历所有完整文件」
3. 「给我随便分析两个**MB电路**的完整时序弧」← 核心需求
4. 「内容太多可以摘取相关的一些主要典型部分，不用全部分析读取」

真实任务：用户拿到一个 7nm typical CCS 时序库（`tcbn07_bwph240l8p57pd_base_lvttt_0p75V_25C`），要 agent (a) 概览 lib，(b) **抽取 MB（multi-bit）电路的完整时序弧**（timing arc: from_pin→to_pin, timing_type, timing_sense, 表值）。agent 写了 `inspect_lib*.sh` / `mbgrep.sh` 用 grep/awk 解析 .lib。

## 金标准 / 判分要点（B档 synthesized 自含版）
- 输入：合成小 CCS .lib（A），含若干 cell：组合（INV/NAND/BUF/NOR，positive/negative unate）+ **多比特 cell（MB2INV / MB4DFF）** + 时序 cell（DFF：D→Q edge_triggered + setup/hold D→CLK + recovery/removal RSTB→CLK）。
- 交付：python 抽取器 `extract_arcs.py`，吃 .lib 输出结构化 JSON：`{library, cells:[{name, pins, bits, arcs:[{from,to,timing_type,timing_sense,scalar}]}]}`。
- 隐藏 B：不同 cell 集 / 不同位宽 / 不同 timing_type，防硬编。
- L2 真跑 (§4.2)：`subprocess` 真跑候选脚本于 B，断言**解析后的 JSON 结构**（非文本相似）。
- 难点核：① 多比特 bus 展开（D[0..n]→Q[0..n]）② 时序 timing_type 分类（combinational / setup / hold / recovery / removal / rising_edge）③ timing_sense（positive_unate / negative_unate / non_unate）④ 标量延迟值容差。

## 拟定 check.py 条件（≥8，对应断言）
a zip 含 extract_arcs.py · b 候选在 B 上 exit0 且产出合法 JSON · c JSON 顶层结构(library+cells) · d B cell 数=期望 · e 组合 arc sense/type 正确(如 NOR negative_unate combinational) · f 多比特 cell bus 展开(bit 数对) · g 时序 cell D→Q timing_type 含 rising_edge · h setup+hold arc D→CLK 存在 · i recovery/removal RSTB→CLK 存在 · j 标量延迟数值且在容差内 · k 无幻觉 cell(arc 数精确) · l §4.9 三假全 FAIL。

## infra
- 纯 python L1-boundary（.lib 文本解析），无需 vcs/calibre；self-verify 走 `tools.pyAether.run_code(lang=pyAether,host=aether)` 在 .75 跑 python（judge env 不可直连 .75，但 check.py 是纯 python 可本地 import 跑 + .75 二次验证）。
- assets 自含小 .lib，不需真实 7nm 库（用户库 /proj/lacaa 不可达且巨大）。
- 5 维全异(A vs B)：library 名 / cell 集 / 位宽 / timing_type 组合 / 标量值。

## 下轮第一件事（DEBT=1）
**直接合成 drv8a → EDA-Eval-DesignFlow-LibArcExtract-001**：写 assets_A/lib_A.lib + hidden/lib_B.lib + reference/extract_arcs_ref.py + check.py(≥12 条件) + negative(5) + negative_selftest.py → 自验(ref PASS + §4.9 三假 FAIL + negatives FAIL) → 断言闸门(k_rationale=k_check≥8) → 追加 A.jsonl → mark case(digital) → 日报。台账 drv8a 已 claim。
