# 深读笔记 — 1nsgi · netlist_cell_convert（schematic_netlist 域）

> trace 来源（保留原用户名用于溯源，即时令 XII）：host=`hfeg0plg17`(172.16.8.162，NFS home 共享故同 session_file 在多机出现) · user=`e0039602` · session_file=`1792376698189_1nsgi` · session_msgs=317(160 user/157 assistant) · tool_use=119(editor 54 / run_approved_command 29 / read_files 26 / search_codebase 3 / list_allowed_files 4) · real_task_summary=`netlist_cell_convert 工具：抽象 cell 网表→simlib 物理单元(inv_base/inven_base)转换，迭代 prompt 规则 + 死节点/合并/互补选通 三级映射`
>
> match_count=394 · keywords=`netlist:1801;transistor:95;analog:24;schematic:12;mosfet:8;cmos:5;` · categorize=schematic_netlist（netlist 命中且无更高优先级 marker）

## 一、用户目标与完整工作过程

用户 e0039602 在 `~/Documents/netlist_change_v0.2/netlist_cell_convert/` 维护一个 Python 工具：把 schematic 导出的结构化 Verilog 网表里**simlib 物理库中不存在的抽象 cell**（fbs/inven/nor2/invhiz/inv/invenLVSx1/invDSx1/nand2/nand3…）逐 module 替换成 simlib 已有的物理单元（inv_base/inven_base/nn/pp/invhiz_base…）+ 门原语（buf/not/and/or）+ 参数（strength1/strength0），并注入 `fgc_pwrstate_monitor`。转换由外部 LLM（deepseek-v4-flash，经 gateway）推理；本工具负责解析网表、组 prompt、调 agent、写报告。

5 阶段工作流：
- **A 理解项目**（msg1-14）：让 agent 通读 run.py/src 8 模块/simlib_base.sv/outputs，总结数据流 `config→run.py→解析缺失cell→组prompt→agent推理→报告txt`。
- **B 诊断转换错误**（msg9,15-26）：`AF_ffrqLx1_Red`（7 抽象 cell：fbs/inven×2/nor2/invhiz/inv×2）被模型"逐格机械改名"成 7 个 *_base，而期望是"整块粗粒度重构"（3 个 inv_base + buf/not/assign clk）。根因：prompt 逼模型做 1:1 改名，没给"整块压缩"模板。
- **C 重构为按 module 组织**（msg15-41）：`build_prompt` 改为以 module 为单位传入完整模块原文 + 内部缺失 cell；输出格式三段式 `model：/ cell：/ 转换结果：`；后简化为两段 `cell：/ 转换结果：`（model 已在输入里）。`netlist_parser` 加 `module_blocks()` 提取模块完整原文。
- **D 强化转换规则**（msg79-145）：加"先理解语义再选单元"；**三级实现选择**（① 基础模块 inv_base/inven_base ② 门原语 buf/not/trireg ③ 裸管 nn/pp）；**裸原语使用边界**（不丢物理信息才可用）；**死节点/合并判断**（空载死节点删除、同输入同函数合并）；**互补选通合并**（二选一开关用 buf/not/assign clk）；**输出前必检三检查**（① 原语简化 ② 死节点/合并 ③ 互补选通合并）。
- **E 调网关健壮性**（msg43-158）：502/503 gateway 超时诊断；retry 上限改 3 次；单 module 失败不中断、跳过继续下一个；备份 prompt 再改。

## 二、转换规则（从 trace 提炼，用于 case）

**三级实现选择（按顺序判断）**：
1. 第一级【基础模块】：优先用 simlib_base 自带电源/衬底脚的物理单元（inv_base/inven_base/invhiz_base/fbs_base…）。
2. 第二级【门原语】：纯数字逻辑/锁存/时钟/保持，且第一级不适用时，用 buf/not/and/or/nand/nor/notif/trireg。
3. 第三级【裸管】：模拟/传输管逻辑才直接铺 nn/pp。

**裸原语使用边界**：用前先判断"会不会丢物理信息"——只在不丢失电源/衬底/强度语义时才用裸原语替代。

**死节点/合并判断**：
- 空载死节点 = 内部 wire 被某实例 output 驱动，但**不被任何其他实例 input 消费、也不是顶层 output** → 该驱动实例可删除。
- 同输入同函数合并 = 多个实例 cell 类型相同、输入脚接同一 net、电源脚相同 → 合并为 1 个物理单元。

