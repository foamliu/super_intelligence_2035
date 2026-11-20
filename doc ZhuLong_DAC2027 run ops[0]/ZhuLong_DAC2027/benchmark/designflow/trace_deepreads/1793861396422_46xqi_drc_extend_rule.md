# Deepread: 1793861396422_46xqi — DRC pattern rule GDS 几何校验器

- **trace**: `1793861396422_46xqi.messages.json` (169 msgs, 1.6 MB)
- **user / host**: xxchen @ hfeg0pkn002
- **match_count**: 181 (drc:794 + dbcreaterect:167 + .gds:125 + calibre:64 + schematic:40 + layout:38)
- **domain**: physical_verify (DRC pattern rule generator + GDS 几何断言)
- **case-id**: EDA-Eval-DesignFlow-DrcExtendRuleValidator-001
- **shard**: C (physical_layout), round 217
- **track**: faithful (B-synthesized, L1-boundary)

## 真实任务流水（trace grounding）

xxchen 在 hfeg0pkn002 写一条 DRC pattern rule 的 generator `alayer_extend_blayer.py`（217 行），规则叫 `DNW_EXT_005`（alayer extend from blayer，NW 从 DNW 上沿伸出 `extend` 长度）。generator 产出 4 类 temp cell：
- `bad_<prefix>_p1`（bug 3：protrusion 不够长，少一个 grid）
- `bad_<prefix>_p7`（bug 1：protrusion 不够 + layer1 切穿 layer2 底边 → 双 highlight）
- `bad_<prefix>_p11`（bug 2：上沿多了一块 6 顶点 protrusion 多边形）
- `good_<prefix>_p7`（bug 4：outside touch，不报错，0 highlight）

用户反复在「肉眼看 GDS / 用 dbCreateRect 量坐标 / 跑 calibre drc 回检」之间手动确认 4 个 engineer bug 是否修对，没结构化断言。assistant 复刻 generator 后写 `check_dnw_ext_gds.py`（272 行，用 gdspy 读 GDS）逐条 assert 4 个 bug 的几何条件：
- bad_p1: layer1 bbox `(0,0,L,W)`, layer2 bbox `(-E,-W,L+E,W-E+G)`, protrusion `== E-G` 且 `< E`, 1 top highlight rect
- bad_p7: 同 bad_p1 几何但 layer1 下沉到 `(0,-W,L,W)`, + bottom edges flush, + 2 highlight rects（顶 + 底）
- bad_p11: layer1 是 6 顶点斜切角多边形, layer2 顶边 `== dnw_top = 2L+y_sq-E+G`, 1 bottom highlight rect + 1 上沿 6 顶点 protrusion 多边形（全部 y≥dnw_top，恰 2 顶点 y==dnw_top）
- good_p7: layer1 bbox `(0,E,L,E+W)`, layer2 bbox `(-E,-W,L+E,E)`, layer1 bottom flush layer2 top, 0 highlight

trace 无单一干净 accepted artifact（用户在反复修 4 个 bug 中结束 session），但 `check_dnw_ext_gds.py` 是完整 4-bug GDS 几何断言闭环。真实几何值（E=1.85, W=2.016, L=4.0, dnw_top=6.8628, y_sq=0.7127, protrusion=1.8499）verbatim from `check_dnw_ext_gds.py`。

## 选料理由

r217 shard C 候选池 mc>=30 多在 ledger_C/all_excl 排除，按 phys_score（drc/dbCreateRect/.gds/calibre/layout 加权）排序，46xqi（xxchen @ hfeg0pkn002, mc=181, drc:794+dbCreateRect:167+.gds:125, NEW user, 真 DRC pattern rule generator + 真 check_dnw_ext_gds.py GDS 断言）→ physical_verify 域。DISTINCT from r208 DrcUnusedVarClassify（DRC variableUnused 4 桶分类）/ r172b DrcRuleCellMatch（rule→cell 5 策略匹配）/ r216 CalibreLvsRepDiag（LVS run-log 解析）— 本案首次 ground on **DRC pattern rule GDS 几何校验**（alayer_extend_blayer pattern generator 4-bug 修复条件 GDS polygon 顶点断言 + protrusion==E-G 且 <E + 切边双 highlight + 上沿 6 顶点 protrusion 多边形 + outside touch 无 highlight + cell inventory + GRID alignment 共 35 条 check），与 DRC variableUnused / rule-cell / LVS 报告解析互补不重叠（GDS 几何断言 ≠ DRC 变量分类 / rule-cell 匹配 / LVS 报告解析）。

## 合成任务

trace 无单一干净 accepted artifact（用户在反复修 4 个 bug 中结束）→ B-synthesized grounded on 真实 `check_dnw_ext_gds.py` 4-bug GDS 几何断言逻辑。合成「DRC pattern rule GDS 几何校验器」任务（SUT 写 `extend_rule_validator.py`，CLI 2 参 `<geom_dump.json> <config.json>`，仅标准库 json/math/sys，禁 gdspy/numpy）。

**关键设计**：judge 沙箱（36.15）无 gdspy，所以 GDS 几何预抽成 JSON dump（`dump_gds_geom.py` 在 .75 上用 gdspy 产出 `{cell_prefix, cells:{<name>:{polygons:{<layer>;<datatype>:[[[x,y],...],...]}}}}`），SUT 校验器仅消费 JSON dump（stdlib only）。这样判分环境与 SUT 解耦：.75 有 gdspy 产 dump，36.15 无 gdspy 跑校验器。

## 资产

