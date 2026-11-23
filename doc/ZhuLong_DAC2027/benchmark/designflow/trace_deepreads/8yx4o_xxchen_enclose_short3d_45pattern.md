# Deepread: 1794991068908_8yx4o — xxchen enclose_short3D 45° pattern fix

**session**: 1794991068908_8yx4o · **user**: xxchen · **host**: hfeg0plg19 · **mc**: 301
**cwd**: /home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1
**status**: completed (exit 0) · **model**: deepseek-v4-flash · **msgs**: 211 (109 user)
**keywords**: drc:655 .gds:150 rtl:22 pdk:2 waveview:1 pex:1 dbcreatepath:1 calibre:1
**scan**: ssh_eda_search_20261123_064315/summary.tsv (mc=301, fresh vs 4-shard ledger)

## 项目背景
同 r1019 (WidthLengthQaPatternGen-001, session 1794825699351_mxlxx) — xxchen 的 DRC_pattern_tool/0.6/device_rule1，QA pattern 生成框架。**8yx4o 是同一工具的不同 DRC function**：`enclose_short3D` (CoreM0C_ENC_005_01Min)，与 r1019 的 `width_length` (CoreM0C_W_001_01Min) 是不同规则。

## 用户真实意图（4 条 user_input）
1. **初始 context**：新增 DRC QA function `enclose_short3D`（LDR `CoreM0C_ENC_005_01Min`）：M0C_FINAL_CORE 沿 45° 斜边包 PC 短边，包覆量 ≥ 0.023，M0C 3D 短线端定义 = 线端宽 < lay1Width3D（0.343）。方案 B：3D 图案金属宽 m3 = lay1Width3D - checkStep。已建 function/enclose_short3D/simple/enclose_short3D.py（解析 lay1size/lay2size、onlyCheck 45° 门控、m3 = lay1Width3D - checkStep、round-to-nearest snap + poly_3d）。
2. **反馈 1**：45° pattern 有问题。参考 GDS `temp_manual_gds/CoreM0C_ENC_005_01.gds` 有两个 45° 斜角特征，用这两个 pattern 类型替换当前 enclose_short3D 里的 45° pattern。pattern num 不再 follow metal_3d_enclose_one_side_land，3D 类型已单独抽取，pattern 从 1 开始顺序命名。
3. **反馈 2**：45° 特征抓取不对 — pattern 1 的斜边长度需满足 lay1Width3D 条件；pattern 2 的两个斜边中间的横线需满足 lay1Width3D 条件。
4. **反馈 3**：pattern 2 的 PC 位置有问题，PC shortSide 应在 lay1Width3D 的边下边，当前太靠右边斜边了。

## 关键产物
- `function/enclose_short3D/simple/enclose_short3D.py`：入口模块，读 config 生成 QA pattern。
- `temp_manual_gds/CoreM0C_ENC_005_01.gds`：参考 GDS，含两个 45° 斜角特征（layer (51,0) + (60,10) 各 2 polys）。
  - inspect 输出：`POLY (15.8934,6.3938)(16.0805,6.3938)(16.0805,6.6553)(15.8934,6.6553)` 等。
- 生成的 .qap manifest：含 pattern 1 (oblique_edge) + pattern 2 (double_oblique_hline)，每类 good/bad 变体。

## 两种 45° pattern 类型（核心几何）
- **pattern 1 (oblique_edge)**：单斜边，斜边长度需 ≥ lay1Width3D。
- **pattern 2 (double_oblique_hline)**：两斜边中间夹一横线，横线长度需 ≥ lay1Width3D；PC shortSide 须在 lay1Width3D 边下边（不能太靠右斜边）。
- 包覆量 enclose ≥ 0.023 (enclose_min)。
- m3 宽 = lay1Width3D - checkStep。
- pattern num 从 1 顺序命名（不 follow metal_3d_enclose_one_side_land 编号）。

## 可造 case 设计（DEBT，下一轮合成）
**task_id**: EDA-Eval-DesignFlow-EncloseShort3DPatternGen-001 · **domain**: physical_verify · **k≥8**

**deliverable**: submit.zip 含 `enclose_short3d_gen.py` + 生成的 `enclose_short3d.qap`。
**config A (public)**: lay1Width3D=0.343, checkStep=0.028, enclose_min=0.023, m3=0.315
**config B (hidden)**: 不同值（如 lay1Width3D=0.300, checkStep=0.025, enclose_min=0.030, m3=0.275）

**check() k=16 断言**：
① zip 合法含 enclose_short3d_gen.py + .qap
② generator py_compile 通过
③ .qap 解析 JSON 含顶层键 (rule_id, lay1Width3D, m3_width, enclose_min, patterns)
④ pattern num 顺序从 1 (1,2) 不 follow metal_3d
⑤ pattern1 good: oblique_len ≥ lay1Width3D (B)
⑥ pattern1 bad: oblique_len < lay1Width3D (B)
⑦ pattern2 good: hline_len ≥ lay1Width3D (B)
⑧ pattern2 bad_short_hline: hline_len < lay1Width3D (B)
⑨ pattern2 good: PC shortSide 在 lay1Width3D 边下边 (B)
⑩ pattern2 bad_pc_pos: PC shortSide 位置错 (B)
⑪ good patterns: enclose ≥ enclose_min (B)
⑫ bad_enclose: enclose < enclose_min (B)
⑬ 45° 角验证 (angle_deg == 45 ± tol)
⑭ cross-input guard: B 运行值匹配 B config (反硬编 A)
⑮ m3_width == lay1Width3D - checkStep (B)
⑯ ≥2 distinct pattern types (oblique_edge + double_oblique_hline)

**negatives**: neg_empty (空壳) / neg_print_only (只 print) / neg_hardcode_a (硬编 A, B 反硬编) / neg_delete_core (删核心返 {})
**§4.9 三假**: (a)空壳 neg_empty + (b)只print neg_print_only + (c)删核心 neg_delete_core 全 FAIL

## 与 r1019 区别（防 intent-dup）
- 规则不同：CoreM0C_ENC_005_01Min (3D 短端包覆) vs CoreM0C_W_001_01Min (长度门控宽度)
- 几何不同：45° 斜边包覆 (oblique_edge + double_oblique_hline 两类型) vs 垂直 length-gating width
- 断言不同：oblique_len/hline_len/PC shortSide 位置/45° 角 vs length/width gating
- 同项目同用户但不同 DRC function，类似 verification suite 多检查项

## 状态
**DEBT: 1 deepread 未合成**。本轮时间预算不足 (40min, deepread+选料已耗 ~28min)，合成完整 case (9 文件 + k=16 check.py + 4 neg + negative_selftest + 自验 + build) 需下一轮。已 claim (physical_verify, mc=301)，下一轮直接合成无需重选料。
