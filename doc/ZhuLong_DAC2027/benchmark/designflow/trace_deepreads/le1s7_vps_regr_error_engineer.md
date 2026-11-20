# Deepread: le1s7 — VPS/UVS 回归错误编排（verification, L2 候选）

## trace_source
- user: jason17w  · host: hfeg0pnd002 (10.129.32.190)  · session: 1791941227075_le1s7
- mc=310 (summary.tsv keywords)  · 742 msgs  · 2.84 MB messages.json
- scp'd to .75 session workdir (shardA_20261104-runA59-scan)
- tool histogram (cline): run_approved_command 123, editor 109, read_files 61, ask_question 22, list_allowed_files 21, search_codebase 5
- domain: **verification**（VPS = Verification Productivity System, UniVista；UVS = UniVista Simulator, vsim 内核）

## 真实任务流（user 意图逐轮）
1. **#0** 创建 vps-cli skill（基于 VPSUserGuide.pdf 深入学习 VPS CLI）— meta-tooling，但贯穿全 session 提供 VPS CLI 知识。
2. **#314**「[vps-cli] 帮我用vps跑 ./run_script_uvs/run_step1_bk。使用uvs，有不明白的地方先问我，这轮测试的目的是测试 verilogrun 文件是否可以保留。」— **clean 提需求**，A档②合格。
3. **#435**「把这5个case的verilogrun中的 -noerror 120343 去掉，并且把 -v libs/simlib_base.sv 换成 -v libs.bak20260416/simlib_base.svp。做一份verilogrun的备份。」— 用户给出根因+修复方案 → A档②**禁用**（可作 hint）。
4. **#461**「[vps-cli] 帮我用vps重跑一遍 ./run_script_uvs/run_step1_bk。使用uvs工具，使用目前上一轮目录中遗留的verilogrun脚本（更改了 -noerror 和 -v libs.bak20260416/simlib_base.svp），有不明白的地方先问我，这轮测试的目的是测试这版本verilogrun文件是否可以让 UVS 报错。」— **clean 提需求**，A档②合格。
5. **#505/#547/#561/#579** 用户持续给出根因+修复（改回 .sv / 加 -noerror / 修复 noerror）→ A档②**禁用**。
6. **#591**「如果我跑一轮 step1_bk 中的30-40条tasks，前面遇到过的 .svp 问题（-v libs/simlib_base.sv）和 noerror 问题（-noerror 120343），我希望在这轮回归在有3个报 .svp 问题一，有3个报 noerror 问题二。我的目的是这轮跑出错误后，把报错的结果交给其他AI分析平台分析后修复掉再重跑可以不报错，显示出这套分析系统的AI分析闭环能力，告诉我应该怎么设置。稍后我会用你提供的设置重新试一轮，并且全程屏幕录像，有问题先问我。」— **clean 提需求（错误编排 + AI 闭环演示）**，A档②合格，**最丰富**。
7. **#619**「我改变想法了，就把之前跑过的5个会出错的case作为报错case的展示，你找3条task报错误一，2条task报错误二。」— 收窄为 5 case（3 svp + 2 noerror）。
8. **#637**「接下来我会跑一下 run_step1_bk，先告诉我有多少task任务量，以及期望的结果，先不运行直到我同意你运行」— 要求 agent 给出 task 量 + 期望结果预测（不运行）。

## A档候选（3 个 clean 提需求轮）
- **#314**：跑回归测 verilogrun 保留 — 产物=VPC+运行，需 UVS 真跑（vsim）。
- **#461**：用改过的 verilogrun 重跑测 UVS 报错 — 产物=运行+报错确认，需 UVS。
- **#591（首选）**：错误编排（3 svp-error + 3→2 noerror-error）+ AI 闭环演示 — 产物=**选择+改写 verilogrun + VPC + 运行确认报错分布 + 预测报告**。最自含、可 L2 真跑验证。

## 金标准（待下轮合成时从 assistant 回复精确提取）
- agent 对 #591/#619 的实际回复：选了哪 5 个 case、每个 case 应用哪种改写（3 个→`-v ...sv`→`.svp` 触发 svp-error；2 个→移除 `-noerror 120343` 触发 noerror-error）、生成的 VPC、对 #637 给的 task 量+期望结果预测。
- 末尾用户接受的结果（agent 是否被用户同意运行 + 跑出 3+2 报错分布）。