- **A**（可见，SUT-seen）= 真实 trace grounded：layer1=[8,0] NW, layer2=[6,0] DNW, highlight=[4001,51], extend=1.85, width=2.016, length=4.0, cell_prefix=DNW_EXT_005_00_NW_DNW_NW_DNW, dnw_top=6.8628, protrusion=1.8499。35/35 PASS。
- **B**（隐藏，judge-runs-on）= 全重参数化：layer1=[91,0] M3, layer2=[88,0] M2, highlight=[4002,51], extend=0.05, width=0.08, length=0.09, cell_prefix=M3_EXT_005_00_M3_M2_M3_M2, dnw_top=0.1583, protrusion=0.0499。几何结构同构 → 35/35 PASS。B 与 A 全重参数化（layer/datatype 全不同 + 尺寸量级全不同 1.85→0.05 / 2.016→0.08 / 4.0→0.09 + cell_prefix 全不同 + protrusion/dnw_top 数值全不同）击穿硬编码 A。
- **B_broken**（隐藏哨兵）= bad_p7 的 highlight 层故意少画底边 cut-edge rect（1 rect 而非 2）→ 校验器必须 exit 1 + FAILED 提及 bad p7 / highlight。测 A/B 都不覆盖的 cut-edge 检测路径 + 杀 stub-always-pass。

## 判分（check.py，16 条 a-p）

判分对 B 跑候选（subprocess）+ A 跨输入守卫 + B_broken 哨兵 + 3-seed 确定性：
- (a) submit.zip 合法 zip 含 >=1 .py 生成器
- (b) py_compile + 仅标准库（json/math/sys，禁 gdspy/numpy）
- (c) B exit 0 + stdout 含 'ALL 35 CHECKS PASSED'
- (d) B stdout 含全部 6 段头（cell inventory / GRID alignment / bad p1 / bad p7 / bad p11 / good p7）
- (e) B stdout [PASS] 计数 == 35（SUT 跑完整 35 条 check 而非子集）
- (f) B stdout 含 B 专属 protrusion '0.0499'（B 的 E-G=0.05-0.0001，反硬编码 A 的 '1.8499'）
- (g) B stdout 不含 A 专属 protrusion '1.8499'（反硬编码 A）
- (h) B stdout 含 B 专属 dnw_top '0.1583'（反硬编码 A 的 '6.8628'）
- (i) B stdout 不含 A 专属 dnw_top '6.8628'（反硬编码 A）
- (j) 跨输入守卫 A：A exit 0 + 'ALL 35 CHECKS PASSED' + 含 '1.8499'（反硬编码 B）
- (k) 跨输入守卫 A：含 '6.8628' + 不含 '0.1583'（反硬编码 B）
- (l) B_broken 哨兵：exit 1 + stdout 含 'FAILED'
- (m) B_broken FAILED 块提及 'bad p7' 和 'highlight'（cut-edge 哨兵，反 stub 失败在错误的 check）
- (n) B_broken 0 < [PASS] 计数 < 35（反 always-fail + 反 always-pass）
- (o) 3-seed 确定性：B 跑 3 次在 3 个临时副本上 exit 0 + md5(stdout) 一致（反非确定性）
- (p) B stdout [FAIL] 计数 == 0（正确 dump 上无虚假失败，反 paranoid validator）

k_check=16 >= 8 ✓。

## self-verify

- 本机 Python 3.12（无 gdspy，stdlib only）：ref 校验器用 A 跑出 35/35 PASS + 'ALL 35 CHECKS PASSED'；B 跑出 35/35 PASS + 'ALL 35 CHECKS PASSED'；B_broken 跑出 32 PASS + 1 FAIL 'bad p7: 2 highlight rects (top + bottom), got 1' + exit 1。
- golden submit.zip（ref 校验器）→ check.py CHECK PASS 16/16。
- 3 §4.9 fake 全 FAIL：empty_shell → (c)（B 无 'ALL 35 CHECKS PASSED'）；print_expected → (j)（A 跨输入守卫失败，stub 不知道 A 该输出什么）；core_deleted → (c)（同 empty_shell）。
- 3 negative 全 FAIL 独立条件：naive → (c)（json 没 import，NameError，B exit != 0）；always_a → (c)（硬编码 A prefix 'DNW_EXT_005...' 不匹配 B 的 cells 'M3_EXT_005...'，cell inventory FAIL → B exit 1）；stub → (l)（stub 用 config 派生值打印 ALL 35 CHECKS PASSED，B_broken 也 'pass' → exit 0 而非 1）。
- 3-seed 确定性：B 跑 3 次在 3 个临时副本上 md5(stdout) 一致。
- E2E：从 jsonl `test` 字段抽 check.py 跑 golden PASS + stub FAIL on (l)，sha256 与 disk check.py 一致。

## case files

- `assets/EDA-Eval-DesignFlow-DrcExtendRuleValidator-001/{prompt.txt, task_brief.md, geom_A.json, rule_config_A.json, hidden/{geom_B.json, geom_B_broken.json, rule_config_B.json, hidden_manifest.json}}`
- `reference/EDA-Eval-DesignFlow-DrcExtendRuleValidator-001/{check.py, extend_rule_validator_ref.py, selfverify.py, negative/{naive.py, always_a.py, stub.py}, negative_selftest.py}`

## 备注

- gdspy 1.6.13 在 .75（hfeg0pkn002 有 xxchen env）可用；judge env 36.15 无 gdspy → 校验器消费预抽 JSON geom dump（stdlib only）。
- 真实 `ref_check_dnw_ext_gds.py`（272 行，.75 workdir）+ `ref_alayer_extend_blayer.py`（217 行）+ `ref_verify_aeb.py` 是 grounding 来源。
- y_sq = snap_fix(√2/2 · 0.5·W, precision) = trunc(0.02828...·10000)/10000 = 0.0282（B）/ 0.7127（A，verbatim from trace）。
- dnw_top = 2L + y_sq - E + G = 0.1583（B）/ 6.8628（A，verbatim from trace）。
