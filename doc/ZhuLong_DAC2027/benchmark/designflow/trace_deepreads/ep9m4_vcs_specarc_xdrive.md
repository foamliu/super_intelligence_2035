# 深读笔记：ep9m4 (lorikx@hfeg0pkn001, mc104, verification)

**trace**: `/home/lorikx/.cline/data/sessions/1789545210038_ep9m4/1789545210038_ep9m4.messages.json` (1.8MB, 98 msgs, 53 user turns)
**项目**: `/home/lorikx/1prfbv_refer/v_model/CXMT_SPSRAM_0914_v14/` (CXMT SPSRAM 1-port SRAM Verilog 模型 v14)
**配置**: 128×80, CD=1 (Center Decode), TV=1 (TIMING_VALIDATION), CM=1 (2-bit group repair)，simv=`simv__128x80_cd_tv_cm1`，VCS V-2023.12-SP2-3

## 用户意图（A-faithful 候选轮）
- **USER#0 (ts=1789545210651)**: `请分析目前的仿真为什么FAIL @rtl/sp_sram.v @sim/tb_sp_sram.v` ← **clean 需求轮**（未给根因/修复），可作 A 档任务说明。
- USER#79 (ts=1789547789696): `可是我要是用这个做例化然后去做验证的话，还得打开宏？TSMC不是这么做的吧` ← **否决 macro-gating 修复**（用户约束：不能用宏门控，要符合 TSMC 惯例）。
- USER#93 (ts=1789548394203): 粘贴 `sram_sp.sv` SystemVerilog 行为模型参考（提供参考文件，非根因/修复）。
- USER#94 (ts=1789548444780): `Error-[SMOPMP] Size mismatch ../rtl/sp_sram.v, 3436 ... (posedge CLK => Q) = (tcd_s, tcd_s, thold_s, tcd_s, thold_s, tcd_s); 85 warnings 1 error 还是有问题` ← **报告第二版修复的 VCS 编译错误**（SMOPMP = 6-tuple delay on simple parallel path without `: value` 不允许）。
- USER#97: 切换到 GAAFET TEG 选择题（与本任务无关，trace 结束）。

## assistant 工具链（98 msgs，48 tool_use）
list_allowed_files → get_agent_policy_status → list_allowed_files(sim/rtl) → read_files(Makefile/filelist/VCS log) ×多 → search_codebase(tb Test 19 / check_memoryIO) ×多 → read_files(tb 分页定位 Test 1-18) ×多 → read_files(DUT CM=1 timing params / CD CR-shift logic) ×多 → read_files(specify block / buf-gate / cond_q_arc / ARCMASK / DM macro) → editor ×5（修复迭代）→ read_files(验证)

## 根因 + 修复链（3 版修复，2 错 1 对）

### Bug（v14.3b）
sp_sram.v specify block 行 ~3436:
```verilog
if (cond_q_arc)
    (posedge CLK => (Q : 1'bx)) = (tcd_s, tcd_s, thold_s, tcd_s, thold_s, tcd_s);
```
- `` `define DM 1`` 当 `TIMING_VALIDATION` (TV=1) 定义时
- `localparam ARCMASK = `DM;` → ARCMASK=1
- `assign cond_q_arc = !CEB_buf & WEB_buf & (ARCMASK == 1);` → 读时激活
- `tcd_s = tcd = DM*TACC = 4.0ns`（DM=1 时非零）
- **VCS V-2023.12 在 DM=1 时把 specify path 的 `: 1'bx` default 当作持续驱动源（persistent driver）**，和 buf gate 行为驱动长期并存 → 多驱动冲突 → **Q = X**（每个读操作）
- v14.3b changelog 自己警告："VCS TV-mode regression must be re-run to confirm no X-drive regression; if it re-appears, the fallback is gating this arc behind a macro"
- iverilog 下 buf gate (gate primitive) 优先级胜过 path default → 不触发 X-drive（故 v14.3b buf-gate 修复在 iverilog 验证通过，VCS TV 模式失败）

### 修复 1（m#66-76，错）：macro-gating
```
`ifdef SPECIFY_ARC_LIVE
    localparam ARCMASK = `DM;
`else
    localparam ARCMASK = 0;   // arc inert for behavioral sim
