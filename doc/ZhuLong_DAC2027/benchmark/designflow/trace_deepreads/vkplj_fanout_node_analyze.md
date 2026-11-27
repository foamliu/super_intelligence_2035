# trace_deepread: 1795505250070_vkplj — CMOS inter-module fanout analyzer

- **user/host**: cyrusrao @ hfhds201 (= .75 本地, trace 直读无 ssh 摩擦)
- **session**: 1795505250070_vkplj.messages.json (1.9MB, 374 msgs)
- **match_count**: 532 (aether:1719 / pyaether:904 / cmos:685 / netlist:463 / schematic:834 / transistor:166)
- **domain**: schematic_netlist (D)
- **claimed**: r1630 (2026-11-28)
- **case**: EDA-Eval-DesignFlow-FanoutNodeAnalyze-001 (LIVE-NA, judge_layers=[L0,L1])

## 真实用户意图
cyrusrao 要计算 CMOS 层级电路 `DRGOA_SaCtrol` (lib `/proj/drgoa/V0/libs/drgoa_cmos_work`) 中**每一个模块间连接节点**的前级输出驱动与后级 loading 的**上拉(PMOS)/下拉(NMOS) fanout**，依据是节点前后级所连 MOS 管的 W/L 尺寸（× multiplier）。输出须含：节点名、前级驱动模块名、后级 loading 模块名、上下拉 fanout 数值。

## 助手做法
写 `fanout_analyzer.py`（pyAether）：
1. 开顶层 schematic，遍历 sub-module 实例
2. 对每个实例开其子电路 schematic，分析 I/O pin：input pin(MOS 栅极) vs output pin(MOS D/S)
3. 对每个模块间 net：driver 实例输出 pin → load 实例输入 pin
   - driver_pmos_W / driver_nmos_W = 子电路里 D/S 接到 driver pin 的 PMOS/NMOS W*mult 之和（驱动强度；nand2 串联 NMOS 只有直连 out 的那只计入）
   - load_pmos_W / load_nmos_W = 子电路里 gate 接到 load pin 的 PMOS/NMOS W*mult 之和（栅极负载）
4. pull_up_fanout = load_pmos_W/driver_pmos_W；pull_down_fanout = load_nmos_W/driver_nmos_W
5. 输出 report.txt + CSV（net/driver_inst.cell.pin/load_inst.cell.pin/pu/pd/total_fanout）+ HIGH-FANOUT ALERT(>4 排序) + Net Connection Map(auto-named net 定位)
- MOS cell 集：ptk/ntk/ptn/ntn 等；POWER_NETS 排除 vss!/vdd! 等

## 后段（不合成）
trace 后 ~1/3 陷于「如何在用户 terminal 跑 pyAether」环境排障：LD_LIBRARY_PATH 缺 Aether 平台库 / Python 3.9 vs 系统 3.7 PyQt5 冲突 / Aether GUI 初始化 ABRT —— 与 fanout 主任务无关，不进 case。

## case 合成（synthesized-reframe）
把真实电路抽象成结构化 spec JSON（cells[pins+mosfets{type,w,l,mult,g,d,s,b}]/instances[inst,cell,pins]/nets[net,driver{inst,pin},loads]），reframe 为通用「fanout 分析器 `fanout_analyzer.py <spec> <report>` + hidden-B 反硬编码」。
- **A**(visible) spec_A.json：AmpChain，cells=inv/nand2/nor2/buf/nmos_cap/inv_small/nmos_inv，6 net 8 entry，含 multi-load(n2/n3)、load 仅 NMOS 栅(n4 pu=0)、driver 无 PMOS(n6 pu=None)、high-fanout(n5 pu=8>4)。
- **hidden B**(token-structurally 不同) spec_B.json：SenseAmpCtrl，cells=INVx/ND2x/NR2x/BFx/NCAPx/INVxs/NMOSDRVx，inst=U1..U10，net=m1..m7，**W/L 比值不同 → fanout 数值不同**(m1=2.0 vs n1=1.333；m5=5.0/6.25 vs n5=8.0/8.0) → A 硬编码器(名字/数值)在 B 全错。
- **reference** `fanout_analyzer_ref.py` spec 驱动通用实现（_pin_w driver=d|s==pin / load=g==pin → 累加 W*mult；pu=pd=None 处理；total=None 处理）。
- **check.py 15 conds(a-o)**：判分器**独立复算**(_recompute 单独代码路径)逐 entry 比对(±1e-6)：a zip+py ②b compile ③c A run exit0 ④d A 非空+14字段 ⑤e n1 driver/load cell/pin ⑥f n1 pu/pd 匹配复算 ⑦g n2 multi-load 2条匹配 ⑧h n4 load仅NMOS pu=0.0 ⑨i n6 driver无PMOS pu=None+total=None ⑩j n5 high-fanout>4 ⑪k B run合法 ⑫l B m1匹配复算(反硬编码) ⑬m B m5匹配复算 ⑭n B m4/m7 边界 ⑮o 源码无 A 专属 token。
- **LIVE-NA**(deliverable=Python 分析器, check 跑候选+独立复算断言, 无真实 EDA 工具二进制依赖；pyAether/Aether 不在 eval 沙盒不强求 L2.live) judge_layers=[L0,L1] 无 check_live。

## 自验
- ref check.py → PASS (direct judge check(ref)=True + negative_selftest REF PASS)
- negative_selftest 4 neg ALL-FAIL distinct{a,f,d,l}：empty→a / print_expected(const 1.0)→f / core_deleted(empty report)→d / hardcode_a(A report on B)→l；§4.9 trio{a,f,d} distinct ✓
- SKIP_RUN=1 deploy workdir clean (no check.py/reference/hidden leak) ✓
- sha 3-way sync: disk check.py == JSON test field == metadata.check_sha256 = 689dcc1759b17f56ae2b4cefb36874f1393ff08d1b72f430ec27ccda7592ecdc (size 13722)
- k_check=15=k_rationale=15 ✓
- D jsonl auto-build 598 case 含本条 ✓
- 台账 mark: 1795505250070_vkplj → case(EDA-Eval-DesignFlow-FanoutNodeAnalyze-001)
