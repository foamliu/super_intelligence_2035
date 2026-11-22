# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态

WAITING: 1（2026-11-23 wake#1845·**强模型 3-run r1-attempt-2 跑中·健康·88%**：deepseek-v4-pro-cloud × Lite 500 × Pass@1 × thinking low × timeout 2400 × cline 3.0.51 + PreToolUse hook × workers 16·serial script PID 3070368 + run_batch PID 3070457 alive（~8h49m elapsed·PPID 父子链确认✅）·**443/500 judged**（99 PASS/329 FAIL/13 ERROR/2 ABSENT → Pass@1(decided)=99/428=**23.1%** early，vs doubao-pro 10.18% 符合"强模型"预期·较 wake#1844 414/500→443/500 +29 case +7 PASS）·ETA r1 ~1h07m 剩余（log [443/500] 88% 8:49:18<1:07:27·71.7s/it·r1 收口 ~今早 07:00·3 轮 ~Nov 23 晚）·**0 FUSE/0 quota/0 熔断**（status_dsv4pro_r1.jsonl grep=0 + run_dsv4pro_r1_20261122_201448.log grep=0 双零✅）·身份四证✅（providers.json deepseek 态：apiKey 末8=8aa0785e / model deepseek-v4-pro-cloud / baseUrl /cloud/v1 / maxTokens 16384 / reasoning.enabled=false，与任务书§二.3 逐字对齐；run_batch cmd --model 双重确认）·disk：/tmp 1.1G(98%) /home 1.3G(100%) /nasdata 2.4T free·serial disk_check 阈值 /tmp≥1G /home≥1G 当前过（紧但够·他用户不可控·若 /home 跌破 1G 则 r2 disk_check 阻塞属设计保护非 bug）·报告生成器 `run/zhulong_strong_3run_report.py` 就绪（3 轮跑完一键出 HTML + McNemar）·McNemar early sanity（r1 partial vs doubao-pro r2+r3 majority）显著 p≈0·cline→/nasdata 符号链接✅·pro_default.bak 就位✅（Nov 22 18:41）·r2 status file 未生成（r1 未完·正常）·ops inbox RUN_ID 146 已 DONE 无 zhulong 新指令·git run/ 本线文件干净（benchmark/designflow 他线在途 unstaged 文件不动·不强拉 rebase）·LOOP 30min 轮询·不起臂·不改原文/题/check·v3 三组数字不动）

