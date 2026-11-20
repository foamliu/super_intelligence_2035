# r531 deepread — axjv8 (xinqiaoz@hfeg0plg56, mc=536, physical_verify)

**USER#0 原话**：
> 你有调用 skipper，calibre 等指令的权限（需要先 ssh 到我的 local），我想问一下，如果让你做 dummy qa，给你一个 gds，让你测量某一层 dummy 生成的情况。量测长宽，间距，和 target layer 的距离，你觉得你可以做到吗？你可以拿 /home/pdk/xinqiaoz/01_dummy/DYT4E_WHCFP_LHCRP_DHCFP/v0d5_rev01/frame/QA/ 中的 gds 文件做测试。

**判定：produce-task ✓**（A档可选：USER#0 是提出需求/目标，未给根因或修复方案）。本轮做 **B档合成**（方向互补，与 r525-r530 一致：纯 Python offline，因为 skipper/calibre binary 在沙箱不可靠）。

## 真实工具链（trace 262 msgs, 1.06MB）
1. **数据前置**：`/home/pdk/xinqiaoz/01_dummy/DYT4E_WHCFP_LHCRP_DHCFP/v0d5_rev01/frame/`
   - `QA_chip.gds`（design topcell `QA_chip`）+ `QA/QA_chip_dummy.gds`（dummy topcell `QA_chip_rev01`）
2. **skipper 合并挂载**（核心难点）：本机缺 Qt4/boost 跑不起 skipper → `ssh hfeg0pfn108` + `xvfb-run -a skipper xxx.tcl -noterm`。
   - `dbIPMerge` 的 REF 只合并重名 cell，三种模式（overwrite/default/swap）都不能把 dummy 树挂进 design topcell。
   - 正解：`dbCreateInst -libId $lib -cellName QA_chip -masterLibId $lib2 -masterName QA_chip_rev01 -instPos (0,0)` 跨库挂载 + `dbLibExport` → `QA_chip_full.gds`（40MB）。
3. **calibre 测量 deck** `measure_deck.svrf`（关键内容）：
   ```
   LAYER m1z     88 8      # dummy
   LAYER m1z_tgt 88 14     # target/prohibit
   LAYER m1z_main 88 0     # main
   LAYER d1b     394 8
   LAYER d1b_tgt 394 14
   LAYER d1b_main 394 0
   m1z_size_all      { INTERNAL m1z < 50 }          # 长/宽
   m1z_space_all     { EXT m1z < 50 }               # dummy 间距
   m1z_space_vio     { EXT m1z < 0.26 }             # 间距违规（Mspace=0.26）
   m1z_to_prohibit_vio { m1z EXT m1z_tgt < 0.22 }   # 到 target 违规（bordSpace=0.22）
   m1z_to_prohibit_all { m1z EXT m1z_tgt < 50 }     # 到 target 全量
   m1z_to_main_all   { m1z EXT m1z_main < 50 }      # 到 main
   # d1B 同构：Mspace=1.0, bordSpace=1.0
   ```
   - SVRF 语法要点：`INTERNAL`（非 `INT`）= 内部尺寸；`EXT l < v` = 同层外部间距；`A EXT B < v` = 跨层间距；命名 RuleCheck 自动写 RDB，不需 `OUTPUT`。
   - 结果量控制：30 万 dummy 时 `EXT < 50` 会输出上亿对 → 按业务阈值收紧（d1b 用 `< 5`）。
4. **calibre 执行**：`calibre -drc measure_deck.svrf` → `measure.drc.results`（ASCII RDB, 374MB）+ `measure.drc.summary`（RULECHECK RESULT STATISTICS）。
   - 实测 D1B：size mean=1.0001 ✓（1×1）；space min=0.5 ✗（应 ≥1.0），593,692 间距违规；to_prohibit 大量=0.5。
5. **Python 解析** `analyze_measure.py`：解析 ASCII RDB → 每 rulecheck 测量值分布（n/min/max/mean um）。
   - RDB 格式：line1 = `<topcell> <precision>`；每 rulecheck：`<name>` + header + `Rule File Pathname:` + `e <id> 2` + 2 行 segment（每行 4 坐标 DBU）。
   - `measure_val(segs)`：两 segment 同向（都竖或都横）→ gap = |x1-u1|（竖）或 |y1-v1|（横）；um = DBU/precision。

## 交付（用户接受）
- 测量报告（per-rulecheck 分布 + 违规判定）。
- SOP 文档 `docs/proposals/04_dummy_gds_measure_qa_sop.md`（609 行，12 章）。

## 合成方向（B档，纯 Python offline，physical_verify L2-boundary）
候选写 `dummy_measure.py <measure.rdb> <guideline.txt> <out.txt>`：
1. 解析 ASCII RDB（topcell+precision、per-rulecheck edge 记录 `e N 2` + 2 segment DBU 坐标）→ 每 rulecheck 测量值列表（um = DBU/precision）。
2. 按 rulecheck 名映射测量类型（`<p>_size_all`=尺寸 / `<p>_space_all`=间距 / `<p>_space_vio`=间距违规 / `<p>_to_prohibit_all`=到target / `<p>_to_prohibit_vio`=到target违规 / `<p>_to_main_all`=到main）。
3. 读 guideline.txt（per prefix：target_size, mspace, bord_space）。
4. **交叉核对**：`<p>_space_vio` 报告数 == count(`<p>_space_all` < mspace)；`<p>_to_prohibit_vio` == count(`<p>_to_prohibit_all` < bord_space)；size 违规 == count(|size_all - target| > tol)。
5. 输出三段：DISTRIBUTION（n/min/max/mean）/ CROSS-CHECK（recomputed vs reported + match）/ VERDICT（PASS/FAIL）。

**与既有 case 区分**：DummyMeas-001=skipper 几何 audit；DummyGeoVerify-001=几何 check；DummyFillCoverageAnalyzer-001=rule deck 静态推算。本案=RDB 解析 + 分布统计 + 显式违规 rulecheck 与全量分布的一致性交叉核对（analyze_measure.py 的实际交付，trace 真实产物格式）。

A 用真实 trace 层名/指南（M1Z 88:8 / D1B 394:8, precision=10000），B 用不同层名/精度/几何/计数（MX2 60:8 / QA3 72:8, precision=2000/5000）防硬编码。k=16 a-p。
