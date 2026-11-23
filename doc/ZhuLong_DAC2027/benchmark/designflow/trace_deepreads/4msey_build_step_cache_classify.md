# Deepread: 4msey — stdcell_web build_step cache/reload 架构判定

- **trace**: chapinc @ hfeg0pkn002, session `1795172721372_4msey.messages.json` (411 msgs / 801KB active + 8.6MB archive)
- **scan match_count**: 5 (spice 口径), 但 hspice:679 / netlist:1522 (高活跃)
- **project**: `/home/chapinc/AIforstdcell/` + `/home/chapinc/stdcell_web/` — 标准单元尺寸表征 Web 服务
- **agent**: lead (zhulong)

## 会话流

- msg[0]: Context summary — 之前在改 index.html 静态路径（❓/🔗 改成服务静态路径）
- msg[8] USER: "你看一下现在在运行的网页，为什么不出图一直卡在这" — 网页不出图
- msg[9] ASSISTANT: 诊断服务状态/日志
- msg[63]/[326]: "继续任务" (plan mode)
- msg[348] USER: "是的，按你说的改"
- msg[399] USER: "模板你不是每次都调用我文件夹里都现改吗，你说的监控是什么意思"
- msg[400] ASSISTANT: 读 `engine.py` `build_step` (line 260) 确认模板用法
- msg[410] ASSISTANT: **核心架构判定**（最终答案）

## msg[410] 核心判定（reframe 来源）

agent 读 `engine.py` 第 260 行 `build_step` + 顶层 import，区分两类文件：

**1. 仿真模板（`netlist_sp/*.sp` 和 `*_netlist`）—— 不缓存，现改现用**
- `engine.py:271` `with open(os.path.join(TEMPLATE_DIR, sp_name)) as f:` — 每次提交现场读模板
- `engine.py:273` `with open(os.path.join(TEMPLATE_DIR, nl_name)) as f:` — 每次提交现场读 netlist
- `engine.py:277/346` 把生成的带参数 `.sp` 写进项目目录
- `TEMPLATE_DIR = netlist_sp/`，`build_step` 每次"提交仿真"那一刻才从文件夹读，不进内存
- 改模板 → 下次提交自动生效，跟服务重启无关

**2. Python 模块（`engine.py / app.py / mt0_parser.py`）—— 启动时进内存，改了不重启用不上**
- `engine.py:23` `from mt0_parser import parse_mt0, corner_label` — 进程启动时一次性载入
- 进程只在启动那一刻把 `engine.py` 读进内存一次；运行中改代码但服务没重启 = 执行的还是内存里旧代码（上次"卡住不出图"根因）

**3. 边界**: 改模板后，已在跑的作业不受影响（用提交那一刻生成的 `.sp` 副本），新提交才用新模板 — 即"现改现用"

## reframe

把"代码理解 → 缓存/重载行为判定"程序化 → `build_step_cache_classifier.py <engine_src.py> <spec.json> <out.json>`，Python AST 静态分析，按 spec 列出的每个 artifact 分类：
- `fresh_per_submit` (open in target fn 读 template_dir) → effective_on_next_submit
- `written_per_submit` (open(...,"w") in target fn) → snapshot_per_job
- `startup_loaded` (module-level import / 模块级 open(startup_config)) → requires_process_restart
- `locked_persistent` (open(persistent_var) + fcntl.flock 锁) → persistent

L1 纯 Python 标准库 ast，无 EDA 依赖。domain=characterization (stdcell 表征引擎)。

## near-dup 自查

对照已有 case：
- ProbeCovAnalyzerProduce-001 (r1066) — FineSim .probe 语句覆盖分析器（判 OP 参数可恢复性），结构相似（静态分析 + verdict）但对象完全不同（.probe 语句 vs build_step 缓存行为）
- CornerBlockGenProduce-001 (r1074) — FineSim corner 块 .lib/.alter 生成器（生成器，非分析器）
- SubcktUnclosedDiagProduce-001 (r1073) — .SUBCKT/.ENDS 未闭合诊断器（语法诊断，非缓存行为）
- Mt0CornerPivotAggregate-001 (r1079) — .mt0 多 corner 列透视聚合器（数据聚合，非代码结构分析）
无 near-dup：本题是唯一对"Python 源码 artifact 缓存/重载行为"做 AST 静态分类的 case。

## A / hidden B 设计

**A** (chapinc 真实结构): engine_A.py 忠实节选（imports + 常量 TEMPLATE_DIR/REGISTRY/TIMING + build_step + LSF + _locked helper），spec_A 11 artifacts（3 sp 模板 + 3 netlist 模板 + 2 生成件 + mt0_parser 模块 + registry/timing 持久态）。

**hidden B** (7 重 anti-hardcode): ①函数名 run_sim_step ②模板目录变量 SIM_TPL_DIR ③多一类 lib_template (corner.lib) ④artifact 名全换 ⑤生成件后缀 _deck.sp/_nl ⑥多一个 startup_config 类 (run_config.yaml 在 import 时读一次) ⑦持久态换 jobs.json/stats.json。

## 判分

check.py 12 条 (a-l): zip完整性 / B运行 / 顶层键精确 / n_artifacts==11 / 字段齐全 / cache_class==oracle / reload_verdict+verdict_map==oracle / by_class分组 / evidence_line指向真实open/import/lock行 / target_function==B / anti-hardcode(A名+build_step+TEMPLATE_DIR全缺席,B名全在场) / 3-seed sha256一致。

自验: REF 12/12 PASS ✓, 3 negs (empty/print-A/naive-all-fresh) 全 FAIL ✓, §4.9 三假齐 ✓, 3-seed 确定性 ✓ (条件 l)。
