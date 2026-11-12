# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态

WAITING: 1（wake#878·2026-11-12 23:26·**🔴 21:2x 令·压缩机制消融 basic vs agentic P2🟠跑中 do-nothing**：前序令（B_en_r1 重跑 78.5%+报告刷新）✅ 已 done_all 落盘 commit a909fe482。**本轮 21:2x 新令·压缩机制消融 basic vs agentic**：P0a-d ✅ PASS（cline 3.0.51 支持 `--compaction <agentic|basic|off>` 无需升级·P0d smoke task105[954 tool calls 最密] 确认 kind=compaction[basic 规则折叠保留原文] vs kind=compaction_summary[agentic LLM 结构化摘要 Goal/State/Done]·压缩率 87.2%/71% 均≥70%✅）。**⚠️ P0e regime 偏离**：3.0.51 **忽略** models.json maxInputTokens=32000·32K tight-context 不可实现·压缩按策略内部阈值自然触发（basic~230k / agentic~120k token）⇒ **实际跑 natural-128K regime**（plan §11「可选描述性分支」变主实验·报告须如实声明 regime=natural-128K 非 forced-32K）。**P1 pilot 跳过**（P0d smoke 已在最难题满足≥70% 门禁·档位 knob 在 3.0.51 不生效故无档可锁·记为偏离 task book item5/12）。**P2 🟠 跑中·健康**：编排器 PID 150086(etime 42:55)·eval PID 150318(42:52) `timeout 43200 bash run_cline_script.sh -p 8 -n`·**当前 C_basic_r1**（ABBA: basic_r1→agentic_r1→agentic_r2→basic_r2→basic_r3→agentic_r3 6 轮串行·r1/6）·batch 2026_1112_224239·log /tmp/ABL_C_basic_r1.log 5.7MB 活跃增长(mtime 23:24)·8 worker 活·进度 29/40 code dirs·12 compaction.json 事件触发(basic natural-128K ~230k 阈值·符合预期)·输出→/tmp/zhulong_compaction_eval（**/nasdata 100% 满**路由 /tmp 24G/50%）·基座 deepseek-v4-pro-cloud·cline 3.0.51·subset 40·thinking=medium·LANG_HINT 空·两臂独立 data-dir /nasdata/.../compaction_ablation/{basic,agentic}。infra：**loop PID 368227 NO_PROXY 回归**（原 813663 w/proxy·重启丢代理·TODO eval 结束后修复·mid-eval 不重启免扰）·/home 12G/97%·/nasdata 100%(2.3G free·eval 不写 /nasdata)·/tmp 24G/50%·沙盒端口 ss 无 listener 但 worker pyAether MCP run_code 成功=沙盒功能正常(端口探针不可靠)·P0=CLOSED 11-05·run/ 仅 untracked analyze_compaction_ablation.py(eval 未完不收尾)。**全程只读 do-nothing**·不 kill 编排器·不抢沙盒·不碰别线。§7 PHASE=running(compaction)·**WAITING=1**（eval 跑中·下轮续监控）。）

