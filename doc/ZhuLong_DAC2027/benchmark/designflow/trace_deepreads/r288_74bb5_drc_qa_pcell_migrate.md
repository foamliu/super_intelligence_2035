# r288 deepread — 1791770038834_74bb5 (xxchen@hfeg0pkn002/10.129.2.11)

**选料**: r288 ledger-aware dbcreate scan（修复 r287 「.75 scan 盲区」）→ 186 dbcreate cands → 排 ledgered(139)+AVOID(9) → 38 viable → top=74bb5（xxchen, dbc=215, lay=215, sim=0, 纯 layout 创建）→ CLAIMED。
**为何 74bb5**: 215 dbcreaterect + 0 sim = 真实 layout produce-task（非 RAG-inflation/recon-inflation）；xxchen 已交付 r283 DrcRulePkgConvert-001（proven produce-task user）；NEW session（非 ledgered）；grounding 丰富（qa_config_device.txt 124 行 + 28 个 per-rule-type manuals + qa_pattern_tool.py + per-function generators）。
**规模**: archive 2.6MB/575 msgs + active 315KB/49 msgs = 624 msgs / 3MB → 触发 §3 深读例外（>2MB 且 >600 msgs），本轮只深读，r289 必须先交付 case。

## 真实任务（archive AU#0-AU#5 + active U#0-U#3）

xxchen 的 DRC_pattern_tool（/home/xxchen/workspace/DRC_pattern_tool/0.3/device_rule1/）正在做 **SKILL pcell → Python QA pattern generator 批量迁移**（28 个 must_cover rule types，已完成 20/28）。多轮迭代：
- AU#0「阅读 AGENTS.md + QA_pattern_notes.md，理解 QA pattern 绘制准则」
- AU#1「继续下一个 must_cover 的 pcell skill→python 转换」
- AU#2 报错（VIRLAYER M1_NO_DUMMY 解析失败，layer map 格式）
- AU#3「must_cover OK，继续 no_overlap 转换」
- AU#4「无 value 的 function 用 check 代替 0（0 也是值，有检查歧义）」
- AU#5 报错（VIRLAYER SA 解析，no_overlap config）
- active U#0 上下文摘要（会话延续说明，20/28 完成，auxRegion 迭代重构）
- active U#1/U#2 报错（draw() signature / finish() bbox — concave_corner_enclose generator）
- active U#3「总结 DRC QA tool 开发进展（已转/未转/优化/deviceRule+VIRLAYER 使用配图/未完成）」

## 真实 grounding（已 scp 到 .75 workdir）

1. **qa_config_device.txt**（124 行，真实附件）：
   - `TOOL config` output_gds=QA.gds / output_ANT_gds / layerMap=layer.map
   - `TOOL TECH` errorLayer=4001;51 / bordLayer=4002;51 / textLayer=230;0 / waiveLayer=321;51 / checkStep=1 GRID / DBunit=10000 / precision=10000 / GRID=0.0001 / bordSpaceRatio=20 / bordSpaceX=5 / bordSpaceY=10 / bordEncPattern=2 / cellSpaceX=30 / cellSpaceY=10 / cellSpaceRatio=25
   - `DEVICE MOS` NMOS/PMOS/NMOS_ANT/PMOS_ANT/NMOS_peri（AA AT4;NCH / POLY PG;NCH / implant NSD/PSD/NW + w/l/imp_enc_aa/aa_enc_poly/poly_ext_aa）
   - `DEVICE DIODE` PPD/NPD（AA AT4;NCH / via PC / implant PSD MT2 / NSD MT2 NW + w/l/viaSize/imp_enc_aa）
   - `LDR connect` ANT_connect（GATE {AT4;NCH PG;NCH} {AT4;PCH PG;PCH} ...）
   - `VIRLAYER` 12 个虚拟层定义：DIFF=AT4;PCH,AT4;NCH,AT4;DUMMY2,AT4;CMP / NDIFF=DIFF&NSD / PERI=BORD;drawing&BORD;PERI / Pguardring=AT4;PCH&PSD+0.05 / M1_NO_DUMMY=M1;drawing,M1;CLOSE / M2_NO_DUMMY / SA=RLDEV;mark1 / SWD=RLDEV;mark2 / SWC=RLDEV;mark3 / CORE=SA,SWD,SWC / MOS_ANT=NMOS_ANT,PMOS_ANT
   - `QACELL` ~25 条：DGX_ENC_018_00..021_00（enclose，DGX->AT4;NCH/NMOS/NDIFF，value 0.6/0.975/1.2，params layer2_device/insideLayerNotAllowedOutside/dir/w/deletePattern/waivePattern）+ DNW_W_000_00（width 8.260）+ DNW_S_001_00（space 9.240，Check45dgree）+ DNW_EXT_005_00（alayer_extend_blayer NW->DNW 1.850，width/length/withTwoSide/Layer1NOTVia/InsideTouch/OutsideTouch）+ DNW_O_006_00（layer1_overlap_layer2 NW->DNW 1.386）+ DNW_S_008_00_c/p（space DNW->Pguardring 2.08/2.10，auxRegion CORE）+ DNW_A_004_00（area 52）+ DNW_HA_014_00（hole_area 52）+ DNW_CL_015_00（step_height 0.176）+ NCH_S_002_02（prl_space 0.366）+ M1_S_008_01/012_00（space_upon_width 0.215/0.553）+ M1_LS_013_02/03（line_end_space）+ M1_F_028_00（orthogonal_45degree）
