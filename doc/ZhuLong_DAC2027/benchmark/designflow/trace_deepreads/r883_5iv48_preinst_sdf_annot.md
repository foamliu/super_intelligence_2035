# r883 deepread: 5iv48 (lein@hfeg0pkn002) — preinst.pl analysis + SDF back-annotation file discovery

**session**: 1795166853337_5iv48 · lein · hfeg0pkn002 (10.129.x) · mc3119 · 88 msgs / 638KB
**agent**: lead · updated 2026-11-20T10:51
**scan kw**: verilog:1660;netlist:1180;schematic:113;lib.defs:51;aether:51;cmos:40;primetime:12;.cdl:12
**ledger**: claimed r883 (verification), mc=3119
**ALIVE**: YES (pkn002, msgs 638KB, mtime 11-20 18:51)
**domain**: verification (SDF back-annotation / PrimeTime sdfgen / verilog sim netlist) — A-domain ✓

## 用户 5 轮真实意图（逐字）

- **U#1 msg#0**: `/home/lein/inst/preinst.pl 逐行分析 这个perl脚本`
- **U#2 msg#4**: `/rundata/decqa/V0/simdir/verilog/lein/1113/1103_lp6tb/netlist 在这个文件夹 下查找 统计结果的文件 里面包含 网表 反标情况`
- **U#3 msg#40**: `/rundata/dejoa/V0/simdir/verilog/lein/Final/netlist/V0_LP6TOP_2026Sep20.082026/ 在此路径下查找 含有 parasitics 关键字的 文件 并告诉我路径`
- **U#4 msg#53**: `/rundata/dejoa/V0/simdir/verilog/lein/Final 在这个路径下 查找 含有 parasitics 关键字的 文件 如果有超链接 需要到超链接 指定的路径下查找`
- **U#5 msg#76**: `/rundata/dejoa/V0/simdir/verilog/lein/Final 在这个路径下 查找 含有 annotate 关键字的 文件 如果有超链接 需要到超链接 指定的路径下查找 并给出 文件名 列表`

## trace assistant 关键发现（gold）

### U#1 preinst.pl 分析
脚本路径 `/home/lein/inst/preinst.pl`，**602 行 / 26718 字节**（已 scp 到 r883 workdir）。
- 用途：**自动检查并修正标准单元/存储器单元库 instance 文件（`.inst`）与对应 spice 网表（`.cdl.spf` / `.cdl`）一致性** — EDA 单元库预检查（pre-install / characterization 准备）工具
- 作者：Weihanwu，版本 v1.0(2025/02/18) → v2.7(2026/01/20)
- 关键模块：`use CXMT::Common;` `Getopt::Long` `File::Basename` `Switch` `Term::ANSIColor`
- CLI: `-lib <libname>` (必需，否则 help+exit 1), `-t <tool>` (tool 选项, aether 支持 v2.1+)
- 主流程：`&Readinst` → `&Readnet` → `print "[INFO]: compare inst file to spice netlist"` → `&InstCompare` → 输出 `instcmp.log`
- 数据结构：`%sislibinst` (lib → Totalinsts/Backdoorcells)
- Readinst: 读 `export/$lib.list` + `export/backdoorcells.list`，过滤 backdoor cells，逐个读 `sisregular/$lib/control/$eachinst.inst`
  - 解析 `set_netlist_file <path>` 提取 netlist 文件名
  - 解析 `set_subckt_ports` 提取 pin 列表
  - bus pin 处理（`AN<1>` 单 bus pin v2.4, buspin slow pintype v2.5）
  - 自动 add_pin（inst 无 pin 定义时 v2.3）
  - slow type keep function（v1.2/v1.3）
  - aether cap cell 检测（v2.6/v2.7）
- Readnet: 读对应 `.cdl.spf` / `.cdl` spice 网表
- InstCompare: 对比 inst pin 与 netlist port，写 `instcmp.log`
- **fixture 可行性**: preinst.pl 已 scp 完整 602 行（自包含，无外部依赖除 CXMT::Common），可作 B档 fixture A

### U#2 网表反标统计文件发现
- 路径 `.../lein/1113/1103_lp6tb/netlist` 是**符号链接** → `.../eric1ch/netlist`（assistant 通过 list_allowed_files 返回的 root 字段发现）
- netlist 目录下：`V0_LP6TOP_2026Oct26.185525/` 等顶层单元目录，含 `A_Pattern_Sim.v` / `emy.log` / `netlist.mapping` / `pt_dir/`
- `emy.log` = Aether 网表导出日志（非反标统计）
- `netlist.mapping` = 空
- **关键发现**: 每个顶层单元 `pt_dir/sdf.tcl` 第 31 行 `report_annotated_parasitics -list_not_annotated ...` —— 这就是「网表寄生 RC 反标情况」报告命令
- 实际反标报告输出 → `save_session ./sdfgen.log`（PrimeTime 运行日志）
- assistant 写了 3 个 python 扫描脚本（find_bak_annot.py / find_bak_report.py / find_bak_namelog.py）确认
- 结论：反标统计文件 = `pt_dir/sdf.tcl`（命令源）+ `sdfgen.log`（PT 输出）

### U#3/U#4 parasitics 文件查找（dejoa 路径）
- 路径 `.../dejoa/.../V0_LP6TOP_2026Sep20.082026/` 解析到 `.../lein/source/netlist/...`
- 精确 "parasitics" 命中 0 文件；放宽到 "parasitic" 命中
- `pt_dir/pt_dir/Compress.LP6TOP.sdf.gz`（压缩 SDF，含 parasitic）
- 需 gzip 解压扫描（assistant find_parasitics.py 用 gzip 模块）