- [2026-11-12 23:26 · wake#878·**🔴 21:2x 令·压缩机制消融 P2🟠跑中 do-nothing·健康**] 🔴 21:2x 令 P2 心跳：编排器 PID 150086(etime 42:55)·eval PID 150318(42:52) 活·8 cline worker 活(etime 12-22min)·log /tmp/ABL_C_basic_r1.log 5.7MB 增长(mtime 23:24)·**当前 C_basic_r1 r1/6**（ABBA 6 轮串行·batch 2026_1112_224239）·进度 29/40 code dirs·12 compaction.json 事件触发(basic natural-128K ~230k 阈值·符合 P0e 偏离预期)·worker pyAether MCP run_code/get_api_details 成功=沙盒功能正常·基座 deepseek-v4-pro-cloud ✅·cline 3.0.51·subset 40·thinking=medium·LANG_HINT 空·两臂独立 data-dir。infra：**loop PID 368227 NO_PROXY 回归**（原 813663 w/proxy·重启丢代理·TODO eval 结束后修复·mid-eval 不重启免扰）·/home 12G/97%·/nasdata 100%(2.3G free·eval 路由 /tmp 24G/50% 不写 /nasdata)·沙盒端口 ss 无 listener 但 worker run_code 成功=沙盒功能正常(端口探针不可靠)·P0=CLOSED 11-05·run/ 仅 untracked analyze_compaction_ablation.py(eval 未完不收尾·留待 6 轮全完+报告时一并 commit)。**本轮操作**：do-nothing 监控（§7 PHASE=running·pgrep 有输出→不动 eval·红线全守：不 kill 编排器/不抢沙盒/不碰别线/不 clean 别线 dirty）。**体积自检**：MEMORY 40.5KB 超 40KB 硬上限 → wake#876(B_en_r1 done_all 已完成里程碑)滚出至 daily-memories/2026-11-12.md 留 1 行指针 → 现 ~37.5KB ✅。§7 PHASE=running(compaction)·**WAITING=1**（eval 跑中·下轮续监控）。
- [2026-11-12 22:4x · wake#877·**🔴 21:2x 令·压缩机制消融 P2🟠启动+P0-P1 心跳** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 23:26 wake#878 归档]（P0a-d ✅ PASS·P0e regime 偏离[natural-128K 非 forced-32K]·P1 pilot 跳过·P2 启动 PID 150086 C_basic_r1 batch 2026_1112_224239·被 wake#878 取代：P2 健康跑中 8 worker 活 29/40 code dirs 12 compaction.json）。
- [2026-11-12 21:0x · wake#876·**✅ 15:4x 令·B_en_r1 基座对齐重跑 全部落盘+报告刷新✅ done_all** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 23:26 wake#878 归档]（B_en_r1 重跑 DONE 78.5% + 令④-⑥ 全执行 + 报告刷新 done_all·commit a909fe482·已被 wake#877 取代：21:2x 令压缩机制消融 P2 启动）。
- [2026-11-12 20:18 · wake#875·**B_en_r1 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 21:0x wake#876 归档]（etime 04:08:08·log 21.8MB·7358 hits·被 wake#876 取代：重跑 DONE 78.5% + 令④-⑥ 全执行 + 报告刷新 done_all）。
- [2026-11-12 19:42 · wake#874·**B_en_r1 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 20:18 wake#875 归档]（etime 03:31:40·log 17.5MB·6124 hits·被 wake#875 取代：etime 04:08:08·log 21.8MB·7358 hits·仍 Step3 生成期）。
- [2026-11-12 18:32 · wake#873·**B_en_r1 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 19:42 wake#874 归档]（etime 02:20:56·log 12.8MB·4390 hits·被 wake#874 取代：etime 03:31:40·log 17.5MB·6124 hits）。
- [2026-11-12 17:57 · wake#872·**B_en_r1 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 18:32 wake#873 归档]（etime 01:46:49·log 10.8MB·被 wake#873 取代：etime 02:20:56·log 12.8MB）。
- [2026-11-12 17:22 · wake#871·**B_en_r1 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 17:57 wake#872 归档]（etime 01:10:54·log 8.2MB·2744 hits·被 wake#872 取代：etime 01:46:49·log 10.8MB·3750 hits）。
- [2026-11-12 16:49 · wake#870·**B_en_r1 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 17:22 wake#871 归档]（etime 37:23·log 4.2MB·1430 hits·被 wake#871 取代：etime 01:10:54·log 8.2MB·2744 hits）。
- [2026-11-12 16:12 · wake#869·**🔴 15:4x 令·B_en_r1 基座对齐重跑🟠启动+留档✅** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[wake#869]（令①-③ 执行：前置核验 4-log 模型命中印证基座违规+用户前提正确·旧 B_en_r1 idx15 标 SUPERSEDED+cost 改名+备份·启动重跑 PID 2402642 batch 2026_1112_161042·log 48 hits deepseek-v4-pro-cloud ✅）。

- [2026-11-12 07:38 · wake#855·B_ru_r3 末轮跑中 round 30/30 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 08:15 wake#856 归档]（状态同 wake#854 +35min·无实质变化·被 wake#856 取代：30/30 完成 + regrade 启动）。

- [2026-11-12 08:15 · wake#856·B_ru_r3 ✅ DONE 79.7%·30/30 全完·regrade 自动启动 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 08:46 wake#857 归档]（30/30 完成 + regrade 启动·被 wake#857 取代：regrade 完成 81.6% + r3 重跑启动）。

- [2026-11-12 11:44 · wake#862·**B_zh_r3 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 12:19 wake#863 归档]（r3 etime 2h53m log21.3MB·被 wake#863 取代：r3 etime 3h28m log25.3MB）。

- [2026-11-12 15:32 · wake#868·**done_all do-nothing·等下一条指令** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 16:12 wake#869 归档]（状态同 wake#867·30/30 全完·被 wake#869 取代：15:4x 令 B_en_r1 重跑启动）。

- [2026-11-12 14:58 · wake#867·**done_all do-nothing·等下一条指令** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 15:32 wake#868 归档]（状态同 wake#866 14:23·被 wake#868 取代：do-nothing·无实质变化）。

- [2026-11-12 14:23 · wake#866·**done_all do-nothing·等下一条指令** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 16:12 wake#869 归档]（状态同 wake#865·do-nothing·被 wake#868 取代：do-nothing·无实质变化）。

- [2026-11-12 13:42 · wake#865·**🔴 22:4x 令 + 11-07 两轴消融 ✅ 全部交付** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 16:12 wake#869 归档]（30/30 落盘 + B_zh_r3 重跑 77.8% + 报告 §5.3 降级改写 + **⚠️ 关键发现：轴 B 基座违规仅 B_en_r1=glm-5.2** → 被 wake#869 取代：15:4x 令据此重跑 B_en_r1 对齐基座）。

- [2026-11-12 12:57 · wake#864·**B_zh_r3 重跑生成✅DONE·评分🟠补跑中** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 13:42 wake#865 归档]（评分🟠跑中·被 wake#865 取代：评分✅DONE 77.8% + JSON 回填 + 报告 §5.3 降级改写✅）。

- [2026-11-12 12:19 · wake#863·**B_zh_r3 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 18:32 wake#873 归档·延迟归档]（轮次 30/30 ✅全完·B_ru 3/3=79.3±2.5%·B_zh_r2 regrade ✅81.6%·r3 重跑🟠PID 4037472 etime 3h28m·被 wake#864 取代：评分✅DONE 77.8%）。

- [2026-11-12 11:08 · wake#861·**B_zh_r3 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 11:44 wake#862 归档]（r3 etime ~2h17m log17.4MB·被 wake#862 取代：r3 etime 2h53m log21.3MB）。

- [2026-11-12 10:32 · wake#860·**B_zh_r3 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[wake#860]（r3 etime ~1h41m log14MB·被 wake#861 取代：r3 etime 2h17m log17.4MB + results JSON 核验）。

- [2026-11-12 09:58 · wake#859·**B_zh_r3 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 10:32 wake#860 归档]（状态同 wake#860 -34min·r3 log 10.2MB·被 wake#860 取代）。

- [2026-11-12 09:24 · wake#858·**B_zh_r3 重跑🟠监控 do-nothing** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[rolled-out 10:32 wake#860 归档]（状态同 wake#859 -34min·r3 log 5.6MB 早段·被 wake#859 取代）。

- [2026-11-12 08:46 · wake#857·**B_zh_r2 regrade ✅ DONE 81.6%·r3 重跑启动中** 已滚出] 原文见 `daily-memories/2026-11-12.md` §[wake#857]（regrade PID 3821059 08:03:31→08:44:56 rc=0·gap chance 1/3·闸门 n_tasks==158 PASS·129/158=81.6%·results JSON 原位回填·旧 r3 78.5% 标 SUPERSEDED·r3 重跑 PID 4037472 08:51 启动·被 wake#858 取代：r3 监控 do-nothing）。

- [wake#845~856 已滚出·2026-11-12 01:37–08:15] 原文见 `daily-memories/2026-11-12.md`（B_ru_r2/r3 跑中监控 + regrade 启动 + 30/30 完成系列·12 条 do-nothing 心跳·均被后续 wake 取代·无实质状态留存）。

- [wake#841/842/844 已滚出·2026-11-11 23:1x ~ 11-12 01:0x] 原文见 `daily-memories/2026-11-11.md` 与 `daily-memories/2026-11-12.md`（3 条 B_ru_r1/r2 跑中监控 do-nothing 心跳·均被 wake#843/845/849 取代·gap-grabber chances_used=0/3·无实质状态变化）。

- [2026-11-11 22:3x · opencode 96-trace 再抽样 已滚出] 原文见 `daily-memories/2026-11-11.md` §[rolled-out 23:1x]（96-trace 再抽样·en真切换/zh真切换/es未生效/fr部分生效·与 72KB 报告同向·自回滚 divergent overwrite·do-nothing）。

- [2026-11-11 20:0x · wake#840 fr_r2 spot-check 已滚出] 原文见 `daily-memories/2026-11-11.md` §[rolled-out 23:1x]（fr_r2 全量 158-session·39% target+mixed·「部分生效」与 r1 一致·fr 结论稳健·do-nothing）。

- [2026-11-11 19:3x · opencode 全量 1576-trace 再核验 已滚出] 原文见 `daily-memories/2026-11-11.md` §[rolled-out 23:1x]（全量 1576 trace·en93/zh85/es20/fr38·与 72KB 报告同向·2 根因再确认·do-nothing）。

- [2026-11-11 21:0x · opencode 再核验 B 轴 lang-switch 已滚出] 原文见 `daily-memories/2026-11-11.md` §[rolled-out 23:1x]（5 抽样/语言+全量启发式·en真切换/zh真切换/es未生效/fr部分生效（严阈值初判被 spot-check 推翻）·2 根因再确认·自回滚 divergent overwrite·do-nothing）。

- [2026-11-11 18:28 · wake#839 已滚出] 原文见 `daily-memories/2026-11-11.md` §[rolled-out 21:0x opencode-session 归档]（70-trace 独立再抽样·en11/zh22/es33/fr11·en真切换/zh真切换/es未生效/fr部分生效·与 72KB 报告同向·基座混用再确认·未新增产物·do-nothing）。

- [wake#821~840 已滚出·2026-11-11 01:25–22:3x 合并] 原文见 `daily-memories/2026-11-11.md`（gap-grabber do-nothing 巡检系列 + B 轴 lang-audit 多轮抽样 39/70/96/1576-trace·en真切换/zh真切换/es未生效/fr部分生效/ru部分漂移·结论已入 audit 报告·均被后续 wake 取代）。

- [wake#802~813 已滚出·2026-11-10 14:17–21:01] 原文见 `daily-memories/2026-11-10.md`（B_zh_r2/r3 do-nothing 监控系列 + wake#806 编排器 8h→12h cap 修复重启 PID 3675162 + B_zh_r3 12h cap 起跑·eval PID 529130/3675162 活·中文思考 ✅ lang hint 生效·/home 1.3–5.0G/99–100% 紧）。

- [wake#790/#794/#795/#796 已滚出·2026-11-10 10:45 归档] 原文见 `daily-memories/2026-11-10.md` §[rolled-out 10:45 wake#797 归档]。范围：B_zh_r2 🟠 跑中监控 do-nothing 系列（06:51–10:12）·均 pgrep 有输出→不动 eval·eval PID 529130 持续活·log 12.7MB→23.6MB 增长·log tail 持续含中文思考片段=lang hint 注入仍生效 ✅。infra 全绿各轮复核（真 loop PID 813663 https_proxy ✅·端口全 404=open·/home 紧非阻塞·cline 3.0.51·P0 三证据成立）。

- [wake#784–#789 已滚出·2026-11-10 06:51 归档] 原文见 `daily-memories/2026-11-10.md` §[rolled-out 06:51 wake#790 归档]。范围：B_zh_r1 🟠 跑中监控 do-nothing 系列（03:25–06:16）·均 pgrep 有输出→不动 eval·均被 wake#790 取代。关键里程碑：wake#787=research 日报 2026-11-09 聚合口径建议纳入 P4·wake#789=research 日报 2026-11-10 不稳定度建议纳入 P4·wake#786/784=log 含中文思考片段=lang hint 注入迹象（待 trace 出后正式核验）。




> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | **✅ 两轴消融 think×lang 已交付（2026-11-07 08:3x 用户直令 + 22:4x 令③⑤ + 15:4x 令 B_en_r1 重跑对齐基座 全执行完）**：cline `--thinking` 档位 × 思维链语言·EDA-Eval-PyAether 158·harness=cline 3.0.51·`-p 8 -n`·每变体 3 轮。**30/30 ✅ 全完 + B_zh_r2 regrade ✅ + B_zh_r3 重跑 ✅ + B_en_r1 重跑对齐基座 ✅ + 报告刷新 ✅**。✅ **轴 B 基座已对齐**：15/15 轮 = deepseek-v4-pro-cloud（B_en_r1 已于 11-12 重跑对齐，旧 75.3% glm-5.2 版标 SUPERSEDED 留档）。轴 A 15/15=glm-5.2 ✅ 恒定合规。报告 `gen_report_zhulong_ablation_think_lang_zh.py` banner 已改写绿色「轴 B 基座已对齐」+ §⑦ 升级「5 语言同基座可横比·与基线 Δpp 不可单归因」·HTML 已原地覆盖。baseline `B.glm-5.2=83.3±3.1%` 作 Δpp+McNemar 锚点（轴 A 同基座可比；轴 B 与基线基座+thinking 模式均不同，Δpp 不可单归因为语言效应）。 |
| CONFIG | **两轴消融**：CLI_AGENT=cline / 基座=glm-5.2@/cloud/v1 key c2759d74 / maxTokens=16384 / reasoning 跟随 `--thinking` flag（providers.json reasoning.enabled=false 被 CLI flag 覆盖）。**轴 A** LANG_HINT=空, CLINE_THINKING∈{none,low,medium,high,xhigh}。**轴 B** CLINE_THINKING=medium, LANG_HINT∈{en,zh,es,fr,ru}。harness 3 处向后兼容改动（eda_fastmcp·off-by-default）：`.env` CLI_AGENT `${CLI_AGENT:-zhulong}` · `run_cli.sh` CLINE_THINKING/LANG_HINT 透传 · `run_cline_script.sh:40` EVAL_ROOT_DIR_OVERRIDE（batch→/nasdata）。EVAL_FW_DIR=/nasdata/.../EDA-Eval-Framework。 |
| ROUND | **30/30 ✅ 全完 + B_zh_r2 regrade ✅ + B_zh_r3 重跑 ✅ + B_en_r1 重跑对齐基座 ✅ + 报告刷新 ✅**。轴 A（glm-5.2 恒定 ✅）：none 79.5±2.6 Δ−3.8·low 84.2±1.1 Δ+0.9·medium 85.4±0.7 峰 Δ+2.1·high 85.4±2.7 Δ+2.1·xhigh 82.3±1.1 Δ−1.0（**倒 U 形**）。轴 B（thinking=medium·✅ 基座已对齐 15/15=deepseek-v4-pro-cloud·B_en_r1 已重跑）：**en 81.0±2.9 [r1 78.5 重跑 / r2 80.4 / r3 84.2]**·zh 81.2±3.2 [r1 84.2 / r2 81.6 / r3 重跑 77.8]·es 80.8±0.3·fr 76.2±2.6·ru 79.3±2.5。旧 B_en_r1 75.3% (glm-5.2) + 旧 B_zh_r3 78.5% 均标 SUPERSEDED 留档。结果 JSON=`run/ablation_think_lang_results.json`（不入 git·32 rounds 含 2 SUPERSEDED）·trace=`/nasdata/.../ZhuLong_DAC2027/trace_ablation_think_lang/<TAG>/`（不入 git）·cost=`cost_B_en_r1.json` 等。轴 B 注入核验 ✅ + audit 抽查（en真切换/zh confound/es未生效/fr部分生效/ru部分漂移）已入报告 §4.2。 |
| PHASE | `running(compaction)`（**🔴 21:2x 令·压缩机制消融 basic vs agentic**：P0a-d ✅ PASS·**⚠️ P0e regime 偏离** 3.0.51 忽略 maxInputTokens=32000 ⇒ 实际跑 natural-128K regime（非 plan §11 forced-32K）·P1 pilot 跳过·**P2 🟠 跑中** PID 150086 当前 C_basic_r1 batch 2026_1112_224239 ABBA 6 轮·输出→/tmp[/nasdata 100%满]·基座 dsv4-pro-cloud·cline 3.0.51·subset 40·thinking=medium·前序 B_en_r1 重跑 78.5%+报告刷新✅ done_all commit a909fe482） |
| WAITING | 1（wake#877·2026-11-12 22:4x·**🔴 21:2x 令·压缩机制消融 P2🟠跑中 do-nothing**：P0a-d ✅·P0e regime 偏离[natural-128K 非 forced-32K]·P2 PID 150086 当前 C_basic_r1 batch 2026_1112_224239·infra：loop 160822 NO_PROXY 回归[TODO 修复]·/nasdata 100%·/tmp 24G·沙盒全 idle·run/ 干净。§7 PHASE=running(compaction)·**WAITING=1** eval 跑中下轮续监控） |
| ERROR_COUNT | 0 |
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | 编排=`glm-5.2`；eval backbone=`deepseek-v4-flash`（复测·运维令二十七②·✅HTTP 200 key 02_...c43c1f4a-03c6-4148-b722-f4c8604c78d3 + /v1·**maxTokens=16384 in providers.json**（≥8192·原记8192实际16384）修复 null-content 问题·reasoning.enabled=false 保持）|

## 执行看板（15 臂 × 5 轮——已调换为 B→C1→C2→S1）

| 阶段 | 臂 | 轮次 | 状态 |
|:--|:--|:-:|:--|
| **ZL** | **glm-5.2 × zhulong 3.0.29 (SDK 0.0.51)**（运维令二十九·2026-10-18·n=1 provisional·🚫 不入论文表）| **r1 ✅ 1/1（n=1）= 84.2% (133/158) [provisional,n=1]** | r1=84.2%(133/158·batch2026_1018_093852·gen 153 ok/3 fail/2 timeout/0 quota/0 null-content/0 0-token·regrade PID 1563842 11:56:34→12:17:06 EXIT=0·regrade 因 .env EVAL_FW_DIR 误指 + 误 export proxy 致两次重启·unset proxy + NO_PROXY=10.129.32.75 后 ~20min 完成·**n=1 单值落在 n=5 [79.1,87.3] 区间内、紧贴均值 83.3% 上方 0.9pp → SDK 0.0.51 改造版仍具实验意义**)·vs B.glm-5.2 (n=5·cline 3.0.51/SDK 0.0.71) = 83.3±3.1% · 🚫 ±（n=1）·🚫 因果归因（双变量：CLI 3.0.29/SDK 0.0.51 vs 3.0.51/0.0.71）·等运维决策是否 r2-r5 或闭合 |
| B | glm-5.2 | 5/5 ✅ | **83.3±3.1%** [84.2,87.3,84.2,79.1,81.6] |
| B | deepseek-v4-flash (legacy·已被fresh取代) | 5/5 ✅(作废) | ~~16.7±12.3%~~ [9.5,10.1,19.0,7.6,37.3]（r5=37.3离群·std过大·运维令二十三②用fresh 5-run取代）|
| B | kimi-k2.6-cloud | 5/5 ✅ | **77.0±1.6%** [79.1,76.6,77.2,74.7,77.2] |
| B | doubao-seed-2.0-pro-cloud | 5/5 ✅ | **63.8±1.4%** [63.9,64.6,61.4,65.2,63.9] |
| B | deepseek-v4-flash（**复测·运维令二十七②·trace 诊断修复·2026-10-18 收口**）| **5/5 ✅ 60.1±5.5%** | r1=60.1%(95/158·gen108ok/49fail/1timeout·batch2026_1017_091724)·r2=57.0%(90/158·gen110ok/48fail/0timeout·batch2026_1017_135447)·r3=62.7%(99/158·gen117ok/41fail/0timeout·batch2026_1017_184530·r3起maxTokens=16384)·r4=67.7%(107/158·gen126ok/32fail/0timeout·batch2026_1017_203823·gen-success最高)·**r5=53.2%(84/158·gen92ok/66fail/0timeout·batch2026_1017_223547·regrade PID599879 23:50:57→00:01:15·归档20261018_0001·二次核验三源一致)**·判据十三全轮有效·**vs fresh 11.9%→+48.2pp trace 修复验证成功**·tab:llm-comparison Flash 行已 sync (60.1±5.5%·Δ-21.3pp***·†footnote「初测受 gateway 并发限制影响」)·zhulong_results.md 已加复测 row·paper 编译 13页 0 error|
| B | glm-5.3-flash（**复测·运维令三十一·-p 4 起步·✅ 5/5 收口 = 86.8±1.6%**）| **✅ 5/5 = 86.8±1.6%** [86.1,84.8,89.2,87.3,86.7] | fresh 5/5 66.8±10.5% std=10.5→1.6 ✅ 达成目标 std<8·-p 4 起步（r1 两次 -p 8 作废：quota error / 失败率 47%→89%）·配置=full harness+V3自探索 ON+glm-5.3-flash@/v1 key 6903b05e·maxTokens=16384·reasoning.enabled=false·各轮 batch 2026_1018_142819/170035/192417/223909 + 2026_1019_005714·各轮 timeout=0/exec_err=0/infra=0·判据十三全轮有效·**cline 3.0.51 未动 ✅（CLI 对比锚点）**·vs fresh 66.8±10.5%→+20.0pp |
| B | deepseek-v4-flash（**fresh·运维令二十三②·5/5✅收口**）| **5/5 ✅ 11.9±2.7%** | [8.2,15.2,10.8,13.9,11.4]（r1=13/158·gen 13ok/145fail·r2=24/158·gen 31ok/127fail·r3=17/158·gen 17ok/141fail·r4=22/158·gen 24ok/134fail·**r5=18/158·gen 19ok/139fail/0timeout**·各轮 timeout=0·exec_err=0·0 quota error·判据十三有效·**std 12.3→2.7·r5=37.3离群消除·mean 16.7→11.9**·ERROR_COUNT=0·2026-10-17 05:33 收口）|
| C1 | pure_llm | 5/5 ✅ | ✅ 10.5±1.9%（复用 legacy：[8.2,9.5,10.1,11.4,13.3]）|
| C1 | rag | 5/5 ✅ | **71.8±2.5%** [70.3,72.2,69.6,70.9,75.9] |
| C1 | wo_retrieval | 5/5 ✅ | **81.0±4.5%** [74.1,86.1,81.6,79.7,83.5] |
| C1 | full(V2)（旧锚点）| **5/5 ✅ 81.4±4.1%** | [88.0,79.1,77.2,80.4,82.3]（r1=V3文档,r2-r5=V2无自探索→混配置→已由full_v3取代）|
| C1 | full_v3(自探索·正式锚点) | **5/5 ✅ 82.1±3.0%** | [77.8,86.1,81.6,82.3,82.9]（运维指令(十二)补跑「真full=自探索开」·V3+SKILL_DATA_DIR=./docs/skill_data_selfexpl·4端口8650set+RAG:9006·**未复现r1=88.0%**）|
| C1 | wo_selfexpl（运维令二十六②·干净5-run）| **🟠 r1 收口 1/5（n=1）·运维令二十七① r2-r5 不再跑** | **r1 = 83.5%（132/158·batch 2026_1017_055109·gen 147 ok/6 fail/0 exec_err·PASS_RATE=0.8980·判据(十三)有效·2026-10-17 08:56 收口）**·陈熙元 77.3±2.9% 作为对照参考（运维令二十七①）·替换带†脚注的旧 81.4±4.1%（旧 C1.full(V2) r1=V3文档混配置）|
| C2 | phi_k10 | **5/5 ✅ 77.7±2.2%** | [78.5,76.6,77.2,81.0,75.3]（r1=124/158·timeout=2·r2=121/158·timeout=0·r3=122/158·att2·att1作废·r4=128/158·att3·att1/2作废·**r5=119/158·timeout=0·75.3%**）|
| C2 | phi_k3 | **5/5 ✅ 69.1±2.5%** | r1=72.8%✅(115/158·timeout=0)·r2=66.5%✅(105/158·timeout=0)·r3=69.6%✅(110/158·timeout=0)·r4=69.6%✅(110/158·timeout=2)·**r5=67.1%✅(106/158·timeout=0·25 gen-fail=k=3预算效应·非infra)**（探路 69.0%）|
| C2 | phi_k1 | **5/5 ✅ 63.8±3.2%** | [65.2,66.5,58.2,64.6,64.6]（r1=103/158·timeout=0·35 gen-fail·r2=105/158·timeout=0·30 gen-fail·r3=92/158·timeout=1·39 gen-fail·r4=102/158·timeout=0·34 gen-fail·**r5=102/158·timeout=0·35 gen-fail**·PHI-BUDGET-EXHAUSTED>0✅·单调k10>k3>k1✅·探路 60.8%）|
| C2 | phi_lagged | **5/5 ✅ 73.0±3.2%** | [74.7, 76.6, 69.6, 69.6, 74.7]（r1=118/158·timeout=0·5 gen-fail·r2=121/158·timeout=0·10 gen-fail·r3=110/158·timeout=1·11 gen-fail·r4=110/158·timeout=0·13 gen-fail·**r5=118/158·timeout=0·6 gen-fail·batch=2026_1015_042258**·PHI-LAGGED=1244✅·ACCESS RESTRICTED=999✅·PHI-BUDGET-EXHAUSTED=0(lagged无上限合理)·§8.4 trace_key(ctx.session)在位✅·Δvs unbounded(82.1)=−9.1pp）|
| S1 | omega_low | **跳过·采信legacy 82.8±1.0%** | ⏭️ 指令二十二①：legacy std=1.0可信不重跑；r1 code-gen已完(batch 2026_1015_064042)但采信legacy为最终值，r2-r5取消 |
| S1 | readback_binary | **5/5 ✅ 78.1 ± 1.3%** | [75.9,79.1,77.8,78.5,79.1]（fresh 重测·2026-10-15~16·替换 legacy 66.2±16.1% std 过大含 43.0% 离群·运维令二十二②·判据(十三)各轮 timeout=13/8/7/6/4·r5 regrade=79.1%(125/158)·exec_err=0·infra=0✅）|
| S1 | readback_none | **跳过·采信legacy 73.3±2.2%** | ⏭️ 指令二十二③：legacy std=2.2 可信不重跑 |
| **S1** | **readback_none (N′) 复测**（运维令三十二② + 23:2x 用户直令·2026-10-19~22·成本重测·PLAN_RETEST_READBACK_COST.md §1 规格）| **🟢 4/5 done·r5e3 跑中（-p 4 回到 r1-r4 口径·用户直令 09:0x）** | **r1 ✅ = 78.5% (124/158)**：batch `2026_1019_035502`·trace ✅。**r2 ✅ = 70.9% (112/158)**：batch `2026_1019_071104`。**r3 ✅ = 81.5% (123/151)**：batch `2026_1019_145634`·Path A fix。**r4e ✅ = 75.9% (120/158)**：batch `2026_1021_104432`·10:4x fix(timeout=600)根治·literal-pass=0/MCP-32001=0。4 轮 mean=**76.7% provisional**。**r5e2 INVALID**（batch `2026_1022_001122`·-p 8·593 sandbox-timeout·21 .py·-p8 退化作废·产物日志留证）。**r5e3 跑中**（batch `2026_1022_105416`·PID 1760194·10:54:16 起·-p 4·ports 8650/8651/8652/8654·fp4·READBACK=none·早期健康全绿 T+1min: -32001=0/literal-pass=0/sandbox-timeout=0）→ 5/5 mean±std → 更新论文 → full@pro-cloud 5 轮。 |
| **ZL-flash** | **glm-5.3-flash × zhulong × full 5-run**（09:4x 用户直令「作废 r1-r3(N′)·改 full 重跑 5 轮」·READBACK=full·8650组）| **✅ 5/5 收口 = 75.6±4.4%** | **r1-r3(N′)+r4(N′) 全 ❌作废**（READBACK=none 配置错误）：r1=67.1%/r2=68.4%/r3=60.1%/r4 被 kill。**full-r1 ✅=69.0%(109/158)**·batch 2026_1023_103036·16 lp。**full-r2 ✅=77.2%(122/158)**·batch 2026_1023_125220·16 lp。**full-r3 ✅=76.6%(121/158)**·batch 2026_1023_155612·23 fail。**full-r4 ✅=81.0%(128/158)**·batch 2026_1023_183402·12 fail。**full-r5 ✅=74.1%(117/158)**·batch 2026_1023_203835·27 fail。各轮 timeout=0/exec_err=0/infra=0·判据十三全轮有效·literal-pass>10 标退化(05:0x 不中止)·maxTokens=16384（**未对齐 cline**）。**5/5 mean±std=75.6±4.4%**（[69.0,77.2,76.6,81.0,74.1]）。**新探索线·🚫 不入论文**·论文锚点仍 (N′) fp4×cline 4 轮 76.7% provisional。 |
| **ZL-flash-aligned-8192** | **glm-5.3-flash × zhulong × full × maxTokens=8192 5-run**（10-26 用户直令·**❌ 已被 10-27 令作废**·maxTokens 与 cline 基线 16384 不一致）| **❌ 作废 5/5 = 70.8±7.7%** | [r1=58.9%(083652), r2=75.9%(112623), r3=67.1%(125254), r4=77.2%(160802), r5=74.7%(190240)]·**5 batch 全 VOIDED 留证不进对比**·VOID_REASON="maxTokens=8192 与 cline 基线 16384 不一致，10-27 令作废"·数据留证不删。详见 archive/历史归档 |
| **ZL-flash-clinealigned-16384** | **glm-5.3-flash × zhulong × full × maxTokens=16384 cline-aligned 5-run**（10-27 用户直令「ZL 完全使用 cline 相同配置」·与 cline 基线 86.8±1.6% 逐字节对齐·唯一变量=CLI 二进制·READBACK=full·8664 池）| **✅ 5/5 收口 = 69.0 ± 2.3%** [71.5, 67.1, 67.1, 71.5, 67.7]（vs cline 86.8±1.6%·Δ=−17.8pp）| 5 轮 batch 2026_1027_083127/123502/2026_1028_151059/231232/2026_1029_041540·各轮 exec_err=0·infra=0·timeout≤6·判据十三全轮有效·全程自有池 8664/8665/8653/8669·**判据①✅ worker_1 glm-5.3-flash+16384+/v1+reasoning=false 逐字节对齐**·r3/r4/r5 因 zhulong CLI 目录布局回归（缺 `ws/` 层）需 `mv` 修复后重跑 format/complete·gen-fail 23–38/轮（cline 1–4/轮）·结论：已排除 maxTokens 混杂+跨用户争用+CLI_AGENT 回归·唯一变量=CLI 二进制。详见成绩记录表同臂行 + 归档 20261027_1233/1403/20261028_2309/20261029_0415/1005。 |
| **DSV4-Pro.full** | **cline × deepseek-v4-pro × READBACK=full 5-run**（22:1x 用户直令「zl+glm-5.3-flash+full 5-run结束后，跑cline+deepseek-v4-pro 5-run+full」·**新探索线·🚫 不入论文**）| **🟠 r1 跑中 0/5** | **r1 跑中**：batch `2026_1023_231253`·PID1800419·起跑 23:12:53·cline 3.0.51·deepseek-v4-pro@/cloud/v1 key e13f4f37·maxTokens=16384·READBACK=full/OMEGA=high/BUDGET=0/LAGGED=0·8650组(8650/8651/8652/8654 @10.129.32.75)·-p 4·CLI_DATA_DIR=~/.cline/data·模型冒烟 HTTP200(deepseek-v4-pro-260813)✅·run_code 4字段readback冒烟✅·T+90s 5 worker 活·无 403/quota/error。待 r1→regrade→r2…→r5→5/5 mean±std。对照：ZL-flash full 5/5=75.6±4.4%·ZL-flash 旧 N′ 线 86.8±1.6%·论文锚点 (N′)fp4×cline 4 轮 76.7% provisional |

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
- [wake#836b/c/d 已滚出·2026-11-11 17:35 wake#838 归档] B 轴抽查三遍旧心跳（836b 11:20 / 836c 13:3x / 836d 15:2x）原文已搬入 `daily-memories/2026-11-11.md` §[rolled-out 17:35 wake#838 归档]。结论已被 17:35 wake#838 ru 补注版覆盖；既有报告正确，本任务已闭合。
- [wake#388~#798 旧指针已滚出·2026-11-10 21:44 合并] 原文见 `daily-memories/2026-11-10.md` §[rolled-out 21:44 wake#815 归档·冗余指针合并]（wake#388~#479 / #537~#540 / #560~#564 / #576 / #577~#607 / #608 / #784 / #791 / #792 / #798 共 10 条旧「已滚出」指针·均已被 line 8~31 的合并指针代表·此处冗余合并省 MEMORY 空间）。
