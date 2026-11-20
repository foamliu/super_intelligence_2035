# trace_deepread: r671 sierraw@10.129.32.46 session 1793263826690_n4bf4

**case_id**: EDA-Eval-DesignFlow-BatchGdsCdlCli-001
**domain**: layout_virtuoso (C shard)
**match_count**: 34 | keywords: .cdl:126;virtuoso:108;.gds:98;netlist:23;schematic:12;rtl:12;calibre:6;pyaether:1
**session_msgs**: 69 | user_text turns: 3 | tool_use: 33 (editor:18, run_approved_command:5, read_files:6, list_allowed_files:3, get_agent_policy_status:1)
**delivered**: 2026-11-16 r671

## 真实用户意图 (U#0, 逐字)

> 查看我/home/sierraw/Desktop/script/GDS_CDL这个路径下的文件，这是批量导出&gds的脚本，我希望你改写一下，做到在终端输入命令完全实现不用改动json文件，并选择gds&cdl或者二者其一命令行可以输入输入路径，并保存到特定路径

后续追问 (U#1): 「继续任务」; (U#2): 「现在的batch文件是修改后的吗？还需json文件吗」

**意图分型**: produce-task (脚本改写). 用户有一个 v2 JSON-config 驱动的批量 GDS+CDL 导出脚本，要改写成纯命令行驱动，不用改 JSON，支持 -t gds/cdl/both，命令行输入路径，保存到特定路径。

## 助手工具链 (msg1-65)

1. `list_allowed_files` / `read_files` (msg1-9): 读 /home/sierraw/Desktop/script/GDS_CDL/ 目录 + 原 batch_gds_cdl.py (v2) + gds_cdl.json
2. `editor` (msg12): 写 `_backup_v2.py` (备份原 v2)
3. `editor` (msg16/18): 改 `batch_gds_cdl.py` (初版改写)
4. `editor` (msg24-44, 11 次): 写 `_new_batch_gds_cdl.py` (v3 纯 CLI 版, 分 chunk 写入: build_parser -> resolve_settings -> BatchGdsCdlExport class -> main)
5. `editor` (msg46): 写 `_install_v3.py` (安装脚本, 把 _new_batch_gds_cdl.py 复制为 batch_gds_cdl.py)
6. `run_approved_command` (msg48/52/56): 跑 _install_v3.py + _selftest.py (20/20 自测通过)
7. `editor` (msg61): 写 `_cleanup_pycache.py` (清理 __pycache__ + 自删)
8. msg65: 完整总结 (用法 5 例 + 核心变化表 + 验证结果 20/20)

## v2 原脚本 (JSON-config 驱动, gold_ref 参考)

`/home/sierraw/Desktop/script/GDS_CDL/batch_gds_cdl.py` (619 行 / 23894 B, 实为 v2):
- class `BatchGdsCdlExport.__init__(config_file)`: 从 JSON 加载所有配置 (project_name/work_dir/gds_save_dir/cdl_save_dir/cell_list/include_file/layer_map/queue/max_jobs/bsub_n/export_gds/merge_gds/export_cdl/merge_cdl/merge_cdl_gds_dir/merge_top_cell_name/virtuoso_module)
- `_validate`: work_dir/gds_save_dir/cdl_save_dir/cell_list 必填; export_gds 必须 layer_map; merge_gds/merge_cdl 必须 merge_dir 且配合 export
- `parse_cell_list`: 解析 `lib cell [view]`, view 缺省 layout
- `_gen_si_env`: 生成 si.env (auCdl netlist 配置)
- `_build_cell_script`: 生成 bsub 脚本 (strmout for GDS, si -batch -command netlist for CDL, ThreadPoolExecutor + Semaphore(max_jobs) 并发)
- `_extract_subckts`: 只保留 `.SUBCKT ... .ENDS` 块, 丢弃 header
- `_merge_cdl`: 合并 .cdl -> `<lib>.cdl`
- `_merge_gds`: 合并 .gds -> `<lib>.gds` (生成 create_gds_top 脚本)

`gds_cdl.json` (真实配置, 26 行):
```json
{ "project_name":"lacaa", "work_dir":"/proj/lacaa/TV1_FS_Virtuoso/workdir/sierraw",
  "gds_save_dir":"/proj/lacaa/TV1_FS_Virtuoso/workdir/sierraw/",
  "cdl_save_dir":"/proj/lacaa/TV1_FS_Virtuoso/workdir/sierraw/MB_CDL_1113/MB_AA35_SVT",
  "cell_list":"/proj/lacaa/TV1_FS_Virtuoso/workdir/sierraw/FSP51H204L6W35T6_MB_SVT_schematic/celllist.txt",
  "include_file":"/apps/imctf/cad/runset/lacaa/tv1_fs_virtuoso/current/calibre_empty_subckt_FS.sp",
  "layer_map":"/proj/lacaa/TV1_FS_Virtuoso/libs/35HFS/35HFS.layermap",
  "queue":"pv_lacaa", "max_jobs":100, "bsub_n":2,
  "export_gds":"NO", "merge_gds":"NO", "export_cdl":"YES", "merge_cdl":"YES",
  "merge_cdl_gds_dir":"/proj/lacaa/TV1_FS_Virtuoso/workdir/sierraw/MB_CDL_1113", "merge_top_cell_name":"" }
```

## v3 纯 CLI 版 (助手产出, 从 editor new_text 提取)

`_new_batch_gds_cdl.py` (msg24-44 分 chunk 写入):
- `build_parser()`: argparse 全套 (cell_list 位置/-w/-o/--gds-save-dir/--cdl-save-dir/-t {both,gds,cdl}/--layer-map/--include-file/--init-script/--virtuoso-module/--project-name/--queue/--max-jobs/--bsub-n/--merge-gds/--merge-cdl/--merge-dir/--merge-top-cell/--temp-dir/--config/--dry-run)
- `load_json_config(path)`: 可选 JSON config
- `resolve_settings(args)`: **CLI > JSON config > 内置默认** 三级优先级 (pick() helper)
- `BatchGdsCdlExport` class: `_validate` (work_dir 必填且存在/celllist 必填/-t gds 必须 layer_map/merge 配合 export) + `parse_cell_list` + `_gen_gds_command`/`_gen_cdl_command` (bsub 命令串) + `_extract_subckts` + `_merge_cdl`/`_merge_gds` (**排除合并输出自身 bug 修复**) + `run` (ThreadPoolExecutor + Semaphore)
- **关键 bug 修复**: `_merge_cdl`/`_merge_gds` 排除已生成的 `<lib>.cdl`/`<lib>.gds` 本身, 避免重跑时 subckt 翻倍
- **--dry-run**: 校验 + 打印 resolved settings + planned commands, 不提交任务
- msg65 总结: 20/20 自测通过 (--help/三种导出类型 dry-run/JSON 默认值+CLI 覆盖/celllist 从 JSON 读取/各类参数错误分支/CDL 合并幂等性)

## B档 mock-behavioral reframe

真实 v3 依赖 Virtuoso strmout / Siemens si / LSF bsub (沙盒不可达) → reframe 为通用纯 stdlib `batch_gds_cdl_cli.py`:
- **planner 模式** (默认 + --dry-run): 读 celllist + 可选 --config JSON → resolve_settings (CLI>JSON>默认) → _validate → parse_cell_list → 生成 per-cell bsub 命令串 → 输出 JSON 计划 (settings/cells/gds_commands/cdl_commands/lib_name/merge_plan)
- **--mock 模式** (测试合并逻辑, 无需 bsub): 写 mock .gds/.cdl 文件 per cell (含 .INCLUDE/.GLOBAL/注释 header + .SUBCKT...ENDS 块) → _merge_cdl (只保留 .SUBCKT...ENDS, 排除合并输出自身) / _merge_gds → 输出 JSON 报告 (mode/settings/cells/lib_name/files_written/merge_results)
- **新子型** `batch-gds-cdl-cli-planner`, distinct vs r670 PyaetherAsciiSanitizer=ASCII 清洗 / r667 RoutingTrackFinder=轨道扫描 / r665 AntennaQaPatternReuse=deck diff+AA 翻转 / r664 DrcDeckStatsAnalyzer=SVRF deck 统计

## asset A / hidden B / hidden B2

- **asset A**: celllist_A.txt (lacaa MB_AA35_SVT 8 cells) + config_A.json (真实衍生 v2 JSON schema) + prompt.md + task_brief.md
- **hidden B** (反硬编, 全异): celllist_B.txt (RF_LIB 6 cells: RFAMPX1/2/RFMIXER1/RFVCOX1/RFLNAQ1/RFPA_X1) + config_B.json (rfchip, queue=eda_normal, max_jobs=8, bsub_n=4, export_gds=YES/merge_gds=YES, merge_top_cell=RF_TOP) + layermap_B.placeholder; CLI 覆盖: -t gds --queue fast_lane --max-jobs 16 (验证 CLI>JSON 优先级)
- **hidden B2** (退化): celllist_B2.txt (DBG_LIB 1 cell: DBGCELL1)

## check() 16 条件 a-p

①(a) zip+py_compile ②(b) --dry-run B 退出 0+合法 JSON ③(c) 必需顶层键 ④(d) resolve_settings CLI>JSON (queue fast_lane over eda_normal, max_jobs 16 over 8) ⑤(e) parse_cell_list (B 6 cells, lib_name=RF_LIB) ⑥(f) -t gds 无 --layer-map 退出非 0+报错 layer_map ⑦(g) --merge-cdl 配 -t gds 退出非 0 ⑧(h) bsub 命令串含 bsub/queue/strmout; cdl_commands 为空 ⑨(i) --dry-run 不写文件 ⑩(j) --mock 写 mock .gds/.cdl per cell ⑪(k) --merge-cdl 产出 <lib>.cdl 含所有 .SUBCKT 块 ⑫(l) _extract_subckts 丢弃 header (无 .INCLUDE/.GLOBAL/注释) ⑬(m) merge 排除自身 (merge_dir==cdl_save_dir 重跑 subckt 数稳定) ⑭(n) 确定性 3x byte-identical ⑮(o) 防硬编码 (B≠A: RF_LIB/fast_lane/gds, 无 INVX1/pv_lacaa) ⑯(p) B2 退化 (1 cell, DBG_LIB, 1 gds cmd)

## 自验

- gold_ref 16/16 PASS ✓
- 4 negatives (empty_shell/print_expected_A/core_deleted_copy_input/always_pass_stub) 全 FAIL ✓, first_fail b/d/e/d (3 distinct ≥3 ✓)
- §4.9 三假 (empty/print/core) 全 FAIL ✓
- test==disk sha 22c969a5ea7320e5 ✓
- k_rationale=k_check=16 ≥ 8 GATE PASS ✓
- jsonl_C 416→417
- ledger_C mark n4bf4→case (covered 417→418)
