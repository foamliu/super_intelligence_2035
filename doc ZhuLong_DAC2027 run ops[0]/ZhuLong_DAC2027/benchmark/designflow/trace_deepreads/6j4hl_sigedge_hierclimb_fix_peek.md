# 6j4hl peek — signal-edge-tracer hierarchy-climb fix (schematic_netlist)

**session**: 1789555682011_6j4hl.messages.json · **user**: pjli · **host**: hfeg0plg06 (10.129.8.227) · **mc**: 109
**keywords** (col5): `netlist:391;schematic:89;cmos:80;verilog:24;cadence:9;analog:1` → D-pure (netlist+schematic+cmos dominant, no drc/lvs/aether/hspice)
**fetched**: eda_flow open_session(shardD-20261119-r925) + ssh 10.129.8.227 scp 1108575B messages.json (105 msgs, 58 user / 47 assistant, agent=lead)

## 用户意图 (A-faithful 选轮 U#0)

U#0 (msg 0) `<user_input mode="act">`：用户在 `/home/pjli/Desktop/DFFLatchSR` 跑 `RunTrace`，贴出 trace-back 输出。target 信号 `top.Chip.I_PRAC_Performance_TB_0.I_RH_DLUT_FULL_PRAC_new_0.I_DLUT_CONTROL_PRAC_0.I_DLUT_PRAC_RHR_POINTER_LOCK_0.DLUT_ALL_OPEN` edge#1 (falling) @ 18677924262ps。trace 到 `[1] DRIVER ... driver: I300(nor3x1) out_pin .Y; input .A <- source edge: ...net24 edge#` 就**截断**（"no stdcell driver"）。

**意图**（assistant U#1 thinking 复述）：RunTrace 在信号连到**当前模块的输入 pin**时停下，应当**继续向上钻 hierarchy** 找真正的 stdcell 驱动。用户贴 failing output = 提出需求（符 A 档选轮规则①「提出需求」；非「给出根因/修复」）。

## assistant 诊断 + 修复

read: `signal_edge_tracer.py`（import trace_signal_fixed as ts）、`TraceSignal/trace_signal.py`、`TraceSignal/trace_signal_fixed.py`、`rhr_netlist.sv`(119 modules, root PRAC_Performance_TB_shell)、`find_edge_time.py`、`signal_edge_trace_STopen0.log.json`。

**根因**：`TraceSignal/trace_signal_fixed.py` 里 `lift_net_up()` + `resolve_net_hierarchy()` 在把"当前模块输入 pin 端口信号"上钻到父模块时，遇到父实例用 **concatenation** `{ST_OPEN[5],...,ST_OPEN[0]}` 整总线连接该端口，`is_simple_net()` regex 只认简单 net，不认 concatenation → port→parent 映射失败 → "no stdcell driver" 提前停。

**Fix #1** (A#46/A#50/A#54)：改 `is_simple_net()` 接受 concatenation；改 `lift_net_up`/`resolve_net_hierarchy` 的 `while cur_net in ports` 循环 + 新增 `_net_base`/`_bit_suffix` helper 处理总线 concatenation 端口上钻。

**Fix #2** (A#92/A#102)：Fix#1 后 trace 上钻到 `RH_DLUT_FULL_PRAC_new.ST_OPEN[0]` 又停（非端口而是内部线，由**非 stdcell 子模块实例**驱动，`find_stdcell_drivers()` 不会向下钻非 stdcell 实例 + bit-index 丢失）。Fix：增强 `find_stdcell_drivers()` 向下钻入非 stdcell 子模块，沿 concatenation 跟踪 bit-index。

