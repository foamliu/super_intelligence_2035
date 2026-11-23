# deepread: 1794924287186_13jki (jzeng @ hfeg0pkn002, physical_verify, mc=160)

## session meta
- user: jzeng, host: hfeg0pkn002 (10.129.2.11)
- session: 1794924287186_13jki, status=failed, model=deepseek-v4-flash
- cwd: /ai_sandbox/drcpa/V0/agentdir/jzeng
- 152 messages, 745KB, forked from 4kf4h (M4M5PowerOverlapPatch-001 parent)
- keywords: pyaether drc cellview aether (mc=160, C-dominant)
- tools: pyAether RAG search_apis + editor + run_approved_command(py_compile) + SandBox_MCP_Server__run_code

## 真实任务（user_input 流）
1. **MSG#0**: V4 patch 生成 —— 在 M4（横向）× M5（纵向）交点处贴 V4 patch，按多条规则过滤（width rule / corner skip / containment skip / dedup）。
2. **MSG#20**: corner_tol 调整 —— 交点距离 wire 端点小于 corner_tol 视为角点，跳过。
3. **MSG#40**: dedup 策略 —— 同一交点被多条 wire 重叠覆盖时只生成一个 patch。
4. **后续 refinement**: containment skip（patch 完全落在另一 wire 内则跳过）、width rule（wire 宽度不匹配 v4_params 期望宽度则跳过）。

## assistant 工具链
- read_files 多段读 V4_gen_V4.py（继承自 4kf4h parent 的 V4 patch 生成器）
- RAG search_apis/get_api_details: dbCrtRect, dbNewCellView, dbGetTrueOverlapsEx
- editor 多段写 V4_gen_V4.py
- run_approved_command: check_syntax.py（py_compile）
- SandBox_MCP_Server__run_code 最终直接写文件
- 最终产物：V4_gen_V4.py（纯 ASCII，py_compile 通过），含 4-rule 过滤管线

## 关键算法（最终版）
1. 扫描 deck：m4_wires（horizontal，给定 x_span/y/width）+ m5_wires（vertical，给定 x/y_span/width）
2. **计算交点中心**：每个 M4 × 每个 M5 的几何交点 → (cx, cy)
3. **width rule 过滤**：wire 宽度必须匹配 v4_params 期望宽度（容差内），否则跳过该交点
4. **corner skip**：交点到 wire 端点距离 < corner_tol 视为角点，跳过（避免 patch 贴边）
5. **containment skip**：patch 完全落在另一 wire 覆盖范围内则跳过（避免重复）
6. **dedup**：相同 (cx, cy) 中心去重（多条 wire 重叠时只留一个）
7. 输出 patch 列表 [{center_x, center_y, ...}]

## case 合成
- **case_id**: V4PatchMultiRuleSkip-001 (physical_verify, L2)
- **离线几何版本**：pyAether 在线后端沙盒不可达 → 给 deck JSON（m4_wires horizontal / m5_wires vertical / v4_params / corner_tol），算 M4×M5 交点处 V4 patch 中心，按 4 条规则过滤，输出 out.json
- **config A（公开）**: 4 M4 + 8 M5, corner_tol=0.10 → 15 patches（4-rule 全部 exercise）
- **config B（隐藏主判）**: corner_tol=0.05, 不同坐标/线数 → 13 patches
- **config C（隐藏 cross-input guard）**: 2 M4 + 3 M5, corner_tol=0.20 → 2 patches（与 A/B 线数全不同，反硬编）
- **k=14**: zip+py_compile+run B+keys+n_patches+B count+corner skip count+containment skip count+dedup count+width rule count+patch[0] center+cross-input C count+C corner skip+C containment skip
- **4 neg distinct layers**: empty→cond2 / print_only→cond3 / hardcode_a→cond7 / delete_core→cond10
- **§4.9 三假**: (a)空壳 cond2 + (b)只print cond3 + (c)删核心 cond10 全 FAIL
- **防 intent-dup**（vs AutoViaV4MaxFillPack-001 l9na3 / AutoViaV4Dir3DY-001 wy27j，同 jzeng/IMCleAutoVia 项目）: 算法不同（M4×M5 交点 4-rule 过滤 vs 最大 V4 阵列填充 rows×cols vs 单 V4+dir_3D_Y M4 enclosure fill），产物不同（patch 中心坐标列表 vs pad+vias manifest vs vias+m4_fills JSON），断言不同（4-rule 过滤 cross-input 2-patch guard vs rows×cols max-fill 3×7 guard vs R90 cut 取向 guard），trace 不同（13jki vs l9na3 vs wy27j）
