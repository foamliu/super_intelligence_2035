# Deepread r686 — jzeng / wimgg — DRC PG-Open Rule Generation

## trace_source
- user: jzeng
- host: 10.129.2.12
- session_file: 1794307198596_wimgg
- session dir: /home/jzeng/.cline/data/sessions/1794307198596_wimgg/
- match_count: 288 (keywords: drc:1208; calibre:392; lvs:231; hierarchy:47; connect:38; fgc:62; hgc:60 — top3 drc/calibre/lvs, C-core dominant cTop=3)
- msgs: 274 (USER 137 / ASST 137), tool_use 133 (48 editor, ~0 bash via editor), thinking 136
- size: 1.15 MB messages.json
- claimed: r686 (shard C), domain physical_verify

## real task summary (user intent)
用户 U#0 原话：「写一条rule,能在calibre DRC中跑出来layout中金属层M1 power/ground断开的情况」
= **produce-task**: 编写一条 calibre DRC rule (.drc)，检测 layout 中 M1 金属层 power/ground (VDD/VSS) 网断开(open)的情况。
交付物 = /home/jzeng/Desktop/M1_PG_OPEN.drc (一个可被 `calibre -drc` 编译执行的 SVRF rule file)。

后续 U#1-U#3 = 调试编译错误 (Error SYN1 unrecognized operation / Error INP7 incomplete keyword specification: expand / Error SYN1 line 45)，
助手反复修复 SVRF 语法 (EXPAND → `EXPAND EDGE layer OUTSIDE BY value`，`WIDTH M1_VDD < value` → `M1_VDD WITH WIDTH < value`)。
真实任务形态 = rule authoring + syntax-fix 闭环，核心交付 = 结构正确、可编译的 .drc rule。

## assistant tool chain
- editor 48 次 (写/改 /home/jzeng/Desktop/M1_PG_OPEN.drc)
- run_approved_command 跑 calibre -drc 编译验证 + cleanup 脚本
- read_files 读 .drc 回读检查
- 最终产出 M1_PG_OPEN.drc: 4-method PG-open detection rule (见下结构)

## 真实 .drc 结构 (从 trace msg#11 editor new_text 提取)
```
// SECTION 0 — VARIABLES (tune per node)
VARIABLE _M1_PG_TRUNK_WIDTH_   0.80   // main trunk width threshold (um)
VARIABLE _M1_PG_MIN_WIDTH_     0.10   // min acceptable width on power net (um)
VARIABLE _M1_PG_NOTCH_RATIO_   0.50   // notch depth ratio
VARIABLE _M1_PG_SLIT_WIDTH_    0.20   // min slit width to flag as open (um)
VARIABLE _M1_PG_EXT_LENGTH_    0.05   // extension length for edge ops (um)

// SECTION 1 — NET DEFINITION
M1NET_VDD = M1NET M1 INTERACT VDD_TXT
M1NET_VSS = M1NET M1 INTERACT VSS_TXT
M1_VDD = M1 INTERACT M1NET_VDD
M1_VSS = M1 INTERACT M1NET_VSS
M1_PG  = M1_VDD OR M1_VSS

// SECTION 2 — METHOD 1: ISOLATED PG REGION (完全断开)
//   CONNECT + 找与主 trunk 不连通的带 PG text 的 M1 孤岛

// METHOD 2: MIN WIDTH / NECK
//   M1_PG WITH WIDTH < _M1_PG_MIN_WIDTH_

// METHOD 3: NOTCH / SLIT PENETRATION
//   INT <> / EXT <> + DFM 检测深 notch

// METHOD 4: VIA-CONTACT SEPARATION
//   EXPAND EDGE ... OUTSIDE BY + via 孤立检测

// OUTPUT DRC results database
```
SVRF constructs: VARIABLE, M1NET, INTERACT, OR, CONNECT, CONNECTED, WIDTH (WITH WIDTH), INT <>, EXT <>, EXPAND EDGE ... OUTSIDE BY, DFM SHIFT/EXPAND, OUTPUT.

## reframe plan — EDA-Eval-DesignFlow-DrcPgOpenRuleGen-001
**为何 reframe**: 真实交付需 `calibre -drc` 编译验证，SUT 沙盒无 calibre 引擎、真实 layout/GDS 不可入沙盒 →
**mock-behavioral reframe** (承 r645-r685 家族; 新子型 `drc-pg-open-rule-gen`, **②档 source-semantic-generate**:
spec JSON → SVRF .drc 文本生成, 需实现变量插值 + section 模板 + SVRF 语法正确性, 非纯 regex)。
判分不可跑 calibre → 改为对生成 .drc 做 **结构 + 语法 + spec 一致性** 静态校验 (16 条件)。

**核心差异 vs 历史 case**:
- r685 AutoCellTclFlowValidate = **validate** given TCL flow (8 hard constraints) — 校验既有文件
- r681 CalibreDfmCmdExtract = **classify** deck commands (提取计数)
- r679 LvsGuiConfigGen = SKILL.md → Python config **生成**
- **本 case = spec JSON → SVRF .drc rule 生成** (rule-authoring generation + syntax validation), C 域首例 SVRF-rule-generator

### 交付接口
- prompt: 真实场景 (jzeng 写 M1 PG-open DRC rule, 自然语言, 保留真实用户名/路径/工具)
- task_brief.md: ≤3 行 (交付 pg_open_rule_gen.py + rule_spec.json → outputs/M1_PG_OPEN.drc)
- mode: design_flow, entry_point: outputs/submit.zip, test: check(deliverable, workdir) 双参

