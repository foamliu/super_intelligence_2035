# s08eb — rhyanw @ hfeg0plg76 · mc=33 · schematic_netlist · SPICE include-chain undefined-param scan

## trace source
- session: `1794226612818_s08eb` · user `rhyanw` · host `hfeg0plg76` · 43 msgs / 23 user turns / 230KB
- scan: `ssh_eda_search_20261109_224902/summary.tsv` (mc=33, kw: netlist:114;synopsys:51;schematic:34;pex:6;hspice:6)
- real task summary: 用户贴 PrimeSim 报错日志（`undefined parameter or function definition 'tstart2'`），让 assistant 找出 SPICE deck `mixbest.sp` 的 include 链里所有"引用了但没定义"的参数。

## 真实任务流（11 user turns 演进）
1. U#0 贴 PrimeSim 日志 → `tstart2` undefined in `ideal_stimulus_nooc.sp` (9 处, 行 3/5/7/9/11/13/16/18/20)
2. A 读 `mixbest.sp`/`runsim`/`mixbatch.pl` → 发现 stimulus 用 `tstart2` 但 deck 只 define `tstart`（行29），从未 define `tstart2`
3. A 验证 `tstart2` 未在其它 include 里定义；`ideal_stimulus_drvqa.sp` 定义了 `tstart2=...` 但该 include 被注释掉（`*.inc`）
4. U#14 贴新日志（include 路径变了：从 huange 的 stim 变成本地 `.../SM/05_SANEN_SAPEN/ideal_stimulus_nooc.sp`，8 处错误行 5/8/12/14/16/19/21/23）
5. U#18 贴日志：用户加了 `tstart2` 后报 `tsense` undefined → 一类"未定义参数"一个一个被报出
6. A 写 Python 扫描器 `check_missing_params.py` 一次性扫所有 include 文件找缺哪些
7. A 扫描器 bug 1：把 `*.` 注释行 `.inc` 当真 → 误判 `tsense`/`OcEn` 已定义（其实只在被注释的 `ideal_stimulus_drvqa.sp` 里定义）→ 修复：忽略 `*`-commented `.inc`
8. A 扫描器 bug 2：`mixbest.sp` 行37 写成 `.inc'...'`（`.inc` 与路径间无空格），regex 要求 `\s+` → 漏跟 stimulus → 修复：regex 允许 `\s*`
9. 最终报告（修正后）：当前生效 include 链里"引用但未定义"参数 = `tsense`(行5/12/14/16/19/21/23) / `tocon`(行5) / `teq`(tocon=teq 需要) / `OcEn`(行5/12/14/16/19/21/23 PWL系数) / `OcN_A`/`OcN_B`/`OcN_C` / `OcP_*` ...

## 金标准机制（参数化）
SUT `find_undefined_params.py <deck>` 读 SPICE deck → 沿**生效** `.inc`/`.include`/`.lib` 链递归（跳过 `*`-commented 行，处理 `.inc'...'` 无空格语法）→ 收集 `.param NAME=VAL` 定义 + 收集参数引用（`.param` RHS 与引号内 PWL 时间表达式里的标识符，排除数字单位后缀 n/u/m/p/f/k/g/t/meg 与 SPICE 函数名）→ 输出 undefined = referenced − defined。

关键解析陷阱（金标准必须正确处理，check.py 必验）：
- **`*`-commented `.inc` 不跟**：`*.inc 'decoy.sp'` 是注释，其内 `.param` 定义不计入生效集 → decoy 里定义的 `tsense/tocon/OcEn` 仍算 undefined
- **`.inc'...'` 无空格**：`.inc'stim.sp'`（`.inc` 后无空格直接接引号）必须匹配并跟随
- **嵌套 include**：pwr.sp 里 `.inc sub.sp` → 递归跟到 depth 2，sub.sp 的 `.param` 计入生效定义
- **多 `.param` 每行**：`.param tstart=30n trise=1n t1=5n` 一行 3 个定义

