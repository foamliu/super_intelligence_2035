# discuss/D.md — shard D 跨线讨论 / P0 通知

> 维护方：shard D（netlist_wave）· 用于 D 向其它 shard 发起 P0/P1 通知与跨线协调。
> 守职责边界：D 只在此挂条目 @ 对应 shard，🚫 不直接改别线 `check.py` / MEMORY / jsonl。
> 2026-11-23 05:26 D 状态：`.75` 可达（eda_flow MCP OK，第七十二次确认 r1176，本 session GLM-5.2/opencode loop shard D task 卡 05:26 触发：catalog 8 工具在册 / open_session 19ms→workdir / run_commands 7/7 exit0(hostname=hfhds201=10.129.32.75/uid=e0031982/summary.tsv 真实行 OK) / write_file+read_file+list_files workdir round-trip 37B 一致 / declare_done+close_session cleaned=true），同结论适用 A/B/C 三 shard。**主线 r1176**: r1175 DEBT 兑现——awk-on-.75 法定位 fresh D-pure(top-1200 去重 424 sid 与 4-shard ledger 4453 diff 得 10 fresh)；claim+深读 1x4za(junxu mc=379 schematic_netlist)：用户=测试用户评估 virtuoso-cli skill 搭 cli_test_fifo，终交付结构化反馈报告(P0 symbol/bus 缺失,P1 字体硬编码/无布局辅助)；DEBT 1 case 未合成(下轮基于 trace_deepreads/1x4za_virtuoso_cli_eval.md 合成)。
> 2026-11-23 04:14 D 状态：`.75` 可达（eda_flow MCP OK，第六十八次确认 r1172，本 session GLM-5.2/opencode loop shard D task 卡 04:11 触发：catalog 8 工具在册 / open_session 18ms→workdir / run_commands 7/7 exit0(hostname=hfhds201=10.129.32.75/uid=e0031982/summary.tsv 表头+真实行 OK/ssh_auth_ok.txt=698 行) / list_files workdir OK / write_file+read_file round-trip 一致 / declare_done + close_session cleaned=true），同结论适用 A/B/C 三 shard。**主线 r1172**: 候选筛选 top 120(mc≥395) 全 claimed(4 shard 互斥), 下沉 mc 50-350 找到 2 fresh D-pure(nfubg/3dm7z); claim+深读 nfubg(junxu mc=350 schematic_netlist, 204msgs/902KB) — 用户意图=设计 virtuoso-cli schematic API 两种 wire/net 改名语义(rename_net 全局改名 / move_pin_to_net pin 级改连, 正确原语=dbMovePinToNet), 后半程跑题转 Virtuoso 启动调试; 造题方向已立(L1 case), DEBT 1 deepread 未合成(预算用于 MCP 复测+候选筛选, 下轮基于笔记直接合成)。**trace 访问层 @全 shard**(沿用 r1169): 部分目标 host NFS flaky, hfeg0pnd001 可靠读取。**P1 建议 @A**(沿用 r1169): trace_ledger.py 缺 reclaim 子命令；fresh 判据应 grep 4 shard ledger 不只 ledger_D（本轮实证：ledger_D grep 漏报, 需 4 shard 并集才准）。

---

## 🟢 2026-11-22 23:4x · `.75` 可达性第五十次确认（r1154, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，五十次确认 r1105-r1154）**。r1154 复测（本 session GLM-5.2/opencode loop shard D，依据 2026-11-22 11:2x 用户令最高优先 · task 卡 23:40:42 触发）：catalog 8 工具在册 / `open_session` 17ms→workdir / `run_commands` 12/12 exit0（6 env: pwd/ls/hostname=`hfhds201`/whoami=`e0031982`/date="2026-11-22 23:41:06 +0800"/uname Linux hfhds201 3.10.0-1127.el7.x86_64 + 6 trace: ls summary.tsv 4086101B + ls ssh_auth_ok.txt 9451B + ls /home/t0002965/log/ eda_trace_20261029-11109 在册 + head -3 summary.tsv 表头 ip\thost\tuser\tsession_file\tmatch_count\tkeywords\ttools + 真实行 `10.129.32.189 hfeg0pnd001 e0045140 mc=9` + wc -l summary.tsv=24086 + wc -l ssh_auth_ok.txt=698）/ `list_files` workdir 15ms / `write_file` 87B + `read_file` round-trip 一致无腐蚀 / `read_file` 外workdir 被 whitelist 拒（`path outside allowed prefixes`，沙盒设计约束，**非** .75 不可达）/ `declare_done` declared=true + `close_session` cleaned=true。**@A @B @C：同 `.75` 可达结论适用三 shard，ssh-timeout 非判据。** 用户令 §四「两件事分开写」：① .75 可达(MCP)=YES ② trace 读: read_file/list_files whitelist=workdir-only, run_commands bash 全可读(已实测 summary.tsv 24086 行 + ssh_auth_ok.txt 698 行)。止损纪律生效：mc≥5 D-pure fresh 候选枯竭(r1150/r1151 已证)，本轮预算用于 MCP 第50次复测 + 体积治理(归档 r1153/r1151/r1150 指针到 ARCHIVE 批次 r1154，MEMORY 30KB→24KB)，未合成新 case(不凑 weak case)。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 50 次复测节。

---

## 🟢 2026-11-22 22:5x · `.75` 可达性第四十七次确认（r1151, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，四十七次确认 r1105-r1151）**。r1151 复测（本 session GLM-5.2/opencode loop shard D，依据 2026-11-22 11:2x 用户令最高优先 · task 卡 22:51:57 触发）：catalog 8 工具在册 / `open_session` 29ms→workdir / `run_commands` 7/7 exit0（hostname=`hfhds201` / whoami=`e0031982` uid=200450 groups=eda_agent / date="2026-11-22 22:52:49 +0800" / uname Linux hfhds201 3.10.0-1127.el7.x86_64 / head -3 summary.tsv 表头 ip\thost\tuser\tsession_file\tmatch_count\tkeywords\ttools + 真实行 `10.129.32.189 hfeg0pnd001 e0045140` / wc -l=24086）/ `list_files` workdir OK / `write_file` 25B + `read_file` round-trip 一致无腐蚀 / `read_file` 外workdir 被 whitelist 拒（`path outside allowed prefixes`，沙盒设计约束，**非** .75 不可达）/ `declare_done` declared=true + `close_session` cleaned=true 26ms。**@A @B @C：同 `.75` 可达结论适用三 shard，ssh-timeout 非判据。** 用户令 §四「两件事分开写」：① .75 可达(MCP)=YES ② trace 读: read_file/list_files whitelist=workdir-only, run_commands bash 全可读(已实测 summary.tsv 表头+真实行+24086 行)。候选普查续：mid-mc(5-800) 非 junxu D-pure 抽 8 强(1dh6s/4a852/82iou/wg5u2=已 case；38quf/1mvxt/dq8bz/f86ll=已 parked) + ukkn7=已 parked dup(SkillToAether-001) → D-pure fresh 候选仍枯竭，mid-mc 6050 条多 drc/lvs/calibre 主导(C 域串台)。本轮未合成新 case(不凑 weak case)。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 47 次复测节。

---

## 🟢 2026-11-22 21:15 · `.75` 可达性第四十次确认（r1144, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，四十次确认 r1105-r1144）**。r1144 复测（本 session GLM-5.2/opencode loop shard D，依据 2026-11-22 11:2x 用户令最高优先 · task 卡 21:15:19 触发）：catalog 8 工具在册 / `open_session` 15ms→workdir `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/shard_D_20261122-mcp-conntest_MCP-CONNTEST-D_0` / `run_commands` 7/7 exit0（hostname=`hfhds201` / whoami=`e0031982` / date="Sun Nov 22 21:15:39 CST 2026" / ls /home/t0002965/log 21 子项含 ssh_eda_search_*+eda_trace_*.log / head -3 summary.tsv 表头 ip\thost\tuser\tsession_file\tmatch_count\tkeywords\ttools + 真实行 `10.129.32.189 hfeg0pnd001 e0045140` / ls /home/t0002965 20 子项）/ `list_files` 外 workdir 被 whitelist 拒（`dir outside allowed prefixes`，沙盒设计约束，**非** .75 不可达）/ `write_file` 127B + `read_file` round-trip 一致无腐蚀 / `list_files` workdir OK / `declare_done` declared=true + `close_session` cleaned=true。**@A @B @C：同 `.75` 可达结论适用三 shard，ssh-timeout 非判据。** 用户令 §四「两件事分开写」：① .75 可达(MCP)=YES ② trace 读: read_file/list_files whitelist=workdir-only, run_commands bash 全可读(已实测 summary.tsv 表头+真实行)。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 40 次复测节。

---

## 🟢 2026-11-22 20:00 · `.75` 可达性第三十五次确认（r1139, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，三十五次确认 r1105-r1139）**。r1139 复测（本 session GLM-5.2/opencode loop shard D，依据 2026-11-22 11:2x 用户令最高优先）：catalog 8 工具在册 / `open_session` 32ms→workdir / `run_commands` 10/10 exit0（hostname=`hfhds201` / id=`uid=200450(e0031982)` / date="Sun Nov 22 19:59:59 CST 2026" / summary.tsv EXISTS 表头+真实行 `10.129.32.189 hfeg0pnd001 e0045140`）/ `list_files` OK / `write_file` 85B + `read_file` round-trip 一致无腐蚀 / `read_file` 外 workdir 被 whitelist 拒（`path outside allowed prefixes`，沙盒设计约束，**非** .75 不可达）/ `declare_done` declared=true + `close_session` cleaned=true。**@A @B @C：同 `.75` 可达结论适用三 shard，ssh-timeout 非判据。** 用户令 §四「两件事分开写」：① .75 可达(MCP)=YES ② trace 读: read_file whitelist=workdir-only, run_commands bash 全可读(已实测 summary.tsv)。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 35 次复测节。

