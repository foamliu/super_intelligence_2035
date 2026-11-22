# Deepread: 1791599369493_a5z7g (zlhou @ hfeg0pjn200, mc=75, layout_aether)

- **trace**: `/home/zlhou/.snapshot/weekly-new.2026-11-01_2330/.cline/data/sessions/1791599369493_a5z7g/1791599369493_a5z7g.messages.json` (live session dir rotated to snapshot)
- **size**: 362 KB / 32 msgs / 2026-10-10 03:01Z (agent=lead)
- **keywords**: aether:228; .gds:139; skipper:54; synopsys:1; cadence:1
- **domain**: layout_aether (GDS-tiling flow on Aether sandbox)

## User intent (2 real asks)

1. **U#0** 「查看 /proj/train/V0_NCG_HF_Aether/workdir/zlhou/gds_for_2p/2prf_gds_1010 目录下所有文件（含隐藏），看看哪些可以删除，注意 1.py 是我现在用的主脚本」
2. **U#14** 「.skipper 是干什么的」

## Assistant flow

- `list_allowed_files` (depth 1 + hidden) on `2prf_gds_1010` → got full tree incl. `.0_run.sw*`, `.1.py.sw*`, `__pycache__/`, `output/`, `output/.skipper/`
- `list_allowed_files` on `__pycache__` and `output/` (depth 2) → bytecode + output GDS + `.MY_SRAM_*.swp` swap + `.skipper/caches/`
- `read_files` `1.py` → imports: `gdstk` (ext), `gds_tiler_load_gds as loader`, `gds_tiler_process_pattern as processor`, `connection_rules as cr`, `argparse`, `os`, `math`
- `read_files` `0_run` → `bsub -Is python3 1.py --words 32 --bits 8 ... --leafcell-gds HC2P_A_W64B8M4B2C1.gds --output-dir ./output` (commented-out alt line refs `HC1P_CXN4S1P2048X144M4B2C1R1W1BW1RE1.gds`)

## Gold answer (msg 13 + msg 23)

### Directory cleanup classification

- **🔴 Core (1.py 依赖，绝对不能删)**: `1.py` (main), `gds_tiler_load_gds.py` (imported L5), `gds_tiler_process_pattern.py` (imported L6), `connection_rules.py` (imported L7), `HC2P_A_W64B8M4B2C1.gds` (`0_run` `--leafcell-gds`)
- **🟡 Auxiliary (建议保留)**: `0_run` (bsub 启动脚本), `dump_labels.py` (辅助工具), `gds_tiler_process_pattern_JL.py` (`1.py` 未 import 的变体), `HC1P_CXN4S1P2048X144M4B2C1R1W1BW1RE1.gds` (`0_run` 注释掉的 alt leafcell)
- **🟢 Deletable**:
  - vim swap: `.0_run.sw*` (9), `.1.py.sw*` (10+), `output/.MY_SRAM_*.swp/swo` (4) — vim 崩溃恢复文件
  - `output/.skipper/` — GDS 查看器缓存
  - dated GDS backups: `HC1P_..._0918.gds`, `HC1P_..._0930.gds`
  - `output/` 整个输出目录（会重新生成）

### .skipper 解释 (msg 23)

`output/.skipper/caches/` 含 `.ski.cache` 二进制文件（`HC2P_64X8M4B2C1.gds_*.v0.ski.cache`, `MY_SRAM_32X8...gds_*.v0.ski.cache`）。判定依据：① 缓存名 `ski` 是工具缩写 ② 二进制直接存 cell 名（`HC2P_LEAF_GIO_EDGE`, `ARRAY_GIO_ARRAY`）③ 位于 `output/` 且 `1.py` 及依赖脚本均未引用 "skipper" ④ 纯属 GDS 查看器（Skipper/KLayout 插件等）临时缓存，加速下次打开。**结论：可安全删除，删后用查看器打开会自动重新生成。**

## Synthesis (case EDA-Eval-DesignFlow-GdsLayoutDirCleanupAnalyzer-001)

档B reframe fixture-driven — agent 写 `dir_cleanup_analyzer.py` 读 target_dir + main_script，emit JSON {main_script, core_files[], auxiliary_files[], deletable_files[{path,reason,category}], cache_dir_analysis{dir,purpose,evidence[],safely_deletable}, dependency_graph{main,imports[],referenced_gds[]}, summary}。分类规则：core=main+本地import模块+launch非注释行引用GDS；auxiliary=未import的.py/launch/注释GDS/config；deletable category=vim_swap(.sw*)/pycache/pyc/viewer_cache(.ski.cache)/dated_backup(_MMDD/_YYYYMMDD)/regenerable_output(output/)。env_A 镜像 zlhou 真实 2prf_gds_1010 目录；hidden B (check.py inline gen) 用不同名 run_tiler.py/tile_loader/pattern_proc/net_rules/LEAF_2P_W128B16M4B2C1.gds/launch.sh + 随机化 swap(6-12)/backup(3) 数。k=15 teeth + §4.9(a)(b)(c) 三假全 FAIL + 3-seed 确定性。

## Cross-shard 串台检查

- 4-shard ledger: a5z7g 仅 C claimed (fresh, 无其他 shard 记录)
- 4-shard jsonl trace_source: 无 a5z7g
- 同 domain 已落库 case (AetherLayerPurposeExplainer/PyAetherBridgeDiagClassifier/AutoViaPlanGen/PyLibApiDocGen 等) 全正交 — 子型 "gds_layout_dir_cleanup_analyzer" (layout 工作目录文件分类+viewer-cache 解释器) 首例
