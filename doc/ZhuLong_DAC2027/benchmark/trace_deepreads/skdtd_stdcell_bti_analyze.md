# deepread: 1790649594359_skdtd — Verilog BTI 标准单元模块分析

## trace 来源
- **session**: `1790649594359_skdtd.messages.json`
- **user**: `zmzhang` @ `10.129.8.230` (hfeg0plg 类)
- **match_count**: 8 (verilog:101; drc:101; netlist:5; systemverilog:4; rtl:1; cmos:1)
- **size**: 29961 bytes, 8 messages (4 user, 2 assistant text, 1 tool_use, 1 tool_result)
- **liveness**: r794 verified ALIVE via subdir path (`/home/zmzhang/.cline/data/sessions/1790649594359_skdtd/1790649594359_skdtd.messages.json`)
- **domain**: digital (Verilog 标准单元静态结构分析)

## 对话流

### U0: 「这是什么符号」
用户无上下文地问"这是什么符号"。agent 回复请提供更多上下文（数学/标点/特殊符号/代码符号）。

### U2: 「/rundata/drcpa/V0/simdir/verilog/zmzhang/dpcpa_dbg 分析下面路径的文件」
用户给出 DDR5 DRAM Controller/PHY 仿真调试目录路径，要求分析。

**A3 (tool_use)**: `list_allowed_files` depth=1 limit=200 on `/rundata/drcpa/V0/simdir/verilog/zmzhang/dpcpa_dbg`

**A4 (tool_result)**: 目录含 `]`, `@`, `\` 等特殊文件名 + `08-25`~`09-23` 日期子目录 + `.sv` 文件 + `run_build`/`run_cmd`/`set_env.sh`/`probe.tcl` 脚本 + `libs/`/`libsdb`/`netlist/`/`sdf/`/`patterns/`/`Regressions/`/`proj_monitor/` 等。

**A5 (text)**: 详细分析目录结构：
- DDR5 DRAM 控制器/PHY 仿真调试工作区
- 关键文件: `top.sv`(testbench), `ddr5_test.sv`, `ddr5_tasks.sv`, `ddr5_specdef.sv`, `ddr5_timing.sv`
- 脚本: `run_build`/`run_cmd`/`set_env.sh`/`probe.tcl`
- 库/网表/SDF/patterns/Regressions

### U6: 用户粘贴 T_BTIinvCSx1 模块 + 「这段代码表达是什么逻辑」

```verilog
module T_BTIinvCSx1( A, Y , vssz , vbulkn, vbulkp, vcc);
    input A;
    output Y;
    inout vssz , vbulkn, vcc, vbulkp;
    parameter string strength1 = "strong1";
    parameter string strength0 = "strong0";
    invYx_base #(strength1, strength0) I0 (.A(A), .Y(Y), .vcc_(vcc), .vss_(vssz), .vbulkn_(vbulkn), .vbulkp_(vcc));
    fgc_pwrstate_monitor ISPMONITOR (.celltype("invCS"),.sin(A),.sout(Y),.vpwr(vcc),.vgnd(vssz),.vblkn(vbulkn),.vblkp(vcc));
    specify
        specparam tRise = 25*`CDLYW:40*`CDLYW:60*`CDLYW, tFall = 25*`CDLYW:40*`CDLYW:60*`CDLYW;
        (A => Y) = (tRise, tFall);
    endspecify
endmodule
```

### A7: agent 逐段解析（关键产出）

1. **模块功能**: 反相器 `Y = ~A`
2. **电源与体偏置端口**: `vcc`(正电源), `vssz`(地), `vbulkn`(NMOS 体偏置), `vbulkp`(PMOS 体偏置,实际接 vcc 无独立偏置)
3. **invYx_base 实例**: 参数 `strength1`/`strength0` 控制驱动强度; `.vbulkp_(vcc)` → PMOS body 接 vcc
4. **fgc_pwrstate_monitor**: BTI 老化监控单元, `celltype("invCS")`, 追踪翻转率/电压应力/体偏置应力
5. **specify 时序**: `tRise`/`tFall` = 25:40:60 × CDLYW (min:typ:max, PVT 角)
6. **总结**: "智能"反相器, BTI aging-aware 标准单元, 用于可靠性签核

## case 合成决策

**档**: B档 synthesized（真实 `/rundata/drcpa/` 组私有路径 Permission denied 不可读 → 合成资产还原意图）

**§5 produce-task reframe**: 用户原始意图是「解释这段代码」(analysis-Q&A)。按新任务初衷，analysis-Q&A 是合法任务形态。为给 check() 加"牙"，reframe 成 produce-task：写 `analyze_stdcell_bti.py` 可复用脚本，对任意同类 BTI 标准单元做静态结构分析，输出 18 字段 JSON 报告。hidden-B 换成不同单元验通用性。

**A (visible)**: `T_BTIinvCSx1.v`（trace 原始模块）+ `config_a.json` + `task_brief.md`(18 字段规格) + `prompt.txt`

**B (hidden)**: `T_BTInandCSx2.v`（2-input NAND, 关键差异：
- 2 输入 A,B vs A 的 1 输入
- `nandYx_base` vs `invYx_base`
- `strength0="weak0"` vs `"strong0"`
- `celltype("nandCS")` vs `"invCS"`
- `ISPMONITOR2` vs `ISPMONITOR`
- `vbulkp_`(vbulkp) 独立连接 vs `.vbulkp_(vcc)` 接 vcc
- 2 条 specify 弧 (A=>Y)+(B=>Y) vs 1 条
- 延迟 30:50:70 vs 25:40:60

**check.py**: 22 独立断言（18 ground-truth 字段 + 确定性 3seed + 反硬编码 B-token + 反硬编码 A-leak + 非退化）

**自验**: ref PASS 22/22 + 4neg 全 FAIL(empty/print_only/hardcode_a/core_deleted) + harness-sim PASS

**ledger**: skdtd r794 parked → r812 claimed → case (EDA-Eval-DesignFlow-StdCellBtiAnalyze-001)
