# Deepread: 1791963948520_hk622 — rongtaoy / hfeg0plg99 / mc257

## Domain
schematic_netlist (SPF DSPF 寄生网表 vs 前仿 SPICE 网表 subckt 端口/层次对比)

## Trace 概况
- 266 msgs / 8 轮用户需求 / rongtaoy (DDR5 感测放大器模拟设计工程师) on hfeg0plg99
- agent 用 7 个 analyze*.py 脚本（python-runner profile）解析 50K+ 行 SPF + 网表
- 真实文件在 `/rundata/ddgoa/...rongtaoy/`（rongtaoy-owned，e0031982 无权读）→ 按公开事实合成 A 资产

## 首轮用户原话（A 档任务说明，msg[0]）
> 请读取以下两个文件，并做对比分析：文件1（SPF 源文件）msaq_U_CCR_fBcc_int.spf_CC；文件2（前仿网表）netlist。1.提取SPF所有.subckt定义+cell name+端口列表；2.提取网表中 msaq_U_CCR_fBcc_int_spf_o / _spf 的端口列表+层次深度；3.对比判断同名/端口一致/能否 .inc netlist + .inc spf 替换。

## 关键事实（agent 终局报告 msg[40]，用户接受）
- **SPF** `msaq_U_CCR_fBcc_int.spf_CC`：644706 行，**唯一 1 个 `.SUBCKT`**，**单行 DSPF 头**（无 `+` 续行），cell name=`msaq_U_CCR_fBcc_int`，**10377 端口**（Cslin<1119..0>...cn14blb<18..0>...vad2! vblh! vblhbk! vdd2h! vintlp! vss!）；body=520412 C 叶子 + 67078 X（`XI*.XRRI0 ... brknet R=0.001` 短接桥），**无 M/R 晶体管叶子**。
- **网表** `netlist`：
  - `msaq_U_CCR_fBcc_int_spf_o`（行 8092–17459）：**11867 端口**（**多行 `+` 续行**，BLafar<743..662>...Cslin...inh_vad2/inh_vblh/.../NCSR/PreEq_bUin_1）；body=9064 X（brknetBL 7488 / brknetM3A 1488 / brknetM2A 70 / brknetM2 10 / m0bla/m1bla/m3bla/cn04bla 各 1），**本级无直接 R/C/M**（非叶子包装层）；父级 `msaq_U_fBcc_O_spfsim` 的 `XI22`（行 21525）实例化。
  - `msaq_U_CCR_fBcc_int_spf`（行 21535–30902）：**11867 端口**，与 _spf_o **逐位完全相同**（identical_order=True）；body 结构与 _spf_o 完全相同；父级 `msaq_U_fBcc_E_spfsim` 的 `XI22`（行 31224）实例化。
- **对比结论**：
  - SPF cell name `msaq_U_CCR_fBcc_int` ≠ 网表 `_spf_o`/`_spf`（缺后缀）→ name_match=False
  - SPF 10377 ≠ 网表 11867 → port_count_match=False
  - 交集 10371；SPF 独有 6（vad2! vblh! vblhbk! vdd2h! vintlp! vss!）；网表独有 1496（BLafar 744 + BLbfar 744 + inh_* 6 + NCSR 1 + PreEq_bUin_1 1）
  - **不能**直接 `.inc netlist` + `.inc spf` 替换（需改名 + 扩端口 10377→11867 + 对齐顺序 + 电源轨改名 vad2!→inh_vad2）

## 用户纠正点（msg[31]，关键陷阱）
agent 首版只取 `.SUBCKT` 头**第一行** token 当完整端口表（漏 `+` 续行），把 _spf_o/_spf 端口数算成 82（实际 11867）；用户 msg[31]「_spf_o/_spf 你应该是只看了第一行内容，他的 net 远不止这些」。→ 参考解必须正确合并 `+` 续行；negative `no_continuation.py` 复现此 bug。

## 后续轮（msg[43]+，未用作 A 档任务说明——用户已给方案/对比指令）
- msg[43] 对比 sim_7sec_fbcc_spf.netlist vs _evan.netlist（先定位 XI 再比，结论：语义等价，仅书写顺序+注释头不同）
- msg[72] 概念问「替换模块只要名称不变 pin 不变内部无所谓？」→ 原则对，前提 name+port_count+port_order 三致
- msg[74] 对比 0608BK vs spf 网表
- msg[5–7] SPF 抽取报错排查（array*_fbcc_spf no reference ckt / Cannot find schematic view / spicesimspf 设置）

## 合成决策
- A 档 trace-faithful：任务说明 = msg[0] 逐字原文（提出需求轮，非给方案轮）。
- 真实 SPF/网表不可读 → 按 trace 公开事实合成 A 资产（端口数 10377/11867、命名族、body 元素构成、父级 XI22、_spf_o/_spf 端口逐位相同全用原值）；body 规模降采样（C 520412→1500、X 67078→250；网表 X 9064→292）以控文件体积，结构性质不变。
- hidden B：换名 msaq_V_DCR_fBcc_ext / 端口数 8421/9530 / 端口族 Dlin/BLafar→DLafar / X 子电路引用 brknetDL/brknetN4A/.../q*dlb → 杀硬编码。

## 交付
EDA-Eval-DesignFlow-SPFNetlistCompare-001（L2 schematic_netlist，track=faithful，harness=cline）
- 参考 `compare_spf_netlist_ref.py`（fold `+` 续行 + .SUBCKT/.ENDS 块解析 + body 元素分类 + 对比 name/count/order/set/intersection + can_replace）
- check.py 17 条件 a–q（ref PASS 17/17 · 4 negatives ALL-FAIL distinct{empty→d / print_expected→e / core_deleted→l / no_continuation→i} · §4.9 三假 a→d / b→e / c→l distinct）
- k_rationale = k_check = 17 ≥ 8 ✓