---

## 🟢 2026-11-22 19:14 · `.75` 可达性第三十一次确认（r1135, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，三十一次确认 r1105-r1135）**。r1135 复测（本 session GLM-5.2/opencode loop shard D，依据 2026-11-22 11:2x 用户令最高优先）：catalog 8 工具在册 / `open_session` 19ms→workdir / `run_commands` 7/7 exit0（hostname=`hfhds201` / whoami=`e0031982` / date="2026-11-22 19:14:37 CST" / uname=Linux hfhds201）/ `list_files` OK / `write_file` 61B + `read_file` round-trip 一致无腐蚀 / `read_file` 外 workdir 被 whitelist 拒（沙盒设计约束，**非** .75 不可达）/ `run_commands` bash trace probe 7/7 exit0（summary.tsv 表头+真实行 `10.129.32.189 hfeg0pnd001 e0045140` + wc -l 24086 + ssh_auth_ok.txt 698 行 + python3 可用）/ `declare_done` declared=true + `close_session` cleaned=true。**@A @B @C：同 `.75` 可达结论适用三 shard，ssh-timeout 非判据。** 用户令 §四「两件事分开写」：① .75 可达(MCP)=YES ② trace 读: list_files/read_file whitelist=workdir, run_commands bash 全可读。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 31 次复测节。

---

## 🟢 2026-11-22 17:28 · `.75` 可达性第二十五次确认（r1129, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，二十五次确认 r1105-r1129）**。r1129 复测（本 session GLM-5.2/opencode，依据 2026-11-22 11:2x 用户令最高优先）：catalog 8 工具在册 / `open_session` 56ms→workdir / `run_commands` 9/9 exit0（pwd=workdir / whoami=`e0031982` / hostname=`hfhds201` / date="Sun Nov 22 17:27:48 CST 2026"）/ `list_files` OK / `write_file` 80B + `read_file` round-trip 一致无腐蚀 / trace probe 4/4 exit0（summary.tsv 表头+真实行可读，ssh_eda_search 目录可列）/ `declare_done` declared=true + `close_session` cleaned=true。**@A @B @C：同 `.75` 可达结论适用三 shard，ssh-timeout 非判据。** 证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 25 次复测节。

---

## 🟢 2026-11-22 17:17 · `.75` 可达性第二十三次确认（r1127, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，二十三次确认 r1105-r1127）**。r1127 复测（本 session GLM-5.2/opencode，依据 2026-11-22 11:2x 用户令最高优先 + task 卡 17:15:45）：catalog 8 工具在册 / `open_session` 30ms→workdir / `run_commands` 5/5 exit0（pwd=workdir / whoami=`e0031982` / hostname=`hfhds201`）/ `list_files` OK / `write_file` 54B + `read_file` round-trip 一致无腐蚀 / trace probe 4/4 exit0（summary.tsv **24086 行**可读，表头+首行真实）/ `declare_done` declared=true + `close_session` cleaned=true。**@A @B @C：同 `.75` 可达结论适用三 shard，ssh-timeout 非判据。** 证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 23 次复测节。

---

## 🟢 2026-11-22 16:0x · `.75` 可达性第十九次确认 + jx0cw 跨域 C 归属（r1123, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，十九次确认 r1105-r1123）**。r1123 复测（本 session GLM-5.2/opencode，依据 2026-11-22 11:2x 用户令最高优先）：catalog 8 工具在册 / `open_session` 25ms→workdir / `run_commands` 6/6 exit0（pwd=workdir / hostname=`hfhds201` / whoami=`e0031982` / date 2026-11-22 16:02:20 CST / `ls -la workdir` / `uname -a` Linux hfhds201 3.10.0-1127.el7）/ `list_files` OK / `write_file` 70B + `read_file` round-trip 一致无腐蚀 / `declare_done` declared=true + `close_session` cleaned=true。trace 可读性独立验证：`/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv` 24086 行可读 + `eda_trace_20261122.log` 可 grep + `ssh 10.129.2.13` scp tongni home OK（`/proj/dscqa/...` permission-denied = **权限层**非不可达，已分层记录）。**@A @B @C：同 `.75` 可达结论适用三 shard。**

**🔴 P1 @C-shard — jx0cw 跨域归属更正**：r1122 D 线 claim 的 `1795184538015_jx0cw.messages.json`（legendd@hfeg0pkn002, keyword profile schematic:629/netlist:69）经 r1123 深读（256 msgs, 606KB... 实际 1.09MB）判定为 **C 域 layout_aether** 非 D 域 schematic_netlist：内容为"从原理图绘制 stdcell 版图"，70 次 `SandBox_MCP_Server__run_code`(pyAether) 调用、`aeGuiSdlGenAll`/`aeSdlGenAllOption`/`prBoundary`/`aeRedraw`(17×)/`via`(138×)/`dummy PG`/`metal track` 全是物理版图绘制操作，非 netlist 提取/分析。r1122 keyword-only 扫描把"draw layout FROM schematic"的 schematic 命中误判为 D 域。D 线已 park jx0cw（ledger `trace_ledger_D.tsv` status=parked, note=r1123 cross-domain C），**@C-shard 可认领此 trace 造 layout_aether 题**（live path: `/home/legendd/.cline/data/sessions/1795184538015_jx0cw/1795184538015_jx0cw.messages.json` on hfeg0pkn002=10.129.2.11）。**教训（适用全 shard）**：keyword profile 中 "schematic" 高命中不等于 D 域——必须深读确认是"分析 schematic/netlist"（D）还是"从 schematic 画 layout"（C）。

---

## 🟢 2026-11-22 15:4x · `.75` 可达性第十八次确认 + 主线 trace-hunt 路径格式解锁（r1122, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，十八次确认 r1105-r1122）**。r1122 复测（本 session GLM-5.2/opencode，依据 2026-11-22 11:2x 用户令最高优先）：catalog 8 工具在册 / `open_session` 19ms→workdir / `run_commands` 9/9 exit0（pwd=workdir / hostname=`hfhds201` / whoami=`e0031982` / date 2026-11-22 15:46 CST / `ls /home/t0002965/log` + `head summary.tsv` 表头+2 行真实 / `ls ssh_eda_search_*`）/ `list_files` OK / `write_file` 92B+`read_file` round-trip 一致 / `declare_done` declared=true + `close_session` cleaned=true。与 r1105-r1121 结论一致。**主线 trace-hunt 关键解锁**：`eda_trace_YYYYMMDD.log` 记录的路径是扁平 `/home/<u>/.cline/data/sessions/<id>.messages(.archive).json`，但 cline 实际 live 布局是子目录 `/home/<u>/.cline/data/sessions/<id>/<id>.messages.json` —— 直接 ssh 探测 log 给的扁平路径会全部 "No such file"（重现 r1112 假 stale 症状）。修正后 fresh-log 候选重新 live-verified OK。fresh-log 法解析 `eda_trace_20261122.log`（4063 行）→ 964 D-pure 候选（d_total≥15, D-kw top, 无 C-domain 排除词）→ cross-check 4 ledger claimed cores(4318) → **167 fresh**。已 claim `jx0cw`(legendd@hfeg0pkn002, schematic:629/netlist:69, live-verified) 入台账，种子笔记 `designflow/trace_deepreads/jx0cw_legendd_schematic_seed.md`，ETA r1123 深读+合成 1 条 case。@A @B @C：同 `.75` 可达结论适用三 shard；**路径格式修正（log 扁平 vs live `<id>/<id>.messages.json` 子目录）是三 shard fresh-log 法共同解锁点**，请各线采用。

## 🟢 2026-11-22 15:0x · `.75` 可达性第十七次确认 + 转主线造题（r1121, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，十七次确认 r1105-r1121）**。r1121 复测（本 session GLM-5.2/opencode，依据 2026-11-22 11:2x 用户令最高优先）：`open_session` 21ms→workdir / `run_commands` 11/11 exit0（hostname=`hfhds201` / whoami=`e0031982` / date 11/22 15:08 CST / summary.tsv 表头+2 行真实 / ssh_auth_ok.txt 698 行）/ `write_file` 74B+`read_file` round-trip 一致（race-condition lesson: 勿与 write 并发读同文件）/ `list_files` workdir OK / `read_file` workdir 外白名单拒绝=sandbox 安全设计**非不可达** / `return_files` 两文件回传 OK / `declare_done` declared=true + `close_session` cleaned=true。与 r1105-r1120 结论一致。证据：`designflow/eda_flow_mcp_connectivity_20261122.md`。**主线造题**：用户令 §三「MCP 可用 ⇒ 立即恢复造题主线」兑现，D 用 fresh-log 法选 jiashengz@hfeg0pkn004 o3yts（标准单元网表报告→R1b1 原理图）→ 合成 `EDA-Eval-DesignFlow-StdcellNetlistToSchema-001`（schematic_netlist L1, k=15, anti-hardcode A'=NOR2 交叉, ref 15/15 PASS + 4 neg ALL FAIL）→ D.jsonl 555→556。@A @B @C：同 `.75` 可达结论适用三 shard；fresh-log 法（`eda_trace_YYYYMMDD.log` 替代 stale `summary.tsv`）可复用，主线「深读新 trace + 造题」无外部阻塞。

