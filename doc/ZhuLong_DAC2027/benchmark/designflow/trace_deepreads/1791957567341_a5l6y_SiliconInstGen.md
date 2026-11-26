# 深读笔记：1791957567341_a5l6y（SiliconSmart .inst 生成）

## trace meta
- session: 1791957567341_a5l6y.messages.json (1.34MB / 292 msgs)
- user: chaor / host: hfeg0pgn145 (10.129.35.244)
- match_count: 207 · keywords: netlist:1094; .cdl:157; cellview:51; transistor:50; schematic:43; pyaether:40
- domain: eda_other（SiliconSmart characterization 流程 inst 文件生成）/ cell 属 dscqa_digital
- ssh from .75 (e0031982@hfhds201) → 10.129.35.244 免密 OK；scp 不带 user（用 e0031982 身份读 /home/chaor）
- session 结构：dict{version,updated_at,agent,sessionId,messages[list 292],system_prompt}；msg={id,role,content[list of blocks: text/thinking/tool_use/tool_result],ts}

## 会话主线
dscqa 项目 SiliconSmart 表征流程：用户 chaor 给 cell 的 SPF/CDL 网表，要求按 golden .inst 格式写 SiliconSmart inst 文件（表征配置）。

## 关键用户轮（A-faithful 选料）
- [0] "你现在是桥接在dscqa项目吗" — 上下文问
- [4] "描述下 dscqa_digital库里 R_RasVdbiasDly_LowSigma_0110 的功能" — 描述功能（提需求✓但偏查询）
- [22] "你能解析spf文件吗" — 能力问
- [56] "根据这个spf解析功能" — 解析 SPF 描述功能（提需求✓）
- **[89] 主任务（A 档选料）**："这个是cell的spf，需要根据这个写inst文件，inst文件是siliconsmart的格式，可以参考这些golden的写法，路径在.../GOLDEN" — 干净提需求轮 ✓（写 inst from spf，siliconsmart 格式，ref golden；用户未给根因/修复方案，规则②不命中）
- [117] "直接打印inst" — 跟进指令
- [119] "把 IO_CACSSetHld_CS/IO_CSBufDcc/IO_RocPumpOscUnitVcc 的 inst 写完，放到 control 下" — 批量任务（提需求✓）
- [152] "你不要单纯只参考golden的文件，主要看 netlists 里面对应的spf或者cdl文件" — 方法指导（边界，非根因）
- [184] "IO_CSBufDcc 的逻辑还要包括 En 不然没有上拉" — **用户给修复（缺 En）→ 规则②🚫**
- [192] "需要写 inst，spf 在 netlists 下" — 批量任务（4 digital cells）
- [247] "Vpwr...去掉 power_meas_supplies 中的，add pin" — **用户给修复 → 规则②🚫**
- [263] "Lat4ckUnit_Prac 中还得有别的限制，同一时间只能有一个 clk 能是 en 状态" — **用户给约束/修复 → 规则②🚫**
- [273]/[276]/[284] fix 指令

→ 选 [89] 作 A 档 task 说明（verbatim 逐字）。

## 金标准 = trace [118] 助手产出的 Lat4ckUnit_Prac.inst（用户接受，会话继续基于它）
[118] 全文 inst（真实产物，逐字）：
- power_meas_supplies { vbp vcc } / grounds { vbn vss }
- set_netlist_file [get_location]/netlists/Lat4ckUnit_Prac.cdl.spf
- 15 端口：CkPre Clk<0:3> ClkN<0:3> D0 D1 D2 D3 Q RN；Q=-output，余 -input
- set_subckt_ports { CkPre Clk<3> Clk<2> Clk<1> Clk<0> ClkN<3> ClkN<2> ClkN<1> ClkN<0> D0 D1 D2 D3 Q RN }
- 4 对 add_switching_set { Clk<i> ClkN<i> } + add_forbidden_state { !(Clk<i>^ClkN<i>) }
- add_latch IQ IQN CkPre (Clk<0>&D0)|(Clk<1>&D1)|(Clk<2>&D2)|(Clk<3>&D3) -clear !RN
- add_function Q IQ
- config: create_parameter cut_netlist / set_config_opt -opcond __default__ -- cut_netlist Lat4ckUnit_Prac.cdl.spf / state_partitions 系列

## 助手关键洞见（[112]/[116]/[158]）
- 结构部分（端口/电源/引脚方向/差分时钟对/配置项）从 SPF 可**确定性**提取
- add_latch 布尔方程是**推断**（SPF 是寄生网表，能定拓扑/引脚/互补对/反相次数，但不能唯一推 4 相选通时刻与复位极性）→ check 不断言精确方程，只断言 add_latch 存在 + -clear !RN + data 引用 D/Clk
- [158] IO_CSBufDcc 初版 Out=In（buffer，照搬 golden）错，重读 netlist 发现 Out=!In（inverter）→ 印证"必须以 netlist 实际为准，不能只抄 golden"（本 case 的真实难度核心）

## 资产策略（同 DeadLoopScan/PDKRunsetExplore 先例：fixture 合成，金标真实）
- 真实 /rundata/dscqa/... permission-denied（e0031982 guest 不可读 chaor 私有）→ 合成 SPF fixture 忠实复刻结构（trace+金标真实，fixture 复刻端口/电源/拓扑）
- A = prompt.txt（[89] 逐字）+ task_brief.md（3 行接口）+ Lat4ckUnit_Prac_A.spf（合成 SPF：15 端口 + .GLOBAL vbp vcc vbn vss + 实例 XI0-XI10 复刻逻辑链 + Q 由 XI7 驱动）+ golden/（4 个合成 golden inst 样本：latch/ff/inv/buffer 格式参考）
- hidden B = Bufx2_B.spf（不同结构：buffer 2 端口 In Out，.GLOBAL vcc vss，无时钟对，无 latch）+ gold Bufx2.inst（测泛化：生成器须对任意 SPF 通用，不得硬编码 A 的 15 端口/Clk 对/vbp 电源）
- 交付件 = gen_inst.py（CLI `python3 gen_inst.py <spf_file> <output_inst_file>`，纯 stdlib 解析 SPF → 生成 SiliconSmart inst）+ Lat4ckUnit_Prac.inst（A 输出）
- check.py：subprocess 在 A + hidden B 上跑 gen_inst.py（§4.2 L2 结构判分，不跑 SiliconSmart 二进制）；断言 inst 结构（端口/引脚方向/电源/switching_set/add_latch/add_function/config）+ 跨输入 B 泛化 + anti-hardcode

## 难度评估
L2（subprocess 在 A+B SPF fixture 上跑候选生成器，§4.2 结构判分）。A-faithful 真实难度 = 模型须从 verbatim prompt（"根据 spf 写 inst，siliconsmart 格式，ref golden"）推断：①解析 SPF .SUBCKT 提取端口清单 + 电源/地 net 分类；②识别输出端口（被实例驱动）；③识别互补差分对 Clk<i>/ClkN<i>（switching_set/forbidden_state）；④写 add_latch（推断方程 + -clear !RN）+ add_function；⑤配置项（cut_netlist/state_partitions）；⑥泛化到隐藏 B（buffer，无时钟对，不同电源，不得硬编码 A）。预期 ≤10% pass。
