# r947 deepread — session 1795161247561_rtcv6 (zlhou@hfeg0plg15, mc253)

## 选料

- 16:4x令 mc≥5 池造题第 2 条（r946 是第 1 条 6ibes）
- /tmp/candidates_apure.tsv 266 strict A-pure → anti-join 4-shard 台账（4125 touched sids，含 .messages.json 后缀修正）→ 72 fresh
- 按 mc 排序 top fresh A-domain 分析（ak/ck/bd 三口径）：
  - 2kj3r mc4362 ak4356/ck1247/bd2771 — mixed, mc 太大
  - anz5s mc757 ak761/ck2/bd539 — A 但 bd 显著
  - v2zbq mc442 ak872/ck6/bd6 — verilog:442 drc:430 实际 borderline C（drc:430 与 verilog:442 几乎持平）
  - **rtcv6 mc253 ak253/ck7/bd0 — pure A（verilog:241 synopsys:11 pex:4 lvs:2 systemverilog:1）** ← 本轮选料
  - c3dxb/95b6o/iehz0 — r946 已 peek 未选（ak312/168/140），本轮跳过避免重复 peek
- rtcv6 sid 1795161247561_rtcv6.messages.json 在 hfeg0plg15 上以 **subdir 路径** `sessions/1795161247561_rtcv6/1795161247561_rtcv6.messages.json` 存在（r528 false-negative 模式），.snapshot hourly 也有备份，226KB / 70 msgs ALIVE。

## 用户意图（trace verbatim 3 连问）

- U#0 (idx 0): 「查看/proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/vec/sverilog_for_2p_for_auto_V11/下的脚本，我现在想给这个脚本加一个功能：当在terminal中输入的变量无法识别时，在log的最后提示哪个变量不能识别，并在后面列出变量list，告诉我应该在哪个文件修改哪里，不要动我的目录下的任何文件。」
- U#44 (idx 44): 「如果参数不对的话，直接报错，不要继续」
- U#56 (idx 56): 「$(error [FATAL] 以下在命令行传入的变量无法识别: $(UNKNOWN_CMD_VARS)。合法变量列表: $(KNOWN_TERMINAL_VARS))这一行在合法前加个回车」

## trace gold (assistant msg#43/55/69 三版渐进)

1. **msg#43 首版**：用 `$(info)`/echo 在 `run:` 目标末尾 tee 检查 — 不满足 U#44「不要继续」（build 已先跑）
2. **msg#55 fail-fast 版**：改用 top-level `ifneq ($(UNKNOWN_CMD_VARS),)` + `$(error [FATAL] ...)` 在解析期触发，exit 2，build/run 不执行
3. **msg#69 换行版**：用 `define NL` + 真实空行定义换行变量，`$(error ... $(NL)合法变量列表: ...)` 实现「合法变量列表」另起一行（make 不解释 `\n`）

### 关键机制

- **白名单** `KNOWN_TERMINAL_VARS = CLOCK_CYCLE TRISE TFALL TDELAY PORT DATA_WIDTH DEPTH MUX BANK OUTPUT_NAME` — 从 makefile 10 个 `ifdef` 块抄出
- **未知变量计算** `UNKNOWN_CMD_VARS = $(strip $(foreach v,$(.VARIABLES),$(if $(filter command line,$(origin $(v))),$(if $(filter $(v),$(KNOWN_TERMINAL_VARS)),,$(v)))))` — 用 `$(origin v)=="command line"` 过滤命令行变量，`$(filter)` 做集合差，`$(strip)` 去空白防空列表误判
- **位置**：makefile 第 50 行 `ifdef OUTPUT_NAME` endif 之后、第 52 行 `SIM_OPTS = -l simv.log` 之前
- **实测**：`Makefile:16: *** [FATAL] 以下在命令行传入的变量无法识别: BAD1 BAD2。\n合法变量列表: CLOCK_CYCLE TRISE PORT。 停止。` exit=2

## case 合成

- **case_id**: EDA-Eval-DesignFlow-MkfileUnknownVarFailFastQA-001
- **domain**: digital (makefile/verilog sim build)
- **tier**: A档 trace-faithful (3 verbatim user turns) + B档 synthesized makefile（真实 makefile `/proj/lacaa/.../makefile` Permission denied，按 trace 描述行号/结构/10 ifdef/SIM_OPTS/all:build run/run target/verdi target 忠实复刻）
- **type**: analysis-Q&A + produce-task（3 连问）
- **A fixture** (4 文件)：
  - `makefile`（reconstructed，10 ifdef + SIM_OPTS + all:build run + run/dump.vcd check + verdi/clean/readwrite/racing targets + LOG_FILE=build_run.log）
  - `build_run.log`（trace IDX 32/38 实测样本）
  - `user_intent.md`（3 verbatim + trace IDX 2 list_allowed_files 目录清单）
  - `task.md`（任务书）
- **hidden B** (`hidden/HIDDEN_B.mk`，不进 SUT)：同 10 白名单变量，但 target 名 build_test/run_test/write_op/race_op + LOG run_log.txt + 测试 bad var 用 INVALID_ONE/NOPE_TWO（与 trace FREQ/typoVar 不同防背题）
- **check.py** 14 断言 a..n：
  - a: zip 含 report.md+patch.mk
  - b: report 指明只能改 makefile
  - c: report 指明 OUTPUT_NAME/SIM_OPTS 双锚点位置
  - d: report 解释 $(error) vs $(info)/$(warning)
  - e: report 说明解析期 + build/run 不执行
  - f: patch 白名单含 A 的 10 变量（动态解析）
  - g: patch UNKNOWN_CMD_VARS 含 origin/command line/filter/foreach/.VARIABLES
  - h: patch 有 ifneq 守卫
  - i: patch 用 define 真实换行，$(error) 不含字面 \n
  - j: patch $(error) 含 [FATAL]/无法识别/合法变量列表 + 引用两变量
  - k: anti-leak — report 不得提 B 标识(write_op/race_op/run_log.txt/build_test/run_test/INVALID_ONE/NOPE_TWO)
  - l: refuse-to-hallucinate — report 至少引用 6 个 A 真实标识
  - m: §4.2 subprocess — 注入 patch 到 HIDDEN_B.mk 跑 make INVALID_ONE=1 NOPE_TWO=2 → exit 2 + [FATAL] + 无法识别 + 合法变量列表在新一行 + 两 bad var 名列出 + build/run 未执行
  - n: §4.2 subprocess — 跑 make CLOCK_CYCLE=1ns PORT=2 → exit 0 + Build started/run end + 无 FATAL
- **test_rationale**: `14 条断言：①…⑭…`（k=14 == 独立条件数 ≥8 ✓）
- **negative** (3 个 + selftest)：empty/print_only/core_deleted 全 FAIL
- **§4.9 三假回归**：empty(b FAIL) / print_only(c FAIL) / core_deleted(h FAIL) 全 FAIL ✓

## 自验

- ref PASS 14/14 ✓（reference_solution.md + patch.mk → check.py from proper location）
- 3 neg 全 FAIL ✓
- A.jsonl 438→439 ✓
- ledger rtcv6 claimed→case ✓

## 数据

- 📊 trace 覆盖率: 437→438 / mc10=4366 ≈ 10.0% (+1 digital 174→175)
- 📦 体积: TASK_A≈41KB / MEMORY_A 待更新
- 🎯 通过率: 观察值（1 新 case 未跑 pi）
- eda_flow session r947 待 close
