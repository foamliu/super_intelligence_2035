# trace deepread — w2fwq (SpfCellCrossRefProduce)

- **session**: 1795077131085_w2fwq.messages.json (39 msgs, 266 KB)
- **user/host**: caozhang @ hfeg0pkn003 (10.129.2.12)
- **match_count**: 31, domain: analog_context (analog:146; cmos:86; netlist:24; opamp:4; D-pure)
- **status**: deepread → 待合成 (r1078)

## trace_source (for metadata.trace_source)
- user: caozhang
- host: hfeg0pkn003 (10.129.2.12)
- session_file: 1795077131085_w2fwq.messages.json
- match_count: 31
- real_task_summary: cross-reference a list of circuit cell names (file `aaa`, 145 cells, one per line) against 4 SPF simulation-setup config sources (no_vcap / skip_cell / ignore_cells globs / control.nanospice_promd_spfba_common finesim_mode+finesim_ignore), report per-source membership counts + matched cell names. doc-search / cross-check Q&A, analog-sim setup verification.

## 用户原话（U#0，重复 5 次因 retry）
> /rundata/.../MatrixRun_Netlist_SpfBa_20261031PM/aaa 中的cell 分别在
> /proj/.../post_sim/SPF/no_vcap  /proj/.../post_sim/SPF/skip_cell
> /proj/.../post_sim/SPF/ignore_cells  /proj/.../control.nanospice_promd_spfba_common
> 中是否存在 ，详细列出

## trace 实际行为
1. assistant 先读错 aaa 路径（`/rundata/.../aaa` = matrix-run 状态文件，132 条 `Fail nanospice.golden...` case 名，非 cell 名），比对 4 源 → 0 命中，发现 aaa 内容是跑批 case 名不是电路 cell 名。
2. U#21 用户纠正：用正确 aaa 路径 `/proj/.../MatrixRun_Netlist_SpfBa_20261031PM_V0_1st_wow_1030_PDN/aaa`（145 个真实 cell 名，每行一个）。
3. assistant 改 `check_cells_in_refs.py`：parse_aaa 读纯 cell 名；match 用精确匹配（no_vcap/skip_cell/control）+ fnmatch 通配（ignore_cells）；control `finesim_mode` 条目去 `:prohd/:spicehd` 后缀再比。
4. rerun → 145 cell 在 4 源全部 0 命中（aaa 多为行列地址/驱动/SCMOS 类带 `20261109` 版本号，4 源多为 analog/array/regulator/dlyg 类，无交集）。
5. 最终交付 `check_cells_in_refs.py`（可复用）+ 详细比对表（每源: 源 cell 数 / 与 aaa 匹配数 / 命中 cell 名）。

## 4 个参考源格式（关键，决定 fixture 设计）
- **no_vcap**: 每行一个 cell 名，`#` 开头注释行不计。295 个活跃 cell。名如 `DqIO`、`WckRcvGutV3V4`、`dlyg2Ns2_gut2`。
- **skip_cell**: 每行一个 cell 名，无注释。43 个。名如 `AnalogAry…`、`DLDO_…`、`RowRed…`。
- **ignore_cells**: 每行一个 glob 通配模式。11 条：`dlyrc*  dlynrc*  dlymosc*  dlynmosc*  dlybias*  Dlyrc*  DlybiasGFGutvintIP  DlybiasPFGutvintIP  DlybiasGFGutvdd2hIP  DlybiasPFGutvdd2hIP  dlyg*`。
- **control.nanospice_promd_spfba_common**: 含 `.option finesim_mode="cellA:prohd cellB:spicehd ..."`（64 cell，`:后缀` 去掉再比）+ `.option finesim_ignore="cellC cellD ..."`（104 cell）。并集 168。

