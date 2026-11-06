# 深读 ziv3j — CDL 晶体管统计 + CDL/GDS 文件对照

- **trace**: 1793157233266_ziv3j · user e0047434 · host 10.129.32.190 · mc54 · domain schematic_netlist
- ** msgs**: 134 total · 5 real user turns (`<user_input mode="act">`)
- **A-faithful produce-task = U#0**（唯一提出需求、未给根因/修复）

## U#0 逐字（A-faithful prompt）
```
请到这个目录中：
/home/e0047434/work/std_cell/data/FS204_for_Justin

里面有两个子目录，分别放着cdl网表和gds版图

在本会话中，你不能修改CDL和GDS目录中的任何内容；
你如果需要输出，请写在zl_output 目录中

所有输出尽量用中文，专业名词除外。

请帮我做两件事：
1. 检查cdl和gds是否是一一对应的，看文件名；
2. 对每个cdl，统计它们分别有几根管子组成，既要写文字的report，也要给出适合人类直观查看的可视化输出
```

后续轮（不进 A-faithful prompt）：
- U#17「继续。在上述内容基础上，cdl 的管子数量，需要做必要的统计；请你自己给出应该做统计的指标…」(目标细化)
- U#77「请再帮我查看并统计一个点：对于这些 gds 版图，请查看每个版图有几个金属层…」(另一子任务，超出本轮范围)

## trace agent 工具链
list_allowed_files → 列 CDL/GDS/zl_output 目录 → read_files 样例 CDL → probe_env.py(探测 python/matplotlib/字体/CDL 器件分布) → 写 analyze_cdl.py(分多段 editor edit: string table / parse_cdl / file check CSV / charts / summary) → run_code 跑 → 修 bug(devices_outside_subckt 误报 .INCLUDE/.PARAM 点命令 / OTHER 类太大细化分类规则 / wgaa 参数 / 线性并联扩展检查) → 读特殊单元(AIOI21/DECAP/DELA~G/ICGD1)确认归类 → 生成中文报告。

## 关键事实（金标准 = trace 末尾用户接受的结果）
- **文件对照**：464 CDL ↔ 464 GDS，文件名严格一一对应，only_cdl=0 only_gds=0
- **晶体管**：总数 10812，PMOS=5406 / NMOS=5406（完美 1:1，全 464 单元 PMOS==NMOS 对称）
- **尺寸参数**：全库统一 `l=6n, wgaa=0.035u, nfin=1, nf=1, mr=1`（驱动靠并联管子，非加大尺寸）
- **统计分布**：平均 23.30 / 中位 24 / 最大 80（CKNR2D8）/ 非零最小 2（INVD1）/ 奇数管子单元 0 / 零管子单元 30（18 BOUNDARY + 11 FILL + TAPCELL）
- **功能类别**：28 类全覆盖 464 单元，OTHER=0（INV/BUF/CLKBUF/AND/NAND/OR/NOR/AO/OA/XOR/XNR/MUX/DF/SDF/FA/HA/ISO/BOUNDARY/FILL/TAP/DECAP/DELAY/ICG…）
- **功能族**：145 个族，113 个有多驱动档，112 个族管子数随档位变化（唯一恒定 = FILL 填充族），31 个族严格线性（总管数 = k×驱动档，如 INV 每档 2 管、ND2 每档 4 管、ND3 每档 6 管）
- **CDL 格式**：`.SUBCKT <name> <ports>` 开头，`M` 开头行 = MOS 管（model `psvt_fs`=PMOS / `nsvt_fs`=NMOS），`.ENDS` 结尾；FILL/BOUNDARY/TAPCELL 无 M 器件
- **输出**：FS204_CDL_GDS对照与晶体管统计报告.md（中文 9 章）+ 晶体管数量明细表.md（464 行）+ charts/（11 PNG）+ data/（4 CSV: 文件对照表/单元统计/类别汇总/功能族驱动档检查）+ analyze_cdl.py + summary.txt，全部写入 zl_output/，CDL/GDS 目录未改动

## 合成策略
真实 /proj CDL/GDS 不可附加（464 个文件 + 二进制 GDS）→ **B-grade synthesized**：
- 参数化生成 A/B/B2 三套 CDL 库（每套 = 多个功能族 × 多驱动档，含零管子物理单元 FILL/BOUNDARY）
- GDS 仅生成空 stub 文件（文件名 .gds，对照只验文件名级，与 trace 一致「GDS 为二进制未解析，对应性检查为文件名级」）
- 金标 = 通用 CDL 解析+统计脚本（CLI `<cdl_dir> <gds_dir> -o <out_dir>`），对 A/B/B2 任一输入都能产出正确统计
- 反硬编码：A/B/B2 三轴全不同（cell 数、族集合、驱动档、总管数、类别分布），功能端口跨变体一致简化评估
- 验收聚焦可验文本产物（file_check.csv / cell_stats.csv / category_summary.csv / family_drive.csv / report.md / summary.txt），PNG 图表不验（trace 本身也只说"适合人类直观查看"，无定量校验）
