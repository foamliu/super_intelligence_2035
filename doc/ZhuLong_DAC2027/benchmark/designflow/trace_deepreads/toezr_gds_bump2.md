# 深读笔记: toezr (xxchen / hfeg0plg53 / mc318)

session: 1792323159551_toezr.messages.json (349 msgs, 187 user, 162 assistant)
domain: schematic_netlist (GDS layer manipulation via skipper TCL)
case: EDA-Eval-DesignFlow-GdsBump2-001

## 用户原话 (U#0, A-faithful 提需求轮)
> 帮我用tcl+skipper工具 写一个脚本，脚本名称 gds_bump2，
> 功能：把gds中的所有层次按照用户指定的number增加一个值。
> 如原本 gds number 为100 ，用户给bump2=20000, 导出的gds number 既为 20100
> 你可以参考下面目录下的tcl脚本写法：module_checkFlow
> 测试GDS为：A1_CA2_connection_check_A1.gds

workspace: /home/xxchen/workspace/small_tool/gds_bump2 (含测试 GDS + module_checkFlow 符号链接)
policy: agent-policy-engine enforcing (run_approved_command profile, editor)

## agent 工具链
1. list_allowed_files 探 workspace → 找到 A1_CA2_connection_check_A1.gds + module_checkFlow symlink
2. skills(qualib-tcl-generator) → 不匹配(qualib 检查流程,非 skipper GDS)
3. list_allowed_files module_checkFlow/{gdsMerge,common} → 找到 common/run_skipper.py (skipper 调用模式)
4. read_files run_skipper.py → skipper <tcl> -noterm 调用, TCL 内 dbImport/dbLibGetId/dbLibExport
5. RAG search_apis "modify layer number" → 返回 Cadence techfile API (非 skipper, 弃)
6. 探索 skipper 安装: /apps/empyrean/tools/skipper, PDF 文档 (pdftotext 需 clean env)
7. probe1.tcl: `info commands db*` → 拿到 dbLayerMove/dbLayerCopy/dbLayerDelete/dbLayerExist/dbLibLayers
8. probe 空参触发 usage → dbLayerMove -libId -cellName -lpp1 -lpp2 -depth 语法
9. editor 写 gds_bump2.tcl (多轮 PART1/2/3 拼装)
10. run_gds_bump2_test.py 回归 (bump=20000 + verify_bump.tcl + roundtrip + error handling)

## 金标 gds_bump2.tcl (304 行, 磁盘 /home/xxchen/workspace/small_tool/gds_bump2/gds_bump2.tcl)
结构 (layer-direct conversion, 非逐 cell):
- helpers: gb2_log/gb2_die/gb2_lpp_split/gb2_lpp_desc(降序)/gb2_lpp_asc(升序)
- gb2_parse_args: 位置 <input.gds> <bump2> [output.gds] + env GDS_IN/BUMP2/GDS_OUT 回退
  - 整数校验 regexp ^[+-]?[0-9]+$ ; 默认输出 <stem>_bump<bump>.gds
- gb2_own_figs: dbCellGetByName + dbCellGetBBox -withLabel + dbFigQuery -stopLvl 0 -maxFigNum -1
- main:
  - dbImport + dbLibGetId
  - dbLibLayers -libId → allLpps 快照
  - 前置范围校验 [0,65535] (nl<0||nl>65535 → rangeErr → gb2_die 不改任何东西)
  - 碰撞告警 (new_lpp 已在 allLpps → WARNING, 内容会合并)
  - dbLibTopCell -libId → tops (空则回退 dbLibGetAllCells)
  - figTotal0 = sum own_figs (验证基线)
  - 排序: bump>=0 降序 / bump<0 升序 (避免 moved-to 被当 source 重处理)
  - 逐 lpp: dbLayerMove -libId -cellName $top -lpp1 $lpp -lpp2 $newLpp -depth 100000 (层级一次移)
  - 验证 sweep: figTotal1 vs figTotal0 ; leftover(cell,lpp) 局部 dbLayerMove -depth 0 修复
  - dbLibExport $outGds ; 文件存在+非空校验
- 配套: gds_bump2 (bash wrapper exec skipper) + verify_bump.tcl (独立 checker, cell-by-cell 比对 fig count)

## trace 终局
- U#345 "上面的任务完成了吗？"
- A#348 "是的...A1_CA2_connection_check_A1_bump20000.gds 已生成...24 cells/34 lpp 全部成功...run_gds_bump2_test.py 全通过(bump=20000)"
- 磁盘: A1_CA2_connection_check_A1_bump20000.gds (11272 bytes) + bump30000.gds 均生成
- 用户隐含接受 (无拒绝)

## 降级理由 (L1-boundary)
真实 skipper 二进制 (/apps/empyrean/tools/skipper) 是 Empyrean 商业工具, 评测沙箱无许可证/环境,
无法跑 dbImport/dbLayerMove。降级为读 config 确定性生成器 gen_gds_bump2.py: 读 config.json
(tool/input_gds/bump2/output_gds/gdsii_layer_max/hierarchy_depth/top_cells/cells/lpps[]),
计算 old->new mapping + 范围校验 + 碰撞检测 + 排序, 生成 gds_bump2.tcl(完整 skipper TCL 结构) +
layer_bump_plan.json(mapping/sort_order/collisions/fig_total)。保留全核心结构 (六 API/范围/排序/验证/层级移动/导出)。

## 资产
- A (visible): config_A.json (A1_CA2_connection_check_A1, bump=20000, 33 lpp layers 1-160, 24 cells, no collision) + prompt.txt(U#0 逐字) + task_brief.md
- B (hidden): config_B.json (X2_DB1_via_chain_check_B1, bump=12, 22 lpp layers 1-300, 18 cells, 10 collisions) + hidden_manifest.json (expected mapping/collisions/cross_guard)
- check.py 15 条件 a-o, ref PASS 15/15, 4 negatives ALL-FAIL, §4.9 三假 (empty→c/print_fixed_A→e/core_deleted→d) 3-distinct ✓
