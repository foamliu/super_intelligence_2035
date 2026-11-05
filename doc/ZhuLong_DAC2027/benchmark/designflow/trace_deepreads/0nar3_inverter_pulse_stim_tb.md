# trace_deepread: 0nar3 — inverter pulse stimulus testbench

- **session**: `1790143934595_0nar3.messages.json` (qifanli @ 10.129.8.233, mc=41, n=36 msgs)
- **domain**: schematic_netlist
- **shard**: D
- **case_id**: EDA-Eval-DesignFlow-InvPulseStimTb-001

## 用户轮（逐字）

- **U#0 (msg0)** — 粘贴 Cadence SPICE 网表片段（带行号）：
  ```
  .subckt switch_close POS NEG
  r0 POS NEG r=0.001
  .ends switch_close
  .subckt switch_open POS NEG
  .ends switch_open
  .GLOBAL vcc! vss!
  * Library : ldo_qifanli
  * Cell    : inv_20260922
  * View    : schematic
  **TopDesStart
  XMMN0 OUT IN vss! vss! ntn w=150e-9 l=36e-9 nf=1
  XMMP0 OUT IN vcc! vcc! ptn w=150e-9 l=36e-9 nf=1
  **TopDesEnd
  ```
- **U#1 (msg4)** — ★A-faithful 任务说明（逐字）：
  > add 1v pulse signal to the above inverter, pulse width 1us,period 2us,and transient simulation time 10us

  纯提需求，未给根因/修复 → A-faithful 合规。

## assistant 工具链

1. list_allowed_files / search_codebase 探索 /home/qifanli/simulation/.../sim_inv（找到既有 sim_inv testbench：V0 val0=0 val1=1.1 period=1u width=500n，tran 10u — 与目标不同 cell）。
2. **editor** 创建 `inv_20260922_tb.scs`（Spectre 语法）：`simulator lang=spectre` + 把反相器包成 `subckt inv_20260922 OUT IN`（含两 MOS 实例）+ `global 0 vss! vcc!` + `VCC vsource dc=1.0` / `VSS vsource dc=0` + **`VIN (in vss!) vsource type=pulse val0=0 val1=1.0 delay=100n rise=10n fall=10n width=1u period=2u`** + `XI0 (out in) inv_20260922` + `CLOAD capacitor c=10f` + **`tran tran stop=10u`**。
3. 因 `/home/qifanli/simulation/...` 不可写，改写至 `/home/qifanli/.cline/scripts/data/inv_20260922_tb.scs`（同内容）。
4. 另建 `run_inv_20260922.scs` 包装器（include testbench + simulatorOptions + PDK model 占位）。

## 金标准（trace 末尾用户接受的结果）

testbench 网表（Spectre/SPICE）：反相器包成 subckt（保留 MOS 实例/型号/尺寸）+ 全局电源直流源 + **1V 脉冲源（width=1us, period=2us）驱动输入端口** + DUT 实例化 + **.tran stop=10us**。

## 合成（B-grade synthesized）

真实 /rundata /proj 网表 permission-denied 不可附加 → B-grade 合成。资产 A = 清理后的 inverter 网表（去行号前缀，保留真实 cell 名 inv_20260922 / 尺寸 / 全局 / switch 子电路）。金标泛化为 `gen_tb_ref.py`：CLI `<netlist>` → 解析 `* Cell :` 取 cell 名 + `.GLOBAL` 取全局 + `**TopDesStart/End` 块取 MOS 实例 → 输出 SPICE testbench（subckt <cell> <out> <in> + 全局直流源 + `VIN <in> 0 pulse(0 1.0 100n 10n 10n 1u 2u)` + `XI0 <out> <in> <cell>` + `.tran 1n 10u`）。out=共享 drain(pos1)，in=共享 gate(pos2)。

## 隐藏 B / B2（反硬编码）

- **B** `netlist_B.sp`：inv_20261015，端口 Y A，全局 vdd! gnd!，尺寸 w=200e-9 l=40e-9 nf=2（无 aux subckt）。
- **B2** `netlist_B2.sp`：inv_20260901，端口 Z B，全局 vcc! vss!，尺寸 w=180e-9 l=36e-9 nf=1（+ cap_load aux subckt）— cross-input guard。

## check.py 14 条件 a-n

a zip+无禁 import/path · b py_compile · c B exit0+非空 · d B subckt(inv_20261015)+MOS/型号/尺寸/端口 · e 脉冲 val1=1.0V · f width=1us · g period=2us · h tran stop=10us · i DUT(inv_20261015 含 Y/A)+VIN 接 A · j B 全局(vdd!/gnd!)直流源 · k 反硬编码 A(无 inv_20260922/OUT/IN) · l 跨输入 B2(cell/端口/全局+脉冲+tran+输出≠B) · m sys.argv 通用 CLI · n 3 重跑 sha256 一致。

## 自验

ref submit.zip PASS 14/14(abcdefghijklmn)；6 negative(empty→c/print_a→d,k,l/no_stimulus→e,f,g/wrong_tran→h/static_b→l/ref_core_deleted→d,i)全 FAIL NEG_SELFTEST PASS distinct{c,d,e,h,l}=5；§4.9 三假(empty→c/static_b→l/ref_core_deleted→d)全 FAIL distinct{c,l,d}=3；k_rationale=k_check=14≥8 GATE PASS；test==disk sha 2e8826d63690 MATCH；D.jsonl 136→137。

## 教训

(1) **Cadence SPICE 网表 TopDes 块 = 顶层设计（非 .subckt）**，反相器端口 = 共享 drain(pos1, OUT)/gate(pos2, IN)，电源网 = source/body(pos3,4, vcc!/vss!)，是 schematic_netlist L1 可验好范式：包成 subckt + 加脉冲 + tran。
(2) **check 时间解析须跳过注释行**：`* ... tran stop=10us` 注释会触发 Spectre regex 误匹配 → _find_tran_stop 须 `startswith("*")` continue + unit 捕获 `[0-9.]+[a-z]*`。
(3) **全局网名带 `!` 致 `\b` 失效**：`vdd!\b` 在 "!" 后无 word boundary → 供电源 regex 须用 `v\S+\s+<global>(?=\s|$)`（实例名也带 ! 须 \S+ 非 \w+）。
(4) **反硬编码双轴**：(i) B 全换 cell/端口/全局/尺寸/aux + (ii) B2 同全局但不同 cell/端口/尺寸 → print_a(硬编 A)被 (d)/(k) 拦，static_b(硬编 B)被 (l) B2 拦。
(5) **A-faithful prompt = U#1 逐字**，资产 = U#0 粘贴网表（"the above inverter"），SUT 须从 prompt+task_brief 推断 CLI 接口（gen_tb.py <netlist> → stdout testbench）。
