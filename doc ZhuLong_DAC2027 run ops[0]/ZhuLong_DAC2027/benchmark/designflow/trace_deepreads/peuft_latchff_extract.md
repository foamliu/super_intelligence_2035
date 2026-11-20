# Deepread: 1792466303393_peuft (zxtu / hfeg0pkn002 / mc167)

## U#0 (verbatim, A-faithful requirement)
> 给定一个subckt网表描述 分析这个subckt的逻辑功能，/rundata/.../subckt_template， 所有的subckt都在这个文件中，分析所有subckt的逻辑功能，分析哪些subckt是latch/FF, 将这些latch/FF subckt提取出来，放到/proj/.../ 目录文件下面

## Trace shape
- 303 msgs / 1.38MB / 22 user turns (多轮: U#0 提需求, U#67 要求端口签名 CSV, U#73/U#81/U#99 改进轮)
- 网表 118MB / 9214 subckts (LP5X DRAM 晶体管级库), agent 无法直接 read (too large) → 写 python 脚本分析
- agent 在 /home/zxtu/ 写 ~20 个迭代脚本 (analyze_subckts.py → find_latch.py → dump_ffcells.py → dump_leaf.py → storage_detect.py[corrupted→storage_detect2.py] → analyze_seq.py → refine.py → filter_final.py → select_final.py → final_v3.py[corrupted] → make_selection.py → extract.py → produce_table*.py)
- 多次 editor 损坏 (`$'`-before-quote 触发 splice bug) → 重写为 fresh 文件

## Gold algorithm (3 scripts, 抓自磁盘 /home/zxtu/*.py)
1. **storage_detect2.py** (结构性检测): parse .SUBCKT/.ENDS → index MOSFET(XMM*: gate→drain) + 子实例(X*: port mapping) → 递归 port_io 展开 (in/out ports, break cycle) → 每 subckt 数据通路图有向环检测 (DFS WHITE/GRAY/BLACK) → seq vs comb (9214 → 1677 seq)
2. **make_selection.py** (数字 latch/FF 筛选): interface 过滤(control_re ^ck|clk|lat|en|wck|ce|lc + din_re ^d + dout_re ^q) OR name_marker(ff/latch/lat, LAT_FALSE 黑名单 interpolator/regulator/...) → is_primitive(不实例化其他 seq) → RS-latch 补充(is_rs: rsnand|rsnor|rsaoi|rsoai 或 ^rs_|rseg|rsr) → 304 primitive + 32 macro = 336
3. **extract.py** (逐字提取): 按 seq_names/primitive/macro 列表从原网表切出 verbatim body → latch_ff_subckts.sp / latch_ff_cells.sp / latch_ff_macros.sp + latch_ff_analysis_report.txt
- 关键拒判: VpcsgPhaseDrvVdd1IP(电平转换,有环但无 D/Q 接口+无 latch 名)→rejected; TempFF(mux wrapper 实例化 ffrqLx1 但无端口级环路)→comb

## Benchmark 化 (L1-boundary, downsampled faithful)
- /rundata 网表 e0031982 无权读 → 自建降采样网表 (匹配真实格式: XMM 晶体管/X 子实例/inh_ 电源/各类 cell)
- 资产 A: subckt_template_A.sp (11 subckts: inv/nand2/nor2/mxi2Lx1 comb + ffrqLx1/latqGFx1/lat2inECC/R1in1Latch seq-prim + VpcsgLvlShift seq-rejected + TempFF comb-hier + FFmacroWrap seq-macro)
- 隐藏 B: subckt_template_B.sp (10 subckts, 不同命名族 + rsnor22 练 is_rs 路径 + dffrLx2/latqBx1/lat2inB/FFmacroB)
- ref gen_latch_ff.py = 三脚本融合参数化; check.py 18 条件 a-r; negatives 5 个 (§4.9 distinct r/d/e)
- 自验: ref PASS 18/18 · 5 negatives ALL-FAIL · test==disk EXACT(sha f314b7d0) · k_rationale=k_check=18 ✓
