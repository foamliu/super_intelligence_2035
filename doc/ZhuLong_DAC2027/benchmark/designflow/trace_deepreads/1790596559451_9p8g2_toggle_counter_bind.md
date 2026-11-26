# trace_deepread: 1790596559451_9p8g2 (clwang @ 10.129.2.14) — toggle_counter bind 生成

- sid: 1790596559451_9p8g2 · user: clwang · host: 10.129.2.14 · mc=31 · domain: schematic_netlist
- msgs.json: 3.4MB / ~110+ msgs / 多轮 user_input（多数为工具结果回显，真实用户输入轮 ≈ U#0, U#91）

## U#0（唯一 A-faithful produce，逐字原文）
> 输入件目录是/home/clwang/test；编写一个python脚本，通过bind的方式，对文件cellname中的cell的输入输出信号添加信号翻转计数，具体的cell定义在cell_define.sv文件中，自己定义一个统计信号翻转的module，把定义的moudle和bind代码放在一个文件,文件名叫toggle_counter.sv

判定：纯提需求（spec → 产物），用户未给根因/修复 → **A-faithful 合格**。
- U#91「修改了输入件，请重新执行」为细化指令（非 produce），用作 hint 不进 prompt。
- 无「用户已指出根因/给修复方案」的轮。

## 真实输入（attachments）
- `/home/clwang/test/cellname.sv`：每行一个 cell 名。trace 末尾接受版（U#93/U#104）= `invx1 / nand2Lx1 / oai21GFx3`（3 cells）。
- `/home/clwang/test/cell_define.sv`：真实 cell 库（8711 行，非 ANSI 风格 `module foo(A,B,Y,vcc,vss); input A,B; output Y; inout vcc,vss; … endmodule`），含 invx1/nand2Lx1/oai21GFx3 等数十个 cell。
  - invx1: input A; output Y; inout vcc/vbp/vss/vbn → 监测 A,Y
  - nand2Lx1: input A,B; output Y; inout … → 监测 A,B,Y
  - oai21GFx3: input A,B,C; output Y; inout vcc/vbp/vbn/vssz → 监测 A,B,C,Y

## agent 工具链 / 产物
- agent 受 policy-engine writableRoots 限制，逐块 editor 写 `/home/clwang/test/add_toggle_counter.py`（generator）+ `/home/clwang/test/toggle_counter.sv`（产物）。
- 多次 search_codebase 超时（30s），靠 read_file 分段读 cell_define.sv（按行号区间）。
- 最终接受产物 toggle_counter.sv（U#104 diff）格式：
  ```
  // Cells instrumented: invx1, nand2Lx1, oai21GFx3
  module toggle_counter_invx1 ( input A, input Y );
      logic [31:0] cnt_A; always @(A) cnt_A <= cnt_A + 32'd1;
      logic [31:0] cnt_Y; always @(Y) cnt_Y <= cnt_Y + 32'd1;
  endmodule
  bind invx1 toggle_counter_invx1 u_invx1 (.A(A), .Y(Y));
  …
  ```
  - 每 cell 一个 `toggle_counter_<cell>` module，input/output 端口都作为 counter 的 `input` 监测，inout/电源轨排除；32-bit 计数器；`bind` 语句连每个信号。

## 金标准
- 用户实际接受 = 上述 toggle_counter.sv（U#104）。有 user-accepted 产物 → **A-faithful 可用真实金标**；但真实 /home/clwang/test 不可附加 → **B-grade synthesized**（assets 用真实 cell_define 子集 + 真实 cellname，hidden B/B2 合成不同 cells/端口/总线，prompt 仍用 U#0 逐字，track=faithful 诚实标记）。

## 合成要点（见 case EDA-Eval-DesignFlow-ToggleCounterBindGen-001）
- asset A: cell_define.sv（真实 7-module 子集含 3 targets + 4 distractors）+ cellname.sv(invx1,nand2Lx1,oai21GFx3) + prompt(U#0 逐字) + task_brief(交付接口 ≤3 行)。
- hidden B: cell_define_B.sv(bufx1/nand3Px1/oai22x/mux2busx，含总线 [3:0] + 电源 vdd/gnd) + cellname_B.sv。
- hidden B2: cell_define_B2.sv(invxZ/and2x/nor2Qx) + cellname_B2.sv(含 notexistX 缺失 cell 测优雅跳过)。
- 反硬编码三轴：A/B/B2 cell 名完全不相交；B 含总线端口测范围处理；B2 含缺失 cell 测鲁棒性。
- 16 条件 a-p：zip/py_compile/B-run/每 cell module/每 cell bind/input 计数/output 计数/inout 排除/bind 连接/总线范围/反硬编码 A+泛化/B2 泛化/缺失 cell 优雅/确定性/递增/单文件。
- 自验：ref PASS 16/16；10 negative 全 FAIL；§4.9 三假全 FAIL；test==disk sha 一致；k=16。
