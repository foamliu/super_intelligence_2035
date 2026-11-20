# r887 deepread — giuwf (Liberty / cells.yaml 文件清单扫描器 produce-task)

## Trace identity
- session: `1792497366260_giuwf` (subdir-path `sessions/1792497366260_giuwf/messages.json`)
- user: johnl
- host: hfeg0pkn001 / 10.129.2.10（NFS-synced：pkn001/pkn002/pkn003/pkn005 + pfn119/pfn120/...）
- mc: 24 (scan keyword mix: innovus:277; verilog:94; lvs:74; .lef:44; aether:23; netlist:20; cadence:18; synopsys:13; lib.defs:12)
- size: 282KB / 58 msgs / agent=lead (zhulong) / 2026-10-20
- ALIVE 5/5 hosts (subdir-path 复苏 pattern)

## 用户真实意图（5 个 user turn，逐字）

| # | user 原话 | 意图 |
|---|---|---|
| U#0 | `查找home目录下的所有的.lib文件` | home 下 .lib 文件枚举 |
| U#25 | `给出生成时间` | 附带每个 .lib 的生成时间（含 PrimeLib 内部 "File generated on" 行） |
| U#41 | `那找下所有的cells.yaml还有时间` | 把 cells.yaml 也纳入清单 |
| U#47 | `隐藏文件夹也要算啊` | 包含隐藏目录（用户纠正 agent 此前为防超时跳过隐藏目录） |
| U#52 | `.cline下到所哟lib` | 单独扫描 /home/johnl/.cline 下所有 .lib |

## Trace agent 工具链

trace agent 写了 5 个 Python 扫描脚本（run_approved_command python-runner profile 执行）：
1. `find_lib_files.py` — os.walk home，skip_dirs 防超时，列 .lib 文件
2. `lib_file_times.py` — 取每个 .lib 的 mtime/ctime
3. `lib_file_gen_time.py` — 抽取 .lib 头部 "File generated on ..." 内部生成时间行（修正匹配 `generated` → `generated on` 精确化）
4. `find_cells.yaml.py` — 同样逻辑找 cells.yaml（用户要求含隐藏目录后改 skip_dirs）
5. `find_cline_lib.py` — 单独扫 /home/johnl/.cline

trace agent 的 skip_dirs 集合（msg #16 / #42）：
```
.aether_log, .abrt, .bmatrix, .cache, .config, .dbus, .gnupg, .gvfs, .local,
.bun, .dsim, .empyrean, .finesim, .fontconfig, .gconf, ...
```

## 真实产物（trace agent 最终输出）

- home 下 25 个 .lib（Primelib 特性化输出 23 + innovus_verify/data/SS_0p98_m40c_lvs.lib 1 + prb/cds.lib 1「非 Liberty 警示」）
- home 下 2 个 cells.yaml（spice2dc / spiceTdc 下 primelib_char_T_IsmTop/config/cells.yaml）
- /home/johnl/.cline 下 40 个 .lib（primelib_char_all_comb 全库 + dc sim 6 个 cds.lib 非 Liberty）
- 每个 .lib 给出 mtime + 内部 "File generated on" 时间（无该行的标 "no internal 'generated' line"）

## 可造性判定

- **旧判（r37 / r553 旧规则）**："Q&A non-design_flow / file-discovery weak / 不可造"
  - 旧理由引「§5 L1/L2/L3 准入」与「analysis-only 判 weak」 → 11-15 用户令作废
- **新判（11-15 任务初衷）**：file-discovery / retrieval / inventory 是真实用户意图，合法
- **reframe**：把 trace agent 写的 5 个一次性脚本抽象为单一可重用 `lib_inventory.py` CLI 工具（通用 --root/--patterns/--skip-dirs/--include-hidden/--output 接口），输出结构化 manifest.json
- **可写牙**：B 档 synthesized produce-task，hidden B 目录树与 A 结构不同，check.py 真跑 SUT 脚本在 B 上 subprocess 执行，逐条断言 manifest 结构/字段/计数/skip_dirs/hidden/gen_time/size/mtime/anti-leak/anti-degenerate，k=18
- **自包含**：fixture A=tree_A 25文件 faithful compact 重建（Primelib/innovus/.cline/hidden/skip-dirs 真实结构），hidden B=21文件 base64 内联 check.py SUT 不可见
- **域归属**：eda_other（文件清单工具，跨 EDA tool 通用 utility，非 pg_layout——shard C 早前 parked 是 wrong-domain）

