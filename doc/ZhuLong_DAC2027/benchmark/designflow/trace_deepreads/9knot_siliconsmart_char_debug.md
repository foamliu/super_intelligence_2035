# 深读 trace 记录：9knot（SiliconSmart 库表征配置调试 · .inst/.tcl 错误修复）

> 即时令 IX §五 要求：本轮先深读 1 条真实 trace，理解完整对话流，下一轮提炼成 case。本文件为脱敏深读笔记。
> 原始 messages.json 4.0MB / 655 msgs / 352 user / 303 assistant / 51 editor / 139 read_files / 37 run_approved_command / 307 tool_result，
> 已 scp 到 .75 workdir 解析后 close_session keep=false cleaned（不入库，不入 git）。
> 与已用的 ukkn7（hfeg0plg91 / e0031668 / ERC-aether）和并行 agent 的 m2vah（hfeg0pkn001 / e0014566 / rscalc-autovia）**无交集**（不同用户 vincelu / 不同主题 SiliconSmart 表征 / 主机 hfeg0plg49），避免冲突。

## trace 来源（脱敏）
- host: `hfeg0plg49`（10.129.8.86；同 session 亦出现在 hfeg0plg100 / hfeg0plg55 等，NFS 共享 home）
- user_hash: `sha1[:12] of "vincelu"`（real user vincelu，建 case 时 hash）
- session_file: `1792297573507_9knot`（实际路径 `<ip>:/home/vincelu/.cline/data/sessions/1792297573507_9knot/1792297573507_9knot.messages.json`，4,194,140 字节；另有 `.messages.archive.json` 5MB 不读）
- session_msgs: 655
- summary.tsv match_count: **862**（dedup 后该 session 排名第 5，仅次于 ukkn7 1478 / x4b0p 1367 / m2vah 975 / 82ybr 878）
- keywords: `cmos:5640;netlist:4613;analog:938;.cdl:879;hspice:494;schematic:266;synopsys:163;mixed-signal:19`
- tool_use 分布: read_files 139 · list_allowed_files 58 · editor 51 · run_approved_command 37 · search_codebase 16 · run_commands 4 · RAG search 2
- real_task_summary: SiliconSmart 库表征（characterization）配置调试——跑 drgqx 5 个库的 `.tcl`/`.inst` 配置，逐类修复 configure/characterize/model 阶段报错至全 tasks 成功

## 用户真实目标（45 条 user message 提炼）
用户手头有一个 **Synopsys SiliconSmart 库表征流程**，工作目录 `/rundata/drgqx/V0_20261007/simdir/verilog/workdir/vincelu/tt_25_1017/`：
- 5 个库：`drgqx_cmos_analog`(33 cell) / `drgqx_cmos_digital`(180) / `drgqx_cmos_io`(154) / `drgqx_cmos_stdcells`(359) / `stdcells_ac`(678)
- 编排：`export/drgqx_cmos_*.tcl` + `stdcells_ac.tcl`（含 `model`/`qualify_library`/`set_config_opt`）；每 cell 一个 `sisregular/<lib>/control/<cell>.inst`（含 `add_pin`/`add_latch`/`add_flop`/`add_function`/`add_forbidden_state`/`set_netlist_file`/`cut_netlist`/`set_config_opt`）；全局 `sisregular/configure.tcl`
- **核心需求**：跑 SiliconSmart 表征，**解决所有 error 且不影响结果**（不允许"避开"）
- **关键纠偏**（USER #28 idx 517）：用户明确"之前说的遇到 error 避开是不合理的方案，是要解决所有的 error 且不影响结果"——agent 早期提的"把无 PEX 的 cell 从 list 移走/注释 qualify 跳过"被否，要求**彻底修复**
- **真实工作流**：`bsub -I -q interactive siliconsmart ./export/<lib>.tcl` → 跑出 error → 把 error 原文贴给 agent → agent 诊断根因 + 改 `.inst`/`.tcl`/`configure.tcl` → 重跑 → 新 error → 迭代

