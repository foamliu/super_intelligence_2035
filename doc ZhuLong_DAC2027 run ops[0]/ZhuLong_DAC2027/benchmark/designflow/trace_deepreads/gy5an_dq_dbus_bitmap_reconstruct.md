# Deepread: gy5an — DQ↔Dbus Bit Mapping Reconstruction

**Session**: 1794976771694_gy5an  
**User**: my7li @ hfeg0pkn002 (10.129.2.11)  
**MC**: 291 (netlist:829/schematic:185/analog:108/virtuoso:98/dbopencellviewbytype:56)  
**Msgs**: 327  
**Domain**: schematic_netlist (D)  
**Date**: 2026-11-19  

## User Intent Chain (20 user_input msgs)

- **U1**: 既然连接到了iejoal，我们继续迭代知识库，增强ai自主迁移到新项目时的准确性和泛化能力
- **U43**: 检查当前的知识条目，除了像是22ull，ip, gut这样的通用字段，能覆盖多少module的解释：1.分词 2.命中 3.拼接对应知识 4.核对静态知识和关系检查的推论 5.对模块做出合理的解释
- **U84**: 既然已经连接到了工程，eda工具能暴露出比单纯网表多很多的信息...有哪写能进一步挖掘的信息, 并且跑通和virtuoso里获取来的信息的校验
- **U153** *(key falsifiable)*: 因为在dqtool中，dq bus mapping是提供bitmap后, 人工提示, 调整成符合预期的映射，现在我需要你使用工具本身的查询trace功能，还原出各个节点的映射，将其总结成项目迁移时改动点
- **U190** *(key falsifiable)*: 那么现在列举出每一步的映射规则和对应的电路节点要附上查询脚本的log
- **U206**: abus你没追踪到吗，虽然我们桥接的是iejoal，但是dram die的网表在工具本地是有的
- **U226**: 你是如何保存注意力经验的，因为迁移到新项目后，命名和架构都可能发生很大变化
- **U256**: 名字能反映设计意图，因为整个电路是手工搭的，这是跨项目迁移最大的依据
- **U262**: 工具即将发布测试版，需要增加一个方便用户操作的知识标注功能入口
- **U288**: 开始实现

## Assistant's Key Work (U153-U210)

### DQ↔Dbus Bit Mapping Auto-Reconstruction

The assistant wrote `_dq_bitmap.py` to auto-reconstruct DQ↔Dbus bit-level mapping
from netlist evidence using dqtool's `TraceData.nets.drivers/loads` + `inst_cell` API.

**Mapping rule discovered**:
```
DbusEv/Od[ pad×4 + beat×48 + {0..3} ]
  pad = 0..11, beat = 0..5, Ev == Od (symmetric)
  MIL pads (4,5,10,11): only 16 pins (skip beat 2 and beat 5)
  Normal pads: 24 pins (6 beats × 4 bits)
```

**Bridge cells found**: `DbusPrcInDQByteM6_22ull`, `DbusM2PitDQ_22ull`, `DbusPrcInDQByteM3_22ull`

**Step-by-step datapath** (U190):
- STEP1: DQ Pad → Dbus (logic_netlist, host=DQSC_22ull)
- STEP2: Dbus → DPSC (bridge DbusPrcInDPSC_22ull)
- Cross-die: DbusM2PitDQ bridges logic → dram netlist
- STEP3: Lbus (dram_netlist, LbusRWctrl)
- STEP4: Yio (YioPrcTopL/R, YioSaCtrl, YioWrRdCtrl)
- STEP5: SA (msaq_top/bot_E/O)
- Missing: Abus (U206 — user pointed out, assistant added)

## Case Synthesis (r985)

**Reframe**: produce-parser — synthesized Verilog netlist → bit mapping reconstruction

**A (visible)**: DQSC_22ull netlist, 12 pads (8 normal + 4 MIL), DbusEv/Od[279:0]
- pad_stride=4, beat_stride=48, bits_per_beat=4, normal_beats=6, MIL skips beat 2&5

**B (hidden)**: DQS_CORE netlist, 8 pads (6 normal + 2 MIL), DataE/O[91:0]
- pad_stride=3, beat_stride=24, bits_per_beat=2, normal_beats=4, MIL skips beat 1&3
- All names different, all parameters different → anti-hardcode

**Reference**: Pure Python Verilog parser (regex-based module/instance extraction,
bus port detection, pin→bit mapping, beat grouping by gap detection, stride computation)

**Check.py**: 14 assertions (a-n), k_check=k_rationale=14
- a-c: zip structure + compile + schema
- d-i: A parameter verification (n_pads, pad_stride, beat_stride, bits_per_beat, mil_pads, pin mapping)
- j-m: B parameter verification (all different from A)
- n: anti-hardcode (B output has zero A-only tokens)

**Self-verify**: ref 14/14 PASS + 3 negatives all FAIL + 3-seed determinism identical md5
