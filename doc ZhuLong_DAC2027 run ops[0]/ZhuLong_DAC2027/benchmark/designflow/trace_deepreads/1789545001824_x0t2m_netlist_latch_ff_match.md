# Deepread: 1789545001824_x0t2m (ethanw@hfhds201) — Netlist Latch/FF Match Process

## Session Meta
- **sid**: 1789545001824_x0t2m
- **user**: ethanw, **host**: hfhds201 (10.129.32.75 = .75 本机)
- **status**: idle, 183 msgs, 3 user turns, model=deepseek-v4-flash
- **cwd**: /rundata/dscqa/V0/simdir/finesim/workdir/ethanw/local/cck/0916_cck
- **scan**: mc=145, lvs:6025;netlist:2464;schematic:490;cmos:245;hspice:143;analog:65;drc:57;pex:40

## User Intent (U#2, verbatim — A档 faithful seed)
> "I want to create a matching process that uses the information in DDR6TOP_Latch_FF_RS.list to match the netlist. For example, (dscqa_digital latrq2_ckUnit corresponds to * Library : dscqa_digital * Cell : latrq2_ckUnit, and the library and cell need to be exactly matched) After matching, the netlist will be * Library / * Cell / * View / * Inherited view list... .SUBCKT latrq2_ckUnit Clk0 Clk0N Clk1 Clk1N D0 D1 Q RN vbn! vbp! vcc! vss! ... arrange according to the rules: subckt, refname, signame, data, RN, SN, R, S ... In the template, there are reference arrangements available. In case of conflicts, the one that is captured will prevail ... If 'cm...' appears, it can be considered invalid and will not be processed. (A file containing the matched output will be generated for viewing. There will be three lines of 'lib cell subckt' information). Arrange the output (in a format similar to that of the template file)"

**判定**: CLEAN produce-task (提出需求/表达目标)。U#0/U#1 为 setup（读目录/切换中文），U#2 为唯一需求轮。用户未指出根因或修复方案。符合 §A rule 1/2。

## Real Attachments (from session tool_results)
1. **DDR6TOP_Latch_FF_RS.list** (269 行): 库/单元清单，格式 "library cell"（如 dscqa_digital latrq2_ckUnit），# 开头注释
2. **netlist** (198MB): SPICE 网表，含 * Library / * Cell / .SUBCKT 块，端口含 clock/clock_N/data/RN/SN/R/S + power(vbn!/vbp!/vcc!/vss!) + cm*(cm0_ts_FsPgm 等)
3. **template** (78 行): 输出格式参考，CSV: subckt,refname,signame,data,RN,SN,R,S

## Assistant Gold (run_match.py, 5658 bytes)
真实 assistant 受 agent-policy 限制（run_commands 禁用、仅 hello_world profile），未能实跑脚本，但写出完整 run_match.py：
1. 解析 .list → get (library, cell) pairs
2. 逐行扫描 netlist → 匹配 * Library + * Cell + .SUBCKT
3. 过滤 power 端口 (vbn!/vbp!/vcc!/vss!/vcc2sc! + endswith('!'))
4. 过滤 cm* 端口 (re.match(r'^cm\d*_'))
5. 正则分类端口: CLOCK_PAT(Clk|Ck|CLK|Lat|READ+digits), CLOCK_N_PAT(+N suffix), DATA_PAT(D+digits), DATA_EXT_PAT(D|Din|DE|DO+digits), RN_PAT(RN|RstN|ResetN|...), R_PAT(R|RST|Reset|RESETB), SN_PAT(SN|SetN|Set_N), S_PAT(S|Set)
6. build_clock_pairs: clock 与 clock_N 配对 (c+'N' or c+'n')
7. gate 单元 (无 clock/data) → 填 R,S 列 (端口两两配对)
8. 输出: per match → * Library / * Cell / .SUBCKT line + CSV lines

session 末尾 assistant 创建 run_match.py 成功但无法执行（run_commands 被策略禁用），给出使用说明后结束。用户未明确接受/拒绝（status=idle）。

## Case Design (A档 faithful)
- **prompt**: U#2 逐字原文
- **A assets**: cell_list.list (20 cells 合成) + spice_netlist (20 SUBCKT 块合成) + template.csv (24 行)
- **B hidden**: B_list.list (18 cells 不同结构) + B_netlist (18 SUBCKT 块, 含 cm*/gate/dual-data/vcc2sc!) + B_template.csv
- **check.py**: 12 条件 a-l, 跑候选脚本 on B, 验证 zip/exit/output/FMT header/18 cells matched/power filter/cm filter/clock pairing/data classification/RN/SN/gate R,S
- **3 negatives**: fake_print_only (不写文件) / fake_hardcode (仅 2 cells 硬编码) / fake_no_filter (不过滤 power/cm 不分类)
- **§4.9 三假**: empty shell / print expected / hardcode → 全 FAIL ✓
- **ref self-test**: ALL PASS ✓
- **negative_selftest**: ALL FAIL ✓

## Key Insight
真实 gold 受策略锁死未实跑 → 改造为"通用 netlist 匹配+端口分类脚本"题。候选须实现完整解析链：.list 解析 + netlist Library/Cell/SUBCKT 匹配 + power/cm 过滤 + 8 类端口正则分类 + clock 配对 + gate 单元 R,S 填充 + CSV 输出。B 变体含 5-pair clock cell / dual-data cell / cm* ports / vcc2sc! power / gate cells，区分真解析器与硬编码 stub。