## agent 工作过程（51 editor + 37 run_approved_command）
1. **库内容核验**：读生成 Liberty（33 cell，9007 行，pg_pin/function/timing arc 正确）
2. **第 1 类 lc_shell 权限**：`qualify_library` 调 lc_shell 报 `Operation not permitted` → 注释 5 个 `.tcl` 的 `set_config_opt qualification_lc_shell` + `qualify_library` 行
   - **真实陷阱**（idx 510）：首次用 `...  # disabled: ...` 行**尾**注释 → 命令仍执行！必须改行**首** `#` 才真注释
3. **第 2 类 -verilog all 建模缺失 PEX**：analog 库 10 cell 无 PEX 目录 → SMSC-99 → `model -create_new_model -verilog all` 改 `-timing $cells`（只建模有 character 数据的 cell）
4. **第 3 类 add_latch 语法 + ^ 非法**（`ffrqIOLVx2_pc60_odt.inst`）：
   - `add_latch Q {} Ck D -clear {!RN}` → `{}` 被当负寄存器名、`Ck` 当 enable、缺 data_expr → 改 `add_latch Q Ck D -clear {!RN}`
   - `add_forbidden_state { !(Ck ^ CkN) }` → `^`(XOR) 在 Liberty 布尔表达式非法 → 改 `{ ((!Ck) & CkN) | (Ck & (!CkN)) }`
5. **第 4 类 ^ 在 add_function**（`T_CompXor.inst`/`AF_FsPPRTokenSel.inst`）：同上，`^` → `&`/`|`/`!`
6. **第 6 类 网表名不匹配**（`nor3IOLVIOx1_DQS.inst`）：`set_netlist_file`(L7) + `cut_netlist`(L33) 指向旧名 `nor3IOLVIO_1p6.spf_RC`（实际 `nor3IOLVIOx1_DQS.spf_RC`）→ 全部更正
7. **第 5 类 缺失 .inst**：`R_SrefRateLookUpTable42t58.inst`/`IO_VrefDqGenV3_cvps.inst` 缺失 → 参考同 pinout cell 恢复
8. **第 7 类 vssFoot 重复**（`configure.tcl`）：dup 定义 → 重命名 `__param_VSSFOOT`
9. **IO 库一组**（第 8 类 a-d）：
   - `IO_capbuf_vrefdq_anti_kb.inst` 端口不匹配
   - `IO_FFEDRV.inst` enable pin 卡死
   - `IO_DqSlicerHflatrnf_typeA.inst` pass-gate 关断
   - `IO_TX_LOCAL_DCA_DQS.inst` forbidden state 冲突 + `default_input_state` 未定义（PARA-7）→ 加 `set_config_opt -opcond __default__ -- default_input_state { DP1_per_0 1 DN1_per_0 0 ... }`；并修 bachIn ParseError（`DP1_per<0> == 0 || DP1_per<1> == 0` 的 `<`/`||` 非法 → 用 `|`/`&`/`!`）
10. **invYx2_CoM.inst**：2.75V(vwlp) 供电反相器，输入 pin 用 `default` pintype（0.94V 阈值，幅度不够触发翻转）→ `add_pin A/Y default` 改 `vwlp_type`（VDD/2≈1.375V 阈值参考）
11. **verilogFind.log 清理**（USER #32 idx 557）：根据 verilogFind.log 把不需要的 cell inst 移走
12. **总结**（USER #19/#20 idx 436/438）：agent 出 12→16 类 error↔fix 对照表 + 全库成功率（analog 100% / digital 100% / io >99.5% / stdcells ~100% / stdcells_ac >99.9%）

## 最终状态
trace 在"IO 库重跑 + set_config_opt 作用解释"处接近收尾（USER #45 idx 654 问 `set_config_opt` 各作用）。16 类问题全修复，5 库表征跑通至 ~100% tasks 成功。交付 = patched `.tcl`/`.inst`/`configure.tcl` + fix 总结。这是一个**真实、hard、多步调试 + 跨文件配置修复**任务，天然有区分度。

