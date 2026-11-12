# lilaj (1793259975527_lilaj) — X_S_Check lib-check report 诊断 + dbg 端口宏化方案

**trace**: lorikx / hfeg0pkn004 (10.129.2.13) / mc58 / verilog:295;rtl:279 dominant (c=0 b=0 n=0, clean A) / session dir `1793259975527_lilaj/` (含 .json + .messages.json, 415KB / 86 msgs / 46 user / 40 asst) / agent=lead / deep-read 2026-11-12 r424.

## 用户意图（3 条真实 prompt）
- **U#0** (mode=act):「请查看 report/X_S_Check_inspection.html 文件，检查 fail，model 和 lib 到底有哪些没对上，如果需要改的话需要怎么改，先给我个计划，不要修改文件」→ 诊断需求，未给根因 → **A-faithful 合格**。
- **U#31**:「我准备去另一个路径去修改 model 的部分，请你把需要修改的内容整理出来，做法我选修改 model 的代码来规避 dbg 信号，仿真中可以看，但是例化中默认用宏定义关掉这些接口」→ 指定修法方向（宏化 dbg 端口），但仍需 agent 整理具体改点。
- **U#43**:「请输出成 markdown 文件」→ 产出 `dbg_fix_plan.md`。

## agent 工具链
list_allowed_files + run_approved_command(shell-runner/python-runner) + read_files + editor×多 (写临时分析脚本 _tmp_scan/_tmp_lib/_tmp_src2-4/_dbgan/_dbgscope，分析后 _cleanup 删除，不动报告/数据)。

## 关键发现（agent 诊断结论）
1. **报告总览** (corner tt0p75v25c)：check_Verilog(model) E=0；check_Tmlib(lib) **E=4**；xcheck_Verilog_Tmlib(model vs lib) **E=1**。
2. **check_Tmlib 4 个 E**：timing_table_value_cloned（minimum_period rise/fall_constraint 值相同）×2、library_attribute_presence、operating_conditions_attribute_presence。
3. **xcheck 1 个 E = pin_name "Verilog Only: dbg_***"**：Verilog model 有 dbg_* 端口但 lib 没有。
4. **根因**：源文件 `CXN4HCSPS512X8M4B2C1R1W1BW1RE1_FS.v` 中 dbg_* 的**内部驱动逻辑全部已用 `ifdef TIMING_DEBUG` 包住（66 处）**，**唯独 module 端口列表的 dbg 声明（第 1045–1074 行，30 个 dbg 端口）是无条件声明**——这就是 pin_name 报 Verilog Only 的根源。.org 版本与主文件相同（非无-dbg 版）。
5. **修法**：端口列表 dbg 块加 `ifdef TIMING_DEBUG` 包裹，处理边界逗号（上一个非-dbg 端口后的逗号）；注意原有注释提到「故意不用 ifdef 包端口列表（怕 VCS 解析 issue）」，改用宏需处理该坑。

## 产出
`dbg_fix_plan.md`（结论速览 + 修改内容[端口块 ifdef 包裹 + 边界逗号] + 30 个 dbg 端口清单 + 风险[VCS 端口列表 ifdef]）。

## 合成方案（B 档 synthesized）
- **archetype**: spec-driven 静态分析器 / 诊断器（digital L1），同 VecgenProbeDiag / SimIncludeMissDiag 模式。
- **deliverable**: `dbg_port_audit.py`（纯 stdlib）—— 解析 Verilog model 端口列表（逐行跟踪 `ifdef TIMING_DEBUG` guard 状态，含嵌套 ifdef）→ 识别 dbg_* 端口 → 分类 wrapped/unwrapped；解析 X_S_Check 检查摘要（per-check W/E/T 计数 + fail 条目[check/session/category/severity/message]）→ 关联 unwrapped dbg 端口 ↔ pin_name "Verilog Only: dbg_*" fail → 输出 JSON。
- **A** (SUT-visible): model_A.v（30 dbg 端口全无条件 + 内部驱动全 ifdef）+ X_S_Check_summary_A.txt（check_Tmlib E=4 / xcheck E=1 pin_name 3 个 dbg）+ spec.md。
- **B** (hidden): model_B.v（不同布局：2 unconditional + 4 ifdef-wrapped + 2 nested-ifdef-wrapped）+ X_S_Check_summary_B.txt（check_Tmlib E=3 / xcheck E=2：pin_name "Verilog Only: dbg_rdcnt" + missing_port Q）。跨输入守卫 A 无 nested-ifdef / B 的 unwrapped 集合与 A 不同。
- **判分**: check.py 独立 line-scan oracle（vs ref 的状态机 regex），k≈14：定位模块/函数、B 端口 dbg 总数/wrapped/unwrapped 计数、unwrapped 名单、B 摘要 per-check E 计数、fail 条目数、pin_name fail 名单、correlation(unwrapped==pin_name set)、嵌套 ifdef 正确分类、跨输入守卫（B unwrapped ≠ A）、3-seed 洗牌端口集合不变、missing_port 分类。
- **A-faithful**: U#0 未给根因 → 合格。B 档（trace 产出是 markdown 诊断方案，无可复用脚本工具，合成纯 Python 静态分析器核心）。
