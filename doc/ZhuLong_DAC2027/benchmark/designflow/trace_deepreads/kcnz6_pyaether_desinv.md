# trace_deepread: kcnz6 — pyAether 打通 + Aether 设计结构查询

- session: `1795070909054_kcnz6` (目录 `1795070909054_kcnz6/`)
- user: hao37w  host: hfeg0pkn001 (10.129.2.10)  mc=153 (scan 20261119/20)
- domain: schematic_netlist / waveform / analog_context（D 域）
- 68 msgs (39 user / 29 assistant), 489KB messages.json
- agent: lead

## 8 个 user turn（真实意图流）

1. (i=0) 咨询 SimVision 相关有哪些 skill 可用 → 列 aether-tool-qa / waveview-fsdb-readerV2-2 / finesim-fsdb-reader / search_apis（Q&A）
2. (i=2) 问 simvision 问题是不是用 ask_eda 更好 → 对比 aether-tool-qa（手册+群问答+bindkey）vs ask-eda（Dify RAG），建议前者首选后者兜底（Q&A）
3. (i=4) **aether 如何与 simvision 连动** → 加载 aether-tool-qa skill，写 `grep_refs.py` 跨 14 个 Part 手册 + 群问答库 + bindkey 速查表检索（修了 `|` 转义 bug），结论：Aether 原生联动 iWave/waveview 非 SimVision，cross probe 机制 `Outputs→Select From Design` / ctrl+w（Q&A + flow）
4. (i=27) 继续任务
5. (i=29) **Schematic view 里 block 输入信号，什么快捷键跳到驱动信号** → 检索 bindkey 表 + 手册 Ch15.1 Trace Net，结论：无单一 go-to-driver 键，方法一 `alt+1` 悬停高亮 / 方法二 `9` Trace Net + Zoom To（Q&A）
6. (i=40) **block 输入连线 MRR0<7:0> 但端口只写 MRR0，block 内部看不出多 bit，仿真却对，为什么** → 检索 FAQ Q8 + Ch11.6/11.8 bus 语法 + Ch14.10 Navigator，结论：base name 归一（MRR0 与 MRR0<7:0> 同命名空间），位宽是 pin/net 属性非 label 文字，网表按 bus range 展开（Q&A，关键机制）
7. (i=47) 有个 schematic 看不懂，怎么让你看到 → 4 种喂图方式：截图放工作目录 / 抽网表文本 / pyAether 脚本直读 / 纯文字（Q&A）
8. (i=51) **我们来打通 pyAether 的用法** → 加载 eda_agent/pyaether skill，`run_code` 桥接到 live Aether GUI，`aeGetCurDesign()` 读到 `drcpa_io/IO_DcaAdjVdd0_Tsac/schematic`（只读），枚举 cv 214 属性，跑通实例枚举（修 `inst.master.name`→`cellName` bug），列出 20 instance（PIN0/1/3/4 io、MN0/1/2/6 ntn_lv、I0/1/2/8 vcc）/ 12 net / 4 terminal，**彩蛋印证 turn 6**：net 表里同时有 `ptrim<2:0>` bus + `ptrim<0>/<1>/<2>` bit member，terminal 定义为 3-bit bus input（flow-driving + 真实执行 + 交付脚本）

## 可离线判分内核抽取

turn 8 的真实交付 = pyAether 脚本读 live 设计 → 产出结构化设计清单（instance+master、net、terminal+方向、bus+bit member）。pyAether 桥接依赖 live Aether GUI 无法离线判分，但**纯 Python 内核**可抽：解析 SPICE subckt 网表 → 同构清单（与 turn 6 的 bus/base-name 机制直接对应）。

内核 `schem_desinv.py`：
- 解析 `.SUBCKT Name ports... .ENDS` → terminal 名（检测 `<h:l>` bus）
- 解析 `* .terminal name direction [range]` 注释指令 → terminal 方向（input/output/inout）+ bus range
- 解析 `Xname nodes... master [params]` → instance(type=subckt)
- 解析 `Mname d g s b model [params]` → instance(type=mosfet)
- nets = ports ∪ 所有 instance 连接节点
- bus 检测：`name<h:l>` / `name<n>` → base + bit members 展开
- 输出 JSON：cell / instances[{name,master,type,nodes}] / nets / terminals[{name,direction,is_bus,base,bit_members}] / bus_nets{base:[members]} / summary{n_inst,n_inst_subckt,n_inst_mosfet,n_net,n_terminal,n_bus}

## 三网表结构性不相交（A vs B1 vs B2）

| | cell | terminal | bus | inst 前缀 | master |
|---|---|---|---|---|---|
| A(visible) | IO_DcaAdjVdd0_Tsac | ptrim<2:0> in / vdd in / out out / gnd inout | ptrim→[<0>,<1>,<2>] | PIN*/MN*/I* | io_drv/ntn_lv/vcc_clamp |
| B1(hidden) | IO_DcaAdjVdd1_Ppump | ctrl<3:0> in / avdd in / avss inout / pad inout / fb out | ctrl→[<0>..<3>] | DRV*/MP*/MN7/IC* | io_pmpdrv/ptm_hv/nhv_lv/ivc_clamp |
| B2(hidden) | AnaClkBuf_TrimSel | clkin in / sel<1:0> in / clkout out / vcca in / vssa inout | sel→[<0>,<1>] | INV*/MP*/MN*/BC* | inv_a/pmos_a/nmos_a/bkf_clamp |

模块/实例/net/master/信号名全不相交（MN7 vs MN0/MN1/MN2/MN6 全名不交）。

## 与近期 D case 内核不相交

r1209 SigHierTraceProduce（Verilog module 端口方向+实例连接层次追踪）/ r1208 AsyncRiskResetWaiveGen（门级网表引脚-信号+复位过滤+waive）/ r1206 FifoStructNetlistGen（FIFO 结构网表生成）/ r1205 SxCmdRefClassify（SX 命令分类）。本 case = SPICE subckt 网表解析→设计清单（instance/net/terminal/bus），解析对象/输出结构/正则体系全不同。