## 关键文件/产物（路径含真实用户名，建 case 时脱敏 <USER>）
- 工作根：`/rundata/drgqx/V0_20261007/simdir/verilog/workdir/<USER>/tt_25_1017/`
- 编排：`export/drgqx_cmos_analog.tcl` / `..._digital.tcl` / `..._io.tcl` / `..._stdcells.tcl` / `stdcells_ac.tcl`（含 `model`/`qualify_library`/`set_config_opt qualification_lc_shell`）
- 全局配置：`sisregular/configure.tcl`（`vssFoot` dup 等）
- 每 cell：`sisregular/<lib>/control/<cell>.inst`（`add_pin`/`add_latch`/`add_flop`/`add_function`/`add_forbidden_state`/`set_netlist_file`/`cut_netlist`/`set_config_opt`/`add_switching_set`）
- 网表：`netlists/<cell>.spf_RC`（PEX 后仿）/ `.cdl`（前仿）
- 工具：`bsub -I -q interactive siliconsmart ./export/<lib>.tcl`（LSF 集群）
- 运行产物：`sis.log` / `deck.lis` / `cell.stat.gz` / `models/liberty/*.lib`

## 可提炼的 design_flow case 方向（下一轮）
**case 主题**：SiliconSmart 库表征配置调试——修复 `.tcl`/`.inst` 配置错误使表征跑通
- **metadata.domain**：characterization（新建子向）或归 digital（库表征是数字标准单元/IO 为主，含 analog 库）。建议 `metadata.domain: "characterization"`，与 Verification-001(analog/ERC) 错开，扩 benchmark 域覆盖。
- **prompt**（自然语言任务目标，反映真实场景）：
  给定 drgqx 项目的 SiliconSmart 库表征配置（5 个 `export/*.tcl` 编排脚本 + 若干 `sisregular/<lib>/control/<cell>.inst` cell 配置 + 全局 `sisregular/configure.tcl`）与一份表征运行 error 摘要（`sis.log`/`deck.lis` 摘录）。任务：诊断每个 error 的根因并修复对应 `.tcl`/`.inst`/`configure.tcl`，使表征能跑通且结果不受影响（不允许仅"避开"——例如不能只把报错 cell 从 list 删除了事）。需修复的典型问题包括：(1) `qualify_library` 调 lc_shell 权限错；(2) `model -verilog all` 建模无 PEX 的 cell；(3) `add_latch` 语法错 + `add_forbidden_state`/`add_function` 中 `^`(XOR) 非法；(4) `set_netlist_file`/`cut_netlist` 网表名不匹配；(5) `default_input_state` 参数未定义 + bachIn 表达式 `<`/`||` 非法；(6) vwlp 供电 cell 输入 pin pintype 用错；(7) `vssFoot` 重复定义。交付：所有 patched `.tcl`/`.inst`/`configure.tcl` + 一份 fix 总结（每个 error → 根因 → 修复），打包 `outputs/submit.zip`。约束：不改 cell 接口/网表本身，只改表征配置；注释必须是行首 `#`（行尾注释命令仍执行）。
