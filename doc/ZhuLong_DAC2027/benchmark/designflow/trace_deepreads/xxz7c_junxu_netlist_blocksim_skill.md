# Deepread: xxz7c (junxu, netlist/finesim block-sim skill 构建)

**trace_source**:
- user: junxu
- host: hfeg0pkn005 (10.129.2.14) [also replicated on hfeg0pjn200/hfeg0plg79/hfeg0plg17]
- session_file: 1789041210705_xxz7c.messages.json
- session_dir: /home/junxu/.cline/data/sessions/1789041210705_xxz7c/  (文件名 = `<dirname>.messages.json`，非裸 `messages.json` —— r1105 误判路径即此)
- match_count: 1465 (netlist:1625;virtuoso:1374;hspice:1025;schematic:915;cmos:203;cellview:123;verilog:57;cadence:45;drc:41;spectre:39;analog:33;synopsys:30;...). D-pure (netlist 主导).
- meta: 507 msgs, 2026-09-10→09-14 (4d), status=failed (external_process_exit), model=glm-5.2, cwd=/home/junxu/.cline/skills/block-sim, provider=cxmt-glm52
- real_task_summary: 用户带 agent 走一遍 finesim block 仿真人工流程（fifo_3x8 电路，Virtuoso ADE 抽网表 / CXMT DSIM Block），目标转换成可复用 cline skill（参考 wayfinder skill）

## 对话弧（msg#0–#506 全段；中段 #89–#496 于 r1107 补读）

**真实用户文本消息全集**（type=text，剔 tool_result）：
- #0 `/brainstorming` 构建通过 finesim 做 block 仿真的 skill，流程复杂需配多参数，当前人工流程有可复用脚本，想先带 agent 走一遍流程再转 skill，参考 wayfinder
- #9 拿 fifo_3x8 为例；通常在 virtuoso 里 ADE 抽网表=CXMT Extract Netlist 自定义 skill 函数（名不详）；先探索 virtuoso CXMT 菜单→Spice Simulation 子菜单→DSIM Block（wizard，涵盖 block 仿真全部配置项）
- #98 「DSIM Block 没法复用了是吗？还是得从 ADE 入手？」
- #110 「先把网表抽出来，做成 python 接口做进 virtuoso-cli 这个 skill」← **核心意图拐点**
- #213 有弹窗可能阻塞；/proj/iejoad/V0/workdir/junxu/simulation 之前跑过很多 block 仿真可参考
- #242 弹窗标题「check and save cellviews」
- #362 能再试一下吗
- #438 simInitEnv() 是 virtuoso 自带的吗
- #442 你没法自己打开 ADE 吗
- #448 再试一下 skill 能不能直接打开 ADE
- #473 我手动打开了 ADE，你再试试
- #478 你能检查一下 CXMT Extract Netlist 是怎么实现的吗？应该是用脚本提取的网表
- #489 刚刚 virtuoso 卡死重启了，这个菜单不在 CXMT 里，在 ADE 的 Simulation 菜单里

**agent 中段行为**（#89–#496）：读 DSIM block Qt 二进制 + config（project_speed_pvt.cfg / dsim_block_guide.pdf pdftotext）/ old/bin/dsimblock 文本脚本 → 结论 DSIM Block 是 GUI 不可脚本复用 → 转 ADE 路线 → 试 hnlRunNetlister / simInitEnvWithArgs / hnlSetOutputVars（多为 nil 或超时）/ 读 .simrc.cdl / si.env / input.ckt / 既有 fifo_3x8 simdir → 用户手开 ADE 后 asiCreateSession/asiNetlist/asiCreateNetlist 变可用 → #502 尝试 asiCreateSession→set design/simulator→asiCreateNetlist → session failed (external_process_exit) 终结。**全程无干净可运行交付脚本**。

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

**结论**：xxz7c 是真实 D-pure 高 mc 候选，意图合法（flow-driving / skill-authoring / netlist-extraction 接口化），但 4 天探索无干净交付。

### reframe 决策（r1107 补读后定）

**选定 = 候选 B（L1，netlist/sim config 校验归一化）+ 候选 C（L1，netlist-extraction API routing map）二选一，倾向 C**：

- **候选 A（L2，netlist 抽取编排脚本 asiCreateSession→asiCreateNetlist）弃用**：需 live Virtuoso + CXMT + 手开 ADE 才能让 asi 函数可用（trace 本身就因 virtuoso 卡死 / ADE 弹窗阻塞 / asi 函数 nil 反复失败），hidden B 构造需 live 环境，L2 重且复现性差，与 trace「failed 探索」属性冲突。
- **候选 C（L1，netlist-extraction API routing map）首选**：trace 里 agent 实际探索出的 API 路由序列是真实素材——意图「抽网表做 python 接口」→ 路由 `asiCreateSession(design) → set simulator(hspiceD) → asiCreateNetlist → 输出 netlist 文件`，前置=ADE session 已开/simulator 已选，后置=netlist 文件产出+SUBCKT/端口校验；同 r1099 manual-map 范式。checkable：hidden B = 异 cellview/异 simulator 意图集，offline Python，SUT 不可见 A'。**与 trace 真实意图（netlist-extraction 接口化）最贴合**。
- **候选 B（L1，DSIM block config 校验归一化）备选**：trace #84-#96 agent 读 project_speed_pvt.cfg / dsim_block_guide.pdf / old/bin/dsimblock，可作真实素材；但 DSIM Block 用户最终弃用（#98），config 校验偏离核心意图（netlist 抽取），优先级低于 C。

**合成 ETA**：下轮（r1108）按候选 C 合成——assets = virtuoso-cli skill 源片段 + ADE API 参考语料（从 trace agent 读过的真实文件取材，scp 到 workdir 后脱路径敏感），hidden B = 异意图集，check.py k≥8 + A' 交叉 + 3 neg + §4.9 三假。

## DEBT
- ~~补读 xxz7c 中段 msg#89–#496~~ ✅ r1107 完成（见上「真实用户文本消息全集」+「agent 中段行为」）
- ~~选定 reframe 候选~~ ✅ r1107 定 = 候选 C（netlist-extraction API routing map，L1，r1099 范式）
- **r1108 合成候选 C case**：assets 取材（virtuoso-cli skill 源 + ADE API 参考，scp 到 workdir 脱路径）+ hidden B（异意图集）+ check.py k≥8 + A' 交叉 + 3 neg + §4.9 三假 + pi 实跑 + 追加 D.jsonl
- 路径解锁增益：cline session 文件 = `<session_dir>/<dirname>.messages.json`（非裸 messages.json）—— 后续所有 trace 读取按此定位
