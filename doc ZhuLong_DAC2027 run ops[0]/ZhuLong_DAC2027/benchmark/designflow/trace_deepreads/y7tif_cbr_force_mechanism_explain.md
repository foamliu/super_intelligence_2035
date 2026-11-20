# y7tif — LPDDR6 CBR Force 机制讲解（trace deepread）

- session: `1794362305034_y7tif`  user: `lein`  host: `hfeg0pkn005`  mc=49  scan=1115
- trace: 105 msgs / 1.47MB / agent=lead / 7 substantive user turns / model=deepseek-v4-flash / status=failed (terminal_marker failed_external_process_exit)
- 真实 trace 源: `ssh hfeg0pkn005 cat /home/lein/.cline/data/sessions/1794362305034_y7tif/1794362305034_y7tif.messages.json`

## 用户真实意图（原话链）
1. msg0: 「比较分析 /rundata/decqa/V0/simdir/verilog/lein/1103_lp6tb/Regressions 路径下 proj_function 和 function之间 用例的 区别 在哪里？」
2. msg30: 「分析 .../proj_function/refresh_cbr.run 用例主要的 验证场景」
3. msg57: 纠正 agent — 「CBR 是refresh的 计数器，主要用来计算refresh所需的地址，CBR 全称是 CAS Before RAS，列地址解析在前」
4. msg61: 追问「此 task 通过 Test Mode Register 编程将芯片内部刷新地址计数器直接加载到指定值 … 是哪条语句实现该功能的」
5. msg98: 「解析一下 上面 Force_CBR 的底层实现逻辑」
6. msg100: 「上述 Force_CBR 最终force到网表的哪个信号？」
7. msg101/102/103: 追问 force 到网表中的逻辑层次 / 哪个信号
8. msg104 (final, 未答): 「1103_lp6tb 是 lpddr6的验证平台 这个平台中 如何通过Force_CBR 把 初始值 force到 网表里的 且 网表中的 路径 是什么？」

**意图归纳**: LPDDR6 验证平台中 Force_CBR 如何把 CBR 刷新行地址计数器初值 force 到网表、底层实现逻辑、网表层次路径。A 档 trace-faithful（多轮「求解释/分析」Q&A，agent=lead）。

## 关键事实（ground truth，来自 trace 中 agent 读取的真实源码）

### A. refresh_cbr.run（proj_function/，regression_name="Refresh_CBR"）
- 速率: SetDataRateSpeedMR(...14400...,"4b4g")
- tRFC 倍率: trfc=1 默认；TRFC2X→trfc=2(+TM_2XTRFC+TM_NEWHALFWL)；TRFC0P5X→trfc=5；TRFC0P25X→trfc=25；SEFF→randcase 随机
- 核心序列 (lines 97-145):
  - repeat(16) Refresh // normal8192
  - `Force_CBR (.random(0), .trfc(2), .cbr(8190), .force_red(0));`
  - repeat(24) Refresh // normal8192 -> slt128
  - `Force_CBR (.random(0), .trfc(2), .cbr(16'h1CFD), .force_red(0));`  (7421)
  - repeat(24) Refresh // slt128 -> red32
  - `Force_CBR (.random(0), .trfc(2), .cbr(30), .force_red(0));`
  - repeat(24) Refresh // red32 -> normal8192

### B. proj_monitors.sv — task Force_CBR (lines 89-176)
```systemverilog
task Force_CBR (bit random=0, int trfc=0, bit[15:0] cbr=0, bit boundary=0, bit sc=sc_int, bit force_red=0);
begin
    bit[15:0] RowAddr; bit sc2force;
    sc2force = sc;
    `ifdef SCSWAP
    sc2force=~sc;
    `endif
    if (random==1) begin
        case (trfc)
            2: RowAddr=$urandom_range(8190);   // 1FFF
            1: RowAddr=$urandom_range(16382);  // 3FFF
            5: RowAddr=$urandom_range(32766);  // 7FFF
            25: RowAddr=$urandom_range(65534); // FFFF
            default: RowAddr=$urandom_range(16382);
        endcase
    end
    else if(boundary==1)begin
        case (trfc)
            2: RowAddr=8190; 1: RowAddr=16382; 5: RowAddr=32766; 25: RowAddr=65534;
            default: RowAddr=16382;
        endcase
    end
    else begin
        RowAddr=cbr;
    end
    proj_voltage_monitors.tbctrlmonitors.cbrinit[sc2force] = {force_red, RowAddr};
end
endtask
```
- 3 模式: random==1 (按 trfc urandom_range), boundary==1 (按 trfc 固定最大值), else (RowAddr=cbr 由调用者指定)
- trfc→max 映射: 2→8190(0x1FFF), 1→16382(0x3FFF), 5→32766(0x7FFF), 25→65534(0xFFFF)
- **核心赋值语句 (line 170)**: `proj_voltage_monitors.tbctrlmonitors.cbrinit[sc2force] = {force_red, RowAddr};`
  - 17-bit = {force_red[1], RowAddr[16]}
  - 网表层次路径: `proj_voltage_monitors.tbctrlmonitors.cbrinit[sc2force]`
- sc2force = sc (或 ifdef SCSWAP 时 ~sc) — 子通道索引
- **机制本质**: 直接层次引用赋值 (direct hierarchical reference)，NOT MRW/Mode Register Write（agent 最初误判为 Test Mode Register 编程，被用户纠正后修正）

## CBR 概念（用户纠正后）
CBR = CAS Before RAS — DRAM 传统刷新协议，列地址选通先于行地址选通；DRAM 内部 CBR 计数器(刷新行地址计数器)追踪下一次刷新的行。Force_CBR 在 Test Mode 下直接覆写该计数器到指定值，跳过自然递增，便于定向验证边界条件。

## 合成方案
- task_id: EDA-Eval-DesignFlow-CbrForceMechanismExplain-001
- 形态: spice_sim verification-grounded explain-Q&A → 产 `cbr_force_mechanism_analyzer.py(workdir,out_dir)` 解析 2 文件 → `cbr_force_mechanism_report.json`
- A 档 trace-faithful: A=真实 refresh_cbr.run + proj_monitors.sv（从 trace verbatim 提取）
- hidden B cross-input guard: DDR5 平台 ForceRefreshCounter task（不同 task 名/参数/网表路径/trfc 映射/位宽/调用值），check 只跑 B
- 断言 ≥8: 见 check.py