## 域归属纠正说明

shard C 在 r37（2026-11-08）把 giuwf 标 pg_layout/parked，理由"innovus kw from dir names not tool runs; no layout/PG deliverable"。但实际：
- 用户任务是 home 目录文件清单，不是 PG/layout 流程
- innovus 关键词来自目录名 `innovus_verify/data/`，不是 innovus 工具调用
- 11-15 用户令后 file-discovery/inventory 合法，属 A 域 eda_other
- 本轮 A --force 覆盖 C 的 parked 记录，理由记入 ledger note + 本笔记

## 合成方案（r887 已交付）

- **case_id**: EDA-Eval-DesignFlow-LibInventoryManifestProduce-001
- **domain**: eda_other / track B / level L1
- **k_check = k_rationale = 18**
- **fixture A**（SUT 可见）: `assets/.../tree_A/` 25 文件 + `task_brief.md`
- **hidden B**（SUT 不可见）: 21 文件 base64 内联 check.py（sram_compiler/output 4 lib + config cells.yaml + tempcell_config cells.yaml + io_libs + work_b/sim_b cds.lib + .tapeout_backup 2 文件 + .archive_dir legacy.lib + 6 skip-dir 文件 + 3 non-matching）
- **check.py 18 条独立断言**：① zip valid ② lib_inventory.py 定位 ③ py_compile ④ CLI 5 参数 ⑤ run exit 0 ⑥ manifest valid JSON ⑦ 顶层 files+summary ⑧ entry 5 字段 ⑨ 总数匹配 ⑩ .lib 集合 ⑪ cells.yaml 集合 ⑫ skip_dirs 缺席 ⑬ hidden 出席 ⑭ gen_time 抽取 ⑮ size ⑯ mtime_iso ⑰ anti-leak A-only ⑱ anti-degenerate B-only + summary 四字段
- **自验**: ref PASS 18/18（3 次确定性重跑全 PASS）+ 5 neg 全 FAIL（fake_empty / fake_print_only / fake_core_deleted / naive_hardcode_a / naive_split_only）+ §4.9 (a)(b)(c) 三假全 FAIL
- **op-order V 落库**: assets/EDA-Eval-DesignFlow-LibInventoryManifestProduce-001/(tree_A/25 文件 + task_brief.md) + reference/.../(check.py + lib_inventory.py + reference_submit.zip + hidden/ + negative/5 stubs + negative/negative_selftest.py) + A.jsonl 437→438
- **ledger**: A 台账 giuwf parked → case（--force 覆盖 C 早前 wrong-domain parked，理由记 note）
- **eda_flow**: r887 session open（scp giuwf messages.json 282KB + parse 58msg deepread）→ declare_done → close cleaned

## 教训 / 注意

1. **subdir-path ALIVE 复苏 pattern 持续有效**：giuwf 走 `sessions/<sid>/<sid>.messages.json` 路径，多 host NFS-synced ALIVE，与 r821-r828/r855-r862 一致
2. **跨 shard wrong-domain parked 需 --force**：选料前应 grep 全 shard 台账并集，但若域归属判定有误（旧规则下），A 域可 --force 覆盖并记 note
3. **B 档 synthesized produce-task reframe 适合 file-discovery trace**：trace agent 的一次性脚本 → 通用 CLI 工具，hidden B 用结构不同的目录树 + base64 内联 check.py，可写牙且自包含
4. **k=18 远超 ≥8 硬闸门**：18 条独立断言覆盖 zip/script/CLI/run/JSON/structure/fields/counts(×3)/skip/hidden/gen_time/size/mtime/anti-leak/anti-degenerate/summary(×4)
