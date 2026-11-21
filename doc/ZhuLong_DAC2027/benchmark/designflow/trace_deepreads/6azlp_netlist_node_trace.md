# trace_deepread: 1795076423732_6azlp (tongfanl@hfhds201, mc=55, schematic_netlist)

## 真实用户意图（逐字）
- **U#0**: `si.inp 166行，.param pvdias=0.9102 / vdbias vdbias! 0 dc=pvdias power=0 / 这个是怎么吃进primesim仿真的？影响了哪些电路？`
- **U#31**: `在nerlist中怎么看出来的？`
- **U#37**: `帮我看下该netlist中，R_Ref_tRASLock的heirachy`

## agent 真实做法（trace 上下文）
- 写 `trace_vdbias.py` 在 sim 目录扫 `vdbias` 引用 → `si.inp:167` 是唯一本地定义
- 展平后仿网表 `netlist` 文件有 **2193 处** `vdbias!` 引用
- **三招判断**（U#31 回答）：
  1. 同名节点=同电位（spice 本质）：`si.inp:167` 电源给 `vdbias!`，`netlistHeader:10` 列入全局节点表
  2. `vdbias!` 出现在 `.SUBCKT` 端口表末端（与 `vbn! vbp! vcc! vss!` 一串）→ 电源/偏置轨，靠继承供电
  3. 看实例化的器件端子连到哪个节点
- **R_Ref_tRASLock 层次**（U#37 回答，从 `netlist` 解析，带行号）：
  - `R_Ref_tRASLock` 定义 L30493–L30551，端口 6 信号 + 5 电源（vbn!/vbp!/vcc!/vdbias!/vss!）
  - 31× `R_buf_RasVdbiasDlySlow1111`（全部带 vdbias!，构成 tRASLock 延迟链）
  - 4× `bufLx2_org`、1× `bufLx4_org`、5× `mxi2Lx1_org`、2× `mx2Lx1_org`、9× `invLx2_org`、4× `nand2Lx1_org`（无 vdbias）
  - 下一层 `R_buf_RasVdbiasDlySlow1111` → 叶子 `R_RasVdbiasDlySlow_gut`（depth 3）

## 可验证结构核（synthesized-reframe 依据）
真实 NFS 网表 4GB+ 不可沙盒 → 合成 A/B/A' 三集 token 完全不相交的网表：
- **param/node 追踪**：`.param` 定义 → 电压源 `v<name> <node> 0 dc=<param>` → `.global` 全局节点 → `.SUBCKT` 端口表含 `<node>` 的子电路（偏置轨消费者）
- **hierarchy 解析**：`<top>` 体内 X 实例行（callee=行末 token）按 callee 分组计数 + carries_node + 递归 depth

## case 映射
- A (visible): pvdias/vdbias!/R_Ref_tRASLock_A（31× R_buf_RasVdbiasDlySlow_A + 4×bufLx2 + 5×mxi2Lx1 + 2×nand2Lx1，depth 3）
- hidden B: pvref/vref!/DlyChain_B（20× BufDly_B + 3× Inv2x_B + 6× Mux2_B，depth 3，total 29）
- hidden A' (anti-hardcode): pvbias_n/vbias_n!/AmpTree_Ap（12× GainStage_Ap + 2× Load_Ap + 4× BiasTap_Ap，depth 3，total 18，subckts_with_node=4）
- check k=14（9 B-side a-i + 5 A'-gold j-n），§4.9 三假全 FAIL，n_distinct=3

## trace 溯源
- user: tongfanl, host: hfhds201, session: 1795076423732_6azlp.messages.json, mc=55
- 取 trace 经 eda_flow MCP open_session + 本地 python3 解析（host=hfhds201=.75 本身，session 文件在 /home/tongfanl/.cline/data/sessions/1795076423732_6azlp/）