**互补选通合并（二选一开关）**：两个 enabled 反相器（inven*）输出共驱、En/EnN 互补（Sel/SelN）→ 用 `buf(ck0nb_int,SelN); not(ck0_int,Sel); assign clk=((ck0nb_int===1'bx)|(ck0_int===1'bx))?1'bx:(ck0_int|ck0nb_int);` 派生 clk，再两个 inven_base 一用 `.En(clk).EnN(~clk)`、一用 `.En(~clk).EnN(clk)`。

**nand/nor → inv_base**：`nand2 I(.A(a).B(b))` → `inv_base I(.A(a&b))`；`nand3 I(.A(a).B(b).C(c))` → `inv_base I(.A(a&b&c))`；nor 用 `|`。

**fgc_pwrstate_monitor 注入**：每个逻辑输入 sin 注一个 `fgc_pwrstate_monitor(.celltype(...),.sin,.sout,.vpwr,.vgnd,.vblkn,.vblkp)`。

## 三、关键例（BEFORE 网表 → AFTER 转换 sv，verbatim 脱敏）

### 例1 T_inv_f3NORMSsub — 同输入合并 + 死节点删除
BEFORE（netlist，3 个 invDSx1 同 .A(in)，I2→net7/I1→out/I0→net6 死）：
```verilog
module T_inv_f3NORMSsub (out, in, inh_vcc, inh_vss, inh_vbn);
  output out; input in; inout inh_vcc, inh_vss, inh_vbn;
  wire net7; wire net6;
  invDSx1 I2 (.Y(net7), .vbn(inh_vbn), .vbp(inh_vcc), .vcc(inh_vcc), .vss(inh_vss), .A(in));
  invDSx1 I1 (.Y(out), .vbn(inh_vbn), .vbp(inh_vcc), .vcc(inh_vcc), .vss(inh_vss), .A(in));
  invDSx1 I0 (.Y(net6), .vbn(inh_vbn), .vbp(inh_vcc), .vcc(inh_vcc), .vss(inh_vss), .A(in));
endmodule
```
AFTER（合并为 1 inv_base，死节点 net6/net7 删除）：
```verilog
module T_inv_f3NORMSsub (out, in, inh_vcc, inh_vss, inh_vbn);
  output out; input in; inout inh_vcc, inh_vss, inh_vbn;
  inv_base I_invPS_12 (.Y(out), .A(in), .vbulkn_(inh_vbn), .vbulkp_(inh_vcc), .vcc_(inh_vcc), .vss_(inh_vss));
  fgc_pwrstate_monitor ISPMONITOR (.celltype("invCS"), .sin(in), .sout(out), .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vcc));
endmodule
```

### 例2 PWY_mxi2_TrimA_cvps — 互补选通合并
BEFORE（2 个 invenLVSx1，En/EnN 互补 Sel/SelN，共驱 Out）：
```verilog
module PWY_mxi2_TrimA_cvps (Out, Inv1_In, Inv2_In, Sel, SelN, inh_vss, inh_vcc, inh_vbn);
  output Out; input Inv1_In, Inv2_In, Sel, SelN; inout inh_vss, inh_vcc, inh_vbn;
  invenLVSx1 I30 (.Y(Out), .vbn(inh_vbn), .vbp(inh_vcc), .vcc(inh_vcc), .vss(inh_vss), .A(Inv1_In), .En(SelN), .EnN(Sel));
  invenLVSx1 I0  (.Y(Out), .vbn(inh_vbn), .vbp(inh_vcc), .vcc(inh_vcc), .vss(inh_vss), .A(Inv2_In), .En(Sel),  .EnN(SelN));
endmodule
```
AFTER（buf/not/assign clk 派生 + 2 inven_base 互补 En/EnN + 4 fgc_pwrstate_monitor）：
```verilog
module PWY_mxi2_TrimA_cvps (Inv1_In, Inv2_In, Sel, SelN, Out, inh_vcc, inh_vss, inh_vbn);
  input Inv1_In, Inv2_In, Sel, SelN; output Out; inout inh_vcc, inh_vss, inh_vbn;
  wire clk;
  parameter string strength1 = "strong1"; parameter string strength0 = "strong0";
  buf (ck0nb_int, SelN);
  not (ck0_int, Sel);
  assign clk = ((ck0nb_int===1'bx)|(ck0_int===1'bx))?1'bx:(ck0_int | ck0nb_int);
  inven_base #(strength1, strength0) I50 (.A(Inv2_In), .Y(Out), .EnN(clk),  .En(~clk),  .vcc_(inh_vcc), .vss_(inh_vss), .vbulkn_(inh_vbn), .vbulkp_(inh_vcc));
  inven_base #(strength1, strength0) I49 (.A(Inv1_In), .Y(Out), .EnN(~clk), .En(clk),   .vcc_(inh_vcc), .vss_(inh_vss), .vbulkn_(inh_vbn), .vbulkp_(inh_vcc));
  fgc_pwrstate_monitor ISPMONITOR_A (.celltype("invenGS"), .sin(Inv1_In), .sout(Out), .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vcc));
  fgc_pwrstate_monitor ISPMONITOR_D (.celltype("invenGS"), .sin(Inv2_In), .sout(Out), .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vcc));
  fgc_pwrstate_monitor ISPMONITOR_B (.celltype("invenGS"), .sin(Sel),     .sout(Out), .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vcc));
  fgc_pwrstate_monitor ISPMONITOR_C (.celltype("invenGS"), .sin(SelN),    .sout(Out), .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vcc));
endmodule
```

