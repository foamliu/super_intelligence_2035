# deepread: 1795830818571_z8i5q — vsim Perl sim-driver deletion forensics

- session: 1795830818571_z8i5q.messages.json
- user: guangmingz @ hfeg0pkn004 (10.129.2.13)
- agent: lead (cline, policy-engine enforced)
- mc=60, keywords: verilog:900;netlist:370;analog:36;.def:9;lib.defs:8;aether:4;drc:3;pt_shell:2
- domain: digital / verification (genuine A — verilog:900 + pt_shell:2 + xrun sim driver)
- discovered: r1540 NEW fullscan 102722 (vs 093245), fresh A-domain candidate
- scan coverage window this candidate falls in: created 2026-11-28 ~09:53 (after 093245 finished 09:38)

## 用户真实意图（3 轮追问）

用户在排查一个 Perl 仿真驱动脚本 `vsim`：
`/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/bin/vsim`
（xrun/VCS 仿真 flow 的 run-script 调用的驱动，跑 DDR6 dscqa 验证 pattern）。

3 个递进问题：
1. **为什么 vsim 会把环境 `.sv` 源文件删掉？**（proj_package.sv / ddr6_test.sv / top.sv / ddr6_parameter.sv 等软链在 run 后消失）
2. **给定具体 vsim 命令**（`-p dscqa/V0 -s -r Fuse004_..._FUSE_CHIPPROBE -f TM -d "..." -b X1P12 -l log_2026_Spf/Fuse/Read/1127 --tool xrun`），**枚举所有涉及删除文件的地方，带绝对路径**。
3. **为什么会把 `vecgen_local` 顶层软链删了？**（答：`-u`/`-U` update 分支 `gentblnfile`，非 `-s` 分支）
4. **同命令，枚举所有删除点带绝对路径，并分析每个删除是否「先检查文件存在再删」**。

## assistant 排查链（关键事实）

- vsim 是 Perl 脚本，跑仿真时 `chdir` 到 run 目录（`$CWD/log_*/<reg>.<plusmode>/`），做「清空→软链部署→仿真→清空」循环。
- 删除发生在收尾 subs：`rmlnfile` / `rmpatternsfile` / `rmworklib`（`rm -Rf` .sv / pattern / worklib）。
- 顶层软链删除走独立 `-u`/`-U` 更新分支（~385-399 行 `if($updateusr || $updateusrforce){ &gentblnfile(...) }`），`-s` 分支不会删顶层。
- 每个 run 目录跑完后不留 .sv（实测 `Plan_0723_SHORT_11600/CAPairty001...FF.X2P6_11600/` 只有 `A_Pattern_Sim.v / Pattern_tasks.v / probe.tcl / *.run / *.inc / stimulus.* / verilogrun`）。
- 最终结论 msg[36]：逐处枚举所有 `rm -Rf` 删除点，标绝对路径 + 是否 `-e` 先检存在。

## case 合成计划（DEBT — 下一轮）

**任务形态**：code-comprehension / 仿真驱动脚本取证。给 vsim 脚本（附件 A）+ 一条具体 vsim 命令，产出「所有删除点枚举报告」：每条 = {删除代码位置/行号, 目标绝对路径表达式, 是否先 -e 检查存在}。

**判分对象**：报告的结构化枚举（解析成字段后比较），不是文本相似。
- 隐藏 B：不同 `-l`/`-r`/`-b`/`-f` 参数 → 不同 run 目录绝对路径，但删除点代码位置集合不变。
- ≥8 断言：① 报告含 N 个删除点 ② 每个删除点的绝对路径前缀正确（含 $CWD/$logname/$regname/$plusmode 拼接）③ 顶层软链删除归因到 -u/-U 分支 ④ -s 分支不删顶层 ⑤ rmlnfile/rmpatternsfile/rmworklib 三 subs 各被识别 ⑥ 收尾清空 vs 部署前清空区分 ⑦ 每个 rm 是否 -e 守卫分类正确 ⑧ 退化提交（空报告 / 只 print 期望 / 删核心）全 FAIL。
- 真跑候选：可让 agent 在 B 上 `grep -n 'rm\b\|unlink\|rmdir'` vsim 脚本，断言提取出的删除行号集合 ⊆ 参考集合。

**阻塞**：vsim 脚本从 .75 ssh 直取 `Permission denied`（/proj/dscqa 归 guangmingz，policy-engine 管控）。**脚本内容已嵌在 trace 的 tool_result messages 里**（msg[5]/[8]/[11]/[20] read_files 返回 vsim 源码片段）→ 下一轮须从 messages.json 提取 vsim 源码片段重建附件 A（必要时按原脚本风格合成一个等价 B 变体）。

**真实性**：trace_source 完整（user/host/session_file/mc=60/real_task_summary=vsim 删除点取证）。A 档 trace-faithful：prompt 用 guangmingz 原话「分析全部涉及删除文件的地方 并带上删除文件的绝对路径 / 分析是否检查文件存在再删除」。

## 状态
- ledger: claimed → deepread (r1540)
- case: DEBT（下一轮交付，需先从 trace 重建 vsim 脚本附件）