### U#5 annotate 文件查找
- 同 Final 路径，关键字 "annotate"，跟超链接
- （未完整提取，msg#76 之后）

## 合成方案（B档 synthesized，DEBT 下轮）

**case_id 候选**: EDA-Eval-DesignFlow-PreinstPlAnnotDiscoverQA-001
**domain**: verification
**task 形态**: analysis-Q&A（双问合并：preinst.pl 逐行分析 + SDF 反标文件发现）
**fixture A**（自包含，从 trace 真实内容重建）:
- `preinst.pl` — 真实 602 行（已 scp，逐字用作 fixture）
- `sim_tree_A.txt` — 合成的 verilog sim 目录树（含 pt_dir/sdf.tcl 片段 + emy.log + netlist.mapping + sdfgen.log 片段 + Compress.X.sdf.gz 占位），从 trace list_allowed_files tool_result 重建
- `sdf_A.tcl` — pt_dir/sdf.tcl 内容（含 `report_annotated_parasitics -list_not_annotated` + `save_session ./sdfgen.log`）
- `sdfgen_A.log` — PrimeTime sdfgen 日志片段（含 "Report : annotated parasitics" / "Not annotated" 统计）
- `task_brief.md` — 用户双问原文（U#1 + U#2 逐字）

**hidden B**（判分，结构不同）:
- `preinst_B.pl` — 不同 perl 脚本（改 lib 名/版本/pin 解析逻辑/作者），但同 .inst-vs-.cdl 一致性检查框架
- `sim_tree_B.txt` — 不同顶层单元名（LP6TOPB / 日期不同 / sdfgen.log 名不同）
- `sdf_B.tcl` / `sdfgen_B.log` — 不同反标命令变体 + 不同 not-annotated 计数

**check.py ≥8 断言**（动态解析 A 推导 ground-truth，非硬编码）:
1. 非空壳：中文 ≥150 字 + 主题词（perl/inst/.cdl/反标/parasitics/sdf）
2. preinst.pl 用途正确识别（.inst vs .cdl.spf/.cdl 一致性检查 / pre-install / cell lib check）
3. preinst.pl 主流程顺序：Readinst → Readnet → InstCompare → instcmp.log
4. preinst.pl CLI：-lib 必需（无则 help+exit 1），-t tool 选项
5. preinst.pl 关键数据结构/解析：set_netlist_file / set_subckt_ports / bus pin / backdoor cells 过滤
6. SDF 反标统计文件定位：pt_dir/sdf.tcl 含 report_annotated_parasitics -list_not_annotated
7. 反标报告输出落点：sdfgen.log（PrimeTime save_session）
8. 符号链接处理：1103_lp6tb/netlist → eric1ch/netlist（assistant 通过 root 字段发现）
9. parasitics 关键字扫描：精确 0 命中 → 放宽 "parasitic" 命中 Compress.*.sdf.gz
10. 反硬编码 A：B-only 标识符不出现（LP6TOPB / 不同 lib 名 / 不同日期）
11. anti-leak：不泄漏 B 独有标识符
12. 确定性：重解析稳定 + markdown ≥2 标题

**neg**: empty / generic-print / wrong_purpose（说是 layout DRC 而非 inst-cdl 一致性）/ leak-B（用 B 标识符）/ core-del（删反标文件定位）

**自验**: ref PASS 12/12 + 3 neg FAIL + §4.9 (a)空zip (b)print-expected (c)core-deleted 全 FAIL

## DEBT
- **下轮合成 5iv48 → EDA-Eval-DesignFlow-PreinstPlAnnotDiscoverQA-001**（preinst.pl 已 scp 在 r883 workdir，sim_tree/sdf.tcl/sdfgen.log 需从 trace tool_result 重建）
- preinst.pl fixture A 完整 26718 字节已就绪
- 仍需：合成 sim_tree_A/B + sdf_A/B.tcl + sdfgen_A/B.log + check.py + neg + 自验

## 选料教训
- 11-21 新 scan (ssh_eda_search_20261121_005100) A-pure fresh 候选核查：
  - jason17w cluster (atgt9/xh3mj/xm22u/pwhqb, mc8000+, verilog+drc+netlist) = VPS verilog regression orchestration，与已造 VpsRegrErrorEngineer-001/VerilogrunPreserve-001 **intent-dup**，skip
  - c9l2c (alan3zh, pkn001, mc3309, innovus/pdk/rtl) = .v vs dont_touch.tcl diff，与已造 VnetDontTouchDiffProduce-001 **直接 intent-dup**（同 user 同 project 同 files），skip
  - zjqiao 8ucoj (mc6060, netlist:5886) = FineSim/PrimeSim SPICE 仿真时长比较 = **C-domain (spice_sim/waveform)** 非 A，skip
  - **5iv48 (lein, pkn002, mc3119, verilog+netlist+primetime) = SDF back-annotation 发现 + preinst.pl 分析 = verification A-domain ✓**，可造（本轮 deepread，下轮合成）
- A-pure 候选池 rotation 状况改善：5iv48/c9l2c/atgt9 均 ALIVE（11-20 新 scan + pkn002 NFS 同步），r877 的 NOFILE rotation 暂缓
