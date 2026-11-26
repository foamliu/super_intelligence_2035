# deepread: 1795073373751_cixxj (e0029308 @ hfeg0plg49, mc234)

- **trace**: 343 msgs / 1.4MB, agent=lead, sessionId=1795073373751_cixxj
- **host**: 10.129.8.86 (hfeg0plg49), user e0029308 (老用户, 首见 r888 g9bki NEW-user #22, 本轮新 session)
- **scan**: b_pool_1119.tsv fresh (mc>=10, cross-shard dedup A/C/D=0), claim r899

## 用户真实意图（trace 原话）

用户维护 `Auto_Check.py`（Hspice/AMS 仿真链真值表汇总 GUI 工具，`/proj/lacaa/TV1_DBC_Virtuoso/workdir/e0029308/BK/AI/Auto_Check/`），本轮做两件事：

1. **XNR cell 名提取修复**（核心）：`5_Truth_table_summary.py` 与 `10_CLC_truth_table_summary.py` 的 `extract_circuit_family()` 里三档兜底匹配（enhanced/traditional/generic）全部加 `re.IGNORECASE`，实测 `XNR2D1FSP51H204L6W35T6ELVT → XNR2`，顺带修 `XOR2D1→XOR2`、`AN2D1→AN2`、`NR2D1→NR2`（大写 D 匹配小写 d 模式）。
2. **进度条纳入"结果对比汇总"**：新增 `COMPARE_SHARE=10`，组合流程走完停在 ~90%，执行完 `_compare_in_dir` 后跳到 100%。
3. 后续：核对 Hspice/AMS 两侧 `extract_circuit_family` 一致性 → 发现 DFF 侧 `compare_truth_table.py` 的 `norm_cell()` 缺 IGNORECASE → 打补丁修复 → 给 `compare_truth_table.py` 的 `render()` 加「整体判定: PASS/FAIL」行 + GUI 弹窗着色。

## 关键产物（trace 里的代码）

### `extract_circuit_family()` (5_Truth_table_summary.py / 10_CLC_truth_table_summary.py)
- 工艺后缀剥离: `re.sub(r'(?:DBCP|FSP)\d+H\d+L\d+W\d+T\d+[A-Z0-9]*$', '', title, flags=re.IGNORECASE)`
- 32 条 FAMILY_RULES（按优先级）: cknd2/ckan2/ckbd/cklh/ckln/ckn/dcckb/dcckn/lhq/lnq/lhsn/lnsn/mux\d+n/mux\d+/del/nr\d+/aioi\d+/buff/clkbuff/and\d+/or\d+/nand\d+/nor\d+/xor\d+/xnor\d+/dff/lat/inv/buf/clk/oai\d+/aoi\d+
- enhanced 兜底: `^([a-zA-Z]+(?:\d+)?[a-z]*)d\d+` (IGNORECASE)
- traditional 兜底: `^([a-zA-Z0-9_]*[a-zA-Z_])(\d+)$` (IGNORECASE)
- generic 兜底: `^([a-zA-Z]+\d+)` (IGNORECASE)
- 全部未命中返回原名

### `norm_cell()` (compare_truth_table.py)
- `re.sub(r'(?:DBCP|FSP)\d+H\d+L\d+W\d+T\d+[A-Z0-9]*$', '', str(name), flags=re.IGNORECASE)`（补丁加了 IGNORECASE）

## reframe

trace 原意图是 maintenance/bugfix（修 IGNORECASE bug），reframe 成 **produce 型参数化提取器** `cell_family_extractor.py`：
- 把写死的 32 条 FAMILY_RULES + 后缀正则 + 三档兜底抽成 **spec.json 驱动**
- 对任意规则集 + cell 列表输出 `{mapping, stats, rules_count, cells_count}` JSON
- 隐藏 B 用结构性反转的 7 条规则（含 B 专属字面量 replacement `DEL_B`）+ 小写后缀测 case-insensitive + first-match-wins + 全部兜底路径
- B2 空 rules 测纯兜底防 stub
- 判分器在 B/B2 上断言正确提取 + 反硬编码 A（rules_count=7≠32, DEL_B≠del）+ 确定性

## 与既有 case 区分

- vs WmMt0Diag-001 (r898): WM/RM .mt0 诊断器，非 cell 名提取
- vs DffPvtCompareGen-001 (r897): DFF PVT 对比表生成器，非家族名提取
- 本 case 是首个 **cell-name-family-extraction** 型 + **maintenance-bugfix reframe** 型

## case

- **id**: EDA-Eval-DesignFlow-CellFamilyExtractGen-001
- **domain**: spice_sim, **layer**: L1
- **k_check = k_rationale = 14** (a-n)
- **自验**: ref 14/14 PASS, NEG_RC=5/5 (empty/print-only/hardcode-A/core-deleted/always-pass 全 FAIL), det 3-run sha256 一致
- **§4.9 (a)(b)(c)**: neg_01(empty)+neg_02(print-only)+neg_04(core-deleted) 全 FAIL ✓