## case reframe (synthesized, B档 — trace 的 aaa/4源是 foundry-bound NFS 大文件不可入沙盒)
- **任务形态 = doc-search / cross-reference produce**（真实意图零偏移）：给一个 cell 名单文件 + 4 个 SPF 配置源，写脚本交叉比对，产 detailed membership report。
- **交付 = check_cells_in_refs.py + 跑 B 产 report**。L1（纯 Python 文本处理，无 EDA 二进制）。

## synthesis plan (下轮执行，A/B/A' 三集 token 结构性不相交)

### A (visible, SUT 沙箱内)
- `aaa_A.txt`: 40 个 cell，每行一个。token 风格：`RA_XYQ_Drv_ddgoa_2026`、`WCK2Ti_PS_1106`、`Spnand3x2_A`、`Spaoi21_B`、`dynamic_Latch_C`、`SCmos_ColBuf_D`（行列/驱动/SCMOS 类，带版本号，仿真实 trace）。
- 4 源 A: `no_vcap_A`(30 cell, 3 行 `#` 注释), `skip_cell_A`(12 cell), `ignore_cells_A`(6 glob: `Spnand*  Spaoi*  dynamic_*  SCmos_*  WCK2*  RAbus*`), `control_A`(finesim_mode 20 cell 带 `:prohd/:spicehd` + finesim_ignore 30 cell)。
- A 的命中分布（设计成非全零，让断言有牙）：no_vcap 5 命中 / skip_cell 3 / ignore globs 6 / control 4。

### B (hidden, assets/.../hidden/, 不进 SUT 沙箱, check() 只跑 B)
- `aaa_B.txt`: 50 个 cell，token 全不相交：`ColDec_BnkA_v2`、`WlDrv_Main_07`、`Saoi22_X`、`Snand4_Y`、`vrg_Latch_Z`、`CMos_PreBuf_W`（列译码/字线驱动/不同 SCMOS 风格）。
- 4 源 B: `no_vcap_B`(40 cell, 5 `#` 注释), `skip_cell_B`(15 cell), `ignore_cells_B`(7 glob: `Saoi*  Snand*  vrg_*  CMos_*  WlDrv*  ColDec*  Xpre*`), `control_B`(finesim_mode 25 cell + finesim_ignore 35 cell)。
- B 命中分布（与 A 不同）：no_vcap 8 / skip_cell 5 / ignore globs 9 / control 7。judge 独立重算 B-gold。

### A' (anti-hardcode, hidden, reference/.../hidden_a/, SUT 不可见, judge 经 HERE 读取)
- `aaa_Ap.txt`: 35 个 cell，token 与 A/B 全不相交：`BitLine_SA_v3`、`Rdmux_Aux_05`、`Nand2x_P`、`Nor3x_Q`、`preChg_Latch_R`、`Tmos_CapBuf_S`。
- 4 源 A': `no_vcap_Ap`(35), `skip_cell_Ap`(10), `ignore_cells_Ap`(5 glob: `Nand*  Nor*  preChg*  Tmos*  BitLine*`), `control_Ap`(finesim_mode 18 + finesim_ignore 28)。
- A' 命中分布（与 A/B 全异）：no_vcap 6 / skip_cell 4 / ignore globs 5 / control 5。A'-gold 硬编码于 check.py（固定 fixture，judge 不导入 ref）。

### check.py (k=18, ≥8 GATE PASS)
- **B-side (a-n, 14)**:
  - a: zip 含 check_cells_in_refs.py + py_compile exit 0
  - b: 候选脚本在 B 上 subprocess 跑 exit 0
  - c: stdout/stderr 非空，产出 report（JSON 或固定表格格式，prompt 指定 JSON schema）
  - d: report 含 4 源 key (no_vcap/skip_cell/ignore_cells/control)
  - e: B no_vcap 匹配数 == judge 重算 B-gold (8) — 核心正解
  - f: B skip_cell 匹配数 == B-gold (5)
  - g: B ignore_cells glob 匹配数 == B-gold (9)（验 fnmatch 真跑，不是子串）
  - h: B control 匹配数 == B-gold (7)（验 `:prohd/:spicehd` 后缀剥离）
  - i: B 命中的 cell 名集合 == judge 重算集合（精确，无漏无多）
  - j: B no_vcap `#` 注释行未被计入源 cell（验注释处理）
  - k: B control `finesim_mode` 与 `finesim_ignore` 并集正确（不重复计）
  - l: B 全 0 命中源不被谎报为有命中
  - m: 3-seed 确定性（脚本对 B 跑 3 次 md5 一致）
  - n: 无 `__chk` 污染 SUT workdir
