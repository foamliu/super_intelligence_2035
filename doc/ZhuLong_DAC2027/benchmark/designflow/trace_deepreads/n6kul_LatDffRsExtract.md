# Deepread: n6kul (LatDffRsHierExtract)

- **session**: 1790254821572_n6kul · pjli @ 172.16.8.13 · mc=70 · n_msgs=72 (n_user=36, n_asst=36)
- **path**: /home/pjli/.cline/data/sessions/1790254821572_n6kul/1790254821572_n6kul.messages.json
- **domain**: schematic_netlist (Verilog 结构网表解析 → latch/DFF/RS 提取)
- **档位**: A-faithful (B-grade synthesized — 真实 netlist rhr_netlist.sv / /proj 路径不可附加，合成等价 netlist)

## 用户原话（唯一真实提需求轮 U#0，逐字）

> 输入：list:一些模块的instance路径(和网表是对应的)、verilog网表
> 目的：在输入的verilog网表里 抓取这些instance里包含的所有的latch(关键词lat)、DFF(关键词ff)、RS锁存器(关键词rsnand、rsnor)
> 输出：一个csv表，第一列是抓取到的cell的hierarchy，第二列是这些instance cell对应的lib，第三列是这些instance cell对应的cell名字。还输出每个instance cell的每个引脚上的net的hierarchy，方便我结合/home/pjli/Desktop/DFFLatchSR里的代码来trace这些信号，把这个保存到一个log文件里。
> 输入例子：list：[top.Chip.I_PRAC_Performance_TB_0.I_RHRCalCtrl_cqa_4, ...] 、verilog网表：/proj/degpa/V0_CMOS/workdir/pjli/simvision.vcd

纯提需求 + 完整 I/O 规格，未给根因/修复 → A-faithful ✓。其余 user 轮均工具结果/澄清，非新需求。

## trace 演化

1. list_allowed_files(/home/pjli/Desktop/DFFLatchSR) → read_files(rhr_netlist.sv, signal_edge_tracer.py, extract_waveform.py, TraceSignal/trace_signal_fixed.py, find_edge_time.py)
2. search_codebase + grep 找 lat/ff/rsnand/rsnor cell 名模式（latrqx2/ffrqx2/...）
3. 写 extract_latch_dff.py：复用 trace_signal_fixed.parse_netlist → build_cell_lib_map（specparam CDS_LIBNAME/CDS_CELLNAME + `// Library - X, Cell - Y` 注释）→ navigate_to_instance（处理 top.Chip 外部前缀）→ collect_matching（递归收集叶 cell，关键词大小写不敏感子串）→ resolve_pin_net_hierarchy → CSV + log
4. 关键修复：加 leaf-only 过滤（容器模块名含 LATCH 但有子 instance 不报，只报叶 cell）—— 避免 DLUT_PRAC_RHR_LATCH_new 这类容器误报
5. 写 inst_list.txt + RunExtract + test_extract_latch_dff.py
6. run_approved_command 受限无法直接跑，靠 read_files 人工核验

## 金标准泛化（B-grade synthesized）

真实 rhr_netlist.sv (12191 行) + /proj/simvision.vcd + /home/pjli/Desktop/DFFLatchSR/trace_signal_fixed.py 不可附加 → 合成自包含 Verilog 结构网表（A 给 SUT，B 隐藏）。金标 = 通用 Verilog 网表解析器 + 关键词叶 cell 提取 + lib 映射(specparam + // Library 注释) + 外部前缀导航 + 递归收集 + 叶过滤 + pin→net 层级解析。SUT 提交 extract_latch_dff.py（CLI `--list --netlist --csv --log`），check.py 在隐藏 B 上跑 SUT 脚本 vs 参考脚本，结构化比对 CSV（hierarchy/lib/cell 集合）+ log（pin→net 层级）。

## 关键判分点（→ check.py 条件）

- 关键词过滤：lat/ff/rsnand/rsnor 大小写不敏感子串
- 叶 cell 过滤：容器模块名含关键词但有子 instance → 不报；其内叶 cell → 报
- lib 解析：specparam CDS_LIBNAME 优先，回退 `// Library - X, Cell - Y` 注释
- 外部前缀：inst list 路径 `top.Chip.X` 中 top.Chip 在 netlist root 之上，需剥前缀导航
- hierarchy 全路径：CSV 第一列 = inst list 路径 + ... + inst name
- log：每个匹配 cell 的每个 pin → net 层级（dotted path）
- 负过滤：无关键词 cell（AOI/ND/inv）不入 CSV
- RS 两类：rsnand + rsnor 都要能匹配

## 教训

- trace 复用既有 parser（trace_signal_fixed.py）；合成 case 须让 SUT 脚本自包含（hidden B 不提供 parser）
- leaf-only 过滤是核心难点（容器名含 LATCH 误报）—— 必须在 check.py 设独立条件