### 资产
- **asset A (可见)**: rule_spec_A.json
  - metal_layer: "M1", vdd_text_layer: "VDD_TXT", vss_text_layer: "VSS_TXT", via_layer: "M1_VIA"
  - params: trunk_width=0.80, min_width=0.10, notch_ratio=0.50, slit_width=0.20, ext_length=0.05
  - layout_path / source_path / output_db
- **hidden B (反硬编, 全异)**: rule_spec_B.json
  - metal_layer: "M2", vdd_text_layer: "VDD2_TXT", vss_text_layer: "VSS2_TXT", via_layer: "M2_VIA1"
  - params: trunk_width=1.20, min_width=0.14, notch_ratio=0.45, slit_width=0.24, ext_length=0.08
- **hidden B2 (退化)**: rule_spec_B2.json
  - metal_layer: "M3", vdd_text_layer: "VDD3_TXT", vss_text_layer: "VSS3_TXT", via_layer: null (无 via)
  - params: trunk_width=0.60, min_width=0.08, notch_ratio=0.50, slit_width=0.18, ext_length=0.04
  → METHOD 4 via-contact 应缺席, 退化最小 rule

### gold reference: pg_open_rule_gen.py (纯 stdlib)
读 rule_spec.json → 生成 M1_PG_OPEN.drc, 含:
- header comment (rule name, description, layer mapping, usage)
- SECTION 0 VARIABLE 声明 (5 个, 值来自 spec.params)
- SECTION 1 NET DEFINITION (M1NET × 2 + layer extract × 2 + OR combine, 层名/网名来自 spec)
- METHOD 1 ISOLATED REGION (CONNECT 主 trunk + 找不连通孤岛)
- METHOD 2 MIN WIDTH (WITH WIDTH < min_width)
- METHOD 3 NOTCH/SLIT (INT <> / EXT <> + DFM)
- METHOD 4 VIA-CONTACT SEPARATION (EXPAND EDGE ... OUTSIDE BY + via 层, 仅当 via_layer ≠ null)
- OUTPUT DRC results database
- stdout 汇总头: `PG-Open DRC Rule Generated`

### check.py 16 条件 a-p
1. (a) zip 内 py_compile submit.py 通过
2. (b) B 退出 0 + stdout 含 'PG-Open DRC Rule Generated' + 写非空 .drc
3. (c) B .drc 含 5 个 VARIABLE 声明, 名字 _M2_PG_TRUNK_WIDTH_/_M2_PG_MIN_WIDTH_/_M2_PG_NOTCH_RATIO_/_M2_PG_SLIT_WIDTH_/_M2_PG_EXT_LENGTH_, 值来自 B params (1.20/0.14/0.45/0.24/0.08)
4. (d) B .drc 含 M1NET 定义 × 2 (M2NET_VDD2 = M1NET M2 INTERACT VDD2_TXT / M2NET_VSS2 = M1NET M2 INTERACT VSS2_TXT) — 层名/网名来自 B spec
5. (e) B .drc 含 layer extract (M2_VDD2 = M2 INTERACT M2NET_VDD2 / M2_VSS2 = M2 INTERACT M2NET_VSS2)
6. (f) B .drc 含 OR combine (M2_PG = M2_VDD2 OR M2_VSS2)
7. (g) B .drc 含 METHOD 1 ISOLATED REGION (CONNECT + 孤岛逻辑, 引用 PG 网)
8. (h) B .drc 含 METHOD 2 MIN WIDTH, 用 WITH WIDTH < _M2_PG_MIN_WIDTH_ 语法 (非 "WIDTH layer <")
9. (i) B .drc 含 METHOD 3 NOTCH/SLIT (INT <> 或 EXT <> 出现)
10. (j) B .drc 含 METHOD 4 VIA-CONTACT, 引用 via_layer M2_VIA1 + EXPAND EDGE ... OUTSIDE BY 语法
11. (k) B .drc 含 OUTPUT DRC results database 语句
12. (l) B .drc 所有 EXPAND 均为 `EXPAND EDGE ... OUTSIDE BY` 完整形式 (无 incomplete keyword)
13. (m) B .drc 所有 WIDTH 检查为 `layer WITH WIDTH < value` 形式 (无 "WIDTH layer <" 裸式)
14. (n) B2 退化 (via_layer=null): .drc 不含 METHOD 4 via-contact, 不含 via 层名, 仍含 METHOD 1-3 + OUTPUT
15. (o) 确定性: 同一 B spec 3 次运行 .drc 字节一致 (md5)
16. (p) 防硬编: B .drc 含 M2/VDD2/VSS2/M2_VIA1 (不在 A 集 M1/VDD/VSS/M1_VIA); A 与 B 层名集无交集

### 4 negatives (first_fail 各异, ≥3 distinct)
- empty_shell: 语法错 → a
- print_expected_A: 硬编 A 的 .drc 值 (M1/VDD/VSS/M1_VIA, A params) → d/j (层名不匹配 B)
- core_deleted_silent_error: 空输出 → b
- always_pass_stub: 打印 OK 不生成 → b

### 自验
- gold_ref 16/16 PASS (A/B/B2 三 spec)
- negative_selftest 4/4 FAIL + GOLD_PASS + first_fail ≥3 distinct
- §4.9 三假 (空壳/只 print A/删核心) 全 FAIL
- k_rationale = k_check = 16 ≥ 8 GATE PASS

## build status
- **DEFER r687** (40-min budget 不足完整 case build: gold generator + SVRF .drc parser + 16-cond check + 4 neg + 自验)
- 本轮 = SELECTION + DEEPREAD ✓
- DEBT: 1 (wimgg deepread done, build deferred r687)