## B-grade synthesized 设计（SpiceUndefParamScan-001）
A/B/C 三套 deck，参数/net/instance 名前缀完全不相交（A: tstart/tsense/OcN_A; B: vstart/vsense/OcN_B; C: wstart/wsense），undefined 数量不同（A=7, B=7, C=4）防硬编码计数。
- A（visible, assets/inputs_A/）：mixbest_A.sp + stim_A.sp（`.inc'...'` 无空格引入）+ pwr_A.sp（`.inc ` 空格引入）+ decoy_A.sp（`*.inc '...'` 注释引入，定义 tsense/tocon/OcEn/teq/OcN_A1/OcN_A2 但不计）
  - 生效定义 = {tstart, trise, t1, OcP_A1, OcP_A2, tcom}；引用 = {tstart2, trise, t1, tstart, tsense, tocon, teq, OcEn, OcN_A1, OcN_A2, tcom, OcP_A1, OcP_A2}；undefined = {tstart2, tsense, tocon, teq, OcEn, OcN_A1, OcN_A2}
- B（hidden, assets/hidden/inputs_B/）：嵌套 include depth 2（pwr_B → sub_B），undefined = {vstart2, vsense, vocon, veq, OcEnB, OcN_B1, OcN_B2}
- C（anti-hardcode, 嵌入 check.py 字面量）：undefined = {wstart2, wsense, wocon, weq}（数量 4 ≠ A/B 的 7，破计数硬编码）

## SUT 约束
- 纯 stdlib（re, os, json, argparse, sys）；禁 numpy/pandas/subprocess/socket/eval/exec；禁 B/C 字面量（vstart/vsense/wstart/wsense/D_WrC10_B 等）
- CLI: `find_undefined_params.py <deck> [--out report.json]`
- 输出 JSON: {deck, defined_params:[...], referenced_params:[...], undefined_params:[...], include_chain:[...], commented_includes:[...]}

## check.py（≥10 条件 a-k 独立 oracle）
a zip 合法 + 无禁 import/eval/exec/B字面量/泄漏  / b py_compile  / c SUT 退出 0 + JSON + 6 顶层键  / d include_chain 含 stim+pwr（depth≥2 时含 sub）  / e commented_includes 含 decoy（验证 `*`-comment 不跟）  / f `.inc'...'` 无空格语法被跟（stim 在 chain 里）  / g defined_params == oracle 生效定义集  / h referenced_params == oracle 引用集  / i **undefined_params == oracle undefined 集（核心）**  / j 反硬编码 C 跨输入匹配 oracle（C undefined 数量 4 ≠ A 7）  / k 3-seed sha256 稳定

## 维度正交（vs 既有 D schematic_netlist case）
既有：SchemExplodeLabel-001(#503 schematic 标签展开) / SpfDiffCompare-001(通用 SPF diff) / NetlistPortClean-001(#495 端口清洗) / TbFamilyMergeConverted-001(#482 testbench 合并) / FindCir4CrossProbe-001(#497 cross-probe) / ExprLogicCheck-001(#498 表达式逻辑)。
本 case = SPICE `.inc` include-chain 递归解析 + `.param` 定义/引用收集 + undefined-param 报告 + `*`-comment/include 无空格语法处理 —— 机制（include 链递归 + param 定义/引用分析）与产物（undefined-param 报告）全不同，非重复。

## difficulty = L1（诚实标）
SUT 纯 stdlib 文本解析（re 扫 SPICE deck），check.py subprocess 跑 SUT 脚本（非 PrimeSim/HSPICE）。按 §5 L2=真跑沙盒 EDA 工具不满足；按 r518 P-003 提议，真实 grounding demand = depth 1-2（text-in/script-out）。与既有 D 域 SPF/netlist 文本后处理 case 同类（§4.2 subprocess 满足，但非 drive EDA tool）。