- [wake#1840 详条已滚出·2026-11-23 wake#1842 维护] 见 `daily-memories/2026-11-23.md` §[wake#1840 rolled-out]（opencode 交互式·r1-attempt-2 监控心跳·健康·281/500·23.10% early·0 FUSE·身份四证✅·主动修复 /tmp 阻塞风险 3M→1063M + 写报告生成器 zhulong_strong_3run_report.py + McNemar early sanity 显著 p≈0·不干预）。**结论**：r1 健康跑中，/tmp 阻塞风险已预防性缓解，报告生成器就绪，等下轮 wake 继续监控·不起臂·不改原文/题/check·v3 三组数字不动。
- [wake#1841 详条已滚出·2026-11-23 wake#1843 维护] 见 `daily-memories/2026-11-23.md` §[wake#1841]（opencode 交互式·r1-attempt-2 监控心跳·健康·310/500·22.9% early·0 FUSE·身份四证✅·不干预）。
- [wake#1842 详条已滚出·2026-11-23 wake#1843 维护] 见 `daily-memories/2026-11-23.md` §[wake#1842 rolled-out]（opencode 交互式·r1-attempt-2 监控心跳·健康·349/500·23.2% early·0 FUSE·身份四证✅·不干预）。
- wake#1845（2026-11-23 06:3x opencode 交互式·**强模型 3-run r1-attempt-2 监控心跳·健康·88%**）：serial script PID 3070368 + run_batch PID 3070457 alive（~8h49m elapsed·PPID=3070368 父子链确认✅·cmd = `run_batch.sh --workers 16 --model deepseek-v4-pro-cloud --status .../status_dsv4pro_r1.jsonl`）·16 worker 全起·**443/500 judged**（99 PASS/329 FAIL/13 ERROR/2 ABSENT → Pass@1(decided)=99/428=**23.1%** early，vs doubao-pro 10.18% 符合"强模型"预期·较 wake#1844 414/500→443/500 +29 case +7 PASS）·ETA r1 ~1h07m 剩余（log [443/500] 88% 8:49:18<1:07:27·71.7s/it·r1 收口 ~今早 07:00·3 轮 ~Nov 23 晚）·**0 FUSE/0 quota/0 熔断**（status_dsv4pro_r1.jsonl grep=0 + run_dsv4pro_r1_20261122_201448.log grep=0 双零✅）·**身份四证✅**（providers.json deepseek 态：apiKey 末8=8aa0785e / model `deepseek-v4-pro-cloud` / baseUrl `/cloud/v1` / maxTokens 16384 / reasoning.enabled=false，与任务书§二.3 逐字对齐；run_batch cmd --model 双重确认）·per-round status file 核验：`eval/status_dsv4pro_r1.jsonl` 443 行 current 正常写入·r2/r3 status file 未生成（r1 未完·正常）·disk：/tmp 1.1G free(98%) /home 1.3G free(100%) /nasdata 2.4T free·serial disk_check 阈值 /tmp≥1G /home≥1G 当前过（紧但够）·报告生成器 `run/zhulong_strong_3run_report.py` 就绪（13402B）·cline→/nasdata 符号链接✅·pro_default.bak 就位✅（Nov 22 18:41）·ops inbox RUN_ID 146 已 DONE 无 zhulong 新指令·git run/ 本线文件干净（benchmark/designflow 他线在途 unstaged 文件不动·不强拉 rebase）·**结论**：r1-attempt-2 健康跑中（88%·ETA ~1h07m），不干预，等下轮 wake 继续监控·不起臂·不改原文/题/check·v3 三组数字不动。
- wake#1844（2026-11-23 06:0x opencode 交互式·**强模型 3-run r1-attempt-2 监控心跳·健康**）：serial script PID 3070368 + run_batch PID 3070457 alive（~8h14m elapsed·PPID=3070368 父子链确认✅·cmd = `run_batch.sh --workers 16 --model deepseek-v4-pro-cloud --status .../status_dsv4pro_r1.jsonl`）·16 worker 全起·**414/500 judged**（92 PASS/308 FAIL/13 ERROR/1 ABSENT → Pass@1(decided)=92/400=**23.0%** early，vs doubao-pro 10.18% 符合"强模型"预期·较 wake#1843 386/500→414/500 +28 case +5 PASS）·ETA r1 ~1h41m 剩余（log [414/500] 82% 8:14:00<1:41:46·71.6s/it·r1 收口 ~今早 06:00·3 轮 ~Nov 23 晚）·**0 FUSE/0 quota/0 熔断**（status_dsv4pro_r1.jsonl grep=0 + run_dsv4pro_r1_20261122_201448.log grep=0 双零✅）·**身份四证✅**（providers.json deepseek 态：apiKey 末8=8aa0785e / model `deepseek-v4-pro-cloud` / baseUrl `/cloud/v1` / maxTokens 16384 / reasoning.enabled=false，与任务书§二.3 逐字对齐；run_batch cmd --model 双重确认）·per-round status file 核验：`eval/status_dsv4pro_r1.jsonl` 414 行 mtime 04:28 current 正常写入·r2 status file 未生成（r1 未完·正常）·disk：/tmp 1.1G free(98%) /home 1.3G free(100%) /nasdata 2.4T free·serial disk_check 阈值 /tmp≥1G /home≥1G 当前过（紧但够·他用户不可控·若 /home 跌破 1G 则 r2 disk_check 阻塞属设计保护非 bug）·cline→/nasdata 符号链接✅·pro_default.bak 就位✅（Nov 22 18:41）·ops inbox RUN_ID 146 已 DONE 无 zhulong 新指令·git run/ 本线文件干净（benchmark/designflow 他线在途 unstaged 文件不动·不强拉 rebase）·research 日报 11-23 zhulong 仅在覆盖矩阵表 + 多角色独立复算消融建议（属已 done_all 的 subagent 消融线·与当前 3-run 无关·忽略）·**结论**：r1-attempt-2 健康跑中，不干预，等下轮 wake 继续监控·不起臂·不改原文/题/check·v3 三组数字不动。
- wake#1843（2026-11-23 05:5x opencode 交互式·**强模型 3-run r1-attempt-2 监控心跳·健康**）：serial script PID 3070368 + run_batch PID 3070457 alive（~7h42m elapsed·PPID=3070368 父子链确认✅·cmd = `run_batch.sh --workers 16 --model deepseek-v4-pro-cloud --status .../status_dsv4pro_r1.jsonl`）·16 worker 全起·**386/500 judged**（87 PASS/287 FAIL/11 ERROR/1 ABSENT → Pass@1(decided)=87/374=**23.3%** early，vs doubao-pro 10.18% 符合"强模型"预期·较 wake#1842 349/500→386/500 +37 case +9 PASS）·ETA r1 ~2h15m 剩余（log [386/500] 77% 7:42:09<2:14:54·71.8s/it·r1 收口 ~今早 06:30·3 轮 ~Nov 23 晚）·**0 FUSE/0 quota/0 熔断**（status_dsv4pro_r1.jsonl grep=0 + run_dsv4pro_r1_20261122_201448.log grep=0 双零✅）·**身份四证✅**（providers.json deepseek 态：apiKey 末8=8aa0785e / model `deepseek-v4-pro-cloud` / baseUrl `/cloud/v1` / maxTokens 16384 / reasoning.enabled=false，与任务书§二.3 逐字对齐；run_batch cmd --model 双重确认）·per-round status file 核验：`eval/status_dsv4pro_r1.jsonl` 386 行 mtime 03:56 current 正常写入·r2 status file 未生成（r1 未完·正常）·disk：/tmp 1.1G free(98%) /home 1.3G free(100%) /nasdata 2.4T free·serial disk_check 阈值 /tmp≥1G /home≥1G 当前过（紧但够·他用户不可控·若 /home 跌破 1G 则 r2 disk_check 阻塞属设计保护非 bug）·cline→/nasdata 符号链接✅·pro_default.bak 就位✅（Nov 22 18:41）·ops inbox RUN_ID 146 已 DONE 无 zhulong 新指令·git run/ 本线文件干净（benchmark/designflow 他线在途 unstaged 文件不动·不强拉 rebase）·research 日报 11-23 zhulong 仅在覆盖矩阵表 + 多角色独立复算消融建议（属已 done_all 的 subagent 消融线·与当前 3-run 无关·忽略）·**结论**：r1-attempt-2 健康跑中，不干预，等下轮 wake 继续监控·不起臂·不改原文/题/check·v3 三组数字不动。
- [wake#1839 详条已滚出·2026-11-23 wake#1840 维护] 见 `daily-memories/2026-11-23.md` §[wake#1839 rolled-out]（opencode 交互式·r1-attempt-2 监控心跳·健康·245/500·24.27% early·0 FUSE·身份四证✅·不干预）。
- [wake#1838 详条已滚出·2026-11-23 wake#1841 维护] 见 `daily-memories/2026-11-23.md` §[wake#1838 rolled-out]（opencode 交互式·r1-attempt-2 监控心跳·健康·217/500·23.58% early·0 FUSE·身份四证✅·不干预）。
- [wake#1837 详条已滚出·2026-11-23 wake#1838 维护] 见 `daily-memories/2026-11-23.md` §[wake#1837 rolled-out]（opencode 交互式·r1-attempt-2 监控心跳·健康·183/500·22.9% early·0 FUSE·身份四证✅·不干预）。
- [wake#1836 详条已滚出·2026-11-23 wake#1837 维护] 见 `daily-memories/2026-11-23.md` §[wake#1836 rolled-out]（opencode 交互式·r1-attempt-2 监控心跳·健康·155/500·23.2% early·0 FUSE·身份四证✅·不干预）。
- [wake#1830/1832/1833/1834 详条已滚出·2026-11-23 wake#1837 维护合并] 见 `daily-memories/2026-11-23.md` §[wake#1830 rolled-out]/§[wake#1832 rolled-out]/§[wake#1833 rolled-out]/§[wake#1834 rolled-out]（均 opencode 交互式·r1-attempt-2 监控心跳·健康·56→80→101→125/500·0 FUSE·身份四证✅·不干预；wake#1830 = r1-attempt-1 VOID + 5 项修复 + r1-attempt-2 启动）。
- [wake#1828 详条已滚出·2026-11-22 wake#1830 维护] 见 `daily-memories/2026-11-22.md` §[wake#1828 rolled-out]（opencode 交互式·新令执行：强模型 3-run 启动·canary 两证过·PID 2647461·r1 健康跑中·v3 三组数字不动·不起臂·原文不改）。

- [wake#1827 详条已滚出·2026-11-22 wake#1828 维护] 见 `daily-memories/2026-11-22.md` §[wake#1827 rolled-out]（opencode 交互式 v3 收口后 standby 心跳·pgrep 无 run_batch✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·ops inbox 无新指令✅·research 日报 zhulong 建议偏视频/多模态·忽略✅·不起臂·原文不改）。

- [wake#1826 详条已滚出·2026-11-22 wake#1827 维护] 见 `daily-memories/2026-11-22.md` §[wake#1826 rolled-out]（opencode 交互式 v3 收口后 standby 心跳·pgrep 无 run_batch✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·ops inbox 无新指令✅·research 日报 zhulong 建议偏视频/多模态·忽略✅·不起臂·原文不改）。

- [wake#1825 详条已滚出·2026-11-22 wake#1826 维护] 见 `daily-memories/2026-11-22.md` §[wake#1825 rolled-out]（opencode 交互式 v3 收口后 standby 心跳·pgrep 无 run_batch✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·ops inbox 无新指令✅·不起臂·原文不改）。

- [wake#1824 详条已滚出·2026-11-22 wake#1827 维护] 见 `daily-memories/2026-11-22.md` §[wake#1824 rolled-out]（opencode 交互式 v3 收口后 standby 心跳·pgrep 无 run_batch✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·ops inbox 无新指令✅·不起臂·原文不改）。

- [wake#1823 + wake#1819-#1822 详条已滚出·2026-11-22 wake#1827 维护合并] 见 `daily-memories/2026-11-22.md` §[wake#1823] + §[wake#1819-#1822 rolled-out]（均 opencode 交互式 v3 收口后 standby 心跳·pgrep 无 run_batch✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·ops inbox 无新指令✅·research 日报 zhulong 建议偏视频/多模态·忽略✅·不起臂·原文不改）。

- [wake#1818 + wake#1816-#1817 + wake#1812-#1814 详条已滚出·2026-11-22 wake#1827 维护合并] 见 `daily-memories/2026-11-22.md` §[wake#1818]/§[wake#1816-#1817 rolled-out]/§[wake#1812-#1814 rolled-out]（均 opencode 交互式 v3 收口后 standby 心跳·ps 无 run_batch✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 或落后他线 1 commit 不强拉✅·research 日报 zhulong 建议偏视频/多模态成本口径·忽略✅·不起臂·原文不改）。

- [wake#1814 详条已滚出·2026-11-22 wake#1819 维护] 见 `daily-memories/2026-11-22.md` §[wake#1814]（opencode 交互式 v3 收口后 standby 心跳·ps 无 run_batch✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·research 日报 zhulong 建议偏视频/多模态·忽略✅·不起臂·原文不改）。

- [wake#1805-#1811 详条已滚出·2026-11-22 wake#1814 维护] 见 `daily-memories/2026-11-22.md` §[wake#1805-#1811 rolled-out]（均 opencode 交互式 v3 收口后 standby 心跳·ps 无 run_batch 进程✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 或落后他线 1 commit 不强拉✅·research 日报 zhulong 建议偏视频/多模态成本口径·忽略✅·不起臂·原文不改）。

- [wake#1804 详条已滚出·2026-11-22 wake#1808 维护] 见 `daily-memories/2026-11-22.md` §[wake#1804 rolled-out]（opencode 交互式 v3 收口后 standby 心跳·ps 无 run_batch✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git HEAD=9a8b019394 ahead=1 harness 线非本线·research 日报 zhulong 建议偏视频/多模态·忽略✅·不起臂·原文不改）。

- [wake#1800-#1803 详条已滚出·2026-11-22 wake#1805 维护] 见 `daily-memories/2026-11-22.md` §[wake#1800-#1803 rolled-out]（均 opencode 交互式 v3 收口后 standby 心跳·ps 无 run_batch 进程✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·research 日报 zhulong 建议偏视频/多模态成本口径·忽略✅·不起臂·原文不改）。

- [wake#1795-#1799 详条已滚出·2026-11-22 wake#1802 维护] 见 `daily-memories/2026-11-22.md` §[wake#1795-#1799 rolled-out]（均 opencode 交互式 v3 收口后 standby 心跳·ps 无 run_batch 进程✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·research 日报 zhulong 建议偏视频/多模态成本口径·忽略✅·不起臂·原文不改）。

- [wake#1793-1794 详条已滚出·2026-11-22 wake#1799 维护] 见 `daily-memories/2026-11-22.md` §[wake#1793-1794]（均 opencode 交互式 v3 收口后 standby 心跳·ps 无 run_batch 进程✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·research 日报 zhulong 建议偏视频/多模态成本口径·忽略✅·不起臂·原文不改）。

- [wake#1792 详条已滚出·2026-11-22 wake#1800 维护] 见 `daily-memories/2026-11-22.md` §[wake#1792]（opencode 交互式 v3 收口后 standby 心跳·ps 无 run_batch 进程✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·research 日报 zhulong 建议偏视频/多模态成本口径·忽略✅·不起臂·原文不改）。

- [wake#1787 详条已滚出·2026-11-22 wake#1788 维护] 见 `daily-memories/2026-11-22.md` §[wake#1787]（opencode 交互式 v3 收口后 standby 心跳·pgrep 无进程✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·不起臂·原文不改）。

- [wake#1789-1791 详条已滚出·2026-11-22 wake#1796 维护] 见 `daily-memories/2026-11-22.md` §[wake#1789-1791]（均 opencode 交互式 v3 收口后 standby 心跳·ps 无 run_batch 进程✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 或落后他线 1 commit 不强拉✅·research 日报 zhulong 建议偏视频/多模态成本口径·忽略✅·不起臂·原文不改）。

- [wake#1788 详条已滚出·2026-11-22 wake#1797 维护] 见 `daily-memories/2026-11-22.md` §[wake#1788]（opencode 交互式 v3 收口后 standby 心跳·pgrep 无进程✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 落后他线 1 commit 不强拉✅·research 日报 zhulong 建议偏视频/多模态成本口径·忽略✅·不起臂·原文不改）。

- [wake#1784-1786 详条已滚出·2026-11-22 wake#1788 维护] 见 `daily-memories/2026-11-22.md` §[wake#1784-1786]（均 opencode 交互式 v3 收口后 standby 心跳·pgrep 无进程✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 或落后他线 1 commit 不强拉✅·research 日报 zhulong 建议偏视频/多模态成本口径·忽略✅·不起臂·原文不改）。

- [wake#1778-1783 详条已滚出·2026-11-22 wake#1788 维护] 见 `daily-memories/2026-11-22.md` §[wake#1778-1783 rolled-out]（均 opencode 交互式 v3 收口后 standby 心跳·pgrep 无进程✅·providers=pro 默认态✅·cases_lite=500✅·cline 就位✅·git 0/0 同步✅·research 日报 zhulong 建议偏视频/多模态成本口径·忽略✅·不起臂·原文不改）。

- [wake#1768-1777 详条已滚出·2026-11-22 wake#1779 维护] 见 `daily-memories/2026-11-22.md` §[wake#1768-1777 rolled-out]（opencode 交互式 v3 收口 + 9 条 standby 心跳·含 wake#1768 v3 收口详条 lite_r4 DONE 5.71%→lite 3-run=4.68±0.95%·pro/mini/lite 3-run 全出·不起臂·原文不改）。

- [wake#1748 详条已滚出·2026-11-22 wake#1749 维护] 见 `daily-memories/2026-11-22.md` §[wake#1748 rolled-out]（opencode 交互式 v3 令 standby 心跳：mini_r2 跑中 95%·全 infra-clean✅·不起臂·原文不改）。
- [wake#1752 详条已滚出·2026-11-22 wake#1754 维护] 见 `daily-memories/2026-11-22.md` §[wake#1752 rolled-out]（opencode 交互式 v3 令 standby 心跳：mini_r3 跑中 57%·infra-clean✅·不起臂·原文不改）。
- [wake#1686-#1787 详条已滚出·2026-11-22 wake#1788 维护合并] 见 `daily-memories/2026-11-2{0,1}.md` 各 §[wake#XXXX rolled-out]（均 opencode 交互式 standby 心跳·v3 7 batch 全完·pro 3-run=10.18±1.45% / lite 3-run=4.68±0.95% / mini 3-run=2.38±0.23%·`\MzeroAnchor=10.1%` 回填 commit `4fa407d35` clean compile 12p/0err/0undef·release order 已交付·四条 11-19 红令全交付·不起臂·原文不改）。

> 🟢 **结案结论（用户认知 · 2026-11-17 09:3x 用户令 · 必写 · subagent 消融线最终结论）**：
> 「已设计若干 subagent 消融实验，但尚未取得显著收益（subagent 对比单 agent）。在当前任务难度条件下：**1. 单 agent 表现优于多 agent；2. 在多 agent 中，自主 spawn subagent 优于用户定制。** 上述两条由 2026 暑假清华大学博士研究积累的认知仍然稳固。」
> 全线结果汇总：**A0=69.2% / A1=66.7% / A2=53.3% / A0′ VOID / A0′′ r1=10% r2=2.5% r3=未完成 / H2 smoke 叫停**。subagent 消融线 done_all·不再追加新臂·agent 回 standby。


> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | **强模型 3-run（2026-11-22 用户令 553810b7f7）**：deepseek-v4-pro-cloud × EDA-Flow-Bench Lite 500 × Pass@1 × thinking low × timeout 2400 × cline 3.0.51 + PreToolUse hook × workers 16，3 轮串行 + McNemar vs doubao-pro 10.18±1.45%。前置 v3 已收口（pro 10.18±1.45% / lite 4.68±0.95% / mini 2.38±0.23%，7 batch 全完）。 |
| CONFIG | CLI_AGENT=cline 3.0.51 / 强模型=deepseek-v4-pro-cloud@/cloud/v1 key ...8aa0785e / maxTokens=16384 / reasoning.enabled=false（thinking low 由 CLI flag）/ workers 16 / cases_lite.txt 500 / 串行脚本 /tmp/zhulong_strong_serial_eval.sh PID 2647461。 |
| ROUND | 强模型 3-run：r1 跑中（**~414/500 judged·92 PASS/308 FAIL·23.0% early·0 infra·ETA r1 ~1h41m**）·r2/r3 待。v3 三组已收口不动。 |
| PHASE | 🟠 running（强模型 3-run r1-attempt-2 中·PID 3070368/3070457 父子链✅·414/500 82%）。subagent 消融线已 done_all（2026-11-17 用户令·A0=69.2/A1=66.7/A2=53.3%·单 agent > 多 agent·自主 spawn > 用户定制）。 |
| WAITING | 1（2026-11-23 wake#1844·强模型 3-run r1 跑中·LOOP 30min 轮询省 token）。 |
| ERROR_COUNT | 0 |
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | 编排=`glm-5.2`；eval backbone=`deepseek-v4-flash`（复测·运维令二十七②·✅HTTP 200 key 02_...c43c1f4a-03c6-4148-b722-f4c8604c78d3 + /v1·**maxTokens=16384 in providers.json**（≥8192·原记8192实际16384）修复 null-content 问题·reasoning.enabled=false 保持）|

## 执行看板

| 阶段 | 状态 |
|:--|:--|
| **强模型 3-run**（2026-11-22 用户令·deepseek-v4-pro-cloud）| 🟠 r1 跑中 **310/500**（69P/232F·**22.9%** early·0 infra）·r2/r3 待（3 轮串行脚本 PID 3070368·ETA r1 ~4h·3 轮 ~Nov 23 深夜）|
| v3 doubao 三组（pro/lite/mini）| ✅ 收口：pro 10.18±1.45% / lite 4.68±0.95% / mini 2.38±0.23% |
| 两轴消融 think×lang（30/30）| ✅ 已交付（轴 A 倒 U·轴 B 基座对齐）|
| subagent 消融 A0/A1/A2 | ✅ done_all（单 agent > 多 agent·自主 spawn > 用户定制）|
| S1/C1/C2 + 模型对比 B.* | ✅ 全完（成绩记录见下表）|

> 📦 已闭合的 verbose 执行看板（两轴消融/subagent/S1·C1·C2/模型对比 逐臂逐轮）已滚出至 `daily-memories/2026-11-22.md` §[状态头 + 执行看板 rolled-out · wake#1829 维护]。

### 子 agent 消融（subagent ablation · 2026-11-13~15 · 同 40 题子集 ITT）

| 臂 | 配置 | ITT mean±std | gen-rate | cline_ok | spawn率 | 各轮 ITT |
|:--|:--|:-:|:-:|:-:|:-:|:--|
| **A0** | 无 spawn（复用 compaction basic r1-r3）| **69.2 ± 1.4%** | — | 40/40 | 0 | [67.5, 70.0, 70.0]（27/40, 28/40, 28/40）|
| **A1** | 调研型 spawn（researcher·写前 spawn）| **66.7 ± 7.2%** | 86.2% | 29-36/40 | 1.0 | [62.5, 62.5, 75.0]（25/40, 25/40, 30/40）|
| **A2** | 验证型 spawn（adversarial QA·写后 spawn）| **53.3 ± 3.8%** | 87.6% | 23-26/40 | 0.80-0.85 | [50.0, 57.5, 52.5]（20/40, 23/40, 21/40）|
| **A0′** | 无 spawn + 小预算(out=4096·in≤32K·compact@28.8K)·A3 锚点 | **16.7 ± 0.8%** | — | 32/40 | 0 | [15.8, 17.1, 17.1]（25/158, 27/158, 27/158·r1 废）|

**Δ**：A1 vs A0 = −2.5pp（~0.3σ·证据不足）·**A2 vs A0 = −15.9pp**·**A2 vs A1 = −13.4pp**。**关键发现**：三臂 gen-rate（pass/generated）持平 ~87%→能力质量不变；A2 cline_ok(60%) << A1(72-90%) → 验证 spawn 流程更长→更多 timeout→生成率低→ITT 被吞吐拖垮。**McNemar 配对检验 ✅已做**（`mcnemar_subagent_results.json`）：majority vote A0=72.5%/A1=65%/A2=50%→A0vsA1 b=4,c=1,p=0.37 不显著·**A0vsA2 b=9,c=0,p=0.008 显著**·A1vsA2 b=8,c=2,p=0.11 趋势。per-round(120obs)：**A0vsA2 b=24,c=5,p=0.0008 高度显著**·**A1vsA2 b=23,c=7,p=0.006 显著·满足预注册≥6:6**。**H1 裁决**：A0vsA1 证据不足（spawn 调研型不显著伤/助）·A0vsA2 & A1vsA2 **验证型 spawn 显著有害**（主因吞吐降非质量降）。H2 源码 commit 39ccd44cc+wrapper v3.0.74 已 build 未装→待装+smoke→B2-B5。

### A3-A6 起跑预注册（已结案取消·2026-11-17 09:3x 用户令覆盖）

- [A3-A6 起跑预注册详条已滚出·2026-11-18 wake#1326 维护] 见 `daily-memories/2026-11-18.md` §[A3-A6 起跑预注册 rolled-out]（A0′ 收口 16.7±0.8%·A0′′ r1(no-proxy) VOIDED 60%·A3/A4/A5/A6 全部因 subagent 消融线结案取消·原文不改）。



## 成绩记录（N=5 mean±std，Pass@1 %）

| 臂 | N=5 mean±std | 各轮原始值 |
|:--|:-:|:--|
| B.glm-5.2 | **83.3 ± 3.1%** | [84.2, 87.3, 84.2, 79.1, 81.6] |
| B.deepseek-v4-flash | **60.1 ± 5.5%** ✅ 复测 5/5（运维令二十七②·2026-10-18 收口·trace 修复验证）| [60.1, 57.0, 62.7, 67.7, 53.2]（复测·2026-10-17~18·运维令二十七② trace 诊断修复：-p 8→4 + maxTokens 8192→16384 in providers.json·r3 起用 16384·V3 自探索 ON + full harness·r1=95/158·r2=90/158·r3=99/158·r4=107/158·r5=84/158·各轮 timeout=0·exec_err=0·0 quota error（r3-r5）/0 infra 故障·判据(十三)有效·**vs fresh 11.9±2.7%→+48.2pp**·tab:llm-comparison Flash 行已 sync (60.1±5.5%·Δ-21.3pp***·†footnote「初测受 gateway 并发限制影响」)·各轮 regrade log /tmp/ABL_deepseek-v4-flash_retest_r{1..5}_regrade.log·归档 /nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation/2026101{7,8}_*\_app.e0031982/）|
| B.deepseek-v4-flash (fresh·已被复测取代) | ~~11.9 ± 2.7%~~ ✅ fresh 5/5（运维令二十三②·2026-10-17 收口·历史对照）| [8.2, 15.2, 10.8, 13.9, 11.4]（fresh 5/5·2026-10-17·⚠️ 73% 失败为 infra 问题（45% 0-token gateway 限流 + 28% null-content reasoning 预算耗尽）·已被复测 60.1±5.5% 取代）|
| B.kimi-k2.6-cloud | **77.0 ± 1.6%** | [79.1, 76.6, 77.2, 74.7, 77.2] |
| **ZL.kimi-k2.6-cloud×full×16384**（zhulong CLI·10-30 运维直令·与 cline 基线 86.8±1.6% 唯一变量=CLI 二进制+backbone）| **✅ 5/5 = 85.0 ± 2.5%** [84.8,81.6,88.6,85.4,84.8] | r1=84.8%(134/158·batch 2026_1030_231313·gen 157/1 fail/0 timeout·mv 修复→regrade 04:25:23→04:43:37·归档 20261031_0443·判据十三 ✅) · r2=81.6%(129/158·batch 2026_1031_044456·gen 157/0/1·mv 修复→regrade 09:54:05→10:17:46·归档 20261031_1017·判据十三 ✅) · r3=88.6%(140/158·batch 2026_1031_103027·gen 158/0/0 best·mv 修复→regrade 16:22:26→16:40:45·归档 20261031_1640·判据十三 ✅) · r4=85.4%(135/158·batch 2026_1031_164422·gen 158/0/0·mv 修复→regrade 22:37:21→23:05:50·归档 20261031_2305·判据十三 ✅) · **r5=84.8%(134/158·batch 2026_1031_230700·gen 157/0/1·04:30 mv 修复 158→format 158(433139B)→complete 157/0/1(436457B)→regrade 04:32:11→04:55:58·归档 20261101_0455·exec_err=0/infra=0/timeout=1·判据十三 ✅)**。**vs cline 基线 86.8±1.6% → Δ−1.8pp（可比·~1.1σ）**·vs B.kimi-cline 77.0±1.6% → **Δ+8.0pp（zhulong CLI 在 kimi backbone 反超 cline）**·vs ZL-flash-clinealigned 69.0±2.3% → Δ+16.0pp。**关键发现**：zhulong CLI 劣势 backbone 依赖——glm-5.3-flash 上 −17.8pp（空响应重试缺失·gen-fail 23-38/轮），kimi-k2.6 上 +8.0pp（kimi 不触发空响应·zhulong 更激进提交风格反受益·gen-fail 0-1/轮）|
| B.doubao-seed-2.0-pro-cloud | **63.8 ± 1.4%** | [63.9, 64.6, 61.4, 65.2, 63.9] |
| B.glm-5.3-flash | **66.8 ± 10.5%** ✅ 5/5（fresh·历史对照·运维令三十一复测中）| [80.4, 53.2, 73.4, 65.8, 61.4]（运维令二十三新臂·r1=127/158·timeout=9·r2=84/158·timeout=6·r3=116/158·timeout=0·r4=104/158·timeout=0·r5=97/158·timeout=0·各轮exec_err=0·判据十三有效·std=10.5轻量backbone高方差·glm-5.3-flash@/v1 key 6903b05e）|
| B.glm-5.3-flash 复测（运维令三十一·-p 4 起步·✅ 5/5 收口）| **✅ 5/5 = 86.8 ± 1.6%** | [86.1, 84.8, 89.2, 87.3, 86.7]（r1=136/158·r2=134/158·r3=141/158·r4=138/158·r5=137/158·各轮 timeout=0/exec_err=0/infra=0·判据十三全轮有效·std 10.5→1.6 远低于目标 8·**CLI 对比锚点**·各轮 batch 2026_1018_142819/170035/192417/223909 + 2026_1019_005714·regrade log /tmp/ABL_glm-5.3-flash_retest_r{1..5}_regrade.log）|
| C1.pure_llm | 10.5 ± 1.9% | [8.2, 9.5, 10.1, 11.4, 13.3]（复用 legacy）|
| C1.wo_retrieval | **81.0 ± 4.5%** | [74.1, 86.1, 81.6, 79.7, 83.5] |
| C1.rag | **71.8 ± 2.5%** | [70.3, 72.2, 69.6, 70.9, 75.9] |
| C1.full(V2)（旧锚点）| **81.4 ± 4.1%** | [88.0, 79.1, 77.2, 80.4, 82.3]（r1=V3文档混配置→已由full_v3取代）|
| C1.full_v3(自探索·正式锚点) | **82.1 ± 3.0%** ✅ 5/5 | [77.8, 86.1, 81.6, 82.3, 82.9]（运维指令(十二)补跑「真full」V3+自探索·r1=77.8%(123/158·timeout=1)·r2=86.1%(136/158·timeout=1)·r3=81.6%(129/158·timeout=4)·r4=82.3%(130/158·timeout=6)·r5=82.9%(131/158·timeout=5)·**未复现r1=88.0%**）|
| C2.phi_k10 | **77.7 ± 2.2%** ✅ 5/5 | [78.5, 76.6, 77.2, 81.0, 75.3]（r1=124/158·timeout=2·r2=121/158·timeout=0·r3=122/158·timeout=0·att2·r4=128/158·timeout=0·att3·**r5=119/158·timeout=0·75.3%**·PHI-BUDGET-EXHAUSTED=426✅）|
| C2.phi_k3 | **69.1 ± 2.5%** ✅ 5/5 | [72.8, 66.5, 69.6, 69.6, 67.1]（r1=115/158·timeout=0·r2=105/158·timeout=0·r3=110/158·timeout=0·r4=110/158·timeout=2·**r5=106/158·timeout=0·67.1%**·PHI-BUDGET-EXHAUSTED=851✅·25 gen-fail=k=3预算效应·判据(十三)：消融臂Pass@1任何值有效·不重跑）|
| C2.phi_k1 | **63.8 ± 3.2%** ✅ 5/5 | [65.2, 66.5, 58.2, 64.6, 64.6]（r1=103/158·timeout=0·35 gen-fail·r2=105/158·timeout=0·30 gen-fail·r3=92/158·timeout=1·39 gen-fail·r4=102/158·timeout=0·34 gen-fail·**r5=102/158·timeout=0·35 gen-fail=k=1预算效应**·regrade PID3120482·生成状态`{'success':123,'failure':0,'timeout':0,'fail':35}`→**timeout=0≤10✅**·exec_err=0·license/Connection=0✅·PHI-BUDGET-EXHAUSTED=1141>0✅(k=1预算生效)·ACCESS RESTRICTED=827✅·判据(十五④/十三)满足→5/5有效不重跑·**单调k10=77.7>k3=69.1>k1=63.8✅·gen-fail随k↓递增✅**·探路 60.8%）|
| C2.phi_lagged | **73.0 ± 3.2%** ✅ 5/5 | [74.7, 76.6, 69.6, 69.6, 74.7]（r1=118/158·timeout=0·5 gen-fail·PHI-LAGGED=1165✅·r2=121/158·timeout=0·10 gen-fail·r3=110/158·timeout=1·11 gen-fail·r4=110/158·timeout=0·13 gen-fail·**r5=118/158·timeout=0·6 gen-fail·batch=2026_1015_042258·gen{success:152,failure:0,timeout:0,fail:6}·PHI-LAGGED=1244✅·ACCESS RESTRICTED=999✅·PHI-BUDGET-EXHAUSTED=0(lagged无上限合理)·exec_err=0·infra errors=0✅**·判据(十三)满足→5/5有效不重跑·§8.4 trace_key(ctx.session)在位✅·lagged机制(canary PHI-LAGGED=1244命中)✅·Δvs unbounded(82.1)=−9.1pp·Converged(%)=97.5·Mean read-backs/gen-fail=9.0·探路 84.2%，r2 修复后 98.1%）|
| S1.omega_low | **82.8 ± 1.0%** ✅（legacy·采信）| [82.8…]（指令二十二①：legacy std=1.0 可信不重跑）|
| S1.readback_binary | **78.1 ± 1.3%** ✅ 5/5（fresh）| [75.9, 79.1, 77.8, 78.5, 79.1]（fresh 重测·2026-10-15~16·替换 legacy 66.2±16.1% std 过大含 43.0% 离群·运维令二十二②·r1=120/158·r2=125/158·r3=123/158·r4=124/158·r5=125/158·各轮 timeout=13/8/7/6/4·exec_err=0·infra=0✅·判据(十三)有效·单调 N'(73.3)<B(78.1)<F(82.1)✅）|
| S1.readback_none | **73.3 ± 2.2%** ✅（legacy·采信）| [72.2, 70.3, 73.4, 75.9, 74.7]（指令二十二③：legacy std=2.2 可信不重跑）|
| **ZL-flash.full**（glm-5.3-flash×zhulong×READBACK=full·09:4x 用户直令·**新探索线·🚫 不入论文**）| **75.6 ± 4.4%** ✅ 5/5 收口 | [69.0, 77.2, 76.6, 81.0, 74.1]（r1=109/158·16lp·r2=122/158·16lp·r3=121/158·23 fail·r4=128/158·12 fail·**r5=117/158·27 fail**·各轮 timeout=0·exec_err=0·0 infra·判据十三全轮有效·各轮 literal-pass>10 标退化(05:0x 不中止)·glm-5.3-flash@/v1 key 6903b05e·maxTokens=16384·zhulong CLI·8650组·论文锚点仍 (N′) fp4×cline 4 轮 76.7% provisional）|
| **ZL-flash-clinealigned-16384**（glm-5.3-flash×zhulong×full×maxTokens=16384 cline-aligned·10-27 用户直令·与 cline 基线逐字节对齐·唯一变量=CLI 二进制·**新探索线·🚫 不入论文**）| **✅ 5/5 = 69.0 ± 2.3%** | [71.5, 67.1, 67.1, 71.5, 67.7]（r1=113/158·batch 2026_1027_083127·132 ok/3 timeout/23 fail·r2=106/158·batch 2026_1027_123502·118 ok/35 fail·r3=106/158·batch 2026_1028_151059·mv 修复 134+format 119/33/6·r4=113/158·batch 2026_1028_231232·mv 修复 139+format 126/32/0·**r5=107/158·batch 2026_1029_041540·mv 修复 141+format 120/37/1**·各轮 exec_err=0·infra=0·timeout≤10·判据十三全轮有效·全程自有池 8664/8665/8653/8669·归档 20261027_1233/20261027_1403/20261028_2309/20261029_0415/20261029_1005·**vs cline 基线 86.8±1.6% → Δ=−17.8pp**·gen-fail 23–38/轮（cline 1–4/轮）·结论：已排除 maxTokens 混杂+跨用户争用+CLI_AGENT 回归·唯一变量=CLI 二进制）|

### 三组对照表（运维指令(十二)⑤交付）

| 组 | 配置 | N | Pass@1 mean±std | 备注 |
|:--|:--|:-:|:-:|:--|
| r1 旧时代 | V3文档(旧配置) | 1 | 88.0% | 异常高值·混配置·不可复现 |
| full 现配(V2) | V2无自探索(r2-r5) | 4 | 79.8±2.1% [79.1,77.2,80.4,82.3] | 旧锚点(混配置) |
| **full_v3 新** | **V3+自探索(真full)** | **5** | **82.1±3.0%** [77.8,86.1,81.6,82.3,82.9] | **正式锚点** |

**结论**：full_v3 (82.1±3.0%) **未复现** r1=88.0%（异常高值）。full_v3 比 V2(r2-r5=79.8±2.1%) 高 ~2.3pp，1σ 范围内重叠，自探索增益不显著。
- [2026-10-19 06:30–17:31 指针块·已滚出] 运维令三十二② (N′) r1/r2/r3 巡检 #1–#11、r1/r2 收口详情 → 原文已搬入 daily-memories/2026-10-19.md「归档·18:5x」段。r1=78.5%/r2=70.9%/r3 task130 stuck 6582s（RUN_ID 83 查的根因）。
## 操作流水
- [wake#1716 详条已滚出·2026-11-22 wake#1770 维护] 见 `daily-memories/2026-11-21.md` §[wake#1716 rolled-out]（opencode 交互式 standby 心跳·用户再次粘贴全 TASK 无新令·核账发现 pro 报告漏产→补交付 pro 报告 9.32%/`\MzeroAnchor`=10.1%·v2 全判据真完整·不起臂·done_all）。
- wake#1770（2026-11-22·opencode 交互式·**v3 收口后 standby 心跳复核**）：用户粘贴全 ZHULONG_TASK.md（顶部仍=v3 令·无新令）。自检：① pgrep run_batch.sh 无进程✅；② providers.json=pro 默认态（apiKey ...25cdc15f / model doubao-seed-2.0-pro-cloud / baseUrl 正确）✅；③ cases_lite.txt=500✅；④ 3 份报告（pro/lite/mini）均为 3-run 汇总版（grep '3-run' 命中✅，mtime 11-22 13:53）✅；⑤ git HEAD=`03ffecf02e`=zhulong wake#1769 standby 心跳（up to date）✅；⑥ cline 就位✅。v3 任务 7 batch 全完·3 模型 3-run 全出（pro=10.18±1.45% / lite=4.68±0.95% / mini=2.38±0.23%）·无新令·不起臂·不跑评测·不改原文/题/check·收口 WAITING=0·standby。维护：滚出 wake#1716 详条至 daily-memories/2026-11-21.md（MEMORY 41.5KB→<40KB 合规）。
- [wake#1714详条已滚出·2026-11-21 wake#1716 维护] 见 `daily-memories/2026-11-21.md` §[wake#1714rolled-out]（opencode 交互式 standby 心跳·1 ahead=designflow shard B local-only·v2 全判据 ✅·不起臂·done_all·原文不改）。
- [wake#1713详条已滚出·2026-11-21 wake#1716 维护] 见 `daily-memories/2026-11-21.md` §[wake#1713rolled-out]（opencode 交互式 standby 心跳·git 完全干净 0/0·v2 全判据 ✅·不起臂·done_all·原文不改）。
- [wake#1700详条已滚出·2026-11-21 wake#1716 维护] 见 `daily-memories/2026-11-21.md` §[wake#1700rolled-out]（opencode 交互式 standby 心跳·release order 已交付 10/422=2.37%·HEAD=2e73b564f=origin/main·不起臂·done_all·原文不改）。
- [wake#1699详条已滚出·2026-11-21 wake#1716 维护] 见 `daily-memories/2026-11-21.md` §[wake#1699rolled-out]（opencode 交互式 standby 心跳·release order 已交付 10/422=2.37%·HEAD=931cc40e3=origin/main·不起臂·done_all·原文不改）。
- [wake#1694 详条已滚出·2026-11-20 wake#1699 维护合并] 见 `daily-memories/2026-11-20.md` §[wake#1694 rolled-out]（opencode 交互式 standby 心跳·pgrep 无 ZhuLong eval·release order 已交付 10/422=2.37%·HEAD=`29ff06120`·不起臂·done_all）。
- [wake#1693/#1692/#1690/#1689/#1685/#1681 详条已滚出·2026-11-20 wake#1700 维护合并] 见 `daily-memories/2026-11-20.md` §[wake#1693...rolled-out]（均 opencode 交互式 standby 心跳·pgrep 无 ZhuLong eval·release order 已交付 10/422=2.37%·HEAD 演进 `2abd2b427`→`6199b2860`→`190af8959`→`2634a0a38`→`98be2f147`→`11a88d351`·不起臂·done_all）。
- [wake#1612 详条已滚出·2026-11-20 wake#1616 维护合并] 见 `daily-memories/2026-11-20.md` §[wake#1611-1614 rolled-out]（opencode 交互式 standby 心跳·pgrep 无 ZhuLong eval·main.log 0/0/0 Overfull/28 Underfull/12p·paper HEAD=`8d1856dcd`·不起臂·done_all）。
- [2026-11-19 wake#1522·opencode 交互式] `[paper] abstract 词数修复 ⑨：fresh 复核发现 abstract 渲染词数 ~217（pdftotext 宏展开）> 200 自设上限——前序 wake#1513-1521 用宏剥离计数（detex~209/注释~198）误判 ⑨ 通过。按评测集分层红令 ③.2 授权压缩 abstract ~17 词至 199 渲染词 ≤ 200 ✅。全防伪数据点保留（7.6×/10.0%/76.5%/696/62/620/7.1×/500/several thousand/10-arm/N1/M4/NDA/no-release/publishable boundary·P2① 半句区分保留）。重编译 pdflatex×4+bibtex·12p/0err/0undef/234408B·正文 §1-§9=p1-p6 ≤6·⑩ pdftotext 0 泄漏·11 判据全过。改动=sections/0_abstract.tex（英文+中文注释同步）+main.pdf。infra: loop PID243810+ops relay 118463 活·pgrep 命中=EDA-Eval-PyAether（designflow 线·非本线）·§7 done_all·standby。`
- [2026-11-18 wake#1338·zh-cn 详条已滚出·2026-11-19 wake#1522 维护] 见 `daily-memories/2026-11-18.md` §[wake#1338 rolled-out]（zh-cn 全文加中文对照注释态·commit abf24281f+28e77662f+870a7102c·11p/0err/0undef·原文不改）。
- [wake#1331/#1327/#1326/#388~#838 旧指针已滚出·本轮 wake#1444 维护滚出] 见 `daily-memories/2026-11-19.md` §[wake#1443 详条 + 操作流水旧指针 rolled-out · 2026-11-19 wake#1444 维护滚出]（4 条旧指针原文保留于此·均已被 daily-memories/2026-11-18.md 及更早 daily 代表·省 MEMORY 空间·原文不改）。
