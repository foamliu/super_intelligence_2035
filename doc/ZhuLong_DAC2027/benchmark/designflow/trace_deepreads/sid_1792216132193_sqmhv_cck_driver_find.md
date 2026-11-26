# cck driver-find (chengk sqmhv) — shard C 轮(41) 深读笔记

## trace
- session: `1792216132193_sqmhv` (chengk @ hfeg0pgn022, mc=213, model deepseek-v4-flash, cwd /home/chengk/work/ZL_work/cck_skill, status=completed)
- 415 msgs / 25 user_input / 191 tool_uses (agent=lead)
- tools: 1095 netlist + 47 hspice + 45 dbGet + 31 schematic + 5 spectre (cck connectivity-check netlist traversal)

## 用户意图（A-档 seed 评估）
- UI@0: `# Skill 写作指南（Meta-Skill）` — meta-skill 创作引导（非设计需求）
- UI@32: `继续完成以上任务` — 续 meta-skill
- UI@115-134: cckExplore/cckGetNodeName 报错调试（用户给报错 + 想让 cckExplore 遍历所有 node）
- **UI@136（逐字）**：`现在有如下需求，输入为一个电路中inst的层次结构，对应cck的fullpath，希望脚本首先能够定位到这个inst，其次获得他的输入和输出端口，最后从输入端口连接的net找到这个inst输入的net连接的驱动inst端口和位置，首先拆解需求，构造实例，查看api，给出完整思路,最后直接输出代码实例` = **纯需求委托轮，无根因/无修复/无追问 ⇒ 合规 A-档 seed**
- UI@155: `英文注释`（refine）
- UI@185-304: 多轮 driverFind.tcl 迭代（用户给报错/输出，要求修正逻辑/提高性能/对比网表）
- UI@377: `解释怎么判断端口是输入还是输出，以及怎么找输入端口的驱动`（追问解释，非新需求）
- UI@378-379: `review这个skill设计...迭代得到精确的api信息...`（skill review，重复两次，**非接受**）

## assistant 工具链
- list_allowed_files/get_agent_policy_status（探查 cck_skill 目录）
- run_commands（ls/find/htm 列举 cck doc）
- run_approved_command（shell-runner / python-runner 跑 inspect.py/build_kb.py/listdocs.py/scan_constants.py）
- editor 42 次写 `driverFind.tcl`（@142-372，从 tests/t20_port_driver.tcl 迁到 task3_src/driverFind.tcl，bug-laden 迭代：cckGetNodeName handler 错/instance not found/extra characters after close-brace/CCK_VSRC no such variable/...）
- read_files 读 API_INDEX.csv / cck API txt / demo tcl

## gold 评估
- 末版 driverFind.tcl（@372，1786B）= 仅 ClassifyPort + ParentOf 两 proc 片段（partial edit，非完整文件）
- 42 次 partial edit，无 byte-faithful 完整终版；trace 末轮 UI@378-379 仍 "review skill" = **无用户接受 ⇒ A-档 disqualified**
- cck API 需 live calibre/customsim netlist（L2 fragile，沙盒不可复现）
- → **B-档 synthesized**：按 cck API 面（cckSearchNode/cckGetNodeName/cckExplore/cckSearchInst -adj/cckGetInstFullName）+ UI@136 设计请求，合成自包含 Python SPICE 网表遍历器

## 合成 gold = cck_driver_find.py（自包含 Python3 + re + argparse）
1. `parse_netlist`（两遍）：pass1 收集 .subckt 名，pass2 解析 inst 行；x 前缀二义消歧（trailing token ∈ subckts → sub；否则 4 net + model → mos），支持 m/r/c/v 叶器件 + x sub-inst，case-insensitive subckt 查询
2. `find_inst_by_fullpath`：dotted fullpath 逐级下钻，返回 (inst, subckt, port_net_map)
3. `_port_driven_internally`：递归检测 subckt 内是否有 mos drain / sub-inst output port 驱动该 net
4. `classify_ports`：sub-inst 端口（内部驱动→output，rail 名→rail，否则→input）；leaf 器件按固定端子方向（mos drain=output/gate=input/source=bidir/bulk=input）
5. `find_input_drivers`：在 parent scope 找 sibling（mos output 端子或 sub-inst output port 接到该 net）+ parent_port（net 是 parent subckt 的 port 名 → 由 grandparent 驱动）
6. `run` + `format_report` + `main` CLI（--netlist/--inst/--out）

## A/B 网表
- **A（visible）**：BUF 链（INV(2 mos) → BUF(2 INV) → xbuf1），target=xbuf1.xi1 → in=input(parent_port)/out=output/vdd,vss=rail；xbuf1.xi2 → in=input(sibling xi1@out)
- **B（hidden）**：NAND3（3 nmos 堆 + 3 pmos）+ INV + NAND3_TOP → xtop.xnand/xinv，target=xtop.xinv（sibling xnand@y）+ xtop.xnand（a/b/c=parent_port, y=output）

## check.py（16 条独立断言，k=16=k_check≥8）
(a)zip 含 cck_driver_find.py (b)≥800B (c)UTF-8 无 NUL + py_compile (d)import re+argparse (e)CLI --netlist/--inst/--out (f)≥3 核心函数 (g)B xtop.xinv exit0 (h)报告头 Target type=sub (i)in net=ybar direction=input (j)out net=z direction=output (k)vdd+vss rail (l)driver xnand@xtop.xnand port=y sibling (m)xtop.xnand exit0+a/b/c=input+y=output (n)≥3 parent_port (o)cross-input guard 无 A token (p)确定性 3x 一致

## 自验
- ref PASS 16/16（reference_submit.zip → check.py exit 0）
- 4 neg FAIL：empty_stub / always_print / no_driver_logic（删 driver 查找）/ hardcoded_A（只认 xbuf1.xi1）
- negative_selftest.py OK
- 本地纯 Python3 验证（case 无 .75/sandbox 依赖）

## 与既有区别
- DRConnTiming/DRCTimeStats/DRCKDeckOpt/DRCSFCompare/FreezeMaker/VTTFLayerMap（calibre rule/log 文本解析）→ 本案 cck 网表实例层次遍历 + 端口方向分类 + 驱动 inst 定位（拓扑遍历，非文本/规则解析），主题独立
- L1-boundary（offline Python SPICE 解析，判分机无需 live cck/calibre）
