# 深读笔记 — s98in (e0017906@hfeg0plg96, mc=106, schematic_netlist)

- session: `1794189255973_s98in.messages.json` (512KB, 57 msgs, 6 real user turns)
- 工具链：纯 pyAether（SandBox_MCP_Server__run_code）+ RAG_MCP_Server__search_apis/get_api_details + aether-tool-qa/eda_agent skills。无 calibre/virtuoso/waveview。
- 上下文：用户在 Aether 里 Edit-in-Place 到 `drcoa_io/IO_CABufCore/schematic`（DDR5 CA 输入缓冲器核心，层级深度 6：`I_Channel/I_BCenter/I_BCenterCA/I_CaPadTierBot/I_IO_CACSBuf/I_IO_CSBufCore`）。
- 真实意图（U#3，决定性需求轮）：「你完整描述到当前电路即可…标准是：只看你的描述，能还原出来电路」——即产出一份**可还原电路的结构化拓扑描述**。U#2 是细粒度拓扑提问（管子 D/G/S/B 连接、信号来源、栅极/源极归属），U#5 是对 assistant 描述的纠正核实（M11/M186 类型与四端接法、M183/M185 传输门、电阻阶梯拓扑）。
- assistant 做法（U#9–U#27）：用 `aeGetCellView`/`aeGetCurDesign`/`aeGetActiveDa`/`aeGetInstHierPath` 取层级链与 cellview；枚举 `cv.instances`（298）/`cv.nets`（206）/`cv.terms`（17 端口）；按 master 聚合实例计数（TECHLIB/RNPDIFF3t x70、TECHLIB/ntn_lv x64、stdcells_ac/invDSx1 等）；逐 net 反查 instTerms（INP→M18/G、INN→M17/G、net6→12 instTerms…）；逐管子四端 D/G/S/B→net（M11=ntn_lvio D=N3/G=N2/S=vss!/B=vss!，M186=ptn_lvio D=N3/G=N2/S=vddqca!/B=vddqca!，纠正了之前把 M186.S 误写成 vss! 的错误）；识别结构：CMOS 反相器（M11+M186 同栅 N2 同漏 N3）、交叉耦合对（M20/M21 栅-漏交叉）、switch 阵列（TECHLIB/switch 的 1/z 连接）、电阻串链（R49 RNPDIFF3t 阶梯）、电源域 fanout（vddqca! 142、vss! 295）。
- 金标准形态：一份结构化文本/表，含端口、实例集合、每管子 D/G/S/B→net、net 扇出、嵌套 subckt 实例化映射、结构识别（反相器/交叉耦合/电阻链/开关）。可还原 = 这些字段齐全且正确。
- 私有性：drcoa_io/IO_CABufCore 真实 cellview + drcoa_top 库不可复刻 → B-grade synthesized 自包含。
- 合成方向（B-grade）：可见 A=IO_CABufCore_A.cdl（差分对+交叉耦合+CMOS 反相器+电阻串链 4 tap+开关阵列 3+嵌套 switch_A/invDSx1_A）vs 隐藏 B=IO_RxCore_B.cdl（同构但名字/规模全不相交：端口 DQP/DQN/.../vddqrx!/vssrx!、管子 Mr1..Mr10/Mrm、net N21/N22/net8/Rs0..Rs3、电阻串 5 tap、开关 2、嵌套 switchRX_B/invRX_B）。SUT 交付 topo_extract.py 解析网表→topology.json（design/instances/mosfets/net_fanout/subckts）。check.py 13 条件 a-m 独立 oracle（split 手写 tokenizer，与 ref 的 compiled-regex 不同）验证重构保真度。
- 维度正交：既有 D schematic_netlist case 多为「诊断/lint/族配对/glob 解析/模块目录/指令配对/层级路径」；本 case=**完整拓扑重构提取**（器件集合 + D/G/S/B 端子映射 + net 扇出 + 嵌套 subckt + X 引脚映射，对账独立 oracle 实现重构保真），机制/产物全不同。