### 例3 IO_rsnand21nand31_DL_ACT_MERGE_READ — nand→inv_base 用 &
BEFORE（nand2 I6(.A(S).B(net16)) + nand3 I0(.A(R1).B(R0).C(Y))，net16 中间节点）：
AFTER：
```verilog
module IO_rsnand21nand31_DL_ACT_MERGE_READ (Y, inh_vbn, inh_vbp, inh_vcc, inh_vss, R0, R1, S);
  output Y; input R0, R1, S; inout inh_vbn, inh_vcc, inh_vss, inh_vbp; wire net16;
  parameter string strength1 = "strong1"; parameter string strength0 = "strong0";
  inv_base #(strength1, strength0) I6 (.A(net16&S),  .Y(Y),     .vcc_(inh_vcc), .vss_(inh_vss), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp));
  inv_base #(strength1, strength0) I7 (.A(R1&R0&Y),  .Y(net16), .vcc_(inh_vcc), .vss_(inh_vss), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp));
  fgc_pwrstate_monitor ISPMONITOR_A (.celltype("nandIOLV"), .sin(S),  .sout(Y), .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vbp));
  fgc_pwrstate_monitor ISPMONITOR_B (.celltype("nandIOLV"), .sin(R0), .sout(Y), .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vbp));
  fgc_pwrstate_monitor ISPMONITOR_C (.celltype("nandIOLV"), .sin(R1), .sout(Y), .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vbp));
endmodule
```

### 例4 D_latqn_ffRdBlk1 — 锁存保持（trireg + invhiz_base）
AFTER（关键：`trireg (medium) #(1,1,100) QN;` 保持高阻电荷节点；inven_base I0 驱动 QN，inv_base I1 反相到 net9，invhiz_base I2 弱驱动回 QN 形成保持）：
```verilog
module D_latqn_ffRdBlk1 (D, Lat, LatF, QN, inh_vcc, inh_vss, inh_vbn, inh_vbp);
  input D, Lat; output LatF, QN; inout inh_vcc, inh_vss, inh_vbn, inh_vbp;
  trireg (medium) #(1,1,100) QN;
  inven_base I0 (.Y(QN), .A(D), .EnN(Lat), .En(~Lat), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp), .vcc_(inh_vcc), .vss_(inh_vss));
  inv_base   I1 (.Y(net9), .A(QN), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp), .vcc_(inh_vcc), .vss_(inh_vss));
  invhiz_base #(.strength1("pull1"), .strength0("pull0")) I2 (.Y(QN), .A(net9), .EnN(~Lat), .En(Lat), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp), .vcc_(inh_vcc), .vss_(inh_vss));
  inv_base   I3 (.Y(LatF), .A(Lat), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp), .vcc_(inh_vcc), .vss_(inh_vss));
  fgc_pwrstate_monitor ISPMONITOR0 (.celltype("inven"), .sin(D),   .sout(QN),   .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vbp));
  fgc_pwrstate_monitor ISPMONITOR1 (.celltype("inv"),   .sin(Lat), .sout(LatF), .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vbp));
endmodule
```

## 四、simlib_base.sv 物理单元（关键定义）

`nn(B,D,G,S)` / `pp(B,D,G,S)`：nmos/pmos 包装器，mostype 参数选 nmos/rnmos/tranif1 / pmos/rpmos/tranif0。

`inv_base(Y, A, vbulkn_, vbulkp_, vcc_, vss_)`：反相器。strength1/strength0 参数；strong1→pp m1(.B(vbulkp_).D(Y).G(A).S(vcc_))，strong0→nn m2(.B(vbulkn_).D(Y).G(A).S(vss_))。