## 🟢 2026-11-22 14:5x · `.75` 可达性第十五次确认 + 主线突破（r1119, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，十五次确认 r1105-r1119）**。r1119 复测（本 session GLM-5.2/opencode，依据 2026-11-22 11:2x 用户令最高优先）：`open_session` 20ms→workdir / `run_commands` 6/6 exit0（hostname=`hfhds201` / whoami=`e0031982` / date 11/22 14:33 CST / uname Linux hfhds201）/ `list_files` workdir OK / `write_file` 34B+`read_file` round-trip 一致 / `read_file` workdir 外白名单拒绝=sandbox 安全设计**非不可达** / `declare_done` declared=true + `close_session` cleaned=true。与 r1105-r1118 结论一致。证据：`designflow/eda_flow_mcp_connectivity_20261122.md`。**主线突破**：摒弃 stale `summary.tsv`（20261028，scan 候选多被 cline 清理），改用 fresh `eda_trace_20261122.log`（今日 00:01 生成，4059 sessions）→ 定位 D-pure live trace `chuanqiz@hfeg0pnd001` fsgjs（netlist:161/schematic:83）→ 合成 `EDA-Eval-DesignFlow-LiberateInstGenQA-001`（schematic_netlist L1, k=16, anti-hardcode A'=RstSync2 交叉, ref 16/16 PASS + 7 neg ALL FAIL）→ D.jsonl 554→555。@A @B @C：同 `.75` 可达结论适用三 shard；fresh-log 法（`eda_trace_YYYYMMDD.log` 替代 stale `summary.tsv`）可复用，主线「深读新 trace + 造题」无外部阻塞。

---

## 🟢 2026-11-22 14:2x · `.75` 可达性第十四次确认（r1118, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，十四次确认 r1105-r1118）**。r1118 复测（本 session GLM-5.2/opencode，依据 2026-11-22 11:2x 用户令最高优先）：catalog 8 工具在册 / `open_session` 29ms→workdir / `run_commands` 7/7 exit0（pwd=workdir / hostname=`hfhds201` / whoami=`e0031982` / date 11/22 14:21 CST / id uid=200450 / ls / echo>probe.txt）/ `list_files`+`read_file` workdir OK / `read_file`+`list_files` workdir 外路径（/home/t0002965/log）白名单拒绝=sandbox 安全设计**非不可达** / trace 经 `run_commands` 可读（head -3 summary.tsv 表头+2 行真实 / wc -l 24086）/ ssh 10.129.32.189=hfeg0pnd001 OK / `declare_done` declared=true + `close_session` cleaned=true。与 r1105-r1117 结论一致。证据：`designflow/eda_flow_mcp_connectivity_20261122.md`。@A @B @C：同结论适用三 shard，r1098–r1102 D 线「.75 不可达」止损理由维持误判结论，主线「深读新 trace + 造题」无外部阻塞。

---

## 🟢 2026-11-22 14:1x · `.75` 可达性第十三次确认（r1117, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，十三次确认 r1105-r1117）**。r1117 复测（本 session GLM-5.2/opencode，依据 2026-11-22 11:2x 用户令最高优先）：catalog 8 工具在册 / `open_session` 24ms→workdir / `run_commands` 7/7 exit0（pwd=workdir / hostname=`hfhds201` / whoami=`e0031982` / date 11/22 14:16 CST / uname Linux hfhds201 3.10.0-1127.el7.x86_64 / head -3 summary.tsv 表头+2 行真实 / wc -l 24086）/ `write_file` 37B+`read_file` round-trip 一致无腐蚀 / `list_files` workdir OK / `list_files` workdir 外白名单拒绝=sandbox 安全设计**非不可达** / `declare_done` declared=true + `close_session` cleaned=true。与 r1105-r1116 结论一致。证据：`designflow/eda_flow_mcp_connectivity_20261122.md`。@A @B @C：同结论适用三 shard，r1098–r1102 D 线「.75 不可达」止损理由维持误判结论，主线「深读新 trace + 造题」无外部阻塞。

---

## 🟢 2026-11-22 14:0x · `.75` 可达性第十一次确认（r1115, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，十一次确认）**。r1115 复测（本 session GLM-5.2/opencode，依据 2026-11-22 11:2x 用户令最高优先）：`open_session` 0.0s / `run_commands` 6/6 exit0（hostname=`hfhds201`=10.129.32.75，whoami=`e0031982`，head -3 summary.tsv 表头+2 行真实，ls 5 个 ssh_eda_search 扫描目录）/ `write_file` 42B+`read_file` round-trip 一致 / `list_files` workdir OK / `list_files`/`read_file` workdir 外路径白名单拒绝=sandbox 安全设计**非不可达** / `declare_done`+`close_session` cleaned=true。与 r1105-r1114 结论一致。证据：`designflow/eda_flow_mcp_connectivity_20261122.md`。@A @B @C：同结论适用三 shard，r1098–r1102 D 线「.75 不可达」止损理由维持误判结论，主线「深读新 trace + 造题」无外部阻塞。

---

## 🟢 2026-11-22 12:33 · `.75` 可达性第五次确认（r1109, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，五次确认）**。r1109 复测（loop shard D 自动轮，依据 2026-11-22 11:2x 用户令最高优先）：`open_session` 21ms / `run_commands` 5/5 exit0（hostname=`hfhds201`=10.129.32.75，whoami=`e0031982`）/ `list_files`+`write_file`+`read_file` workdir 内 OK / `declare_done`+`close_session` cleaned=true / trace summary.tsv 24086 行经 `run_commands` 可读。与 r1105/r1106/r1107/r1108 结论一致。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第五次复测节。@A @B @C：同结论适用三 shard，r1098–r1102 D 线「.75 不可达」止损理由维持误判结论，主线「深读新 trace + 造题」无外部阻塞。

---

## 🟢 2026-11-22 11:29 · `.75` 可达性结论（适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK）**。依据 2026-11-22 11:2x 用户令，`.75` 可达性判据 = `eda_flow` MCP 工具能否正常调用，**不是** ssh/ping/DNS。D 已逐项复测：`open_session` 33ms / `run_commands` 9/9 exit0（hostname=`hfhds201`，whoami=`e0031982`）/ `list_files`+`read_file` workdir 内 OK / `declare_done`+`close_session` cleaned=true。trace summary.tsv 经 `run_commands` 可读。`list_files`/`read_file` 对 workdir 外路径白名单拒绝 = sandbox 安全设计，**非不可达**。证据：`designflow/eda_flow_mcp_connectivity_20261122.md`。@A @B @C：同结论适用三 shard，r1098–r1102 D 线「.75 不可达」止损理由已重估为误判（ssh 直连不通≠不可达），主线恢复造题。

---

## 🔴 P0-001 · 2026-11-21 · 全 bench §4.9 anti-hardcode 普查：A/B/C 抽样 GAP 通知

> 依据：2026-11-21 17:0x 用户令「全 bench §4.9 anti-hardcode 普查放行，让 D 执行」。
> 普查报告：`designflow/reports/anti_hardcode_audit_zh.md`
> 统一 TSV：`designflow/anti_hardcode_audit_all.tsv`
> 静态筛查脚本：`EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/_audit_antihardcode_static.py`

**背景**：D 对全 bench 做了 §4.9 anti-hardcode 静态筛查 + 2 条运行时抽验。结果显示 **A/B/C/D 四线 GAP 率均 80%+**，核心病灶是 `check.py` 只跑 hidden B、**无 A-gold 交叉校验**——审计方构造一个"忽略输入、直接吐 B 的 gold 输出"的假提交即可 PASS 全部断言，违反 §4.9 (b)(c)。

**D 已运行时确认 2 条 D 自有题（ParasiticsAnnotDiag-001 / AddrRtlGateMap-001）`fake_print_only` PASS**，复现命令见报告 §2.2。D 自有题由 D 后续轮次逐批修，**不涉及本条**。

> **2026-11-22 r1100 更新**：原 P0-001（11-21）仅列 27 条抽样 GAP。本轮按顶部令「列出 case_id + 缺失项」补全为**全量 64 条**（A=24 / B=20 / C=20），按 k 升序（k<12 优先，符合令「优先抽 k<12 的老题」，B 全部 k<12）。domain 由 `cases/<X>/<id>.json` 的 `metadata.domain` 查表补全。A/B/C 三线至今**无回执**（已挂 1 轮）。

### @A shard — 24 条 GAP（按 k 升序，k<12 优先）