## L2 可行性（关键发现 · 修正先前 BLOCKER 假设）
- **.75 沙盒 HAS**：`vcs`(/apps/synopsys/SRB/vcs/R-2020.12/bin/vcs)、`vsim`(/proj/shdc/sim/bin/vsim，疑 UniVista vsim)、`dc_shell`、`primetime`、`pt_shell`。
- **.75 沙盒 MISSING**：verdi、formality、verilint、uvs、vps（VPS CLI/VPC 引擎是 UniVista 私有，不在沙盒）。
- ⇒ Verilog 仿真 L2 **可行**（用 vcs 或 vsim 替代 UVS 内核）；VPS 私有 CLI/VPC 引擎不可真跑，但 verilogrun（=vsim 命令行）改写 + vcs 真跑验证报错分布 = 合规 L2。
- ⇒ 先前 MEMORY BLOCKER「verification L2 infeasible」**部分错误**：sim 工具有，缺的是 VPS 编排器与 verdi/formality。

## 合成计划（下轮 · DEBT:1）
**case_id**: EDA-Eval-DesignFlow-VpsRegrErrorEngineer-001  ·  verb: `vps-regr-error-engineer`  ·  domain: verification  ·  level: L2  ·  track: faithful(A档)
- **A档 task** = USER #591 逐字原文。
- **assets (A 可见)**：
  - `verilogrun/` 5 个合成 verilogrun 脚本（vsim 命令行：`vsim -noerror 120343 -v libs/simlib_base.sv -f case_<n>.f ...`），各对应一个 DDR5 case 名（沿用 trace 风格 ddr5.drcoa）。
  - `rtl/` 一个小 Verilog 模块 + `libs/simlib_base.sv`（基线 lib）+ `libs.bak20260416/simlib_base.svp`（含与 .sv 不一致的端口/定义 → 换上即 vcs compile error = svp-error）。
  - `spec.json`：`{cases:[...5...], error1:{count:3, mod:"swap_svp"}, error2:{count:2, mod:"strip_noerror"}, expect_pass:0}`。
  - `task_brief.md` ≤3 行（交付接口：submit.zip{engineer.py + VPC + modified_verilogrun/ + run_report.json}）。
- **候选 deliverable**：`engineer.py`（CLI `--spec spec.json --verilogrun <dir> --rtl <dir> -o <out>`）→ 选 case + 应用 spec 指定的改写（swap `-v`→`.svp` / strip `-noerror 120343`）+ 生成 VPC（合成的 case 列表）+ 调 vcs 真跑 5 case + 解析 log 出报错类别 + 写 run_report.json{per_case:{category, exit, log_snippet}, distribution:{error1:3, error2:2, pass:0}}。
- **hidden B**：异构 — 不同 5 case 名 / 不同 RTL（counter 而非 DDR5）/ error1=2 error2=3 反转 / 不同 lib 路径 → 击破硬编 A。
- **check.py ≥8 断言**（独立可 FAIL）：① zip 含 engineer.py+VPC+modified_verilogrun/+run_report.json ② py_compile ③ 候选跑 A exit0 ④ 5 个 verilogrun 改写正确（3 个 svp-swap、2 个 noerror-strip、其余不变）⑤ 备份 .bak 存在 ⑥ VPC 列出 5 case ⑦ run_report.json distribution==spec ⑧ **vcs 真跑**：3 个 svp-case 的 log 含 compile error 且 category=error1；2 个 noerror-case category=error2 ⑨ 跨输入守卫 B：B 的 VPC 不含 A case 名 ⑩ 跨输入守卫 B：B distribution==B spec（非 A）⑪ 反硬编 engineer.py 源码不含 A/B case 字面量 ⑫ 随机化 3 跑 A run_report 字节一致。k=12≥8。
- **negatives**：fake_empty / fake_print_expected / fake_core_deleted(no vcs 跑) / naive_hardcode_a / naive_skip_sim → 全 FAIL（fake_skip_sim 触⑧）。
- **§4.9 三假**：(a)空壳 (b)只 print 期望 run_report (c)参考解删 vcs 调用 → 全 FAIL。
- **难点**：合成一个换 .svp 即 compile-error、strip -noerror 即 warning-as-error 的小 Verilog lib 对（需 vcs 实测验证）。下轮先做 lib 对 + vcs 烟测，再写 check。

## 备注
- 本轮（A #59）仅深读（trace 2.84MB/742msgs，§3 大 trace 例外），DEBT:1，下轮第一件事合成此 case。
- 本轮另一产出：确认 .75 沙盒有 vcs/vsim/dc_shell/primetime（修正 BLOCKER），verification L2 sim 类 case 可做。
- 候选稀缺确认：summary.tsv(10/28) + daily eda_trace_2026110{1-4}.log 全扫，纯数字工具(vcs/verdi/dc_shell/formality/primetime/pt_shell)在 daily log 的 tool markers 中**0 命中**（daily_eda_scan.sh step3 awk 缺数字工具词，需运维修）；summary.tsv tools 列亦无这些 marker。所有 innovus-heavy 候选已入台账为 case。fresh 候选仅剩 calibre/virtuose-dominant（physical/analog，他 shard）或本 VPS netlist-heavy 验证 trace。
