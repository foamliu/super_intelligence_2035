# yhaoi — DRC Testpattern Generator (e0041123 @ hfeg0plg104)

- session: `1790230411878_yhaoi.messages.json` (16 msgs, 51KB, 2026-09-24)
- user: `e0041123`, host: `hfeg0plg104` (10.129.8.236), mc=2572 (11-21 scan) / mc=18 (11-20 scan)
- domain: layout_aether (pyAether .oa generation) + physical_verify (DRC) context
- keywords (11-21): drc:1339; aether:524; pyaether:406; techfile:157; lib.defs:80

## 用户意图 (U#0 逐字)

用户写了一个详尽的 SKILL spec「DRC Testpattern Generator」，描述如何用 `run_drc_pattern.sh` 包装脚本 + `pythone` 执行 `drc_pattern_gen.py` 从规则名(通配符)生成 .oa testpattern。本 session 用户让烛龙用 query `DNW_W_000_00` 调用该 skill 生成 1 条 width 规则的 PASS/FAIL .oa。

> # DRC Testpattern Generator
> ## 目标
> 用户给出规则名(支持通配符*，忽略大小写)，烛龙用 `run_approved_command` 调用 `run_drc_pattern.sh` 包装脚本，通过 `pythone` 执行主体脚本 `drc_pattern_gen.py` 生成 .oa 数据。
> ## 输出
> - .oa路径: `<DATA_DIR>/drc_pattern/DRCPatLib/{CellName}/layout/layout.oa`
> - Cell名: 从查询通配符派生(去除`*`和`?`)，如 `DNW*`->`DNW`
> - 布局: 大图形和小图形分两列，每条规则 PASS左 / FAIL右并排对比，上方居中标注 rule_id

## 助手 gold 链

idx=11: `run_approved_command`(profile `shell-runner`) 调 `/home/e0041123/.cline/scripts/data/run_drc_pattern.sh` 传 `DNW_W_000_00` → 生成 1 条 width 规则 PASS/FAIL .oa。idx=15 摘要确认: matched 1 rule, cell `DNW_W_000_00`, PASS(DNW 8.30×20) / FAIL(DNW 8.00×20), small pattern (h<50μm), .oa 落盘。

真实 gold = `drc_pattern_gen.py` (468 行, 18.9KB, on .75 `10.129.8.236:/home/e0041123/.cline/scripts/data/`):
1. 读 `sample_drc_deck/config/drc_rules_spec.json` (49 rules) + `derived_layer_map.json`
2. `fnmatch`(rule_id.upper(), query.upper()) 去重保序匹配
3. `derive_cell_name(queries)`: strip 首尾 `*?`, 内部 `*?`→`_`, join `_`, 空回退 `drcPatterns`
4. `parse_coords(coordinates_hint)`: 正则 `(\w+):\s*\(([\d.]+),([\d.]+),([\d.]+),([\d.]+)\)` 抽 `(layer,x1,y1,x2,y2)`
5. `resolve_layer(name, rule_layers)`: NON_LAYER_NAMES(Rect1/polygon/shape 等)→rule_layers[0] 递归; LAYER_SUB(PERI→BORD, NACT→AT4, GATE→PG 等硬编 dict); physical_layer_map(去 `_drawing` bare); 否则 bare
6. 布局: `calc_size` 算 pass/fail h/w; `SIZE_THRESHOLD=50.0` 分 large/small; large 列 x=0, small 列 x=max_large_w+COL_GROUP_GAP(30.0); 每规则 PASS 左(x_offset) / FAIL 右(x_offset+pass_w+COL_GAP=10.0); 图形从 y_top 向下(y_top-(y-min_y)); `y_cursor -= (row_height + row_gap)`, `row_gap=max(15, label_space*1.5)`
7. pyAether `dbCrtRect`/`dbCrtLabel` 写 .oa

## 档 B reframe (case EDA-Eval-DesignFlow-DrcTestpatternGen-001)

真实 gold 用 pyAether `dbCrtRect` 写 .oa (judge env 无 pyAether) → reframe 为 **纯标准库 JSON 布局生成器**:
- 输出 `layout.json` (结构化 PASS/FAIL 矩形 + draw_layer 解析 + large/small 分类) 替代 .oa
- 用户意图(规则匹配 + cell 名派生 + 图层解析 + PASS/FAIL 布局)完整保留，仅交付形态 .oa→JSON (离线化)

### 可见 A fixture (assets/)
- `spec_A.json`: 4 rules (DNW_W_000_00 width/DNW large h=55, M1_E_002_00 enclosure/PERI→BORD+M1, PG_W_003_00 width/PG small, NACT_W_004_00 width/NACT→AT4 small)
- `lmap_A.json`: physical_layer_map (DNW/BORD_drawing/PG_drawing/AT4_drawing/M1_drawing) + layer_sub (PERI→BORD, NACT→AT4, GATE→PG)
- query A: `DNW*` → matches 1 → cell_name "DNW"

### 隐藏 B fixture (嵌 check.py)
- B_SPEC: 4 不同 rules (DMY_W_010_00 width/DMY1 large h=60, DMY_E_012_00 enclosure/PERI→BORDX+DMY4, DMY_W_013_00 width/DMY6 small, NACT_S_014_00 spacing/NACT→AT4X+DMY2)
- B_LMAP: layer_sub PERI→BORDX, NACT→AT4X (不同于 A 的 BORD/AT4)
- query B: `["DMY*","NACT*"]` → matches 4 → cell_name "DMY_NACT"

### 判分 (check.py 15 teeth a-o)
a zip+1.py≥500B+py_compile / b stdlib only / c B exit0+layout.json / d 顶层键 / e lib_name==DRCPatLib / f cell_name==DMY_NACT / g queries==[DMY*,NACT*] / h matched_count==4 / i rules len==4+rule_id set / j pass+fail 非空+entry 键 / k draw_layer 解析(PERI→BORDX, NACT→AT4X, DMY1→DMY1) / l size_class 分列(DMY_W_010_00=large, 余 small) / m DMY_W_010_00 PASS bbox==[0,-60,5.1,0] FAIL bbox==[15.1,-60,19.9,0] / n 反硬编 A 守卫(跑 A query DNW* 应 cell_name==DNW matched_count==1) / o 3-seed 确定性 + 反作弊 B 字面量<2

### 自验
- ref solve.py PASS 15/15
- negative_selftest: empty_stub→a / print_only→c / delete_core→j / wrong_resolve→k 全 FAIL distinct (4 distinct teeth)
- §4.9 三假 (empty_stub/print_only/delete_core) 全 FAIL
- roundtrip jsonl test==disk check.py sha16 7aad4ba0c2946c30 ✓
- JUDGE-tree 独立 dir PASS (check.py 自包含, B/A fixture 全内嵌)

### 意图审计: keep
e0041123 真实意图(DRC testpattern generator: 规则名→PASS/FAIL 布局 .oa)完整保留; reframe 是 grounding(pyAether .oa 不可沙盒 → 纯标准库 JSON 布局, 离线化)非加难; U#0 用户原话逐字入 prompt; fnmatch 匹配 + cell 名派生 + 图层解析 + PASS/FAIL 布局 + large/small 分列 全部直出 trace gold `drc_pattern_gen.py` 逻辑; 11-15 reaudit 后 produce-task 合法。
