# r852 深读 — 1791974855202_32935 — UVM-style SRAM 验证 SV 脚本代码审查 (code-review Q&A)

## 元数据
- session: `1791974855202_32935`
- user: `shanliny` @ `hfeg0pkn003`(10.129.2.12) [scan 也命中 hfeg0plg107(10.129.8.239)/hfeg0plg100(10.129.8.232)]
- mc=51, agent=lead, subdir-path ALIVE 133092B(messages.json) / 2213911B(archive.json) / 237 msgs (12 user turns)
- 域: verification (类 UVM SRAM 验证 SV testbench 代码审查 + 后续 debug-fix) — scan keyword systemverilog:353/synopsys:36/verilog:21
- 旧判 r501(2026-11-14): "SV UVM code-review Q&A" → parked (旧§5 Q&A-gate 误杀)
- 11-15 reaudit: code-review Q&A 合法 → 复活 (本条为「24 待深读」之一)
- shanliny 已有 27 case (跨 shard), 但本 session 意图 (UVM SRAM testbench 代码审查找 bug) 与现有 case 主题不同 (现有多为 STA/SDC/synthesis/IR-lint), 非 intent-dup

## 用户真实意图 (原话)
- U#0: `这是一个形似uvm的sram验证sv脚本` + 11 个 attached .sv 文件 (driver/env/interface/monitor/package/ref_model/strategy_base/strategy_ext/top/transaction_base/transaction_ext)
- = 单轮 code-review Q&A: 审查这套类 UVM SRAM 验证 SV 脚本, 找出 bug/问题
- (后续 U#10/U#76/U#92/U#146/U#202 等为 debug-fix 迭代, 非 U#0 意图, 不纳入本 case)

## 11 个 attached .sv 文件 (uploads/ 可达, A档资产可行)
路径: `/home/shanliny/.cline/data/sessions/1791974855202_32935/uploads/`
- driver.sv 7289B, env.sv 4987B, interface.sv 14319B, monitor.sv 13056B, package.sv 751B
- ref_model.sv 29676B, strategy_base.sv 5183B, strategy_ext.sv 31089B, top.sv 5347B
- transaction_base.sv 4962B, transaction_ext.sv 15542B
- (另有 log 461723B / monitor_log.csv 25947B / timing.vcd 747474B — 后续 debug 用, 非 U#0)
- **A档可行性**: uploads/ 对 e0031982 在 10.129.2.12 实测可读 (ls -la 成功), .sv 文件自包含, 无 /rundata 权限问题 → A档 trace-faithful 可行 (与 r851 pits0 /rundata Permission denied 不同)

## agent 真实做法 (msg 9 完整代码审查报告)
agent 通读 11 文件后输出按严重程度分类的 bug 报告, **14 个 bug**, 每个含 文件+行号+代码片段+描述+严重度+修复建议:

### 🔴 严重 (2)
- **Bug 1**: `monitor.sv` L278-284 — TIMING_VALIDATION 路径下 `ref_model` 未声明 (sram_monitor 类只有 vif/scb 两成员, 无 ref_model 句柄; ref_model 属 sram_scoreboard) → 编译报错. 修复: 把 ref_model 传给 monitor 或让 scoreboard 封装 get_expected_data()
- **Bug 2**: `transaction_ext.sv` — test 信号约束与执行不一致 (write_transaction L74-78 约束 test=='1 但 execute L91 驱动 test=1'b0; bitwrite L103-108 同; column_redundancy L230-237/L268 同) → randomize 满足 test==1 但 execute 覆盖为 0, 拷贝粘贴引入. 修复: 约束改 test=='0

### 🔴 重要 (3)
- **Bug 3**: `top.sv` L114-116 + L150 — dut_bwen 多驱动源 (ifdef BITWRITE 下 assign dut_bwen=sram_vif.bwen 与 L150 无条件 assign 重复). 修复: 删 L114-116 ifdef 包裹或把 L150 移入 ifdef
- **Bug 4**: `transaction_base.sv` L108 — `virtual virtual function void execute(...)` virtual 重复 → 部分综合/仿真器报语法错误. 修复: 删一个 virtual
- **Bug 5**: `strategy_ext.sv` L49-51 — `random_strategy::get_data_pattern()` 函数体为空无 return (基类 pure virtual 必须实现) → 编译警告/错误. 修复: 加 return '0

### 🟡 中等 (3)
- **Bug 6**: `transaction_base.sv` L73 — 硬编码 `top_tb.target_clk_half_period_init` 层次路径 → 不能重命名 top/不能复用/null pointer 风险. 修复: 构造函数参数传入
- **Bug 7**: `strategy_ext.sv` — `march_c_bitwrite_strategy` 名为 March C bitwrite 但只测地址 0 不扫描全地址空间. 修复: 加地址循环或重命名
- **Bug 8**: `interface.sv` L132-135 + L143-148 — vec_cb 与 mon_cb 都声明 output 同一组信号 (test/ra_e/wa_e/wat/wav/wt/rt/trkt/byp), vec_cb 未被 modport 引用 (dead code) → 多 clocking block 驱动同信号不规范. 修复: 删 vec_cb 或移入 modport

### 🟢 轻微 (6)
- **Bug 9**: `package.sv` L24-31 — `sram_testchip_pkg` 定义但从未 import/使用 (dead package)
- **Bug 10**: `transaction_base.sv` L65-66 — `$floor()` 返回 real 赋给 parameter → 类型转换警告. 修复: 用整数除法 DATA_WIDTH/4, DATA_WIDTH/2
- **Bug 11**: `strategy_base.sv` L86 — `int addr` (有符号) 与 `rand bit [ADDR_WIDTH-1:0]` (无符号) 混用 → 边界条件隐式转换出错
- **Bug 12**: `driver.sv` L100 — `if (op.name == "COLUMN REDUNDANCY")` 字符串名匹配判断事务类型 → 脆弱 (name 改了静默失效). 修复: 用 $cast/tagged union
- **Bug 13**: `ref_model.sv` — `sram_testmode_ref_model` 扩展 sram_behavioral_model 但未覆写 write/read → testmode 时序逻辑未启用 (与普通行为模型无异)
- **Bug 14**: `strategy_base.sv` L69 — 硬编码 `top_tb.target_clk_half_period = op.clk_half_period` (同 Bug 6 模式)

## agent 总结表
| 严重程度 | 数量 | 主要问题 |
|---|---|---|
| 🔴 严重 | 2 | monitor 缺 ref_model 句柄、test 信号约束/执行不一致 |
| 🔴 重要 | 3 | dut_bwen 多驱动、virtual 重复、空函数体 |
| 🟡 中等 | 3 | 硬编码 top_tb、bitwrite 不扫描地址、clocking block 冲突 |
| 🟢 轻微 | 6 | 未用 package、类型混用、字符串比较、不完整实现等 |
优先修复: Bug 1 (TIMING_VALIDATION 编译失败) + Bug 2 (test 信号随机化矛盾)

## A档可行性核验
- uploads/ 11 .sv 文件对 e0031982 在 10.129.2.12 实测可读 (ls -la 成功, scp 成功)
- → **A档 trace-faithful 可行**: 用真实 .sv 文件作 fixture A, 真实用户 U#0 原话作 prompt, agent msg 9 的 14 bug 报告作 gold
- hidden-B 需 synthesized variant (改 bug 标识符: 不同文件名/不同行号/不同信号名/不同 bug 类型), judge-only 不进 SUT 沙箱

## 拟造任务形态 (defer 到下轮, 本轮时间预算不足以合成 11 文件 + variant B)
- case_id: EDA-Eval-DesignFlow-UvmSramTbCodeReviewQA-001
- domain: verification
- 档: A档 trace-faithful (真实 .sv 文件) + synthesized hidden-B (variant .sv)
- 范式: S5 code-review Q&A + specificity oracle (静态中文 markdown bug_report.md, 同 SimStimulusLocateQA-001 范式)
- 交付: submit.zip 内 bug_report.md
- fixture A(可见): 11 真实 .sv 文件 (从 uploads/ scp, 自包含)
- hidden-B(判分, synthesized variant): 11 .sv 文件变体, bug 标识符全改 (不同文件名/行号/信号名/bug 类型), judge-only 不进 SUT 沙箱
- check.py: 解析 A 的 11 .sv 推导 ground-truth 14 bug 签名 (文件+行号+bug 类型描述); 解析 B 推导 B-only 标识符; 断言 SUT bug_report.md:
  - 识别 Bug 1 (monitor.sv TIMING_VALIDATION ref_model 未声明) ①
  - 识别 Bug 2 (transaction_ext.sv test 约束 vs execute 不一致) ②
  - 识别 Bug 3 (top.sv dut_bwen 多驱动) ③
  - 识别 Bug 4 (transaction_base.sv virtual virtual 重复) ④
  - 识别 Bug 5 (strategy_ext.sv get_data_pattern 空体无 return) ⑤
  - 识别 Bug 6/14 (硬编码 top_tb 层次路径) ⑥
  - 识别 Bug 8 (interface.sv vec_cb/mon_cb 多 clocking block 驱动同信号) ⑦
  - refuse-to-hallucinate: 不编造 A 中不存在的 bug (B-only bug 标识符不得出现) ⑧
  - 报告含严重程度分级 + 文件名 + 行号 (specificity) ⑨
  - 不泄漏 B 独有标识符 (防背题) ⑩
  - 反退化 (markdown 结构 + 中文主体 + 非空壳) ⑪
  - 确定性 (报告内容稳定) ⑫
  - 预计 k≈12-14
- 自验: ref bug_report.md (agent msg 9 提炼) PASS 12/12 + 3 neg (empty/print_only硬编A bug名/core_del只报 2 bug) 全 FAIL + §4.9(a)(b)(c) 三假提交全 FAIL

## 同批未选 (r852 选料)
- 5u1j9 (e0039102, verification, run_regr 架构分析) — **intent-dup 22gh5 RunRegrArchAnalyze-001** (同 user e0039102/同项目 drgsa+ddgoa/同意图"理解 run_regr 框架架构整理报告", forked session) → 不可造(已覆盖)
- 685bd (eric1ch, digital, LPDDR6 regression debug skill 固化) — skill-engineering + lpregr 工具依赖 + 2.2MB archive, 无牙 headless check (skill 固化/expected-value 拆解需 skill 上下文) → 不可造(无牙 check, skill-dependent)
- 本轮选 32935 深读 (mc 最高 51 + A档可行 + bug gold 具体), 但 11 文件 + variant B 合成超本轮时间预算 → defer 下轮

## 教训
- 选料前必须查 intent-dup (同 user/同项目 forked session 的意图碰撞), 不能只查 session ID 碰撞 (5u1j9 session ID clean 但 intent=22gh5)
- A档可行 (uploads/ 可达) 的 case 比 /rundata Permission denied 的 B档 reframe 更忠实, 优先选
- 11 文件 code-review case 合成需 ≥1 整轮 (variant B 11 文件 + check.py 12+ 断言), 不宜在 40min 单轮内与选料深读合并