`inven_base(Y, A, EnN, En, vbulkn_, vbulkp_, vcc_, vss_)`：使能反相器（三态）。EnN 高时 pmos 路开，En 高时 nmos 路开。

其他：`fbs_base/fbr_base/fbens_base/fbrs_base/fbsr_base`（反馈锁存系列，带 En/EnN/R/SN）、`invhiz_base`（高阻反相器）、`passg_base`（传输门）、`dlyrc_base`（延迟）、`fgc_pwrstate_monitor(celltype,sin,sout,vpwr,vgnd,vblkn,vblkp)`（电源态监控，每个逻辑输入注一个）。共 ~25 顶层 module。

## 五、下轮 case 设计（本轮深读→下轮合成，IX §五 两轮节奏）

**Case ID**：`EDA-Eval-DesignFlow-Schematic-001`（schematic_netlist 域首条 proper，填空白域 2362 命中）

**定位**：纯 Python（标准库）网表"抽象 cell→simlib 物理单元"转换 + 简化工具。**确定性、无 LLM**——只做机械可推导的变换（死节点删除、同输入合并、nand/nor→inv_base 用 &/|、互补选通合并、fgc_pwrstate_monitor 注入），不做需语义判断的整块重构（AF_ffrqLx1_Red 那种留给 LLM，不入本 case）。这正好区别于 Analog-001（连接链追踪）与 LayoutAether-001（LVS 比对）。

**assets**（4 个，脱敏，从本 trace 真实数据合成）：
1. `sample_netlist.v` — 4 module 抽象网表：T_inv_f3NORMSsub(3 invDSx1) / PWY_mxi2_TrimA_cvps(2 invenLVSx1 互补) / IO_rsnand21nand31(nand2+nand3) / D_latqn_ffRdBlk1(锁存)。
2. `simlib_base_defs.sv` — inv_base/inven_base/invhiz_base/nn/pp/fgc_pwrstate_monitor 定义（供 agent 查物理单元端口）。
3. `convert_rules.md` — 三级实现选择 + 死节点/合并 + 互补选通 + nand→inv_base& + fgc 注入 规则（从 trace §二 提炼）。
4. `task_brief.md` — CLI 接口 + 输出格式 + 约束（纯标准库、确定性变换、不调 LLM/EDA 工具）。

**entry_point**：`outputs/submit.zip`（内含 `netlist_convert.py` + `converted.sv` + `transform_report.md`）

**test 思路**（Python `check(deliverable, workdir)` 双参，7 条件独立有牙）：
- (a) 解 zip 校验 3 文件齐全
- (b) netlist_convert.py 语法合法（py_compile）
- (c) 实跑 `python3 netlist_convert.py --netlist sample_netlist.v --simlib simlib_base_defs.sv --out converted.sv` 退出码 0
- (d) converted.sv 含 `inv_base I_invPS_12`（T_inv 合并死节点→1 inv_base，死 net6/net7 不出现）—— naive 只逐格改名保留 3 invDSx1→FAIL
- (e) converted.sv 含 `inven_base` ×2 + `assign clk` + `buf (ck0nb_int,SelN)` + `not (ck0_int,Sel)`（PWY 互补选通合并）—— naive 保留 2 invenLVSx1→FAIL
- (f) converted.sv 含 `.A(net16&S)` 与 `.A(R1&R0&Y)`（nand→inv_base 用 & 合并）—— naive 保留 nand2/nand3→FAIL
- (g) transform_report.md 列出死节点清单(net6/net7) + 合并组(3 invDSx1→1) + 互补选通组(PWY) + nand 合并组，每项带 module 名

**reference**：`netlist_convert.py`（纯标准库，parse Verilog module/instance/pin/net/port-direction，按规则做 4 类确定性变换，emit sv + report）+ reference_submit.zip + check.py。ref 自验 PASS；naive（逐格改名）3 类 FAIL。

**trace_source metadata**：`{host:"hfeg0plg17", user:"e0039602", session_file:"1792376698189_1nsgi", session_msgs:317, real_task_summary:"netlist_cell_convert 抽象cell网表→simlib物理单元转换+死节点/合并/互补选通"}`（user 用原用户名，即时令 XII）。

## 六、PII / 红线
- trace 原始 messages.json 仅在 .75 workdir 临时解析，已 close_session cleaned=true，不入库。
- 真实用户名 e0039602 / 路径 /home/e0039602/Documents/... 仅记于本笔记用于溯源；case 的 assets/prompt 不含真实用户名/路径（用 sample_netlist.v 等通用名）。
- 无 key/token/密码。