2. **rule manuals**（28 个 markdown，per-rule-type）：must_cover.md / no_overlap.md / enclose.md / width.md / space.md / area.md / hole_area.md / step_height.md / prl_space.md / space_upon_width.md / line_end_space.md / orthogonal_45degree.md / alayer_extend_blayer.md / layer1_overlap_layer2.md / concave_corner_enclose.md / convex_corner_enclose.md / single_via.md / metal_to_unrelated_via_space.md / via_around_via_space.md / rectangle_size.md / dumbbell_shape.md / and_layer.md / larger_3d_metal_enclose_via.md / prl_space.md / space_upon_width.md / space_different_direction.md / space_upon_width.md / pattern_design.md / script.md / QA_tool_main.md
   - 已读 must_cover.md（198 行片段）：二值检查（A 覆盖 B，无阈值），good=1（A 完全包覆 B 四周余量）+ bad=3（inset_right_fail/island_fail/right_shift_fail，errorLayer 4001;51 高亮 B 区域），QACELL value=check（非数值），he=5*checkStep
3. **QA_Pattern_tool/script/qa_pattern_tool.py**：主工具，generate_single_cell() 调 generator.generate(good_subcell, eff_layer1, eff_layer2, l2_poly, value, good_options)（active U#1 报错处 line 377）
4. **QA_Pattern_tool/function/<type>/<name>.py**：per-function generators，如 concave_corner_enclose/simple/concave_corner_enclose.py（generate() + finish(bbox)，active U#2 报错处 line 237）
5. **AGENTS.md / QA_pattern_notes.md / skill_pcell_conversion/conversion_progress.md**：迁移计划 + 绘制准则 + 进度（20/28）

## 工具执行（archive）

assistant tool_use: editor=112 / read_files=110 / run_approved_command=46 / list_allowed_files=24 / search_codebase=6 / run_commands=4 / SandBox_MCP_Server__run_code=1。215 dbcreaterect markers 来自 run_approved_command 跑 qa_pattern_tool.py（pyAether dbCrtRect 渲染 QA cell），非 SandBox 直接调（仅 1 次 SandBox_run_code）。

## B 档重定义（离线 L1/L2）

真实 pyAether/OA + layer.map + GDS 输出不可沙盒复现 → 离线核心 = 给定 qa_config（TOOL/DEVICE/VIRLAYER/QACELL）+ layer.map + rule-type specs → 结构化 qa_pattern_plan.json：
- 解析 qa_config（TOOL/TECH 全局参数 + DEVICE 定义 + VIRLAYER 虚拟层展开 + LDR connect + QACELL 条目）
- 对每个 QACELL：解析 rule type / layer1->layer2（经 VIRLAYER 展开）/ value / params{} → 派发到 rule-type 处理器 → 计算 good/bad pattern geometry（bbox + errorLayer marker 位置）+ value/check + cell 命名（QACELL name）+ cell 布局（cellSpaceX/Y/bordSpace）
- 输出：{global_config, devices, virtual_layers, cells:[{name, rule_type, layer1, layer2, value, params, good:[{geom, markers}], bad:[{geom, markers, viol_reason}], layout}]}
- check.py 在 hidden B 上 subprocess 真跑候选（L2）

## DISTINCT from 现有 layout_aether / physical_verify 系

- **r286 DrcPatternPkgGen-001**（lizwen）：DRC deck SVRF → pattern query → layer map → grid snap → 单 pattern PASS/FAIL render .oa。核心 = SVRF 解析 + query 解析 + 单 pattern 几何。
- **本案 74bb5**：QA config（VIRLAYER/QACELL 多 rule-type）→ rule-type 派发 → 多 cell good/bad 几何 plan + errorLayer markers + DEVICE/VIRLAYER 上下文。核心 = config schema 解析 + VIRLAYER 递归展开 + rule-type dispatch + good/bad 双 pattern 几何 + errorLayer 高亮位置。
- 差异维度：输入（qa_config vs DRC deck）、核心（dispatch+good/bad 双 pattern vs query+单 pattern）、deliverable（cell plan JSON vs pattern package）、rule 类型集（28 SKILL rule-types vs DRC deck 规则）、上下文（DEVICE/VIRLAYER/LDR vs 无）。
- 与 r283 DrcRulePkgConvert-001（xxchen 同 user，SVRF deck+LDR CSV→rule package）亦不同：r283=SVRF 解析+CSV schema，本案=QA config cell plan 生成。不同 trace + 不同 deliverable + 不同核心算法 → 无撞库。

## hidden B 反硬编码思路

A = qa_config_device.txt slice（DNW/M1 rule types, AT4/M1/M2 layers）vs B = 另一 slice（DGX/NCH rule types, 不同 VIRLAYER 组合, 不同 value/params）。A/B QACELL name 集合 + rule-type 集合 + layer 集合全不相交 → 强交叉输入守卫（挫败 print_expected_A / wrong_layer_map）。A 有 DEVICE MOS+DIODE，B 只 MOS（或反过来）→ DEVICE 解析必须 generalize。

## r289 计划（必须先交付 case）

1. 合成 assets/A（prompt + task_brief + qa_config_A.txt + layer_map_A + rule_specs_A）+ hidden/B（qa_config_B + layer_map_B + hidden_manifest）
2. reference/qa_pattern_plan_gen.py（golden）+ check.py（≥8 条件 a-n，含 VIRLAYER 展开 + rule-type dispatch + good/bad 几何 + errorLayer marker + value/check + 交叉输入守卫 + cell 命名 + 布局）
3. negatives（empty/print_expected_A/core_deleted/wrong_virlayer_expand/naive_single_ruletype）+ negative_selftest.py
4. 自验：ref PASS + §4.9 三假 FAIL + negatives FAIL + k_rationale=k_check≥8 + test==disk + jsonl roundtrip
5. mark 74bb5→case + 日报一行
