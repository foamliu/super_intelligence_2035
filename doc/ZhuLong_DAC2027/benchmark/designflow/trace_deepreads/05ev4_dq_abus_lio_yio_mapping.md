# Deepread: 05ev4 — DQ/Abus/Lbus/Yio/YioN 映射关系整理 (my7li@hfeg0plg56)

- **session**: `1794795731500_05ev4.messages.json` (804 msgs)
- **user/host**: my7li / hfeg0plg56
- **match_count**: 409 (keywords netlist:736; analog:602; schematic:216; virtuoso:202)
- **domain**: analog_context (D-pure: doc/mapping 分析, 非跨域 layout; virtuoso 关键词来自项目背景而非 layout 操作)
- **选料**: r981 fresh D-pure 池 (r979 发现的 207 条), mc≥10 口径, 05ev4 mc=409 为池中第 2 高
- **case_id**: EDA-Eval-DesignFlow-DqAbusLioYioMappingExtractProduce-001

## 1. 真实任务上下文

会话是 dqtool LP5→ddjob 网表移植项目。用户 my7li 在 IDX 535 发出:

> 「很好我看到了你移植的效果，现在使用dqtool里的知识库和查询功能，整理出dq，abus，lio，yio的映射关系，并且更新dq mapping相关的代码」

真实资产: `/home/my7li/Desktop/dqtool_lp5/MAPPING_RULES.md` (13027 字节 / 244 行 / 10 节, eda_flow ssh 可达)。该文档是 `main_py37.py` 的**权威映射参考**, 明确写「If this document and the code ever disagree, the code wins」。

## 2. 资产结构 (MAPPING_RULES_A.md, 逐字保留)

- §1 数据流总览: DQ 512-bit → beat0-47×dq0-11 位矩阵 → Abus(16×16-bit) → Lbus → Yio/YioN(nibble 交叉+取反)
- §2 `_compute_d_index(beat, dq)`: 6 group (G0-G5), 每 group 4 beat; G2/G5 带 M/L mask (invalid dq=4,5,10,11); group base: G0=0/G1=48/G2=96/G3=128/G4=176/G5=224; G2/G5 的 dq6-9 紧凑到 112-127/240-255
- §3 `_ABUS_MAP`: **双表** — abus_idx 表 (6×12, — 表示 M/L mask 丢弃) + bit_base 表 (G0-G2 用 0/4, G3-G5 用 8/12)
- §4 BL 模式 × Even/Odd: 4 行 (BL24/BL48 × T/F) 决定 col0/col1 与 Lbus1st/Lbus2nd 来源
- §5 nibble 交叉: Yio={~N3,N1,~N2,N0}, YioN={N3,~N1,N2,~N0} (16-bit in/out, 纯位运算)
- §6-§10: Decode→Channel0 高亮 / UI 列与 SORT_MAPS / 修改清单 / DFT cm 过滤 / curate.json 人工标注 (判分不涉及, 但保留完整以维持资产真实性)

## 3. case 设计 (A-faithful + L2 produce-from-scratch reframe)

- **reframe**: 把「整理映射关系 + 更新代码」物化为**通用 markdown 表格解析器** `dq_mapping_extract.py`, 读 MAPPING_RULES_*.md, 输出 5 键 JSON (d_index_groups/abus_index/bit_base/bl_mode_table/nibble_map)
- **A 档 trace-faithful**: 用户原话 IDX 535 逐字保留; A 资产 = 真实 244 行文档逐字
- **隐藏 B**: 结构同 A (同 10 节同表布局), 数值系统性相异 — group base 上下半交换 (G0=128/G1=176/G2=224/G3=0/G4=48/G5=96); G2/G5 invalid mask=[4,5,6,7] (A 为 [4,5,10,11]), 紧凑带 dq8-11 (A 为 dq6-9); abus_idx G0/G1 与 G3/G4 配对交换 (G0=[1,1,4,4,7,7,9,9,13,13,15,15]); bit_base 半交换 (G0-G2 用 8/12, G3-G5 用 0/4); nibble Yio↔YioN 互换; BL Even/Odd col0/col1 交换
- **判分范式**: subprocess-parser-dual-input — 候选解析器在 A(可见) 与 B(隐藏) 上各跑一次; A 验正确性(证明真解析非 stub), B 验相异性(反硬编码); 源码扫 A 表格字面量签名; 3 次 md5 确定性
- **13 条断言 a-m**: a zip+py / b py_compile / c A exit0+JSON / d A 结构完整 / e A abus G0+G2 null mask / f A G2 base+invalid, G5 base / g A bit_base G0/G3 / h A nibble / i B exit0+abus G0(B 专属) / j B G5 base+G2 invalid(均≠A) / k B nibble+bit_base(均≠A) / l 反硬编码源码 / m 3 次确定性

## 4. 自验

- 参考 parser (通用 regex 表格解析, 零硬编码) 对 A/B 各跑 exit=0, A/B 输出在 abus_index G0 / base G5 / nibble yio[15:12] / bit_base G0 上均相异
- check.py 对 reference_submit.zip: **13/13 PASS**
- 3 negatives 全 FAIL: empty_shell→d (结构空), print_expected→i (硬编码 A, B abus G0 不符, 反硬编码守卫命中), delcore→d (核心删除, 结构空)
- k_rationale == k_check == 13 ≥ 8 ✓

## 5. 关键工程点

- **双表歧义**: §3 有 abus_idx 表与 bit_base 表, header 都是 "Group|dq0..dq11", abus_idx 表多一个 beat 列(14 cell), bit_base 表 13 cell; 参考 parser 用 "第二个 Group header 即 break" 区分, 并用 `re.match(r"^G\d+$")` 拒收 "Group" header 行(早期 bug: "Group".startswith("G") 为真导致 bit_base 覆盖 abus_idx)
- **base 提取**: 从 d_index 公式 `(\d+)\s*\+\s*o` 取首整数; G2/G5 紧凑组取 `dq0-3:` 后公式的 base
- **invalid_dq**: 从 §2 末列解析整数列表, "—" → []
- **null 语义**: abus_idx 的 "—" 与 bit_base 的 "*" 均映射 null; _to_int_or_none 兼容 em-dash/en-dash/星号
- **反硬编码双重守卫**: 输出层 (B 值必须 ≠ A, 条件 i/j/k) + 源码层 (禁止 A 表格字面量签名, 条件 l); print_expected negative 同时被两层拦截 (i 命中输出层, l 命中源码层)
- **negative_selftest 路径 bug 修复**: 原模板 CHECK=os.path.join(CASE_DIR,"check.py") 指向 reference/check.py(不存在), 导致 negatives 因 "can't open file" 假性 FAIL; 改为 CHECK=os.path.join(HERE,"check.py")(同目录)后 negatives 才真正被断言拦截 — 此 bug 在 r980 模板中亦存在, 本轮修正

## 6. trace 覆盖率

D.jsonl 523→524 · ledger 05ev4 claim→mark case · trace 覆盖率 519/486=106.8%→520/486=106.9% (cases/D +1, mc≥10 口径, 快照 1119)
