# Deepread: 1795074487708_fuj9e — DRAM 网表 clock 源头追溯

- **session**: `1795074487708_fuj9e`
- **user**: wade1zh @ hfeg0plg76
- **mc**: 54 (netlist:141;cmos:84;verilog:38;analog:32;schematic:30;bandgap:1)
- **trace**: archive 1.66MB/26msgs(13u/13a) + active 269KB/6msgs = 87 msgs total (合并后 32 user-turns 含大量空 user 占位)
- **domain**: schematic_netlist (Verilog 门级网表分析)
- **FRESH**: 是（NEW user wade1zh，4-shard 台账无此 slug）

## 真实任务（两个子问题）

### U#0 (msg 0-25): 分析 DRAM 网表功能 + 列出 clock 及其来源
用户给了一份从 ATPG 流程导出的 LPDDR5 DRAM 门级 Verilog 网表路径
`/home/dfx/dev/cust2atpg/workdir/ddjob/atpg/rev0.4_wadez/tcl/tmp/netlist_verilog.atpg.out9_final.v`
（~30 万行），要求：分析功能、梳理有哪些 clock、源头在哪。

assistant 结论：
- 顶层 `ddjobhk20_top`（LP5TOP）= LPDDR5 DRAM die 设计
- **自定时（self-timed）设计**：顶层无显式 clock 输入端口
- clock/timing 相关信号分 7 类：
  1. `PhDecR/L/Up/Dn` 相位解码（主时基，源自片外 DQ/DQS 经 `Ras2XdecPrc`）
  2. `GrDec*` 全局行解码（地址总线 → `GrDecX*`/`XDec*`）
  3. `Yio*` 列解码（列地址 → `PhDecX4/X8`）
  4. `RdEn*`/`WrEn*` 读写使能（per-sector）
  5. `inh_*` 模拟电压就绪标志（vad2/vblh/vcc/vintlp/vkb/vwln/vwlp，gate array 操作直到电源稳定）
  6. 模拟电压生成（vad2/vblh/vintlp/viso/vcsl/vdbias/vwln/vwlp，片上 charge pump + regulator amp）
  7. 控制逻辑（`Ras2XdecPrc`/`XDecGprc`/`YsDecM4PrcUnit`/`CompRdUnitECC`/`ColAddrLat` 等 `ddjobhk20_digital` 库单元）
- 主时钟源 = 片外 LPDDR5 CK/DQS，经外部 PHY 处理后以地址/命令总线馈入核心 array

### U#1 (msg 27-86): "clock" 信号具体从哪个模块来？
assistant 沿实例化层次反向 trace 出 **5 级 clock 源头链**：

```
LEVEL 1: CK_t/CK_c Pads (片外 PHY)
   ↓
LEVEL 2: CaRcvCoreM5 (L1602852) — CA Bus Receiver
   入: CktPad/CkcPad/CA0Pad/CSPad → 出: CLKCAF/CLKCAR/CA0F/CA0R
   ↓
LEVEL 3: CsClkGen (L1601207) — Chip Select Clock Generator
   入: CLKCAF/CLKCAR/Cs → 出: ClkCAE/ClkCAO  (Cs 来自 CSPad，控制脚直连 pad)
   ↓
LEVEL 4: ClkFstGen (L1598917) — First Pulse Generator
   入: ClkCAE/ClkCAO → 出: ClkC/ClkT
   ↓
LEVEL 5: ClkGenM5 / ClkCmdGen (L1599256 / L1599352) ★ 主时钟生成
   入: ClkC/ClkT → 出: ClkCmd/ClkRd/ClkWr/ClkSync/ClkMskRd/...
```

数组侧（sense amp/wordline/bitline）不用 ClkGenM5 的时钟，自定时用 PhDec/GrDec/Yio/RdEn/WrEn（地址/命令总线跳变经 delay-matched path 传播，无常规时钟树）。

## case 设计（synthesized-reframe）

**真实任务** = 沿实例化层次反向追溯 clock 信号源头（哪个模块生成它 → 上游模块 → ... → pad）。
**reframe** = spec-JSON 驱动纯 Python 「Verilog 门级网表 clock 源头层次反向追溯器」
`trace_clock_source.py(spec)->report.json`，反向 BFS。

### spec schema
- `top` / `target_clock` / `pad_signals` / `modules{name:{ports:{in,out}}}`
- 顶层模块额外带 `instances[{inst,cell,pins{port:net}}]`（in/out 端口都连顶层 net）

### 反向 BFS 算法
1. 从 `target_clock` 出发，找哪个实例的 **output** 端口驱动了它 → 该实例 cell 入链（来源模块）
2. 把该实例**所有 input 端口**对应的 net 排序后入队继续追
3. net ∈ `pad_signals` → 记入 pad_sources，停止该分支
4. 同一 `(module, instance)` 只入链一次（去重）；已访问 net 不再处理（防环）
5. **只反向**：实例 input 端口连的 net 不会把该实例当来源（消费侧不进链）

### A (visible) spec_A.json — 镜像真实 DRAM trace
- top=ddjobhk20_top, target=ClkCmd, pads=[CktPad,CkcPad,CA0Pad,CSPad]
- 5 模块: CaRcvCoreM5/CsClkGen/ClkFstGen/ClkGenM5 + 干扰 DataLatch(消费 ClkCmd)
- 链: ClkGenM5→ClkFstGen→CsClkGen(pad 侧输入 CSPad 分支)→CaRcvCoreM5→PADS
- chain_depth=4, self_timed=True, DataLatch 不在链里(消费侧干扰)

### hidden B spec_B.json — token-structurally 不相交
- top=SerdesTop, target=TxClk, pads=[RefClkP,RefClkN,RstN,CfgPad,DataIn]
- 6 模块: RefClkRcv/PllCore/ClkDiv/TxClkGate/CtlReg + 干扰 RxLatch
- 链含**分支**(TxClkGate 2 上游: ClkDiv + CtlReg) + **交叉链接**(PllLock 馈 CtlReg 但 PllCore 已访问去重)
- chain_depth=5, pad_sources={RefClkP,RefClkN,RstN,CfgPad} ≠A

### check.py 16 conds (a-p), 独立 gold (list+integer-index BFS + dict-comprehension driver map + inline entry, 与 reference deque+popleft + setdefault + _entry_for 不同代码路径)
a zip含py ②b py_compile ③c A valid+确定性 ④d A origin ⑤e A source_modules有序 ⑥f A depth+self_timed ⑦g A pad_sources ⑧h A chain[0] driven/input ⑨i A chain[2] CsClkGen 含 CSPad 分支 ⑩j A DataLatch 排除 ⑪k B valid ⑫l B origin≠A ⑬m B source_modules+depth ⑭n B pad_sources≠A ⑮o malformed valid=False ⑯p anti-hardcode tokenize

### LIVE-NA judge[L0,L1]
deliverable=Python 追溯器, check 跑候选 subprocess + 独立 gold BFS 复算断言, 无真实 EDA 工具二进制依赖 (Verilog 网表 reframe 为结构化 spec->JSON 纯图算法判分)

### 自验
- REF PASS 16/16
- 6 neg ALL FAIL distinct first-fails {c,d,e,l,o,p} (§4.9 trio {empty→c, core_deleted→d, print_only→l} 3-distinct)
- 3-way sha sync (disk check.py == JSON test == test_sha256 = 93855dc9)
- D jsonl 633→634 含本条
- SKIP_RUN=1 框架接受 (workdir clean no-leak, infra_fail=0, hook_blocks=0, FAIL only from no submit.zip)