**最终** (U#103/U#104 重跑 RunTrace)：trace 正确上钻输入端口 + 下钻非 stdcell 实例，产出完整 driver chain。

## buildable 判定

✅ **真实 trace**：pjli@hfeg0plg06, session 1789555682011_6j4hl, mc109
ℹ️ **revival（非 fresh）**：D ledger 2026-11-06 park「mid-conv: user pastes RunTrace trace-back; not a clean U#0 produce-task proposal」。r925 复核推翻：U#0 实为 msg 0（session 首条 user turn，`<user_input mode="act">`），非 mid-conv。提出需求 pattern（贴 failing output 要求修复 tracer）= A 档选轮规则①，承 r922 ArgparseWaveviewFixQA-001 precedent（user 贴 argparse error → A-faithful debug-Q&A→produce reframe，2026-11-06 park 早于该 precedent 确立）。`mark --force --status revival`。
✅ **D-domain**：schematic_netlist（Verilog netlist 解析 + hierarchy 信号沿溯源 + stdcell driver chain）
✅ **A-faithful U#0 选轮合规**：用户贴 failing output（提出需求），非给根因/修复
✅ **k≥8 有牙 check 可写**：candidate=fixed `trace_signal_fixed.py`；check.py 在 hidden B（合成小 Verilog netlist，含 input-port-concatenation + 非 stdcell 子实例结构）subprocess 跑 candidate，断言：① trace 上钻输入端口（hierarchy level 增加）② 下钻非 stdcell 子实例 ③ driver chain cell 类型/pin 名/edge# 正确 ④ 不在 "no stdcell driver" 提前停 ⑤ 输出 JSON 结构 ⑥ 反硬编码 hidden-B-only token ⑦...≥8 独立可 FAIL
✅ **资产 synthesized-reframe**：/home/pjli/Desktop/DFFLatchSR 仅 pjli 可读 → 合成重建（从 trace 提取 rhr_netlist.sv 结构签名 + trace_signal_fixed.py fix 逻辑），hidden B 平行场景（不同 module/net/instance 名 + 不同 concatenation 结构 + 不同 bit-index，反硬编码）

## 拟造 r926

- **case_id**: EDA-Eval-DesignFlow-SigEdgeHierClimbFix-001
- **domain**: schematic_netlist
- **grade**: A (trace-faithful)
- **l1_subgrade**: L1-realrun-python
- **asset_fidelity**: synthesized-reframe
- **k**: ≥10
- **资产 A**: 合成精简 `rhr_netlist_A.sv`（含 DLUT_PRAC_RHR_POINTER_LOCK 模块 + ST_OPEN bus concatenation input port + 非 stdcell 子实例驱动 ST_OPEN[0]）+ `simvision_A.vcd`（含 DLUT_ALL_OPEN falling edge + net24 rising edge）+ buggy `trace_signal_fixed_buggy.py`（原始 is_simple_net/lift_net_up/find_stdcell_drivers，触发 "no stdcell driver" 提前停）
- **hidden B**: 合成平行 `rhr_netlist_B.sv`（不同顶层 TopLatchSR_HierClimb + 不同 bus port RDQ_BUSY[7:0] concatenation + 不同非 stdcell 子实例名，反硬编码 A-only token{DLUT_ALL_OPEN,ST_OPEN,PRAC_RHR_POINTER_LOCK,RH_DLUT_FULL_PRAC_new,DLUT_CONTROL_PRAC,net24,I300,nor3x1}）+ `simvision_B.vcd` + hidden_manifest.json
- **candidate_ref.py**: 修复版 trace_signal_fixed（is_simple_net 接受 concat + lift_net_up/resolve_net_hierarchy 处理 bus concat port + find_stdcell_drivers 下钻非 stdcell + bit-index 跟踪）→ 输出 driver chain JSON
- **check.py**: ≥10 断言（zip+cand.py 编译 / A trace 上钻输入端口 / A 下钻非 stdcell / A driver chain cell+pin+edge / A 不提前停 / B subprocess / B 反硬编码 0 A-only token / B driver chain B-only 名 / 输出 JSON 结构 / hierarchy depth ≥ N）

## 0-case 合规

peek-only per established 2-round pattern (r921/r922, r923/r924)。synth ~35-45min（合成 Verilog netlist + VCD + fix + check.py subprocess）超 r925 剩余预算 → 拆 peek+synth 两轮，r926 synth。
