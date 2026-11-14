# trace deepread — 0p7m5 (miccao@hfeg0pkn004, mc=75, physical_verify)

**round**: r561  **case**: EDA-Eval-DesignFlow-MetalProximityGroup-001 (physical_verify L2-boundary, B-synthesized, k=14 a-n)
**claim**: `trace_ledger_C.tsv` 1793067650462_0p7m5 / miccao / hfeg0pkn004 / mc=75 / physical_verify / claimed 2026-11-14 15:51

## 1. 用户意图（produce-task，A 档eligible 但取 B 档 synthesized）

U#1（原话）：「在array die中...将临近的metal线给总结出来...我给你个gds，你要怎么处理」
= 给 GDS，找每根 metal 线**邻近的 metal 线**，用于串扰分析。阈值 **182nm**，目标层 **M1A/M2A/M3A**（layer 500/502/504，来自 `/apps/imctf/libs/dfii/cxmtG4C/current/layer.map`）。

**末轮关键澄清**（msg 146，原话）：「我需要知道的是邻近的那根的**信号名**，而不是 net 名，比如 `s40m2wle<100>` 旁边是 `s40m2wle<101>` `s40m2wle<99>` 这种」
= 邻居必须是**信号名**（同族相邻索引 strap），**不是** net 名、也**不是**未命名的 metal id（如 `uM2A#12`）。**这是本题输出语义的核心**。

信号命名规则：`s<NN>m<d><wlo|wle><idx>`，例如 `s40m2wle<100>`（<NN>=阵列号 40、<d>=metal 序号、wlo|wle=strapping 族、<idx>=族内索引）。

## 2. trace 现场算法（assistant 实做，有 caveat）

- `gdslib.py`：轻量 GDSII parser+flatten（自写，不依赖 gdspy），解析 Ary_m512Meg_U_fbcc.gds（223MB, 542 cell, libname=ddgoa_array_core, top=Ary_m512Meg_U_fbcc）。
- `analyze_s40.py` / `analyze_s40_txt.py`：读 GDS → flatten 到顶层 → 在 s40 区域（label layer 230=text）找 label → 按 family prefix `s40m<d><wlo|wle>` 分组 → bbox coarse-filter + segment-distance refine 182nm 阈值 → 输出 `s40_neighbors.txt`（852 行，格式 `A: B C...`）。
- metal 几何在 WL-strapping 子cell（`lwx592?_*_WLstrapping_M1A_gut`、`BL_WLstrapping_gut*`、`WLe/WLo_M1A_M2A_con*`）经 AREF/SREF array 摆放；scaleUUperDBU 0.0001 → 1DBU=0.1nm，182nm=1820DBU（GDS UNITS record 异常，不可用）。
- s40 区域有 7 个 metal 族 ×1184 label/族（m0wle/m1wlo/m2wle/m3wlo/m4wle/m5wlo/m6wle），用户只要 m1/m2/m3。

## 3. live-run caveat（**不**复制为 oracle 的「正确」）

- M1A 在 s40 区域**缺失**（layer 500 几何不在该区域）；
- M2A/M3A 在该区域仅 12/9 polys；
- strap 与 label **错位**（坐标 x 压缩）；
- 产出 `s40_neighbors.txt` 的邻居全是**未命名 id**（`uM2A#idx`）而非真实信号名 → 触发用户末轮澄清。
→ 因此本题**不**直接复制 live 产出，而是用**干净的合成 deck** 让算法产出正确、可验证的信号名-邻居输出。

## 4. B 档 case 设计（synthesized mock-behavioral）

把 live GDS metal-邻近重构为**纯 Python JSON layout deck fixture**（线段级 metal 几何，mock gdslib/gdspy），核心算法不变：
- deck = `{threshold_nm, target_layers, layer_map, segments[{signal, layer, x0,y0,x1,y1}]}`，每段是水平 metal strap，signal 名 `s<NN>m<d><wlo|wle><idx>`。
- 算法：①读阈值 ②层过滤（丢 m0=499/m4=506 decoy）③**真实线段-线段距离**（不只 |y0-y1|）④≤阈值互为邻居 ⑤输出 `<signal>: <neighbour...>` 文本，行/邻居按信号名字典序，无邻居也输出 `<signal>:`，确定性。

**关键陷阱设计**（让 oracle 可强验证）：
- **naive-|dy| 陷阱**（B deck）：`s52m2wlo<8>@[0,800]@420` 与 `s52m2wlo<9>@[1100,1900]@560`，|dy|=140<182 但真实线段距离=√(300²+140²)=331>182 → **不是**邻居。只看垂直差的错误算法会判错（check.py cond g 抓）。
- **跨族邻居**（B deck）：`s52m1wlo<7>@280` 与 `s52m2wlo<8>@420`（不同金属层 m1/m2）距离 140≤182 → 跨族邻居（cond h 验证真实距离非仅同族相邻索引）。
- **层过滤**（B/B2 deck）：m0/m4 decoy 必须被丢弃（cond f）。
- **无邻居行**（B deck `s52m3wlo<10>` 单根；B2 deck `s60m3wle<6>/<7>` pitch 190>182）：空邻居行（cond j / cond m，阈值强制）。
- **B2 反硬编码**：B2 用不同信号族（s60m1wle/s60m2wle/s60m3wle）+ m1<3>↔m2<4> 距离 210>182 无跨族（与 B 不同），硬编码 B 输出必败（cond m）。
- **确定性**：重跑 B 字节一致（cond n）。

## 5. GOLD 自验

- ref 在 A/B/B2 三 deck 的产出与设计预期逐行一致（A: 8 行含 m1<12>↔m2<20> 跨族 + m3 空邻居；B: 6 行含 m1<7>↔m2<8> 跨族 + m2<9> 陷阱不邻居 + m3<10> 空；B2: 7 行 m3 全空无跨族）。
- negative_selftest：4 negative（core_deleted/naive_dy/no_layer_filter/hardcode_B）全 FAIL，ref PASS。
- 逐 negative 失败原因核对：naive_dy→cond g（陷阱对）；no_layer_filter→cond d（多 2 行 m0/m4）；hardcode_B→cond m（B2 信号集合==B）；core_deleted→cond d（0 行）。checker 区分度正确。

## 6. 交付物

- `assets/MetalProximityGroup-001/`：task_brief.md, input_spec.json, layout_deck_A.json, proximity_spec_A.json, hidden/{layout_deck_B,B2}.json + proximity_spec_{B,B2}.json + hidden_manifest.json
- `reference/MetalProximityGroup-001/`：metal_proximity_ref.py, check.py(14 cond a-n), negative_selftest.py, negative/{4 files}
- `EDA-Eval-DesignFlow_C.jsonl`：342→343
- k_rationale = k_check = 14 ≥ 8 ✓；≥1 subprocess-run（cond c）✓；≥2 negatives（4）✓；§4.9 four-fake-submit 全 FAIL ✓；hidden B/B2 randomized ✓