`endif
```
→ USER#79 否决：例化做验证还得打开宏，TSMC 不这么做。

### 修复 2（m#88，错）：去 `: 1'bx` 保 6-tuple
```verilog
if (cond_q_arc)
    (posedge CLK => Q) = (tcd_s, tcd_s, thold_s, tcd_s, thold_s, tcd_s);
```
→ USER#94 报错：VCS `Error-[SMOPMP] Size mismatch` —— 6-element delay tuple `(d01,d10,d0z,dz1,d1z,dz0)` **要求** `: expression` 语法，简单 parallel path `(posedge CLK => Q)` 不带 `: value` 不能用 6-tuple。

### 修复 3（m#95 提案，对）：2-delay rise/fall 无 `: 1'bx`
```verilog
if (cond_q_arc)
    (posedge CLK => Q) = (tcd_s, tcd_s);
```
- 无 `: 1'bx` → 无持续 X 驱动源 → 无 X-drive 冲突
- 2-delay (rise/fall) 形式 → VCS 接受（无 SMOPMP 错误）
- arc 条件 (cond_q_arc) 保留 → arc live for qualib xcheck
- 无 macro gating → 符合 TSMC 惯例（specify arc 始终编译，arc 条件始终 live，无额外 define）
- **注意**：m#95 仅文本提案，trace 在应用前结束（USER#97 切走）→ 此为 agent 推导出的技术正确解，非用户显式接受，但符合两条用户约束（无宏 + 能编译）。

## TSMC 惯例对比（agent m#80-92 总结）
| 特性 | v14.3b（旧） | v14.3c（对） | TSMC |
|---|---|---|---|
| specify arc 始终编译 | ✓ | ✓ | ✓ |
| arc 条件 live (!CEB&WEB) | ✓ | ✓ | ✓ |
| 额外 define/宏 | 不需要 | **不需要** | 不需要 |
| 行为仿真 DM=0 | ✓ | ✓ | ✓ |
| TV=1 行为仿真 | ✗ FAIL | **✓** | ✓（或用 SDF back-annotation） |
| path default `: 1'bx` | 有（致 X-drive） | **无** | 无 |

## case 设计（SpecArcXdriveFix-001）
- **domain**: verification（VCS sim 失败诊断 + RTL specify-block 修复）
- **档**: B 档 synthesized（真 sp_sram.v 3400 行太大；合成 minimal repro module 保 bug 结构）
- **层**: L1-static（check subprocess 真跑候选 fix_spec_arc.py，解析输出 .v 结构断言；不依赖 VCS/iverilog 编译）
- **交付**: `fix_spec_arc.py <input_v> <output_v> <report.json>` —— 读 buggy .v，定位 specify arc 的 `: 1'bx` default，转 2-delay rise/fall 无 default，保 arc 条件 + delay 值 + 不加宏，写 fixed .v + 诊断 JSON
- **A 可见**: sp_sram_A.v (buggy specify arc with `: 1'bx` 6-tuple) + vcs_fail_A.log (Q=X 症状) + task_brief + prompt
- **B 隐藏**: sp_sram_B.v (不同 module/端口/位宽/delay/arc 条件名 + 干扰 specify arc 必须不动 + 2 个错解陷阱注释) + vcs_fail_B.log
- **check.py 16 conds (a-p)**: 见 reference/check.py
- **negative**: empty_stub / print_only / macro_gate_stub (用宏门控=被否决的修复) / six_tuple_stub (6-tuple 无冒号=SMOPMP 错) / naive_delete_arc (删整个 arc)

## 与既有 case 区分
- SimFailParse-001 = xrun rpt/log 解析产 JSON 诊断（无修复）
- VcheckMacroAdd-001 = UVM ref_model 宏注入
- FsdbVerdiInteg-001 = FSDB+Verdi 集成脚本
- ParamRecon-001 = python-vs-verilog 参数对齐
- 本 case = VCS specify-arc X-drive 根因诊断 + RTL specify-block 修复（2-delay 转换），交付形态/判分字段全不同