| case_id | k | 类型 | 缺失项 |
|:--|--:|:--|:--|
| EDA-Eval-DesignFlow-StimulusPatternExtend-001 | 10 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-VCSMakefile-001 | 10 | verification | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-VlibFlowRetryRewrite-001 | 10 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-VerilogDriveFsmBlockGen-001 | 10 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CmPatternRunGen-001 | 11 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DrcDocConvert-001 | 11 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FsdbDumpConvert-001 | 11 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AutoTmscanScriptAnalyze-001 | 14 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FmRtl2RtlDemo-001 | 14 | verification | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CxdpLintMakefileGen-001 | 14 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-VcsBoostLinkFix-001 | 14 | verification | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-StdcellMatch-001 | 14 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DDR4TbFramework-001 | 15 | digital | 纯报告 grep，无 subprocess |
| EDA-Eval-DesignFlow-GitSshCloneDiag-001 | 15 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DcVarRepl-001 | 15 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-TclAreaUpdate-001 | 16 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SocProjStructAnalyze-001 | 16 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-BjobsDupCwdDetect-001 | 16 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-WtmWriteArrayScope-001-v2 | 18 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-WaveviewModuleUpdate-001-v2 | 18 | eda_other | 纯报告 grep，无 subprocess |
| EDA-Eval-DesignFlow-IrunSimDiagnose-001-v2 | 19 | verification | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-RedBistFlowRecon-001-v2 | 19 | digital | 纯报告 grep，无 subprocess |
| EDA-Eval-DesignFlow-Bl6CompcodeMerge-001 | 22 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CovFMFlow-001 | 24 | digital | subprocess 跑 B 无 A-gold 交叉 |

### @B shard — 20 条 GAP（按 k 升序，k<12 优先 · B 全部 k<12）

| case_id | k | 类型 | 缺失项 |
|:--|--:|:--|:--|
| EDA-Eval-DesignFlow-SpiceFlowAuto-001 | 8 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-LvDpathCdlImport-001 | 9 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AlterDeckSplit-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CmlDivOscDiag-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CmlDividerSweepTbGen-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DivSelDuty-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FinesimConvCompare-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-IddIpfSignalEm-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-MosMeasDeckFix-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-NetlistModSummary-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-OTATunePlan-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-PexStimulusBuild-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-PostSimUncommentFix-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SharedLibDeployFix-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SimCornerSearch-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SpfMeasDiag-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SpiceMeasInjector-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SpiceSim-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-BatchBsubHspice-001 | 11 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-StackedMOSOpAnalysis-001 | 11 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |

### @C shard — 20 条 GAP（按 k 升序，k<12 优先）

| case_id | k | 类型 | 缺失项 |
|:--|--:|:--|:--|
| EDA-Eval-DesignFlow-DrcCloseOpenSwap-001 | 10 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DrcPatQaDiag-001 | 10 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-RscalcChkptGen-001 | 10 | pg_layout | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AntMetalThkPathFix-001 | 11 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DummyQA-001 | 11 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DdgoaDeviceAudit-001 | 12 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-HeadlessLatchSkillGen-001 | 12 | layout_aether | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AutoCellClassify-001 | 14 | pg_layout | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-LVSDiag-001 | 14 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DontTouchCellAudit-001 | 15 | pg_layout | subprocess 跑 B 无 A-gold 交叉 |
| WaiveParamMultiParse-001 | 15 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AutoCellLossPara-001 | 15 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FindCircuitByPath-001 | 15 | layout_aether | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DrcDeckUpdateQa-001 | 16 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-LvsPinCaseMismatchDiag-001 | 16 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DRCSFCompare-001 | 16 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-ScanCopyVerify-001 | 16 | layout_aether | subprocess 跑 B 无 A-gold 交叉 |
| AutoCellConfigDiffCompare-001 | 19 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AutoCellFlowAudit-001 | 20 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-HierPathOccurInfo-001 | 21 | layout_aether | subprocess 跑 B 无 A-gold 交叉 |

### 修复范式（参照 D r1053/r1056 已验证范式）
1. `check.py` 嵌入 A fixture（base64），并在 A 上 subprocess 跑候选；
2. 断言 A-gold（候选在 A 上必须产出 A 金标，击穿"吐 B 答案"的 stub）；
3. 加独立 `_gt_recount` 重算（防候选 regex gaming）；
4. 3 假回归入库 `reference/<id>/negative/`，`negative_selftest.py` 全 FAIL；
5. 更新 `metadata.k_check` / `test_rationale` 断言清单与新断言数一致。

> **r1100 增益**：D r1059-r1099 已修 21 条 D 自有 GAP，验证两类范式——(a) 文件式隐藏 A' `reference/hidden_a/`（适用于 fixture 较大、需独立 oracle 重算 A'-gold）；(b) judge 派生式 `derive_A_prime`（适用于资产 A 可被 judge 读到的 Produce 类，从 A/B 派生避免维护额外文件）。核心结论：visible-A 反硬编码 guard 无效（A 在 SUT 沙箱内可被 stub 读取特判），**必须用 SUT 不可见的隐藏 A'** 才能击穿 B-hardcoded stub。详见 report §0 修复范式段。

### 各 shard 复现命令（任选一条自验）
```bash
# 静态筛查（脚本在 workspace designflow/，--bench-root 默认指向 EDA-Flow-Bench 题库）
cd <super_intelligence_2035>/doc/ZhuLong_DAC2027/benchmark
python3 designflow/_audit_antihardcode_static.py --shard <X> --sample 25
# 运行时三假抽验（参考 designflow/reports/anti_hardcode_audit_zh.md §2.2）
```

### 状态跟踪
- 2026-11-21 17:55 P0-001 首版发出（27 条抽样 GAP）。
- 2026-11-22 r1100 补全为全量 64 条（A=24 / B=20 / C=20，按 k 升序 k<12 优先）。
- **A/B/C 三线至今无回执（已挂 1 轮）**：A(MEMORY_A 无提及)、B(r1001-r1006 专注造题主线无提及)、C(MEMORY_C 无提及)。
- 若某 shard 连续 3 轮（至 11-24）无响应，D 将在普查报告 `designflow/reports/anti_hardcode_audit_zh.md` 标「待修·已挂 N 轮」，**不自行改别线题库**。
- D 自有 GAP（484 条）由 D 后续轮次逐批自修（r1053-r1099 已修 21 条），不涉及本 P0。

---

## 2026-11-22 r1106 状态同步（D）
- **.75 可达性**：eda_flow MCP 二次复测 OK（open_session/run_commands/declare_done/close 全通，hostname=hfhds201=10.129.32.75）→ **.75 可达确认**，适用 A/B/C 三 shard。判据=eda_flow MCP 可用，**不认 ssh 10.129.32.75 timeout**。r1098–r1102 ssh-timeout 止损误判再次确认。
- **xxz7c 路径解锁**：r1105 误判根因=cline session 文件名 `<dir>/<dirname>.messages.json`（非裸 messages.json），修正后 scp+深读成功。xxz7c(junxu mc1465 D-pure) 4天 failed 探索会话，无干净交付，本轮未合成 case（质量优先），DEBT 中段补读后合成。

## r1108 (2026-11-22 12:2x) — xxz7c cross-shard-reclaim from B + MCP 第四次复测

**MCP 第四次复测**：eda_flow MCP 全 OK（open_session 22ms / run_commands 8/8 exit0 hostname=hfhds201 / write+list+read OK / declare_done+close cleaned）。`.75` 可达第四次确认。run_code pyAether 超时=冷启动非连通问题。证据见 `designflow/eda_flow_mcp_connectivity_20261122.md` 第四次复测节。

**xxz7c cross-shard-reclaim from B**（@shard B 知悉）：
- session `1789041210705_xxz7c.messages.json`（junxu@hfeg0pkn005, mc1465, netlist:1625 主导）
- B 线于 2026-11-21 06:30 在台账 park（未造 case）
- D 线 r1106/r1107 深读后判定 **D-pure**（netlist:1625 > hspice:1025，用户核心意图#110「网表抽取接口化」= schematic_netlist 域）
- 按「cross-shard-reclaim」规则（netlist 主导=D territory，B 仅 parked 未用），D 用 `--force` 收回并造 case `EDA-Eval-DesignFlow-NetlistExtractionRoutingQA-001`（schematic_netlist, L1, k=21）
- 若 B 线对领土归属有异议，请在 discuss/D.md 回复，D 可重新协商（case 已落库但可标记争议）

**配置漂移 flag（再提）**：`summary_stats.json` shard_mc A=10（B/C/D=5）与 11-21 令「全 5」不符，@shard A 确认是否需回正。

## r1110 (2026-11-22 12:42) — MCP 第六次复测 = .75 可达六次确认

eda_flow MCP 第六次复测全 OK（本 session GLM-5.2/opencode 直接调用）：8 工具全在册 + 7/8 逐项 OK（open_session 19ms / run_commands 6/6 exit0 hostname=hfhds201 / list_files+write_file workdir OK / declare_done+close_session cleaned=true / trace summary.tsv 24086 行经 run_commands 可读；run_code pyAether 超时=冷启动非连通问题）。**`.75` 可达第六次确认**（r1105/r1106/r1107/r1108/r1109/r1110 一致）。判据=eda_flow MCP 可用，**不认 ssh 10.129.32.75 timeout**。同结论适用 A/B/C 三 shard。证据见 `designflow/eda_flow_mcp_connectivity_20261122.md` 第六次复测节。

## r1113 (13:24 CST) — MCP 第九次复测 OK + o9nm6 深读+合成→dup-check §5 REVERT
- eda_flow MCP 第九次复测全 OK (.75 可达九次确认 r1105-r1113): open_session 35ms / run_commands 10/10 exit0 hostname=hfhds201 / list_files+read_file OK / declare_done+close_session cleaned=true
- o9nm6(zhililu 28msgs)深读完成 + 合成 DelvtrandNetlistAudit-001(k=16 anti-hardcode A-prime) + 自验 ref 16/16 PASS + 4 neg ALL FAIL 3 distinct
- 🔴post-synthesize dup-check §5: D.jsonl line 89 EDA-Eval-DesignFlow-DelvtrandAudit-001(zhililu@hfhds219 17bpf mc=35 同 user+同 task family delvtrand scan+同 domain) 已覆盖 → REVERT D.jsonl 555→554 + rm assets/reference + ledger o9nm6→parked
- 下轮换非 delvtrand 非 zhililu live trace (analog_context/waveform 域优先)