- **attachments**（合成/脱敏，因真实 .inst/.tcl/PEX 为私有）：合成的 5 个 `export/*.tcl`（含 `qualify_library` + `set_config_opt qualification_lc_shell` + `model -create_new_model -verilog all`）+ 带缺陷的 `<cell>.inst`（ffrqIOLVx2_pc60_odt.inst 含 `add_latch Q {} Ck D` + `^`；nor3IOLVIOx1_DQS.inst 含错网表名；invYx2_CoM.inst 含 `default` pintype；IO_TX_LOCAL_DCA_DQS.inst 缺 default_input_state + 含 `<`/`||`；T_CompXor.inst 含 `^`）+ `configure.tcl`（含 vssFoot dup）+ 一份 `errors.txt`（真实 error 摘录脱敏），入 `assets/<task_id>/`
- **entry_point**：`outputs/submit.zip`
- **test**（Python 双参 `check(deliverable, workdir)`）：解 zip → 断言（每条独立有牙，buggy 原件提交必 FAIL）：
  (a) 5 个 `.tcl`：`set_config_opt qualification_lc_shell` 与 `qualify_library` 在**行首** `#` 注释（行尾 `# disabled` 不算！正则 `^\s*#.*(qualify_library|qualification_lc_shell)`，且无未注释的同名行）；`model` 用 `-timing $cells` 而非 `-verilog all`；
  (b) `ffrqIOLVx2_pc60_odt.inst`：`add_latch` 无空 `{}` 寄存器名（正则 `add_latch\s+\S+\s+\S+\s+\S+`，禁 `add_latch\s+\S+\s+\{\}`）；`add_forbidden_state`/`add_function` 不含 `^`；
  (c) `nor3IOLVIOx1_DQS.inst`：`set_netlist_file` 与 `cut_netlist` 均指向 `nor3IOLVIOx1_DQS.spf_RC`（不含旧名 `nor3IOLVIO_1p6.spf_RC`）；
  (d) `invYx2_CoM.inst`：A/Y pin 用 `vwlp_type`（不含 bare `add_pin\s+(A|Y)\s+default`）；
  (e) `IO_TX_LOCAL_DCA_DQS.inst`：含 `default_input_state` 定义；bachIn 表达式不含 `<`/`||`（用 `|`/`&`/`!`）；
  (f) `configure.tcl`：`vssFoot` 不重复定义（计数 ≤1 或重命名为 `__param_VSSFOOT`）；
  (g) fix 总结文件存在且逐 error 列出根因 + 修复。
  参考 `docs/rtl_design_flow_case_design.md` §3 的脚本交付件 test 写法 + Verification-001 的 4 条件独立有牙范式。
- **test 语言**：Python（全本地判分，校验脚本/配置产物，不强求真跑 SiliconSmart——规避无 license/无集群的 block，与 Verification-001 同策略）
- **metadata.trace_source**：见本文顶部 trace 来源块（host hfeg0plg49 / user_hash / session 9knot / 655 msgs / real_task_summary）
- **难度**：hard（多步调试 + 跨 5 库多文件配置修复 + 真实陷阱：行尾注释无效/`^`非法/网表名漂移/pintype 阈值/参数未定义）
- **资产缺口**：真实 .inst/.tcl/PEX/sis.log 是 vincelu 私有；建 case 时用等价合成资产（照真实结构仿造：.tcl 嵌入 qualify+model 行，.inst 嵌入真缺陷语法，errors.txt 用脱敏 error 摘录）。test 校验产物结构 + 各 fix 落地，可全本地 Python 跑。

## 备注
- 本 trace 真实跑通依赖 SiliconSmart license + LSF 集群（agent 调 run_approved_command 37 次大半在 bsub 跑表征）；pi 被测若真跑会撞无 license/无集群 block。**判分用产物校验（Python 本地）规避**：test 只校验 zip 内 patched 脚本/配置，不强求 pi 真跑 SiliconSmart。
- 即时令 IX §三.3：prompt 里可有真实文件名/工具名/库名（SiliconSmart / drgqx_cmos_analog / ffrqIOLVx2_pc60_odt / add_latch / qualify_library / vwlp_type），但脱敏真实用户名/路径（<USER> 占位，vincelu→hash）。
- **下一轮**：照本节"可提炼的 design_flow case 方向"合成 assets（5 .tcl + 5 .inst + configure.tcl + errors.txt）+ 写 prompt + 写 Python 双参 test（7 条件独立有牙）+ 入 `EDA-Eval-DesignFlow.jsonl`（追加，不建新文件）+ pi 调试。case id 建议 `EDA-Eval-DesignFlow-Characterization-001`。
