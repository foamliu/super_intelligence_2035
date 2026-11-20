# deepread: 1793927167185_ayinb (dorisz @ hfeg0plg98, mc=59, waveform)

## trace 来源
- session: `/home/dorisz/.cline/data/sessions/1793927167185_ayinb/1793927167185_ayinb.messages.json`
- host: hfeg0plg98 (10.129.8.230) / hfeg0plg94 / hfeg0plg52（同一 session 多 host 命中）
- user: dorisz（fresh-user，不在任何 4-shard ledger / D.jsonl）
- sid `ayinb` 在 shard B ledger 中被 parked，note = "waveview fsdb open wrong-shard D" —— B 明确判定属 D 域并移交给 D，未做 case，本次由 D 回收。

## 用户原话（逐字）
- U#0（act）: 「在terminal里边输入wv打开waveview 在waveview里边把/proj/ddgoa/V0/simdir/finesim/ddgoaF/MatrixRun_Netlist_IDD_20260928_1030_newDOUmodel/里边所有文件打开一遍找到.fsdb结尾的，全部在waveview里边打开。」
- U#47（act）: 「给我弄一个在terminal里边直接输入的命令」
- U#49（act，问半导体物理，与本任务无关）: 「工作在亚阈值区的管子的vdsat是怎么定义的」

## 真实任务
FineSim IDD 仿真输出目录 `/proj/.../MatrixRun_Netlist_IDD_20260928_1030_newDOUmodel/` 下有大量 corner 子目录，每个 `raw/` 里有一个 `finesim.fsdb` 波形文件（实测共 **37 个**）。dorisz 要在终端用 `wv` 打开 WaveView，把这些 `.fsdb` 一次性全部打开，且要一条可直接粘贴执行的命令。

## 关键障碍 + 金标准机制
直接 `wv <fsdb>` 崩溃：`symbol lookup error ... undefined symbol: FT_Done_MM_Var`。
根因：`LD_LIBRARY_PATH` 含 Cadence（INCISIVE/cdsmgr）自带的旧 `libfreetype.so.6`，缺 `FT_Done_MM_Var` 符号，覆盖系统版本。
金标准解（agent U#48 给出的一条命令）：
1. `find <dir> -name '*.fsdb' -type f | sort` 收集所有 `.fsdb`（37 个，全名 `finesim.fsdb`，散在各 corner 的 `raw/`）
2. 清洗 `LD_LIBRARY_PATH`：剔除含 `cdsmgr` 或 `INCISIVE` 的条目，其余按原序保留
3. `LD_LIBRARY_PATH='<清洗后>' wv <所有 fsdb>` 启动 WaveView
agent 还发现 `/proj` 被策略映射到 `/rundata`（path remap）。

## 合成设计（B-grade synthesized L1，waveform）
放弃：真跑 `wv`（需 GUI + license，沙盒不可达）/ FSDB 二进制解析（Q&A）/ `LD_LIBRARY_PATH` path-remap 探测（环境依赖）。
保留核心三件：递归收集 `.fsdb`（精确后缀，排除 `.fsdb.bak`/`.fsdb.tmp` decoy）+ Cadence 路径剔除（cdsmgr/INCISIVE）+ `wv` 启动命令拼装。SUT 只生成命令，不真跑。
- A（SUT 可见）: `sim_A/` 8 corner × `raw/finesim.fsdb` + decoy(`run.log`/`README.txt`/`finesim.fsdb.bak`/`tmp.fsdb.tmp`)；`ld_A.txt` = 6 条路径含 2 个 Cadence。
- B（hidden）: `sim_B/` 12 corner × `raw/wave_B.fsdb` + decoy；`ld_B.txt` = 8 条路径含 4 个 Cadence（cdsmgr×3 + INCISIVE 系）。
- C（嵌入 check.py 反硬编码）: 5 corner × `raw/wave_C.fsdb`；`C_LD` = 6 条含 2 个 Cadence。
A/B/C 的 corner 名、fsdb 文件名、数量、LD 混合全不相交。

## check.py 14 条件 a-n（独立 oracle，subprocess 真跑 SUT on B+C+empty，不 import SUT）
a zip 含 py + 无禁 import/call(subprocess/os.system/popen/eval/exec/socket/ctypes/numpy) + 无 B/C 字面量泄漏(BC_TOKENS 18 个) / b py_compile / c 跑 B 退 0 + JSON 含 6 顶层键 / d fsdb_count==12 / e fsdb_files==oracle 排序列表 / f 无非 .fsdb 混入(decoy 排除) / g removed_paths==oracle(Cadence cdsmgr/INCISIVE 条目) / h cleaned_ld==oracle(剔除 Cadence 其余原序保留) / i wv_command 前缀 `LD_LIBRARY_PATH='` + 含 ` wv ` + 全部 B fsdb 为参数 / j wv_command 不含任何被剔除 Cadence 路径 / k 空目录 edge(fsdb_count==0 + wv_command 含 wv) / l 反硬编码 C(fsdb_count==5 + files==C-oracle + removed==C-oracle + C≠B) / m 3-seed sha256 一致 / n 非 Cadence 路径原序保留

## 维度正交（非 dup）
vs WvWdfVerPathProc-001(#544, Tcl proc 取 wdf 版本/路径) / WvEyeSelect-001(#535, .rep 眼图选点) / FsdbPowerWindowAnalysis-001(#475, FSDB 功耗窗口) / FsdbSpfbaPowerfillCatalog-001(#477, powerfill 目录) / SimFailFsdbProbe-001(waveform, fail probe) —— 本 case = 批量 .fsdb 收集 + Cadence LD_LIBRARY_PATH 冲突剔除 + wv 启动命令拼装，机制不同 → 非 dup ✓

## 自验
ref 14/14 PASS + 4neg(header_only/hardcode_B/naive_no_ld_clean/wrong_glob)全FAIL + §4.9三假(empty/print_only/core_removed)全FAIL + A 逐字节 8 fsdb + 3-seed sha256 一致。k_rationale=k_check=14 ✓
