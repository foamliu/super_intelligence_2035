# trace_deepread: 1794538116030_3aslp — CxDP STA flow driver improvement

- **session**: `1794538116030_3aslp.messages.json`
- **user/host**: e0046913 @ hfeg0pkn003 (10.129.2.12)
- **match_count**: 109 (netlist:502 / pt_shell:212 / synopsys:194 / primetime:64 / verilog:16)
- **size**: 839 KB / 151 msgs / 2 real user turns (single-turn produce-task + a "please continue")
- **scan**: ssh_eda_search_20261113_131349 (11/13 池)

## 用户意图（原话摘要）

U#0（9284 字符，核心 produce-task，单轮）：
> 「我是一名数字CAD工程师，正在开发CxDP STA flow，目前已有一套初期脚本在
> /proj/lacaa/TV1_digital/simdir/yutingq/CxDP/cla_top/sta 路径下… 我准备在保留原脚本
> 基础上进行改进并调试，因此新建了 .../cla_top_DS/sta 空目录，希望在此路径下 improve。」

用户给了一份完整的需求规格书 + deepseek 的 review 分析 + 三项具体改进：
- ① 选择性读入 + 详细信息（绝对路径 / 耗时 / 时间戳）—— 把 step 表扩成
  `{name proc script requires}` 声明式结构，`requires` 为 Tcl 布尔表达式，
  **"读入(source)"与"执行(call)"分开**，带 banner 与耗时打印。
- ② TimeStamp 汇总段 + 关键资源信息（每步耗时 + 实时 RSS + CPU + peak）。
- ③ Error / Warning / Information 汇总（解析 Makefile tee 出的 sta_*.log，
  按 `Error:`/`Warning:`/`Information:` 前缀分类计数）。
- 顺带 bug 修复（`current_design=_sel1` link 命名问题）+ LSF queue + check_config 变量完备性。

U#145：`你的回答似乎没有结束，请继续思考和回答`（催促续答，不构成新任务）。

## agent 工具链（86 tool_use）

