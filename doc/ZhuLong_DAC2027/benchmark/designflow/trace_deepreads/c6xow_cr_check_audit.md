# Deepread — c6xow (lorikx / hfeg0pkn004 / 1793069875156_c6xow)

- **trace**: lorikx @ hfeg0pkn004 (10.129.2.10), session `1793069875156_c6xow` (mc158, rtl:413;verilog:120 dominant, c_tot=1 b_tot=0 n_tot=2 → clean A-dominant digital/verification). Session is a **directory** (autofs): messages at `<dir>/1793069875156_c6xow.messages.json`, 1.07MB / 149 msgs. Agent = deepseek-lead.
- **user turns (2 real `<user_input>`)**:
  - U#0: 「请阅读 rtl/ 文件夹内的修改记录 markdown 文件，以及最新的 .v 文件，调整一下 testbench，符合最新的修改要求」
  - U#1: 「请继续」
  - **A-faithful produce-task 合格**: user 给了任务（调整 TB 适配新 CR 语义）但**未给根因/未给具体改法**。
- **agent work**: read_files (CR_MODEL_ALIGNMENT_NOTES.md = G1-G5 golden rules, sp_sram.v old vs new, tb_sp_sram.v) + editor×31 (~14 direct edits to `sim/tb_sp_sram.v`: Version 9.5→9.6, CR_DISABLE/ENABLE, spare column replacement, test_14b_cd_left, `array preserved across CRSxE edge (G1)`, etc.) + reused `diff_rtl.py` as scratch probe rewritten ~12× (`diff`, `Analyze tb_sp_sram.v: find CR-related checks that may depend on old array-corruption behavior`, `find localparams`, `list sim_logs`, `parse build logs`, `poll builds`, `run sequential regression`, …) + run_approved_command×22 (run probes + VCS builds).
- **沉淀需求**: testbench check-task 抽取（每个 `task check_*`/`task expect_*` 有 FAIL+PASS `$display` 消息对）+ 按消息文本做 CR 语义归类 + 块注释/行注释/skip-only 处理。
- **deliverable decision**: A-faithful 直接复刻 agent 的 TB 修改产物不可行（依赖完整 VCS sim 环境 + 私有 RTL，无法 offline 验证）。→ **B 档合成** `cr_check_audit.py`：纯 stdlib 静态审计器，把 agent 「find CR-related checks + 判定是否依赖旧 array-corruption 行为」的分析需求抽成可 offline 验证的代码生成器。
- **case**: EDA-Eval-DesignFlow-CrCheckAudit-001 (verification L1 spec-driven static audit, k=16 B 档).
- **TFC = 4/4 = 100%**:
  1. check/expect task 抽取 ← agent diff_rtl.py 「find CR-related checks」probe
  2. FAIL+PASS `$display` 消息配对 ← agent 编辑的真实 tb check 结构（check_qx_after_cr_edge / check_mem_cr_edge_unchanged / check_memoryIO / check_mem_cr …）
  3. CR 语义类判定 ← CR_MODEL_ALIGNMENT_NOTES.md G1-G5 golden rules + agent「old array-corruption behavior」分析
  4. 块注释排除 + skip-only ← agent 处理 SKIP 桩（check_memoryIO_left 的 SD-mode SKIP）与注释 task
- **同 user 第 2 case**（r424 lilaj XsCheckReportDiag-001 端口审计，同 user 不同 session 不同 deliverable 零重叠）→「同 user 多 session」扩样路径第 2 连实证。
- **判分亮点**: check.py 独立 line-scan oracle（str.find + 手动引号扫描 + 逐行块注释状态机，vs ref 的 regex finditer + 字符流块注释剥离，两套独立避免同 bug 互掩）；⑪⑫ B 特有类 repair_off_read/timing_violation 击败 hardcoded_A；⑦ 块注释 task check_commented_out 排除；⑥ skip-only 桩；⑮ 3 随机 task 块洗牌 (name,class) 集合不变。