- **A'-gold 交叉 (o-s, 5, §4.9 anti-hardcode)**:
  - o: 候选脚本在隐藏 A' 上 subprocess 跑 exit 0 + 合法 report
  - p: A' no_vcap 匹配数 == A'-gold (6) — 核心交叉，击穿 B-hardcode stub（对任意输入吐 B-gold 8）
  - q: A' ignore_cells glob 匹配数 == A'-gold (5) — 击穿 stub 吐 B-gold 9
  - r: A' control 匹配数 == A'-gold (5) — 击穿 stub 吐 B-gold 7，且验 `:suffix` 剥离在 A' 上独立成立
  - s: A' 命中 cell 名集合 == A'-gold 集合 — 显式输入相关，击穿恒定输出 stub

### negative (reference/.../negative/, ≥4, 全 FAIL)
- neg_fake_empty: 空脚本 → FAIL[b]
- neg_fake_print_only: 打印 B-gold JSON 串不做计算 → FAIL[e 或 i]（命中集合错或 glob 不真跑）
- neg_fake_core_deleted: 删 fnmatch/`:suffix` 剥离逻辑只留骨架 → FAIL[g 或 h]
- neg_fake_hardcode_b (smart §4.9(b)): 按输入文件名/md5 查表 A→A-gold/B→B-gold/unknown→B-gold fallback，源码带齐 d/e/f 静态模式 → pre-fix 应 FAIL[o-s A' 交叉]（A' 不认 md5 → fallback 吐 B-gold ≠ A'-gold），post-fix 确认 FAIL[p/q/r] n_distinct≥2

### test_rationale (k=18 清单)
18 条断言：①zip含脚本+py_compile ②B跑exit0 ③产出合法report ④report含4源key ⑤B no_vcap匹配数==B-gold ⑥B skip_cell匹配数==B-gold ⑦B ignore glob匹配数==B-gold(fnmatch真跑) ⑧B control匹配数==B-gold(:后缀剥离) ⑨B命中cell名集合==judge重算 ⑩B no_vcap #注释行未计入 ⑪B control mode/ignore并集不重复 ⑫B全0源不谎报 ⑬3-seed确定性 ⑭无__chk污染 ⑮A'跑exit0+合法report ⑯A' no_vcap匹配数==A'-gold(击穿B-hardcode) ⑰A' ignore glob匹配数==A'-gold(击穿stub) ⑱A' control匹配数==A'-gold(:suffix在A'独立成立)

## 与已有 case 的区分
- 无现有 cell-cross-ref 类 case（D.jsonl 现有: spice-fix / netlist-trace / virtuoso-cli / skill-install / rc-viz / netlist-broadcast / ae-del-cell 等，无 SPF-config cross-reference）。互补非重复。

## 资产便携性
- trace 的真实 aaa/4源 = foundry NFS 大文件（`/proj/ddgoa/...`），不可入沙盒。reframe 三集 mock（每集 <50 cell，纯文本），完全便携。A-faithful（格式 100% 复刻真实：每行一 cell / `#` 注释 / glob 通配 / `.option finesim_mode="..."`）。

## 下轮合成 ETA
- r1079 合成：建 assets (A/B/A' 三集 mock 文件) + reference (check_cells_in_refs_ref.py) + check.py (k=18) + negative (4) + negative_selftest + 自验 + D.jsonl 追加。预算 40min 可完成（fixture 全是纯文本 mock，无 EDA 二进制，无 .75 依赖）。
