# Deepread: xxz7c (junxu, netlist/finesim block-sim skill 构建)

**trace_source**:
- user: junxu
- host: hfeg0pkn005 (10.129.2.14) [also replicated on hfeg0pjn200/hfeg0plg79/hfeg0plg17]
- session_file: 1789041210705_xxz7c.messages.json
- session_dir: /home/junxu/.cline/data/sessions/1789041210705_xxz7c/  (文件名 = `<dirname>.messages.json`，非裸 `messages.json` —— r1105 误判路径即此)
- match_count: 1465 (netlist:1625;virtuoso:1374;hspice:1025;schematic:915;cmos:203;cellview:123;verilog:57;cadence:45;drc:41;spectre:39;analog:33;synopsys:30;...). D-pure (netlist 主导).
- meta: 507 msgs, 2026-09-10→09-14 (4d), status=failed (external_process_exit), model=glm-5.2, cwd=/home/junxu/.cline/skills/block-sim, provider=cxmt-glm52
- real_task_summary: 用户带 agent 走一遍 finesim block 仿真人工流程（fifo_3x8 电路，Virtuoso ADE 抽网表 / CXMT DSIM Block），目标转换成可复用 cline skill（参考 wayfinder skill）

## 对话弧（msg#0–#89 + #497–#506 末段；中段 ~#89–#496 待补读）

- #0 用户: /brainstorming 构建 finesim block 仿真 skill，参考 wayfinder，先走一遍流程再转 skill
- #1 agent: read wayfinder + block-sim 目录
- #8 agent: 任务分类=架构级（从零构建 skill，定义完整工作流+参数配置）
- #9 用户: 拿 fifo_3x8 为例，Virtuoso 里 ADE 抽网表 = CXMT Extract Netlist 自定义 skill 函数；先探索 virtuoso CXMT 菜单 Spice Simulation 子菜单 DSIM Block 相关 API
- #10-#20 agent: RAG search_apis 搜 "DSIM Block"/"CXMT"/"finesim" → 标准文档库无命中（自定义 skill 函数）。改文件系统搜
- #22-#29 agent: 找到现有 skill `virtuoso-cli`(Python API) + `block-design`(含 CXMT)。读 virtuoso-cli/SKILL.md + schematic.py(grep netlist/extract/sim) + general.py + ocean.py + netlistsimulateref.md + py-reference-schematic.md
- #38 agent: 发现环境 FINESIM_HOME=/apps/synopsys/SRB/finesim/V-2023.12-1，PATH 含 /proj/shdc/sim/bin
- #41 agent: Virtuoso 运行中 + bridge 已连 → 内省运行中 Virtuoso 菜单。/proj/shdc/sim/bin 有大量 finesim 脚本
- #44-#61 agent: 多次尝试 SKILL eval 内省菜单（shell 引号问题→改 Python via virtuoso-cli.sh eval；PYTHONHOME 污染→env -u PYTHONHOME/PYTHONPATH 用 /apps/local/python/python3.11.9）。确认 `innoCreateSchBndry` 存在（CXMT 函数已加载）
- #61-#82 agent: 搜 CXMT SKILL 源码 /proj/shdc/cad/skill/hi/CXMThiPullDownSch.il + CXMThiCIWBannerMenu.il → 菜单创建的是 "CXSH" 非 "Spice Simulation"。/proj/shdc/cad/script/bin/convertDesignReview.pl 引用 /apps/imctf/cad/script/Frontend/DSIM/
- #82-#88 agent: **关键发现** `/apps/imctf/cad/script/Frontend/DSIM/block/` = dsim_block Qt GUI 二进制 + config（支持 Finesim/Hspice/Nanospice/Primesim + 项目/队列配置）+ old/bin/dsimblock 文本脚本 + 用户指南 PDF + PVT 配置
- #89–#496 (中段，未细读): 继续探索，最终走到 ADE API 路线
- #498 agent: asiCreateSession/asiNetlist/asiRunSimulation/asiCreateNetlist 可用
- #502 agent: 尝试 asiCreateSession 创建 ADE session → set design+simulator → asiCreateNetlist
- #504-#506 用户: "好了吗"/"继续" —— session 终结 failed (external_process_exit)

## 交付评估

**无干净最终交付**：4 天探索会话，agent 始终在「发现 API/菜单/脚本」阶段，未产出可运行的 block-sim skill。session 以 failed 终结。真实交付=探索发现集合（API 名/菜单结构/脚本位置/配置路径），属 flow-exploration / skill-architecture brainstorming。

**可 checkable 子交付 reframe 候选**（按 r1092/r1088 范式：把探索/prose reframe 成脚本交付）：

- **候选 A（L2，重）**: 「给定运行中 Virtuoso session + 目标 cellview，产出网表抽取编排脚本（asiCreateSession→set design/simulator→asiCreateNetlist 序列）并校验抽取网表结构」。checkable：hidden cellview B 上跑脚本，断言网表文件产出+结构（SUBCKT 数/端口）。**缺点**：需 live Virtuoso + CXMT 环境，hidden B 构造重。
- **候选 B（L1，中）**: 「给定 DSIM block 配置文件集 + 仿真器选项，产出参数配置校验/归一化脚本：解析 config，校验仿真器名/PVT corner/队列设置，emit 归一化 JSON」。checkable：offline Python，hidden B = 异内容 config。**前提**：需读 /apps/imctf/cad/script/Frontend/DSIM/block/ 下真实 config 文件（中段未读）。
- **候选 C（L1，轻）**: 「给定 pyAether API 参考语料，识别网表抽取+仿真的正确 API 路由序列，产出结构化 routing map（意图→API→前置/后置）」。同 r1099 manual-map 范式。checkable：hidden B = 异意图集。

**结论**：xxz7c 是真实 D-pure 高 mc 候选，意图合法（flow-driving/skill-authoring），但 4 天探索无干净交付，需补读中段 ~400 msg 才能定 reframe 候选并取真实素材。本轮先记 DEBT，下轮补读中段后选 B/C reframe 合成。

## DEBT
- 补读 xxz7c 中段 msg#89–#496（聚焦：用户每轮具体指令 / agent 读到的 config 文件内容 / 任何产出的脚本片段）
- 选定 reframe 候选（B 或 C）后合成 case
- 路径解锁增益：cline session 文件 = `<session_dir>/<dirname>.messages.json`（非裸 messages.json）—— 后续所有 trace 读取按此定位
