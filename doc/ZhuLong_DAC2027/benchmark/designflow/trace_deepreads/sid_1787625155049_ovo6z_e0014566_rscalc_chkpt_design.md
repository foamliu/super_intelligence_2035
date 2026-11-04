# Trace Deep-read — sid 1787625155049_ovo6z (e0014566 @ hfeg0pkn001)

- **session**: 1787625155049_ovo6z.messages.json, 289 msgs, 1.7 MB
- **user**: e0014566, host hfeg0pkn001 (10.129.2.10)
- **mc**: 285; tools 356 virtuoso + 192 cellview + 171 dbGet + 37 skill(lang) + 4 calibre + 3 schematic + 2 spectre + 1 netlist
- **domain**: layout_virtuoso (Virtuoso SKILL 版图编辑 + RsCalc 电阻分析)
- **case**: EDA-Eval-DesignFlow-RsCalcChkPtGen-001 (B-档 synthesized, L1-boundary)

## 用户意图（逐字）

USER#1 (msg0, A-档 seed, 提出目标未给根因/修复):
> 先看一下配置参数 rscalc.config, 获取到 目标 layout. 我现在要用rscalc计算电阻，看看其 powernet 上的RTEXT，没有的话，帮忙在合适的位置上打上。既然不能修改原本的layout, 请先原风不动拷贝一份这个layout, 然后分析，然后打上RTEXT。另外，请在配置文件rscalc.config 中修改 checkPoints, 以计算这点的电阻。增加的量控制在50左右，分布要广泛典型。不用真正打上RNODE，直接用checkPoints 表示RNODE就可以了。用 skill virtuoso-rtext-checkpoint-designer

USER#2 (msg87): 开始计算电阻值吧。计算完了之后，出一个报告在。英文报告，不要有乱码。 → 后续给方向，不进 prompt
USER#3-6 (msg226/231/244/265): continue / cotinue → 无信息

## assistant 工具链

- read_files21 + run_commands74 + SandBox_MCP_Server__run_code37 + editor11 + search_codebase3 + skills1
- 读 rscalc.config + virtuoso-rtext-checkpoint-designer/SKILL.md(分段) + prompt.md + gen_rscalc_agent.py
- SKILL 探查 (msg19): dbOpenCellViewByType("auto_austin_case1" "Array16G_T" "layout" "" "r") → bBox, foreach shapes 数 RTEXT/RNODE(均 0), 列 instances
- 拷贝+打标 (msg75): procedure(AL(cv lay pur x y txt) dbCreateLabel(cv list(lay pur) x:y txt "centerCenter" "R0" "stick" 1.0)); dbCopyCellView(srcCv "auto_austin_case1" "Array16G_T_rscalc" "layout" t); 打 vcc!@(-17865.247,1468.5355)/vss!@(-17859.753,1468.5355) M4/RTEXT; dbSave/dbClose
- config 改 (msg79 editor): cellName→Array16G_T_rscalc, pwrNets→"vcc! vss!", checkPoints=list(... 50 点 vcc!/vss! × M3/M4/M5 × pad-region(4X×2Y)+far-field ...); 后续 useExistGds→Yes, gdsFile→Array16G_T_rscalc.gds
- 跑 rscalc: gen_rscalc_agent.py 生成 run_rscalc_agent.il; 多轮排错(hierarchy crash/geOpen crash/NFS lock/直接跑 runrsc Perl via bsub)
- 报告 (msg276-284 editor): RsCalc_Report_Array16G_T.md, 243 行 10 节, 纯 ASCII 无乱码

## 金标准（用户实际接受的结果）

- vcc!: 0.66h, 21.8M nodes, 0.006–24.19 Ohm; vss!: 4.89h, 42.4M nodes, 0.008–6.34 Ohm
- 50 checkPoints 中 24 个产出电阻值(12/net), M4/M5 同 X 电阻相近证 via stack 良好
- 交付: place RTEXT 于 power pad(2 个) + config 50 checkPoints(代表 RNODE) + 英文报告

## A-档 disqualified → B-档 synthesized

- gold 依赖 live Virtuoso + live RsCalc 引擎(RSCALC 8.2.1.1/Calibre) + live OA 库 auto_austin_case1/Array16G_T(2.95GB GDS, 8126 cells) → .75 沙盒不可达 → A-档 disqualified(tooling)
- B-档 synthesized L1-boundary: 纯离线 layout_manifest.json → 生成 place_rtext.il(SKILL) + rscalc.config + checkpoint_report.json

## 合成（与现有正交）

- 与 r87 PowerFillMergeGen(合并 dbCreateInst)/r93 SchWireRebuildGen(schCreateWire)/r92 GdsRectGen(GDS 坐标)正交——本案是 RsCalc 电阻 checkpoint 设计(拷贝+RTEXT+checkPoints 分布)
- gen_rtext_checkpoint_design.py(标准库, 确定性): pad-region 网格(padX 向 bBox 内侧偏移 × padRegionRows × 前置 metals) + far-field(X 跨 bBox 均匀, Y 三子行错开, 全 metals 轮转) + 覆盖率兜底
- check.py 15 条断言 a-o: zip+py_compile / 3 文件+报告键 / dbCopyCellView 到 _rscalc / 源 r+副本 a+原不改 / dbCreateLabel RTEXT 于 pad / dbSave+dbClose / config cellName_rscalc / pwrNets / checkPoints 数~target+可解析 / X&Y 跨度达标+在 bBox 内 / on-metal on-net / 无重复 / 报告计数一致 / 3×md5 确定 / B2 坐标≠B+B3 优雅失败
- 自验: ref PASS 15/15; 4 neg(空壳→b / RTEXT 错位→e / 缺 dbCopyCellView→c / 时间抖动→n)全 FAIL NEG_RC=0; §4.9(a)(b)(c)全 FAIL; test==disk roundtrip PASS
