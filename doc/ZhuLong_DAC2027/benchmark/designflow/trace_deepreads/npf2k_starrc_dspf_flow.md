# Deepread: npf2k — StarRC DSPF flow + SPF resistor-layer parser (pnr_signoff, L2, B档)

## trace
- session: `1792386615426_npf2k.messages.json`
- user/host: e0045488 @ hfeg0pkn002
- mc=103, 110 msgs, 602KB
- keywords: `synopsys:2076;netlist:764;schematic:21;calibre:15;techfile:14;hspice:13;primetime:12;cadence:11`
- tools histogram: `netlist:119; schematic:20; dbGet:4; pyAether:3; virtuoso:2; cellview:2; calibre:2`
- trace path (.75): `/home/e0045488/.cline/data/sessions/1792386615426_npf2k/1792386615426_npf2k.messages.json` (dir form, autofs intermittent)

## 用户意图（逐字原话）
- u#1/u#2: `starrc manual`
- u#3: `I want to work on dspf flow. Now I need to know some parameters or options to use StarRC. Here is the path of where starrc is installed: /apps/synopsys/SRB/star/. But the doc/ directory only contains "man". I don't know how to use it.`
- u#4: `I checked the user manual of starrc and know what options to use now. The result generated is here. Please tell me what does lvl (level) mean here. /proj/drexp/V0/ver/pex/e0045488/invBx2/lpe/invBx2/invBx2.spf`
- u#5: `ok. please tell me what layer each Resistor is on in this file.`

## assistant 工具链 / 产物
1. RAG_MCP_Server__search_apis (StarRC parasitic extraction) + list_allowed_files (/apps/synopsys/SRB/star) + search_codebase (DSPF/SPF/StarRC)
2. read_files StarRC man pages (/apps/synopsys/SRB/star/W-2024.09/doc/starrc/man/catn/EX/EX-113.n 等)
3. editor + run_approved_command: 多个 grep/find_dspf_man.py / find_dspf_opts.py / grep_dspf.py / grep_opts.py / grep_err.py / grep_err2.py 脚本扫描 StarRC 安装树找 DSPF 选项关键词
4. editor: `starrc_dspf.cmd` (StarRC 命令文件, 全注释模板, 含 NETLIST_FORMAT:SPF/CONNECTION:DEF/LAYER_MAP_FILE/NETLIST_FILE 等)
5. read_files `/proj/drexp/.../invBx2.spf` (tool_result 空 — 权限拒绝, owner e0045488)
6. editor + run_approved_command: `spf_layers.py` (.spf 电阻层解析器: 建 layer map `* idx NAME ITF=`, 遍历 `*|NET`, 解析 R 行 $lvl/$l/$w/$a, 按层汇总 + 每电阻明细)
7. editor + run_approved_command: `grep_geom.py` / `grep_geom2.py` (找 GEOMETRY/OUTPUT/LEVEL 关键词) + 多个 _rm.py/_clean.py 清理脚本

## 金标准评估（诚实）
- ✅ 完整 StarRC DSPF 命令文件骨架: starrc_dspf.cmd 含 NETLIST_FORMAT:SPF + ITF/CONNECTION/NETLIST/reduction/coupling 选项段
- ✅ spf_layers.py 解析逻辑正确: layer_idx map + *|NET 遍历 + R 行 $lvl/$l/$w/$a 属性 + 按层汇总 + 每电阻明细
- ❌ starrc_dspf.cmd 全注释(所有选项行以 * 开头, 非激活), 路径硬编码 `/home/e0045488/Desktop/...`
- ❌ cmd 含多个未经验证/错误关键词: `CONNECTION: DEF` / `DEF_FILE` / `LAYER_MAP_FILE` / `NETLIST_PARASITIC_RESISTOR_MODEL` / `NETLIST_INDUCTANCE` / `OUTPUT_FORMAT` / `OUTPUT_SPF_FILE` / `COUPLING_TO_GROUND` / `MAX_OPENS` — .75 StarXtract R-2020.09 实测均报 SX-0271 unknown keyword
- ❌ spf_layers.py 初版硬编码路径 `/proj/drexp/.../invBx2.spf` (后改 argv[1])
- ❌ /proj/drexp/.../invBx2.spf 权限拒绝(read_files tool_result 空) — 真实资产不可达

## case 合成决策
- 重构 design_flow: 给定 dspf_A(可见 DSPF 示例, M1/M2/M3/PO/NW 多层电阻), SUT 交付参数化 StarRC DSPF flow 5 文件
- L2 真跑 python3 parser on A/B/变异 + fake StarXtract on resolved cmd
- 隐藏 B = dspf_B.spf (异构层集 M4/M5/M6/CO/PO, netB_*, RBT*) 同格式同解析要求 → 交叉输入护栏击穿硬编码 A 层图的 parser
- feint = 残缺 cmd(硬编码 /home + 缺 DSPF 选项) + 残缺 parser(仅读 header + 硬编码单层)

## .75 infra 发现 (L2 真跑验证)
- StarRC: `module load star/2020.09-SP5-4` (default; `ds/star/2020.09-SP5-4` 亦可用)
- StarXtract: `/apps/synopsys/SRB/starrc_2020.09-SP5-4-20220823/bin/StarXtract` (命令文件用 `StarXtract <cmd>` positional; **非** `starrc_shell -clean -cmd_command_file` — 后者 SX-010 拒绝)
- StarRC 命令文件关键词验证: 逐一探测后保留 24 个真接受关键词(TCAD_GRD_FILE/TEMPERATURE_SENSITIVITY/OPERATING_TEMPERATURE/GDS_FILE/MAPPING_FILE/NETLIST_FILE/NETLIST_FORMAT:SPF/NETLIST_INSTANCE_SECTION/NETLIST_NODE_SECTION/NETLIST_GROUND_NODE_NAME/NETLIST_NODENAME_NETNAME/NETLIST_PRINT_CC_TWICE/NETLIST_CONNECT_OPENS/NETLIST_DELIMITER/NETLIST_MINCAP/NETLIST_TOTALCAP/NETLIST_MINRES/NETLIST_MINRES_HANDLING/NETLIST_REMOVE_DANGLING_BRANCHES/NETLIST_REMOVE_LOOPS/COUPLING_ABS/COUPLING_REL/COUPLING_REPORT_FILE/COUPLING_REPORT_NUMBER)
- 被拒关键词(SX-0271): CONNECTION, DEF_FILE, LAYER_MAP_FILE(正名 MAPPING_FILE), NETLIST_PARASITIC_RESISTOR_MODEL, NETLIST_INDUCTANCE, OUTPUT_FORMAT, OUTPUT_SPF_FILE, COUPLING_TO_GROUND, MAX_OPENS, OUTPUT_NET_CAPACITANCE
- .75 StarXtract on resolved ref cmd: SX-0271 count=0 (仅 SX-0967/0969 data-missing) → 语法 100% 合法
- .75 python3 3.7.1: parser on A(6 电阻)/B(7 电阻) PASS + 3x md5 一致(确定性)
- judge env 无真实 StarRC → check.py (m) 用 fake StarXtract fixture(同 njd2w StarRCFlow-001 模式)

## 区别于既有 StarRCFlow-001 (njd2w)
- njd2w: StarXtract multi-corner RC extraction (gxtr/run_gxtr_MULTI_CORNER.csh + extract_rc.py + extract_net_info.py)
- 本 case: StarRC DSPF 命令文件(starrc_dspf.cmd,NETLIST_FORMAT:SPF)+ SPF 电阻层解析器(spf_layers.py) — 完全不同交付物,不同 StarRC 命令文件关键词集