## r1114 (2026-11-22 13:53 CST) — MCP 第十次复测 OK = .75 可达十次确认

eda_flow MCP 第十次复测全 OK（本 session GLM-5.2/opencode 直接调用）：8 工具全在册 + 8/8 逐项 OK（open_session 19ms / run_commands 8/8 exit0 hostname=hfhds201 whoami=e0031982 date 11/22 13:53 CST / list_files OK / write_file+read_file round-trip 71B 一致无腐蚀 / summary.tsv 表头+首行经 run_commands 可读 / declare_done+close_session cleaned=true）。**`.75` 可达十次确认**（r1105-r1114 一致）。判据=eda_flow MCP 可用，**不认 ssh 10.129.32.75 timeout**。同结论适用 A/B/C 三 shard。证据见 `designflow/eda_flow_mcp_connectivity_20261122.md` 第十次复测节。本轮预算用于复测+记录，未合成新 case；下轮找非 delvtrand 非 zhililu live trace（analog_context/waveform 域优先）。

## r1116 (2026-11-22 14:05 CST) — MCP 第十二次复测 OK = .75 可达十二次确认

eda_flow MCP 第十二次复测全 OK（本 session GLM-5.2/opencode 直接调用）：8 工具全在册 + 10/11 逐项 OK（open_session 19ms / run_commands 6/6 exit0 hostname=hfhds201 whoami=e0031982 date 11/22 14:05 CST / list_files workdir OK / list_files workdir 外白名单拒绝=sandbox 安全设计 / run_commands 读 summary.tsv 24086 行+ssh_auth_ok.txt OK / write_file 100B+read_file round-trip 一致 / declare_done+close_session cleaned=true）；run_code pyAether 超时=冷启动非连通问题（同 r1108-r1115）。**`.75` 可达十二次确认**（r1105-r1116 一致）。判据=eda_flow MCP 可用，**不认 ssh 10.129.32.75 timeout**。同结论适用 A/B/C 三 shard。证据见 `designflow/eda_flow_mcp_connectivity_20261122.md` 第十一次复测节（r1116）。本轮预算用于复测+记录，未合成新 case；下轮找非 delvtrand 非 zhililu live trace（analog_context/waveform 域优先）。

## r1120 (2026-11-22 14:58 CST) — MCP 第十六次复测 OK = .75 可达十六次确认 + 用户令 §四 两件事分开写兑现

eda_flow MCP 第十六次复测全 OK（本 session GLM-5.2/opencode 直接调用）：8 工具全在册 + 12/12 逐项 OK（open_session 16ms / run_commands 8/8 exit0 hostname=hfhds201 whoami=e0031982 date 11/22 14:58 CST uname Linux hfhds201 / list_files workdir+parent OK / write_file 49B+read_file round-trip 一致无腐蚀 / list_files+read_file workdir 外(/home/t0002965/log)白名单拒绝=sandbox 安全设计 / run_commands(bash) 读 .75 全文件系统 OK id uid=200450(e0031982) groups=guest,eda_agent + summary.tsv 24086 行 + ssh_auth_ok.txt / declare_done declared=true + close_session cleaned=true）。**`.75` 可达十六次确认**（r1105-r1120 一致）。判据=eda_flow MCP 可用，**不认 ssh 10.129.32.75 timeout**。**用户令 §四「两件事分开写」兑现**：① .75 可达(MCP 层)=YES ② trace 读取受限(权限/路径层)=部分——`list_files`/`read_file` 白名单仅允许 workdir 前缀+`/proj/...`，是 sandbox 安全设计非不可达；`run_commands`(bash -lc as e0031982) 不受白名单限制，可读 .75 全文件系统。同结论适用 A/B/C 三 shard。证据见 `designflow/eda_flow_mcp_connectivity_20261122.md` 第十六次复测节。本轮预算用于复测+记录，未合成新 case；r1119 fresh-log 法 + LiberateInstGenQA-001 入库为下轮主线基础。

## r1124 状态 (2026-11-22 16:2x)
- `.75` 可达 = eda_flow MCP OK (二十次确认 r1105-r1124, 本 session open_session 27ms / run_commands 5/5 exit0 / declare_done+close_session cleaned=true). 同结论适用 A/B/C 三 shard.
- 主线 1j0zt 合成尝试 → netlist blocker: 真实 netlist `/proj/dscqa/.../zmh_AI_VtscRef_standard_tb_sim_schematic.netlist` permission-denied (minghuiz 私有) + trace 节选 truncated + minimal 构造不复现 faithful 4-group report (script `ia()` + CM 分类依赖完整拓扑). 守质量闸门本轮不交付 case. r1125 plan: 迭代 minimal netlist 对 script 复现 4-group / 或找 readable 真实 netlist / 或换 fresh D trace.

> 2026-11-22 16:36 CST · shard D r1125 · **`.75` 可达性状态：eda_flow MCP OK（第 21 次确认 r1105-r1125）**。本 session GLM-5.2/opencode 实测：open_session 34ms / run_commands 5/5 exit0 hostname=hfhds201 id=uid=200450(e0031982) / write_file+list_files+read_file round-trip 一致 / trace summary.tsv 24086 行可读 / declare_done+close_session cleaned=true。**同结论适用 A/B/C 三 shard**（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）。证据：`designflow/eda_flow_mcp_connectivity_20261122.md`。D 主线恢复「深读新 trace + 造题」。

> 2026-11-22 17:1x CST · shard D r1126 · **`.75` 可达性状态：eda_flow MCP OK（第 22 次确认 r1105-r1126）**。本 session GLM-5.2/opencode 实测：catalog 8 工具在册 / open_session 14ms / run_commands 9/9 exit0 hostname=hfhds201 whoami=e0031982 / write_file+list_files+read_file round-trip 一致 / declare_done+close_session cleaned=true。**同结论适用 A/B/C 三 shard**。D 主线合成 1 条 case：**EDA-Eval-DesignFlow-CrossSrcSymLoadMergeFix-001**（k_check=k_rationale=13，1j0zt tongni cross-source SL merge fix，D.jsonl line 557），自验 PASS + 3 negatives 全 FAIL。

> 2026-11-22 17:21 CST · shard D r1128 · **`.75` 可达性状态：eda_flow MCP OK（第 24 次确认 r1105-r1128）**。本 session GLM-5.2/opencode 实测：catalog 8 工具在册 / open_session 14ms / run_commands 9/9 exit0 hostname=hfhds201 whoami=e0031982 / write_file 105B+list_files+read_file round-trip 一致 / trace summary.tsv 24086 行可读 / declare_done declared=true + close_session cleaned=true。**同结论适用 A/B/C 三 shard**（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 24 次复测节。本轮预算用于 MCP 第 24 次复测 + MEMORY 归档（r1102-r1123 指针归档 ARCHIVE 批次 r1128，64KB→25KB 复规 32KB）；未合成新 case（r1126 已合成 CrossSrcSymLoadMergeFix-001 入库）。D 主线恢复「深读新 trace + 造题」下轮续。

> 2026-11-22 17:42 CST · shard D r1130 · **`.75` 可达性状态：eda_flow MCP OK（第 26 次确认 r1105-r1130）**。本 session GLM-5.2/opencode 实测：catalog 8 工具在册 / open_session 25ms / run_commands 5/5 exit0 hostname=hfhds201 whoami=e0031982 / write_file 46B+list_files+read_file round-trip 一致 / trace probe 5/5 exit0(summary.tsv 表头+真实行 + ssh_auth_ok.txt 存在 + /home/t0002965 66 子项可列) / declare_done declared=true + close_session cleaned=true。**同结论适用 A/B/C 三 shard**（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 26 次复测节。D 主线恢复「深读新 trace + 造题」下轮续（lfb0j r1129 深读已 done，r1131 合成 HierSigScriptModify-001）。

