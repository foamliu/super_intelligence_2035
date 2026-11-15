# trace_deepread — 7at4j (lvyy @ hfeg0pkn002, mc69, spice_sim)

**session**: `1793856196029_7at4j.messages.json` (61 msgs, 394KB, 3 substantive user turns)
**trace_source**: lvyy(drgqa) 在 hfeg0pkn002 上, 真实 LSF bsub 仿真提交问题

## 用户三轮提问
1. (msg0) "为什么我仿真提交上去了，但是没有生成文件夹？换了 fqueue3_dll 的队列也是这样" — 命令 `bsub -q fqueue3 001_current.sp -o ./001_current/`，Job 1611446 PEND
2. (msg11) "这些语句是什么意思 .option post / .OPTION PARHIER=LOCAL / probe=1 / ARTIST=2 / INGOLD=..." — HSPICE .option 含义
3. (msg26) "怎么跑不了 ac 了呀, 报错文件在 .../011_CIO" — AC analysis "can be done in spice mode only"

## 根因诊断 (issue #1, 本 case 主题)
助手查 `bjobs -l 1611446` → Status=EXIT, **exit code 126**, Command=`<001_current.sp -o ./001_current/>`；`bqueues -l fqueue3` → MAX=96, 96 RUN, 332 PEND, JL/U=8；读 `001_current.sp` 头部 → `.include/.LIB/.temp/.param` 确认 SPICE 网表；读 `run_1` → 保存的就是那条错误命令。

**三层根因**:
- RC1 `bsub_option_misplaced`: `-o` 写在网表名后被当成网表参数 (bjobs Command 行铁证)
- RC2 `non_executable_netlist`: .sp 是网表不可执行 → exit 126, 0.0 CPU 秒
- RC3 `queue_full_pending`: fqueue3 满 (96/96) 致 PEND ~11min, 换队列命令相同结果相同

**正确提交**: `mkdir -p 001_current && bsub -q fqueue3 -J 001_current -o ./001_current/run_%J.log finesim 001_current.sp`

## 造题
- 形态: debug-Q&A → 根因诊断报告 (L1 离线解析器)
- case_id: EDA-Eval-DesignFlow-BsubNoFolderDiag-001
- A/B: B-档 synthesized (真实 LSF 输出在 .75 内网, SUT 不可达); A=真实值(job 1611446/fqueue3/001_current.sp), B=替换值(job 2077889/fqueue5/003_power.sp/hfeg0plg077/hfsds514/队列 128)
- k=14 断言 (a-n): zip/真跑/JSON/12键/user_command(B)/job_id(B)/queue(B)/netlist(B)/exit_code=126/root_causes≥3/RC1 evidence引B Command行/RC2 evidence引126+网表标记/fix flags+example/确定性3 rerun
- ref PASS 14/14 + 4 negs (naive_hardcode_a/empty_shell/print_only/core_deleted) 全 FAIL ✓
- 旧判 parked (why_no_folder_diag r435 / reject diagnostic r618 reaudit 可造) → r644 复活池变现 #26
