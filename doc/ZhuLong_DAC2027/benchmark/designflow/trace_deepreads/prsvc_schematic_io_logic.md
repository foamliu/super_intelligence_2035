# prsvc deepread — schematic I/O 静态逻辑关系推导 (analog IP cell)

- **trace**: `1795056204141_prsvc` · chuanqiz @ hfeg0pnd001 (10.129.32.189) · mc=80
- **kw**: virtuoso:278 / schematic:154 / analog:84 / cellview:70 / cadence:16 / netlist:13
- **size**: 305KB / 97 msgs / 6 real user turns (U#1 是 virtuoso-cli command-instructions 系统注入, 非真用户任务)
- **date**: 2026-11-20 r865 fresh deepread
- **domain 裁决**: **D 域** (schematic_netlist/analog_context), 非 C 域。virtuoso:278 keyword 误 bin 入 C 池。按 P-005 裁决2 软优先级 schematic→D / analog_context→D。C 不造不 claim，让渡 D。

## 用户真实意图 (4 真 user 轮)

- U#2 (msg#36): 「读取analogIP library下的CustomDlyNcCtrlIP」
- U#3 (msg#58): 「能否给出输入和输出的逻辑关系？」
- U#4 (msg#70): 「忽略内部信号，能否给出输入和输出的逻辑关系？」
- U#5 (msg#72): 「忽略内部信号，CustomDlyPulse200nsVbnVbpCtrlBIP这个cell能否给出输入和输出的逻辑关系？」
- U#6 (msg#92): 「忽略内部信号，ustomDlyRdColPlsGenIP这个cell能否给出输入和输出的逻辑关系？」(笔误少 C)

**意图归纳**: 读 analogIP library 的 CustomDly* 模拟 IP cell **schematic**，推导**顶层输入→输出静态逻辑关系**（忽略内部信号/RC 延迟网络），产出端口表 + 每个输出的静态布尔函数 + 真值表 + 哪些输入仅作延时配置（不动静态逻辑）。

## 助手 gold 链

virtuoso-cli Python API (eda.general / eda.schematic) 读 cellview:
1. `list_libraries` → 确认 analogIP
2. `get_cell_info(lib, cell, view)` → terminals (name, direction, width)
3. `list_instances(lib, cell, view)` → 143 instances (name, master_cell, pin→net)
4. connectivity (net→pin mapping) → 信号通路追踪
5. 人工推导: 从 input port 经 instance 链(inv/nand2/nor2/buf)到 output port，逐门传播布尔函数，**吸收律化简**，识别 delay-only inputs

### gold 答案形态 (以 CustomDlyNcCtrlIP 为例)

```
端口表:
  In         input  1
  Out        output 1
  OutN       output 1
  cm1_ro_NcDly<4:0>  input(仅延迟配置) 5

静态逻辑函数 (忽略内部信号):
  Out  = In          (同相缓冲)
  OutN = ¬In         (反相输出)
  二者恒互补 OutN = ¬Out

真值表:
  In | Out | OutN
  0  | 0   | 1
  1  | 1   | 0

delay-only inputs:
  cm1_ro_NcDly<4:0>  仅配置 RC 延时级数, 不改变稳态逻辑值

推导链 (evidence):
  In → I5(inv) → I13(inv) → InBuf  (两级反相, 净同相)
  InBuf → I1(inv) → I28.B
  Dly200nsCap → I28.A
  I28 = nor2  → net5 = ¬(Dly200nsCap ∨ In)
  net5 → I2(inv) → net05
  I10 = nand2 → OutN = ¬(In ∧ net05)
  I9 = inv → Out = ¬OutN
  化简: OutN = ¬(In ∧ (Dly200nsCap ∨ In)) = ¬In (吸收律)
```

## reframe 可行性 (若 D 域造)

档 B fixture-driven **schematic I/O static-logic-derivation analyzer**:
- **fixture**: mock cell library tree, 每 cell = JSON {views, terminals(name/direction/width), instances(name/master/pin→net), gate_library(inv/nand2/nor2/buf...定义布尔函数)}
- **candidate**: `analyze_io_logic.py <lib_root> <cell_name> [-o out.json]` 解析 cell 结构, 沿 instance 链从 input 传播布尔函数到 output, 化简, 分类 delay-only inputs, 输出 JSON {ports, outputs:[{name,function,simplified,depends_on,derivation_chain}], delay_only_inputs, truth_table}
- **check.py**: 隐藏 fixture B (不同 cell/instance/net), 验证 per-output 函数 + 端口方向 + delay-only 分类 + 真值表 + derivation evidence (citing real B instances/nets, anti-hardcode)
- **k_check ≥ 8**: 端口数/方向/每输出函数/化简/delay-only 分类/真值表行/evidence 引用/anti-stub

**P-006 (C) triage**: 用户要"答案"(逻辑关系) 非"工具", 但 reframe 成 analyzer 后 §4.2 subprocess-on-B + §4.9 anti-hardcode 可满足 (B 不同 cell, 硬编 A 答案 FAIL)。属 (C)-(A) v2 可造类(evidence-verify: derivation chain 引用 fixture B 真实 instance/net)。**但 domain = D**, C 让渡。

## 让渡结论

- C 不 mark parked (免占 D 候选)
- D 可直接 claim `1795056204141_prsvc` (chuanqiz@hfeg0pnd001, mc=80)
- prsvc axis-2 = pure-text-stdlib (low) 补强 D r863 axis-2 case-level 论 (virtuoso keyword ≠ axis-2 high)