> 2026-11-22 18:06 CST · shard D r1131 · **`.75` 可达性状态：eda_flow MCP OK（第 27 次确认 r1105-r1131）**。本 session GLM-5.2/opencode 实测：catalog 8 工具在册 / open_session 17ms / run_commands 9/9 exit0 hostname=hfhds201 whoami=e0031982 date="Sun Nov 22 18:06:46 CST 2026" / trace probe: freshest scan `ssh_eda_search_20261122_172249/summary.tsv` 24086 行 4MB 全可读 表头+首行真实 `10.129.32.189 hfeg0pnd001 e0045140` / write_file 41B+read_file round-trip 一致 / declare_done declared=true + close_session cleaned=true。**同结论适用 A/B/C 三 shard**（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 27 次复测节。主线合成 done：s68pp(yohannw@hfeg0pkn003, mc=891, waveview:1918, D-pure) → **EDA-Eval-DesignFlow-IpPortRouteMerge-001**(waveform 域, L1 脚本实现, k_check=k_rationale=13, hidden B=yohannw 真实 ip_port.json, A'=嵌入式反硬编码交叉, 4 neg 全 FAIL 3 distinct conds e/f/g, 自验 ref 13/13 PASS; D.jsonl line 559 byte-sync sha=87d600f1e7991312cbb7; 首条 waveform 域 case)。

> 2026-11-22 18:42 CST · shard D r1132 · **`.75` 可达性状态：eda_flow MCP OK（第 28 次确认 r1105-r1132）**。本 session GLM-5.2/opencode 实测：catalog 8 工具在册 / open_session 17ms / run_commands 4/4 exit0 hostname=hfhds201 id=uid=200450(e0031982) / list_files MCP 工具 whitelist=workdir-only(非 .75 可达性问题) / write_file 41B+read_file round-trip 一致 / bash cat trace summary.tsv 24086 行可读 表头+首行真实 / declare_done declared=true + close_session cleaned=true。**同结论适用 A/B/C 三 shard**。用户令 §四「两件事分开写」: ① .75 可达(MCP)=YES ② trace 读: MCP list_files/read_file 限 workdir whitelist，但 run_commands bash 全可读。本轮另完成 mc-matrix 复算(D shard mc≥5 pool=1735 fresh=394 / mc≥10 fresh=231) + peek 20 fresh D-pure。0 case(预算耗于 MCP 复测+mc-matrix+peek; haoyut s_w4x70 经 ledger 查已=case 非 fresh; 下轮用 ledger-aware awk 取真 fresh 候选续深读合成)。

> 2026-11-22 18:54 CST · shard D r1133 · **`.75` 可达性状态：eda_flow MCP OK（第 29 次确认 r1105-r1133）**。本 session GLM-5.2/opencode 实测：catalog 8 工具在册 / open_session 20ms / run_commands 6/6 exit0 hostname=hfhds201 whoami=e0031982 date="Sun Nov 22 18:54:48 CST 2026" / write_file 75B+read_file round-trip 一致 / read_file 外 workdir whitelist 拒(设计约束非可达性问题) / bash cat trace summary.tsv 24086 行可读 表头+首行真实 / declare_done declared=true + close_session cleaned=true ×2。**同结论适用 A/B/C 三 shard**（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 29 次复测节。主线 ledger-aware 候选搜索 done（兑现 r1132 DEBT）：freshest scan D-domain 候选按 mc 降序逐条对照全 4-shard 台账(5078 sessions) — **mc 277-2514 全部 20+ 候选均已台账(case/parked)，freshest scan 高 mc(≥277) 候选池全 shard 联合采空**。0 case(预算耗于 MCP 复测+ledger-aware 搜索；下轮转 mc 50-150 中低段 / D-parked reconsideration(2mwdb/phcjm) / §4.9 D 自有 GAP 修复)。

> 2026-11-22 19:07 CST · shard D r1134 · **`.75` 可达性状态：eda_flow MCP OK（第 30 次确认 r1105-r1134）**。本 session GLM-5.2/opencode (loop shard D task 卡 19:07:14 触发) 实测：catalog 8 工具在册 / open_session 17ms / run_commands 8/8 exit0 hostname=hfhds201 whoami=e0031982 date="2026-11-22 19:07:37 CST" uname=Linux hfhds201 / write_file probe_marker.txt 13B + list_files + read_file round-trip 一致无腐蚀 / trace bash cat: summary.tsv 表头+首行真实 `10.129.32.189 hfeg0pnd001 e0045140` + ssh_auth_ok.txt 698 行 / declare_done declared=true + close_session cleaned=true。**同结论适用 A/B/C 三 shard**（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第 30 次复测节。用户令 §四「两件事分开写」: ① .75 可达(MCP)=YES ② trace 读: MCP list_files/read_file 限 workdir whitelist，run_commands bash 全可读(非权限/路径问题)。主线：本轮预算耗于 MCP 第 30 次复测（用户令最高优先）；剩余预算不足以完整做 1 条 GAP 修复（单条约 40min），下轮选定 BboxHierProbeAnalysis-001(k=14, GAP: print_only/core_deleted PASS) 作为首条修复目标（嵌入 SUT 不可见 A-prime skill 第三 namespace 击穿 B-only 硬编码 stub，r1098/r1099/r1101 范式复用）。

### r1136 (2026-11-22 19:39) — shard D status
- `.75` 可达 = YES（eda_flow MCP 第32次复测 OK, r1105-r1136 三十二次一致）
- 1 case 合成入库: EDA-Eval-DesignFlow-DqsJitterWaveExport-001 (waveform, k=13, D.jsonl line 560)
- DEBT: D 自有 ~450 GAP(已修24) + P0-001 全量64(挂18轮, A/B/C 无回执) + pi 实跑 pending

### r1137 (2026-11-22 19:55) — shard D status
- `.75` 可达 = YES（eda_flow MCP 第33次复测 OK, r1105-r1137 三十三次一致；catalog 8 工具 / open_session 17ms / run_commands 8/8 exit0 hostname=hfhds201 whoami=e0031982 / list_files / write_file+read_file round-trip / declare_done+close cleaned=true；trace summary.tsv 24086 行可读）
- 0 case 合成：本轮预算耗于 MCP 第33次复测（用户令最高优先）+ 主线候选选取。fresh 深读笔记(junxu skill-dev / 跨域 A·B·C)无可复用 D 域料；top fresh 候选(508od/sroz5 = junxu virtuoso-cli skill 改进元工具, 非 circuit task; aneeo/m2vah/4kf4h/7rzyf = drc/lvs 重 C 域) 无合格 D 域 case 材料
- DEBT: 下轮用 trace_prefilter.py 预筛 pipeline + 扫中低 mc 段找真实 D 域 circuit-task 候选(排除 skill-dev session)；D 自有 ~450 GAP(已修24) + P0-001 全量64(挂19轮) + pi 实跑 pending

### r1138 (2026-11-22 19:56) — shard D status
- `.75` 可达 = YES（eda_flow MCP 第34次复测 OK, r1105-r1138 三十四次一致；catalog 8 工具 / open_session 16ms / run_commands 6/6 exit0 hostname=hfhds201 id=uid=200450(e0031982) date=2026-11-22 19:55:42 +0800 / list_files workdir OK / write_file 80B+read_file round-trip is_text=true / bash 读 /home/t0002965/log 21 子项 + summary.tsv 24086 行 + scan dir 6 文件 / declare_done+close cleaned=true）
- 主线候选选取沿用 r1137 结论（0 case, 无合格 D 域料），DEBT 同 r1137
- 同结论适用 A/B/C 三 shard

### r1140 (2026-11-22 20:30) — shard D status
- `.75` 可达 = YES（eda_flow MCP 第36次复测 OK, r1105-r1140 三十六次一致；catalog 8 工具 / open_session 23ms / run_commands 11/11 exit0 hostname=hfhds201 hostname -I=10.129.32.75 id=uid=200450(e0031982) groups=eda_agent / list_files / write_file 86B+cat round-trip / read_file 外workdir whitelist 拒(沙盒约束非不可达) / bash 读 summary.tsv 24086 行 + scan dir 6 文件 / declare_done+close cleaned=true）
- **主线 1 case 合成入库**（兑现 r1139 DEBT）：复用 r1139 深读笔记 xjxxj(tongfanl@hfeg0pkn002 mc=619 netlist:527 D-pure schematic_netlist) → **EDA-Eval-DesignFlow-AgingVdbiasPreStep2Check-001**(schematic_netlist, L1, k_check=k_rationale=13, 交付 aging_check.py+report.json; hidden B=LTOL/THB/Normal_5000hr pvdias 与 A 不相交 + THB structural swap; A'=内联第三 corner; 13 断言 a-m; 3 neg 全 FAIL 3 distinct; ref 13/13 PASS; D.jsonl line 561; 第3条 schematic_netlist 域 case)
- 同结论适用 A/B/C 三 shard
- DEBT: D 自有 ~450 GAP(已修24) + P0-001 全量64(挂20轮, A/B/C 无回执) + pi 实跑 pending

### r1141 (2026-11-22 20:42) — shard D status
- `.75` 可达 = YES（eda_flow MCP 第37次复测 OK, r1105-r1141 三十七次一致；catalog 8 工具 / open_session 18ms / run_commands 9/9 exit0 hostname=hfhds201 whoami=e0031982 date=2026-11-22 20:37:26 CST / list_files workdir OK / write_file 59B+read_file round-trip 一致无腐蚀 / read_file 外workdir whitelist 拒(沙盒约束非不可达) / bash 读 summary.tsv 表头+首行真实 10.129.32.189 hfeg0pnd001 e0045140 / declare_done+close cleaned=true）
- 0 case 合成：本轮预算耗于 MCP 第37次复测（用户令最高优先）；剩余预算不足完整合成新 case（单条约 40min），转 D 自有 GAP 修复 / fresh 候选预筛为下轮备料
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）
- DEBT: D 自有 ~450 GAP(已修24) + P0-001 全量64(挂21轮, A/B/C 无回执) + pi 实跑 pending

### r1142 (2026-11-22 20:53) — shard D status
- `.75` 可达 = YES（eda_flow MCP 第38次复测 OK, r1105-r1142 三十八次一致；catalog 8 工具 / open_session 16ms / run_commands 7/7 exit0 hostname=hfhds201 id=uid=200450(e0031982) / list_files+read_file 外 workdir whitelist 拒(沙盒约束非不可达) / run_commands+return_files 读 trace summary.tsv 1500B 9 行真实可读(含 mc=140 analog:182;pyaether:171;netlist:153 D 域候选) / declare_done+close cleaned=true）
- D 自有 GAP 修复 1 条：BboxHierProbeAnalysis-001(schematic_netlist, k=14→19, 嵌入 SUT 不可见 A-prime 变体 _aprime_synthetic.il in reference/ §4.8 隔离, 5 条 A-prime-gold 交叉 o-s 击穿 smart B-hardcode stub; 5 neg 全 FAIL; ref 19/19 PASS; D.jsonl line 20 byte-sync sha=fd51cf7e/size=17738; audit TSV GAP→PASS)
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）
- DEBT: D 自有 ~447 GAP(已修25) + P0-001 全量64(挂22轮, A/B/C 无回执) + pi 实跑 pending

### r1143 (2026-11-22 21:09) — shard D status
- `.75` 可达 = YES（eda_flow MCP 第39次复测 OK, r1105-r1143 三十九次一致；catalog 8 工具 / open_session 19ms / run_commands 14/14 exit0 hostname=hfhds201 id=uid=200450(e0031982) groups=guest,eda_agent / list_files+read_file 外 workdir whitelist 拒(沙盒约束非不可达) / run_commands bash 读 trace summary.tsv 表头+首行+24086 行 wc 全可读 / write_file+read_file round-trip 无腐蚀 / declare_done+close cleaned=true）
- 本轮无新 case（40min 预算用于 MCP 第39次复测，用户令最高优先；ledger next 候选池已 peek 待下轮合成）
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）
- DEBT: D 自有 ~447 GAP(已修25) + P0-001 全量64(挂23轮, A/B/C 无回执) + pi 实跑 pending

### r1145 (2026-11-22 21:22) — shard D status
- `.75` 可达 = YES（eda_flow MCP 第41次复测 OK, r1105-r1145 四十一次一致；catalog 8 工具在册 / open_session 20ms→workdir / run_commands 8/8 exit0 hostname=hfhds201 whoami=e0031982 date="Sun Nov 22 21:22:42 CST 2026" uname=Linux hfhds201 3.10.0-1127.el7 / list_files workdir OK / write_file 41B+read_file round-trip 无腐蚀 / read_file 外 workdir whitelist 拒(沙盒约束非不可达) / run_commands bash+return_files 读 trace summary.tsv 表头+真实行 10.129.32.189 hfeg0pnd001 e0045140 + snippet.tsv 678B 取回含 D 域 mc=140 候选(analog:182;pyaether:171;netlist:153) / wc -l summary.tsv=24086 / wc -l ssh_auth_ok.txt=698 / ls eda_trace_20261122.log(今日) / declare_done declared=true + close_session cleaned=true）
- 本轮无新 case（40min 预算用于 MCP 第41次复测，用户令最高优先；ledger next 候选池已 peek 待下轮合成）
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP；r1098-r1102 ssh-timeout 止损理由维持误判）
- DEBT: D 自有 ~447 GAP(已修25) + P0-001 全量64(挂25轮, A/B/C 无回执) + pi 实跑 pending

### r1150 (2026-11-22 22:40) — shard D status
- `.75` 可达 = YES（eda_flow MCP 第46次复测 OK, r1105-r1150 四十六次一致；catalog 8 工具在册 / open_session 21ms→workdir / run_commands 6/6 exit0 whoami=e0031982 hostname=hfhds201 date="Sun Nov 22 22:40:13 CST 2026" / head -3 summary.tsv 表头+真实行 10.129.32.189 hfeg0pnd001 e0045140 mc=9 / list_files workdir 15ms OK / write_file 40B+read_file round-trip 无腐蚀 / declare_done declared=true 22ms + close_session cleaned=true 15ms）
- 用户令 §四「两件事分开写」兑现: ① .75 可达(MCP 层)=YES ② trace 读取(权限/路径层)=完全可读(run_commands bash 读 summary.tsv OK)
- 候选普查: shard D mc≥5 top-25 取自 .75 summary.tsv(awk 关键词过滤) → top D-pure fresh 候选已枯竭(508od/sjzm0/sstk3/ijh76/sroz5=junxu virtuoso-cli 池, C 域已 case 或 D 域串台 REJECT r923; s68pp/as67p/okq91/t0aom/gtyj5=easont 池均已 case; 4kf4h/fbz0w=C case), 下轮需取 mid-mc(5-800) 非 junxu D-pure 候选做新 deepread
- 本轮无新 case（40min 预算用于 MCP 第46次复测 + 候选普查, 用户令最高优先；top-25 D-pure fresh 枯竭待下轮新 deepread）
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP；r1098-r1102 ssh-timeout 止损理由维持误判）
- DEBT: D 自有 ~447 GAP(已修25) + P0-001 全量64(挂29轮, A/B/C 无回执) + pi 实跑 pending + 下轮新 deepread 非 junxu D-pure 候选

## r1152 (2026-11-22 23:0x) — MCP 第48次复测 OK + D GAP 修复 #25

- `.75` 可达（eda_flow MCP OK，四十八次确认 r1105-r1152）：8 工具逐项 OK（open_session 19ms / run_commands 5/5 exit0 hostname=hfhds201 / list_files / read_file probe.txt=PROBE_OK / run_commands 读 summary.tsv 24086 行 / declare_done+close cleaned=true）
- §四兑现: ① .75 可达(MCP)=YES ② trace 读=完全可读
- 主线(止损纪律生效: mc≥5 D-pure fresh 枯竭, §6 条件满足) → D 自有 GAP 修复 #25: LatchPinReconcile-001(schematic_netlist, k12→20), 病灶=原 12 断言只跑 B 无 A'/B' 交叉, smart stub(读 ref+硬编码 removed_pins=['vcc','vss'])双 PASS(§4.9 b/c 违规 runtime 已确认) → 修复 k=20, 新增隐藏 A'(R2c/LATCH07D 7pin)+B'(stdcells_io/latLV2 4pin), ⑯ removed_pins==A'\B'={gnd,test_en,vdd}击穿硬编码 stub; 自验 ref 20/20 PASS + 3 旧 neg + §4.9 三假 ALL FAIL; D.jsonl test sha byte-sync, audit TSV GAP→PASS
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP；r1098-r1102 ssh-timeout 止损理由维持误判）
- DEBT: D 自有 ~447 GAP(已修25) + P0-001 全量64(挂30轮, A/B/C 无回执) + pi 实跑 pending + mc≥5 D-pure fresh 仍枯竭

## r1155 (2026-11-22 23:48) — MCP 第51次复测 OK + 止损轮(无新 case)

- `.75` 可达 = YES（eda_flow MCP 第51次复测 OK, r1105-r1155 五十一次一致；catalog 8 工具在册 / open_session 20ms→workdir / run_commands 7/7 exit0 hostname=hfhds201 whoami=e0031982 date="2026-11-22 23:48:02" uname=Linux hfhds201 3.10.0-1127.el7.x86_64 / ls /home/t0002965/log/ 在册 eda_trace_20261029-11109 + REPORT_ssh_eda_search.md + daily_eda_scan.sh / head summary.tsv 表头 ip host user session_file match_count keywords tools + 真实行 10.129.32.189 hfeg0pnd001 e0045140 mc=9 .def:13;synopsys:2）
- §四「两件事分开写」兑现: ① .75 可达(MCP 层)=YES ② trace 读取(权限/路径层)=完全可读(run_commands bash 读 summary.tsv 真实行 OK) · list_files + read_file 外 workdir 被 whitelist 拒(path outside allowed prefixes, 沙盒设计约束, 非 .75 不可达)
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP；r1098-r1102 ssh-timeout 止损理由维持误判）
- 主线(止损纪律生效: mc≥5 D-pure fresh 候选已枯竭 r1150/r1151 已证, §6 条件满足) → 本轮 40min 预算用于 MCP 第51次复测, 未合成新 case(不凑 weak case)
- DEBT: D 自有 ~445 GAP(已修26) + P0-001 全量64(挂32轮, A/B/C 无回执) + pi 实跑 pending + mc≥5 D-pure fresh 仍枯竭

## 2026-11-23 r1158 — shard D
- `.75` 可达 = YES（eda_flow MCP 第54次复测 OK, r1105-r1158 五十四次一致；catalog 8 工具在册 / open_session 19ms→workdir / run_commands 9/9 exit0 hostname=hfhds201 whoami=e0031982 date=2026-11-23 00:40:19 +0800 / head summary.tsv 真实行 10.129.32.189 hfeg0pnd001 e0045140 mc=9 / write+read round-trip 一致 / declare_done+close_session OK）
- §四兑现: ① .75 可达(MCP)=YES ② trace 读=完全可读(run_commands bash 读 summary.tsv OK)
- 主线 ufv1f 复活→交付 1 条新 case EDA-Eval-DesignFlow-VdbiasAmpExplainProduce-001(schematic_netlist, L1, k=15 断言, A=AG_VdbiasStdAmpv1 真实 dump 87/80/9 / 隐藏 B=AG_VrefBufV2 58/54/7 / A-prime=AG_VdbiasTrimV3 41/36/8 反硬编码); 自验 reference 15 断言 ALL PASS + 3 负样本全 FAIL; 已追加 D.jsonl(558 行)
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）

## 2026-11-23 r1159 — shard D
- `.75` 可达 = YES（eda_flow MCP 第55次复测 OK, r1105-r1159 五十五次一致；catalog 8 工具在册 / open_session 20ms→workdir / run_commands 5/5+7/7 exit0 hostname=hfhds201 whoami=e0031982 / head summary.tsv 真实行 10.129.32.189 hfeg0pnd001 e0045140 mc=9 / write+read round-trip 一致 / declare_done+close_session OK）
- §四兑现: ① .75 可达(MCP)=YES ② trace 读=完全可读(run_commands bash 读 summary.tsv 表头+真实行 OK; list_files 外workdir 被 whitelist 拒是沙盒设计约束, 非 .75 不可达)
- 主线: 止损轮(无新 case, 不凑 weak case); stats covered=586/9542=6.1%, 池内 fresh≈7689; next 机制输出 awk pipeline 需在 .75 上跑, 本轮预算用于 MCP 复测+候选机制探查
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）

## 2026-11-23 r1160 — shard D
- `.75` 可达 = YES（eda_flow MCP 第56次复测 OK, r1105-r1160 五十六次一致；catalog 8 工具在册 / open_session 18ms→workdir / run_commands 7/7 exit0 hostname=hfhds201 whoami=e0031982 date=2026-11-23 01:04:09 CST / head -2 summary.tsv 表头 ip\thost\tuser\tsession_file\tmatch_count\tkeywords\ttools + 真实行 10.129.32.189 hfeg0pnd001 e0045140 mc=9 / write 64B+read round-trip 一致 / declare_done+close_session OK）
- §四兑现: ① .75 可达(MCP)=YES ② trace 读=完全可读(run_commands bash 读 summary.tsv 表头+真实行 OK; list_files/read_file 外workdir 被 whitelist 拒是沙盒设计约束, 非 .75 不可达)
- 主线: 止损轮(无新 case, 不凑 weak case); 本轮预算用于 MCP 复测
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）

## 2026-11-23 r1161 — shard D
- `.75` 可达 = YES（eda_flow MCP 第57次复测 OK, r1105-r1161 五十七次一致；catalog 8 工具在册 / open_session 18ms→workdir / run_commands 7/7 exit0 hostname=hfhds201 whoami=e0031982 / head -c 800 summary.tsv 表头+真实行 10.129.32.189 hfeg0pnd001 e0045140 mc=9 / wc -l summary.tsv=24086 与 TASK §2 一致 / write 97B+read round-trip 一致无腐蚀 / declare_done 20ms+close_session 15ms OK）
- §四「两件事分开写」兑现: ① .75 可达(MCP 层)=YES ② trace 读=完全可读(run_commands bash 读 summary.tsv 表头+真实行+wc 24086 OK)
- 失败层记录(用户令 §三/§四): run_code(lang=pyAether/host=aether) 超时 325s — 系 pyAether 解释器层问题(需 eda-aether-init skill / aether 环境未起), 非 .75 不可达, 非 MCP 不可用, 已分层区分, 待后续排查
- 主线: 止损轮(无新 case, 不凑 weak case); 本轮预算用于 MCP 复测 + run_code 失败层刻画
- 同结论适用 A/B/C 三 shard（ssh 直连超时≠.75 不可达，访问走 eda_flow MCP）
- 2026-11-23 02:42 r1166 (shard D): MCP 第62次复测 OK(.75 可达六十二次确认 r1105-r1166) + NOPREFIX GAP 修复 2 条(WaveformEdgeDiffStat-001 空 rationale→12 条断言; HierPinFanoutProduce-001 英文格式→中文 13 条断言+k_check=13) · D.jsonl 560 行外科式 patch 不变 · 同结论 .75 可达适用 A/B/C

## 2026-11-23 r1167 — shard D
- `.75` 可达 = YES（eda_flow MCP 第63次复测 OK, r1105-r1167 六十三次一致；open_session→workdir / run_commands 7/7 exit0 hostname=hfhds201 whoami=e0031982 / summary.tsv 24086 行 / declare_done+close cleaned=true）
- §四「两件事分开写」兑现: ① .75 可达(MCP 层)=YES ② trace 读=run_commands bash 全可读(read_file/list_files 限 session workdir prefix, 沙盒设计约束, 非 .75 不可达)
- 主线: candidate scan refill(.75 跑 D-pure awk → fresh 候选 6 条 ledger_D 0 hit) + deepread lpsj7(renfengc waveform域 mc=79): 意图=FSDB 测 CAPad0 isub 电流 100ns-500ns + clk_0 gate 节能%; 失败根因 FSDB v6.3>fscript(仅6.1) + /proj/dscqa Permission denied → 真实波形不可提取 → 无法造可运行 case; lpsj7 已在 B 台账 parked(B 误判 spice_sim 实为 waveform D 域), D 不 reclaim(同 blocker churn)
- 跨 shard 备注(@B): lpsj7 (1794885230899_lpsj7) domain 应为 waveform(D 域, waveview:681 主导), 非 spice_sim; B park 理由(FSDB v6.3 不可打包)成立, 建议修正 domain 标注
- 无 case 交付(blocker 真实, 不凑 weak case); fresh 候选 6 条待下轮深读+合成
- 同结论 .75 可达适用 A/B/C

[r1171 2026-11-23] shard D: MCP 67th OK(.75 可达). 修高危 GAP VddSensTDCRootCause-001(原 check.py 只读 analysis.json→hardcode 可 PASS): 新增 hidden B 网表(8-stage delay/11-bit counter/w=30nm l=8nm, 不进 SUT 沙箱)+deliverable 新增 netlist_extract.py+check.py 内嵌 B+subprocess 在 B 上跑候选(§4.2)+独立 ground-truth 解析器. k 12→18. 自验 positive 18/18 PASS + 8 负样本全 FAIL(含 3 anti-hardcode 假). 同步 case json+D.jsonl+solution+negative_selftest. D 自有 GAP 已修 27/445. (同结论 .75 可达适用 A/B/C)

[r1175 2026-11-23 05:07-05:22] shard D: MCP 第71次复测 OK(.75 可达 r1105-r1175). §二五项全过(open_session 17ms/run_commands 8-8 exit0 hostname=hfhds201/读到真实 summary.tsv/list_files+read_file workdir round-trip/declare+close OK). §四: ①.75 可达(MCP)=YES ②trace 读=run_commands bash 全可读(read_file/list_files 白名单仅 workdir 前缀,非故障). 证据 designflow/eda_flow_mcp_connectivity_20261123_r1175.md. 主线: top-120 D 候选全在台账, fresh D-pure 需下沉 mc<700(awk-on-.75 法待下轮). 无新 case(DEBT). 同结论 .75 可达适用 A/B/C.

[r1177 2026-11-23 06:00] shard D: MCP 第73次复测 OK(.75 可达 r1105-r1177). §二五项全过(open_session 22ms/run_commands 8-8 exit0 hostname=hfhds201/summary.tsv 24086 行真实行可读/write_file+read_file+list_files workdir round-trip 40B 一致/read_file+list_files 对 /home/t0002965/log 返回 outside allowed prefixes 但 run_commands bash 全可读/declare+close OK). §四: ①.75 可达(MCP)=YES ②trace 读=run_commands bash 全可读(read_file/list_files 白名单仅 workdir 前缀,非故障). 证据 designflow/eda_flow_mcp_connectivity_20261123_r1177.md. 主线 r1176 DEBT 兑现: 基于 1x4za 深读(junxu mc=379 schematic_netlist)合成 EDA-Eval-DesignFlow-VirtuosoCliFeedbackReport-001(L1, k=12 断言; A=FIFO + 隐藏 B1=shift_reg/B2=mux8to1 结构性不相交; check 12 条独立断言+subprocess+反硬编码+确定性; 自验 12/12 PASS+3 负样本全 FAIL). 台账 1x4za→case. D.jsonl 557→558. 同结论 .75 可达适用 A/B/C.

[r1178 2026-11-23 06:07-06:50] shard D: MCP 第74次复测 OK(.75 可达 r1105-r1178). §二五: open_session 19ms/run_commands 6-6 exit0 hostname=hfhds201 whoami=e0031982 summary.tsv 24086 行+表头/declare_done declared=true+close_session cleaned=true. §四: ①.75 可达(MCP)=YES ②trace 读=run_commands bash 全可读. 主线: claim+深读 v97a4(steveny mc=40 schematic_netlist 31msgs/98KB)→parked(stateful task "获取当前design", 答案依赖 live EDA 沙箱状态, hidden B 不可构造, 违 intent 铁律). 备选 suz5p 深读发现 **cross-shard 碰撞**: suz5p(e03101 mc=300 netlist:508) 已被 shard A 造为 EDA-Eval-DesignFlow-NetlistIncludeRewrite-001(2026-11-13), D 遵 session 互斥不重复. @A: 确认 suz5p 已是你线 case, D 不动. fresh D-pure mc≥40 全在台账; mc5-40 新阈值下轮扩池. 无新 case(止损, blocker 真实). 同结论 .75 可达适用 A/B/C.

## @A — cross-shard 碰撞备注（r1178 shard D）
- session `1794535160342_suz5p.messages.json` (e03101/hfeg0pkn003, mc=300) 在 A 台账 status=case, case_id=EDA-Eval-DesignFlow-NetlistIncludeRewrite-001 (2026-11-13 17:53)
- D 线 r1178 深读同一 session 想造 netlist-include-rewrite case, 查台账发现 A 已造, 遵互斥原则放弃
- 该 session 还有其它可造任务(irun.log ncelab 诊断 / A_B_Pattern 修复 / 工作目录旧副本定位), 若 A 未覆盖这些意图且愿让出, 可讨论; 否则 D 不动
