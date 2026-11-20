# trace_deepread: j9ycq (xxchen @ hfeg0pkn001) — DRC connectivity path resolver

- **session**: `1793002485489_j9ycq` · user `xxchen` · host `hfeg0pkn001` (10.129.2.10) · mc=288 (drc:452;gds:171;calibre:72;lvs:14 → physical_verify DRC-dominant)
- **agent**: cline (lead), 242 msgs, 123 user turns (mostly tool_result); 5 real `<user_input>` turns.
- **workdir**: `/home/xxchen/workspace/small_tool/drcConnect/0.2/connectivity/` (real, kept per red line #2).
- **package**: `conncheck/` (graph.py, decompose.py, verify_decomp.py, config.py, runflow.py, gdsgen.py, rdb.py, connect_drc.py, layer_map.py) + top-level `validate_refactor.py`, `decompose_path.py`, `config`, `connectPath.rep`, `connectPath_decomposed.rep`.

## 真实任务（多轮迭代）
xxchen 在迭代 DRC connectivity QA 工具——工程师把全连接按 sub-stack 分组拆解，脚本按分组用 findPath 解析路径、生成 connectPath.rep、画 pattern GDS、跑 calibre DRC。5 个真实用户轮：

1. **idx35**：「当前 connectPath.rep 中的 path 显示还是旧的 path 路径。我希望按照工程师拆解的路径+findPath 自动解析获得所有路径。检查脚本，并优化。」
2. **idx69**：「你理解错了，需要每个分组连接的最底层直接 follow 用户给的最底层。如 [M8,HSV,HSP],[M7,V7,M8],...,[M1,V1,M2]，以 M1 为 bottomLayer，再通过 findPath 把这段连接按原先的逻辑解析。不再包含分组外的层。」
3. **idx109**：「我们约定下，以每个分组的最后一个连接的第一个 metal 作为 bottomLayer，如 [M1,CT,TCP,M0U] bottomLayer 就是 M1 了，TCP 和 M0U 不作为 bottomLayer。这里就不应该报错了：ERROR: TCP used as the primary target of edge [M1,CT,TCP,M0U] must be declared in bottomLayer (it becomes a bottom layer). 修改你的脚本。」
4. **idx148**：「修改下你的 pattern 绘制的间距，不同的分组之间的 pattern 的间距拉到到常规间距的 3 倍。」
5. **idx176**：「你当前绘制的 sameNet 的 group0-path1，HSP 连接 和 group1-path1 的图形之间 overlap 了，没有留出正常的 space。检查脚本，并优化。」

## gold 逻辑（用于 reframe）
- `graph.find_all_paths(connectivity, start)`：递归 DFS，4+ 项边 `[lower,via,u1,...]` 每个上层一分支。
- `graph.resolve_substacks(groups)`：**每组 bottomLayer = group[-1][0]**（最后一条边的首个金属）；findPath 只在该组边集上跑，不跨组。
- `graph.multi_edges_info`：4+ 项边 → shield string `lower via : u1->u2->...`（不再报 "TCP must be declared in bottomLayer" ERROR）。
- `verify_decomp.check_decomposition(groups, connectivity, bottom_layer)`：边界金属（非 bottomLayer/非 top）必须被他组共享；每 bottomLayer 可达性。
- `write_path_report`：header `total N paths` + per-group 段 `(bottomLayer: b)` + shield relations + decomposition check findings。
- `runflow.next_path_y`：组间 pattern 间距 = 3× REGULAR_GAP（修 idx148）；`build_test_gds` 防止跨组 overlap（修 idx176）。

## 本案 reframe（档 B）
A 档 gold = 多轮 live-env 迭代（依赖 /apps layer.map + calibre + GDS，不可达且无 ≥8 硬断言牙）→ reframe 为**离线单文件** `connpath_resolver.py`（纯 stdlib），聚焦 idx69+idx109 的核心：bottomLayer 约定 + 逐组 findPath + decomposition check + connectPath.rep 报告。pattern 间距/overlap（idx148/176）属 GDS 几何，不入本案判分（可另造 case）。

## 可见 A / 隐藏 B
- **visible A**：真实 `config_A.py`（5 group：M-stack / CT-shield / TSV / PG-M0C / PG-MT2，bottomLayer=[PG,M1]）—— SUT 沙箱内。
- **hidden B**：`config_B.py` 结构全异（N-stack / 3-target CV-shield SX,SY,SZ / TV-MID-PA / GND-N0C / GND-MX，bottomLayer=[GND,N1]，total 7 paths vs A 的 6）—— 不进 SUT 沙箱，check() 内嵌。

## 子型正交性
C 域 physical_verify **connectivity-path-resolution reframe 子型首例**（与 DrcQaRunDiag QA-tool run diag / DrcJobExitCwdDiag LSF-作业退出 / PexGxrcDiag PEX 抽取失败 / DrcRuleModSem rule modifier 语义 / BridgeConnDiag / DrcLog4ModTruncOpt 正交：本案 = engineer sub-stack 分组 + bottomLayer 约定 + findPath 逐组路径解析 + decomposition check 报告生成）。
