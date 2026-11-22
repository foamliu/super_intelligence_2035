# r1071 — junxu @ hfeg0pkn005 — FineSim block-sim SKILL: .mt0.csv results parser + Python 3.6 compat + nlchk suppress

**trace**: 1789374352756_57i4y / junxu / hfeg0pkn005 / mc=161 / 155 msgs / 467KB
**keywords**: netlist:821;virtuoso:203;hspice:184;schematic:117;cmos:44;cadence:7;cellview:5;maestro:2
**domain**: spice_sim (B shard) — FineSim block-level simulation SKILL (virtuoso-cli bridge)
**scan**: ssh_eda_search_20261123_064315/summary.tsv (fresh_Bspice_r1050.tsv, cross-4-shard-ledger 全 NONE ✓)
**access**: expect+password scp e0031982@hfeg0pkn005 → /home/junxu/.cline/data/sessions/1789374352756_57i4y/ (messages.json 467KB/155msgs, tool_results 已 context-compressed 为空, 但 assistant text+tool_use 完整; 实物脚本 extract_results.py 经 scp 取得 4550B 完整源码)

## 真实工作场景
junxu 在构建 `block-sim` SKILL（Cadence virtuoso-cli bridge 驱动 FineSim block-level 仿真），SKILL 目录 `/home/junxu/.cline/skills/block-sim/`，含 5 个 Python 脚本 + SKILL.md + references 模板。本 session（压缩后 155 msgs）覆盖：SKILL.md 文档完善、FIFO 3x8 仿真目录清理、Python 3.6 兼容性修复、nlchk.rpt 弹窗抑制、git 仓库初始化。

## 5 个 user 任务

### Task 1 (U0, msg 0-13) — SKILL.md 文档完善（.meas 点号 + 前台运行强调）
- `.meas inference` 段落加 blockquote：`.meas` 必须以点 `.` 开头否则 FineSim 静默跳过
- Stage 5 加 blockquote：必须用 `run_simulation.py` 经 `bsub -K` 前台运行，禁止手动后台 LSF

### Task 2 (U14, msg 14-31) — FIFO 3x8 仿真目录清理
- 删除 /tmp 下所有 fifo_3x8 相关目录（simrun_junxu_fifo3x8 ~110MB + 多个空 netlist 目录）和辅助脚本/日志
- 纯 rm -rf 清理，无 reframe 价值

### Task 3 (U32, msg 32-107) — Python 3.6 兼容性 ✅ 选作 reframe 的 sister task（extract_results.py 为载体）
- 5 脚本 py_compile + 实跑验证
- 发现 `run_simulation.py` L67/94 用 `capture_output=True, text=True`（3.7+）→ 改回 `stdout=PIPE, stderr=PIPE, universal_newlines=True`
- 删 `gen_control.py`/`gen_stimulus.py`，改用 `references/control-template.md`/`stimulus-template.md` 模板
- 教训：py_compile 只查语法不查运行时；--help 在 subprocess.run 前退出

### Task 4 (U108, msg 108-138) — nlchk.rpt 弹窗抑制
- `extract_netlist.py` 加 `SUPPRESS_NLCHK = 'envSetVal("asimenv.envOpts" "viewNLCheck" \'boolean nil)'`
- 在 `cxmt_SchmaticTool_Dsim_SpiceOut`（内部 `createNetlist(?display nil)`）前执行
- `?display nil` 只抑制 netlist 内容显示，`viewNLCheck` 才控制 nlchk.rpt 弹窗

### Task 5 (U133, msg 133-154) — git 仓库初始化
- `git -C /home/junxu/.cline/skills/block-sim init` + .gitignore(__pycache__/*.pyc) + initial commit

## reframe 选 extract_results.py（FineSim .mt0.csv 测量结果解析器）
**选作理由**：
- extract_results.py 是 5 脚本中唯一「纯文件解析 + 结构化 JSON 输出」脚本，无 virtuoso-cli/LSF 依赖，L1 可独立验证
- Task 3 的 3.6 兼容性、Task 4 的 nlchk 抑制都依赖运行环境（py36/virtuoso），无法在 SUT 沙盒闭环验证
- .mt0.csv 格式有真实测试数据（msg 53 assistant 造的 mock CSV：`.TITLE 'tt_25c_0.9v'`/`$DATA1`/`tdelay`/`1.234e-09` 和 `error`），格式明确

**真实 extract_results.py 行为**（scp 取得 4550B 源码）：
- glob `finesim#*.mt0.csv`（fallback `finesim.mt0.csv`）
- 逐文件解析：`.TITLE '<corner>'` → corner；`$DATA1` → data marker；首非注释非 header 行=列名；次行=值
- 值分类：float → `{value:num, status:ok, negative:num<0}`；`error`/`failed` → `{value:val, status:val.lower()}`；其他 → `{value:val, status:unknown}`
- 输出 JSON：`[{corner, measurements:{name:{value,status,[negative]}}, file}]`
- 非 --json 模式打印人类可读表格（⚠️ emoji 标负值）

**reframe**: `finesim_mt0_parser.py <sim_dir> <out_json>`，递归 glob finesim#*.mt0.csv，解析 corner/列名/值，分类 ok/negative/error/failed/unknown，emit JSON report{files_scanned, files_parsed, corners:[{corner,file,measurements}], summary:{n_ok,n_error,n_failed,n_negative,n_unknown}}。L1 纯 Python。

## case 设计（k=12 a-l）
- **A**（junxu 真实 mock 数据采样）：2 文件 finesim#0/#1.mt0.csv，1 列 tdelay，corners tt_25c_0.9v(=1.234e-09 ok)/ss_-40c_0.88v(=error)
- **hidden B**（五重 anti-hardcode）：①4 文件异 A 2 ②4 corner 名 ff_125c_1.1v/tt_-40c_1.0v/ss_85c_0.9v/tt_25c_1.0v 异 A ③3 列 tdelay,trise,tfall 异 A 1 列 ④混合状态 ok+负值+error+failed（A 仅 ok+error）⑤含 negative 值（-3.0e-09）测 negative flag（A 无负值）
- **check 12 条**: a(zip+compile+size) b(B exit0+非空JSON) c(顶层键⊇{files_scanned,files_parsed,corners,summary}) d(scanned==4) e(parsed==4) f(len corners==4) g(每 corner 键⊇{corner,file,measurements}) h(anti-hardcode B corners 在场/A corners 缺席) i(每文件 3 meas: tdelay,trise,tfall) j(ff_125c 全 ok 非 negative) k(tt_-40c tdelay negative==True) l(ss_85c tdelay status==error + tt_25c trise status==failed) m(summary 计数正确) n(3-seed sha256 一致)
- **3 negs**: neg_empty(空壳→a/b) / neg_print_only(硬编 A report 不读 B→d/h/i/j/k/l) / neg_no_classify(解析但跳过 error/failed/negative 分类→j/k/l)