- `editor` ×46、`run_approved_command` ×19、`read_files` ×11、`list_allowed_files` ×8。
- 读原 flow（Makefile / sta_setup.tcl / sta.tcl / proc/*.tcl / try-run log / qa report）。
- editor 被 Agent Policy Engine 拦（writableRoots 仅 `/home/e0046913`）→ 改走
  `run_approved_command` 经 shell-runner 写 `/home/e0046913/cxdp_stage/`，再 `cp` 到目标
  `/proj/lacaa/.../cla_top_DS/sta/`。
- 产 `_preflight.sh` / `_deploy.sh` / `impl/run/sta_setup.tcl` / `impl/run/sta.tcl`
  / `Makefile` 等并 try-run（pt_shell_command.log 2.5MB）。

## 最终交付物（agent 写在 /home/e0046913/cxdp_stage/impl/run/，已 scp 验证）

### sta_setup.tcl（10195 B，改进版）
- 新增变量默认：`STA_NETLIST_STAGE`/`STA_DELAY_PARAM`/`LIB_CORNER`/`RC_CORNER`/
  `CXDP_STA_SDC_MODES`/`STA_SDC_LIST`（多模式 SDC）/`MVDD_EN`/`MVTC_FILE`/
  `IRDROP_EN`/`IRDROP_FILE`/derate 值。
- 输出目录（report/out_src/session/log）。
- helper proc：`read_file_as_list`、`count_blackbox`。
- 多模式 SDC 解析：`STA_SDC_LIST` 非空→逐个加入 `CONSTRAINT_FILES`，否则回落单 SDC。
- **`CXDP_STA_STEP_LIST` 用 `list` (非 brace literal) 构建**，每个 step =
  `{name proc script requires}`，`requires` 在 setup 期 `[expr {...}]` 求值
  （如 `read_sdc` 的 requires = `[expr {[llength $CONSTRAINT_FILES] > 0}]`）。
- 新增 `check_config` step（变量完备性 + 输入文件存在性）。

### sta.tcl（6437 B，改进版 driver）
- source `sta_setup.tcl` + 可选 `../data/sta_override.tcl` + `glob proc/*.tcl`
  按数字序 source（**仅定义 proc，不执行**）。
- `cxdp_now`：wall-clock timestamp。
- `cxdp_live_rss`：`exec sh -c {awk '/VmRSS/{print $2}' /proc/self/status}`（Tcl exec
  不经 shell，故包 `sh -c`）。
- `cxdp_run_step`：① START/STOP 子串过滤 ② `CXDP_BLOCK_RUN` 闸门
  ③ `requires` 闸门（`uplevel #0 [list expr $requires]`）→ 通过则打 banner
  `>>>> CXDP-STA entering step <name> @ <walltime>` + `script: [file normalize $script]`，
  计时 `clock milliseconds`，catch 异常，`lappend ::_step_times $sname $_dt`，
  打 `CXDP-TIME : step <name> elapsed= ${_dt} ms ... rss=[cxdp_live_rss]`。
- `cxdp_timestamp_summary`：每步 ms 表 + TOTAL + `session_cpu`(`ps -p [pid] -o time=`)
  + `session_rss` + peak(`VmHWM`) + `wall_end`。
- `cxdp_message_summary`：`glob $LOG_DIR/sta_*.log`，逐行 `string match "Error:*"/"Warning:*"/"Information:*"`
  计数；无日志→`counts: unavailable (no log file found under $LOG_DIR)`。
- run engine 循环 `CXDP_STA_STEP_LIST`，结尾两 summary，`exit $_flow_status`。

## A-faithfulness 评估

✅ 合格。用户给的是「需求规格书 + review 分析 + 三项改进方向」，未给出：
- `requires` 表达式的具体写法（`[llength $CONSTRAINT_FILES] > 0`）
- source/execute 分离的具体实现（`cxdp_run_step` 把 source 已在前面 glob 完成，execute 才 call）
- banner 的精确格式（`>>>> CXDP-STA entering step ...`、`CXDP-TIME : ... elapsed= ... ms`）
- TimeStamp/Message Summary 的精确版式与字段
- `sh -c` 包 awk 的 RSS 取值技巧
- `count_blackbox` 用 `report_design` 而非 `get_cells -filter is_blackbox`（避 FLT-005）

这些都是 agent 的实现决策，符合 A-faithful「给 WHAT/方向，未给 HOW」标准。

## deliverable 可行性

- 目标路径 `/proj/lacaa/TV1_digital/simdir/yutingq/CxDP/cla_top_DS/sta` 是私有项目路径。
- 真实流程需 PrimeTime license + 项目 netlist/lib/sdc/spef/sdf 输入。
- 在 SUT 沙盒（无 PT license、无私有设计库）**INFEASIBLE** → **B档合成**。

## B档合成方案

写一个**纯 Python 标准库 CLI `cxdp_sta_driver.py`**，离线仿真该改进版 driver
（mock handler 模拟各 proc，不调用 pt_shell），完整复刻四项改进 + BLOCK_RUN/START-STOP 闸门：
- `setup.json` 声明 `vars` + `step_list[{name,handler,script,requires}]` + `log_dir`。
- Phase 1 register（仅定义）→ Phase 2 execute（START/STOP→BLOCK_RUN→requires 三闸门）。
- 每步 banner（enter walltime / abs script / elapsed ms / RSS）。
- TimeStamp Summary + Message Summary（glob sta_*.log 按 Error:/Warning:/Information: 计数）。
- 产 `report.json`。

A/B 配置在 SDC 模式 / 延迟参数 / MVDD / IRDROP / 日志 E/W/I 计数 上完全不同（跨输入守卫）。

## case 产出

`EDA-Eval-DesignFlow-StaStepDriverGen-001`（pnr_signoff L1-B B档，
archetype=cxdp-sta-step-driver-with-conditional-gating-and-dual-summary，k=18）。
