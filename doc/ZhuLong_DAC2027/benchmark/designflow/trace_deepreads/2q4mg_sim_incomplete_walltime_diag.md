# 2q4mg 深读 — 仿真结果不全根因诊断（walltime + 节点过载）

- session: 1793274153419_2q4mg.messages.json
- user: rhyanw @ hfeg0pkn002
- mc: 79, domain: spice_sim
- trace: 430 msgs / 1.3MB / ~40 substantive user turn
- 旧判定: parked "reject how-to 仿真任务运行还是卡死" (r435) → r618 reaudit 可造（debug-Q&A 根因诊断）

## 用户真实意图（trace 原文）
1. 「怎么确认我的仿真任务是在运行还是卡死里」
2. 「具体一点，是怎么用linux终端输入什么」
3. （贴 ps/bjobs 输出）「但是我的仿真是再fqueue2h服务器上跑到你这个检查方法不准确吧」
4. 「我去哪查看仿真结束之后的报告」
5. 「runsim 这个文件里的-o保存的文件夹，中间的SM1029 改成对应到sp名比如N10P10之类的」
6. 「smdatagrab2.pl我现在运行这个程序显示很多不存在的文件，是因为什么」
7. 「仿真是之前跑到的，这几个仿真为什么只有一个数值」
8. 「为什么没跑完呢」
9. 「是不是因为我之前查询是否卡死导致的」
10. 「你检查一下sp文件有没有问题」
11. 「检查一下runsim文件对不对」
12. 「那你估计一下这些全部跑完需要多久我换个服务器，3h的可以不，fqueue3」
13. 「为什么需要这么久到时间，我记得单个sp只需要40min啊」
14. 「改成np16会好意到名」

## 核心根因链（assistant 实证）
1. **运行/卡死确认**: `bjobs` STAT=RUN 只代表「占资源在队列里活着」，不代表「在算」。真判据：登执行机 `ps -eo pid,%cpu,etime,stat,cmd --sort=-%cpu` 看 CPU，或 `bjobs -l <JOBID> | grep "CPU time"` 两次隔 30s 对比是否在涨。`fqueue2h` 是队列名（QUEUE 列）不是服务器名，EXEC_HOST 才是执行机。
2. **报告位置**: 每个任务在自己 run 目录 `result/` 下，找 `*.html *.xlsx *.rpt *.log *.sum *report*`。
3. **runsim -o 路径**: 原本 40 条 bsub 全 `-o ./result/SM1029/mismatchXX`（写死同一目录），改为每行 `-o ./result/<该行-i的SP名>/mismatchXX`。每行独立映射，`-1` 变体也独立目录。
4. **smdatagrab 缺文件**: 改了 runsim 输出目录到 per-SP，但 `smdatagrab2.pl` 第10行还硬编码 `./result/SM1029/mismatch0${n}-1.bisec_mt0` → 找不到新结果。需同步改抓数脚本。
5. **bisec 只有一个值/没跑完**: `.bisec_mt0` 每行=一次 bisection 迭代（alter#）。1 行 = 只跑到 alter#=1。日志文件名 `#1_userstop` + 结尾 `save isnapshot ... by user signal` + `Total elapsed time: 7200 sec (2.00 hours)` → **LSF 队列 fqueue2h 的 2h walltime 上限**到点发停止信号。不是卡死、不是手动 kill、不是 SP 错。
6. **SP 文件检查**: 40 个 SP 参数规律正确，基版 `(nl,nr,pl,pr)=(+,-,+,-)` vs `-1` 变体 `(-,+,-,+)` 符号取反；N0P0 与 N0P0-1 完全相同是因全 0 翻转仍 0，正常。
7. **为什么这么久**: 单 SP 本身 ~40min，但 40 任务 ×6 核 = 240 核一次提交挤共享节点，过载致每代从 ~150s 拖到 550~1200s。`-np 16` 更糟（640 核，超配更严重）——`-np` 管单任务内核，不解决「同时跑 40 个」的抢占。

## 拟造任务形态
debug-Q&A 根因诊断报告。B 档 synthesized（A 档不可行：真实 runsim/sp/日志在 /proj/drvqa 内网工程目录，SUT 沙盒无 /proj 权限不可达）。
- A=可见 fixture（queue=fqueue2h, walltime=2h/7200s, -o=SM1029, SP=NxPy, np=6, 40 任务）
- B=隐藏 fixture（queue=fqueue3h, walltime=3h/10800s, -o=Run2077, SP=MxQy, np=8, 36 任务）
- 任务: 写 `sim_incomplete_diag.py(workdir,out_dir)` 解析 fixture 产 `sim_incomplete_diag.json`，断言根因=walltime+过载、证据引用 B 实测值、cross-input guard、A-leak guard、真跑候选、确定性。

## 判分 16 断言 a-p
①12 顶层键齐全 ②root_cause.primary=lsf_queue_walltime_limit ③secondary=node_overload ④not_caused_by 含 manual_kill/sp_file_error/stuck ⑤elapsed_sec=B(10798) ⑥queue_name=B(fqueue3h) ⑦hours_str=B(3.00 hours) ⑧A-leak 无 SM1029/fqueue2h/7209/2.00hours ⑨bisec incomplete_lines=B(2)/complete=B(14) ⑩runsim total_cores=B(288=36*8)/np=B(8) ⑪smdatagrab hardcoded_path 含 Run2077 ⑫np_verdict proposed_np16=worse ⑬recommendations 含 longer-queue AND reduce-parallelism ⑭bjobs RUN!=computing ⑮真跑候选 subprocess exit 0 ⑯确定性 3 rerun byte-identical
